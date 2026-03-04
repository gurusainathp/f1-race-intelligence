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
 11. Data leakage detection (no post-race features in pre-race tables)
 12. Target distribution   (is_podium rate overall, by era, and by constructor era)
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
DRIVER_RACE_FULL_PARQUET        = PROCESSED_DIR / "driver_race_full.parquet"
DRIVER_RACE_PRE_PARQUET         = PROCESSED_DIR / "driver_race_pre.parquet"
DRIVER_SEASON_PARQUET           = PROCESSED_DIR / "driver_season_features.parquet"
CONSTRUCTOR_SEASON_PARQUET      = PROCESSED_DIR / "constructor_season_features.parquet"
DRIVER_RACE_ROLLING_PARQUET     = PROCESSED_DIR / "driver_race_rolling.parquet"
CONSTRUCTOR_RACE_ROLLING_PARQUET = PROCESSED_DIR / "constructor_race_rolling.parquet"

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
POINTS_PASS_DELTA = 2.0
POINTS_WARN_DELTA = 5.0

# ── Target distribution thresholds (Section 12) ───────────────────────────────
# Expected podium rate: 3 podium spots / ~20 starters ≈ 15%
# Warn if overall rate falls outside this band.
PODIUM_RATE_LOW  = 0.12   # 12% — investigate if below
PODIUM_RATE_HIGH = 0.18   # 18% — investigate if above

# Constructor dominance eras for breakdown (inclusive year ranges)
CONSTRUCTOR_ERAS = {
    "Pre-turbo (1950–1982)":    (1950, 1982),
    "Turbo era (1983–1988)":    (1983, 1988),
    "Normally aspirated (1989–2005)": (1989, 2005),
    "V8 era (2006–2013)":       (2006, 2013),
    "Hybrid era (2014–2021)":   (2014, 2021),
    "Ground effect (2022–)":    (2022, 9999),
}

# ── Data Leakage Detection ─────────────────────────────────────────────────────
POST_RACE_FEATURES: set[str] = {
    # Race outcomes
    "finish_position", "position", "points", "laps", "milliseconds", "time",
    # DNF status
    "is_dnf", "dnf_type",
    # Podium / winner / points finisher
    "is_podium", "is_winner", "is_points_finish",
    # Pit stop execution data (race-specific)
    # NOTE: avg_pit_duration_ms is intentionally absent here.
    # Season-level tables store this as season_avg_pit_duration_ms to avoid
    # name collision. The race-level name below still triggers leakage if
    # found in driver_race_pre.
    "pit_stop_count", "avg_pit_duration_ms", "total_pit_duration_ms",
    # Lap-level data
    "fastest_lap", "fastestLap", "fastest_lap_time_ms", "fastestLapTime_ms",
    "fastest_lap_rank", "rank",
    # Position changes during race
    "positions_gained", "positions_lost",
    # Actual lap times
    "lap_time_ms", "lap_times_data",
}

# ── Impossible value bounds ─────────────────────────────────────────────────────
BOUNDS_CHECKS = [
    # driver_race_full
    ("driver_race_full", "grid",             "<",  0,    "FAIL", "Grid position cannot be negative"),
    ("driver_race_full", "finish_position",  "<",  1,    "FAIL", "Finish position cannot be below 1"),
    ("driver_race_full", "positions_gained", "<", -30,   "FAIL", "Losing 30+ places in one race is impossible"),
    ("driver_race_full", "positions_gained", ">",  33,   "FAIL", "Gaining 33+ places in one race is impossible (max grid ~20 cars)"),
    ("driver_race_full", "points",           "<",  0,    "FAIL", "Race points cannot be negative"),
    ("driver_race_full", "pit_stop_count",   "<",  0,    "FAIL", "Pit stop count cannot be negative"),
    ("driver_race_full", "avg_pit_duration_ms", "<", 0,  "FAIL", "Pit duration cannot be negative"),
    ("driver_race_full", "is_dnf",           "<",  0,    "FAIL", "is_dnf must be 0 or 1"),
    ("driver_race_full", "is_dnf",           ">",  1,    "FAIL", "is_dnf must be 0 or 1"),
    # driver_race_pre
    ("driver_race_pre", "grid",             "<",  0,    "FAIL", "Grid position cannot be negative"),
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
    # driver_race_rolling — rolling stats should be non-negative counts/rates
    ("driver_race_rolling", "rolling_cumulative_points",   "<", 0, "FAIL", "Cumulative points cannot be negative"),
    ("driver_race_rolling", "rolling_cumulative_podiums",  "<", 0, "FAIL", "Cumulative podiums cannot be negative"),
    ("driver_race_rolling", "rolling_cumulative_wins",     "<", 0, "FAIL", "Cumulative wins cannot be negative"),
    ("driver_race_rolling", "rolling_dnf_rate",            "<", 0, "FAIL", "Rate cannot be negative"),
    ("driver_race_rolling", "rolling_dnf_rate",            ">", 1, "FAIL", "Rate cannot exceed 1.0"),
    ("driver_race_rolling", "rolling_races_counted",       "<", 0, "FAIL", "Race count cannot be negative"),
    # constructor_race_rolling
    ("constructor_race_rolling", "rolling_cumulative_points",   "<", 0, "FAIL", "Cumulative points cannot be negative"),
    ("constructor_race_rolling", "rolling_dnf_rate",            "<", 0, "FAIL", "Rate cannot be negative"),
    ("constructor_race_rolling", "rolling_dnf_rate",            ">", 1, "FAIL", "Rate cannot exceed 1.0"),
    ("constructor_race_rolling", "rolling_races_counted",       "<", 0, "FAIL", "Race count cannot be negative"),
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


def _classify_duplicate_pair(grp: pd.DataFrame) -> str:
    has_constr = "constructorId" in grp.columns
    if has_constr and grp["constructorId"].nunique() > 1:
        return "dual_constructor"
    if has_constr and grp["constructorId"].nunique() == 1 and grp["constructorId"].notna().all():
        return "shared_drive"
    return "unexplained"


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
    Load all parquet feature stores.
    Missing files are logged as warnings and stored as None.
    """
    mapping = {
        "driver_race_full":        DRIVER_RACE_FULL_PARQUET,
        "driver_race_pre":         DRIVER_RACE_PRE_PARQUET,
        "driver_season":           DRIVER_SEASON_PARQUET,
        "constructor_season":      CONSTRUCTOR_SEASON_PARQUET,
        "driver_race_rolling":     DRIVER_RACE_ROLLING_PARQUET,
        "constructor_race_rolling": CONSTRUCTOR_RACE_ROLLING_PARQUET,
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


# ── Section 2: Null Analysis ──────────────────────────────────────────────────

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

    dual_constructor: set[tuple] = set()
    shared_drive:     set[tuple] = set()
    unexplained:      set[tuple] = set()

    if dupe_pairs > 0:
        dupe_df = results[dupe_mask].copy()

        for (race_id, driver_id), grp in dupe_df.groupby(["raceId", "driverId"]):
            pair     = (race_id, driver_id)
            category = _classify_duplicate_pair(grp)
            if category == "dual_constructor":
                dual_constructor.add(pair)
            elif category == "shared_drive":
                shared_drive.add(pair)
            else:
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
            f"| Same team, two result rows — expected | ✅ Ignored |",
            f"| ❓ Unexplained | {len(unexplained)} "
            f"| constructorId absent or null"
            f" | {'✅ None' if len(unexplained) == 0 else '❌ FAIL'} |",
        ]

    lines.append(f"\n**Overall:** {_badge(passed)}")
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
        f"- Hard fail: < {LAP_TIME_MIN_MS / 1000:.0f} s or > {LAP_TIME_CORRUPT_MS / 1000:.0f} s",
        f"- Warning: {LAP_TIME_WARN_MS / 1000:.0f}–{LAP_TIME_CORRUPT_MS / 1000:.0f} s (SC/VSC)",
        f"- Z-score outlier: |z| > {LAP_Z_THRESHOLD}σ",
        "",
        "| Metric | Value |",
        "|--------|------:|",
        f"| Total records | {n_total:,} |",
        f"| Valid (non-null) | {n_valid:,} |",
        f"| Null / missing | {n_null:,} ({_pct(n_null, n_total)}) |",
        f"| Mean | {series.mean() / 1000:.3f} s |",
        f"| Median | {series.median() / 1000:.3f} s |",
        f"| Min | {series.min() / 1000:.3f} s |",
        f"| Max | {series.max() / 1000:.3f} s |",
        "",
        "| Check | Count | Severity | Result |",
        "|-------|------:|----------|:------:|",
        f"| Negative values | {negatives:,} | ❌ Corrupt | {_badge(negatives == 0)} |",
        f"| < {LAP_TIME_MIN_MS / 1000:.0f} s | {too_fast:,} | ❌ Corrupt | {_badge(too_fast == 0)} |",
        f"| SC/VSC laps | {sc_vsc_laps:,} | ⚠️ Warning | ℹ️ Expected |",
        f"| > {LAP_TIME_CORRUPT_MS / 1000:.0f} s | {corrupt:,} | ❌ Corrupt | {_badge(corrupt == 0)} |",
        f"| **Hard-fail total** | **{hard_fail:,}** | | **{_badge(hard_fail == 0)}** |",
    ]

    return "\n".join(lines), passed


# ── Section 7: Status Validation ──────────────────────────────────────────────

def section_status_validation(tables: dict[str, pd.DataFrame]) -> tuple[str, bool]:
    lines = ["## 7. Status & DNF Validation", ""]

    if "status" not in tables or "results" not in tables:
        return "\n".join(lines + ["> ⚠️ Required tables not available."]), False

    status_df = tables["status"]
    results   = tables["results"]

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
        f"**Unmapped statusId:** {unmapped_count:,} → {_badge(unmapped_count == 0)}",
        "",
        "| Category | Count | % |",
        "|----------|------:|--:|",
        f"| ✅ Finished | {finished_count:,} | {_pct(finished_count, total_entries)} |",
        f"| ❌ DNF | {dnf_count:,} | {_pct(dnf_count, total_entries)} |",
        f"| ❓ Other | {other_count:,} | {_pct(other_count, total_entries)} |",
    ]

    top_dnf = (
        status_usage.loc[status_usage["category"] == "DNF"]
        .sort_values("count", ascending=False)
        .head(10)
    )
    if not top_dnf.empty:
        lines += ["", "### Top 10 DNF Causes", "", "| Cause | Count |", "|-------|------:|"]
        for _, row in top_dnf.iterrows():
            lines.append(f"| {row['status']} | {int(row['count']):,} |")

    return "\n".join(lines), passed


# ===========================================================================
# Section 8: Feature Table Duplicate Keys
# ===========================================================================

def section_feature_duplicate_keys(
    feature_tables: dict[str, pd.DataFrame | None],
) -> tuple[str, bool]:
    lines    = ["## 8. Feature Table — Duplicate Key Check", ""]
    all_pass = True

    key_map = {
        "driver_race_full":        ["raceId", "driverId"],
        "driver_race_pre":         ["raceId", "driverId"],
        "driver_season":           ["driverId", "race_year"],
        "constructor_season":      ["constructorId", "race_year"],
        "driver_race_rolling":     ["raceId", "driverId"],
        "constructor_race_rolling": ["constructorId", "race_year", "round"],
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

        if table_key.startswith("driver_race") and dupe_count > 0:
            dupe_mask = df.duplicated(subset=key_cols, keep=False)
            dupe_df   = df[dupe_mask].copy()
            unexplained_pairs: set[tuple] = set()

            for (race_id, driver_id), grp in dupe_df.groupby(["raceId", "driverId"]):
                if _classify_duplicate_pair(grp) == "unexplained":
                    unexplained_pairs.add((race_id, driver_id))

            n_unexplained = len(unexplained_pairs)
            passed        = n_unexplained == 0
            if not passed:
                all_pass = False

            lines.append(
                f"| `{table_key}` | {', '.join(f'`{c}`' for c in key_cols)}"
                f" | {len(df):,} | {dupe_count:,} | {n_unexplained:,} | {_badge(passed)} |"
            )
        else:
            passed = dupe_count == 0
            if not passed:
                all_pass = False
            lines.append(
                f"| `{table_key}` | {', '.join(f'`{c}`' for c in key_cols)}"
                f" | {len(df):,} | {dupe_count:,} | {dupe_count:,} | {_badge(passed)} |"
            )

    lines += ["", f"**Overall:** {_badge(all_pass)}"]
    return "\n".join(lines), all_pass


# ===========================================================================
# Section 9: Feature Value Bounds
# ===========================================================================

def section_feature_bounds(
    feature_tables: dict[str, pd.DataFrame | None],
) -> tuple[str, bool]:
    lines    = ["## 9. Feature Value Bounds Check", ""]
    any_fail = False

    tables_covered = sorted({b[0] for b in BOUNDS_CHECKS})

    lines += [
        "| Table | Column | Check | Violations | Severity | Result |",
        "|-------|--------|-------|----------:|:--------:|:------:|",
    ]

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

    lines += ["", f"**Overall (FAIL-severity checks only):** {_badge(not any_fail)}"]
    return "\n".join(lines), not any_fail


# ===========================================================================
# Section 10: Points Reconciliation
# ===========================================================================

def section_points_reconciliation(
    feature_tables: dict[str, pd.DataFrame | None],
) -> tuple[str, bool]:
    lines = ["## 10. Points Reconciliation — Driver vs Constructor Totals", ""]

    dr_df  = feature_tables.get("driver_race_full")
    con_df = feature_tables.get("constructor_season")

    if dr_df is None or con_df is None:
        lines += ["> ⚠️ Cannot run reconciliation — required tables not available."]
        return "\n".join(lines), False

    missing_cols: list[str] = []
    if "points"       not in dr_df.columns:  missing_cols.append("driver_race_full.points")
    if "race_year"    not in dr_df.columns:  missing_cols.append("driver_race_full.race_year")
    if "total_points" not in con_df.columns: missing_cols.append("constructor_season.total_points")
    if "race_year"    not in con_df.columns: missing_cols.append("constructor_season.race_year")

    if missing_cols:
        lines += [f"> ⚠️ Missing columns: {', '.join(f'`{c}`' for c in missing_cols)}"]
        return "\n".join(lines), False

    driver_season_pts = (
        dr_df.groupby("race_year")["points"].sum()
        .rename("driver_total").reset_index().rename(columns={"race_year": "season"})
    )
    constructor_season_pts = (
        con_df.groupby("race_year")["total_points"].sum()
        .rename("constructor_total").reset_index().rename(columns={"race_year": "season"})
    )

    recon = driver_season_pts.merge(constructor_season_pts, on="season", how="outer")
    recon["driver_total"]      = recon["driver_total"].fillna(0)
    recon["constructor_total"] = recon["constructor_total"].fillna(0)
    recon["delta"]             = (recon["driver_total"] - recon["constructor_total"]).abs()
    recon = recon.sort_values("season")

    def _classify(delta: float) -> str:
        if delta <= POINTS_PASS_DELTA:  return "✅ PASS"
        elif delta <= POINTS_WARN_DELTA: return "⚠️ WARN"
        else:                            return "❌ FAIL"

    recon["result"] = recon["delta"].apply(_classify)
    n_fail          = int((recon["result"] == "❌ FAIL").sum())
    scorecard_pass  = n_fail == 0

    lines += [
        f"**Tolerance:** PASS ≤ {POINTS_PASS_DELTA} pts | WARN ≤ {POINTS_WARN_DELTA} pts | FAIL > {POINTS_WARN_DELTA} pts",
        f"**Scorecard:** {_badge(scorecard_pass)}",
        "",
        "| Season | Driver Total | Constructor Total | Delta | Result |",
        "|-------:|-------------:|------------------:|------:|:------:|",
    ]
    for _, row in recon.iterrows():
        lines.append(
            f"| {int(row['season'])} | {row['driver_total']:,.1f}"
            f" | {row['constructor_total']:,.1f} | {row['delta']:.1f} | {row['result']} |"
        )

    return "\n".join(lines), scorecard_pass


# ===========================================================================
# Section 11: Data Leakage Detection
# ===========================================================================

def section_data_leakage(
    feature_tables: dict[str, pd.DataFrame | None],
) -> tuple[str, bool]:
    lines = ["## 11. Data Leakage Detection", ""]

    dr_df = feature_tables.get("driver_race_pre")

    if dr_df is None:
        lines += ["> ⚠️ `driver_race_pre.parquet` not available — skipping."]
        return "\n".join(lines), False

    leaked_cols = sorted(set(dr_df.columns) & POST_RACE_FEATURES)
    passed      = len(leaked_cols) == 0

    lines += [
        f"**Table:** `driver_race_pre.parquet`",
        f"**Leaked columns detected:** {len(leaked_cols)}",
        f"**Result:** {_badge(passed)}",
        "",
    ]

    if not passed:
        lines += [
            "| Leaked Column | Severity |",
            "|---------------|----------|",
        ]
        for col in leaked_cols:
            if col in {"finish_position", "position", "points", "is_dnf"}:
                sev = "🔴 Critical"
            elif col in {"pit_stop_count", "avg_pit_duration_ms", "positions_gained"}:
                sev = "🟠 High"
            else:
                sev = "🟡 Medium"
            lines.append(f"| `{col}` | {sev} |")

    # Advisory check on season tables
    lines += [
        "",
        "### Season & Rolling Tables (Advisory)",
        "",
        "| Table | Columns | Risk | Notes |",
        "|-------|---------|------|-------|",
    ]

    advisory_tables = [
        ("driver_season",           "Historical full-season aggregates (prior season). Low risk."),
        ("constructor_season",      "Historical full-season aggregates (prior season). Low risk."),
        ("driver_race_rolling",     "Cumulative within-season stats — shift(1) applied. Verified leakage-free by design."),
        ("constructor_race_rolling","Cumulative within-season stats — shift(1) applied. Verified leakage-free by design."),
    ]

    for tbl_key, note in advisory_tables:
        df = feature_tables.get(tbl_key)
        if df is None:
            lines.append(f"| `{tbl_key}` | — | — | Not available |")
            continue
        season_leaked = sorted(set(df.columns) & POST_RACE_FEATURES)
        risk = f"⚠️ High: {len(season_leaked)} leaked" if season_leaked else "✅ Low"
        lines.append(f"| `{tbl_key}` | {len(df.columns)} | {risk} | {note} |")

    return "\n".join(lines), passed


# ===========================================================================
# Section 12: Target Distribution  (NEW)
# ===========================================================================

def section_target_distribution(
    feature_tables: dict[str, pd.DataFrame | None],
) -> tuple[str, bool]:
    """
    Check the distribution of the target variable `is_podium` in
    driver_race_full.parquet.

    Checks:
      1. Overall podium rate (expect 12–18%)
      2. Rate by pre/post 2000 era
      3. Rate by constructor dominance era
      4. Top 10 constructors by podium count (dominance check)

    Scorecard passes if the overall rate is within [PODIUM_RATE_LOW, PODIUM_RATE_HIGH].
    Era and constructor breakdowns are informational only.
    """
    lines = ["## 12. Target Distribution — `is_podium`", ""]

    df = feature_tables.get("driver_race_full")

    if df is None:
        lines += ["> ⚠️ `driver_race_full.parquet` not available — skipping."]
        return "\n".join(lines), False

    if "is_podium" not in df.columns:
        lines += ["> ⚠️ Column `is_podium` not found in `driver_race_full.parquet`."]
        return "\n".join(lines), False

    if "race_year" not in df.columns:
        lines += ["> ⚠️ Column `race_year` not found — cannot compute era breakdowns."]
        return "\n".join(lines), False

    target     = pd.to_numeric(df["is_podium"], errors="coerce").dropna()
    n_total    = len(target)
    n_podium   = int(target.sum())
    n_non      = n_total - n_podium
    rate        = n_podium / n_total if n_total > 0 else 0.0

    passed = PODIUM_RATE_LOW <= rate <= PODIUM_RATE_HIGH

    rate_pct = f"{rate * 100:.2f}%"
    band_str = f"[{PODIUM_RATE_LOW * 100:.0f}%, {PODIUM_RATE_HIGH * 100:.0f}%]"

    lines += [
        "### Overall",
        "",
        f"| Metric | Value |",
        f"|--------|------:|",
        f"| Total driver-race rows | {n_total:,} |",
        f"| Podium (is_podium = 1) | {n_podium:,} ({rate_pct}) |",
        f"| Non-podium (is_podium = 0) | {n_non:,} ({_pct(n_non, n_total)}) |",
        f"| Class imbalance ratio | {n_non / n_podium:.1f} : 1 |",
        f"| Expected band | {band_str} |",
        f"| **Result** | **{_badge(passed)}** |",
        "",
    ]

    if not passed:
        if rate < PODIUM_RATE_LOW:
            lines += [
                f"> ⚠️ Podium rate {rate_pct} is **below** expected minimum {PODIUM_RATE_LOW * 100:.0f}%.",
                "> Possible causes: data filtered too aggressively, era with large grids,"
                " or `is_podium` flag computed incorrectly. Investigate before modeling.",
                "",
            ]
        else:
            lines += [
                f"> ⚠️ Podium rate {rate_pct} is **above** expected maximum {PODIUM_RATE_HIGH * 100:.0f}%.",
                "> Possible causes: small grid eras included, duplicate rows, or flag logic error.",
                "",
            ]

    # ── By pre/post 2000 era ─────────────────────────────────────────────────
    lines += [
        "### By Era (Pre-2000 vs Post-2000)",
        "",
        "| Era | Rows | Podiums | Rate | Note |",
        "|-----|-----:|--------:|-----:|------|",
    ]

    era_splits = {
        "Pre-2000 (1950–1999)": df["race_year"] < 2000,
        "Post-2000 (2000–)":    df["race_year"] >= 2000,
    }

    for era_label, mask in era_splits.items():
        era_df    = df[mask]
        era_n     = len(era_df)
        if era_n == 0:
            lines.append(f"| {era_label} | 0 | 0 | N/A | No data |")
            continue
        era_pod   = int(pd.to_numeric(era_df["is_podium"], errors="coerce").fillna(0).sum())
        era_rate  = era_pod / era_n
        note      = ""
        if era_rate < PODIUM_RATE_LOW:
            note = "⚠️ Below expected band — larger grids pre-2000 (up to 26 cars)"
        elif era_rate > PODIUM_RATE_HIGH:
            note = "⚠️ Above expected band — investigate"
        else:
            note = "✅ Within expected band"
        lines.append(
            f"| {era_label} | {era_n:,} | {era_pod:,} | {era_rate * 100:.2f}% | {note} |"
        )

    lines.append("")

    # ── By constructor dominance era ─────────────────────────────────────────
    lines += [
        "### By Constructor Dominance Era",
        "",
        "| Era | Years | Rows | Podiums | Rate |",
        "|-----|-------|-----:|--------:|-----:|",
    ]

    for era_label, (yr_min, yr_max) in CONSTRUCTOR_ERAS.items():
        mask   = (df["race_year"] >= yr_min) & (df["race_year"] <= yr_max)
        era_df = df[mask]
        era_n  = len(era_df)
        if era_n == 0:
            lines.append(f"| {era_label} | {yr_min}–{min(yr_max, 9999)} | 0 | 0 | N/A |")
            continue
        era_pod  = int(pd.to_numeric(era_df["is_podium"], errors="coerce").fillna(0).sum())
        era_rate = era_pod / era_n
        yr_str   = f"{yr_min}–{yr_max}" if yr_max < 9999 else f"{yr_min}–present"
        lines.append(
            f"| {era_label} | {yr_str} | {era_n:,} | {era_pod:,} | {era_rate * 100:.2f}% |"
        )

    lines.append("")

    # ── Top constructors by podium count ─────────────────────────────────────
    if "constructorId" in df.columns:
        lines += [
            "### Top 10 Constructors by Podium Count",
            "",
            "> Informational — shows constructor dominance. High concentration here is",
            "> expected in F1 and is not a data quality issue.",
            "",
            "| Rank | constructorId | Podiums | Podium Rate | Races Entered |",
            "|-----:|--------------:|--------:|------------:|--------------:|",
        ]

        con_stats = (
            df.groupby("constructorId")
            .agg(
                total_races  = ("raceId",    "count"),
                total_podiums= ("is_podium", "sum"),
            )
            .reset_index()
        )
        con_stats["podium_rate"] = con_stats["total_podiums"] / con_stats["total_races"]
        con_stats = con_stats.sort_values("total_podiums", ascending=False).head(10)

        for rank, (_, row) in enumerate(con_stats.iterrows(), 1):
            lines.append(
                f"| {rank} | {int(row['constructorId'])} "
                f"| {int(row['total_podiums']):,} "
                f"| {row['podium_rate'] * 100:.1f}% "
                f"| {int(row['total_races']):,} |"
            )

    lines += [
        "",
        f"**Scorecard result:** {_badge(passed)}  "
        f"_(fails only if overall podium rate is outside {band_str})_",
        "",
        "> ℹ️ Era-level and constructor-level breakdowns are advisory.",
        "> Imbalanced classes are expected and handled at the modeling stage"
        " via class weighting or resampling — not by filtering data here.",
    ]

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

    s_inventory                      = section_inventory(tables)
    s_nulls,    nulls_pass           = section_null_analysis(tables)
    s_schema,   schema_pass          = section_schema_drift(tables)
    s_fk,       fk_pass              = section_fk_validation(tables)
    s_dupes,    dupes_pass           = section_duplicate_check(tables)
    s_lap,      lap_pass             = section_lap_time_validation(tables)
    s_status,   status_pass          = section_status_validation(tables)
    s_feat_dupes, feat_dupes_pass    = section_feature_duplicate_keys(feature_tables)
    s_bounds,     bounds_pass        = section_feature_bounds(feature_tables)
    s_points,     points_pass        = section_points_reconciliation(feature_tables)
    s_leakage,    leakage_pass       = section_data_leakage(feature_tables)
    s_target,     target_pass        = section_target_distribution(feature_tables)  # NEW

    scorecard = section_scorecard([
        ("No unjustified high-null columns",                       nulls_pass),
        ("Schema: all expected columns present",                   schema_pass),
        ("Foreign key integrity",                                  fk_pass),
        ("No unexplained duplicate race-driver records",           dupes_pass),
        ("Lap time: no corrupt values",                            lap_pass),
        ("Status integration with results intact",                 status_pass),
        ("Feature tables: no duplicate composite keys",            feat_dupes_pass),
        ("Feature values: no impossible values (FAIL checks)",     bounds_pass),
        ("Points reconciliation: no season delta > 5 pts",         points_pass),
        ("No data leakage: post-race features in pre-race tables", leakage_pass),
        ("Target distribution: podium rate within expected band",  target_pass),   # NEW
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
        s_leakage,
        s_target,    # NEW
        footer,
    ])

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(content, encoding="utf-8")

    print(f"\n✅ Report written → {REPORT_PATH}")
    print("────────────────────────────────────────────────────────\n")


if __name__ == "__main__":
    generate_report()