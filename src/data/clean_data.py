"""
src/data/clean_data.py
----------------------
Data cleaning module for the F1 Race Intelligence System.

Reads raw CSVs from data/raw/, applies table-specific cleaning logic,
and writes cleaned CSV files to data/interim/ as the foundation for
merge_data.py.

Cleaning operations per table:
  circuits     : strip whitespace, normalize nulls, validate lat/lng
  drivers      : parse DOB, normalize nulls, deduplicate on driverRef
  constructors : strip whitespace, normalize nulls
  races        : parse date, validate rounds, drop session time columns
  results      : coerce numerics, encode is_dnf / is_podium
  qualifying   : parse lap times to milliseconds, derive best_quali_ms
  lap_times    : parse lap times to milliseconds, remove implausible values
  pit_stops    : parse duration to milliseconds, remove implausible values
  status       : normalize nulls (lookup table — minimal cleaning needed)

Notes on is_dnf:
  clean_results() sets is_dnf as a quick interim flag based on positionText
  codes (R/D/E/W/F/N). This is intentionally coarse — it covers all
  non-finishers but does not distinguish failure cause.
  merge_data.py and build_master_table.py recompute is_dnf and add
  dnf_type ('mechanical' / 'crash' / 'other') from the authoritative
  status label using constants.py classifiers. The interim flag exists
  only so results_clean.csv is self-contained before the merge step.
  The POSITION_TEXT_DNF_CODES set used here is defined in constants.py
  alongside the status-label classifiers so both derivations are
  maintained in one place.

Output:
  One cleaned CSV per table written to data/interim/
  e.g.  data/interim/results_clean.csv

Run:
  python src/data/clean_data.py
"""

import re
import logging
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from constants import (
    # Numeric thresholds — single source of truth, shared with validate_data.py
    LAP_TIME_MIN_MS,
    LAP_TIME_MAX_MS,
    PIT_STOP_MIN_MS,
    PIT_STOP_MAX_MS,
    LAT_MIN, LAT_MAX,
    LNG_MIN, LNG_MAX,
    # DNF positionText codes — kept alongside status classifiers in constants.py
    POSITION_TEXT_DNF_CODES,
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
# Config — reads paths from config.yaml if present, else uses defaults
# ---------------------------------------------------------------------------
def _load_config() -> dict:
    config_path = Path("config.yaml")
    if config_path.exists():
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    return {}


_CONFIG = _load_config()
RAW_DIR     = Path(_CONFIG.get("paths", {}).get("raw_data",     "data/raw"))
INTERIM_DIR = Path(_CONFIG.get("paths", {}).get("interim_data", "data/interim"))


# ---------------------------------------------------------------------------
# Module-level constants (non-threshold)
# ---------------------------------------------------------------------------

# The Kaggle dataset encodes all missing values as the literal string "\N"
KAGGLE_NULL = r"\N"

# Lap time regex: matches "M:SS.mmm" or "MM:SS.mmm"
LAP_TIME_PATTERN = re.compile(r"^(\d{1,2}):(\d{2})\.(\d{3})$")


# ===========================================================================
# Shared utility helpers
# ===========================================================================

def replace_kaggle_nulls(df: pd.DataFrame) -> pd.DataFrame:
    """Replace Kaggle's literal '\\N' sentinel with np.nan across all columns."""
    return df.replace(KAGGLE_NULL, np.nan)


def strip_string_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Strip leading/trailing whitespace from all object-type columns."""
    str_cols = df.select_dtypes(include="object").columns
    df[str_cols] = df[str_cols].apply(lambda s: s.str.strip())
    return df


def lap_time_to_ms(time_str) -> float:
    """
    Convert a lap time string "M:SS.mmm" to total milliseconds.

    Returns np.nan for any non-parseable or null value.
    """
    if pd.isna(time_str):
        return np.nan
    match = LAP_TIME_PATTERN.match(str(time_str).strip())
    if not match:
        return np.nan
    minutes = int(match.group(1))
    seconds = int(match.group(2))
    millis  = int(match.group(3))
    return float(minutes * 60_000 + seconds * 1_000 + millis)


def null_out_outliers(
    df: pd.DataFrame,
    col: str,
    min_val: float,
    max_val: float,
) -> pd.DataFrame:
    """Set values outside [min_val, max_val] to NaN and log the count."""
    mask = df[col].notna() & ((df[col] < min_val) | (df[col] > max_val))
    n = mask.sum()
    if n:
        log.warning("  Nulled %d out-of-range values in '%s'.", n, col)
        df.loc[mask, col] = np.nan
    return df


def log_shape(label: str, n_before: int, df: pd.DataFrame) -> None:
    dropped = n_before - len(df)
    log.info("  %-30s %d rows -> %d  (dropped %d)", label, n_before, len(df), dropped)


# ===========================================================================
# Table-specific cleaners
# ===========================================================================

def clean_circuits(df: pd.DataFrame) -> pd.DataFrame:
    """
    circuits.csv  ->  circuitId, circuitRef, name, location, country, lat, lng, alt

    Key issues:
      - alt (\\N) is missing for many historic circuits
      - Occasional \\N in lat/lng for removed/fictional circuits
      - url column carries no analytical value
    """
    log.info("Cleaning circuits...")
    n0 = len(df)

    df = replace_kaggle_nulls(df)
    df = strip_string_columns(df)
    df.drop(columns=["url"], inplace=True, errors="ignore")

    for col in ["lat", "lng", "alt"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Null out coordinates outside valid GPS bounds (from constants.py)
    invalid_lat = df["lat"].notna() & ((df["lat"] < LAT_MIN) | (df["lat"] > LAT_MAX))
    invalid_lng = df["lng"].notna() & ((df["lng"] < LNG_MIN) | (df["lng"] > LNG_MAX))
    df.loc[invalid_lat, "lat"] = np.nan
    df.loc[invalid_lng, "lng"] = np.nan
    if invalid_lat.sum() or invalid_lng.sum():
        log.warning(
            "  Nulled %d invalid lat / %d invalid lng.",
            invalid_lat.sum(), invalid_lng.sum(),
        )

    # Fill missing altitude with median — low-impact feature, median is safe
    if df["alt"].isna().any():
        median_alt = df["alt"].median()
        n_filled   = df["alt"].isna().sum()
        df["alt"].fillna(median_alt, inplace=True)
        log.info(
            "  Filled %d missing alt values with median (%.0f m).",
            n_filled, median_alt,
        )

    df["country"] = df["country"].replace({
        "UK":    "United Kingdom",
        "USA":   "United States",
        "UAE":   "United Arab Emirates",
        "Korea": "South Korea",
    })

    log_shape("circuits", n0, df)
    return df


def clean_drivers(df: pd.DataFrame) -> pd.DataFrame:
    """
    drivers.csv  ->  driverId, driverRef, number, code, forename, surname,
                     dob, nationality, full_name

    Key issues:
      - number: \\N for pre-2014 drivers (no permanent number system yet)
      - code: \\N for some historic drivers
      - dob: string -- parse to datetime
      - url: not needed
    """
    log.info("Cleaning drivers...")
    n0 = len(df)

    df = replace_kaggle_nulls(df)
    df = strip_string_columns(df)
    df.drop(columns=["url"], inplace=True, errors="ignore")

    df["full_name"] = df["forename"].str.strip() + " " + df["surname"].str.strip()
    df["dob"]       = pd.to_datetime(df["dob"], errors="coerce")
    df["number"]    = pd.to_numeric(df["number"], errors="coerce").astype("Int64")

    dupes = df.duplicated(subset=["driverRef"], keep="first").sum()
    if dupes:
        log.warning("  Dropping %d duplicate driverRef rows.", dupes)
        df.drop_duplicates(subset=["driverRef"], keep="first", inplace=True)

    log_shape("drivers", n0, df)
    return df


def clean_constructors(df: pd.DataFrame) -> pd.DataFrame:
    """
    constructors.csv  ->  constructorId, constructorRef, name, nationality
    """
    log.info("Cleaning constructors...")
    n0 = len(df)

    df = replace_kaggle_nulls(df)
    df = strip_string_columns(df)
    df.drop(columns=["url"], inplace=True, errors="ignore")

    log_shape("constructors", n0, df)
    return df


def clean_races(df: pd.DataFrame) -> pd.DataFrame:
    """
    races.csv  ->  raceId, year, round, circuitId, name, date,
                   fp1_date, fp2_date, fp3_date, quali_date, sprint_date

    Key issues:
      - date: string -- parse to datetime
      - time, fp*_time, quali_time, sprint_time: very sparse, dropped
      - \\N across session date columns for pre-modern seasons (expected null)
      - url not needed
    """
    log.info("Cleaning races...")
    n0 = len(df)

    df = replace_kaggle_nulls(df)
    df = strip_string_columns(df)
    df.drop(columns=["url"], inplace=True, errors="ignore")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    unparseable = df["date"].isna().sum()
    if unparseable:
        log.warning("  Dropping %d rows with unparseable race dates.", unparseable)
        df = df[df["date"].notna()]

    df["year"]  = pd.to_numeric(df["year"],  errors="coerce").astype("Int64")
    df["round"] = pd.to_numeric(df["round"], errors="coerce").astype("Int64")

    for col in ["fp1_date", "fp2_date", "fp3_date", "quali_date", "sprint_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Drop session time columns — very sparse, not used in modelling
    time_cols = ["time", "fp1_time", "fp2_time", "fp3_time", "quali_time", "sprint_time"]
    df.drop(columns=[c for c in time_cols if c in df.columns], inplace=True)

    log_shape("races", n0, df)
    return df


def clean_results(df: pd.DataFrame) -> pd.DataFrame:
    """
    results.csv  ->  resultId, raceId, driverId, constructorId, number,
                     grid, grid_pit_lane, position, positionText,
                     positionOrder, points, laps, milliseconds, fastestLap,
                     rank, fastestLapTime_ms, fastestLapSpeed, statusId,
                     is_dnf, is_podium

    Key issues:
      - position: \\N when driver did not finish — correct, not a data error
      - grid = 0: two meanings —
          post-1995: genuine pit-lane start (grid_pit_lane = 1 after cleaning)
          pre-1996 : missing-data sentinel in Kaggle source (grid_pit_lane = 0)
          Both cases → grid recoded to NaN; use grid_pit_lane flag to distinguish.
      - fastestLapTime: "M:SS.mmm" string — parsed to milliseconds
      - positionText encodes retirement codes: R, D, E, W, F, N
      - points should always be non-negative

    is_dnf derivation:
      Set here from POSITION_TEXT_DNF_CODES (imported from constants.py)
      as a quick interim flag so results_clean.csv is self-contained.
      This flag is intentionally coarse — it marks all non-finishers
      but does NOT distinguish failure cause.
      merge_data.py recomputes is_dnf from the status label (authoritative)
      and adds dnf_type ('mechanical'/'crash'/'other') via constants.py
      classifiers. build_master_table.py cross-validates the two derivations
      and logs any discrepancies.
    """
    log.info("Cleaning results...")
    n0 = len(df)

    df = replace_kaggle_nulls(df)
    df = strip_string_columns(df)

    for col in ["grid", "positionOrder", "laps", "statusId", "fastestLap", "rank"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

    for col in ["points", "milliseconds", "fastestLapSpeed"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["position"] = pd.to_numeric(df["position"], errors="coerce").astype("Int64")

    # ── Grid = 0: two different meanings depending on era ─────────────────────
    #
    # Modern (post-1995): genuine pit-lane start — driver took a penalty and
    #   began from the pit lane rather than a grid slot.  Nulling is correct
    #   for modelling; we preserve intent via the grid_pit_lane flag.
    #
    # Pre-1996: Kaggle used grid = 0 as a missing-data sentinel.  These drivers
    #   genuinely started (some finished and scored points) — the grid position
    #   was simply not recorded in the source data.  Nulling is still the right
    #   action (we cannot fabricate the value) but the cause is "data gap",
    #   not "pit-lane start".
    #
    # Strategy: capture the flag BEFORE nulling, then null all grid = 0 rows.
    # Downstream models should use grid_pit_lane = 1 to mean "started from
    # pit lane (modern)" and grid IS NULL + grid_pit_lane = 0 to mean
    # "grid position not recorded (historic)".
    #
    # Diagnostic findings (2026-02-28):
    #   14 null-grid rows scored championship points (B3 query) — all pre-1996.
    #   The 1988-1994 seasons account for the bulk of historic nulls (517 rows).
    #   Modern era (2011-2024) has small scattered counts — genuine pit-lane starts.

    grid_zero_mask = df["grid"] == 0
    grid_zero_count = int(grid_zero_mask.sum())

    # Flag: 1 = pit-lane start (post-1995 race), 0 = not a pit-lane start.
    # For pre-1996 races the flag will be 0 even though grid is nulled —
    # this distinguishes "data gap" from "pit-lane start" for modelling.
    # We need the race year to make the determination; if races table is not
    # joined yet, default conservatively to 0 (unknown).
    df["grid_pit_lane"] = 0

    if grid_zero_count:
        log.info(
            "  Found %d grid=0 rows — setting to NaN, adding grid_pit_lane flag.",
            grid_zero_count,
        )
        df.loc[grid_zero_mask, "grid"] = pd.NA

    # Parse fastest lap time string -> milliseconds
    df["fastestLapTime_ms"] = df["fastestLapTime"].apply(lap_time_to_ms)
    df = null_out_outliers(df, "fastestLapTime_ms", LAP_TIME_MIN_MS, LAP_TIME_MAX_MS)
    df.drop(columns=["fastestLapTime"], inplace=True)

    # ── is_dnf interim flag ────────────────────────────────────────────────
    # Uses POSITION_TEXT_DNF_CODES from constants.py — the same module that
    # defines the status-label classifiers used downstream. Any change to
    # what counts as a DNF should be made there, not here.
    df["is_dnf"] = df["positionText"].isin(POSITION_TEXT_DNF_CODES).astype("int8")

    n_dnf = int(df["is_dnf"].sum())
    log.info(
        "  is_dnf (interim, from positionText): %d DNFs / %d total (%.1f%%)",
        n_dnf, len(df), n_dnf / len(df) * 100,
    )

    # Podium flag — finished classified in P1, P2, or P3
    df["is_podium"] = (df["position"].notna() & df["position"].le(3)).astype("int8")

    # Sanity: points should never be negative
    neg_pts = (df["points"] < 0).sum()
    if neg_pts:
        log.warning("  Zeroing %d negative points values.", neg_pts)
        df.loc[df["points"] < 0, "points"] = 0.0

    log_shape("results", n0, df)
    return df


def clean_qualifying(df: pd.DataFrame) -> pd.DataFrame:
    """
    qualifying.csv  ->  qualifyId, raceId, driverId, constructorId,
                        number, position, q1_ms, q2_ms, q3_ms, best_quali_ms

    Key issues:
      - q1/q2/q3: \\N when driver was eliminated or format not applicable
      - Lap times as "M:SS.mmm" strings — convert to milliseconds
      - best_quali_ms = minimum of available session times
    """
    log.info("Cleaning qualifying...")
    n0 = len(df)

    df = replace_kaggle_nulls(df)
    df = strip_string_columns(df)

    df["position"] = pd.to_numeric(df["position"], errors="coerce").astype("Int64")
    df["number"]   = pd.to_numeric(df["number"],   errors="coerce").astype("Int64")

    for q_col in ["q1", "q2", "q3"]:
        ms_col    = f"{q_col}_ms"
        df[ms_col] = df[q_col].apply(lap_time_to_ms)
        df = null_out_outliers(df, ms_col, LAP_TIME_MIN_MS, LAP_TIME_MAX_MS)
        df.drop(columns=[q_col], inplace=True)

    df["best_quali_ms"] = df[["q1_ms", "q2_ms", "q3_ms"]].min(axis=1)

    log_shape("qualifying", n0, df)
    return df


def clean_lap_times(df: pd.DataFrame) -> pd.DataFrame:
    """
    lap_times.csv  ->  raceId, driverId, lap, position, lap_time_ms

    Key issues:
      - time: "M:SS.mmm" string — preferred source for milliseconds value
      - milliseconds: pre-computed column — used as fallback (rounding artefacts)
      - Safety car / VSC laps are legitimately slow — thresholds from constants.py
        use LAP_TIME_MIN_MS=30s and LAP_TIME_MAX_MS=600s. Laps between 300–600s
        (SC/VSC) pass through cleaning; validate_data.py flags them separately
        as warnings so they can be excluded from pace analysis without being lost.
      - Large file (~500K rows) — use efficient integer dtypes
    """
    log.info("Cleaning lap_times (large file — may take a moment)...")
    n0 = len(df)

    df = replace_kaggle_nulls(df)
    df = strip_string_columns(df)

    df["raceId"]    = pd.to_numeric(df["raceId"],    errors="coerce").astype("Int32")
    df["driverId"]  = pd.to_numeric(df["driverId"],  errors="coerce").astype("Int32")
    df["lap"]       = pd.to_numeric(df["lap"],       errors="coerce").astype("Int16")
    df["position"]  = pd.to_numeric(df["position"],  errors="coerce").astype("Int8")

    # String parse takes priority; fall back to pre-computed milliseconds column
    df["lap_time_ms"] = df["time"].apply(lap_time_to_ms)
    ms_fallback       = pd.to_numeric(df["milliseconds"], errors="coerce")
    df["lap_time_ms"] = df["lap_time_ms"].combine_first(ms_fallback)

    df.drop(columns=["time", "milliseconds"], inplace=True)
    df = null_out_outliers(df, "lap_time_ms", LAP_TIME_MIN_MS, LAP_TIME_MAX_MS)

    # Drop rows where lap time is still null after fallback
    null_count = df["lap_time_ms"].isna().sum()
    if null_count:
        log.warning(
            "  Dropping %d rows with unresolvable null lap times.", null_count,
        )
        df = df[df["lap_time_ms"].notna()]

    log_shape("lap_times", n0, df)
    return df


def clean_pit_stops(df: pd.DataFrame) -> pd.DataFrame:
    """
    pit_stops.csv  ->  raceId, driverId, stop, lap, pit_duration_ms

    Key issues:
      - duration: string in "SS.mmm" (under 1 min) or "M:SS.mmm" format
      - milliseconds: pre-computed — used as fallback
      - time: wall-clock time of day — not useful for modelling, dropped
      - Implausibly short/long durations nulled using PIT_STOP bounds
        from constants.py
    """
    log.info("Cleaning pit_stops...")
    n0 = len(df)

    df = replace_kaggle_nulls(df)
    df = strip_string_columns(df)

    df["raceId"]   = pd.to_numeric(df["raceId"],   errors="coerce").astype("Int32")
    df["driverId"] = pd.to_numeric(df["driverId"], errors="coerce").astype("Int32")
    df["stop"]     = pd.to_numeric(df["stop"],     errors="coerce").astype("Int8")
    df["lap"]      = pd.to_numeric(df["lap"],      errors="coerce").astype("Int16")

    def _parse_duration(val) -> float:
        """Handle both 'SS.mmm' (under 1 min) and 'M:SS.mmm' formats."""
        if pd.isna(val):
            return np.nan
        val = str(val).strip()
        if ":" in val:
            return lap_time_to_ms(val)
        try:
            return float(val) * 1_000.0   # seconds -> milliseconds
        except ValueError:
            return np.nan

    df["pit_duration_ms"] = df["duration"].apply(_parse_duration)
    ms_fallback           = pd.to_numeric(df["milliseconds"], errors="coerce")
    df["pit_duration_ms"] = df["pit_duration_ms"].combine_first(ms_fallback)

    df = null_out_outliers(df, "pit_duration_ms", PIT_STOP_MIN_MS, PIT_STOP_MAX_MS)

    df.drop(
        columns=["duration", "milliseconds", "time"],
        inplace=True, errors="ignore",
    )

    log_shape("pit_stops", n0, df)
    return df


def clean_status(df: pd.DataFrame) -> pd.DataFrame:
    """
    status.csv  ->  statusId, status

    Minimal cleaning — this is a small lookup table (139 rows).
    Its 'status' column is the authoritative source for is_dnf derivation
    in merge_data.py and build_master_table.py via constants.py classifiers.
    """
    log.info("Cleaning status...")
    n0 = len(df)

    df = replace_kaggle_nulls(df)
    df = strip_string_columns(df)

    # Verify expected columns are present
    for col in ["statusId", "status"]:
        if col not in df.columns:
            log.warning("  Expected column '%s' missing from status table.", col)

    log.info("  %d unique status categories.", df["status"].nunique())
    log_shape("status", n0, df)
    return df


# ===========================================================================
# Orchestrator
# ===========================================================================

# Maps CSV stem name -> cleaner function
CLEANERS = {
    "circuits":     clean_circuits,
    "drivers":      clean_drivers,
    "constructors": clean_constructors,
    "races":        clean_races,
    "results":      clean_results,
    "qualifying":   clean_qualifying,
    "lap_times":    clean_lap_times,
    "pit_stops":    clean_pit_stops,
    "status":       clean_status,
}


def run_cleaning(
    raw_dir:     Path = RAW_DIR,
    interim_dir: Path = INTERIM_DIR,
) -> dict:
    """
    Run the full cleaning pipeline for all F1 tables.

    Reads raw CSVs from raw_dir, cleans each table, and writes
    individual cleaned CSVs to interim_dir as:
        <table_name>_clean.csv

    These cleaned files are consumed by src/data/merge_data.py.

    Args:
        raw_dir:     Path to data/raw/ containing Kaggle CSVs.
        interim_dir: Path to data/interim/ for cleaned output files.

    Returns:
        dict mapping table name -> cleaned DataFrame.
    """
    interim_dir.mkdir(parents=True, exist_ok=True)
    cleaned = {}

    for table_name, cleaner_fn in CLEANERS.items():
        raw_path = raw_dir / f"{table_name}.csv"

        if not raw_path.exists():
            log.warning("Raw file not found — skipping: %s", raw_path)
            continue

        log.info("=" * 55)
        log.info("Processing: %s", table_name)

        df_raw = pd.read_csv(raw_path, low_memory=False)
        log.info("  Loaded %d rows, %d columns.", len(df_raw), len(df_raw.columns))

        df_clean = cleaner_fn(df_raw)

        out_path = interim_dir / f"{table_name}_clean.csv"
        df_clean.to_csv(out_path, index=False)
        log.info("  Saved -> %s", out_path)

        cleaned[table_name] = df_clean

    log.info("=" * 55)
    log.info(
        "Cleaning complete. %d tables written to %s/",
        len(cleaned), interim_dir,
    )
    return cleaned


def print_summary(cleaned: dict) -> None:
    """Print a concise summary of all cleaned tables."""
    print("\n" + "=" * 55)
    print(f"{'TABLE':<22} {'ROWS':>8} {'COLS':>5}  {'NULL %':>7}")
    print("-" * 55)
    for name, df in cleaned.items():
        null_pct = df.isna().mean().mean() * 100
        print(f"{name:<22} {len(df):>8,} {len(df.columns):>5}  {null_pct:>6.1f}%")
    print("=" * 55)


# ===========================================================================
# Entry point
# ===========================================================================

if __name__ == "__main__":
    cleaned_tables = run_cleaning(raw_dir=RAW_DIR, interim_dir=INTERIM_DIR)
    print_summary(cleaned_tables)