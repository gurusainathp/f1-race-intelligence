-- ============================================================
-- sql/create_tables.sql
-- F1 Race Intelligence System — Table Creation DDL
--
-- Purpose: Standalone CREATE TABLE statements for all core
--          F1 tables. Used when initialising a fresh database
--          or rebuilding individual tables.
--
-- Relationship to schema.sql:
--   schema.sql   = full schema including indexes and comments
--   create_tables.sql = clean DDL-only version for reference,
--                       documentation, and targeted rebuilds
--
-- Usage:
--   sqlite3 data/processed/f1_database.db < sql/create_tables.sql
-- ============================================================

PRAGMA foreign_keys = ON;

-- ------------------------------------------------------------
-- Dimension tables (no foreign key dependencies)
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS circuits (
    circuitId    INTEGER PRIMARY KEY,
    circuitRef   TEXT    NOT NULL,
    name         TEXT,
    location     TEXT,
    country      TEXT,
    lat          REAL,
    lng          REAL,
    alt          REAL
);

CREATE TABLE IF NOT EXISTS drivers (
    driverId     INTEGER PRIMARY KEY,
    driverRef    TEXT    NOT NULL UNIQUE,
    number       INTEGER,
    code         TEXT,
    forename     TEXT,
    surname      TEXT,
    full_name    TEXT,
    dob          TEXT,
    nationality  TEXT
);

CREATE TABLE IF NOT EXISTS constructors (
    constructorId  INTEGER PRIMARY KEY,
    constructorRef TEXT    NOT NULL UNIQUE,
    name           TEXT,
    nationality    TEXT
);

-- ------------------------------------------------------------
-- races — depends on circuits
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS races (
    raceId       INTEGER PRIMARY KEY,
    year         INTEGER NOT NULL,
    round        INTEGER NOT NULL,
    circuitId    INTEGER REFERENCES circuits(circuitId),
    name         TEXT,
    date         TEXT,
    fp1_date     TEXT,
    fp2_date     TEXT,
    fp3_date     TEXT,
    quali_date   TEXT,
    sprint_date  TEXT
);

-- ------------------------------------------------------------
-- Fact tables — depend on races, drivers, constructors
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS results (
    resultId          INTEGER PRIMARY KEY,
    raceId            INTEGER NOT NULL REFERENCES races(raceId),
    driverId          INTEGER NOT NULL REFERENCES drivers(driverId),
    constructorId     INTEGER NOT NULL REFERENCES constructors(constructorId),
    number            INTEGER,
    grid              INTEGER,
    position          INTEGER,
    positionText      TEXT,
    positionOrder     INTEGER,
    points            REAL,
    laps              INTEGER,
    milliseconds      REAL,
    statusId          INTEGER,
    fastestLap        INTEGER,
    rank              INTEGER,
    fastestLapTime_ms REAL,
    fastestLapSpeed   REAL,
    is_dnf            INTEGER DEFAULT 0,
    is_podium         INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS qualifying (
    qualifyId     INTEGER PRIMARY KEY,
    raceId        INTEGER NOT NULL REFERENCES races(raceId),
    driverId      INTEGER NOT NULL REFERENCES drivers(driverId),
    constructorId INTEGER REFERENCES constructors(constructorId),
    number        INTEGER,
    position      INTEGER,
    q1_ms         REAL,
    q2_ms         REAL,
    q3_ms         REAL,
    best_quali_ms REAL
);

CREATE TABLE IF NOT EXISTS pit_stops (
    raceId          INTEGER NOT NULL REFERENCES races(raceId),
    driverId        INTEGER NOT NULL REFERENCES drivers(driverId),
    stop            INTEGER NOT NULL,
    lap             INTEGER,
    pit_duration_ms REAL,
    PRIMARY KEY (raceId, driverId, stop)
);

CREATE TABLE IF NOT EXISTS lap_times (
    raceId       INTEGER NOT NULL REFERENCES races(raceId),
    driverId     INTEGER NOT NULL REFERENCES drivers(driverId),
    lap          INTEGER NOT NULL,
    position     INTEGER,
    lap_time_ms  REAL,
    PRIMARY KEY (raceId, driverId, lap)
);

-- ------------------------------------------------------------
-- master_race_table — denormalized analytical table
-- Produced by src/data/build_master_table.py
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS master_race_table (
    raceId                  INTEGER,
    year                    INTEGER,
    round                   INTEGER,
    season_round_pct        REAL,
    race_name               TEXT,
    date                    TEXT,
    circuitId               INTEGER,
    circuit_name            TEXT,
    circuitRef              TEXT,
    country                 TEXT,
    lat                     REAL,
    lng                     REAL,
    alt                     REAL,
    driverId                INTEGER,
    driverRef               TEXT,
    full_name               TEXT,
    driver_nationality      TEXT,
    dob                     TEXT,
    driver_age_at_race      REAL,
    constructorId           INTEGER,
    constructorRef          TEXT,
    constructor_name        TEXT,
    constructor_nationality TEXT,
    grid                    INTEGER,
    position                INTEGER,
    positionText            TEXT,
    positionOrder           INTEGER,
    points                  REAL,
    laps                    INTEGER,
    milliseconds            REAL,
    statusId                INTEGER,
    is_dnf                  INTEGER,
    is_podium               INTEGER,
    is_winner               INTEGER,
    is_points_finish        INTEGER,
    fastestLap              INTEGER,
    rank                    INTEGER,
    fastestLapTime_ms       REAL,
    fastestLapSpeed         REAL,
    grid_vs_finish_delta    REAL,
    quali_position          INTEGER,
    q1_ms                   REAL,
    q2_ms                   REAL,
    q3_ms                   REAL,
    best_quali_ms           REAL,
    pole_quali_ms           REAL,
    qualifying_gap_ms       REAL,
    qualifying_gap_pct      REAL,
    total_pit_stops         INTEGER,
    total_pit_time_ms       REAL,
    avg_pit_duration_ms     REAL,
    min_pit_duration_ms     REAL,
    laps_completed          INTEGER,
    avg_lap_time_ms         REAL,
    median_lap_time_ms      REAL,
    std_lap_time_ms         REAL,
    fastest_lap_ms          REAL,
    lap_time_consistency    REAL,
    constructor_season_key  TEXT
);