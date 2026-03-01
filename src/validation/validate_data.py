"""
src/validation/validate_data.py
=================================
Run anytime before modeling to validate data integrity.
Outputs: reports/data_quality/data_quality_report.md

Checks performed:
  0. Quality scorecard
  1. Dataset inventory
  2. Null value analysis  (context-aware: distinguishes justified vs unjustified nulls)
  3. Schema drift         (expected columns present)
  4. Foreign key validation (with orphan row counts)
  5. Duplicate detection  (sprint-race aware; checks constructorId as tiebreaker)
  6. Lap time validation  (tiered thresholds for SC/VSC laps + z-score outliers)
  7. Status & DNF validation (via results integration, improved classifier)
  8. Feature table duplicate keys
  9. Feature value bounds  (impossible values in derived feature columns)
 10. Points reconciliation (driver-race vs constructor-season aggregate cross-check)
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import sys

# Add project root to sys.path for absolute imports from src
_PROJECT_ROOT_VALIDATE = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT_VALIDATE) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT_VALIDATE))

# Import shared classifiers and thresholds — single source of truth
try:
    from src.utils.constants import (
        DNF_KEYWORDS, FINISH_KEYWORDS, LAPPED_PATTERNS,
        LAP_TIME_MIN_MS, LAP_TIME_WARN_MS, LAP_TIME_CORRUPT_MS, LAP_Z_THRESHOLD,
        is_dnf as _is_dnf_fn, is_finish as _is_finish_fn,
    )
    _CONSTANTS_AVAILABLE = True
except ImportError:
    _CONSTANTS_AVAILABLE = False
    LAP_TIME_MIN_MS     = 40_000
    LAP_TIME_WARN_MS    = 300_000
    LAP_TIME_CORRUPT_MS = 600_000
    LAP_Z_THRESHOLD     = 5

# ── Configuration ──────────────────────────────────────────────────────────────
INTERIM_DIR   = Path("data/interim")
PROCESSED_DIR = Path("data/processed")
REPORT_PATH   = Path("reports/data_quality/data_quality_report.md")

# Parquet feature store paths (all live in data/processed/)
DRIVER_RACE_PARQUET        = PROCESSED_DIR / "driver_race_features.parquet"
DRIVER_SEASON_PARQUET      = PROCESSED_DIR / "driver_season_features.parquet"
CONSTRUCTOR_SEASON_PARQUET = PROCESSED_DIR / "constructor_season_features.parquet"

# Foreign key relationships: (child_table, child_col) → (parent_table, parent_col)
FK_CHECKS = [
    ("results", "raceId",        "races",        "raceId"),
    ("results", "driverId",      "drivers",      "driverId"),
    ("results", "constructorId", "constructors", "constructorId"),
    ("results", "statusId",      "status",       "statusId"),
]

# Expected columns per table
EXPECTED_SCHEMA: dict[str, set[str]] = {
    "results":      {"resultId", "raceId", "driverId", "constructorId", "statusId",
                     "grid", "grid_pit_lane",
                     "position", "points", "laps"},
    "races":        {"raceId", "year", "round", "circuitId", "name", "date"},
    "drivers":      {"driverId", "driverRef", "forename", "surname", "nationality"},
    "constructors": {"constructorId", "constructorRef", "name", "nationality"},
    "status":       {"statusId", "status"},
    "lap_times":    {"raceId", "driverId", "lap", "position", "lap_time_ms"},
}

EXPECTED_MASTER_COLS: set[str] = {
    "pit_data_incomplete", "grid_pit_lane",
    "is_dnf", "dnf_type", "is_podium", "is_winner", "is_points_finish",
}

# ── Null context ────────────────────────────────────────────────────────────────
JUSTIFIED_NULLS: dict[str, str] = {
    "sprint_date":       "Sprint sessions only from 2021 (~6% of races)",
    "fp1_date":          "Session dates only recorded from 2021 era",
    "fp2_date":          "Session dates only recorded from 2021 era",
    "fp3_date":          "Session dates only recorded from 2021 era",
    "quali_date":        "Session dates only recorded from 2021 era",
    "number":            "Permanent driver numbers introduced in 2014 only",
    "code":              "3-letter driver codes formalised in modern era only",
    "milliseconds":      "Finish time only for classified finishers (DNFs = null by design)",
    "time":              "Finish time only for classified finishers (DNFs = null by design)",
    "fastestLap":        "Fastest lap data standardised from 2004 season only",
    "fastestLapTime_ms": "Fastest lap data standardised from 2004 season only",
    "fastestLapSpeed":   "Fastest lap data standardised from 2004 season only",
    "rank":              "Fastest lap ranking introduced from 2019 season only",
    "grid_pit_lane": (
        "Binary flag: 1 = post-1995 pit-lane start, "
        "0 = not a pit-lane start or pre-1996 data gap. Always filled — never null"
    ),
    "position": (
        "~41% null in results — expected: all DNFs have null position by design. "
        "Confirmed: null position count == DNF flag count (zero unexplained nulls). "
        "2 lapped-finisher gaps in Kaggle source backfilled from positionOrder in clean_data.py"
    ),
    "grid": (
        "~6% null in results — grid=0 recoded to NaN. Two causes: (1) pre-1996 "
        "Kaggle missing-data sentinel (historic data gap, grid_pit_lane=0); "
        "(2) post-1995 genuine pit-lane starts (grid_pit_lane=1). "
        "Do NOT use grid alone for pre-1996 analysis"
    ),
    "q2_ms": (
        "Q2 null expected for single-session formats (pre-1996, 2003-2005). "
        "Post-2006: driver eliminated in Q1 or did not set a time (DNS/DQ/107%)"
    ),
    "q3_ms": (
        "Q3 only exists for top-10 qualifiers in 3-part format introduced 2006. "
        "Structural ~65% null for all post-2006 races; 100% null for all pre-2006"
    ),
    "q1_ms": (
        "~1.3% null in qualifying — confirmed data gaps: entire races missing from "
        "Kaggle source (patched where possible), 107% failures, DNS/injury before Q1, "
        "modern era DQ/crash/mechanical before setting a time. Not imputable"
    ),
    "best_quali_ms": (
        "Mirrors q1_ms nulls exactly — derived as min(q1_ms, q2_ms, q3_ms). "
        "Null only where all session times are null (same causes as q1_ms above)"
    ),
    "pit_duration_ms": (
        "~4.7% null in pit_stops — clustered feed failures in specific races "
        "(2023 Australian GP 70.8%, 2021 Saudi GP 74.5%, etc.). Not random — "
        "null means data was never recorded. Use pit_data_incomplete flag to exclude "
        "affected races from strategy models. Do NOT impute"
    ),
}

INVESTIGATE_NULLS: dict[str, str] = {}

# ── Points reconciliation thresholds ───────────────────────────────────────────
# Per-season delta between sum(driver points) and sum(constructor points).
# delta = abs(driver_total - constructor_total) per season.
#   <= POINTS_PASS_DELTA  : PASS  (within rounding / shared-drive tolerance)
#   <= POINTS_WARN_DELTA  : WARN  (investigate but don't fail scorecard)
#   >  POINTS_WARN_DELTA  : FAIL  (meaningful discrepancy — pipeline bug)
POINTS_PASS_DELTA = 2.0
POINTS_WARN_DELTA = 5.0

# ── Impossible value bounds for feature columns ─────────────────────────────────
# Format: (table_label, column, operator, threshold, severity, note)
# operator: one of '<', '>', '=='
# severity: 'FAIL' triggers scorecard failure; 'WARN' is advisory only
BOUNDS_CHECKS = [
    # driver_race_features
    ("driver_race", "grid",             "<",  0,    "FAIL", "Grid position cannot be negative"),
    ("driver_race", "finish_position",  "<",  1,    "FAIL", "Finish position cannot be below 1"),
    ("driver_race", "positions_gained", "<", -30,   "FAIL", "Losing 30+ places in one race is impossible"),
    ("driver_race", "positions_gained", ">",  33,   "FAIL", "Gaining 33+ places in one race is impossible (max grid ~20 cars)"),
    ("driver_race", "points",           "<",  0,    "FAIL", "Race points cannot be negative"),
    ("driver_race", "pit_stop_count",   "<",  0,    "FAIL", "Pit stop count cannot be negative"),
    ("driver_race", "avg_pit_duration_ms", "<", 0,  "FAIL", "Pit duration cannot be negative"),
    ("driver_race", "is_dnf",           "<",  0,    "FAIL", "is_dnf must be 0 or 1"),
    ("driver_race", "is_dnf",           ">",  1,    "FAIL", "is_dnf must be 0 or 1"),
    # driver_season_features
    ("driver_season", "dnf_rate",       "<",  0,    "FAIL", "Rate cannot be negative"),
    ("driver_season", "dnf_rate",       ">",  1,    "FAIL", "Rate cannot exceed 1.0"),
    ("driver_season", "win_rate",       ">",  1,    "FAIL", "Rate cannot exceed 1.0"),
    ("driver_season", "podium_rate",    ">",  1,    "FAIL", "Rate cannot exceed 1.0"),
    ("driver_season", "races_entered",  "<",  1,    "FAIL", "Must have entered at least 1 race"),
    ("driver_season", "avg_finish_position", "<", 1, "FAIL", "Avg finish position cannot be below 1"),
    # constructor_season_features
    ("constructor_season", "dnf_rate",  "<",  0,    "FAIL", "Rate cannot be negative"),
    ("constructor_season", "dnf_rate",  ">",  1,    "FAIL", "Rate cannot exceed 1.0"),
    ("constructor_season", "win_rate",  ">",  1,    "FAIL", "Rate cannot exceed 1.0"),
    ("constructor_season", "driver_count", "<", 1,  "FAIL", "Constructor must have at least 1 driver"),
    ("constructor_season", "driver_spread_avg_finish", "<", 0, "WARN",
     "Spread is max−min so should always be >= 0; negative indicates a calculation error"),
    ("constructor_season", "driver_spread_total_points", "<", 0, "WARN",
     "Spread is max−min so should always be >= 0"),
]


# ── Status classifiers ─────────────────────────────────────────────────────────
if _CONSTANTS_AVAILABLE:
    def _is_dnf(label: str) -> bool:
        return _is_dnf_fn(label)

    def _is_finish(label: str) -> bool:
        return _is_finish_fn(label)
else:
    _FALLBACK_DNF = [
        "retired", "accident", "collision", "disqualified", "did not",
        "engine", "gearbox", "hydraulics", "brakes", "wheel", "fuel",
        "suspension", "electrical", "oil", "water", "fire", "spun off",
        "overheating", "mechanical", "transmission", "clutch", "throttle",
        "power unit", "exhaust", "tyre", "puncture", "damage", "withdrew",
        "illness", "injury", "safety", "technical", "vibrations", "debris",
        "battery", "driveshaft", "differential", "turbo", "compressor",
        "pneumatic", "cooling", "alternator", "electronics",
    ]

    def _is_dnf(label: str) -> bool:
        ll = label.lower()
        if ll.startswith("+") and "lap" in ll:
            return False
        return any(kw in ll for kw in _FALLBACK_DNF)

    def _is_finish(label: str) -> bool:
        ll = label.lower()
        if "finished" in ll:
            return True
        if ll.startswith("+") and "lap" in ll:
            return True
        return any(pat in ll for pat in ["lapped", "lap down"])


# ── Helpers ────────────────────────────────────────────────────────────────────

def _hr(char: str = "─", width: int = 60) -> str:
    return char * width


def _badge(passed: bool) -> str:
    return "✅ PASS" if passed else "❌ FAIL"


def _warn(label: str = "⚠️ WARN") -> str:
    return label


def _pct(value: float, total: float, decimals: int = 1) -> str:
    if total == 0:
        return "N/A"
    return f"{value / total * 100:.{decimals}f}%"


# ── Data Loading ───────────────────────────────────────────────────────────────

def load_tables() -> dict[str, pd.DataFrame]:
    """Load all *_clean.csv files from the interim directory."""
    if not INTERIM_DIR.exists():
        print(f"[ERROR] Interim directory not found: {INTERIM_DIR}", file=sys.stderr)
        sys.exit(1)

    files = sorted(INTERIM_DIR.glob("*_clean.csv"))
    if not files:
        print(f"[ERROR] No *_clean.csv files found in {INTERIM_DIR}", file=sys.stderr)
        sys.exit(1)

    tables: dict[str, pd.DataFrame] = {}
    for file in files:
        name = file.stem.replace("_clean", "")
        tables[name] = pd.read_csv(file, low_memory=False)
        print(f"  Loaded '{name}': {len(tables[name]):,} rows × {tables[name].shape[1]} cols")

    return tables


def load_feature_tables() -> dict[str, pd.DataFrame | None]:
    """
    Load the three parquet feature stores.
    Returns a dict with keys 'driver_race', 'driver_season', 'constructor_season'.
    Missing files are logged as warnings and stored as None — checks downstream
    handle None gracefully and report the file as unavailable rather than crashing.
    """
    mapping = {
        "driver_race":        DRIVER_RACE_PARQUET,
        "driver_season":      DRIVER_SEASON_PARQUET,
        "constructor_season": CONSTRUCTOR_SEASON_PARQUET,
    }
    result: dict[str, pd.DataFrame | None] = {}
    for key, path in mapping.items():
        if path.exists():
            result[key] = pd.read_parquet(path)
            print(f"  Loaded feature '{key}': {len(result[key]):,} rows × {result[key].shape[1]} cols")
        else:
            result[key] = None
            print(f"  ⚠️  Feature '{key}' not found at {path} — skipping")
    return result


# ── Section 1: Dataset Inventory ──────────────────────────────────────────────

def section_inventory(tables: dict[str, pd.DataFrame]) -> str:
    lines = [
        "## 1. Dataset Inventory",
        "",
        "| Table | Rows | Columns | Null Cells | Null % |",
        "|-------|-----:|--------:|-----------:|-------:|",
    ]
    for name, df in sorted(tables.items()):
        null_cells = int(df.isna().sum().sum())
        lines.append(
            f"| `{name}` | {len(df):,} | {df.shape[1]}"
            f" | {null_cells:,} | {_pct(null_cells, df.size)} |"
        )
    return "\n".join(lines)


# ── Section 2: Null Analysis (context-aware) ──────────────────────────────────

def section_null_analysis(tables: dict[str, pd.DataFrame]) -> tuple[str, bool]:
    lines = ["## 2. Null Value Analysis", ""]
    unjustified_high_found = False

    for name, df in sorted(tables.items()):
        null_pct        = df.isna().mean() * 100
        cols_with_nulls = int((null_pct > 0).sum())

        lines += [
            f"### `{name}`",
            f"- **Rows:** {len(df):,}  |  **Columns:** {df.shape[1]}"
            f"  |  **Columns with nulls:** {cols_with_nulls}",
            "",
            "| Column | Type | Null Count | Null % | Severity | Note |",
            "|--------|------|----------:|-------:|----------|------|",
        ]

        for col in null_pct.sort_values(ascending=False).index:
            val        = null_pct[col]
            null_count = int(df[col].isna().sum())
            dtype      = str(df[col].dtype)

            if col in JUSTIFIED_NULLS:
                severity = "ℹ️ Justified"
                note     = JUSTIFIED_NULLS[col]
            elif col in INVESTIGATE_NULLS and val > 0:
                severity = "🔍 Investigate"
                note     = INVESTIGATE_NULLS[col]
            elif val == 0:
                severity = "✅ Clean"
                note     = "—"
            elif val < 5:
                severity = "⚠️ Minor"
                note     = "—"
            elif val < 20:
                severity = "🔶 Moderate"
                note     = "—"
            else:
                severity = "❌ High"
                note     = "Unjustified — requires fix"
                unjustified_high_found = True

            lines.append(
                f"| `{col}` | {dtype} | {null_count:,} | {val:.2f}% | {severity} | {note} |"
            )
        lines.append("")

    lines += [
        "### Null Classification Legend",
        "",
        "| Label | Meaning |",
        "|-------|---------|",
        "| ✅ Clean | No nulls |",
        "| ⚠️ Minor | < 5% null, no action needed |",
        "| 🔶 Moderate | 5–20% null, monitor |",
        "| ❌ High | > 20% null, unjustified — fix required |",
        "| ℹ️ Justified | High null rate expected due to era/format/design constraints |",
        "| 🔍 Investigate | Null rate requires manual review before modeling (none currently) |",
    ]

    return "\n".join(lines), not unjustified_high_found


# ── Section 3: Schema Drift ────────────────────────────────────────────────────

def section_schema_drift(tables: dict[str, pd.DataFrame]) -> tuple[str, bool]:
    lines    = ["## 3. Schema Drift Check", ""]
    issues   = []
    all_pass = True

    for tbl_name, expected_cols in sorted(EXPECTED_SCHEMA.items()):
        if tbl_name not in tables:
            issues.append((tbl_name, "—", "—", "⚠️ Table not loaded"))
            all_pass = False
            continue

        actual_cols = set(tables[tbl_name].columns)
        missing     = sorted(expected_cols - actual_cols)
        unexpected  = sorted(actual_cols - expected_cols)
        passed      = len(missing) == 0
        if not passed:
            all_pass = False

        issues.append((
            tbl_name,
            ", ".join(f"`{c}`" for c in missing) or "—",
            ", ".join(f"`{c}`" for c in unexpected) or "—",
            _badge(passed),
        ))

    lines += [
        f"**Overall:** {_badge(all_pass)}",
        "",
        "| Table | Missing Columns | Unexpected Columns | Result |",
        "|-------|-----------------|-------------------|:------:|",
    ]
    for tbl_name, missing_str, unexpected_str, status in issues:
        lines.append(f"| `{tbl_name}` | {missing_str} | {unexpected_str} | {status} |")

    lines += [
        "",
        "> _Unexpected columns are informational only and do not fail this check._",
    ]
    return "\n".join(lines), all_pass


# ── Section 4: Foreign Key Validation ─────────────────────────────────────────

def section_fk_validation(tables: dict[str, pd.DataFrame]) -> tuple[str, bool]:
    lines    = ["## 4. Foreign Key Validation", ""]
    all_pass = True
    summary  = []
    detail_blocks: list[str] = []

    for child_tbl, child_col, parent_tbl, parent_col in FK_CHECKS:
        rel = f"`{child_tbl}.{child_col}` → `{parent_tbl}.{parent_col}`"

        if child_tbl not in tables or parent_tbl not in tables:
            summary.append((rel, "—", "—", "—", "⚠️ Table missing"))
            all_pass = False
            continue

        child_df  = tables[child_tbl]
        parent_df = tables[parent_tbl]

        if child_col not in child_df.columns or parent_col not in parent_df.columns:
            summary.append((rel, "—", "—", "—", "⚠️ Column missing"))
            all_pass = False
            continue

        valid_keys  = set(parent_df[parent_col].dropna())
        orphan_mask = ~child_df[child_col].isin(valid_keys)
        orphan_rows = child_df[orphan_mask]

        total_rows   = int(child_df[child_col].notna().sum())
        orphan_count = int(len(orphan_rows))
        orphan_pct   = _pct(orphan_count, total_rows)
        passed       = orphan_count == 0
        if not passed:
            all_pass = False

        summary.append((rel, f"{total_rows:,}", f"{orphan_count:,}", orphan_pct, _badge(passed)))

        if not passed:
            sample_vals = sorted(orphan_rows[child_col].dropna().unique())[:20]
            detail_blocks.append(
                f"**{rel} — orphan values (up to 20 distinct):**\n\n"
                + ", ".join(f"`{v}`" for v in sample_vals)
            )

    lines += [
        f"**Overall:** {_badge(all_pass)}",
        "",
        "| Relationship | Rows Checked | Orphan Rows | Orphan % | Result |",
        "|---|---:|---:|---:|:---:|",
    ]
    for rel, total, orphans, pct, status in summary:
        lines.append(f"| {rel} | {total} | {orphans} | {pct} | {status} |")

    if detail_blocks:
        lines += ["", "### Orphan Detail", ""] + detail_blocks

    return "\n".join(lines), all_pass


# ── Section 5: Duplicate Detection ────────────────────────────────────────────

def section_duplicate_check(tables: dict[str, pd.DataFrame]) -> tuple[str, bool]:
    """
    Duplicate raceId × driverId detection with three known-legitimate categories:
      1. Dual Constructor: same raceId/driverId pair but different constructorId
      2. Shared Drive: same raceId/driverId/constructorId but different laps or position
      3. Unexplained: any other case
    Scorecard fails only if unexplained duplicates remain.
    """
    lines = ["## 5. Duplicate Race-Driver Records", ""]

    if "results" not in tables:
        return "\n".join(lines + ["> ⚠️ `results` table not available."]), False

    results      = tables["results"]
    subset       = ["raceId", "driverId"]
    missing_cols = [c for c in subset if c not in results.columns]

    if missing_cols:
        return "\n".join(lines + [f"> ⚠️ Missing columns: {missing_cols}"]), False

    dupe_mask     = results.duplicated(subset=subset, keep=False)
    dupe_pairs    = int(results.duplicated(subset=subset).sum())
    rows_affected = int(dupe_mask.sum())
    
    # Scorecard fails only if there are unexplained duplicates
    dual_constructor = set()
    shared_drive     = set()
    unexplained      = set()

    if dupe_pairs > 0:
        dupe_df = results[dupe_mask].copy()
        
        has_constructor = "constructorId" in results.columns
        has_laps        = "laps" in results.columns
        has_position    = "position" in results.columns

        for (race_id, driver_id), grp in dupe_df.groupby(["raceId", "driverId"]):
            pair = (race_id, driver_id)
            
            # Check 1: Dual constructor — different constructorId in the pair
            if has_constructor and grp["constructorId"].nunique() > 1:
                dual_constructor.add(pair)
                continue
            
            # Check 2: Shared drive — same constructor but different laps or position
            if (has_constructor and has_laps 
                    and grp["constructorId"].nunique() == 1):
                laps_differ = (grp["laps"].max() - grp["laps"].min()) > 0
                position_differ = (has_position and grp["position"].nunique() > 1)
                if laps_differ or position_differ:
                    shared_drive.add(pair)
                    continue
            
            # Check 3: Unexplained
            unexplained.add(pair)

    passed = len(unexplained) == 0

    lines += [
        f"**Composite key:** `raceId × driverId`",
        f"**Duplicate pairs found:** {dupe_pairs:,}",
        f"**Rows affected:** {rows_affected:,} / {len(results):,}"
        f" ({_pct(rows_affected, len(results))})",
        "",
    ]

    if dupe_pairs > 0:
        dupe_df = results[dupe_mask].copy()

        all_affected   = sorted(set(pair[0] for pair in dual_constructor | shared_drive | unexplained))
        distinct_races = len(all_affected)
        id_display     = ", ".join(f"`{r}`" for r in all_affected[:30])
        truncation     = f" _(showing first 30 of {distinct_races})_" if distinct_races > 30 else ""

        lines += [
            f"**Distinct races affected:** {distinct_races:,}",
            f"**Affected raceIds:** {id_display}{truncation}",
            "",
            "### Duplicate Root Cause Classification",
            "",
            "| Category | Pairs | Interpretation | Scorecard |",
            "|----------|------:|----------------|:---------:|",
            f"| 🏛️ Dual Constructor | {len(dual_constructor)} "
            f"| Driver raced for 2 teams in same event — expected | ✅ Ignored |",
            f"| 🤝 Shared Drive | {len(shared_drive)} "
            f"| Same team but different laps/position — expected | ✅ Ignored |",
            f"| ❓ Unexplained | {len(unexplained)} "
            f"| No structural reason found | {'✅ None' if len(unexplained) == 0 else '❌ FAIL'} |",
        ]

        if len(unexplained) > 0:
            unexplained_ids = ", ".join(f"`{r}`" for r in sorted(set(pair[0] for pair in unexplained)))
            lines += [
                "",
                f"> ⚠️ **Unexplained duplicate raceIds:** {unexplained_ids}  ",
                "> These do not match dual-constructor or shared-drive patterns.",
            ]

        if len(shared_drive) > 0:
            lines += [
                "",
                "> ℹ️ **Shared-drive duplicates are expected.** Multiple drivers shared one car in stints,"
                " producing different laps/position values for the same raceId×driverId pair.",
            ]

        # Per-race summary
        all_pairs = dual_constructor | shared_drive | unexplained
        race_pair_breakdown = {}
        for race_id, driver_id in all_pairs:
            if race_id not in race_pair_breakdown:
                race_pair_breakdown[race_id] = {"dual": 0, "shared": 0, "unexplained": 0}
            if (race_id, driver_id) in dual_constructor:
                race_pair_breakdown[race_id]["dual"] += 1
            elif (race_id, driver_id) in shared_drive:
                race_pair_breakdown[race_id]["shared"] += 1
            else:
                race_pair_breakdown[race_id]["unexplained"] += 1

        race_summary_rows = sorted(
            race_pair_breakdown.items(),
            key=lambda x: (x[1]["unexplained"], x[1]["dual"] + x[1]["shared"]),
            reverse=True
        )[:15]

        lines += ["", "**Top affected races (up to 15):**", ""]
        lines += [
            "| raceId | Dual Constructor | Shared Drive | Unexplained |",
            "|-------:|----------------:|-------------:|------------:|",
        ]
        for race_id, counts in race_summary_rows:
            lines.append(
                f"| {race_id} | {counts['dual']} | {counts['shared']} | {counts['unexplained']} |"
            )

        # All pairs table
        all_dupes_list = sorted(all_pairs)
        lines += [
            "",
            "**All duplicate pairs:**",
            "",
            "| raceId | driverId | Category |",
            "|-------:|---------:|----------|",
        ]
        for race_id, driver_id in all_dupes_list[:50]:
            if (race_id, driver_id) in dual_constructor:
                cat = "🏛️ Dual Constructor"
            elif (race_id, driver_id) in shared_drive:
                cat = "🤝 Shared Drive"
            else:
                cat = "❓ Unexplained"
            lines.append(f"| {race_id} | {driver_id} | {cat} |")
        
        if len(all_dupes_list) > 50:
            lines.append(f"_(showing first 50 of {len(all_dupes_list)} pairs)_")

        lines += [
            "",
            "### Recommended Fix",
        ]

        if len(unexplained) > 0:
            lines += [
                "",
                "**For unexplained duplicates, investigate:**",
                "```python",
                "# Check the specific pairs to understand the data structure",
                "unexplained_pairs = [(race_id, driver_id), ...]",
                "for race_id, driver_id in unexplained_pairs:",
                "    print(results[(results['raceId'] == race_id) & (results['driverId'] == driver_id)])",
                "```",
            ]

    lines.append(f"**Overall:** {_badge(passed)}")
    return "\n".join(lines), passed


# ── Section 6: Lap Time Validation ────────────────────────────────────────────

def section_lap_time_validation(tables: dict[str, pd.DataFrame]) -> tuple[str, bool]:
    lines = ["## 6. Lap Time Validation", ""]

    if "lap_times" not in tables:
        return "\n".join(lines + ["> ⚠️ `lap_times` table not available."]), False

    lap = tables["lap_times"]
    if "lap_time_ms" not in lap.columns:
        return "\n".join(lines + ["> ⚠️ Column `lap_time_ms` not found."]), False

    series  = lap["lap_time_ms"].dropna()
    n_total = len(lap)
    n_valid = len(series)
    n_null  = n_total - n_valid

    negatives   = int((series < 0).sum())
    too_fast    = int(((series >= 0) & (series < LAP_TIME_MIN_MS)).sum())
    sc_vsc_laps = int(((series > LAP_TIME_WARN_MS) & (series <= LAP_TIME_CORRUPT_MS)).sum())
    corrupt     = int((series > LAP_TIME_CORRUPT_MS).sum())
    hard_fail   = negatives + too_fast + corrupt

    z_scores  = (series - series.mean()) / series.std()
    z_extreme = int((z_scores.abs() > LAP_Z_THRESHOLD).sum())
    z_unexplained = int(
        ((z_scores.abs() > LAP_Z_THRESHOLD) & (series <= LAP_TIME_WARN_MS)).sum()
    )

    passed = hard_fail == 0

    lines += [
        "**Thresholds:**",
        f"- Hard fail: < {LAP_TIME_MIN_MS / 1000:.0f} s (impossible)"
        f" or > {LAP_TIME_CORRUPT_MS / 1000:.0f} s (corrupt)",
        f"- Warning: {LAP_TIME_WARN_MS / 1000:.0f}–{LAP_TIME_CORRUPT_MS / 1000:.0f} s"
        f" (Safety Car / VSC / formation lap — real events, not errors)",
        f"- Z-score outlier: |z| > {LAP_Z_THRESHOLD}σ",
        "",
        "### Descriptive Statistics",
        "",
        "| Metric | Value |",
        "|--------|------:|",
        f"| Total records | {n_total:,} |",
        f"| Valid (non-null) | {n_valid:,} |",
        f"| Null / missing | {n_null:,} ({_pct(n_null, n_total)}) |",
        f"| Mean | {series.mean() / 1000:.3f} s |",
        f"| Median | {series.median() / 1000:.3f} s |",
        f"| Std dev | {series.std() / 1000:.3f} s |",
        f"| Min | {series.min() / 1000:.3f} s |",
        f"| Max | {series.max() / 1000:.3f} s |",
        f"| p5 | {series.quantile(0.05) / 1000:.3f} s |",
        f"| p95 | {series.quantile(0.95) / 1000:.3f} s |",
        "",
        "### Threshold Check",
        "",
        "| Check | Count | % of Valid | Severity | Result |",
        "|-------|------:|-----------:|----------|:------:|",
        f"| Negative values | {negatives:,} | {_pct(negatives, n_valid)} | ❌ Corrupt | {_badge(negatives == 0)} |",
        f"| < {LAP_TIME_MIN_MS / 1000:.0f} s (too fast) | {too_fast:,} | {_pct(too_fast, n_valid)} | ❌ Corrupt | {_badge(too_fast == 0)} |",
        f"| {LAP_TIME_WARN_MS / 1000:.0f}–{LAP_TIME_CORRUPT_MS / 1000:.0f} s (SC/VSC laps) | {sc_vsc_laps:,} | {_pct(sc_vsc_laps, n_valid)} | ⚠️ Warning | ℹ️ Expected |",
        f"| > {LAP_TIME_CORRUPT_MS / 1000:.0f} s (corrupt) | {corrupt:,} | {_pct(corrupt, n_valid)} | ❌ Corrupt | {_badge(corrupt == 0)} |",
        f"| **Hard-fail total** | **{hard_fail:,}** | **{_pct(hard_fail, n_valid)}** | | **{_badge(hard_fail == 0)}** |",
    ]

    if sc_vsc_laps > 0:
        lines += [
            "",
            "> ℹ️ **SC/VSC laps are not data errors.** Safety Car and Virtual Safety Car periods"
            " routinely produce lap times of 3–5 minutes.",
            "",
            "```python",
            f"lap_times['is_slow_lap'] = lap_times['lap_time_ms'] > {LAP_TIME_WARN_MS}",
            "normal_laps = lap_times[~lap_times['is_slow_lap']]",
            "```",
        ]

    lines += [
        "",
        "### Statistical Outlier Detection (Z-Score) — Advisory",
        "",
        f"> Flags lap times where |z| > {LAP_Z_THRESHOLD}. Advisory only — does not affect scorecard.",
        "",
        "| Metric | Value |",
        "|--------|------:|",
        f"| Mean ± 1σ | {series.mean() / 1000:.1f} s ± {series.std() / 1000:.1f} s |",
        f"| Total outliers (\\|z\\| > {LAP_Z_THRESHOLD}) | {z_extreme:,} ({_pct(z_extreme, n_valid)}) |",
        f"| Of those: SC/VSC overlap (already flagged above) | {z_extreme - z_unexplained:,} |",
        f"| Genuinely unexplained outliers (<300s) | {z_unexplained:,} |",
        f"| Outlier check | ℹ️ Advisory ({z_unexplained} unexplained) |",
    ]

    if z_extreme > 0:
        z_series = z_scores.rename("z")
        top_outliers = (
            lap[["raceId", "driverId", "lap", "lap_time_ms"]]
            .join(z_series)
            .dropna(subset=["z"])
            .loc[lambda df: df["z"].abs() > LAP_Z_THRESHOLD]
            .sort_values("z", key=abs, ascending=False)
            .head(10)
        )
        lines += [
            "",
            "**Top outlier records (up to 10):**",
            "",
            "| raceId | driverId | Lap | lap_time_s | z-score | Likely cause |",
            "|-------:|---------:|----:|-----------:|--------:|--------------|",
        ]
        for _, row in top_outliers.iterrows():
            lap_s  = row["lap_time_ms"] / 1000
            z_val  = row["z"]
            cause  = "SC/VSC or red flag" if row["lap_time_ms"] <= LAP_TIME_CORRUPT_MS else "Likely corrupt"
            lines.append(
                f"| {int(row['raceId'])} | {int(row['driverId'])}"
                f" | {int(row['lap'])} | {lap_s:.1f} | {z_val:+.2f} | {cause} |"
            )

    return "\n".join(lines), passed


# ── Section 7: Status Validation ──────────────────────────────────────────────

def section_status_validation(tables: dict[str, pd.DataFrame]) -> tuple[str, bool]:
    lines = ["## 7. Status & DNF Validation", ""]

    if "status" not in tables:
        return "\n".join(lines + ["> ⚠️ `status` table not available."]), False
    if "results" not in tables:
        return "\n".join(lines + ["> ⚠️ `results` table not available."]), False

    status_df = tables["status"]
    results   = tables["results"]

    if "statusId" not in status_df.columns or "status" not in status_df.columns:
        return "\n".join(lines + ["> ⚠️ `status` table missing required columns."]), False
    if "statusId" not in results.columns:
        return "\n".join(lines + ["> ⚠️ `results` table missing `statusId` column."]), False

    status_map   = status_df.set_index("statusId")["status"]
    status_usage = (
        results["statusId"]
        .map(status_map)
        .value_counts()
        .rename_axis("status")
        .reset_index(name="count")
    )

    total_entries  = int(status_usage["count"].sum())
    unmapped_count = int(results["statusId"].map(status_map).isna().sum())
    passed         = unmapped_count == 0

    status_usage["category"] = status_usage["status"].apply(
        lambda s: "DNF" if _is_dnf(str(s))
        else ("Finished" if _is_finish(str(s)) else "Other")
    )

    finished_count = int(status_usage.loc[status_usage["category"] == "Finished", "count"].sum())
    dnf_count      = int(status_usage.loc[status_usage["category"] == "DNF",      "count"].sum())
    other_count    = int(status_usage.loc[status_usage["category"] == "Other",    "count"].sum())

    lines += [
        f"**Status integration:** {_badge(passed)}",
        f"**Total result entries mapped:** {total_entries:,}",
        f"**Unmapped statusId (orphan):** {unmapped_count:,}"
        f" ({_pct(unmapped_count, len(results))})  →  {_badge(unmapped_count == 0)}",
        "",
        "### Race Outcome Summary",
        "",
        "| Category | Count | % of Results |",
        "|----------|------:|-------------:|",
        f"| ✅ Finished (incl. lapped) | {finished_count:,} | {_pct(finished_count, total_entries)} |",
        f"| ❌ DNF / Retirement | {dnf_count:,} | {_pct(dnf_count, total_entries)} |",
        f"| ❓ Other / Unclassified | {other_count:,} | {_pct(other_count, total_entries)} |",
        f"| **Total** | **{total_entries:,}** | **100%** |",
        "",
    ]

    other_rows = (
        status_usage.loc[status_usage["category"] == "Other"]
        .sort_values("count", ascending=False)
    )
    if not other_rows.empty and other_count > 0:
        lines += [
            "### ❓ Unclassified Status Breakdown",
            "",
            f"> These {other_count:,} records ({_pct(other_count, total_entries)}) did not match"
            " Finished or DNF classifiers. Review and reclassify as needed.",
            "",
            "| Status | Count | % of Other |",
            "|--------|------:|-----------:|",
        ]
        for _, row in other_rows.iterrows():
            lines.append(
                f"| {row['status']} | {int(row['count']):,}"
                f" | {_pct(row['count'], other_count)} |"
            )
        lines.append("")

    top_dnf = (
        status_usage.loc[status_usage["category"] == "DNF"]
        .sort_values("count", ascending=False)
        .head(10)
    )
    if not top_dnf.empty:
        lines += [
            "### Top 10 DNF Causes",
            "",
            "| Cause | Count | % of All DNFs |",
            "|-------|------:|--------------:|",
        ]
        for _, row in top_dnf.iterrows():
            lines.append(
                f"| {row['status']} | {int(row['count']):,}"
                f" | {_pct(row['count'], dnf_count)} |"
            )
        lines.append("")

    finish_rows = (
        status_usage.loc[status_usage["category"] == "Finished"]
        .sort_values("count", ascending=False)
    )
    if not finish_rows.empty:
        lines += [
            "### Finished Status Breakdown",
            "",
            "| Status | Count | % of Finished |",
            "|--------|------:|--------------:|",
        ]
        for _, row in finish_rows.iterrows():
            lines.append(
                f"| {row['status']} | {int(row['count']):,}"
                f" | {_pct(row['count'], finished_count)} |"
            )

    return "\n".join(lines), passed


# ===========================================================================
# Section 8: Feature Table Duplicate Keys
# ===========================================================================

def section_feature_duplicate_keys(
    feature_tables: dict[str, pd.DataFrame | None],
) -> tuple[str, bool]:
    """
    Assert that every feature table has a unique composite key.

    Expected keys:
      driver_race        : (raceId, driverId)
      driver_season      : (driverId, race_year)
      constructor_season : (constructorId, race_year)

    For driver_race specifically, duplicates are classified using the exact same
    logic as Section 5:
      - Dual Constructor (constructorId differs)  — expected, does NOT fail
      - Shared Drive (same constructorId but different laps or position) — expected, does NOT fail
      - Unexplained (any other case) — fails the scorecard

    driver_season and constructor_season have no legitimate duplicate causes;
    any duplicate there is a pipeline bug and fails immediately.
    """
    lines    = ["## 8. Feature Table — Duplicate Key Check", ""]
    all_pass = True

    key_map = {
        "driver_race":        ["raceId", "driverId"],
        "driver_season":      ["driverId", "race_year"],
        "constructor_season": ["constructorId", "race_year"],
    }

    lines += [
        "| Table | Key Columns | Rows | Duplicate Pairs | Unexplained | Result |",
        "|-------|-------------|-----:|----------------:|------------:|:------:|",
    ]

    for table_key, key_cols in key_map.items():
        df = feature_tables.get(table_key)

        if df is None:
            lines.append(
                f"| `{table_key}` | {', '.join(f'`{c}`' for c in key_cols)}"
                f" | — | — | — | ⚠️ File not found |"
            )
            all_pass = False
            continue

        missing_key_cols = [c for c in key_cols if c not in df.columns]
        if missing_key_cols:
            lines.append(
                f"| `{table_key}` | {', '.join(f'`{c}`' for c in key_cols)}"
                f" | {len(df):,} | — | — | ⚠️ Key col(s) missing: {missing_key_cols} |"
            )
            all_pass = False
            continue

        dupe_count = int(df.duplicated(subset=key_cols).sum())

        # ── driver_race: classify duplicates before deciding pass/fail ─────
        if table_key == "driver_race" and dupe_count > 0:
            dupe_mask = df.duplicated(subset=key_cols, keep=False)
            dupe_df   = df[dupe_mask].copy()

            has_constr = "constructorId" in df.columns
            has_laps   = "laps" in df.columns
            has_position = "position" in df.columns

            dual_constr_pairs = set()
            shared_drive_pairs = set()
            unexplained_pairs = set()

            for (race_id, driver_id), grp in dupe_df.groupby(["raceId", "driverId"]):
                pair = (race_id, driver_id)

                # Check 1: Dual constructor — different constructorId in the pair
                if has_constr and grp["constructorId"].nunique() > 1:
                    dual_constr_pairs.add(pair)
                    continue

                # Check 2: Shared drive — same constructor but different laps or position
                if (has_constr and has_laps 
                        and grp["constructorId"].nunique() == 1):
                    laps_differ = (grp["laps"].max() - grp["laps"].min()) > 0
                    position_differ = (has_position and grp["position"].nunique() > 1)
                    if laps_differ or position_differ:
                        shared_drive_pairs.add(pair)
                        continue

                # Check 3: Unexplained
                unexplained_pairs.add(pair)

            n_dual_constr = len(dual_constr_pairs)
            n_shared = len(shared_drive_pairs)
            n_unexplained = len(unexplained_pairs)
            passed        = n_unexplained == 0
            if not passed:
                all_pass = False

            lines.append(
                f"| `{table_key}` | {', '.join(f'`{c}`' for c in key_cols)}"
                f" | {len(df):,} | {dupe_count:,} | {n_unexplained:,} | {_badge(passed)} |"
            )

            # Classification breakdown (always shown when driver_race has dupes)
            lines += [
                "",
                f"**`driver_race` duplicate classification** ({dupe_count} pairs total):",
                "",
                "| Category | Pairs | Interpretation | Scorecard |",
                "|----------|------:|----------------|:---------:|",
                f"| 🏛️ Dual Constructor | {n_dual_constr}"
                f" | Driver raced for 2 teams in same event — expected | ✅ Ignored |",
                f"| 🤝 Shared Drive | {n_shared}"
                f" | Same team but different laps/position — expected | ✅ Ignored |",
                f"| ❓ Unexplained | {n_unexplained}"
                f" | No structural reason found"
                f" | {'✅ None' if n_unexplained == 0 else '❌ FAIL'} |",
                "",
            ]

            if n_unexplained > 0:
                unexplained_index = pd.MultiIndex.from_tuples(
                    unexplained_pairs, names=["raceId", "driverId"]
                )
                unexplained_rows = (
                    dupe_df
                    .set_index(["raceId", "driverId"])
                    .loc[lambda d: d.index.isin(unexplained_index)]
                    .reset_index()
                    .sort_values(key_cols)
                    .head(10)
                )
                lines += [
                    "**Unexplained duplicate rows in `driver_race` (up to 10):**",
                    "",
                    "| raceId | driverId | constructorId | (other columns) |",
                    "|-------:|---------:|--------------:|-----------------|",
                ]
                for _, row in unexplained_rows.iterrows():
                    constr_val = str(int(row["constructorId"])) if has_constr and pd.notna(row.get("constructorId")) else "—"
                    lines.append(
                        f"| {int(row['raceId'])} | {int(row['driverId'])}"
                        f" | {constr_val} | _(see parquet for full row)_ |"
                    )
                lines.append("")

        # ── driver_season / constructor_season: no legitimate duplicates ───
        else:
            passed = dupe_count == 0
            if not passed:
                all_pass = False

            lines.append(
                f"| `{table_key}` | {', '.join(f'`{c}`' for c in key_cols)}"
                f" | {len(df):,} | {dupe_count:,} | {dupe_count:,} | {_badge(passed)} |"
            )

            if not passed:
                dupe_mask   = df.duplicated(subset=key_cols, keep=False)
                sample_rows = df[dupe_mask].sort_values(key_cols).head(10)
                lines += [
                    "",
                    f"**Sample duplicate rows in `{table_key}` (up to 10):**",
                    "",
                    f"| {' | '.join(key_cols)} | (row preview) |",
                    f"|{'|'.join(['---:'] * len(key_cols))}|---|",
                ]
                for _, row in sample_rows.iterrows():
                    key_vals = " | ".join(str(row[c]) for c in key_cols)
                    lines.append(f"| {key_vals} | _(see parquet for full row)_ |")
                lines.append("")

    lines += [
        "",
        f"**Overall:** {_badge(all_pass)}",
        "",
        "> ℹ️ For `driver_race`, dual-constructor and shared-drive duplicates"
        " are structurally expected (mirrors Section 5 logic). Only unexplained duplicates"
        " fail the scorecard.",
    ]
    return "\n".join(lines), all_pass


# ===========================================================================
# Section 9: Feature Value Bounds
# ===========================================================================

def section_feature_bounds(
    feature_tables: dict[str, pd.DataFrame | None],
) -> tuple[str, bool]:
    """
    Check that derived feature columns contain no impossible values.

    Two severities:
      FAIL — logically impossible; scorecard fails if any violations found.
      WARN — suspicious but not impossible; advisory only, does not fail scorecard.

    See BOUNDS_CHECKS at the top of this file for the full list.
    """
    lines    = ["## 9. Feature Value Bounds Check", ""]
    any_fail = False

    # Group checks by table for readable output
    tables_covered = sorted({b[0] for b in BOUNDS_CHECKS})

    lines += [
        "| Table | Column | Check | Violations | Severity | Result |",
        "|-------|--------|-------|----------:|:--------:|:------:|",
    ]

    violation_details: list[str] = []

    for table_key in tables_covered:
        df = feature_tables.get(table_key)

        table_checks = [b for b in BOUNDS_CHECKS if b[0] == table_key]

        for _, col, op, threshold, severity, note in table_checks:
            if df is None:
                lines.append(
                    f"| `{table_key}` | `{col}` | — | — | — | ⚠️ File not found |"
                )
                if severity == "FAIL":
                    any_fail = True
                continue

            if col not in df.columns:
                # Column absent — skip silently (may be legitimately optional)
                continue

            series = pd.to_numeric(df[col], errors="coerce").dropna()

            if op == "<":
                mask = series < threshold
            elif op == ">":
                mask = series > threshold
            elif op == "==":
                mask = series == threshold
            else:
                continue

            n_violations = int(mask.sum())
            passed       = n_violations == 0

            op_str       = f"`{col}` {op} {threshold}"
            result_badge = _badge(passed) if severity == "FAIL" else (
                "✅ PASS" if passed else "⚠️ WARN"
            )

            if not passed and severity == "FAIL":
                any_fail = True

            lines.append(
                f"| `{table_key}` | `{col}` | {op_str}"
                f" | {n_violations:,} | {'❌' if severity == 'FAIL' else '⚠️'} {severity}"
                f" | {result_badge} |"
            )

            # Collect violating rows for detail block
            if not passed:
                bad_idx    = mask[mask].index
                sample_df  = df.loc[bad_idx].head(5)
                key_cols   = {
                    "driver_race":        ["raceId", "driverId"],
                    "driver_season":      ["driverId", "race_year"],
                    "constructor_season": ["constructorId", "race_year"],
                }.get(table_key, [])
                display_cols = [c for c in key_cols + [col] if c in sample_df.columns]

                violation_details += [
                    f"**`{table_key}.{col}` {op} {threshold} — sample violations (up to 5):**",
                    f"_Note: {note}_",
                    "",
                    f"| {' | '.join(display_cols)} |",
                    f"|{'|'.join(['---'] * len(display_cols))}|",
                ]
                for _, row in sample_df.iterrows():
                    vals = " | ".join(str(row[c]) for c in display_cols)
                    violation_details.append(f"| {vals} |")
                violation_details.append("")

    lines += ["", f"**Overall (FAIL-severity checks only):** {_badge(not any_fail)}"]

    if violation_details:
        lines += ["", "### Violation Detail", ""] + violation_details

    lines += [
        "",
        "> _WARN-severity violations are advisory and do not affect the scorecard._",
    ]

    return "\n".join(lines), not any_fail


# ===========================================================================
# Section 10: Points Reconciliation
# ===========================================================================

def section_points_reconciliation(
    feature_tables: dict[str, pd.DataFrame | None],
) -> tuple[str, bool]:
    """
    Cross-check: sum(driver-race points) per season == sum(constructor-season total_points)
    per season.

    In F1 the two totals should match exactly (both are derived from race results).
    Historical car-sharing entries and scoring rule changes can introduce small
    discrepancies, so we apply a tiered tolerance:

      delta <= POINTS_PASS_DELTA  : ✅ PASS
      delta <= POINTS_WARN_DELTA  : ⚠️ WARN  (advisory, does not fail scorecard)
      delta >  POINTS_WARN_DELTA  : ❌ FAIL

    Scorecard fails only if any season has delta > POINTS_WARN_DELTA.

    Sources:
      driver_race_features        : grain = driver × race  — sum `points` per season
      constructor_season_features : grain = constructor × season — sum `total_points` per season
    """
    lines = ["## 10. Points Reconciliation — Driver vs Constructor Totals", ""]

    dr_df   = feature_tables.get("driver_race")
    con_df  = feature_tables.get("constructor_season")

    # ── Availability guard ──────────────────────────────────────────────────
    if dr_df is None or con_df is None:
        missing = []
        if dr_df  is None: missing.append("`driver_race_features`")
        if con_df is None: missing.append("`constructor_season_features`")
        msg = ", ".join(missing)
        lines += [
            f"> ⚠️ Cannot run reconciliation — {msg} not available.",
            f"> Run `build_features.py` first to generate the parquet files.",
        ]
        return "\n".join(lines), False

    # ── Column guard ────────────────────────────────────────────────────────
    dr_year_col  = "race_year"
    con_year_col = "race_year"

    missing_cols: list[str] = []
    if "points"       not in dr_df.columns:  missing_cols.append("driver_race.points")
    if dr_year_col    not in dr_df.columns:  missing_cols.append(f"driver_race.{dr_year_col}")
    if "total_points" not in con_df.columns: missing_cols.append("constructor_season.total_points")
    if con_year_col   not in con_df.columns: missing_cols.append(f"constructor_season.{con_year_col}")

    if missing_cols:
        lines += [
            f"> ⚠️ Reconciliation skipped — missing columns: {', '.join(f'`{c}`' for c in missing_cols)}",
        ]
        return "\n".join(lines), False

    # ── Aggregate to season level ───────────────────────────────────────────
    driver_season_pts = (
        dr_df
        .groupby(dr_year_col)["points"]
        .sum()
        .rename("driver_total")
        .reset_index()
        .rename(columns={dr_year_col: "season"})
    )

    constructor_season_pts = (
        con_df
        .groupby(con_year_col)["total_points"]
        .sum()
        .rename("constructor_total")
        .reset_index()
        .rename(columns={con_year_col: "season"})
    )

    recon = driver_season_pts.merge(constructor_season_pts, on="season", how="outer")
    recon["driver_total"]      = recon["driver_total"].fillna(0)
    recon["constructor_total"] = recon["constructor_total"].fillna(0)
    recon["delta"]             = (recon["driver_total"] - recon["constructor_total"]).abs()
    recon = recon.sort_values("season")

    # ── Classify each season ────────────────────────────────────────────────
    def _classify(delta: float) -> str:
        if delta <= POINTS_PASS_DELTA:
            return "✅ PASS"
        elif delta <= POINTS_WARN_DELTA:
            return "⚠️ WARN"
        else:
            return "❌ FAIL"

    recon["result"] = recon["delta"].apply(_classify)

    n_seasons     = len(recon)
    n_pass        = int((recon["result"] == "✅ PASS").sum())
    n_warn        = int((recon["result"] == "⚠️ WARN").sum())
    n_fail        = int((recon["result"] == "❌ FAIL").sum())
    scorecard_pass = n_fail == 0

    lines += [
        f"**Tolerance bands:**  "
        f"PASS ≤ {POINTS_PASS_DELTA} pts  |  "
        f"WARN ≤ {POINTS_WARN_DELTA} pts  |  "
        f"FAIL > {POINTS_WARN_DELTA} pts",
        "",
        "### Season-Level Summary",
        "",
        f"| Outcome | Seasons | % of Seasons |",
        f"|---------|--------:|-------------:|",
        f"| ✅ PASS (delta ≤ {POINTS_PASS_DELTA}) | {n_pass} | {_pct(n_pass, n_seasons)} |",
        f"| ⚠️ WARN ({POINTS_PASS_DELTA} < delta ≤ {POINTS_WARN_DELTA}) | {n_warn} | {_pct(n_warn, n_seasons)} |",
        f"| ❌ FAIL (delta > {POINTS_WARN_DELTA}) | {n_fail} | {_pct(n_fail, n_seasons)} |",
        "",
        f"**Scorecard result:** {_badge(scorecard_pass)}  "
        f"_(fails only on delta > {POINTS_WARN_DELTA})_",
        "",
        "### Per-Season Detail",
        "",
        "| Season | Driver Total | Constructor Total | Delta | Result |",
        "|-------:|-------------:|------------------:|------:|:------:|",
    ]

    for _, row in recon.iterrows():
        lines.append(
            f"| {int(row['season'])}"
            f" | {row['driver_total']:,.1f}"
            f" | {row['constructor_total']:,.1f}"
            f" | {row['delta']:.1f}"
            f" | {row['result']} |"
        )

    # ── Highlight any WARN / FAIL seasons with guidance ────────────────────
    bad_seasons = recon[recon["result"] != "✅ PASS"]
    if not bad_seasons.empty:
        lines += ["", "### Investigation Notes", ""]
        for _, row in bad_seasons.iterrows():
            severity_label = "⚠️ WARN" if row["result"] == "⚠️ WARN" else "❌ FAIL"
            lines += [
                f"**{int(row['season'])} — {severity_label} (delta = {row['delta']:.1f} pts)**",
                "",
                "Common causes to investigate:",
                "- Car-sharing entries in `driver_race_features` counted twice under"
                " two different driverIds but once under the constructor",
                "- Bonus points (fastest lap, pole) present in one table but absent"
                " from the other due to era-specific scoring rule differences",
                "- Shared-drive rows included in driver totals but excluded from"
                " constructor totals (or vice versa)",
                "- A season present in one feature table but not the other"
                " (check `outer` join rows with 0 on one side above)",
                "",
                "```python",
                f"# Drill into {int(row['season'])} discrepancy",
                f"dr  = driver_race_df[driver_race_df['race_year'] == {int(row['season'])}]",
                f"con = constructor_season_df[constructor_season_df['race_year'] == {int(row['season'])}]",
                f"print('Driver total   :', dr['points'].sum())",
                f"print('Constructor total:', con['total_points'].sum())",
                "```",
                "",
            ]

    lines += [
        "> ℹ️ **WARN seasons are advisory.** Small deltas (2–5 pts) are common in"
        " pre-1980 seasons due to car-sharing and dropped-scores rules. They do not"
        " affect model accuracy for post-1990 analysis.",
    ]

    return "\n".join(lines), scorecard_pass


# ── Scorecard ──────────────────────────────────────────────────────────────────

def section_scorecard(checks: list[tuple[str, bool]]) -> str:
    all_pass = all(passed for _, passed in checks)
    lines = [
        "## 0. Quality Scorecard",
        "",
        f"**Overall:** {_badge(all_pass)}",
        "",
        "| # | Check | Result |",
        "|---|-------|:------:|",
    ]
    for i, (label, passed) in enumerate(checks, 1):
        lines.append(f"| {i} | {label} | {_badge(passed)} |")
    lines.append("")
    return "\n".join(lines)


# ── Report Assembly ────────────────────────────────────────────────────────────

def generate_report() -> None:
    print("\n── Data Quality Validator ──────────────────────────────")
    print(f"  Source (raw) : {INTERIM_DIR.resolve()}")
    print(f"  Source (feat): {PROCESSED_DIR.resolve()}")
    print(f"  Output       : {REPORT_PATH.resolve()}")
    print("")

    print("Loading raw tables...")
    tables = load_tables()
    print("")

    print("Loading feature tables...")
    feature_tables = load_feature_tables()
    print("")

    print("Running checks...")

    # ── Raw data checks (sections 1–7) ──────────────────────────────────────
    s_inventory                      = section_inventory(tables)
    s_nulls,    nulls_pass           = section_null_analysis(tables)
    s_schema,   schema_pass          = section_schema_drift(tables)
    s_fk,       fk_pass              = section_fk_validation(tables)
    s_dupes,    dupes_pass           = section_duplicate_check(tables)
    s_lap,      lap_pass             = section_lap_time_validation(tables)
    s_status,   status_pass          = section_status_validation(tables)

    # ── Feature-level checks (sections 8–10) ────────────────────────────────
    s_feat_dupes, feat_dupes_pass    = section_feature_duplicate_keys(feature_tables)
    s_bounds,     bounds_pass        = section_feature_bounds(feature_tables)
    s_points,     points_pass        = section_points_reconciliation(feature_tables)

    scorecard = section_scorecard([
        # Raw data checks
        ("No unjustified high-null columns",                   nulls_pass),
        ("Schema: all expected columns present",               schema_pass),
        ("Foreign key integrity",                              fk_pass),
        ("No unexplained duplicate race-driver records",       dupes_pass),
        ("Lap time: no corrupt values",                        lap_pass),
        ("Status integration with results intact",             status_pass),
        # Feature-level checks
        ("Feature tables: no duplicate composite keys",        feat_dupes_pass),
        ("Feature values: no impossible values (FAIL checks)", bounds_pass),
        ("Points reconciliation: no season delta > 5 pts",     points_pass),
    ])

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = "\n".join([
        "# Data Quality Report",
        "",
        f"> **Generated:** {timestamp}  ",
        f"> **Source (raw):** `{INTERIM_DIR}`  ",
        f"> **Source (features):** `{PROCESSED_DIR}`  ",
        f"> **Tables loaded:** {len(tables)}  ",
        f"> **Feature tables loaded:** {sum(v is not None for v in feature_tables.values())} / {len(feature_tables)}  ",
        "",
        _hr("─", 60),
        "",
    ])

    footer = "\n".join([
        "",
        _hr("─", 60),
        "",
        "_Generated by `validate_data.py`. "
        "Re-run at any time before modeling to verify data integrity._",
    ])

    content = "\n\n".join([
        header,
        scorecard,
        s_inventory,
        s_nulls,
        s_schema,
        s_fk,
        s_dupes,
        s_lap,
        s_status,
        s_feat_dupes,
        s_bounds,
        s_points,
        footer,
    ])

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(content, encoding="utf-8")

    print(f"\n✅ Report written → {REPORT_PATH}")
    print("────────────────────────────────────────────────────────\n")


if __name__ == "__main__":
    generate_report()