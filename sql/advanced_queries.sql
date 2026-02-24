-- ============================================================
-- sql/advanced_queries.sql
-- F1 Race Intelligence System — Advanced Analytical Queries
--
-- Purpose: 10 production-quality analytical queries demonstrating
--          SQL fluency. Each query addresses a distinct business
--          question using CTEs, window functions, and aggregation.
--
-- Database: data/processed/f1_database.db
-- Primary table: master_race_table
-- Supporting views: v_driver_career_stats, v_constructor_season_stats,
--                   v_race_podium_summary, v_qualifying_vs_race
--
-- Usage:
--   sqlite3 data/processed/f1_database.db < sql/advanced_queries.sql
--   Or run individual queries via DB Browser for SQLite / DBeaver.
-- ============================================================


-- ============================================================
-- Query 1: All-time driver leaderboard
-- Ranks drivers by total wins. Uses RANK() OVER PARTITION BY
-- nationality to also show each driver's standing within their
-- home country. Filtered to drivers with 50+ starts to exclude
-- single-race appearances.
-- ============================================================
SELECT
    d.full_name,
    d.nationality,
    COUNT(*)                                            AS total_starts,
    SUM(r.is_winner)                                    AS total_wins,
    SUM(r.is_podium)                                    AS total_podiums,
    SUM(r.is_dnf)                                       AS total_dnfs,
    ROUND(SUM(r.points), 1)                             AS total_points,
    ROUND(100.0 * SUM(r.is_winner)  / COUNT(*), 2)     AS win_rate_pct,
    ROUND(100.0 * SUM(r.is_podium) / COUNT(*), 2)      AS podium_rate_pct,
    ROUND(100.0 * SUM(r.is_dnf)   / COUNT(*), 2)       AS dnf_rate_pct,
    ROUND(AVG(r.points), 3)                             AS avg_points_per_race,
    RANK() OVER (
        PARTITION BY d.nationality
        ORDER BY SUM(r.is_winner) DESC
    )                                                   AS rank_within_nationality
FROM master_race_table r
JOIN drivers d ON r.driverId = d.driverId
GROUP BY r.driverId
HAVING total_starts >= 50
ORDER BY total_wins DESC;


-- ============================================================
-- Query 2: Constructor dominance by decade
-- Groups team performance into 10-year eras. RANK() OVER
-- PARTITION BY decade shows the hierarchy within each era.
-- ============================================================
SELECT
    (r.year / 10) * 10                                  AS decade,
    r.constructor_name,
    COUNT(DISTINCT r.raceId)                            AS races_entered,
    SUM(r.is_winner)                                    AS wins,
    SUM(r.is_podium)                                    AS podiums,
    ROUND(SUM(r.points), 1)                             AS total_points,
    ROUND(AVG(r.points), 3)                             AS avg_points_per_race,
    RANK() OVER (
        PARTITION BY (r.year / 10) * 10
        ORDER BY SUM(r.is_winner) DESC
    )                                                   AS win_rank_in_decade
FROM master_race_table r
GROUP BY decade, r.constructorId
ORDER BY decade, total_points DESC;


-- ============================================================
-- Query 3: Grid position conversion table
-- For each starting grid slot (1-20), shows average finish
-- position, win rate, podium rate, and DNF rate. Reveals
-- how the grid advantage decays toward the back.
-- ============================================================
SELECT
    r.grid,
    COUNT(*)                                            AS occurrences,
    ROUND(AVG(r.position), 2)                          AS avg_finish_position,
    ROUND(AVG(r.grid_vs_finish_delta), 2)              AS avg_positions_gained,
    ROUND(100.0 * SUM(r.is_winner)  / COUNT(*), 2)    AS win_rate_pct,
    ROUND(100.0 * SUM(r.is_podium) / COUNT(*), 2)     AS podium_rate_pct,
    ROUND(100.0 * SUM(r.is_dnf)   / COUNT(*), 2)      AS dnf_rate_pct
FROM master_race_table r
WHERE r.grid IS NOT NULL
  AND r.grid BETWEEN 1 AND 20
GROUP BY r.grid
ORDER BY r.grid;


-- ============================================================
-- Query 4: Driver vs teammate head-to-head
-- Self-join on constructor + race to compare drivers sharing
-- the same car. Positive avg_points_delta = driver A outperforms
-- driver B. Filtered to pairs with 5+ shared races.
-- ============================================================
WITH driver_race AS (
    SELECT
        raceId, year, constructorId, constructor_name,
        driverId, full_name, points, position, is_podium, is_dnf
    FROM master_race_table
    WHERE position IS NOT NULL
),
paired AS (
    SELECT
        a.year,
        a.constructorId,
        a.constructor_name,
        a.full_name                                     AS driver_a,
        b.full_name                                     AS driver_b,
        COUNT(*)                                        AS shared_races,
        ROUND(AVG(a.points - b.points), 3)             AS avg_points_delta,
        ROUND(AVG(
            CASE WHEN a.position IS NOT NULL
                  AND b.position IS NOT NULL
                 THEN CAST(b.position AS REAL) - a.position
                 ELSE NULL END
        ), 2)                                           AS avg_position_advantage,
        SUM(CASE WHEN a.points > b.points THEN 1 ELSE 0 END) AS races_ahead
    FROM driver_race a
    JOIN driver_race b
      ON  a.raceId        = b.raceId
      AND a.constructorId = b.constructorId
      AND a.driverId      < b.driverId
    GROUP BY a.year, a.constructorId, a.driverId, b.driverId
    HAVING shared_races >= 5
)
SELECT *
FROM paired
ORDER BY year DESC, avg_points_delta DESC;


-- ============================================================
-- Query 5: Circuit specialists
-- Ranks drivers by win rate at each circuit. RANK() OVER
-- PARTITION BY circuitRef finds the dominant driver per venue.
-- Filtered to drivers with 3+ starts at that circuit.
-- ============================================================
WITH circuit_driver AS (
    SELECT
        r.circuitRef,
        r.circuit_name,
        r.country,
        r.driverId,
        r.full_name,
        COUNT(*)                                        AS starts,
        SUM(r.is_winner)                                AS wins,
        SUM(r.is_podium)                                AS podiums,
        ROUND(100.0 * SUM(r.is_winner)  / COUNT(*), 1) AS win_rate_pct,
        ROUND(100.0 * SUM(r.is_podium) / COUNT(*), 1)  AS podium_rate_pct
    FROM master_race_table r
    GROUP BY r.circuitRef, r.driverId
    HAVING starts >= 3
)
SELECT
    circuit_name,
    country,
    full_name,
    starts,
    wins,
    podiums,
    win_rate_pct,
    podium_rate_pct,
    RANK() OVER (
        PARTITION BY circuitRef
        ORDER BY wins DESC, win_rate_pct DESC
    )                                                   AS rank_at_circuit
FROM circuit_driver
ORDER BY circuit_name, rank_at_circuit;


-- ============================================================
-- Query 6: Championship battle — round-by-round points gap
-- Tracks cumulative points for P1 and P2 in the drivers'
-- championship within a season. SUM() OVER with an ordered
-- window produces the rolling points total per driver.
-- Change the year value to explore different seasons.
-- ============================================================
WITH cumulative AS (
    SELECT
        r.year,
        r.round,
        r.driverId,
        r.full_name,
        SUM(r.points) OVER (
            PARTITION BY r.year, r.driverId
            ORDER BY r.round
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        )                                               AS cumulative_points
    FROM master_race_table r
    WHERE r.year = 2010   -- change to any season of interest
),
ranked AS (
    SELECT
        year, round, full_name, cumulative_points,
        RANK() OVER (
            PARTITION BY year, round
            ORDER BY cumulative_points DESC
        )                                               AS standing
    FROM cumulative
)
SELECT
    r1.round,
    r1.full_name                                        AS leader,
    r1.cumulative_points                                AS leader_points,
    r2.full_name                                        AS second_place,
    r2.cumulative_points                                AS second_points,
    r1.cumulative_points - r2.cumulative_points         AS gap_to_leader
FROM ranked r1
JOIN ranked r2
  ON r1.round = r2.round
 AND r1.standing = 1
 AND r2.standing = 2
ORDER BY r1.round;


-- ============================================================
-- Query 7: Pit stop strategy — constructor efficiency
-- Compares average and fastest pit stop performance per
-- constructor per season. Only available from 2012 onwards.
-- RANK() OVER PARTITION BY year shows relative speed ranking.
-- ============================================================
SELECT
    r.year,
    r.constructor_name,
    COUNT(DISTINCT r.raceId)                            AS races,
    SUM(r.total_pit_stops)                              AS total_stops,
    ROUND(AVG(r.avg_pit_duration_ms) / 1000.0, 3)      AS avg_stop_sec,
    ROUND(MIN(r.min_pit_duration_ms) / 1000.0, 3)      AS fastest_stop_sec,
    ROUND(AVG(r.total_pit_time_ms)   / 1000.0, 2)      AS avg_total_pit_time_sec,
    RANK() OVER (
        PARTITION BY r.year
        ORDER BY AVG(r.avg_pit_duration_ms) ASC
    )                                                   AS pit_speed_rank
FROM master_race_table r
WHERE r.total_pit_stops > 0
  AND r.year >= 2012
GROUP BY r.year, r.constructorId
ORDER BY r.year, avg_stop_sec;


-- ============================================================
-- Query 8: Driver reliability across career
-- Cumulative DNF rate tracked round-by-round using a running
-- SUM() OVER window. Shows how a driver's reliability profile
-- evolves over their career. Filtered to 10+ career starts.
-- ============================================================
WITH career_running AS (
    SELECT
        r.driverId,
        r.full_name,
        r.year,
        r.round,
        r.raceId,
        r.is_dnf,
        COUNT(*) OVER (
            PARTITION BY r.driverId
            ORDER BY r.year, r.round
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        )                                               AS career_starts,
        SUM(r.is_dnf) OVER (
            PARTITION BY r.driverId
            ORDER BY r.year, r.round
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        )                                               AS career_dnfs
    FROM master_race_table r
)
SELECT
    driverId,
    full_name,
    year,
    round,
    career_starts,
    career_dnfs,
    ROUND(
        100.0 * (career_starts - career_dnfs) / career_starts, 2
    )                                                   AS cumulative_finish_rate_pct
FROM career_running
WHERE career_starts >= 10
ORDER BY driverId, year, round;


-- ============================================================
-- Query 9: Pole position to race win conversion by circuit
-- How often does qualifying P1 convert to a race win?
-- Broken down by circuit and decade. Highlights circuits where
-- qualifying position matters most vs least.
-- ============================================================
WITH pole_and_winner AS (
    SELECT
        r.raceId,
        r.year,
        r.circuit_name,
        r.country,
        (r.year / 10) * 10                              AS decade,
        MAX(CASE WHEN r.quali_position = 1
                 THEN r.driverId END)                   AS pole_driver_id,
        MAX(CASE WHEN r.is_winner = 1
                 THEN r.driverId END)                   AS winner_id
    FROM master_race_table r
    WHERE r.quali_position IS NOT NULL
    GROUP BY r.raceId
)
SELECT
    circuit_name,
    country,
    decade,
    COUNT(*)                                            AS races_with_quali,
    SUM(
        CASE WHEN pole_driver_id = winner_id
             THEN 1 ELSE 0 END
    )                                                   AS pole_to_win_count,
    ROUND(
        100.0 * SUM(
            CASE WHEN pole_driver_id = winner_id
                 THEN 1 ELSE 0 END
        ) / COUNT(*), 1
    )                                                   AS pole_to_win_pct
FROM pole_and_winner
WHERE pole_driver_id IS NOT NULL
  AND winner_id IS NOT NULL
GROUP BY circuit_name, decade
ORDER BY circuit_name, decade;


-- ============================================================
-- Query 10: Constructor 3-season rolling average
-- Smooths single-season anomalies to reveal competitive
-- trajectory. AVG() OVER with ROWS BETWEEN 2 PRECEDING AND
-- CURRENT ROW produces a trailing 3-year average.
-- RANK() OVER shows the team's position in each season.
-- ============================================================
WITH season_totals AS (
    SELECT
        r.year,
        r.constructorId,
        r.constructor_name,
        ROUND(SUM(r.points), 1)                         AS season_points,
        SUM(r.is_winner)                                 AS season_wins,
        COUNT(DISTINCT r.raceId)                         AS season_races,
        ROUND(AVG(r.points), 3)                          AS avg_points_per_race
    FROM master_race_table r
    GROUP BY r.year, r.constructorId
)
SELECT
    year,
    constructor_name,
    season_points,
    season_wins,
    avg_points_per_race,
    ROUND(AVG(season_points) OVER (
        PARTITION BY constructorId
        ORDER BY year
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 1)                                               AS rolling_3yr_avg_points,
    ROUND(AVG(avg_points_per_race) OVER (
        PARTITION BY constructorId
        ORDER BY year
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 3)                                               AS rolling_3yr_avg_per_race,
    RANK() OVER (
        PARTITION BY year
        ORDER BY season_points DESC
    )                                                   AS season_rank
FROM season_totals
ORDER BY constructor_name, year;