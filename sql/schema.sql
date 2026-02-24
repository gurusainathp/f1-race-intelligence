-- ============================================================
-- sql/schema.sql
-- F1 Race Intelligence System — Full Relational Schema
-- Source: Kaggle F1 World Championship Dataset (1950-2020)
--
-- Purpose: Defines the complete relational structure for the
--          F1 SQLite database. All tables with typed columns,
--          primary keys, and foreign key annotations.
--
-- Usage:
--   sqlite3 data/processed/f1_database.db < sql/schema.sql
--   OR executed programmatically by build_master_table.py
--
-- Note: SQLite does not enforce FK constraints by default.
--       Use PRAGMA foreign_keys = ON to enable enforcement.
-- ============================================================

PRAGMA foreign_keys = ON;

-- ------------------------------------------------------------
-- circuits
-- Core dimension table for race venues.
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS circuits (
    circuitId    INTEGER PRIMARY KEY,
    circuitRef   TEXT    NOT NULL,
    name         TEXT,
    location     TEXT,
    country      TEXT,
    lat          REAL,
    lng          REAL,
    alt          REAL        -- altitude in metres (NULL for many historic circuits)
);

-- ------------------------------------------------------------
-- drivers
-- One row per driver across all seasons.
-- number and code are NULL for pre-2014 era (no permanent numbers).
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS drivers (
    driverId     INTEGER PRIMARY KEY,
    driverRef    TEXT    NOT NULL UNIQUE,
    number       INTEGER,            -- permanent number (post-2014 only)
    code         TEXT,               -- 3-letter abbreviation
    forename     TEXT,
    surname      TEXT,
    full_name    TEXT,               -- derived: forename || ' ' || surname
    dob          TEXT,               -- YYYY-MM-DD
    nationality  TEXT
);

-- ------------------------------------------------------------
-- constructors
-- One row per constructor (team) across all seasons.
-- Note: same constructor may appear under different IDs if they
--       changed name (e.g. Tyrrell -> BAR -> Honda -> Brawn -> Mercedes).
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS constructors (
    constructorId  INTEGER PRIMARY KEY,
    constructorRef TEXT    NOT NULL UNIQUE,
    name           TEXT,
    nationality    TEXT
);

-- ------------------------------------------------------------
-- races
-- One row per race event.
-- Session date columns are NULL for pre-modern eras.
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS races (
    raceId       INTEGER PRIMARY KEY,
    year         INTEGER NOT NULL,
    round        INTEGER NOT NULL,
    circuitId    INTEGER REFERENCES circuits(circuitId),
    name         TEXT,
    date         TEXT,              -- YYYY-MM-DD race day
    fp1_date     TEXT,
    fp2_date     TEXT,
    fp3_date     TEXT,
    quali_date   TEXT,
    sprint_date  TEXT
);

-- ------------------------------------------------------------
-- results
-- Core fact table. One row per driver per race.
-- position is NULL for DNF/DSQ/retired (use positionText for status).
-- is_dnf and is_podium are derived binary flags added during cleaning.
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS results (
    resultId          INTEGER PRIMARY KEY,
    raceId            INTEGER NOT NULL REFERENCES races(raceId),
    driverId          INTEGER NOT NULL REFERENCES drivers(driverId),
    constructorId     INTEGER NOT NULL REFERENCES constructors(constructorId),
    number            INTEGER,
    grid              INTEGER,       -- NULL = pit-lane start (recoded from 0)
    position          INTEGER,       -- NULL = did not finish
    positionText      TEXT,          -- R=retired, D=DSQ, E=excluded, W=withdrew
    positionOrder     INTEGER,       -- always populated (used for sorting)
    points            REAL,
    laps              INTEGER,
    milliseconds      REAL,          -- total race time in ms (NULL for DNFs)
    statusId          INTEGER,
    fastestLap        INTEGER,       -- lap number of driver's fastest lap
    rank              INTEGER,       -- fastest lap ranking within race
    fastestLapTime_ms REAL,          -- fastest lap converted to milliseconds
    fastestLapSpeed   REAL,          -- fastest lap average speed (kph)
    is_dnf            INTEGER DEFAULT 0,    -- 1 = did not finish
    is_podium         INTEGER DEFAULT 0     -- 1 = finished P1, P2, or P3
);

-- ------------------------------------------------------------
-- qualifying
-- One row per driver per race (best available session time).
-- Q2/Q3 times are NULL for eliminated drivers (expected).
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS qualifying (
    qualifyId     INTEGER PRIMARY KEY,
    raceId        INTEGER NOT NULL REFERENCES races(raceId),
    driverId      INTEGER NOT NULL REFERENCES drivers(driverId),
    constructorId INTEGER REFERENCES constructors(constructorId),
    number        INTEGER,
    position      INTEGER,
    q1_ms         REAL,           -- Q1 lap time in milliseconds
    q2_ms         REAL,           -- Q2 lap time in milliseconds (NULL if eliminated)
    q3_ms         REAL,           -- Q3 lap time in milliseconds (NULL if eliminated)
    best_quali_ms REAL            -- minimum of q1/q2/q3 (derived during cleaning)
);

-- ------------------------------------------------------------
-- pit_stops
-- One row per individual stop. Multiple rows per driver per race.
-- Only available from 2012 season onwards.
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS pit_stops (
    raceId          INTEGER NOT NULL REFERENCES races(raceId),
    driverId        INTEGER NOT NULL REFERENCES drivers(driverId),
    stop            INTEGER NOT NULL,   -- stop number (1, 2, 3...)
    lap             INTEGER,
    pit_duration_ms REAL,               -- stop duration in milliseconds
    PRIMARY KEY (raceId, driverId, stop)
);

-- ------------------------------------------------------------
-- lap_times
-- One row per lap per driver per race (~500K rows total).
-- Safety car / VSC laps are retained (legitimately slow).
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS lap_times (
    raceId       INTEGER NOT NULL REFERENCES races(raceId),
    driverId     INTEGER NOT NULL REFERENCES drivers(driverId),
    lap          INTEGER NOT NULL,
    position     INTEGER,            -- track position at end of this lap
    lap_time_ms  REAL,               -- lap duration in milliseconds
    PRIMARY KEY (raceId, driverId, lap)
);

-- ------------------------------------------------------------
-- master_race_table
-- Denormalized analytical table. One row per driver per race.
-- Produced by src/data/build_master_table.py.
-- Used as the primary source for feature engineering and modelling.
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS master_race_table (
    -- Race context
    raceId                  INTEGER,
    year                    INTEGER,
    round                   INTEGER,
    season_round_pct        REAL,       -- round / total rounds in season
    race_name               TEXT,
    date                    TEXT,       -- YYYY-MM-DD
    -- Circuit
    circuitId               INTEGER,
    circuit_name            TEXT,
    circuitRef              TEXT,
    country                 TEXT,
    lat                     REAL,
    lng                     REAL,
    alt                     REAL,
    -- Driver
    driverId                INTEGER,
    driverRef               TEXT,
    full_name               TEXT,
    driver_nationality      TEXT,
    dob                     TEXT,
    driver_age_at_race      REAL,
    -- Constructor
    constructorId           INTEGER,
    constructorRef          TEXT,
    constructor_name        TEXT,
    constructor_nationality TEXT,
    -- Race result
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
    grid_vs_finish_delta    REAL,       -- grid - position (positive = gained places)
    -- Qualifying
    quali_position          INTEGER,
    q1_ms                   REAL,
    q2_ms                   REAL,
    q3_ms                   REAL,
    best_quali_ms           REAL,
    pole_quali_ms           REAL,       -- fastest qualifier in same race
    qualifying_gap_ms       REAL,       -- best_quali_ms - pole_quali_ms
    qualifying_gap_pct      REAL,       -- qualifying_gap_ms / pole_quali_ms * 100
    -- Pit stops (aggregated per driver per race)
    total_pit_stops         INTEGER,
    total_pit_time_ms       REAL,
    avg_pit_duration_ms     REAL,
    min_pit_duration_ms     REAL,
    -- Lap times (aggregated per driver per race)
    laps_completed          INTEGER,
    avg_lap_time_ms         REAL,
    median_lap_time_ms      REAL,
    std_lap_time_ms         REAL,
    fastest_lap_ms          REAL,
    lap_time_consistency    REAL,       -- 1 - (std/mean), bounded [0,1]
    -- Derived keys
    constructor_season_key  TEXT        -- constructorRef_year
);

-- ============================================================
-- Indexes
-- Covers the most common filter and join patterns used in
-- analytical queries and feature engineering.
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_results_race        ON results(raceId);
CREATE INDEX IF NOT EXISTS idx_results_driver      ON results(driverId);
CREATE INDEX IF NOT EXISTS idx_results_constructor ON results(constructorId);
CREATE INDEX IF NOT EXISTS idx_qualifying_race     ON qualifying(raceId);
CREATE INDEX IF NOT EXISTS idx_pit_stops_race      ON pit_stops(raceId, driverId);
CREATE INDEX IF NOT EXISTS idx_lap_times_race      ON lap_times(raceId, driverId);
CREATE INDEX IF NOT EXISTS idx_master_year         ON master_race_table(year);
CREATE INDEX IF NOT EXISTS idx_master_driver       ON master_race_table(driverId);
CREATE INDEX IF NOT EXISTS idx_master_constructor  ON master_race_table(constructorId);
CREATE INDEX IF NOT EXISTS idx_master_circuit      ON master_race_table(circuitId);
CREATE INDEX IF NOT EXISTS idx_master_race         ON master_race_table(raceId);