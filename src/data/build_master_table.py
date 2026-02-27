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
                                             - all 9 cleaned source tables
                                               (incl. status lookup)
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

from constants import (
    compute_is_dnf_series,
    compute_dnf_type_series,
    classify_dnf_type,
    is_dnf,
    is_finish,
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
# ---------------------------------------------------------------------------
SCHEMA_SQL_FILE = SQL_DIR / "schema.sql"
VIEWS_SQL_FILE  = SQL_DIR / "views.sql"


# ---------------------------------------------------------------------------
# Interim table map
# Maps SQLite table name -> cleaned CSV filename in data/interim/
# NOTE: status is intentionally included so SQL queries can join
# results.statusId -> status.statusId for label lookups.
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
    "status":       "status_clean.csv",     # ← was missing; needed for label joins
}


# ===========================================================================
# Step 1: Build master_race_table from cleaned_merged_data.csv
# ===========================================================================

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
    "points", "laps", "milliseconds", "statusId", "status",
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


def _recompute_status_flags(df: pd.DataFrame) -> pd.DataFrame:
    """
    Recompute is_dnf and dnf_type from the 'status' label column.

    This is the authoritative derivation — it uses the shared classifier
    from constants.py and is independent of whatever flag was set in
    clean_data.py. It also cross-validates against the pre-existing
    is_dnf column and logs any discrepancies so data quality issues
    in upstream cleaning are surfaced immediately.

    Columns written:
      is_dnf    (int8)  : 1 if driver did not finish, 0 otherwise
      dnf_type  (str)   : 'mechanical' | 'crash' | 'other' | None

    Requires 'status' column to be present in df. If absent, falls back
    to the existing is_dnf column and logs a warning.
    """
    if "status" not in df.columns:
        log.warning(
            "  'status' column not found in merged data. "
            "is_dnf will NOT be recomputed — using pre-existing flag as-is. "
            "Ensure merge_data.py joins the status table correctly."
        )
        if "dnf_type" not in df.columns:
            df["dnf_type"] = None
        return df

    log.info("  Recomputing is_dnf and dnf_type from status label...")

    # ── Recompute from status text ──────────────────────────────────────────
    is_dnf_recomputed = compute_is_dnf_series(df["status"])
    dnf_type_recomputed = compute_dnf_type_series(df["status"])

    # ── Cross-validate against pre-existing is_dnf flag ────────────────────
    if "is_dnf" in df.columns:
        existing = pd.to_numeric(df["is_dnf"], errors="coerce").fillna(-1).astype(int)
        recomputed = is_dnf_recomputed.astype(int)

        # Only compare rows where both values are 0 or 1 (skip -1 = was null)
        comparable = existing.isin([0, 1])
        mismatches = (existing[comparable] != recomputed[comparable]).sum()

        if mismatches > 0:
            log.warning(
                "  ⚠ is_dnf MISMATCH: %d rows differ between "
                "pre-existing flag (clean_data.py) and status-derived value. "
                "Status-derived value will be used — review clean_data.py if unexpected.",
                mismatches,
            )
            # Sample the mismatches for debugging
            mismatch_mask = comparable & (existing != recomputed)
            sample = df.loc[mismatch_mask, ["raceId", "driverId", "status"]].head(10)
            log.warning("  Sample mismatched rows:\n%s", sample.to_string(index=False))
        else:
            log.info("  ✓ is_dnf cross-validation passed — no discrepancies.")

    # ── Write authoritative values ──────────────────────────────────────────
    df["is_dnf"]   = is_dnf_recomputed
    df["dnf_type"] = dnf_type_recomputed

    # ── Status category summary ─────────────────────────────────────────────
    n_total    = len(df)
    n_finished = int((~is_dnf_recomputed.astype(bool)).sum())
    n_dnf      = int(is_dnf_recomputed.sum())

    # Count by dnf_type
    dnf_type_counts = dnf_type_recomputed.value_counts(dropna=True)

    log.info(
        "  Status summary: %d finished (%.1f%%), %d DNF (%.1f%%)",
        n_finished, n_finished / n_total * 100,
        n_dnf, n_dnf / n_total * 100,
    )
    for dtype, count in dnf_type_counts.items():
        log.info("    DNF type %-12s : %d (%.1f%% of DNFs)", dtype, count, count / n_dnf * 100)

    # Warn if the 'Other' unclassified bucket is unexpectedly large
    other_dnf = int(dnf_type_counts.get("other", 0))
    if n_dnf > 0 and other_dnf / n_dnf > 0.25:
        log.warning(
            "  ⚠ %.1f%% of DNFs classified as 'other' — "
            "consider extending MECHANICAL_KEYWORDS or CRASH_KEYWORDS in constants.py",
            other_dnf / n_dnf * 100,
        )

    return df


def build_master_table(merged_path: Path = MERGED_FILE) -> pd.DataFrame:
    """
    Load cleaned_merged_data.csv and produce the curated master race table.

    Adds derived columns:
      is_dnf                : recomputed from status label (authoritative)
      dnf_type              : 'mechanical' | 'crash' | 'other' | None
      grid_vs_finish_delta  : grid - position (positive = gained places)
      is_points_finish      : 1 if points > 0
      is_winner             : 1 if position == 1
      constructor_season_key: constructorRef_year (era-aware grouping key)

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
    # Status-derived flags (authoritative — replaces clean_data.py flags)
    # -----------------------------------------------------------------------
    df = _recompute_status_flags(df)

    # -----------------------------------------------------------------------
    # Remaining derived columns
    # -----------------------------------------------------------------------

    # grid_vs_finish_delta: positive = gained positions from grid to finish.
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
        "dnf_type", "grid_vs_finish_delta",
        "is_points_finish", "is_winner", "constructor_season_key",
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
      2. Load all 9 individual cleaned CSVs (incl. status lookup table)
      3. Load master_race_table
      4. Apply views from sql/views.sql

    The status table is a first-class lookup in the DB — SQL queries
    can now JOIN results.statusId -> status.statusId to get the label,
    or JOIN master_race_table.statusId -> status.statusId for the same.

    The operation is idempotent — safe to re-run (tables are replaced).
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    log.info("Connected to SQLite: %s", db_path)

    # Step 1: Schema DDL
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

    # Step 4: Analytical views
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
    Also verifies status table is present and joinable.
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

    loaded_tables = set()
    for name, obj_type in tables_and_views:
        if obj_type == "table":
            count = cursor.execute(f"SELECT COUNT(*) FROM [{name}]").fetchone()[0]
            print(f"  {name:<35} {obj_type:<8} {count:>8,}")
            loaded_tables.add(name)
        else:
            print(f"  {name:<35} {obj_type:<8} {'—':>8}")

    print("=" * 55)

    # Verify status table is present and FK join works
    if "status" in loaded_tables and "results" in loaded_tables:
        orphan_check = cursor.execute(
            "SELECT COUNT(*) FROM results r "
            "LEFT JOIN status s ON r.statusId = s.statusId "
            "WHERE s.statusId IS NULL"
        ).fetchone()[0]
        if orphan_check == 0:
            print("  ✓ status FK join: all results.statusId match status table")
        else:
            print(f"  ⚠ status FK join: {orphan_check} orphan statusId in results")

        # Show top DNF causes using the actual status table join
        print("\n  Top 5 DNF causes (from status join):")
        top_dnf = cursor.execute(
            "SELECT s.status, COUNT(*) as cnt "
            "FROM master_race_table m "
            "JOIN status s ON m.statusId = s.statusId "
            "WHERE m.is_dnf = 1 "
            "GROUP BY s.status ORDER BY cnt DESC LIMIT 5"
        ).fetchall()
        for label, cnt in top_dnf:
            print(f"    {label:<30} {cnt:>6,}")
    else:
        print("  ⚠ Could not verify status join — table(s) missing")

    print("=" * 55)
    conn.close()


# ===========================================================================
# Orchestrator
# ===========================================================================

def run_build_master_table(
    interim_dir: Path       = INTERIM_DIR,
    processed_dir: Path     = PROCESSED_DIR,
    master_table_file: Path = MASTER_TABLE_FILE,
    db_file: Path           = DB_FILE,
) -> pd.DataFrame:
    """
    Full pipeline:
      1. Build master_race_table from cleaned_merged_data.csv
         - Recomputes is_dnf and dnf_type from status label (authoritative)
         - Cross-validates against pre-existing is_dnf from clean_data.py
      2. Save to data/processed/master_race_table.csv
      3. Load all 9 cleaned tables (incl. status) into SQLite
      4. Load master_race_table into SQLite
      5. Create analytical views
      6. Verify database and status FK join
    """
    processed_dir.mkdir(parents=True, exist_ok=True)

    log.info("=" * 55)
    log.info("STEP 1  Building master race table")
    log.info("=" * 55)
    master_df = build_master_table(MERGED_FILE)

    master_df.to_csv(master_table_file, index=False)
    log.info("Saved -> %s  (%d rows)", master_table_file, len(master_df))

    log.info("=" * 55)
    log.info("STEP 2  Loading tables into SQLite + creating views")
    log.info("=" * 55)
    load_tables_to_sqlite(interim_dir, master_df, db_file)

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

    if "dnf_type" in df.columns:
        print("  DNF breakdown :")
        for dtype, count in df["dnf_type"].value_counts(dropna=True).items():
            print(f"    {dtype:<14} : {count:,}")

    if "status" in df.columns:
        unclassified = df.loc[
            df["is_dnf"].eq(0) & ~df["status"].apply(
                lambda s: is_finish(str(s)) if pd.notna(s) else False
            ),
            "status"
        ].value_counts().head(5)
        if not unclassified.empty:
            print("  Unclassified status (top 5, neither finish nor DNF):")
            for label, cnt in unclassified.items():
                print(f"    {label:<30} : {cnt:,}")

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