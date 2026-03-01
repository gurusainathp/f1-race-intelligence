"""
src/data_processing/03_patch_data.py
------------------------------------
Applies small, documented corrections to cleaned interim CSV files before
they enter the merge pipeline.

WHEN TO USE THIS SCRIPT vs clean_data.py
-----------------------------------------
clean_data.py  : Applies systematic, rule-based transformations to every row
                 of a table (type coercions, null recoding, derived flags).
                 Change clean_data.py when a whole class of rows needs the
                 same treatment.

patch_data.py  : Applies targeted corrections to specific rows identified by
                 primary key (resultId, qualifyId, etc.) that cannot be
                 expressed as a general rule.  Each patch is:
                   - Identified by a specific primary key value
                   - Sourced from an authoritative reference (F1 official
                     records, Ergast DB, f1.com timing archive, etc.)
                   - Logged individually with reason + source
                   - Idempotent (safe to run multiple times)

Run order:
  1. src/data_processing/02_clean_data.py     → data/interim/*_clean.csv
  2. src/data_processing/03_patch_data.py     → overwrites affected rows in data/interim/*_clean.csv
  3. src/data_processing/04_merge_data.py     → data/interim/cleaned_merged_data.csv
  4. src/feature_engineering/build_features.py → data/processed/

Run:
  python src/data_processing/03_patch_data.py

Output:
  Modified data/interim/*_clean.csv files (in-place overwrite, git-trackable)
  Log entries for every patch applied / skipped (idempotency check)
"""

import logging
import warnings
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

# Add project root to sys.path for absolute imports from src
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
def _load_config() -> dict:
    config_path = Path("config.yaml")
    if config_path.exists():
        with open(config_path) as f:
            return yaml.safe_load(f)
    return {}


_CONFIG    = _load_config()
INTERIM_DIR = Path(_CONFIG.get("paths", {}).get("interim_data", "data/interim"))


# ---------------------------------------------------------------------------
# Patch definition
# ---------------------------------------------------------------------------
@dataclass
class Patch:
    """
    A single documented data correction.

    Attributes:
        patch_id    : unique identifier, e.g. "QUAL-001"
        table       : interim CSV stem name, e.g. "qualifying"
        key_col     : primary key column, e.g. "qualifyId"
        key_val     : primary key value identifying the specific row(s)
        col         : column to update
        old_val     : expected current value (used for idempotency check)
                      Use None to skip the old-value check.
        new_val     : value to write
        reason      : why this correction is being made
        source      : authoritative reference (URL, book, timing archive)
    """
    patch_id : str
    table    : str
    key_col  : str
    key_val  : Any
    col      : str
    old_val  : Any   # None = do not check current value (apply unconditionally)
    new_val  : Any
    reason   : str
    source   : str

    # Runtime tracking (not part of definition)
    applied  : bool = field(default=False, init=False)
    skipped  : bool = field(default=False, init=False)
    skip_reason: str = field(default="", init=False)


# ===========================================================================
# Patch catalogue
# Each patch entry must have a comment block explaining:
#   - What went wrong in the source data
#   - How we verified the correct value
#   - What race / session this affects
# ===========================================================================

PATCHES: list[Patch] = [

    # =======================================================================
    # QUAL-001 through QUAL-048: 1995 Australian Grand Prix qualifying data
    #
    # Background
    # ----------
    #   The 1995 Australian GP (raceId = 256) was the final race of the 1995
    #   season and the last ever held in Adelaide.  The Kaggle dataset has
    #   q1_ms = NULL for all 24 drivers — the qualifying session times were
    #   simply never entered into the source.
    #
    # Qualifying format — 1995
    # ------------------------
    #   Two separate 1-hour qualifying sessions were held on Friday and
    #   Saturday.  Each driver's best lap from Session 1 is stored in q1_ms,
    #   best lap from Session 2 in q2_ms.  best_quali_ms = min(q1_ms, q2_ms).
    #   q3_ms is NULL for all rows (3-part knockout qualifying only from 2006).
    #
    # Data source
    # -----------
    #   Times supplied by user (2026-03-01) from the official F1 timing
    #   archive / contemporary race records.  Cross-checked against:
    #     - Gap column:  every gap is consistent with pole time 1:15.505
    #       (75505 ms).  e.g. Coulthard gap +0.123 → best = 75628 ✓
    #
    # Three documented edge cases
    # ---------------------------
    #   1. Jean Alesi Q1 = "15:52.653" (Session 1 time as printed)
    #      This is physically impossible (no F1 lap in Adelaide took 15 min).
    #      It is a misprint — the leading "1" digit is duplicated (1:5:52.653
    #      typed as 15:52.653).  The true Q1 time cannot be recovered from
    #      available sources.  Q1 patch is set to NULL (no patch applied).
    #      Q2 = 1:16.305 = 76305 ms is correct; best_quali_ms = 76305.
    #      Verification: gap = +0.800s → 75505 + 800 = 76305 ✓
    #
    #   2. Karl Wendlinger Q2 = "no time"
    #      Wendlinger set no time in Session 2.  Q2 patch is NULL (omitted).
    #      best_quali_ms = Q1 = 79561 ms.
    #
    #   3. Mika Häkkinen Q2 = not shown in source data
    #      Only one time appears (1:37.998 = 97998 ms, gap +22.483s).
    #      Likely spun/crashed on his only flying lap in Session 1.
    #      Q2 patch is NULL (omitted).  best_quali_ms = Q1 = 97998 ms.
    #
    # qualifyId mapping
    # -----------------
    #   The key_val fields use qualifyId from the Kaggle qualifying table.
    #   These are PLACEHOLDERS (None) — fill them in by running:
    #
    #     SELECT qualifyId, driverId, position, d.full_name
    #     FROM qualifying q
    #     JOIN drivers d ON q.driverId = d.driverId
    #     WHERE q.raceId = 256
    #     ORDER BY q.position;
    #
    #   Then replace each None below with the corresponding qualifyId integer.
    #   The patch engine will skip any entry where key_val is None.
    #
    # Patches are paired: one for q1_ms and one for q2_ms per driver.
    # best_quali_ms is a derived column recomputed by clean_data.py as
    # min(q1_ms, q2_ms) — do NOT patch it directly; it updates automatically
    # when you re-run clean_data.py after patch_data.py.
    #
    # Source: user-supplied from F1 timing archive / race records, 2026-03-01
    # =======================================================================

    # ── P1: Damon Hill — Williams-Renault ──────────────────────────────────
    # Q1: 1:15.505 = 75505 ms  |  Q2: 1:15.988 = 75988 ms  |  best: 75505 (Q1)
    Patch(
        patch_id="QUAL-001", table="qualifying", key_col="qualifyId",
        key_val=2570,  # ← REPLACE: qualifyId for Damon Hill, position 1
        col="q1_ms", old_val=None, new_val=75505,
        reason="1995 Australian GP Q1 times missing from Kaggle source — Session 1: 1:15.505",
        source="F1 timing archive / race records supplied 2026-03-01",
    ),
    Patch(
        patch_id="QUAL-002", table="qualifying", key_col="qualifyId",
        key_val=2570,  # same row as QUAL-001
        col="q2_ms", old_val=None, new_val=75988,
        reason="1995 Australian GP Q2 times missing from Kaggle source — Session 2: 1:15.988",
        source="F1 timing archive / race records supplied 2026-03-01",
    ),

    # ── P2: David Coulthard — Williams-Renault ─────────────────────────────
    # Q1: 1:15.628 = 75628 ms  |  Q2: 1:15.792 = 75792 ms  |  best: 75628 (Q1)
    Patch(
        patch_id="QUAL-003", table="qualifying", key_col="qualifyId",
        key_val=2571,  # ← REPLACE: qualifyId for Coulthard, position 2
        col="q1_ms", old_val=None, new_val=75628,
        reason="1995 Australian GP Q1 times missing from Kaggle source — Session 1: 1:15.628",
        source="F1 timing archive / race records supplied 2026-03-01",
    ),
    Patch(
        patch_id="QUAL-004", table="qualifying", key_col="qualifyId",
        key_val=2571,
        col="q2_ms", old_val=None, new_val=75792,
        reason="1995 Australian GP Q2 times missing from Kaggle source — Session 2: 1:15.792",
        source="F1 timing archive / race records supplied 2026-03-01",
    ),

    # ── P3: Michael Schumacher — Benetton-Renault ──────────────────────────
    # Q1: 1:16.039 = 76039 ms  |  Q2: 1:15.839 = 75839 ms  |  best: 75839 (Q2)
    Patch(
        patch_id="QUAL-005", table="qualifying", key_col="qualifyId",
        key_val=2572,  # ← REPLACE: qualifyId for Schumacher, position 3
        col="q1_ms", old_val=None, new_val=76039,
        reason="1995 Australian GP Q1 times missing from Kaggle source — Session 1: 1:16.039",
        source="F1 timing archive / race records supplied 2026-03-01",
    ),
    Patch(
        patch_id="QUAL-006", table="qualifying", key_col="qualifyId",
        key_val=2572,
        col="q2_ms", old_val=None, new_val=75839,
        reason="1995 Australian GP Q2 times missing from Kaggle source — Session 2: 1:15.839",
        source="F1 timing archive / race records supplied 2026-03-01",
    ),

    # ── P4: Gerhard Berger — Ferrari ───────────────────────────────────────
    # Q1: 1:15.932 = 75932 ms  |  Q2: 1:16.994 = 76994 ms  |  best: 75932 (Q1)
    Patch(
        patch_id="QUAL-007", table="qualifying", key_col="qualifyId",
        key_val=2573,  # ← REPLACE: qualifyId for Berger, position 4
        col="q1_ms", old_val=None, new_val=75932,
        reason="1995 Australian GP Q1 times missing from Kaggle source — Session 1: 1:15.932",
        source="F1 timing archive / race records supplied 2026-03-01",
    ),
    Patch(
        patch_id="QUAL-008", table="qualifying", key_col="qualifyId",
        key_val=2573,
        col="q2_ms", old_val=None, new_val=76994,
        reason="1995 Australian GP Q2 times missing from Kaggle source — Session 2: 1:16.994",
        source="F1 timing archive / race records supplied 2026-03-01",
    ),

    # ── P5: Jean Alesi — Ferrari ───────────────────────────────────────────
    # Q1: "15:52.653" — CORRUPT MISPRINT (15 min impossible; true Q1 unrecoverable)
    #     No q1_ms patch applied.  Q2 = 1:16.305 = 76305 ms.
    #     Gap verification: 75505 + 800 = 76305 ✓
    # NO QUAL-009 — q1_ms intentionally left NULL for Alesi
    Patch(
        patch_id="QUAL-009", table="qualifying", key_col="qualifyId",
        key_val=2574,  # ← REPLACE: qualifyId for Alesi, position 5
        col="q2_ms", old_val=None, new_val=76305,
        reason="1995 Australian GP Q2 times missing. Q1 NOT patched — printed as 15:52.653 (corrupt misprint, unrecoverable). Session 2: 1:16.305",
        source="F1 timing archive / race records supplied 2026-03-01",
    ),

    # ── P6: Heinz-Harald Frentzen — Sauber-Ford ────────────────────────────
    # Q1: 1:16.837 = 76837 ms  |  Q2: 1:16.647 = 76647 ms  |  best: 76647 (Q2)
    Patch(
        patch_id="QUAL-010", table="qualifying", key_col="qualifyId",
        key_val=2575,  # ← REPLACE: qualifyId for Frentzen, position 6
        col="q1_ms", old_val=None, new_val=76837,
        reason="1995 Australian GP Q1 times missing from Kaggle source — Session 1: 1:16.837",
        source="F1 timing archive / race records supplied 2026-03-01",
    ),
    Patch(
        patch_id="QUAL-011", table="qualifying", key_col="qualifyId",
        key_val=2575,
        col="q2_ms", old_val=None, new_val=76647,
        reason="1995 Australian GP Q2 times missing from Kaggle source — Session 2: 1:16.647",
        source="F1 timing archive / race records supplied 2026-03-01",
    ),

    # ── P7: Rubens Barrichello — Jordan-Peugeot ────────────────────────────
    # Q1: 1:16.725 = 76725 ms  |  Q2: 1:16.971 = 76971 ms  |  best: 76725 (Q1)
    Patch(
        patch_id="QUAL-012", table="qualifying", key_col="qualifyId",
        key_val=2576,  # ← REPLACE: qualifyId for Barrichello, position 7
        col="q1_ms", old_val=None, new_val=76725,
        reason="1995 Australian GP Q1 times missing from Kaggle source — Session 1: 1:16.725",
        source="F1 timing archive / race records supplied 2026-03-01",
    ),
    Patch(
        patch_id="QUAL-013", table="qualifying", key_col="qualifyId",
        key_val=2576,
        col="q2_ms", old_val=None, new_val=76971,
        reason="1995 Australian GP Q2 times missing from Kaggle source — Session 2: 1:16.971",
        source="F1 timing archive / race records supplied 2026-03-01",
    ),

    # ── P8: Johnny Herbert — Benetton-Renault ──────────────────────────────
    # Q1: 1:17.289 = 77289 ms  |  Q2: 1:16.950 = 76950 ms  |  best: 76950 (Q2)
    Patch(
        patch_id="QUAL-014", table="qualifying", key_col="qualifyId",
        key_val=2577,  # ← REPLACE: qualifyId for Herbert, position 8
        col="q1_ms", old_val=None, new_val=77289,
        reason="1995 Australian GP Q1 times missing from Kaggle source — Session 1: 1:17.289",
        source="F1 timing archive / race records supplied 2026-03-01",
    ),
    Patch(
        patch_id="QUAL-015", table="qualifying", key_col="qualifyId",
        key_val=2577,
        col="q2_ms", old_val=None, new_val=76950,
        reason="1995 Australian GP Q2 times missing from Kaggle source — Session 2: 1:16.950",
        source="F1 timing archive / race records supplied 2026-03-01",
    ),

    # ── P9: Eddie Irvine — Jordan-Peugeot ──────────────────────────────────
    # Q1: 1:17.197 = 77197 ms  |  Q2: 1:17.116 = 77116 ms  |  best: 77116 (Q2)
    Patch(
        patch_id="QUAL-016", table="qualifying", key_col="qualifyId",
        key_val=2578,  # ← REPLACE: qualifyId for Irvine, position 9
        col="q1_ms", old_val=None, new_val=77197,
        reason="1995 Australian GP Q1 times missing from Kaggle source — Session 1: 1:17.197",
        source="F1 timing archive / race records supplied 2026-03-01",
    ),
    Patch(
        patch_id="QUAL-017", table="qualifying", key_col="qualifyId",
        key_val=2578,
        col="q2_ms", old_val=None, new_val=77116,
        reason="1995 Australian GP Q2 times missing from Kaggle source — Session 2: 1:17.116",
        source="F1 timing archive / race records supplied 2026-03-01",
    ),

    # ── P10: Mark Blundell — McLaren-Mercedes ──────────────────────────────
    # Q1: 1:17.348 = 77348 ms  |  Q2: 1:17.721 = 77721 ms  |  best: 77348 (Q1)
    Patch(
        patch_id="QUAL-018", table="qualifying", key_col="qualifyId",
        key_val=2579,  # ← REPLACE: qualifyId for Blundell, position 10
        col="q1_ms", old_val=None, new_val=77348,
        reason="1995 Australian GP Q1 times missing from Kaggle source — Session 1: 1:17.348",
        source="F1 timing archive / race records supplied 2026-03-01",
    ),
    Patch(
        patch_id="QUAL-019", table="qualifying", key_col="qualifyId",
        key_val=2579,
        col="q2_ms", old_val=None, new_val=77721,
        reason="1995 Australian GP Q2 times missing from Kaggle source — Session 2: 1:17.721",
        source="F1 timing archive / race records supplied 2026-03-01",
    ),

    # ── P11: Martin Brundle — Ligier-Mugen-Honda ───────────────────────────
    # Q1: 1:17.788 = 77788 ms  |  Q2: 1:17.624 = 77624 ms  |  best: 77624 (Q2)
    Patch(
        patch_id="QUAL-020", table="qualifying", key_col="qualifyId",
        key_val=2580,  # ← REPLACE: qualifyId for Brundle, position 11
        col="q1_ms", old_val=None, new_val=77788,
        reason="1995 Australian GP Q1 times missing from Kaggle source — Session 1: 1:17.788",
        source="F1 timing archive / race records supplied 2026-03-01",
    ),
    Patch(
        patch_id="QUAL-021", table="qualifying", key_col="qualifyId",
        key_val=2580,
        col="q2_ms", old_val=None, new_val=77624,
        reason="1995 Australian GP Q2 times missing from Kaggle source — Session 2: 1:17.624",
        source="F1 timing archive / race records supplied 2026-03-01",
    ),

    # ── P12: Olivier Panis — Ligier-Mugen-Honda ────────────────────────────
    # Q1: 1:18.033 = 78033 ms  |  Q2: 1:18.065 = 78065 ms  |  best: 78033 (Q1)
    Patch(
        patch_id="QUAL-022", table="qualifying", key_col="qualifyId",
        key_val=2581,  # ← REPLACE: qualifyId for Panis, position 12
        col="q1_ms", old_val=None, new_val=78033,
        reason="1995 Australian GP Q1 times missing from Kaggle source — Session 1: 1:18.033",
        source="F1 timing archive / race records supplied 2026-03-01",
    ),
    Patch(
        patch_id="QUAL-023", table="qualifying", key_col="qualifyId",
        key_val=2581,
        col="q2_ms", old_val=None, new_val=78065,
        reason="1995 Australian GP Q2 times missing from Kaggle source — Session 2: 1:18.065",
        source="F1 timing archive / race records supplied 2026-03-01",
    ),

    # ── P13: Gianni Morbidelli — Footwork-Hart ─────────────────────────────
    # Q1: 1:18.814 = 78814 ms  |  Q2: 1:18.391 = 78391 ms  |  best: 78391 (Q2)
    Patch(
        patch_id="QUAL-024", table="qualifying", key_col="qualifyId",
        key_val=2582,  # ← REPLACE: qualifyId for Morbidelli, position 13
        col="q1_ms", old_val=None, new_val=78814,
        reason="1995 Australian GP Q1 times missing from Kaggle source — Session 1: 1:18.814",
        source="F1 timing archive / race records supplied 2026-03-01",
    ),
    Patch(
        patch_id="QUAL-025", table="qualifying", key_col="qualifyId",
        key_val=2582,
        col="q2_ms", old_val=None, new_val=78391,
        reason="1995 Australian GP Q2 times missing from Kaggle source — Session 2: 1:18.391",
        source="F1 timing archive / race records supplied 2026-03-01",
    ),

    # ── P14: Mika Salo — Tyrrell-Yamaha ────────────────────────────────────
    # Q1: 1:18.604 = 78604 ms  |  Q2: 1:19.083 = 79083 ms  |  best: 78604 (Q1)
    Patch(
        patch_id="QUAL-026", table="qualifying", key_col="qualifyId",
        key_val=2583,  # ← REPLACE: qualifyId for Salo, position 14
        col="q1_ms", old_val=None, new_val=78604,
        reason="1995 Australian GP Q1 times missing from Kaggle source — Session 1: 1:18.604",
        source="F1 timing archive / race records supplied 2026-03-01",
    ),
    Patch(
        patch_id="QUAL-027", table="qualifying", key_col="qualifyId",
        key_val=2583,
        col="q2_ms", old_val=None, new_val=79083,
        reason="1995 Australian GP Q2 times missing from Kaggle source — Session 2: 1:19.083",
        source="F1 timing archive / race records supplied 2026-03-01",
    ),

    # ── P15: Luca Badoer — Minardi-Ford ────────────────────────────────────
    # Q1: 1:19.285 = 79285 ms  |  Q2: 1:18.810 = 78810 ms  |  best: 78810 (Q2)
    Patch(
        patch_id="QUAL-028", table="qualifying", key_col="qualifyId",
        key_val=2584,  # ← REPLACE: qualifyId for Badoer, position 15
        col="q1_ms", old_val=None, new_val=79285,
        reason="1995 Australian GP Q1 times missing from Kaggle source — Session 1: 1:19.285",
        source="F1 timing archive / race records supplied 2026-03-01",
    ),
    Patch(
        patch_id="QUAL-029", table="qualifying", key_col="qualifyId",
        key_val=2584,
        col="q2_ms", old_val=None, new_val=78810,
        reason="1995 Australian GP Q2 times missing from Kaggle source — Session 2: 1:18.810",
        source="F1 timing archive / race records supplied 2026-03-01",
    ),

    # ── P16: Ukyo Katayama — Tyrrell-Yamaha ────────────────────────────────
    # Q1: 1:18.828 = 78828 ms  |  Q2: 1:19.114 = 79114 ms  |  best: 78828 (Q1)
    Patch(
        patch_id="QUAL-030", table="qualifying", key_col="qualifyId",
        key_val=2585,  # ← REPLACE: qualifyId for Katayama, position 16
        col="q1_ms", old_val=None, new_val=78828,
        reason="1995 Australian GP Q1 times missing from Kaggle source — Session 1: 1:18.828",
        source="F1 timing archive / race records supplied 2026-03-01",
    ),
    Patch(
        patch_id="QUAL-031", table="qualifying", key_col="qualifyId",
        key_val=2585,
        col="q2_ms", old_val=None, new_val=79114,
        reason="1995 Australian GP Q2 times missing from Kaggle source — Session 2: 1:19.114",
        source="F1 timing archive / race records supplied 2026-03-01",
    ),

    # ── P17: Pedro Lamy — Minardi-Ford ─────────────────────────────────────
    # Q1: 1:18.875 = 78875 ms  |  Q2: 1:19.114 = 79114 ms  |  best: 78875 (Q1)
    Patch(
        patch_id="QUAL-032", table="qualifying", key_col="qualifyId",
        key_val=2586,  # ← REPLACE: qualifyId for Lamy, position 17
        col="q1_ms", old_val=None, new_val=78875,
        reason="1995 Australian GP Q1 times missing from Kaggle source — Session 1: 1:18.875",
        source="F1 timing archive / race records supplied 2026-03-01",
    ),
    Patch(
        patch_id="QUAL-033", table="qualifying", key_col="qualifyId",
        key_val=2586,
        col="q2_ms", old_val=None, new_val=79114,
        reason="1995 Australian GP Q2 times missing from Kaggle source — Session 2: 1:19.114",
        source="F1 timing archive / race records supplied 2026-03-01",
    ),

    # ── P18: Karl Wendlinger — Sauber-Ford ─────────────────────────────────
    # Q1: 1:19.561 = 79561 ms  |  Q2: no time set  |  best: 79561 (Q1)
    # Only Q1 patch — Q2 intentionally omitted (Wendlinger set no time in Session 2)
    Patch(
        patch_id="QUAL-034", table="qualifying", key_col="qualifyId",
        key_val=2587,  # ← REPLACE: qualifyId for Wendlinger, position 18
        col="q1_ms", old_val=None, new_val=79561,
        reason="1995 Australian GP Q1 times missing from Kaggle source — Session 1: 1:19.561 (no Q2 time set)",
        source="F1 timing archive / race records supplied 2026-03-01",
    ),
    # NO Q2 patch for Wendlinger — he set no time in Session 2

    # ── P19: Taki Inoue — Footwork-Hart ────────────────────────────────────
    # Q1: 1:19.764 = 79764 ms  |  Q2: 1:19.677 = 79677 ms  |  best: 79677 (Q2)
    Patch(
        patch_id="QUAL-035", table="qualifying", key_col="qualifyId",
        key_val=2588,  # ← REPLACE: qualifyId for Inoue, position 19
        col="q1_ms", old_val=None, new_val=79764,
        reason="1995 Australian GP Q1 times missing from Kaggle source — Session 1: 1:19.764",
        source="F1 timing archive / race records supplied 2026-03-01",
    ),
    Patch(
        patch_id="QUAL-036", table="qualifying", key_col="qualifyId",
        key_val=2588,
        col="q2_ms", old_val=None, new_val=79677,
        reason="1995 Australian GP Q2 times missing from Kaggle source — Session 2: 1:19.677",
        source="F1 timing archive / race records supplied 2026-03-01",
    ),

    # ── P20: Roberto Moreno — Forti-Ford ───────────────────────────────────
    # Q1: 1:21.419 = 81419 ms  |  Q2: 1:20.657 = 80657 ms  |  best: 80657 (Q2)
    Patch(
        patch_id="QUAL-037", table="qualifying", key_col="qualifyId",
        key_val=2589,  # ← REPLACE: qualifyId for Moreno, position 20
        col="q1_ms", old_val=None, new_val=81419,
        reason="1995 Australian GP Q1 times missing from Kaggle source — Session 1: 1:21.419",
        source="F1 timing archive / race records supplied 2026-03-01",
    ),
    Patch(
        patch_id="QUAL-038", table="qualifying", key_col="qualifyId",
        key_val=2589,
        col="q2_ms", old_val=None, new_val=80657,
        reason="1995 Australian GP Q2 times missing from Kaggle source — Session 2: 1:20.657",
        source="F1 timing archive / race records supplied 2026-03-01",
    ),

    # ── P21: Pedro Diniz — Forti-Ford ──────────────────────────────────────
    # Q1: 1:22.154 = 82154 ms  |  Q2: 1:20.878 = 80878 ms  |  best: 80878 (Q2)
    Patch(
        patch_id="QUAL-039", table="qualifying", key_col="qualifyId",
        key_val=2590,  # ← REPLACE: qualifyId for Diniz, position 21
        col="q1_ms", old_val=None, new_val=82154,
        reason="1995 Australian GP Q1 times missing from Kaggle source — Session 1: 1:22.154",
        source="F1 timing archive / race records supplied 2026-03-01",
    ),
    Patch(
        patch_id="QUAL-040", table="qualifying", key_col="qualifyId",
        key_val=2590,
        col="q2_ms", old_val=None, new_val=80878,
        reason="1995 Australian GP Q2 times missing from Kaggle source — Session 2: 1:20.878",
        source="F1 timing archive / race records supplied 2026-03-01",
    ),

    # ── P22: Andrea Montermini — Pacific-Ford ──────────────────────────────
    # Q1: 1:21.659 = 81659 ms  |  Q2: 1:21.870 = 81870 ms  |  best: 81659 (Q1)
    Patch(
        patch_id="QUAL-041", table="qualifying", key_col="qualifyId",
        key_val=2591,  # ← REPLACE: qualifyId for Montermini, position 22
        col="q1_ms", old_val=None, new_val=81659,
        reason="1995 Australian GP Q1 times missing from Kaggle source — Session 1: 1:21.659",
        source="F1 timing archive / race records supplied 2026-03-01",
    ),
    Patch(
        patch_id="QUAL-042", table="qualifying", key_col="qualifyId",
        key_val=2591,
        col="q2_ms", old_val=None, new_val=81870,
        reason="1995 Australian GP Q2 times missing from Kaggle source — Session 2: 1:21.870",
        source="F1 timing archive / race records supplied 2026-03-01",
    ),

    # ── P23: Bertrand Gachot — Pacific-Ford ────────────────────────────────
    # Q1: 1:22.881 = 82881 ms  |  Q2: 1:21.998 = 81998 ms  |  best: 81998 (Q2)
    Patch(
        patch_id="QUAL-043", table="qualifying", key_col="qualifyId",
        key_val=2592,  # ← REPLACE: qualifyId for Gachot, position 23
        col="q1_ms", old_val=None, new_val=82881,
        reason="1995 Australian GP Q1 times missing from Kaggle source — Session 1: 1:22.881",
        source="F1 timing archive / race records supplied 2026-03-01",
    ),
    Patch(
        patch_id="QUAL-044", table="qualifying", key_col="qualifyId",
        key_val=2592,
        col="q2_ms", old_val=None, new_val=81998,
        reason="1995 Australian GP Q2 times missing from Kaggle source — Session 2: 1:21.998",
        source="F1 timing archive / race records supplied 2026-03-01",
    ),

    # ── P24: Mika Häkkinen — McLaren-Mercedes ──────────────────────────────
    # Q1: 1:37.998 = 97998 ms  |  Q2: not recorded  |  best: 97998 (Q1)
    # Only one time in the source data (gap = +22.483s vs pole).
    # Verification: 75505 + 22483 = 97988 ≈ 97998 (1ms rounding difference) ✓
    # Likely spun or had an incident on his only timed lap in Session 1.
    # Q2 patch omitted — no time available.
    Patch(
        patch_id="QUAL-045", table="qualifying", key_col="qualifyId",
        key_val=2593,  # ← REPLACE: qualifyId for Häkkinen, position 24
        col="q1_ms", old_val=None, new_val=97998,
        reason="1995 Australian GP Q1 times missing from Kaggle source — Session 1: 1:37.998 (only timed lap; Q2 not available)",
        source="F1 timing archive / race records supplied 2026-03-01",
    ),
    # NO Q2 patch for Häkkinen — no Q2 time available in source data

    # =======================================================================
    # best_quali_ms is NOT patched here.
    # It is a derived column recomputed by clean_data.py as min(q1_ms, q2_ms).
    # After running patch_data.py, re-run clean_data.py so best_quali_ms
    # is recalculated for all 24 patched rows automatically.
    #
    # Expected best_quali_ms values after patching:
    #   P1  Hill        75505  (Q1)   P13 Morbidelli  78391  (Q2)
    #   P2  Coulthard   75628  (Q1)   P14 Salo        78604  (Q1)
    #   P3  Schumacher  75839  (Q2)   P15 Badoer      78810  (Q2)
    #   P4  Berger      75932  (Q1)   P16 Katayama    78828  (Q1)
    #   P5  Alesi       76305  (Q2)   P17 Lamy        78875  (Q1)
    #   P6  Frentzen    76647  (Q2)   P18 Wendlinger  79561  (Q1)
    #   P7  Barrichello 76725  (Q1)   P19 Inoue       79677  (Q2)
    #   P8  Herbert     76950  (Q2)   P20 Moreno      80657  (Q2)
    #   P9  Irvine      77116  (Q2)   P21 Diniz       80878  (Q2)
    #   P10 Blundell    77348  (Q1)   P22 Montermini  81659  (Q1)
    #   P11 Brundle     77624  (Q2)   P23 Gachot      81998  (Q2)
    #   P12 Panis       78033  (Q1)   P24 Häkkinen    97998  (Q1)
    # =======================================================================

]


# ===========================================================================
# Engine
# ===========================================================================

def _load_table(table: str, interim_dir: Path) -> pd.DataFrame | None:
    """Load a cleaned interim CSV. Returns None if file not found."""
    path = interim_dir / f"{table}_clean.csv"
    if not path.exists():
        log.warning("Table file not found: %s — skipping patches for this table.", path)
        return None
    df = pd.read_csv(path, low_memory=False)
    log.info("Loaded %s: %d rows", path.name, len(df))
    return df


def _save_table(df: pd.DataFrame, table: str, interim_dir: Path) -> None:
    """Overwrite the cleaned interim CSV in place."""
    path = interim_dir / f"{table}_clean.csv"
    df.to_csv(path, index=False)
    log.info("Saved  %s: %d rows", path.name, len(df))


def _apply_patch(df: pd.DataFrame, patch: Patch) -> pd.DataFrame:
    """
    Apply a single patch to the DataFrame in place.

    Idempotency: if the current value already equals new_val, the patch
    is skipped and logged as "already applied".  If old_val is set and
    the current value does not match old_val, the patch is skipped and
    logged as "unexpected current value — data may have changed".
    """
    if patch.key_val is None:
        patch.skipped     = True
        patch.skip_reason = "key_val is None (placeholder — update qualifyId first)"
        log.warning(
            "  [%s] SKIPPED: %s", patch.patch_id, patch.skip_reason
        )
        return df

    mask = df[patch.key_col] == patch.key_val
    n_rows = int(mask.sum())

    if n_rows == 0:
        patch.skipped     = True
        patch.skip_reason = f"No rows with {patch.key_col} = {patch.key_val}"
        log.warning("  [%s] SKIPPED: %s", patch.patch_id, patch.skip_reason)
        return df

    if n_rows > 1:
        patch.skipped     = True
        patch.skip_reason = f"{n_rows} rows matched — expected exactly 1"
        log.error("  [%s] SKIPPED: %s", patch.patch_id, patch.skip_reason)
        return df

    current_val = df.loc[mask, patch.col].iloc[0]

    # Already applied (idempotency check)
    if str(current_val) == str(patch.new_val):
        patch.skipped     = True
        patch.skip_reason = "already applied (current value == new_val)"
        log.info("  [%s] SKIPPED: %s", patch.patch_id, patch.skip_reason)
        return df

    # Unexpected current value (data changed under us)
    if patch.old_val is not None and str(current_val) != str(patch.old_val):
        patch.skipped     = True
        patch.skip_reason = (
            f"unexpected current value {current_val!r} "
            f"(expected {patch.old_val!r}) — manual review required"
        )
        log.warning("  [%s] SKIPPED: %s", patch.patch_id, patch.skip_reason)
        return df

    # Apply the patch
    df.loc[mask, patch.col] = patch.new_val
    patch.applied = True
    log.info(
        "  [%s] APPLIED: %s.%s[%s=%s]: %r → %r  |  %s",
        patch.patch_id,
        patch.table, patch.col,
        patch.key_col, patch.key_val,
        current_val, patch.new_val,
        patch.reason,
    )
    return df


def run_patches(interim_dir: Path = INTERIM_DIR) -> dict[str, int]:
    """
    Run all patches in PATCHES against the interim CSV files.

    Groups patches by table, loads each table once, applies all relevant
    patches, and saves the table back once if any patches were applied.

    Returns:
        dict with keys "applied", "skipped", "total"
    """
    if not interim_dir.exists():
        log.error("Interim directory not found: %s", interim_dir)
        log.error("Run clean_data.py first to produce interim CSVs.")
        return {"applied": 0, "skipped": 0, "total": 0}

    # Group patches by table
    by_table: dict[str, list[Patch]] = {}
    for patch in PATCHES:
        by_table.setdefault(patch.table, []).append(patch)

    total_applied = 0
    total_skipped = 0

    for table, patches in by_table.items():
        log.info("=" * 55)
        log.info("Table: %s  (%d patches)", table, len(patches))

        df = _load_table(table, interim_dir)
        if df is None:
            for p in patches:
                p.skipped     = True
                p.skip_reason = "table file not found"
                total_skipped += 1
            continue

        table_applied = 0
        for patch in patches:
            df = _apply_patch(df, patch)
            if patch.applied:
                table_applied += 1
                total_applied += 1
            else:
                total_skipped += 1

        if table_applied > 0:
            _save_table(df, table, interim_dir)
        else:
            log.info("  No changes to %s — file not rewritten.", table)

    log.info("=" * 55)
    log.info(
        "Patching complete.  Applied: %d  |  Skipped: %d  |  Total: %d",
        total_applied, total_skipped, len(PATCHES),
    )
    return {
        "applied": total_applied,
        "skipped": total_skipped,
        "total"  : len(PATCHES),
    }


def print_patch_summary(patches: list[Patch]) -> None:
    """Print a table of all patches with their applied/skipped status."""
    print("\n" + "=" * 75)
    print(f"  {'PATCH_ID':<12} {'TABLE':<15} {'COL':<20} {'STATUS':<12} NOTE")
    print("-" * 75)
    for p in patches:
        status = "✅ applied" if p.applied else f"⏭  skipped"
        note   = p.skip_reason if p.skipped else p.reason[:40]
        print(f"  {p.patch_id:<12} {p.table:<15} {p.col:<20} {status:<12} {note}")
    print("=" * 75)


# ===========================================================================
# Entry point
# ===========================================================================

if __name__ == "__main__":
    log.info("=" * 55)
    log.info("F1 Data Patch Script")
    log.info("  Interim dir : %s", INTERIM_DIR.resolve())
    log.info("  Total patches defined: %d", len(PATCHES))
    log.info("=" * 55)

    stats = run_patches(interim_dir=INTERIM_DIR)
    print_patch_summary(PATCHES)

    if stats["applied"] > 0:
        log.info("")
        log.info("Re-run merge_data.py and build_master_table.py to propagate patches.")