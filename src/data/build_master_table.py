"""
src/data/build_master_table.py
------------------------------
Produces the final analysis-ready master race table and loads all
cleaned tables into a SQLite database for SQL-based analysis.

Reads:
  data/interim/cleaned_merged_data.csv    (from src/data/merge_data.py)
  data/interim/*_clean.csv               (individual cleaned tables)
  sql/schema.sql                         (table DDL + indexes)
  sql/views.sql                          (analytical views)

Writes:
  data/processed/master_race_table.csv   — denormalized table, one row
                                           per driver per race
  data/processed/f1_database.db          — SQLite database containing:
                                             - all 8 cleaned source tables
                                             - master_race_table
                                             - 4 analytical views

Pipeline position:
  clean_data.py -> merge_data.py -> [THIS FILE] -> feature engineering

Run:
  python src/data/build_master_table.py
"""

import logging
import sqlite3
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

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
# Config — reads from config.yaml, falls back to defaults
# ---------------------------------------------------------------------------
def _load_config() -> dict:
    config_path = Path("config.yaml")
    if config_path.exists():
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    return {}


_CONFIG = _load_config()
INTERIM_DIR   = Path(_CONFIG.get("paths", {}).get("interim_data",   "data/interim"))
PROCESSED_DIR = Path(_CONFIG.get("paths", {}).get("processed_data", "data/processed"))
SQL_DIR       = Path(_CONFIG.get("paths", {}).get("sql_dir",        "sql"))

MERGED_FILE       = INTERIM_DIR   / "cleaned_merged_data.csv"
MASTER_TABLE_FILE = PROCESSED_DIR / "master_race_table.csv"
DB_FILE           = PROCESSED_DIR / "f1_database.db"


# ---------------------------------------------------------------------------
# SQL file paths
# All SQL lives in sql/ as standalone files — Python reads them, never
# embeds them. This keeps SQL version-controllable and independently runnable.
# ---------------------------------------------------------------------------
SCHEMA_SQL_FILE  = SQL_DIR / "schema.sql"
VIEWS_SQL_FILE   = SQL_DIR / "views.sql"


# ---------------------------------------------------------------------------
# Interim table map
# Maps SQLite table name -> cleaned CSV filename in data/interim/
# ---------------------------------------------------------------------------
INTERIM_TABLE_MAP = {
    "circuits":     "circuits_clean.csv",
    "drivers":      "drivers_clean.csv",
    "constructors": "constructors_clean.csv",
    "races":        "races_clean.csv",
    "results":      "results_clean.csv",
    "qualifying":   "qualifying_clean.csv",
    "lap_times":    "lap_times_clean.csv",
    "pit_stops":    "pit_stops_clean.csv",
}


# ===========================================================================
# Step 1: Build master_race_table from cleaned_merged_data.csv
# ===========================================================================

# Final column selection for the master table.
# Deliberate curation — every column here has either analytical or modelling
# value. Intermediate join scaffolding (max_round_in_season etc.) is dropped.
MASTER_TABLE_COLS = [
    # Race context
    "raceId", "year", "round", "season_round_pct",
    "race_name", "date",
    # Circuit
    "circuitId", "circuit_name", "circuitRef", "country", "lat", "lng", "alt",
    # Driver
    "driverId", "driverRef", "full_name", "driver_nationality",
    "dob", "driver_age_at_race",
    # Constructor
    "constructorId", "constructorRef", "constructor_name", "constructor_nationality",
    # Race result
    "grid", "position", "positionText", "positionOrder",
    "points", "laps", "milliseconds", "statusId",
    "is_dnf", "is_podium",
    "fastestLap", "rank", "fastestLapTime_ms", "fastestLapSpeed",
    # Qualifying
    "quali_position", "q1_ms", "q2_ms", "q3_ms",
    "best_quali_ms", "pole_quali_ms",
    "qualifying_gap_ms", "qualifying_gap_pct",
    # Pit stops (aggregated)
    "total_pit_stops", "total_pit_time_ms",
    "avg_pit_duration_ms", "min_pit_duration_ms",
    # Lap times (aggregated)
    "laps_completed", "avg_lap_time_ms", "median_lap_time_ms",
    "std_lap_time_ms", "fastest_lap_ms", "lap_time_consistency",
]


def build_master_table(merged_path: Path = MERGED_FILE) -> pd.DataFrame:
    """
    Load cleaned_merged_data.csv and produce the curated master race table.

    Adds these derived columns on top of what merge_data.py already built:
      grid_vs_finish_delta    : grid - position (positive = gained places)
      is_points_finish        : 1 if points > 0
      is_winner               : 1 if position == 1
      constructor_season_key  : constructorRef_year (era-aware grouping key)

    Args:
        merged_path: Path to cleaned_merged_data.csv

    Returns:
        Curated master race table DataFrame.
    """
    if not merged_path.exists():
        raise FileNotFoundError(
            f"Merged file not found: {merged_path}\n"
            f"Run src/data/merge_data.py first."
        )

    log.info("Loading merged dataset: %s", merged_path)
    df = pd.read_csv(merged_path, low_memory=False)
    log.info("  Loaded: %d rows x %d columns", *df.shape)

    # -----------------------------------------------------------------------
    # Derived columns
    # -----------------------------------------------------------------------

    # grid_vs_finish_delta: positive = gained positions from start to finish.
    # Only populated for classified finishers (position not null).
    df["grid_vs_finish_delta"] = np.where(
        df["grid"].notna() & df["position"].notna(),
        pd.to_numeric(df["grid"], errors="coerce") -
        pd.to_numeric(df["position"], errors="coerce"),
        np.nan,
    )

    # is_points_finish: any points scored in this race
    df["is_points_finish"] = (
        pd.to_numeric(df["points"], errors="coerce").fillna(0) > 0
    ).astype("int8")

    # is_winner: finished in P1
    df["is_winner"] = (
        pd.to_numeric(df["position"], errors="coerce").eq(1)
    ).astype("int8")

    # constructor_season_key: used for era-aware team grouping
    df["constructor_season_key"] = (
        df["constructorRef"].fillna("unknown").astype(str)
        + "_"
        + df["year"].astype(str)
    )

    # -----------------------------------------------------------------------
    # Select and order final columns
    # -----------------------------------------------------------------------
    extra_cols = [
        "grid_vs_finish_delta", "is_points_finish",
        "is_winner", "constructor_season_key",
    ]
    final_cols = [c for c in MASTER_TABLE_COLS if c in df.columns] + extra_cols

    missing = [c for c in MASTER_TABLE_COLS if c not in df.columns]
    if missing:
        log.warning(
            "  %d expected columns absent from merged data "
            "(likely pre-modern era NULLs): %s",
            len(missing), missing,
        )

    df = df[[c for c in final_cols if c in df.columns]].copy()

    # -----------------------------------------------------------------------
    # Type enforcement for SQLite / downstream compatibility
    # -----------------------------------------------------------------------
    for col in ["date", "dob"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%Y-%m-%d")

    int_cols = [
        "raceId", "year", "round", "circuitId", "driverId", "constructorId",
        "grid", "position", "positionOrder", "laps", "statusId",
        "fastestLap", "rank", "quali_position", "total_pit_stops", "laps_completed",
        "is_dnf", "is_podium", "is_winner", "is_points_finish",
    ]
    for col in int_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    float_cols = [
        "points", "milliseconds", "fastestLapSpeed", "lat", "lng", "alt",
        "driver_age_at_race", "season_round_pct",
        "qualifying_gap_pct", "qualifying_gap_ms",
        "best_quali_ms", "pole_quali_ms", "q1_ms", "q2_ms", "q3_ms",
        "total_pit_time_ms", "avg_pit_duration_ms", "min_pit_duration_ms",
        "avg_lap_time_ms", "median_lap_time_ms", "std_lap_time_ms",
        "fastest_lap_ms", "fastestLapTime_ms", "lap_time_consistency",
        "grid_vs_finish_delta",
    ]
    for col in float_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    log.info("  Master table built: %d rows x %d columns", *df.shape)
    return df


# ===========================================================================
# Step 2: Load into SQLite
# ===========================================================================

def _read_sql_file(path: Path) -> str:
    """Read a .sql file and return its contents as a string."""
    if not path.exists():
        raise FileNotFoundError(
            f"SQL file not found: {path}\n"
            f"Ensure the sql/ directory is present at the project root."
        )
    return path.read_text(encoding="utf-8")


def load_tables_to_sqlite(
    interim_dir: Path,
    master_df: pd.DataFrame,
    db_path: Path,
) -> None:
    """
    Initialise the SQLite database and load all tables.

    Steps:
      1. Apply schema from sql/schema.sql  (CREATE TABLE + indexes)
      2. Load all 8 individual cleaned CSVs from data/interim/
      3. Load master_race_table
      4. Apply views from sql/views.sql

    The operation is idempotent — safe to re-run. Tables are replaced
    (if_exists='replace') so re-runs reflect updated data.

    Args:
        interim_dir: data/interim/ containing *_clean.csv files.
        master_df:   The built master race table DataFrame.
        db_path:     Destination path for the .db file.
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    log.info("Connected to SQLite: %s", db_path)

    # Step 1: Apply schema DDL from sql/schema.sql
    log.info("Applying schema from %s ...", SCHEMA_SQL_FILE)
    schema_sql = _read_sql_file(SCHEMA_SQL_FILE)
    conn.executescript(schema_sql)
    conn.commit()
    log.info("  Schema applied.")

    # Step 2: Load individual cleaned tables
    log.info("Loading cleaned source tables...")
    for table_name, csv_name in INTERIM_TABLE_MAP.items():
        csv_path = interim_dir / csv_name
        if not csv_path.exists():
            log.warning("  Skipping %-20s — file not found: %s", table_name, csv_path)
            continue
        df = pd.read_csv(csv_path, low_memory=False)
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        log.info("  Loaded  %-20s  %d rows", table_name, len(df))

    # Step 3: Load master race table
    master_df.to_sql("master_race_table", conn, if_exists="replace", index=False)
    log.info("  Loaded  %-20s  %d rows", "master_race_table", len(master_df))

    # Step 4: Create analytical views from sql/views.sql
    log.info("Creating views from %s ...", VIEWS_SQL_FILE)
    views_sql = _read_sql_file(VIEWS_SQL_FILE)
    conn.executescript(views_sql)
    conn.commit()
    log.info("  Views created.")

    conn.close()
    log.info("SQLite database ready: %s", db_path)


def verify_database(db_path: Path) -> None:
    """
    Run a quick sanity check on the loaded database.

    Prints row counts for all tables and confirms views exist.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    tables_and_views = cursor.execute(
        "SELECT name, type FROM sqlite_master "
        "WHERE type IN ('table', 'view') ORDER BY type, name"
    ).fetchall()

    print("\n" + "=" * 55)
    print("DATABASE CONTENTS")
    print("=" * 55)
    print(f"  {'NAME':<35} {'TYPE':<8} {'ROWS':>8}")
    print("-" * 55)

    for name, obj_type in tables_and_views:
        if obj_type == "table":
            count = cursor.execute(f"SELECT COUNT(*) FROM [{name}]").fetchone()[0]
            print(f"  {name:<35} {obj_type:<8} {count:>8,}")
        else:
            print(f"  {name:<35} {obj_type:<8} {'—':>8}")

    print("=" * 55)
    conn.close()


# ===========================================================================
# Orchestrator
# ===========================================================================

def run_build_master_table(
    interim_dir: Path   = INTERIM_DIR,
    processed_dir: Path = PROCESSED_DIR,
    master_table_file: Path = MASTER_TABLE_FILE,
    db_file: Path       = DB_FILE,
) -> pd.DataFrame:
    """
    Full pipeline:
      1. Build master_race_table.csv from cleaned_merged_data.csv
      2. Save to data/processed/master_race_table.csv
      3. Load all tables + master table into SQLite
      4. Create analytical views from sql/views.sql
      5. Verify database contents

    Args:
        interim_dir:        data/interim/
        processed_dir:      data/processed/
        master_table_file:  Output path for master_race_table.csv
        db_file:            Output path for f1_database.db

    Returns:
        master_race_table as a DataFrame (also saved to CSV and SQLite).
    """
    processed_dir.mkdir(parents=True, exist_ok=True)

    # ----- Step 1: Build -----
    log.info("=" * 55)
    log.info("STEP 1  Building master race table")
    log.info("=" * 55)
    master_df = build_master_table(MERGED_FILE)

    # ----- Step 2: Save CSV -----
    master_df.to_csv(master_table_file, index=False)
    log.info("Saved -> %s  (%d rows)", master_table_file, len(master_df))

    # ----- Step 3-4: Load SQLite -----
    log.info("=" * 55)
    log.info("STEP 2  Loading tables into SQLite + creating views")
    log.info("=" * 55)
    load_tables_to_sqlite(interim_dir, master_df, db_file)

    # ----- Step 5: Verify -----
    log.info("=" * 55)
    log.info("STEP 3  Verifying database")
    log.info("=" * 55)
    verify_database(db_file)

    log.info("=" * 55)
    log.info("build_master_table.py complete.")
    log.info("  master_race_table.csv  -> %s", master_table_file)
    log.info("  f1_database.db         -> %s", db_file)
    log.info("  SQL schema             -> %s", SCHEMA_SQL_FILE)
    log.info("  SQL views              -> %s", VIEWS_SQL_FILE)
    log.info("  SQL queries            -> %s", SQL_DIR / "advanced_queries.sql")
    return master_df


def print_master_summary(df: pd.DataFrame) -> None:
    """Print a profiling summary of the master race table."""
    print("\n" + "=" * 55)
    print("MASTER RACE TABLE — SUMMARY")
    print("=" * 55)
    print(f"  Rows          : {len(df):,}")
    print(f"  Columns       : {len(df.columns)}")
    print(f"  Seasons       : {int(df['year'].min())} – {int(df['year'].max())}")
    print(f"  Races         : {df['raceId'].nunique():,}")
    print(f"  Drivers       : {df['driverId'].nunique():,}")
    print(f"  Constructors  : {df['constructorId'].nunique():,}")
    print(f"  Circuits      : {df['circuitId'].nunique():,}")
    print(f"  Podiums       : {int(df['is_podium'].sum()):,}")
    print(f"  Winners       : {int(df['is_winner'].sum()):,}")
    print(f"  DNFs          : {int(df['is_dnf'].sum()):,}")
    null_pct = df.isna().mean().mean() * 100
    print(f"  Overall null  : {null_pct:.1f}%")
    print("=" * 55)
    top_null = df.isna().mean().sort_values(ascending=False).head(8)
    print("Top 8 columns by null % (high = expected for historic data):")
    for col, pct in top_null.items():
        bar = "█" * int(pct * 20)
        print(f"  {col:<35} {pct*100:5.1f}%  {bar}")
    print("=" * 55)


# ===========================================================================
# Entry point
# ===========================================================================

if __name__ == "__main__":
    master = run_build_master_table(
        interim_dir       = INTERIM_DIR,
        processed_dir     = PROCESSED_DIR,
        master_table_file = MASTER_TABLE_FILE,
        db_file           = DB_FILE,
    )
    print_master_summary(master)