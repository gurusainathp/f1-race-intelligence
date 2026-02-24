-- ============================================================
-- sql/views.sql
-- F1 Race Intelligence System — Analytical Views
--
-- Purpose: Reusable views that pre-compute common aggregations
--          used across analytical queries, notebooks, and the
--          Streamlit dashboard.
--
-- Views defined:
--   v_driver_career_stats       — lifetime stats per driver
--   v_constructor_season_stats  — season-level team performance
--   v_race_podium_summary       — podium finishers per race
--   v_qualifying_vs_race        — qualifying position vs race result
--
-- Usage:
--   sqlite3 data/processed/f1_database.db < sql/views.sql
--   Then query: SELECT * FROM v_driver_career_stats LIMIT 10;
--
-- Note: Run after schema.sql and after data has been loaded.
-- ============================================================

-- ------------------------------------------------------------
-- v_driver_career_stats
--
-- One row per driver. Aggregates their full career across all
-- seasons in the dataset.
--
-- Useful for: driver profile pages, career comparison,
--             all-time leaderboards.
-- ------------------------------------------------------------
DROP VIEW IF EXISTS v_driver_career_stats;

CREATE VIEW v_driver_career_stats AS
SELECT
    m.driverId,
    m.driverRef,
    m.full_name,
    m.driver_nationality,
    MIN(m.year)                                             AS first_season,
    MAX(m.year)                                             AS last_season,
    COUNT(DISTINCT m.year)                                  AS seasons_active,
    COUNT(*)                                                AS total_starts,
    SUM(m.is_winner)                                        AS total_wins,
    SUM(m.is_podium)                                        AS total_podiums,
    SUM(m.is_points_finish)                                 AS total_points_finishes,
    SUM(m.is_dnf)                                           AS total_dnfs,
    ROUND(SUM(m.points), 1)                                 AS total_points,
    ROUND(AVG(m.points), 3)                                 AS avg_points_per_race,
    ROUND(
        100.0 * SUM(m.is_winner) / COUNT(*), 2
    )                                                       AS win_rate_pct,
    ROUND(
        100.0 * SUM(m.is_podium) / COUNT(*), 2
    )                                                       AS podium_rate_pct,
    ROUND(
        100.0 * SUM(m.is_dnf) / COUNT(*), 2
    )                                                       AS dnf_rate_pct,
    ROUND(
        100.0 * SUM(m.is_points_finish) / COUNT(*), 2
    )                                                       AS points_finish_rate_pct,
    COUNT(DISTINCT m.constructorId)                         AS constructors_raced_for,
    ROUND(AVG(m.grid_vs_finish_delta), 2)                  AS avg_positions_gained,
    ROUND(AVG(m.qualifying_gap_pct), 4)                    AS avg_quali_gap_to_pole_pct
FROM master_race_table m
GROUP BY m.driverId;


-- ------------------------------------------------------------
-- v_constructor_season_stats
--
-- One row per constructor per season. Aggregates team
-- performance across both cars for that year.
--
-- Useful for: constructor profiles, era analysis,
--             competitive parity tracking.
-- ------------------------------------------------------------
DROP VIEW IF EXISTS v_constructor_season_stats;

CREATE VIEW v_constructor_season_stats AS
SELECT
    m.constructorId,
    m.constructorRef,
    m.constructor_name,
    m.constructor_nationality,
    m.year,
    COUNT(DISTINCT m.driverId)                              AS drivers_used,
    COUNT(DISTINCT m.raceId)                                AS races_entered,
    COUNT(*)                                                AS driver_race_entries,
    SUM(m.is_winner)                                        AS wins,
    SUM(m.is_podium)                                        AS podiums,
    SUM(m.is_points_finish)                                 AS points_finishes,
    SUM(m.is_dnf)                                           AS dnfs,
    ROUND(SUM(m.points), 1)                                 AS total_points,
    ROUND(AVG(m.points), 3)                                 AS avg_points_per_entry,
    ROUND(
        100.0 * SUM(m.is_winner) / COUNT(*), 2
    )                                                       AS win_rate_pct,
    ROUND(
        100.0 * SUM(m.is_dnf) / COUNT(*), 2
    )                                                       AS dnf_rate_pct,
    ROUND(AVG(m.avg_pit_duration_ms), 1)                   AS avg_pit_duration_ms,
    ROUND(AVG(m.lap_time_consistency), 4)                  AS avg_lap_consistency
FROM master_race_table m
GROUP BY m.constructorId, m.year;


-- ------------------------------------------------------------
-- v_race_podium_summary
--
-- One row per race, showing P1/P2/P3 finishers side by side.
-- Uses conditional aggregation rather than pivoting, so it
-- stays compatible with SQLite.
--
-- Useful for: race result pages, historic podium lookup,
--             podium heatmaps by circuit.
-- ------------------------------------------------------------
DROP VIEW IF EXISTS v_race_podium_summary;

CREATE VIEW v_race_podium_summary AS
SELECT
    m.raceId,
    m.year,
    m.round,
    m.race_name,
    m.date,
    m.circuit_name,
    m.country,
    -- P1
    MAX(CASE WHEN m.position = 1 THEN m.full_name       END) AS p1_driver,
    MAX(CASE WHEN m.position = 1 THEN m.constructor_name END) AS p1_constructor,
    MAX(CASE WHEN m.position = 1 THEN m.points           END) AS p1_points,
    MAX(CASE WHEN m.position = 1 THEN m.fastest_lap_ms   END) AS p1_fastest_lap_ms,
    -- P2
    MAX(CASE WHEN m.position = 2 THEN m.full_name       END) AS p2_driver,
    MAX(CASE WHEN m.position = 2 THEN m.constructor_name END) AS p2_constructor,
    -- P3
    MAX(CASE WHEN m.position = 3 THEN m.full_name       END) AS p3_driver,
    MAX(CASE WHEN m.position = 3 THEN m.constructor_name END) AS p3_constructor,
    -- Pole sitter (qualifying P1)
    MAX(CASE WHEN m.quali_position = 1 THEN m.full_name END)  AS pole_sitter,
    MAX(m.pole_quali_ms)                                       AS pole_time_ms,
    -- Race stats
    COUNT(DISTINCT m.driverId)                                 AS classified_drivers,
    SUM(m.is_dnf)                                             AS total_dnfs
FROM master_race_table m
GROUP BY m.raceId;


-- ------------------------------------------------------------
-- v_qualifying_vs_race
--
-- One row per driver per race. Shows the relationship between
-- qualifying position and race outcome for regression and
-- correlation analysis.
--
-- Useful for: feature validation, EDA notebooks,
--             qualifying-to-race conversion analysis.
-- ------------------------------------------------------------
DROP VIEW IF EXISTS v_qualifying_vs_race;

CREATE VIEW v_qualifying_vs_race AS
SELECT
    m.raceId,
    m.year,
    m.round,
    m.race_name,
    m.circuit_name,
    m.country,
    m.driverId,
    m.full_name,
    m.constructor_name,
    m.quali_position,
    m.best_quali_ms,
    m.qualifying_gap_ms,
    m.qualifying_gap_pct,
    m.grid,
    m.position                                              AS race_position,
    m.positionText,
    m.is_dnf,
    m.is_podium,
    m.is_winner,
    m.points,
    m.grid_vs_finish_delta,
    -- Classifies the qualifying-to-race outcome directionally
    CASE
        WHEN m.position IS NULL            THEN 'DNF'
        WHEN m.grid IS NULL                THEN 'No grid data'
        WHEN m.position < m.grid           THEN 'Gained positions'
        WHEN m.position = m.grid           THEN 'Held position'
        WHEN m.position > m.grid           THEN 'Lost positions'
        ELSE 'Unknown'
    END                                                     AS race_direction
FROM master_race_table m
WHERE m.quali_position IS NOT NULL;