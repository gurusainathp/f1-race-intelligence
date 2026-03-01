"""
src/feature_engineering/build_features.py
------------------------------------------
Produces the final analysis-ready master race table and loads all
cleaned tables into a SQLite database for SQL-based analysis.
Also builds three feature-store parquet files for modelling:

  data/processed/driver_race_features.parquet       (2.1)
  data/processed/driver_season_features.parquet     (2.2)
  data/processed/constructor_season_features.parquet(2.3)

Reads:
  data/interim/cleaned_merged_data.csv    (from src/data_processing/04_merge_data.py)
  data/interim/*_clean.csv               (individual cleaned tables)
  sql/schema.sql                         (table DDL + indexes)
  sql/views.sql                          (analytical views)
  data/processed/f1_database.db          (for parquet building — built in Step 2)

Writes:
  data/processed/master_race_table.csv   — denormalized table, one row
                                           per driver per race
  data/processed/f1_database.db          — SQLite database containing:
                                             - all 9 cleaned source tables
                                               (incl. status lookup)
                                             - master_race_table
                                             - 4 analytical views
  data/processed/driver_race_features.parquet
  data/processed/driver_season_features.parquet
  data/processed/constructor_season_features.parquet

Pipeline position:
  src/data_processing/02_clean_data.py -> src/data_processing/04_merge_data.py -> [THIS FILE]

Run:
  python src/feature_engineering/build_features.py
"""

import logging
import sqlite3
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

# Add project root to sys.path for absolute imports from src
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from src.utils.constants import (
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

# Parquet output paths
DRIVER_RACE_PARQUET        = PROCESSED_DIR / "driver_race_features.parquet"
DRIVER_SEASON_PARQUET      = PROCESSED_DIR / "driver_season_features.parquet"
CONSTRUCTOR_SEASON_PARQUET = PROCESSED_DIR / "constructor_season_features.parquet"


# ---------------------------------------------------------------------------
# SQL file paths
# ---------------------------------------------------------------------------
SCHEMA_SQL_FILE = SQL_DIR / "schema.sql"
VIEWS_SQL_FILE  = SQL_DIR / "views.sql"


# ---------------------------------------------------------------------------
# Interim table map
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
    "status":       "status_clean.csv",
}


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
    "grid", "grid_pit_lane", "position", "positionText", "positionOrder",
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
    "pit_data_incomplete",
    # Lap times (aggregated)
    "laps_completed", "avg_lap_time_ms", "median_lap_time_ms",
    "std_lap_time_ms", "fastest_lap_ms", "lap_time_consistency",
]


# ===========================================================================
# Step 1: Build master_race_table
# ===========================================================================

def _recompute_status_flags(df: pd.DataFrame) -> pd.DataFrame:
    """
    Recompute is_dnf and dnf_type from the 'status' label column.
    """
    if "status" not in df.columns:
        log.warning(
            "  'status' column not found in merged data. "
            "is_dnf will NOT be recomputed — using pre-existing flag as-is."
        )
        if "dnf_type" not in df.columns:
            df["dnf_type"] = None
        return df

    log.info("  Recomputing is_dnf and dnf_type from status label...")

    is_dnf_recomputed   = compute_is_dnf_series(df["status"])
    dnf_type_recomputed = compute_dnf_type_series(df["status"])

    if "is_dnf" in df.columns:
        existing   = pd.to_numeric(df["is_dnf"], errors="coerce").fillna(-1).astype(int)
        recomputed = is_dnf_recomputed.astype(int)
        comparable = existing.isin([0, 1])
        mismatches = (existing[comparable] != recomputed[comparable]).sum()

        if mismatches > 0:
            log.warning(
                "  ⚠ is_dnf MISMATCH: %d rows differ between "
                "pre-existing flag and status-derived value. "
                "Status-derived value will be used.",
                mismatches,
            )
            mismatch_mask = comparable & (existing != recomputed)
            sample = df.loc[mismatch_mask, ["raceId", "driverId", "status"]].head(10)
            log.warning("  Sample mismatched rows:\n%s", sample.to_string(index=False))
        else:
            log.info("  ✓ is_dnf cross-validation passed — no discrepancies.")

    df["is_dnf"]   = is_dnf_recomputed
    df["dnf_type"] = dnf_type_recomputed

    n_total    = len(df)
    n_finished = int((~is_dnf_recomputed.astype(bool)).sum())
    n_dnf      = int(is_dnf_recomputed.sum())
    dnf_type_counts = dnf_type_recomputed.value_counts(dropna=True)

    log.info(
        "  Status summary: %d finished (%.1f%%), %d DNF (%.1f%%)",
        n_finished, n_finished / n_total * 100,
        n_dnf, n_dnf / n_total * 100,
    )
    for dtype, count in dnf_type_counts.items():
        log.info("    DNF type %-12s : %d (%.1f%% of DNFs)", dtype, count, count / n_dnf * 100)

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
    """
    if not merged_path.exists():
        raise FileNotFoundError(
            f"Merged file not found: {merged_path}\n"
            f"Run src/data/merge_data.py first."
        )

    log.info("Loading merged dataset: %s", merged_path)
    df = pd.read_csv(merged_path, low_memory=False)
    log.info("  Loaded: %d rows x %d columns", *df.shape)

    df = _recompute_status_flags(df)

    df["grid_vs_finish_delta"] = np.where(
        df["grid"].notna() & df["position"].notna(),
        pd.to_numeric(df["grid"], errors="coerce") -
        pd.to_numeric(df["position"], errors="coerce"),
        np.nan,
    )

    # OI-5: pit_data_incomplete flag (stop-level null rate)
    pit_incomplete_race_ids: set = set()
    pit_stops_path = INTERIM_DIR / "pit_stops_clean.csv"
    if pit_stops_path.exists():
        pit_raw = pd.read_csv(pit_stops_path, low_memory=False)
        if "pit_duration_ms" in pit_raw.columns and "raceId" in pit_raw.columns:
            pit_race_size = pit_raw.groupby("raceId")["pit_duration_ms"].size().rename("total_stops")
            pit_race_null = pit_raw.groupby("raceId")["pit_duration_ms"].apply(
                lambda s: int(s.isna().sum())
            ).rename("null_stops")
            pit_race_stats = pd.concat([pit_race_size, pit_race_null], axis=1)
            pit_race_stats["null_rate"] = (
                pit_race_stats["null_stops"] / pit_race_stats["total_stops"]
            )
            pit_incomplete_race_ids = set(
                pit_race_stats[pit_race_stats["null_rate"] > 0.30].index
            )
            log.info(
                "  pit_data_incomplete: %d races flagged >30%% null pit duration.",
                len(pit_incomplete_race_ids),
            )
    else:
        log.warning(
            "  pit_data_incomplete: pit_stops_clean.csv not found at %s. "
            "Flag will be 0 for all rows.", pit_stops_path,
        )

    df["pit_data_incomplete"] = df["raceId"].isin(pit_incomplete_race_ids).astype("int8")

    n_incomplete_rows  = int(df["pit_data_incomplete"].eq(1).sum())
    n_incomplete_races = int(df[df["pit_data_incomplete"] == 1]["raceId"].nunique())
    if n_incomplete_rows:
        log.info(
            "  pit_data_incomplete: flagged %d driver-race rows across %d races.",
            n_incomplete_rows, n_incomplete_races,
        )

    df["is_points_finish"] = (
        pd.to_numeric(df["points"], errors="coerce").fillna(0) > 0
    ).astype("int8")

    df["is_winner"] = (
        pd.to_numeric(df["position"], errors="coerce").eq(1)
    ).astype("int8")

    df["constructor_season_key"] = (
        df["constructorRef"].fillna("unknown").astype(str)
        + "_"
        + df["year"].astype(str)
    )

    extra_cols = [
        "dnf_type", "grid_vs_finish_delta",
        "is_points_finish", "is_winner", "constructor_season_key",
    ]
    final_cols = [c for c in MASTER_TABLE_COLS if c in df.columns] + extra_cols

    missing = [c for c in MASTER_TABLE_COLS if c not in df.columns]
    if missing:
        log.warning(
            "  %d expected columns absent from merged data: %s",
            len(missing), missing,
        )

    df = df[[c for c in final_cols if c in df.columns]].copy()

    for col in ["date", "dob"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%Y-%m-%d")

    int_cols = [
        "raceId", "year", "round", "circuitId", "driverId", "constructorId",
        "grid", "grid_pit_lane", "position", "positionOrder", "laps", "statusId",
        "fastestLap", "rank", "quali_position", "total_pit_stops", "laps_completed",
        "is_dnf", "is_podium", "is_winner", "is_points_finish",
        "pit_data_incomplete",
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
        raise FileNotFoundError(f"SQL file not found: {path}")
    return path.read_text(encoding="utf-8")


def load_tables_to_sqlite(
    interim_dir: Path,
    master_df: pd.DataFrame,
    db_path: Path,
) -> None:
    """
    Initialise the SQLite database and load all tables + views.
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    log.info("Connected to SQLite: %s", db_path)

    log.info("Applying schema from %s ...", SCHEMA_SQL_FILE)
    schema_sql = _read_sql_file(SCHEMA_SQL_FILE)
    conn.executescript(schema_sql)
    conn.commit()
    log.info("  Schema applied.")

    log.info("Loading cleaned source tables...")
    for table_name, csv_name in INTERIM_TABLE_MAP.items():
        csv_path = interim_dir / csv_name
        if not csv_path.exists():
            log.warning("  Skipping %-20s — file not found: %s", table_name, csv_path)
            continue
        df = pd.read_csv(csv_path, low_memory=False)
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        log.info("  Loaded  %-20s  %d rows", table_name, len(df))

    master_df.to_sql("master_race_table", conn, if_exists="replace", index=False)
    log.info("  Loaded  %-20s  %d rows", "master_race_table", len(master_df))

    log.info("Creating views from %s ...", VIEWS_SQL_FILE)
    views_sql = _read_sql_file(VIEWS_SQL_FILE)
    conn.executescript(views_sql)
    conn.commit()
    log.info("  Views created.")

    conn.close()
    log.info("SQLite database ready: %s", db_path)


def verify_database(db_path: Path) -> None:
    """
    Sanity-check the loaded database — row counts, views, status FK join.
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
# Step 3: Build parquet feature stores
# ===========================================================================

def _connect_db(db_path: Path) -> sqlite3.Connection:
    """Open a read-only-style connection to the SQLite database."""
    if not db_path.exists():
        raise FileNotFoundError(
            f"Database not found: {db_path}\n"
            f"Run the main pipeline first so f1_database.db is built."
        )
    return sqlite3.connect(db_path)


# ---------------------------------------------------------------------------
# 2.1  Driver–Race features
# ---------------------------------------------------------------------------

def build_driver_race_features(db_path: Path = DB_FILE) -> pd.DataFrame:
    """
    Build driver_race_features.parquet — one row per driver per race.

    Reads master_race_table from SQLite and pulls pit stop counts from
    the pit_stops table directly so the aggregation is always fresh.

    Columns produced
    ----------------
    Keys            : raceId, driverId
    Race context    : race_year, round, circuitId
    Identity        : constructorId
    Grid / result   : grid, finish_position, positions_gained
    Points / flags  : points, is_dnf, is_podium, is_winner, is_points_finish
    Performance     : fastest_lap_rank, qualifying_position, qualifying_gap_ms
                      best_quali_ms, avg_lap_time_ms, lap_time_consistency
    Pit stops       : pit_stop_count, total_pit_time_ms, avg_pit_duration_ms
                      pit_data_incomplete
    """
    log.info("Building driver_race_features ...")
    conn = _connect_db(db_path)

    # ── Core pull from master_race_table ────────────────────────────────────
    master_query = """
        SELECT
            m.raceId,
            m.driverId,
            m.constructorId,
            m.year          AS race_year,
            m.round,
            m.circuitId,

            -- Grid / result
            m.grid,
            m.position      AS finish_position,
            m.positionOrder AS finish_position_order,

            -- Points and status flags
            m.points,
            m.is_dnf,
            m.is_podium,
            m.is_winner,
            m.is_points_finish,
            m.statusId,

            -- Performance metrics
            m.rank                  AS fastest_lap_rank,
            m.quali_position        AS qualifying_position,
            m.qualifying_gap_ms,
            m.best_quali_ms,
            m.avg_lap_time_ms,
            m.lap_time_consistency,
            m.fastest_lap_ms,

            -- Pre-aggregated pit stop columns from master (fallback)
            m.total_pit_stops       AS pit_stop_count_master,
            m.total_pit_time_ms     AS total_pit_time_ms_master,
            m.avg_pit_duration_ms   AS avg_pit_duration_ms_master,
            m.pit_data_incomplete
        FROM master_race_table m
    """
    mdf = pd.read_sql_query(master_query, conn)
    log.info("  master_race_table pulled: %d rows", len(mdf))

    # ── Fresh pit stop aggregation from raw pit_stops table ─────────────────
    # Prefer this over master pre-aggregated values — it's always up-to-date
    # and lets us count stops precisely even when duration is null.
    pit_query = """
        SELECT
            raceId,
            driverId,
            COUNT(*)                    AS pit_stop_count,
            SUM(pit_duration_ms)        AS total_pit_time_ms,
            AVG(pit_duration_ms)        AS avg_pit_duration_ms
        FROM pit_stops
        GROUP BY raceId, driverId
    """
    try:
        pit_agg = pd.read_sql_query(pit_query, conn)
        log.info("  pit_stops aggregated: %d driver-race rows", len(pit_agg))
        pit_available = True
    except Exception as exc:
        log.warning("  pit_stops table unavailable (%s) — using master columns.", exc)
        pit_available = False

    conn.close()

    # ── Merge pit aggregates onto master ────────────────────────────────────
    if pit_available:
        df = mdf.merge(pit_agg, on=["raceId", "driverId"], how="left")
        # Fresh aggregation takes priority; fill gaps with master pre-agg
        df["pit_stop_count"]    = df["pit_stop_count"].fillna(df["pit_stop_count_master"])
        df["total_pit_time_ms"] = df["total_pit_time_ms"].fillna(df["total_pit_time_ms_master"])
        df["avg_pit_duration_ms"] = df["avg_pit_duration_ms"].fillna(df["avg_pit_duration_ms_master"])
    else:
        df = mdf.copy()
        df["pit_stop_count"]    = df["pit_stop_count_master"]
        df["total_pit_time_ms"] = df["total_pit_time_ms_master"]
        df["avg_pit_duration_ms"] = df["avg_pit_duration_ms_master"]

    # ── Derived: positions gained ────────────────────────────────────────────
    # Positive = moved forward; null grid or DNF → NaN
    df["positions_gained"] = np.where(
        df["grid"].notna() & df["finish_position"].notna() & (df["grid"] > 0),
        df["grid"] - df["finish_position"],
        np.nan,
    )

    # ── Final column selection and type tidy ────────────────────────────────
    keep = [
        "raceId", "driverId", "constructorId",
        "race_year", "round", "circuitId",
        "grid", "finish_position", "finish_position_order", "positions_gained",
        "points", "is_dnf", "is_podium", "is_winner", "is_points_finish",
        "fastest_lap_rank", "qualifying_position", "qualifying_gap_ms",
        "best_quali_ms", "avg_lap_time_ms", "lap_time_consistency", "fastest_lap_ms",
        "pit_stop_count", "total_pit_time_ms", "avg_pit_duration_ms",
        "pit_data_incomplete",
    ]
    df = df[[c for c in keep if c in df.columns]].copy()

    int_cols = [
        "raceId", "driverId", "constructorId",
        "race_year", "round", "circuitId",
        "grid", "finish_position", "finish_position_order",
        "is_dnf", "is_podium", "is_winner", "is_points_finish",
        "fastest_lap_rank", "qualifying_position", "pit_stop_count", "pit_data_incomplete",
    ]
    float_cols = [
        "points", "positions_gained", "qualifying_gap_ms", "best_quali_ms",
        "avg_lap_time_ms", "lap_time_consistency", "fastest_lap_ms",
        "total_pit_time_ms", "avg_pit_duration_ms",
    ]
    for col in int_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    for col in float_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    log.info("  driver_race_features: %d rows x %d cols", *df.shape)
    return df


# ---------------------------------------------------------------------------
# 2.2  Driver–Season aggregates
# ---------------------------------------------------------------------------

def build_driver_season_features(
    driver_race_df: pd.DataFrame | None = None,
    db_path: Path = DB_FILE,
) -> pd.DataFrame:
    """
    Build driver_season_features.parquet — one row per driver per season.

    All aggregates are derived exclusively from driver_race_features so the
    dependency chain is explicit and reproducible.

    Columns produced
    ----------------
    Keys         : driverId, race_year
    Volume       : races_entered, races_classified
    Results      : avg_finish_position, median_finish_position
                   best_finish, worst_finish, finish_std_dev
    Points       : total_points, points_per_race, points_per_classified_race
    Flags        : wins, podiums, points_finishes
                   win_rate, podium_rate, points_finish_rate, dnf_rate
    Pace         : avg_positions_gained, avg_qualifying_position
                   avg_qualifying_gap_ms, avg_lap_time_ms
    Consistency  : avg_lap_time_consistency
    Pit          : avg_pit_stop_count, avg_pit_duration_ms
    """
    log.info("Building driver_season_features ...")

    if driver_race_df is None:
        log.info("  driver_race_df not supplied — loading from DB.")
        driver_race_df = build_driver_race_features(db_path)

    df = driver_race_df.copy()
    g  = df.groupby(["driverId", "race_year"])

    # ── Volume ───────────────────────────────────────────────────────────────
    agg = g.agg(
        races_entered          = ("raceId",            "count"),
        races_classified       = ("finish_position",   "count"),  # non-null = classified
    ).reset_index()

    # ── Finish position stats (classified finishers only) ───────────────────
    fin = df[df["finish_position"].notna()].groupby(["driverId", "race_year"])
    agg = agg.merge(
        fin.agg(
            avg_finish_position    = ("finish_position", "mean"),
            median_finish_position = ("finish_position", "median"),
            best_finish            = ("finish_position", "min"),
            worst_finish           = ("finish_position", "max"),
            finish_std_dev         = ("finish_position", "std"),
        ).reset_index(),
        on=["driverId", "race_year"], how="left",
    )

    # ── Points ───────────────────────────────────────────────────────────────
    pts = g.agg(total_points=("points", "sum")).reset_index()
    agg = agg.merge(pts, on=["driverId", "race_year"], how="left")
    agg["points_per_race"]             = agg["total_points"] / agg["races_entered"]
    agg["points_per_classified_race"]  = np.where(
        agg["races_classified"] > 0,
        agg["total_points"] / agg["races_classified"],
        np.nan,
    )

    # ── Wins / podiums / points finishes / DNFs ──────────────────────────────
    flag_agg = g.agg(
        wins           = ("is_winner",        "sum"),
        podiums        = ("is_podium",         "sum"),
        points_finishes= ("is_points_finish",  "sum"),
        dnfs           = ("is_dnf",            "sum"),
    ).reset_index()
    agg = agg.merge(flag_agg, on=["driverId", "race_year"], how="left")

    agg["win_rate"]           = agg["wins"]            / agg["races_entered"]
    agg["podium_rate"]        = agg["podiums"]          / agg["races_entered"]
    agg["points_finish_rate"] = agg["points_finishes"]  / agg["races_entered"]
    agg["dnf_rate"]           = agg["dnfs"]             / agg["races_entered"]

    # ── Qualifying / pace ────────────────────────────────────────────────────
    pace_agg = g.agg(
        avg_positions_gained   = ("positions_gained",    "mean"),
        avg_qualifying_position= ("qualifying_position", "mean"),
        avg_qualifying_gap_ms  = ("qualifying_gap_ms",   "mean"),
        avg_lap_time_ms        = ("avg_lap_time_ms",     "mean"),
        avg_lap_time_consistency=("lap_time_consistency","mean"),
    ).reset_index()
    agg = agg.merge(pace_agg, on=["driverId", "race_year"], how="left")

    # ── Pit stops (exclude incomplete-data races) ────────────────────────────
    pit_df = df[df["pit_data_incomplete"] != 1]
    if len(pit_df) > 0:
        pit_agg_season = pit_df.groupby(["driverId", "race_year"]).agg(
            avg_pit_stop_count  = ("pit_stop_count",    "mean"),
            avg_pit_duration_ms = ("avg_pit_duration_ms","mean"),
        ).reset_index()
        agg = agg.merge(pit_agg_season, on=["driverId", "race_year"], how="left")
    else:
        agg["avg_pit_stop_count"]   = np.nan
        agg["avg_pit_duration_ms"]  = np.nan

    log.info("  driver_season_features: %d rows x %d cols", *agg.shape)
    return agg


# ---------------------------------------------------------------------------
# 2.3  Constructor–Season aggregates
# ---------------------------------------------------------------------------

def build_constructor_season_features(
    driver_race_df: pd.DataFrame | None = None,
    db_path: Path = DB_FILE,
) -> pd.DataFrame:
    """
    Build constructor_season_features.parquet — one row per constructor per season.

    Includes driver performance spread metrics: the gap between the team's
    two drivers across avg finish position, points, and DNF rate, giving a
    signal for intra-team competitiveness vs. car dominance.

    Columns produced
    ----------------
    Keys           : constructorId, race_year
    Volume         : races_entered, driver_count (distinct drivers used)
    Results        : avg_finish_position, best_finish, finish_std_dev
    Points         : total_points, points_per_race, avg_driver_points
    Flags          : total_wins, total_podiums, total_dnfs
                     win_rate, podium_rate, dnf_rate
    Pit            : avg_pit_stop_count, avg_pit_duration_ms (clean races only)
    Driver spread  : driver_spread_avg_finish   (max − min avg finish pos)
                     driver_spread_total_points (max − min total points)
                     driver_spread_dnf_rate     (max − min DNF rate)
                     top_driver_driverId        (driver with most points this season)
    """
    log.info("Building constructor_season_features ...")

    if driver_race_df is None:
        log.info("  driver_race_df not supplied — loading from DB.")
        driver_race_df = build_driver_race_features(db_path)

    df  = driver_race_df.copy()
    g   = df.groupby(["constructorId", "race_year"])

    # ── Volume ───────────────────────────────────────────────────────────────
    agg = g.agg(
        races_entered  = ("raceId",    "count"),
        driver_count   = ("driverId",  "nunique"),
    ).reset_index()

    # ── Finish position ───────────────────────────────────────────────────────
    fin = df[df["finish_position"].notna()].groupby(["constructorId", "race_year"])
    agg = agg.merge(
        fin.agg(
            avg_finish_position = ("finish_position", "mean"),
            best_finish         = ("finish_position", "min"),
            finish_std_dev      = ("finish_position", "std"),
        ).reset_index(),
        on=["constructorId", "race_year"], how="left",
    )

    # ── Points ────────────────────────────────────────────────────────────────
    pts = g.agg(total_points=("points", "sum")).reset_index()
    agg = agg.merge(pts, on=["constructorId", "race_year"], how="left")
    agg["points_per_race"]   = agg["total_points"] / agg["races_entered"]
    agg["avg_driver_points"] = agg["total_points"] / agg["driver_count"]

    # ── Wins / podiums / DNFs ─────────────────────────────────────────────────
    flag_agg = g.agg(
        total_wins   = ("is_winner", "sum"),
        total_podiums= ("is_podium", "sum"),
        total_dnfs   = ("is_dnf",   "sum"),
    ).reset_index()
    agg = agg.merge(flag_agg, on=["constructorId", "race_year"], how="left")
    agg["win_rate"]    = agg["total_wins"]    / agg["races_entered"]
    agg["podium_rate"] = agg["total_podiums"] / agg["races_entered"]
    agg["dnf_rate"]    = agg["total_dnfs"]    / agg["races_entered"]

    # ── Pit stops (clean races only) ──────────────────────────────────────────
    pit_df = df[df["pit_data_incomplete"] != 1]
    if len(pit_df) > 0:
        pit_agg = pit_df.groupby(["constructorId", "race_year"]).agg(
            avg_pit_stop_count  = ("pit_stop_count",     "mean"),
            avg_pit_duration_ms = ("avg_pit_duration_ms","mean"),
        ).reset_index()
        agg = agg.merge(pit_agg, on=["constructorId", "race_year"], how="left")
    else:
        agg["avg_pit_stop_count"]   = np.nan
        agg["avg_pit_duration_ms"]  = np.nan

    # ── Driver performance spread ─────────────────────────────────────────────
    # Compute per-driver per-season summaries, then diff within each constructor
    driver_season = (
        df.groupby(["constructorId", "race_year", "driverId"])
        .agg(
            drv_avg_finish = ("finish_position", "mean"),
            drv_points     = ("points",          "sum"),
            drv_dnf_rate   = ("is_dnf",          "mean"),
        )
        .reset_index()
    )

    def _spread(series: pd.Series) -> float:
        """max − min across drivers; NaN if fewer than 2 drivers have valid data."""
        valid = series.dropna()
        return float(valid.max() - valid.min()) if len(valid) >= 2 else np.nan

    def _top_driver(sub: pd.DataFrame) -> float:
        """driverId of the driver with the most points this season."""
        if sub.empty:
            return np.nan
        return float(sub.loc[sub["drv_points"].idxmax(), "driverId"])

    spread = (
        driver_season
        .groupby(["constructorId", "race_year"])
        .apply(
            lambda s: pd.Series({
                "driver_spread_avg_finish"   : _spread(s["drv_avg_finish"]),
                "driver_spread_total_points" : _spread(s["drv_points"]),
                "driver_spread_dnf_rate"     : _spread(s["drv_dnf_rate"]),
                "top_driver_driverId"        : _top_driver(s),
            })
        )
        .reset_index()
    )
    agg = agg.merge(spread, on=["constructorId", "race_year"], how="left")

    log.info("  constructor_season_features: %d rows x %d cols", *agg.shape)
    return agg


# ---------------------------------------------------------------------------
# Parquet save helper
# ---------------------------------------------------------------------------

def _save_parquet(df: pd.DataFrame, path: Path, label: str) -> None:
    """Save DataFrame to parquet with basic validation logging."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False, engine="pyarrow")
    size_kb = path.stat().st_size / 1024
    log.info(
        "  Saved %-45s  %d rows  %d cols  %.1f KB",
        str(path), len(df), len(df.columns), size_kb,
    )


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
      2. Save to data/processed/master_race_table.csv
      3. Load all 9 cleaned tables (incl. status) into SQLite
      4. Load master_race_table into SQLite
      5. Create analytical views
      6. Verify database and status FK join
      7. Build and save the three parquet feature stores
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
    log.info("STEP 4  Building parquet feature stores")
    log.info("=" * 55)

    # 2.1 — Driver–Race (built from DB; shared into season builds)
    driver_race_df = build_driver_race_features(db_file)
    _save_parquet(driver_race_df, DRIVER_RACE_PARQUET, "driver_race_features")

    # 2.2 — Driver–Season (derived from driver_race_df — no extra DB read)
    driver_season_df = build_driver_season_features(driver_race_df, db_file)
    _save_parquet(driver_season_df, DRIVER_SEASON_PARQUET, "driver_season_features")

    # 2.3 — Constructor–Season (derived from driver_race_df — no extra DB read)
    constructor_season_df = build_constructor_season_features(driver_race_df, db_file)
    _save_parquet(constructor_season_df, CONSTRUCTOR_SEASON_PARQUET, "constructor_season_features")

    log.info("=" * 55)
    log.info("build_features.py complete.")
    log.info("  master_race_table.csv          -> %s", master_table_file)
    log.info("  f1_database.db                 -> %s", db_file)
    log.info("  driver_race_features.parquet   -> %s", DRIVER_RACE_PARQUET)
    log.info("  driver_season_features.parquet -> %s", DRIVER_SEASON_PARQUET)
    log.info("  constructor_season.parquet     -> %s", CONSTRUCTOR_SEASON_PARQUET)
    log.info("  SQL schema                     -> %s", SCHEMA_SQL_FILE)
    log.info("  SQL views                      -> %s", VIEWS_SQL_FILE)
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