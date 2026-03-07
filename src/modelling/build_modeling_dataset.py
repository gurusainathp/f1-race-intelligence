"""
src/modeling/build_modeling_dataset.py
---------------------------------------
Assembles the final modeling-ready dataset for predicting `is_podium`.

Reads five parquet feature stores from data/processed/features/ and
joins them into a single clean table saved to:

    data/processed/modeling/modeling_dataset.parquet

Source tables and their roles
------------------------------
  driver_race_pre.parquet          — race identifiers + pre-race setup
                                     (grid, grid_pit_lane, circuitId, etc.)
  driver_race_rolling.parquet      — primary in-season signal
                                     (cumulative within-season stats, shift(1))
  constructor_race_rolling.parquet — constructor in-season signal (shift(1))
  driver_season_features.parquet   — secondary signal: full prior season stats
  driver_race_full.parquet         — source of target variable: is_podium

Join sequence
-------------
  1. driver_race_pre       (base, filtered to race_year >= 2000)
  2. driver_race_rolling   (LEFT JOIN on raceId, driverId)
  3. constructor_race_rolling (LEFT JOIN on constructorId, race_year, round)
  4. driver_season[year-1] (LEFT JOIN on driverId for prior season stats)
  5. driver_race_full      (LEFT JOIN on raceId, driverId for target)

Null-fill rules
---------------
  Rolling features (round 1 of season — no prior races yet):
    rolling_podium_rate, rolling_dnf_rate, rolling_avg_finish_position,
    rolling_avg_qualifying_position → fill NaN with 0
    rolling_cumulative_points → fill NaN with 0
    # rolling_cumulative_podiums is dropped (rate is kept via rolling_podium_rate)

  Prior season features (rookies or first season >= 2000):
    prev_season_points       → fill NaN with 0
    prev_season_podium_rate  → fill NaN with 0
    has_prev_season          → 0 if no prior season data, else 1

  Constructor rolling follows the same round-1 fill logic.

  Median imputation (sparse cols — global median):
    qualifying_gap_ms, best_quali_ms, con_rolling_win_rate

Dropped columns (redundant / structural)
-----------------------------------------
  grid               — replaced by grid_imputed (no nulls, pit-lane safe)
  qualifying_position — same ordering signal as grid_imputed; gap_ms kept for pace
  rolling_races_counted, con_rolling_races_counted — correlate ~0.95 with round
  constructorId_drv_roll, race_year_drv_roll, round_drv_roll — join suffix artefacts

Deduplication
-------------
  Some driver-race pairs have two result rows (shared drives, dual constructors).
  After joining we dedup on (raceId, driverId), keeping the first row.
  This is consistent with Section 5 / 8 logic in validate_data.py.

Run
---
  python src/modeling/build_modeling_dataset.py
"""

import logging
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

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
# Paths
# ---------------------------------------------------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parents[2]

FEATURES_DIR = _PROJECT_ROOT / "data" / "processed" / "features"
MODELING_DIR = _PROJECT_ROOT / "data" / "processed" / "modeling"

# Inputs
DRIVER_RACE_PRE_PATH         = FEATURES_DIR / "driver_race_pre.parquet"
DRIVER_RACE_ROLLING_PATH     = FEATURES_DIR / "driver_race_rolling.parquet"
CONSTRUCTOR_ROLLING_PATH     = FEATURES_DIR / "constructor_race_rolling.parquet"
DRIVER_SEASON_PATH           = FEATURES_DIR / "driver_season_features.parquet"
DRIVER_RACE_FULL_PATH        = FEATURES_DIR / "driver_race_full.parquet"

# Output
MODELING_DATASET_PATH        = MODELING_DIR / "modeling_dataset.parquet"

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
YEAR_CUTOFF = 2000   # race_year >= YEAR_CUTOFF

# Columns that must NOT appear in the final modeling dataset.
# Hard-coded so the validator can cross-check against the same list.
FORBIDDEN_COLUMNS: set[str] = {
    # ── Post-race outcomes (direct leakage) ──────────────────────────────────
    "finish_position",
    "finish_position_order",
    "positionOrder",
    "positions_gained",
    "milliseconds",
    "time",
    "fastestLap",
    "fastest_lap_rank",
    "fastest_lap_ms",
    "avg_lap_time_ms",
    "lap_time_consistency",
    "pit_stop_count",
    "total_pit_time_ms",
    "avg_pit_duration_ms",
    "is_dnf",
    "dnf_type",
    "is_winner",
    "is_points_finish",
    "points",
    "laps",
    "statusId",
    "rolling_cumulative_wins",
    # rolling_cumulative_podiums — rate (rolling_podium_rate) is kept;
    # the raw count adds multicollinearity with cumulative_points
    "rolling_cumulative_podiums",
    # ── Redundant grid column — grid_imputed is the cleaned version ──────────
    # grid has nulls for pit-lane starts; grid_imputed is always filled.
    # Keeping both adds multicollinearity with no gain.
    "grid",
    # ── Redundant qualifying column ──────────────────────────────────────────
    # qualifying_position carries the same ordering signal as grid_imputed.
    # qualifying_gap_ms is kept — it provides pace signal independent of position.
    "qualifying_position",
    # ── Rolling race count columns — dataset mechanics, not features ─────────
    # rolling_races_counted and con_rolling_races_counted correlate ~0.95
    # with round number, which is already in the dataset. No predictive gain.
    "rolling_races_counted",
    "con_rolling_races_counted",
    # ── Structural suffix columns from the rolling join ──────────────────────
    # When driver_race_rolling is merged onto driver_race_pre both share
    # constructorId, race_year, and round. Pandas appends _drv_roll suffix
    # to the duplicates from the right frame — these must be dropped.
    "constructorId_drv_roll",
    "race_year_drv_roll",
    "round_drv_roll",
}

# Rolling feature columns that should be filled with 0 when NaN
# (occurs for round 1 of each season — no prior races yet)
ROLLING_FILL_ZERO: list[str] = [
    "rolling_cumulative_points",
    # rolling_cumulative_podiums dropped — in FORBIDDEN_COLUMNS
    "rolling_dnf_rate",
    "rolling_avg_finish_position",
    "rolling_avg_qualifying_position",
    # rolling_races_counted and con_rolling_races_counted are in FORBIDDEN_COLUMNS
    # and will be dropped — no need to fill them here.
    "con_rolling_cumulative_points",
    "con_rolling_podium_rate",
    "con_rolling_dnf_rate",
    "con_rolling_avg_finish_position",
]

# Prior-season feature columns filled with 0 for rookies
PRIOR_SEASON_FILL_ZERO: list[str] = [
    "prev_season_points",
    "prev_season_podium_rate",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load(path: Path, label: str) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"{label} not found at {path}\n"
            f"Run build_features.py first to generate all parquet files."
        )
    df = pd.read_parquet(path)
    log.info("  Loaded %-40s  %d rows × %d cols", label, *df.shape)
    return df


def _assert_cols(df: pd.DataFrame, cols: list[str], context: str) -> None:
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"[{context}] Missing expected columns: {missing}")


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def build_modeling_dataset() -> pd.DataFrame:
    """
    Assemble and return the modeling-ready DataFrame.
    Also saves it to MODELING_DATASET_PATH.
    """
    MODELING_DIR.mkdir(parents=True, exist_ok=True)

    log.info("=" * 60)
    log.info("BUILD MODELING DATASET")
    log.info("  Year filter  : race_year >= %d", YEAR_CUTOFF)
    log.info("  Output       : %s", MODELING_DATASET_PATH)
    log.info("=" * 60)

    # ── Load all source tables ───────────────────────────────────────────────
    log.info("Loading source parquets...")
    pre        = _load(DRIVER_RACE_PRE_PATH,     "driver_race_pre")
    drv_roll   = _load(DRIVER_RACE_ROLLING_PATH, "driver_race_rolling")
    con_roll   = _load(CONSTRUCTOR_ROLLING_PATH, "constructor_race_rolling")
    drv_season = _load(DRIVER_SEASON_PATH,       "driver_season_features")
    drv_full   = _load(DRIVER_RACE_FULL_PATH,    "driver_race_full")

    # ── Step 1: Filter base to post-2000 ────────────────────────────────────
    log.info("Step 1 — Filtering to race_year >= %d ...", YEAR_CUTOFF)
    _assert_cols(pre, ["race_year"], "driver_race_pre")
    pre = pre[pre["race_year"] >= YEAR_CUTOFF].copy()
    log.info("  Rows after filter: %d", len(pre))

    # ── Step 2: Join driver rolling features ────────────────────────────────
    log.info("Step 2 — Joining driver rolling features ...")
    _assert_cols(drv_roll, ["raceId", "driverId"], "driver_race_rolling")
    df = pre.merge(drv_roll, on=["raceId", "driverId"], how="left", suffixes=("", "_drv_roll"))
    log.info("  Rows after join: %d", len(df))

    # ── Step 3: Join constructor rolling features ────────────────────────────
    log.info("Step 3 — Joining constructor rolling features ...")
    _assert_cols(con_roll, ["constructorId", "race_year", "round"], "constructor_race_rolling")

    # Rename all rolling cols with con_ prefix to avoid collision with driver rolling
    con_roll_renamed = con_roll.rename(columns={
        "rolling_cumulative_points":   "con_rolling_cumulative_points",
        "rolling_podium_rate":         "con_rolling_podium_rate",
        "rolling_win_rate":            "con_rolling_win_rate",
        "rolling_dnf_rate":            "con_rolling_dnf_rate",
        "rolling_avg_finish_position": "con_rolling_avg_finish_position",
        "rolling_races_counted":       "con_rolling_races_counted",
    })
    df = df.merge(
        con_roll_renamed,
        on=["constructorId", "race_year", "round"],
        how="left",
        suffixes=("", "_con_roll"),
    )
    log.info("  Rows after join: %d", len(df))

    # ── Step 4: Join prior season driver features ────────────────────────────
    log.info("Step 4 — Joining prior season driver features (season N-1) ...")
    _assert_cols(drv_season, ["driverId", "race_year"], "driver_season_features")

    # Compute podium_rate from season table (podiums / races_entered)
    # Use existing podium_rate col if present, otherwise derive it
    if "podium_rate" not in drv_season.columns:
        if "podiums" in drv_season.columns and "races_entered" in drv_season.columns:
            drv_season = drv_season.copy()
            drv_season["podium_rate"] = np.where(
                drv_season["races_entered"] > 0,
                drv_season["podiums"] / drv_season["races_entered"],
                np.nan,
            )
        else:
            drv_season = drv_season.copy()
            drv_season["podium_rate"] = np.nan

    # Select only what we need from season table and shift year by +1
    # so that season 2022 stats become the prior-season signal for 2023 races
    prior = (
        drv_season[["driverId", "race_year", "total_points", "podium_rate"]]
        .copy()
        .rename(columns={
            "total_points": "prev_season_points",
            "podium_rate":  "prev_season_podium_rate",
        })
    )
    prior["race_year"] = prior["race_year"] + 1   # shift: season N stats → season N+1 join key

    df = df.merge(prior, on=["driverId", "race_year"], how="left")
    log.info("  Rows after join: %d", len(df))

    # ── Step 5: Join target variable ────────────────────────────────────────
    log.info("Step 5 — Joining target variable (is_podium) ...")
    _assert_cols(drv_full, ["raceId", "driverId", "is_podium"], "driver_race_full")
    target_df = drv_full[["raceId", "driverId", "is_podium"]].copy()
    df = df.merge(target_df, on=["raceId", "driverId"], how="left")
    log.info("  Rows after join: %d", len(df))

    # ── Step 6: Compute derived rolling_podium_rate ──────────────────────────
    log.info("Step 6 — Computing derived rolling_podium_rate ...")
    if "rolling_cumulative_podiums" in df.columns and "rolling_races_counted" in df.columns:
        df["rolling_podium_rate"] = np.where(
            df["rolling_races_counted"] > 0,
            df["rolling_cumulative_podiums"] / df["rolling_races_counted"],
            np.nan,
        )
    else:
        df["rolling_podium_rate"] = np.nan
        log.warning("  Could not compute rolling_podium_rate — source columns missing.")

    # ── Step 7a: Impute grid for pit-lane starts ─────────────────────────────
    # grid is NULL by design for pit-lane starters (grid_pit_lane = 1).
    # The model cannot consume NaN, so we impute: pit-lane starter gets
    # max(grid in that race) + 1, which is the standard F1 convention
    # (effectively: start from behind the entire grid).
    # grid_pit_lane = 1 remains as an explicit flag so the model knows
    # the value is imputed — do NOT drop it.
    log.info("Step 7a — Imputing grid for pit-lane starts ...")
    if "grid" in df.columns and "grid_pit_lane" in df.columns and "raceId" in df.columns:
        # Max grid position per race (ignoring pit-lane starts)
        race_max_grid = (
            df[df["grid"].notna()]
            .groupby("raceId")["grid"]
            .max()
            .rename("_race_max_grid")
        )
        df = df.join(race_max_grid, on="raceId")

        n_pl_starts = int((df["grid_pit_lane"] == 1).sum())
        n_grid_null = int(df["grid"].isna().sum())

        df["grid_imputed"] = np.where(
            df["grid"].isna(),
            df["_race_max_grid"] + 1,
            df["grid"],
        )
        df = df.drop(columns=["_race_max_grid"])

        # Verify: any remaining nulls in grid_imputed mean the entire race had
        # no grid data (very early era edge case — should not happen post-2000)
        n_still_null = int(df["grid_imputed"].isna().sum())
        log.info(
            "  Pit-lane starts: %d rows  |  grid nulls before: %d  |  grid_imputed nulls: %d",
            n_pl_starts, n_grid_null, n_still_null,
        )
        if n_still_null:
            log.warning(
                "  ⚠ %d rows have null grid_imputed — race had no grid data at all. "
                "Inspect raceIds: %s",
                n_still_null,
                df[df["grid_imputed"].isna()]["raceId"].unique()[:10].tolist(),
            )
    else:
        log.warning("  grid / grid_pit_lane / raceId not found — skipping grid imputation.")
        df["grid_imputed"] = df.get("grid", np.nan)

    # ── Step 7: has_prev_season flag + null-fill ─────────────────────────────
    log.info("Step 7 — Applying null-fill rules ...")

    # has_prev_season: 1 if driver had any season data the year before
    df["has_prev_season"] = df["prev_season_points"].notna().astype("int8")

    # Fill prior season NaNs with 0 (rookies and first season in dataset)
    for col in PRIOR_SEASON_FILL_ZERO:
        if col in df.columns:
            n_filled = int(df[col].isna().sum())
            df[col] = df[col].fillna(0.0)
            if n_filled:
                log.info("    %-40s  filled %d NaNs with 0 (rookies / no prior season)", col, n_filled)

    # Fill rolling NaNs with 0 (round 1 of each season)
    for col in ROLLING_FILL_ZERO:
        if col in df.columns:
            n_filled = int(df[col].isna().sum())
            df[col] = df[col].fillna(0.0)
            if n_filled:
                log.info("    %-40s  filled %d NaNs with 0 (round 1 season openers)", col, n_filled)

    # rolling_podium_rate after fill of races_counted (round 1 → rate = 0)
    if "rolling_podium_rate" in df.columns:
        n_filled = int(df["rolling_podium_rate"].isna().sum())
        df["rolling_podium_rate"] = df["rolling_podium_rate"].fillna(0.0)
        if n_filled:
            log.info("    %-40s  filled %d NaNs with 0", "rolling_podium_rate", n_filled)

    # ── Step 7b: Median imputation for sparse qualifying / constructor cols ─────
    # qualifying_gap_ms, best_quali_ms and con_rolling_win_rate can have moderate
    # null rates (pit-lane starts, penalties, round-1 no prior wins).
    # Fill with global median so the model sees a sensible central value rather
    # than NaN, which tree-based and linear models handle differently.
    log.info("Step 7b — Median-filling qualifying and constructor sparse cols ...")
    MEDIAN_FILL_COLS: list[str] = [
        "qualifying_gap_ms",
        "best_quali_ms",
        "con_rolling_win_rate",
    ]
    for col in MEDIAN_FILL_COLS:
        if col in df.columns:
            n_null  = int(df[col].isna().sum())
            med_val = df[col].median()
            df[col] = df[col].fillna(med_val)
            if n_null:
                log.info(
                    "    %-40s  filled %d NaNs with global median %.4f",
                    col, n_null, med_val,
                )

    # ── Step 8: Drop forbidden columns ──────────────────────────────────────
    log.info("Step 8 — Dropping forbidden post-race / redundant columns ...")
    cols_to_drop = [c for c in FORBIDDEN_COLUMNS if c in df.columns]
    if cols_to_drop:
        df = df.drop(columns=cols_to_drop)
        log.info("  Dropped %d columns: %s", len(cols_to_drop), cols_to_drop)
    else:
        log.info("  No forbidden columns present — nothing to drop.")

    # ── Step 9: Deduplicate on (raceId, driverId) ───────────────────────────
    log.info("Step 9 — Deduplicating on (raceId, driverId) ...")
    n_before = len(df)
    df = df.drop_duplicates(subset=["raceId", "driverId"], keep="first").reset_index(drop=True)
    n_dropped = n_before - len(df)
    if n_dropped:
        log.info("  Dropped %d duplicate rows (shared drives / dual constructors)", n_dropped)
    else:
        log.info("  No duplicates found.")

    # ── Step 10: Drop rows with null target ──────────────────────────────────
    log.info("Step 10 — Dropping rows with null is_podium ...")
    n_before = len(df)
    df = df[df["is_podium"].notna()].reset_index(drop=True)
    n_dropped = n_before - len(df)
    if n_dropped:
        log.warning("  Dropped %d rows with null is_podium — investigate source data.", n_dropped)
    df["is_podium"] = df["is_podium"].astype("int8")

    # ── Summary ──────────────────────────────────────────────────────────────
    n_podium   = int(df["is_podium"].sum())
    n_total    = len(df)
    podium_pct = n_podium / n_total * 100 if n_total > 0 else 0.0

    log.info("=" * 60)
    log.info("MODELING DATASET SUMMARY")
    log.info("  Rows           : %d", n_total)
    log.info("  Columns        : %d", len(df.columns))
    log.info("  Seasons        : %d – %d", int(df["race_year"].min()), int(df["race_year"].max()))
    log.info("  Drivers        : %d", df["driverId"].nunique())
    log.info("  Constructors   : %d", df["constructorId"].nunique())
    log.info("  Races          : %d", df["raceId"].nunique())
    log.info("  Podiums        : %d (%.1f%%)", n_podium, podium_pct)
    log.info("  Non-podiums    : %d (%.1f%%)", n_total - n_podium, 100 - podium_pct)
    log.info("  Rookies        : %d (has_prev_season = 0)", int((df["has_prev_season"] == 0).sum()))
    log.info("  Pit-lane starts: %d (grid_pit_lane = 1, grid_imputed used)", int((df.get("grid_pit_lane", pd.Series(dtype=int)) == 1).sum()) if "grid_pit_lane" in df.columns else 0)
    log.info("  Columns list   : %s", list(df.columns))
    log.info("=" * 60)

    # ── Save ─────────────────────────────────────────────────────────────────
    df.to_parquet(MODELING_DATASET_PATH, index=False, engine="pyarrow")
    size_kb = MODELING_DATASET_PATH.stat().st_size / 1024
    log.info("Saved -> %s  (%.1f KB)", MODELING_DATASET_PATH, size_kb)

    return df


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    build_modeling_dataset()