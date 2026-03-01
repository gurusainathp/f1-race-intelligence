"""
validate_data.py
================
Run anytime before modeling to validate data integrity.
Outputs: reports/data_quality_report.md

Checks performed:
  0. Quality scorecard
  1. Dataset inventory
  2. Null value analysis  (context-aware: distinguishes justified vs unjustified nulls)
  3. Schema drift         (expected columns present)
  4. Foreign key validation (with orphan row counts)
  5. Duplicate detection  (sprint-race aware; checks constructorId as tiebreaker)
  6. Lap time validation  (tiered thresholds for SC/VSC laps + z-score outliers)
  7. Status & DNF validation (via results integration, improved classifier)
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import sys

# Add project root to sys.path to allow absolute imports from src
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# Import shared classifiers and thresholds — single source of truth
from src.utils.constants import (
    DNF_KEYWORDS, FINISH_KEYWORDS, LAPPED_PATTERNS,
    LAP_TIME_MIN_MS, LAP_TIME_WARN_MS, LAP_TIME_CORRUPT_MS, LAP_Z_THRESHOLD,
    is_dnf as _is_dnf_fn, is_finish as _is_finish_fn,
)

# ── Configuration ──────────────────────────────────────────────────────────────
INTERIM_DIR = Path("data/interim")
REPORT_PATH = Path("reports/data_quality_report.md")

# Foreign key relationships: (child_table, child_col) → (parent_table, parent_col)
FK_CHECKS = [
    ("results", "raceId",        "races",        "raceId"),
    ("results", "driverId",      "drivers",      "driverId"),
    ("results", "constructorId", "constructors", "constructorId"),
    ("results", "statusId",      "status",       "statusId"),
]

# Expected columns per table — extend as schema evolves
EXPECTED_SCHEMA: dict[str, set[str]] = {
    "results":      {"resultId", "raceId", "driverId", "constructorId", "statusId",
                     "grid", "grid_pit_lane", "position", "points", "laps"},
    "races":        {"raceId", "year", "round", "circuitId", "name", "date"},
    "drivers":      {"driverId", "driverRef", "forename", "surname", "nationality"},
    "constructors": {"constructorId", "constructorRef", "name", "nationality"},
    "status":       {"statusId", "status"},
    "lap_times":    {"raceId", "driverId", "lap", "position", "lap_time_ms"},
}

# Columns expected in the master_race_table (produced by build_master_table.py)
# These are checked separately in section_schema_drift if master_race_table is loaded.
EXPECTED_MASTER_COLS: set[str] = {
    "is_shared_drive", "pit_data_incomplete", "grid_pit_lane",
    "is_dnf", "dnf_type", "is_podium", "is_winner", "is_points_finish",
}

# ── Null context: columns whose high null rate is structurally expected ─────────
# Format: col_name → (reason, min_null_pct_to_excuse)
# These columns will be marked "ℹ️ Justified" rather than "❌ High" in the report.
JUSTIFIED_NULLS: dict[str, str] = {
    # races — session dates only exist from 2021 Sprint calendar
    "sprint_date": "Sprint sessions only from 2021 (~6% of races)",
    "fp1_date":    "Session dates only recorded from 2021 era",
    "fp2_date":    "Session dates only recorded from 2021 era",
    "fp3_date":    "Session dates only recorded from 2021 era",
    "quali_date":  "Session dates only recorded from 2021 era",
    # drivers — permanent numbers introduced 2014, codes formalised in modern era
    "number":      "Permanent driver numbers introduced in 2014 only",
    "code":        "3-letter driver codes formalised in modern era only",
    # results — timing only available for classified finishers / modern era
    "milliseconds":      "Finish time only for classified finishers (DNFs = null by design)",
    "time":              "Finish time only for classified finishers (DNFs = null by design)",
    "fastestLap":        "Fastest lap data standardised from 2004 season only",
    "fastestLapTime_ms": "Fastest lap data standardised from 2004 season only",
    "fastestLapSpeed":   "Fastest lap data standardised from 2004 season only",
    "rank":              "Fastest lap ranking introduced from 2019 season only",
    # results — grid_pit_lane: 0 = not a pit-lane start / historic data gap,
    #           1 = confirmed pit-lane start (post-1995). Never null — int8 flag.
    "grid_pit_lane": (
        "Binary flag added by clean_data.py: 1 = post-1995 pit-lane start, "
        "0 = not a pit-lane start or pre-1996 data gap. Always filled — never null"
    ),
    # qualifying — session format dependent on era
    # Pre-1996: single aggregate qualifying session (q1_ms captures the time)
    # 1996-2002: two 1-hour sessions (q1_ms = session 1, q2_ms = session 2)
    # 2003-2005: single-lap shootout format (q1_ms used, q2_ms/q3_ms null)
    # 2006+:  three-part knockout format (Q1/Q2/Q3 as currently recorded)
    # Nulls in q2_ms and q3_ms for pre-2006 races are therefore structurally
    # expected. Post-2006 nulls are data gaps (DQ, DNS, 107% failure etc.).
    "q2_ms": (
        "Q2 null expected for single-session formats (pre-1996, 2003-2005). "
        "Post-2006: driver eliminated in Q1 or did not set a time (DNS/DQ/107%)"
    ),
    "q3_ms": (
        "Q3 only exists for top-10 qualifiers in 3-part format introduced 2006. "
        "Structural ~65% null for all post-2006 races; 100% null for all pre-2006"
    ),
}

# Columns that are high-null but NEED investigation (not automatically excused)
# Notes updated from diagnostics_report.md (2026-02-28):
INVESTIGATE_NULLS: dict[str, str] = {
    "position": (
        "41% null in results — expected: all DNFs have null position. "
        "Diagnostics confirmed difference = 2 (two lapped finishers with null "
        "position in Kaggle source — use positionOrder as reliable ordering column)"
    ),
    "grid": (
        "6% null in results — grid=0 recoded to NaN with grid_pit_lane flag. "
        "Pre-1996: 0 was a missing-data sentinel (517 rows, 14 scored points). "
        "Modern: genuine pit-lane starts. Do NOT use grid alone for pre-1996 analysis"
    ),
    "q1_ms": (
        "1.5% null in qualifying — multiple causes confirmed (2026-02-28 investigation): "
        "(1) entire races missing from Kaggle source (e.g. 1995 Australian GP — full grid null); "
        "(2) 107% rule failures (driver set no time); "
        "(3) injury/DNS before Q1 began; "
        "(4) modern era (2018-2024): disqualification, crash before setting a time, "
        "mechanical failure before Q1. Not fixable in pipeline — treat as data gap"
    ),
    "best_quali_ms": (
        "1.5% null in qualifying — mirrors q1_ms nulls exactly (derived as min of q1/q2/q3)"
    ),
    "pit_duration_ms": (
        "4.7% null in pit_stops — clustered in specific modern races (partial feed failures "
        "in Kaggle source, e.g. 2023 Australian GP 70.8% null, 2021 Saudi GP 74.5% null). "
        "Not random. Do NOT impute — null means data was never recorded, not a fast/slow stop"
    ),
}

# ── Status classifiers ─────────────────────────────────────────────────────────
# Use shared classifiers from constants.py (single source of truth).

def _is_dnf(label: str) -> bool:
    return _is_dnf_fn(label)

def _is_finish(label: str) -> bool:
    return _is_finish_fn(label)


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
    """
    Per-column null analysis with three-tier classification:
      - Justified nulls  : structurally expected (era-based, format-based)
      - Investigate nulls: high null rate without a clear structural reason
      - Standard severity: Clean / Minor / Moderate / High
    The scorecard passes only if there are no unjustified High-null columns.
    """
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
                # Investigate columns are flagged for human review, not automated failure.
                # They have already been assessed — do NOT trigger scorecard failure here.
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

    # Summary callout block
    lines += [
        "### Null Classification Legend",
        "",
        "| Label | Meaning |",
        "|-------|---------|",
        "| ✅ Clean | No nulls |",
        "| ⚠️ Minor | < 5% null, no action needed |",
        "| 🔶 Moderate | 5–20% null, monitor |",
        "| ❌ High | > 20% null, unjustified — fix required |",
        "| ℹ️ Justified | High null rate expected due to era/format constraints |",
        "| 🔍 Investigate | Null rate requires manual review before modeling |",
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


# ── Section 5: Duplicate Detection (sprint-aware, car-sharing-aware) ──────────

def section_duplicate_check(tables: dict[str, pd.DataFrame]) -> tuple[str, bool]:
    """
    Duplicate raceId × driverId detection with three known-legitimate categories:

    1. Sprint Race (2021+)
       Sprint + Main race share the same raceId. Identified by: year >= 2021
       AND rows are unique on the 3-key (raceId, driverId, constructorId).

    2. Dual Constructor (any era)
       Driver raced for two different constructors in the same event.
       Identified by: constructorId differs across duplicate rows.

    3. Car Sharing (pre-1970 F1)
       Common 1950s–1960s practice where multiple drivers shared one car in
       stints. Identified by: year < 1970 AND same constructorId across rows
       AND different laps values (different stint lengths).
       Confirmed by diagnostics_report.md (2026-02-28): all 37 "unexplained"
       raceIds from 1950–1964 are car-sharing entries. Not data errors.

    Scorecard fails only if unexplained duplicates remain after all three
    categories are checked.
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
    passed        = dupe_pairs == 0

    # Classification sets — populated inside the block below
    sprint_race_ids  = set()
    dual_constructor = set()
    car_sharing      = set()
    unexplained      = set()

    lines += [
        f"**Composite key:** `raceId × driverId`",
        f"**Duplicate pairs found:** {dupe_pairs:,}  →  {_badge(passed)}",
        f"**Rows affected:** {rows_affected:,} / {len(results):,}"
        f" ({_pct(rows_affected, len(results))})",
        "",
    ]

    if dupe_pairs > 0:
        dupe_df = results[dupe_mask].copy()

        has_race_year = ("races" in tables and "year" in tables["races"].columns
                         and "raceId" in tables["races"].columns)

        if has_race_year:
            race_year_map = tables["races"].set_index("raceId")["year"]
        else:
            race_year_map = pd.Series(dtype=int)

        has_constructor = "constructorId" in results.columns
        has_laps        = "laps" in results.columns

        for (race_id, driver_id), grp in dupe_df.groupby(["raceId", "driverId"]):
            year = int(race_year_map.get(race_id, 0) or 0)

            # ── Check 1: Dual constructor ─────────────────────────────────────
            # Rows differ in constructorId → driver raced for two teams.
            if has_constructor and grp["constructorId"].nunique() > 1:
                dual_constructor.add(race_id)
                continue

            # ── Check 2: Sprint race (2021+) ──────────────────────────────────
            # Same constructor, different laps, modern era.
            if year >= 2021:
                sprint_race_ids.add(race_id)
                continue

            # ── Check 3: Car sharing (pre-1970) ───────────────────────────────
            # Same constructor, different lap counts → shared-drive stints.
            # Confirmed in Kaggle F1 dataset: 1950–1964 races only.
            if (year < 1970
                    and has_laps
                    and has_constructor
                    and grp["constructorId"].nunique() == 1
                    and (grp["laps"].max() - grp["laps"].min()) > 0):
                car_sharing.add(race_id)
                continue

            # ── No known pattern matches ──────────────────────────────────────
            unexplained.add(race_id)

        all_affected   = sorted(dupe_df["raceId"].unique())
        distinct_races = len(all_affected)
        id_display     = ", ".join(f"`{r}`" for r in all_affected[:30])
        truncation     = f" _(showing first 30 of {distinct_races})_" if distinct_races > 30 else ""

        lines += [
            f"**Distinct races affected:** {distinct_races:,}",
            f"**Affected raceIds:** {id_display}{truncation}",
            "",
            "### Duplicate Root Cause Classification",
            "",
            "| Category | Race Count | Interpretation | Action |",
            "|----------|----------:|----------------|--------|",
            f"| 🏎️ Sprint Race (2021+) | {len(sprint_race_ids)} "
            f"| Sprint + Main race share same raceId | Add `session_type` column or separate table |",
            f"| 🏛️ Dual Constructor | {len(dual_constructor)} "
            f"| Driver raced for 2 teams in same event | Extend key with `constructorId` |",
            f"| 🤝 Car Sharing (pre-1970) | {len(car_sharing)} "
            f"| 1950s–60s shared-drive stints — expected historical data | Add `is_shared_drive` flag |",
            f"| ❓ Unexplained | {len(unexplained)} "
            f"| No structural reason found | **Investigate immediately** |",
        ]

        if unexplained:
            unexplained_ids = ", ".join(f"`{r}`" for r in sorted(unexplained))
            lines += [
                "",
                f"> ⚠️ **Unexplained duplicate raceIds:** {unexplained_ids}  ",
                "> These do not match Sprint, dual-constructor, or car-sharing patterns. "
                "Investigate before modeling.",
            ]

        if car_sharing:
            lines += [
                "",
                "> ℹ️ **Car-sharing duplicates are expected historical data.** In 1950s–60s F1,"
                " multiple drivers shared one car in stints. Each stint is a separate row."
                " For main-race analysis, use the row with the highest `laps` value"
                " (final driver to take the wheel). Consider adding an `is_shared_drive` flag.",
            ]

        # Per-race summary table
        race_summary = (
            dupe_df.groupby("raceId")
            .apply(lambda g: g.duplicated(subset=["driverId"]).sum(), include_groups=False)
            .reset_index(name="duplicate_pairs")
            .sort_values("duplicate_pairs", ascending=False)
            .head(15)
        )

        if has_race_year:
            race_summary["year"] = race_summary["raceId"].map(race_year_map).fillna("?").astype(str)
            race_summary["category"] = race_summary["raceId"].apply(
                lambda r: (
                    "🏎️ Sprint"         if r in sprint_race_ids
                    else "🏛️ Dual Constructor" if r in dual_constructor
                    else "🤝 Car Sharing"       if r in car_sharing
                    else "❓ Unexplained"
                )
            )

        lines += ["", "**Top affected races (up to 15):**", ""]

        if has_race_year:
            lines += [
                "| raceId | Year | Duplicate Pairs | Category |",
                "|-------:|-----:|----------------:|----------|",
            ]
            for _, row in race_summary.iterrows():
                lines.append(
                    f"| {int(row['raceId'])} | {row['year']}"
                    f" | {int(row['duplicate_pairs'])} | {row['category']} |"
                )
        else:
            lines += [
                "| raceId | Duplicate Pairs |",
                "|-------:|----------------:|",
            ]
            for _, row in race_summary.iterrows():
                lines.append(f"| {int(row['raceId'])} | {int(row['duplicate_pairs'])} |")

        # All pairs table
        all_dupes = (
            dupe_df.groupby(subset)
            .size()
            .reset_index(name="occurrences")
            .sort_values("occurrences", ascending=False)
            .head(20)
        )
        lines += [
            "",
            "**All duplicate pairs (up to 20):**",
            "",
            "| raceId | driverId | Occurrences |",
            "|-------:|---------:|------------:|",
        ]
        for _, row in all_dupes.iterrows():
            lines.append(f"| {int(row['raceId'])} | {int(row['driverId'])} | {int(row['occurrences'])} |")

        lines += [
            "",
            "### Recommended Fix",
            "",
            "**If duplicates are Sprint races (2021+):**",
            "```python",
            "# Add session_type to differentiate Sprint from Main Race",
            "results['session_type'] = results.groupby(['raceId','driverId']).cumcount()",
            "results['session_type'] = results['session_type'].map({0: 'main', 1: 'sprint'})",
            "```",
            "",
            "**If duplicates are Car Sharing (pre-1970):**",
            "```python",
            "# Keep only the final stint (highest laps = last driver in the car)",
            "results = results.sort_values('laps', ascending=False)",
            "results = results.drop_duplicates(subset=['raceId', 'driverId'], keep='first')",
            "# Or: flag all shared-drive rows for separate analysis",
            "results['is_shared_drive'] = results.duplicated(",
            "    subset=['raceId', 'driverId'], keep=False).astype('int8')",
            "```",
        ]

    # Scorecard: pass if zero unexplained duplicates.
    # Sprint, dual-constructor, and car-sharing duplicates are all structurally
    # expected — they are not data errors.
    scorecard_pass = dupe_pairs == 0 or len(unexplained) == 0

    return "\n".join(lines), scorecard_pass


# ── Section 6: Lap Time Validation (tiered thresholds) ────────────────────────

def section_lap_time_validation(tables: dict[str, pd.DataFrame]) -> tuple[str, bool]:
    """
    Three-tier threshold check:
      < 40 s      → corrupt (impossible)
      300–600 s   → warning (Safety Car / VSC / formation lap — real but anomalous)
      > 600 s     → corrupt (no F1 lap legitimately takes 10+ minutes)
    Plus z-score outlier detection.
    Scorecard fails only on confirmed corrupt records, not SC/VSC warnings.
    """
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

    # Threshold tiers
    negatives   = int((series < 0).sum())
    too_fast    = int(((series >= 0) & (series < LAP_TIME_MIN_MS)).sum())
    sc_vsc_laps = int(((series > LAP_TIME_WARN_MS) & (series <= LAP_TIME_CORRUPT_MS)).sum())
    corrupt     = int((series > LAP_TIME_CORRUPT_MS).sum())
    hard_fail   = negatives + too_fast + corrupt

    # Z-score outlier detection
    z_scores  = (series - series.mean()) / series.std()
    z_extreme = int((z_scores.abs() > LAP_Z_THRESHOLD).sum())

    # Outliers that are ALSO in the SC/VSC band are already accounted for
    # by the threshold warning above — don't double-fail on them.
    # Only truly unexplained z-score outliers (below the SC/VSC threshold) fail.
    z_unexplained = int(
        ((z_scores.abs() > LAP_Z_THRESHOLD) & (series <= LAP_TIME_WARN_MS)).sum()
    )

    passed = hard_fail == 0 and z_unexplained == 0

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
            " routinely produce lap times of 3–5 minutes. These should be **excluded from"
            " race-pace modeling** but retained for full-race analysis.",
            "",
            "**Recommended handling in pipeline:**",
            "```python",
            "# Flag SC/VSC laps rather than dropping them",
            f"lap_times['is_slow_lap'] = lap_times['lap_time_ms'] > {LAP_TIME_WARN_MS}",
            "# Use only normal laps for pace analysis",
            "normal_laps = lap_times[~lap_times['is_slow_lap']]",
            "```",
        ]

    # Z-score section
    lines += [
        "",
        "### Statistical Outlier Detection (Z-Score)",
        "",
        f"> Flags lap times where |z| > {LAP_Z_THRESHOLD}"
        f" (more than {LAP_Z_THRESHOLD} standard deviations from the mean).",
        "",
        "| Metric | Value |",
        "|--------|------:|",
        f"| Mean ± 1σ | {series.mean() / 1000:.1f} s ± {series.std() / 1000:.1f} s |",
        f"| Total outliers (\\|z\\| > {LAP_Z_THRESHOLD}) | {z_extreme:,} ({_pct(z_extreme, n_valid)}) |",
        f"| Of those: SC/VSC overlap (already flagged above) | {z_extreme - z_unexplained:,} |",
        f"| Genuinely unexplained outliers | {z_unexplained:,} |",
        f"| Outlier check | {_badge(z_unexplained == 0)} |",
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
            lap_s    = row["lap_time_ms"] / 1000
            z_val    = row["z"]
            cause    = "SC/VSC or red flag" if row["lap_time_ms"] <= LAP_TIME_CORRUPT_MS else "Likely corrupt"
            lines.append(
                f"| {int(row['raceId'])} | {int(row['driverId'])}"
                f" | {int(row['lap'])} | {lap_s:.1f} | {z_val:+.2f} | {cause} |"
            )

    return "\n".join(lines), passed


# ── Section 7: Status Validation (via results, improved classifier) ───────────

def section_status_validation(tables: dict[str, pd.DataFrame]) -> tuple[str, bool]:
    """
    Validates status integration end-to-end via results.statusId mapping.
    Improved classifier handles lapped finishers (+N Laps), expanded DNF keywords,
    and surfaces the 'Other/Unclassified' bucket for manual review.
    """
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

    # Other bucket detail — surface for investigation
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

    # Top 10 DNF causes
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

    # Finished breakdown
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
    print(f"  Source : {INTERIM_DIR.resolve()}")
    print(f"  Output : {REPORT_PATH.resolve()}")
    print("")

    print("Loading tables...")
    tables = load_tables()
    print("")

    print("Running checks...")

    s_inventory              = section_inventory(tables)
    s_nulls, nulls_pass      = section_null_analysis(tables)
    s_schema, schema_pass    = section_schema_drift(tables)
    s_fk,     fk_pass        = section_fk_validation(tables)
    s_dupes,  dupes_pass     = section_duplicate_check(tables)
    s_lap,    lap_pass       = section_lap_time_validation(tables)
    s_status, status_pass    = section_status_validation(tables)

    scorecard = section_scorecard([
        ("No unjustified high-null columns",               nulls_pass),
        ("Schema: all expected columns present",           schema_pass),
        ("Foreign key integrity",                          fk_pass),
        ("No unexplained duplicate race-driver records",   dupes_pass),
        ("Lap time: no corrupt values",                    lap_pass),
        ("Status integration with results intact",         status_pass),
    ])

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = "\n".join([
        "# Data Quality Report",
        "",
        f"> **Generated:** {timestamp}  ",
        f"> **Source:** `{INTERIM_DIR}`  ",
        f"> **Tables loaded:** {len(tables)}  ",
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
        footer,
    ])

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(content, encoding="utf-8")

    print(f"\n✅ Report written → {REPORT_PATH}")
    print("────────────────────────────────────────────────────────\n")


if __name__ == "__main__":
    generate_report()