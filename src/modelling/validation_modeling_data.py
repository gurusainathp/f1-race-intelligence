"""
src/modelling/validation_modeling_data.py
---------------------------------------------
Validates the final modeling dataset before any model training begins.
Outputs: reports/data_quality/modeling_dataset_validation.md

Checks performed:
  0. Quality scorecard
  1. Dataset inventory        — shape, dtypes, year range, class balance
  2. Duplicate key check      — (raceId, driverId) must be unique
  3. Forbidden column check   — no post-race / leakage columns present
  4. Null audit               — per-column null counts with context rules
  5. Correlation audit        — Pearson matrix; flags |r| > 0.90 pairs

Null rules used in check 4:
  - grid                          → 0 nulls expected
  - is_podium                     → 0 nulls expected (target)
  - rolling_* where round == 1    → NaN allowed (filled with 0 in build step)
  - rolling_* where round >  1    → 0 nulls expected
  - prev_season_* / has_prev_season → 0 nulls expected (filled with 0 for rookies)
  - constructor rolling cols      → same round-1 rule as driver rolling

Note: this script does NOT auto-fix anything.
It reports problems and exits with code 1 if any FAIL-level check fails,
so it can be used as a CI gate before model training.

Run:
  python src/modelling/validation_modeling_data.py
"""

import sys
import warnings
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODELING_DATASET_PATH = _PROJECT_ROOT / "data" / "processed" / "modeling" / "modeling_dataset.parquet"
REPORT_DIR            = _PROJECT_ROOT / "reports" / "data_quality"
REPORT_PATH           = REPORT_DIR / "modeling_dataset_validation.md"

# ---------------------------------------------------------------------------
# Import forbidden columns list from build script (single source of truth)
# ---------------------------------------------------------------------------
try:
    _build_script = _PROJECT_ROOT / "src" / "modeling" / "build_modeling_dataset.py"
    if str(_PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(_PROJECT_ROOT))
    from src.modeling.build_modeling_dataset import FORBIDDEN_COLUMNS
except ImportError:
    # Fallback — keep in sync with build_modeling_dataset.py manually
    FORBIDDEN_COLUMNS: set[str] = {
        "finish_position", "finish_position_order", "positionOrder",
        "positions_gained", "milliseconds", "time",
        "fastestLap", "fastest_lap_rank", "fastest_lap_ms",
        "avg_lap_time_ms", "lap_time_consistency",
        "pit_stop_count", "total_pit_time_ms", "avg_pit_duration_ms",
        "is_dnf", "dnf_type", "is_winner", "is_points_finish",
        "points", "laps", "statusId",
        "rolling_cumulative_wins",
    }

# ---------------------------------------------------------------------------
# Expected columns — every column that MUST be present
# ---------------------------------------------------------------------------
REQUIRED_COLUMNS: list[str] = [
    # Identifiers
    "raceId", "driverId", "constructorId", "race_year", "round", "circuitId",
    # Race setup
    "grid", "grid_pit_lane",
    # Driver rolling
    "rolling_cumulative_points",
    "rolling_cumulative_podiums",
    "rolling_podium_rate",
    "rolling_dnf_rate",
    "rolling_avg_finish_position",
    "rolling_avg_qualifying_position",
    "rolling_races_counted",
    # Constructor rolling
    "con_rolling_cumulative_points",
    "con_rolling_podium_rate",
    "con_rolling_dnf_rate",
    "con_rolling_avg_finish_position",
    "con_rolling_races_counted",
    # Prior season
    "prev_season_points",
    "prev_season_podium_rate",
    "has_prev_season",
    # Target
    "is_podium",
]

# Columns that must have zero nulls regardless of round
ZERO_NULL_ALWAYS: list[str] = [
    "raceId", "driverId", "constructorId",
    "race_year", "round", "circuitId",
    "grid_pit_lane",
    "is_podium",
    "has_prev_season",
    "prev_season_points",
    "prev_season_podium_rate",
]

# Rolling columns that may only be null on round == 1
# (build step fills these with 0, so post-build should also be 0 null)
ROLLING_COLS: list[str] = [
    "rolling_cumulative_points",
    "rolling_cumulative_podiums",
    "rolling_podium_rate",
    "rolling_dnf_rate",
    "rolling_avg_finish_position",
    "rolling_avg_qualifying_position",
    "rolling_races_counted",
    "con_rolling_cumulative_points",
    "con_rolling_podium_rate",
    "con_rolling_dnf_rate",
    "con_rolling_avg_finish_position",
    "con_rolling_races_counted",
]

# Correlation threshold — pairs above this are flagged (advisory, not fail)
CORR_THRESHOLD = 0.90

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _hr(char: str = "─", width: int = 60) -> str:
    return char * width


def _badge(passed: bool) -> str:
    return "✅ PASS" if passed else "❌ FAIL"


def _pct(value: float, total: float, decimals: int = 2) -> str:
    if total == 0:
        return "N/A"
    return f"{value / total * 100:.{decimals}f}%"


# ===========================================================================
# Section 1: Dataset Inventory
# ===========================================================================

def section_inventory(df: pd.DataFrame) -> str:
    n_total  = len(df)
    n_podium = int(df["is_podium"].sum()) if "is_podium" in df.columns else 0
    n_non    = n_total - n_podium
    rate     = n_podium / n_total if n_total > 0 else 0.0
    n_rookie = int((df["has_prev_season"] == 0).sum()) if "has_prev_season" in df.columns else 0

    yr_min = int(df["race_year"].min()) if "race_year" in df.columns else "?"
    yr_max = int(df["race_year"].max()) if "race_year" in df.columns else "?"

    lines = [
        "## 1. Dataset Inventory",
        "",
        "| Metric | Value |",
        "|--------|------:|",
        f"| Rows | {n_total:,} |",
        f"| Columns | {len(df.columns)} |",
        f"| Season range | {yr_min} – {yr_max} |",
        f"| Unique races | {df['raceId'].nunique():,} |" if "raceId" in df.columns else "| Unique races | — |",
        f"| Unique drivers | {df['driverId'].nunique():,} |" if "driverId" in df.columns else "| Unique drivers | — |",
        f"| Unique constructors | {df['constructorId'].nunique():,} |" if "constructorId" in df.columns else "| Unique constructors | — |",
        f"| Podium rows (is_podium=1) | {n_podium:,} ({_pct(n_podium, n_total)}) |",
        f"| Non-podium rows (is_podium=0) | {n_non:,} ({_pct(n_non, n_total)}) |",
        f"| Class imbalance ratio | {n_non / n_podium:.1f} : 1 |" if n_podium > 0 else "| Class imbalance ratio | N/A |",
        f"| Rookie rows (has_prev_season=0) | {n_rookie:,} ({_pct(n_rookie, n_total)}) |",
        "",
        "### Column List",
        "",
        "| # | Column | dtype |",
        "|---|--------|-------|",
    ]
    for i, col in enumerate(df.columns, 1):
        lines.append(f"| {i} | `{col}` | {df[col].dtype} |")

    return "\n".join(lines)


# ===========================================================================
# Section 2: Duplicate Key Check
# ===========================================================================

def section_duplicate_keys(df: pd.DataFrame) -> tuple[str, bool]:
    lines = ["## 2. Duplicate Key Check", ""]

    key_cols = ["raceId", "driverId"]
    missing  = [c for c in key_cols if c not in df.columns]

    if missing:
        lines += [f"> ⚠️ Key columns missing: {missing}"]
        return "\n".join(lines), False

    n_dupes = int(df.duplicated(subset=key_cols).sum())
    passed  = n_dupes == 0

    lines += [
        f"**Composite key:** `raceId × driverId`",
        f"**Total rows:** {len(df):,}",
        f"**Duplicate pairs:** {n_dupes:,}",
        f"**Result:** {_badge(passed)}",
    ]

    if not passed:
        sample = (
            df[df.duplicated(subset=key_cols, keep=False)]
            .sort_values(key_cols)
            .head(10)[key_cols + (["constructorId"] if "constructorId" in df.columns else [])]
        )
        lines += [
            "",
            "**Sample duplicate rows (up to 10):**",
            "",
            sample.to_markdown(index=False),
            "",
            "> Re-run `build_modeling_dataset.py` — dedup logic may have failed.",
        ]

    return "\n".join(lines), passed


# ===========================================================================
# Section 3: Forbidden Column Check
# ===========================================================================

def section_forbidden_columns(df: pd.DataFrame) -> tuple[str, bool]:
    lines = ["## 3. Forbidden Column Check", ""]

    present   = sorted(FORBIDDEN_COLUMNS & set(df.columns))
    passed    = len(present) == 0

    lines += [
        f"**Forbidden columns defined:** {len(FORBIDDEN_COLUMNS)}",
        f"**Forbidden columns present in dataset:** {len(present)}",
        f"**Result:** {_badge(passed)}",
    ]

    if present:
        lines += [
            "",
            "| Column | Risk |",
            "|--------|------|",
        ]
        for col in present:
            if col in {"finish_position", "is_dnf", "points", "is_winner"}:
                risk = "🔴 Critical — direct race outcome"
            elif col in {"pit_stop_count", "avg_pit_duration_ms", "positions_gained"}:
                risk = "🟠 High — race execution data"
            else:
                risk = "🟡 Medium — post-race derived metric"
            lines.append(f"| `{col}` | {risk} |")

        lines += [
            "",
            "> Remove these columns in `build_modeling_dataset.py` "
            "and re-run the build script.",
        ]
    else:
        lines += [
            "",
            "> ✅ No forbidden columns detected. Dataset is leakage-free.",
        ]

    return "\n".join(lines), passed


# ===========================================================================
# Section 4: Null Audit
# ===========================================================================

def section_null_audit(df: pd.DataFrame) -> tuple[str, bool]:
    """
    Null rules:
      - ZERO_NULL_ALWAYS cols    → 0 nulls required (FAIL if any)
      - ROLLING_COLS             → 0 nulls required post-build (build fills round-1
                                   NaNs with 0); FAIL if any nulls remain
      - grid                     → FAIL if any nulls (grid should always be known)
      - Other columns            → advisory only (WARN if > 5%)
    """
    lines    = ["## 4. Null Audit", ""]
    any_fail = False

    lines += [
        "| Column | Null Count | Null % | Rule | Result |",
        "|--------|----------:|-------:|------|:------:|",
    ]

    # Determine rule per column
    def _check_col(col: str) -> tuple[int, str, str, bool]:
        if col not in df.columns:
            return 0, "—", "⚠️ Column missing", False

        n_null   = int(df[col].isna().sum())
        null_pct = n_null / len(df) * 100 if len(df) > 0 else 0.0
        pct_str  = f"{null_pct:.2f}%"

        if col in ZERO_NULL_ALWAYS:
            rule   = "Must be 0"
            passed = n_null == 0
            result = _badge(passed)
        elif col == "grid":
            rule   = "Must be 0"
            passed = n_null == 0
            result = _badge(passed)
        elif col in ROLLING_COLS:
            rule   = "Must be 0 (build fills round-1)"
            passed = n_null == 0
            result = _badge(passed)
        else:
            # Advisory for other columns
            passed = True   # does not fail scorecard
            if n_null == 0:
                rule   = "Advisory"
                result = "✅ Clean"
            elif null_pct < 5:
                rule   = "Advisory"
                result = "⚠️ Minor"
            else:
                rule   = "Advisory"
                result = "🔶 Moderate"

        return n_null, pct_str, rule, passed

    for col in df.columns:
        n_null, pct_str, rule, passed = _check_col(col)
        if not passed:
            any_fail = True
        lines.append(f"| `{col}` | {n_null:,} | {pct_str} | {rule} | {_badge(passed) if rule != 'Advisory' else (pct_str if n_null else '✅ Clean')} |")

    lines += [
        "",
        f"**Overall (FAIL-level checks only):** {_badge(not any_fail)}",
        "",
        "> ℹ️ Advisory nulls do not fail the scorecard.",
        "> Rolling cols should have 0 nulls because `build_modeling_dataset.py`",
        "> fills round-1 NaNs with 0 before saving.",
    ]

    return "\n".join(lines), not any_fail


# ===========================================================================
# Section 5: Correlation Audit
# ===========================================================================

def section_correlation_audit(df: pd.DataFrame) -> tuple[str, bool]:
    """
    Compute Pearson correlation matrix across all numeric feature columns
    (excluding identifiers and target). Flag pairs with |r| > CORR_THRESHOLD.

    This is advisory only — does NOT fail the scorecard.
    Dropping correlated features is a manual decision made after review.
    """
    lines = ["## 5. Correlation Audit (Pearson)", ""]

    # Columns to exclude from correlation (identifiers, target, flags)
    exclude = {
        "raceId", "driverId", "constructorId", "race_year", "round", "circuitId",
        "is_podium", "has_prev_season", "grid_pit_lane",
    }

    numeric_cols = [
        c for c in df.columns
        if c not in exclude and pd.api.types.is_numeric_dtype(df[c])
    ]

    if len(numeric_cols) < 2:
        lines += ["> ⚠️ Not enough numeric feature columns for correlation analysis."]
        return "\n".join(lines), True

    corr_df = df[numeric_cols].corr(method="pearson")

    # Extract upper triangle pairs only (exclude self-correlation)
    high_corr_pairs: list[tuple[str, str, float]] = []
    for i, col_a in enumerate(numeric_cols):
        for col_b in numeric_cols[i + 1:]:
            r = corr_df.loc[col_a, col_b]
            if pd.notna(r) and abs(r) > CORR_THRESHOLD:
                high_corr_pairs.append((col_a, col_b, float(r)))

    high_corr_pairs.sort(key=lambda x: abs(x[2]), reverse=True)

    lines += [
        f"**Features analysed:** {len(numeric_cols)}",
        f"**Threshold:** |r| > {CORR_THRESHOLD}",
        f"**High-correlation pairs found:** {len(high_corr_pairs)}",
        f"**Result:** {'⚠️ WARN — review pairs below' if high_corr_pairs else '✅ No high-correlation pairs'}",
        "",
    ]

    if high_corr_pairs:
        lines += [
            "> ⚠️ These pairs are **flagged for manual review only**.",
            "> Do NOT drop automatically — confirm redundancy before removing.",
            "> Common legitimate causes in F1 data: cumulative points correlates",
            "> with cumulative podiums; constructor and driver stats co-move",
            "> during dominant seasons.",
            "",
            "| Feature A | Feature B | Pearson r | Strength |",
            "|-----------|-----------|----------:|----------|",
        ]
        for col_a, col_b, r in high_corr_pairs:
            strength = (
                "🔴 Very high" if abs(r) > 0.97
                else "🟠 High" if abs(r) > 0.93
                else "🟡 Moderate-high"
            )
            lines.append(f"| `{col_a}` | `{col_b}` | {r:+.4f} | {strength} |")

        lines += [
            "",
            "### Suggested Investigation",
            "",
            "For each flagged pair, ask:",
            "1. Do they measure the same underlying signal?",
            "2. Does one have more predictive signal than the other?",
            "3. Does VIF confirm multicollinearity in the logistic regression?",
            "",
            "Remove the weaker feature only after answering the above.",
        ]

    # Full correlation matrix as a collapsed section
    lines += [
        "",
        "### Full Pearson Correlation Matrix",
        "",
        "> Values shown to 2 decimal places.",
        "",
    ]

    corr_rounded = corr_df.round(2)
    # Header row
    lines.append("| | " + " | ".join(f"`{c}`" for c in numeric_cols) + " |")
    lines.append("|---|" + "|".join(["---:"] * len(numeric_cols)) + "|")
    for row_col in numeric_cols:
        vals = " | ".join(
            f"**{corr_rounded.loc[row_col, c]:.2f}**"
            if abs(corr_rounded.loc[row_col, c]) > CORR_THRESHOLD and row_col != c
            else f"{corr_rounded.loc[row_col, c]:.2f}"
            for c in numeric_cols
        )
        lines.append(f"| `{row_col}` | {vals} |")

    return "\n".join(lines), True   # advisory — always passes scorecard


# ===========================================================================
# Scorecard
# ===========================================================================

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
    lines += [
        "",
        "> ℹ️ Correlation audit (Section 5) is advisory and does not affect the scorecard.",
    ]
    return "\n".join(lines)


# ===========================================================================
# Report Assembly
# ===========================================================================

def generate_report() -> bool:
    """
    Run all checks, write the markdown report, and return True if all
    FAIL-level checks passed (suitable for use as a CI gate).
    """
    print("\n── Modeling Dataset Validator ──────────────────────────")
    print(f"  Dataset : {MODELING_DATASET_PATH}")
    print(f"  Report  : {REPORT_PATH}")
    print("")

    if not MODELING_DATASET_PATH.exists():
        print(
            f"[ERROR] Modeling dataset not found at {MODELING_DATASET_PATH}\n"
            f"Run build_modeling_dataset.py first.",
            file=sys.stderr,
        )
        sys.exit(1)

    print("Loading dataset...")
    df = pd.read_parquet(MODELING_DATASET_PATH)
    print(f"  {len(df):,} rows × {len(df.columns)} columns\n")

    print("Running checks...")
    s_inventory                   = section_inventory(df)
    s_dupes,       dupes_pass     = section_duplicate_keys(df)
    s_forbidden,   forbidden_pass = section_forbidden_columns(df)
    s_nulls,       nulls_pass     = section_null_audit(df)
    s_corr,        corr_pass      = section_correlation_audit(df)

    scorecard = section_scorecard([
        ("No duplicate (raceId, driverId) keys",     dupes_pass),
        ("No forbidden / post-race columns present", forbidden_pass),
        ("Null audit: zero nulls in required columns", nulls_pass),
        ("Correlation audit (advisory)",              corr_pass),
    ])

    all_passed = all([dupes_pass, forbidden_pass, nulls_pass])

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = "\n".join([
        "# Modeling Dataset Validation Report",
        "",
        f"> **Generated:** {timestamp}  ",
        f"> **Dataset:** `{MODELING_DATASET_PATH}`  ",
        f"> **Rows:** {len(df):,}  |  **Columns:** {len(df.columns)}  ",
        f"> **Year range:** {int(df['race_year'].min())} – {int(df['race_year'].max())}  "
        if "race_year" in df.columns else "",
        "",
        _hr("─", 60),
        "",
    ])

    footer = "\n".join([
        "",
        _hr("─", 60),
        "",
        "_Generated by `validate_modeling_dataset.py`.",
        "Re-run after any change to `build_modeling_dataset.py`._",
    ])

    content = "\n\n".join([
        header,
        scorecard,
        s_inventory,
        s_dupes,
        s_forbidden,
        s_nulls,
        s_corr,
        footer,
    ])

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(content, encoding="utf-8")

    status = "✅ ALL CHECKS PASSED" if all_passed else "❌ ONE OR MORE CHECKS FAILED"
    print(f"\n{status}")
    print(f"Report written → {REPORT_PATH}")
    print("────────────────────────────────────────────────────────\n")

    return all_passed


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    passed = generate_report()
    sys.exit(0 if passed else 1)