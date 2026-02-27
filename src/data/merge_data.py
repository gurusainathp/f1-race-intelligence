"""
src/data/merge_data.py
----------------------
Merges all individually cleaned F1 tables into a single flat dataset.

Reads:
  data/interim/*_clean.csv  (produced by src/data/clean_data.py)

Writes:
  data/interim/cleaned_merged_data.csv

This file is the canonical intermediate artifact — it contains one row
per driver per race with all contextual fields denormalized onto it.
It is NOT yet the ML-ready feature matrix; that is built by
src/data/build_master_table.py after feature engineering is applied.

Join logic (all LEFT joins from results as the spine):
  results          <- spine  (one row per driver per race)
    + races        <- race context (year, round, circuit, date)
    + circuits     <- circuit metadata (name, country, lat, lng, alt)
    + drivers      <- driver identity (full_name, nationality, dob)
    + constructors <- team identity (name, nationality)
    + status       <- status label for statusId (for is_dnf derivation)
    + qualifying   <- qualifying position and session times
    + pit_stops    <- aggregated pit stop metrics per driver per race
    + lap_times    <- aggregated lap time metrics per driver per race

Status is joined early (after constructors) so that is_dnf and dnf_type
can be derived from the authoritative status label, not from a pre-existing
flag that may have been set inconsistently in clean_data.py.

Run:
  python src/data/merge_data.py
"""

import logging
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from constants import (
    compute_is_dnf_series,
    compute_dnf_type_series,
)

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
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    return {}


_CONFIG = _load_config()
INTERIM_DIR = Path(_CONFIG.get("paths", {}).get("interim_data", "data/interim"))
OUTPUT_FILE = INTERIM_DIR / "cleaned_merged_data.csv"


# ===========================================================================
# Loader
# ===========================================================================

def load_clean_tables(interim_dir: Path) -> dict[str, pd.DataFrame]:
    """
    Load all cleaned CSV tables from data/interim/.

    Returns:
        dict mapping table name -> DataFrame
    """
    tables = [
        "circuits", "drivers", "constructors", "races",
        "results", "qualifying", "lap_times", "pit_stops", "status",
    ]
    loaded = {}
    for name in tables:
        path = interim_dir / f"{name}_clean.csv"
        if not path.exists():
            raise FileNotFoundError(
                f"Clean file not found: {path}\n"
                f"Run src/data/clean_data.py first."
            )
        df = pd.read_csv(path, low_memory=False)
        log.info("Loaded %-20s  %d rows, %d cols", f"{name}_clean.csv", len(df), len(df.columns))
        loaded[name] = df
    return loaded


# ===========================================================================
# Pre-aggregation helpers
# ===========================================================================

def aggregate_qualifying(df_qual: pd.DataFrame) -> pd.DataFrame:
    """
    Reduce qualifying to one row per (raceId, driverId).

    Columns retained:
      raceId, driverId, quali_position, q1_ms, q2_ms, q3_ms, best_quali_ms
    """
    log.info("Pre-processing qualifying...")
    df = df_qual.copy()
    df = df.rename(columns={"position": "quali_position"})

    # Drop constructorId and number — duplicated in results
    df = df.drop(columns=["constructorId", "number"], errors="ignore")

    before = len(df)
    df = df.drop_duplicates(subset=["raceId", "driverId"], keep="first")
    if len(df) < before:
        log.warning("  Dropped %d duplicate qualifying rows.", before - len(df))

    log.info("  Qualifying aggregated: %d rows", len(df))
    return df


def aggregate_pit_stops(df_pits: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate pit_stops to one row per (raceId, driverId).

    Derived columns:
      total_pit_stops      : number of stops made
      total_pit_time_ms    : sum of all pit durations
      avg_pit_duration_ms  : mean pit duration
      min_pit_duration_ms  : fastest individual stop
    """
    log.info("Aggregating pit_stops...")
    agg = (
        df_pits.groupby(["raceId", "driverId"])
        .agg(
            total_pit_stops=("stop", "count"),
            total_pit_time_ms=("pit_duration_ms", "sum"),
            avg_pit_duration_ms=("pit_duration_ms", "mean"),
            min_pit_duration_ms=("pit_duration_ms", "min"),
        )
        .reset_index()
    )

    for col in ["total_pit_time_ms", "avg_pit_duration_ms", "min_pit_duration_ms"]:
        agg[col] = agg[col].round(1)

    log.info("  Pit stops aggregated: %d driver-race rows", len(agg))
    return agg


def aggregate_lap_times(df_laps: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate lap_times to one row per (raceId, driverId).

    Derived columns:
      laps_completed        : total laps with a recorded time
      avg_lap_time_ms       : mean lap time across all recorded laps
      median_lap_time_ms    : median lap time (robust to SC outliers)
      std_lap_time_ms       : standard deviation (consistency proxy)
      fastest_lap_ms        : personal fastest lap in the race
      lap_time_consistency  : 1 - (std / mean), bounded [0, 1]
    """
    log.info("Aggregating lap_times (large — may take a moment)...")
    agg = (
        df_laps.groupby(["raceId", "driverId"])["lap_time_ms"]
        .agg(
            laps_completed="count",
            avg_lap_time_ms="mean",
            median_lap_time_ms="median",
            std_lap_time_ms="std",
            fastest_lap_ms="min",
        )
        .reset_index()
    )

    agg["lap_time_consistency"] = (
        1 - (agg["std_lap_time_ms"] / agg["avg_lap_time_ms"])
    ).clip(0, 1).round(4)

    for col in ["avg_lap_time_ms", "median_lap_time_ms", "std_lap_time_ms", "fastest_lap_ms"]:
        agg[col] = agg[col].round(1)

    log.info("  Lap times aggregated: %d driver-race rows", len(agg))
    return agg


# ===========================================================================
# Main merge
# ===========================================================================

def build_merged_dataset(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Join all cleaned tables onto the results spine.

    Join order and rationale:
      1. results         — spine (one row per driver per race)
      2. races           — race context: year, round, date, circuitId
      3. circuits        — circuit metadata via circuitId
      4. drivers         — driver identity via driverId
      5. constructors    — team identity via constructorId
      6. status          — status label via statusId (REQUIRED for is_dnf derivation)
      7. qualifying_agg  — qualifying position + session times
      8. pit_stops_agg   — aggregated pit stop metrics
      9. lap_times_agg   — aggregated lap time metrics

    Status is joined at step 6, before enrichment, so that is_dnf and
    dnf_type can be computed from the actual status label in enrich_merged().
    This is the only authoritative source — do not rely on is_dnf flags
    that were set in clean_data.py.
    """
    log.info("=" * 55)
    log.info("Building merged dataset...")

    # ── Step 1: results spine ───────────────────────────────────────────────
    df = tables["results"].copy()
    log.info("  Spine (results):        %d rows", len(df))

    # ── Step 2: + races ─────────────────────────────────────────────────────
    races_cols = ["raceId", "year", "round", "circuitId", "name", "date",
                  "fp1_date", "fp2_date", "fp3_date", "quali_date", "sprint_date"]
    races_cols = [c for c in races_cols if c in tables["races"].columns]
    df = df.merge(
        tables["races"][races_cols].rename(columns={"name": "race_name"}),
        on="raceId", how="left", validate="many_to_one",
    )
    log.info("  After + races:          %d rows", len(df))

    # ── Step 3: + circuits ──────────────────────────────────────────────────
    circuit_cols = ["circuitId", "circuitRef", "name", "location", "country", "lat", "lng", "alt"]
    circuit_cols = [c for c in circuit_cols if c in tables["circuits"].columns]
    df = df.merge(
        tables["circuits"][circuit_cols].rename(columns={"name": "circuit_name"}),
        on="circuitId", how="left", validate="many_to_one",
    )
    log.info("  After + circuits:       %d rows", len(df))

    # ── Step 4: + drivers ───────────────────────────────────────────────────
    driver_cols = ["driverId", "driverRef", "full_name", "nationality", "dob", "code"]
    driver_cols = [c for c in driver_cols if c in tables["drivers"].columns]
    df = df.merge(
        tables["drivers"][driver_cols].rename(columns={
            "nationality": "driver_nationality",
            "code": "driver_code",
        }),
        on="driverId", how="left", validate="many_to_one",
    )
    log.info("  After + drivers:        %d rows", len(df))

    # ── Step 5: + constructors ──────────────────────────────────────────────
    constructor_cols = ["constructorId", "constructorRef", "name", "nationality"]
    constructor_cols = [c for c in constructor_cols if c in tables["constructors"].columns]
    df = df.merge(
        tables["constructors"][constructor_cols].rename(columns={
            "name": "constructor_name",
            "nationality": "constructor_nationality",
        }),
        on="constructorId", how="left", validate="many_to_one",
    )
    log.info("  After + constructors:   %d rows", len(df))

    # ── Step 6: + status (label lookup — critical for is_dnf derivation) ───
    # Only bring in statusId + status label; do not overwrite any results col.
    status_cols = ["statusId", "status"]
    status_cols = [c for c in status_cols if c in tables["status"].columns]

    # If results already has a 'status' column (from clean_data.py), drop it
    # first — the joined label from the status table is authoritative.
    if "status" in df.columns:
        df = df.drop(columns=["status"])
        log.info("  Dropped pre-existing 'status' column from results (will re-join from status table)")

    df = df.merge(
        tables["status"][status_cols],
        on="statusId", how="left", validate="many_to_one",
    )

    # Verify no orphan statusIds after the join
    orphans = df["statusId"].notna() & df["status"].isna()
    if orphans.sum() > 0:
        log.warning(
            "  ⚠ %d results rows have a statusId with no matching label in status table.",
            orphans.sum(),
        )
    else:
        log.info("  ✓ All statusId values resolved to a status label.")

    log.info("  After + status:         %d rows", len(df))

    # ── Step 7: + qualifying ────────────────────────────────────────────────
    qual_agg = aggregate_qualifying(tables["qualifying"])
    df = df.merge(qual_agg, on=["raceId", "driverId"], how="left")
    log.info("  After + qualifying:     %d rows", len(df))

    # ── Step 8: + pit stops ─────────────────────────────────────────────────
    pit_agg = aggregate_pit_stops(tables["pit_stops"])
    df = df.merge(pit_agg, on=["raceId", "driverId"], how="left")
    log.info("  After + pit_stops:      %d rows", len(df))

    # ── Step 9: + lap times ─────────────────────────────────────────────────
    lap_agg = aggregate_lap_times(tables["lap_times"])
    df = df.merge(lap_agg, on=["raceId", "driverId"], how="left")
    log.info("  After + lap_times:      %d rows", len(df))

    return df


# ===========================================================================
# Post-merge enrichment
# ===========================================================================

def enrich_merged(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add derived columns that require the fully merged context.

    Columns added:
      is_dnf              : derived from status label via constants.py
                            (replaces any pre-existing is_dnf flag)
      dnf_type            : 'mechanical' | 'crash' | 'other' | None
      driver_age_at_race  : driver age in years on race day
      qualifying_gap_ms   : best_quali_ms minus pole time for that race
      qualifying_gap_pct  : qualifying_gap_ms / pole_time * 100
      season_round_pct    : round / max_round_in_season  (0–1 progress)
    """
    log.info("Enriching merged dataset...")

    # ── is_dnf and dnf_type from status label ───────────────────────────────
    # This is the single authoritative derivation across the pipeline.
    # build_master_table.py will re-validate this but derives from the same
    # constants.py classifiers, so results will always be consistent.
    if "status" in df.columns:
        log.info("  Deriving is_dnf and dnf_type from status label...")
        df["is_dnf"]   = compute_is_dnf_series(df["status"])
        df["dnf_type"] = compute_dnf_type_series(df["status"])

        n_dnf = int(df["is_dnf"].sum())
        log.info(
            "  is_dnf: %d DNFs / %d total (%.1f%%)",
            n_dnf, len(df), n_dnf / len(df) * 100,
        )
    else:
        log.warning(
            "  'status' column not found after merge — is_dnf cannot be "
            "derived from status label. Check that status table joined correctly."
        )

    # ── Driver age at race ──────────────────────────────────────────────────
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["dob"]  = pd.to_datetime(df["dob"],  errors="coerce")

    has_dob = df["dob"].notna() & df["date"].notna()
    df["driver_age_at_race"] = np.nan
    df.loc[has_dob, "driver_age_at_race"] = (
        (df.loc[has_dob, "date"] - df.loc[has_dob, "dob"]).dt.days / 365.25
    ).round(2)

    # ── Qualifying gap to pole ──────────────────────────────────────────────
    pole_times = (
        df[df["best_quali_ms"].notna()]
        .groupby("raceId")["best_quali_ms"]
        .min()
        .rename("pole_quali_ms")
    )
    df = df.merge(pole_times, on="raceId", how="left")

    df["qualifying_gap_ms"]  = (df["best_quali_ms"] - df["pole_quali_ms"]).round(1)
    df["qualifying_gap_pct"] = (
        (df["qualifying_gap_ms"] / df["pole_quali_ms"]) * 100
    ).round(4)

    # ── Season progress ─────────────────────────────────────────────────────
    max_rounds = (
        df.groupby("year")["round"]
        .max()
        .rename("max_round_in_season")
    )
    df = df.merge(max_rounds, on="year", how="left")
    df["season_round_pct"] = (df["round"] / df["max_round_in_season"]).round(4)

    log.info("  Enrichment complete. Final shape: %s", df.shape)
    return df


# ===========================================================================
# Column ordering and final tidy
# ===========================================================================

_RACE_CONTEXT_COLS = [
    "raceId", "year", "round", "season_round_pct", "race_name",
    "date", "circuitId", "circuit_name", "circuitRef", "location",
    "country", "lat", "lng", "alt",
]
_DRIVER_COLS = [
    "driverId", "driverRef", "driver_code", "full_name",
    "driver_nationality", "dob", "driver_age_at_race",
]
_CONSTRUCTOR_COLS = [
    "constructorId", "constructorRef", "constructor_name", "constructor_nationality",
]
_RESULT_COLS = [
    "resultId", "grid", "position", "positionText", "positionOrder",
    "points", "laps", "milliseconds", "statusId", "status",
    "is_dnf", "dnf_type", "is_podium",
    "fastestLap", "rank", "fastestLapTime_ms", "fastestLapSpeed",
]
_QUALI_COLS = [
    "quali_position", "q1_ms", "q2_ms", "q3_ms",
    "best_quali_ms", "pole_quali_ms", "qualifying_gap_ms", "qualifying_gap_pct",
]
_PIT_COLS = [
    "total_pit_stops", "total_pit_time_ms", "avg_pit_duration_ms", "min_pit_duration_ms",
]
_LAP_COLS = [
    "laps_completed", "avg_lap_time_ms", "median_lap_time_ms",
    "std_lap_time_ms", "fastest_lap_ms", "lap_time_consistency",
]
_SESSION_DATE_COLS = ["fp1_date", "fp2_date", "fp3_date", "quali_date", "sprint_date"]

COLUMN_ORDER = (
    _RACE_CONTEXT_COLS
    + _DRIVER_COLS
    + _CONSTRUCTOR_COLS
    + _RESULT_COLS
    + _QUALI_COLS
    + _PIT_COLS
    + _LAP_COLS
    + _SESSION_DATE_COLS
)


def reorder_columns(df: pd.DataFrame) -> pd.DataFrame:
    ordered   = [c for c in COLUMN_ORDER if c in df.columns]
    remainder = [c for c in df.columns if c not in ordered]
    if remainder:
        log.info("  Appending %d unordered columns: %s", len(remainder), remainder)
    return df[ordered + remainder]


# ===========================================================================
# Orchestrator
# ===========================================================================

def run_merge(
    interim_dir: Path = INTERIM_DIR,
    output_file: Path = OUTPUT_FILE,
) -> pd.DataFrame:
    """
    Full merge pipeline: load -> join -> enrich -> save.

    Status is joined as a first-class table so is_dnf and dnf_type are
    derived from the authoritative label, not from pre-existing flags.
    """
    tables = load_clean_tables(interim_dir)
    df = build_merged_dataset(tables)
    df = enrich_merged(df)
    df = reorder_columns(df)

    null_pct_overall = df.isna().mean().mean() * 100
    log.info("Overall null rate in merged dataset: %.1f%%", null_pct_overall)

    high_null_cols = df.columns[df.isna().mean() > 0.5].tolist()
    if high_null_cols:
        log.warning(
            "  %d columns >50%% null (expected for pre-modern era): %s",
            len(high_null_cols), high_null_cols,
        )

    output_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_file, index=False)
    log.info("=" * 55)
    log.info("Saved merged dataset -> %s", output_file)
    log.info("Final shape: %d rows x %d columns", *df.shape)
    return df


def print_merge_summary(df: pd.DataFrame) -> None:
    """Print column-group null rates for a quick quality check."""
    groups = {
        "Race context":    _RACE_CONTEXT_COLS,
        "Driver":          _DRIVER_COLS,
        "Constructor":     _CONSTRUCTOR_COLS,
        "Results":         _RESULT_COLS,
        "Qualifying":      _QUALI_COLS,
        "Pit stops":       _PIT_COLS,
        "Lap times":       _LAP_COLS,
        "Session dates":   _SESSION_DATE_COLS,
    }
    print("\n" + "=" * 55)
    print(f"{'GROUP':<22} {'COLS':>5}  {'AVG NULL %':>10}")
    print("-" * 55)
    for group_name, cols in groups.items():
        present = [c for c in cols if c in df.columns]
        if not present:
            continue
        avg_null = df[present].isna().mean().mean() * 100
        print(f"{group_name:<22} {len(present):>5}  {avg_null:>9.1f}%")
    print("=" * 55)
    print(f"Total shape: {df.shape[0]:,} rows x {df.shape[1]} columns")
    print("=" * 55)


# ===========================================================================
# Entry point
# ===========================================================================

if __name__ == "__main__":
    merged_df = run_merge(interim_dir=INTERIM_DIR, output_file=OUTPUT_FILE)
    print_merge_summary(merged_df)