"""
src/data/run_diagnostics.py
---------------------------
Runs all data quality diagnostic SQL queries against the SQLite database
and produces a human-readable markdown report at:
    reports/diagnostics_report.md

Purpose: Determine for each scorecard failure whether it is a
  DATA issue  → fix the source CSV / cleaning pipeline
  SCRIPT issue → fix validate_data.py / constants.py

Important note on ordering:
  raceId and driverId are assigned by Kaggle insert order, NOT
  chronologically. All temporal ordering in this script goes through
  races.year + races.round (never ORDER BY raceId / driverId).

Run from the project root:
  python src/data/run_diagnostics.py

Requires:
  data/processed/f1_database.db  (produced by build_master_table.py)
"""

import logging
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

import yaml

# ---------------------------------------------------------------------------
# Path-safe config import (same pattern as load_data.py)
# ---------------------------------------------------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

try:
    from src.config import CONFIG
    DB_PATH     = Path(CONFIG["paths"]["processed_data"]) / "f1_database.db"
    REPORT_DIR  = Path(CONFIG["paths"].get("reports", "reports"))
except Exception:
    DB_PATH     = Path("data/processed/f1_database.db")
    REPORT_DIR  = Path("reports")

REPORT_PATH = REPORT_DIR / "diagnostics_report.md"

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
# Lap time threshold (keep in sync with constants.py)
# ---------------------------------------------------------------------------
try:
    from constants import LAP_TIME_WARN_MS, LAP_TIME_CORRUPT_MS
except ImportError:
    LAP_TIME_WARN_MS    = 300_000
    LAP_TIME_CORRUPT_MS = 600_000


# ===========================================================================
# Query catalogue
# Each entry is a dict with:
#   block    : letter identifier (A, B, C …)
#   query_id : e.g. "A1", "A2"
#   title    : short human-readable label shown as ### heading
#   question : one-sentence description of what this tells us
#   interpret: what the numbers mean (data issue vs script issue)
#   sql      : the SQL to run
#   limit    : optional row cap for large result sets (None = no cap)
# ===========================================================================

QUERIES = [

    # =========================================================
    # BLOCK A — results.position null (Check 1 scorecard fail)
    # =========================================================
    {
        "block": "A",
        "query_id": "A1",
        "title": "Position null vs is_dnf cross-tab",
        "question": "Is the 41% null rate in results.position legitimate?",
        "interpret": (
            "**Data fine / script bug** if 'null position + NOT DNF' count is 0 or tiny.\n"
            "**Data problem** if 'null position + NOT DNF' or 'has position + DNF' counts are large."
        ),
        "sql": """
SELECT
    CASE
        WHEN position IS NULL AND is_dnf = 1 THEN 'null position + DNF (correct)'
        WHEN position IS NULL AND is_dnf = 0 THEN 'null position + NOT DNF (investigate)'
        WHEN position IS NOT NULL AND is_dnf = 1 THEN 'has position + DNF (investigate)'
        WHEN position IS NOT NULL AND is_dnf = 0 THEN 'has position + finished (correct)'
    END AS case_type,
    COUNT(*) AS row_count
FROM results
GROUP BY case_type
ORDER BY row_count DESC
""",
        "limit": None,
    },
    {
        "block": "A",
        "query_id": "A2",
        "title": "Status labels for null-position, non-DNF rows",
        "question": "What statuses explain rows where position is null but is_dnf = 0?",
        "interpret": (
            "'Not classified' is the expected answer — drivers who completed laps but "
            "weren't awarded a finishing position. If other statuses appear here, "
            "those are missing from the DNF classifier in constants.py."
        ),
        "sql": """
SELECT
    s.status,
    COUNT(*) AS count
FROM results r
JOIN status s ON r.statusId = s.statusId
WHERE r.position IS NULL
  AND r.is_dnf = 0
GROUP BY s.status
ORDER BY count DESC
""",
        "limit": None,
    },
    {
        "block": "A",
        "query_id": "A3",
        "title": "Null position count vs DNF flag count",
        "question": "Does null_count(position) ≈ count(is_dnf = 1)?",
        "interpret": (
            "Small difference (< 200) → the gap is explained by 'Not classified' entries; "
            "scorecard Check 1 failure is a **script bug** not a data problem.\n"
            "Large difference → genuine data integrity issue."
        ),
        "sql": """
SELECT
    SUM(CASE WHEN position IS NULL THEN 1 ELSE 0 END) AS position_null_count,
    SUM(CASE WHEN is_dnf = 1       THEN 1 ELSE 0 END) AS dnf_flag_count,
    SUM(CASE WHEN position IS NULL THEN 1 ELSE 0 END) -
    SUM(CASE WHEN is_dnf = 1       THEN 1 ELSE 0 END) AS difference
FROM results
""",
        "limit": None,
    },

    # =========================================================
    # BLOCK B — results.grid null (Check 1 secondary)
    # =========================================================
    {
        "block": "B",
        "query_id": "B1",
        "title": "Status of drivers with null grid",
        "question": "What were null-grid drivers doing — did they actually start?",
        "interpret": (
            "If dominated by 'Did not qualify / prequalify' → pit-lane start "
            "conversion (grid=0→NULL) is working correctly.\n"
            "If finished drivers appear here → data gap, grid was never recorded."
        ),
        "sql": """
SELECT
    s.status,
    COUNT(*) AS count
FROM results r
JOIN status s ON r.statusId = s.statusId
WHERE r.grid IS NULL
GROUP BY s.status
ORDER BY count DESC
LIMIT 20
""",
        "limit": None,
    },
    {
        "block": "B",
        "query_id": "B2",
        "title": "Era breakdown of null-grid rows",
        "question": "Are null grid positions concentrated in a specific era?",
        "interpret": (
            "Concentration in pre-1980 → historic data gap, expected and acceptable.\n"
            "Significant counts in modern era → unexplained data issue."
        ),
        "sql": """
SELECT
    ra.year,
    COUNT(*) AS null_grid_count
FROM results r
JOIN races ra ON r.raceId = ra.raceId
WHERE r.grid IS NULL
GROUP BY ra.year
ORDER BY ra.year DESC
LIMIT 30
""",
        "limit": None,
    },
    {
        "block": "B",
        "query_id": "B3",
        "title": "Null-grid rows that scored points",
        "question": "How many null-grid drivers actually scored championship points?",
        "interpret": (
            "0 → all null grids are DNS/DNQ entries, which legitimately have no grid.\n"
            "> 0 → drivers started (they scored points) but grid was not recorded "
            "— genuine data gap."
        ),
        "sql": """
SELECT
    COUNT(*) AS null_grid_with_points,
    SUM(points) AS total_points_from_null_grid
FROM results
WHERE grid IS NULL
  AND points > 0
""",
        "limit": None,
    },

    # =========================================================
    # BLOCK C — Duplicate raceId × driverId (Check 4)
    # =========================================================
    {
        "block": "C",
        "query_id": "C1",
        "title": "Actual year and name for top duplicate raceIds",
        "question": "Do the high raceIds (700-800+) actually belong to 1950s races?",
        "interpret": (
            "This is the key test for the year-lookup script bug.\n"
            "If results show years 2021-2024 → **script bug** (year lookup was broken, "
            "these are Sprint weekends misclassified as 'Unexplained').\n"
            "If results genuinely show 1950s years → the data itself has non-chronological "
            "raceIds (which is a known Kaggle dataset property) and the duplicates need "
            "a different explanation."
        ),
        "sql": """
SELECT
    ra.raceId,
    ra.year,
    ra.round,
    ra.name,
    COUNT(DISTINCT r.driverId) AS distinct_drivers,
    COUNT(*) AS total_rows,
    COUNT(*) - COUNT(DISTINCT r.driverId) AS duplicate_rows
FROM results r
JOIN races ra ON r.raceId = ra.raceId
WHERE ra.raceId IN (792, 800, 809, 780, 791, 828, 839, 777, 717, 745, 746, 766)
GROUP BY ra.raceId, ra.year, ra.round, ra.name
ORDER BY ra.year, ra.round
""",
        "limit": None,
    },
    {
        "block": "C",
        "query_id": "C2",
        "title": "Full detail on raceId 792 duplicate rows",
        "question": "What exactly differs between the duplicate rows for this race?",
        "interpret": (
            "Different constructorId across rows → dual-constructor (pre-1980s historical).\n"
            "Different laps count across rows → sprint + main race entries.\n"
            "Identical across all columns → true duplicate, data error."
        ),
        "sql": """
SELECT
    r.resultId,
    r.driverId,
    d.full_name,
    r.constructorId,
    c.name AS constructor,
    r.grid,
    r.position,
    r.laps,
    r.points,
    s.status,
    r.positionText
FROM results r
JOIN drivers d ON r.driverId = d.driverId
JOIN constructors c ON r.constructorId = c.constructorId
JOIN status s ON r.statusId = s.statusId
WHERE r.raceId = 792
ORDER BY r.driverId, r.resultId
""",
        "limit": 60,
    },
    {
        "block": "C",
        "query_id": "C3",
        "title": "Classifier breakdown for all unexplained duplicate pairs",
        "question": "For each duplicate pair, do rows differ by constructor, laps, or neither?",
        "interpret": (
            "distinct_constructors = 2 → dual-constructor entry.\n"
            "laps_difference > 0 → sprint vs main race (different race lengths).\n"
            "Both = 0 → truly identical rows, genuine data corruption."
        ),
        "sql": """
SELECT
    ra.year,
    ra.round,
    ra.name AS race_name,
    r.raceId,
    r.driverId,
    d.full_name,
    COUNT(*) AS occurrences,
    COUNT(DISTINCT r.constructorId) AS distinct_constructors,
    MAX(r.laps) - MIN(r.laps) AS laps_difference,
    MAX(r.points) AS max_points,
    GROUP_CONCAT(c.name, ' / ') AS constructors,
    GROUP_CONCAT(r.laps, ' / ') AS laps_values,
    GROUP_CONCAT(s.status, ' / ') AS statuses,
    GROUP_CONCAT(r.positionText, ' / ') AS position_texts
FROM results r
JOIN races ra ON r.raceId = ra.raceId
JOIN drivers d ON r.driverId = d.driverId
JOIN constructors c ON r.constructorId = c.constructorId
JOIN status s ON r.statusId = s.statusId
WHERE r.raceId IN (
    717, 745, 746, 770, 774, 776, 777, 779, 780,
    783, 784, 785, 787, 788, 789, 791, 792, 793,
    795, 797, 800, 801, 803, 804, 806, 809,
    810, 811, 814, 815, 817, 820, 823, 828, 831, 838, 839
)
GROUP BY r.raceId, r.driverId
HAVING COUNT(*) > 1
ORDER BY ra.year, ra.round, r.raceId, r.driverId
""",
        "limit": 100,
    },
    {
        "block": "C",
        "query_id": "C4",
        "title": "Circuit info for top duplicate races",
        "question": "Are the duplicate races held at circuits that could explain dual entries?",
        "interpret": (
            "Indianapolis Motor Speedway → the Kaggle dataset includes the Indy 500 "
            "as an F1 WC round 1950-1960; some drivers have dual entries.\n"
            "Other circuits → check for sprint calendar or historical data issue."
        ),
        "sql": """
SELECT
    ra.raceId,
    ra.year,
    ra.round,
    ra.name AS race_name,
    ci.name AS circuit_name,
    ci.location,
    ci.country
FROM races ra
JOIN circuits ci ON ra.circuitId = ci.circuitId
WHERE ra.raceId IN (792, 800, 809, 780, 791, 828, 839, 777, 717, 745, 746)
ORDER BY ra.year, ra.round
""",
        "limit": None,
    },

    # =========================================================
    # BLOCK D — Lap times > 600s (Check 5 hard fail)
    # =========================================================
    {
        "block": "D",
        "query_id": "D1",
        "title": "All laps > 600s with context",
        "question": "Show every corrupt lap with race, driver, lap number, and ratio to own average.",
        "interpret": (
            "ratio_to_own_avg > 6 and race is old (pre-1990) → likely corrupt timing data "
            "from early electronic timing systems.\n"
            "ratio_to_own_avg 3-6 and recent race → probable red-flag suspension "
            "(race stopped, clock kept running). These may warrant raising the corrupt "
            "threshold or adding a red-flag band."
        ),
        "sql": f"""
SELECT
    ra.year,
    ra.round,
    ra.name AS race_name,
    lt.raceId,
    lt.driverId,
    d.full_name,
    lt.lap,
    ROUND(lt.lap_time_ms / 1000.0, 1) AS lap_time_seconds,
    lt.position AS track_position,
    ROUND(
        lt.lap_time_ms / NULLIF((
            SELECT AVG(lt2.lap_time_ms)
            FROM lap_times lt2
            WHERE lt2.raceId = lt.raceId
              AND lt2.driverId = lt.driverId
              AND lt2.lap_time_ms < {LAP_TIME_WARN_MS}
        ), 0),
        1
    ) AS ratio_to_own_avg
FROM lap_times lt
JOIN races ra ON lt.raceId = ra.raceId
JOIN drivers d ON lt.driverId = d.driverId
WHERE lt.lap_time_ms > {LAP_TIME_CORRUPT_MS}
ORDER BY lt.lap_time_ms DESC
""",
        "limit": None,
    },
    {
        "block": "D",
        "query_id": "D2",
        "title": "How many drivers affected on the same lap number",
        "question": "Was the slow lap isolated to one driver or did the whole field slow down?",
        "interpret": (
            "drivers_affected > 3 on the same lap → almost certainly a red flag or "
            "safety car period (real event, threshold may need raising).\n"
            "drivers_affected = 1 → isolated to one driver, more likely corrupt timing."
        ),
        "sql": f"""
SELECT
    ra.year,
    ra.round,
    ra.name AS race_name,
    lt.raceId,
    lt.lap AS lap_number,
    COUNT(*) AS drivers_affected,
    ROUND(MIN(lt.lap_time_ms) / 1000.0, 1) AS min_s,
    ROUND(MAX(lt.lap_time_ms) / 1000.0, 1) AS max_s
FROM lap_times lt
JOIN races ra ON lt.raceId = ra.raceId
WHERE lt.lap_time_ms > {LAP_TIME_CORRUPT_MS}
GROUP BY lt.raceId, lt.lap
ORDER BY drivers_affected DESC, ra.year, ra.round
""",
        "limit": None,
    },
    {
        "block": "D",
        "query_id": "D3",
        "title": "All driver lap times around the worst lap (raceId=340, laps 16-20)",
        "question": "Was the 854s lap isolated or did multiple drivers slow on that lap?",
        "interpret": (
            "Multiple drivers with very high times on the same lap → red flag event.\n"
            "Only one driver with a high time → corrupt data point for that driver."
        ),
        "sql": """
SELECT
    lt.lap,
    lt.driverId,
    d.full_name,
    ROUND(lt.lap_time_ms / 1000.0, 1) AS lap_time_seconds,
    lt.position
FROM lap_times lt
JOIN drivers d ON lt.driverId = d.driverId
WHERE lt.raceId = 340
  AND lt.lap BETWEEN 16 AND 20
ORDER BY lt.lap, lt.lap_time_ms DESC
""",
        "limit": 50,
    },
    {
        "block": "D",
        "query_id": "D4",
        "title": "Lap time distribution for raceId 340",
        "question": "What is the normal pace for this race, to contextualise the 854s outlier?",
        "interpret": (
            "If avg is ~90s and max is 854s, the outlier is 9x normal pace — "
            "either a very long red flag or corrupt data. "
            "Check D3 to determine which."
        ),
        "sql": f"""
SELECT
    ROUND(MIN(lap_time_ms) / 1000.0, 1) AS min_s,
    ROUND(AVG(lap_time_ms) / 1000.0, 1) AS avg_s,
    ROUND(MAX(lap_time_ms) / 1000.0, 1) AS max_s,
    COUNT(*) AS total_laps,
    SUM(CASE WHEN lap_time_ms BETWEEN {LAP_TIME_WARN_MS} AND {LAP_TIME_CORRUPT_MS}
             THEN 1 ELSE 0 END) AS sc_vsc_laps,
    SUM(CASE WHEN lap_time_ms > {LAP_TIME_CORRUPT_MS}
             THEN 1 ELSE 0 END) AS over_corrupt_threshold
FROM lap_times
WHERE raceId = 340
""",
        "limit": None,
    },

    # =========================================================
    # BLOCK E — Unclassified status labels (Check 7)
    # =========================================================
    {
        "block": "E",
        "query_id": "E1",
        "title": "All status labels not currently classified as Finished or DNF",
        "question": "Which status labels are falling through the classifier?",
        "interpret": (
            "Labels with positionText in (R,D,E,W,F,N) and no position → clearly DNFs, "
            "**script issue** (missing keyword in constants.py).\n"
            "Labels with a filled position or points > 0 → driver finished, need "
            "to check if label is correct or if it's a data issue."
        ),
        "sql": """
SELECT
    s.status,
    COUNT(*) AS occurrences,
    GROUP_CONCAT(DISTINCT r.positionText) AS position_texts,
    SUM(CASE WHEN r.position IS NOT NULL THEN 1 ELSE 0 END) AS rows_with_position,
    SUM(CASE WHEN r.points > 0 THEN 1 ELSE 0 END) AS rows_with_points
FROM results r
JOIN status s ON r.statusId = s.statusId
WHERE LOWER(s.status) NOT IN (
    'finished',
    'engine','gearbox','transmission','hydraulics','brakes','clutch',
    'suspension','electrical','oil pressure','water leak','fuel system',
    'tyres','wheel','exhaust','power unit','turbo','compressor',
    'pneumatics','cooling','alternator','electronics','driveshaft',
    'differential','radiator','vibrations','battery','throttle','fire',
    'overheating','ignition','halfshaft','handling','steering',
    'injection','chassis','mechanical','magneto','axle','power loss',
    'distributor','broken wing','front wing','rear wing','supercharger',
    'ers','undertray','spark plugs','track rod','drivetrain','crankshaft',
    'cv joint','brake duct',
    'accident','collision','spun off','damage','puncture',
    'retired','withdrew','illness','injury','physical','unwell',
    'disqualified','did not qualify','did not prequalify','excluded',
    'debris','safety'
)
AND LOWER(s.status) NOT LIKE '+% lap%'
GROUP BY s.status
ORDER BY occurrences DESC
""",
        "limit": None,
    },
    {
        "block": "E",
        "query_id": "E2",
        "title": "Encoding check on Excluded / Disqualified labels",
        "question": "Is 'Excluded' failing to match due to whitespace or encoding?",
        "interpret": (
            "label_length > expected length OR first_3_bytes_hex != '457863' (Exc) → "
            "hidden characters, **data issue** in the status table itself.\n"
            "All lengths normal → 'Excluded' is genuinely absent from keyword list, "
            "**script issue**."
        ),
        "sql": """
SELECT
    s.statusId,
    s.status,
    LENGTH(s.status) AS label_length,
    HEX(SUBSTR(s.status, 1, 3)) AS first_3_bytes_hex,
    COUNT(r.resultId) AS result_count
FROM status s
LEFT JOIN results r ON s.statusId = r.statusId
WHERE LOWER(s.status) LIKE '%exclu%'
   OR LOWER(s.status) LIKE '%disqual%'
GROUP BY s.statusId, s.status
ORDER BY s.statusId
""",
        "limit": None,
    },
    {
        "block": "E",
        "query_id": "E3",
        "title": "Keyword coverage check against updated constants.py",
        "question": "After the constants.py fix, which labels are now covered and which still need work?",
        "interpret": (
            "'In updated MECHANICAL_KEYWORDS' → will be fixed once constants.py update is applied.\n"
            "'Intentionally Other' → correctly left unclassified (Not classified, 107% Rule etc).\n"
            "'Still missing from keywords' → requires another keyword addition."
        ),
        "sql": """
SELECT
    s.status,
    COUNT(*) AS count,
    CASE
        WHEN LOWER(s.status) IN (
            'overheating','ignition','halfshaft','handling','steering',
            'injection','chassis','mechanical','magneto','axle',
            'power loss','distributor','broken wing','front wing','rear wing',
            'supercharger','ers','undertray','spark plugs','track rod',
            'drivetrain','crankshaft','cv joint','brake duct','radiator'
        ) THEN 'Covered by updated MECHANICAL_KEYWORDS'
        WHEN LOWER(s.status) IN ('physical','unwell','driver unwell','injured')
            THEN 'Covered by updated driver-physical keywords'
        WHEN s.status IN (
            'Not classified','107% Rule','Underweight',
            'Not restarted','Stalled','Launch control',
            'Driver Seat','Seat','Excluded'
        ) THEN 'Intentionally Other (review manually)'
        ELSE 'Still missing — add keyword'
    END AS coverage
FROM results r
JOIN status s ON r.statusId = s.statusId
WHERE s.status IN (
    'Not classified','Ignition','Halfshaft','Handling','Steering',
    'Radiator','Injection','Physical','Chassis','Magneto','Axle',
    'Power loss','Distributor','Broken wing','Driver unwell','Rear wing',
    '107% Rule','Excluded','Injured','Front wing','Supercharger','ERS',
    'Undertray','Spark plugs','Track rod','Drivetrain','Stalled',
    'Launch control','Driver Seat','Crankshaft','Not restarted',
    'CV joint','Underweight','Seat','Brake duct'
)
GROUP BY s.status, coverage
ORDER BY count DESC
""",
        "limit": None,
    },

    # =========================================================
    # BLOCK F — qualifying.q1_ms null (157 rows)
    # =========================================================
    {
        "block": "F",
        "query_id": "F1",
        "title": "Sample of null q1_ms qualifying rows",
        "question": "Are these DNS entries, DQ entries, or data gaps?",
        "interpret": (
            "race_status = 'Did not qualify' / 'Did not prequalify' → driver didn't set "
            "a time, null is correct.\n"
            "race_status = 'Finished' with null q1 → genuine data gap."
        ),
        "sql": """
SELECT
    ra.year,
    ra.round,
    ra.name AS race_name,
    q.raceId,
    q.driverId,
    d.full_name,
    q.position AS quali_position,
    q.q1_ms,
    q.q2_ms,
    q.q3_ms,
    s.status AS race_status,
    r.grid,
    r.laps AS race_laps
FROM qualifying q
JOIN races ra ON q.raceId = ra.raceId
JOIN drivers d ON q.driverId = d.driverId
LEFT JOIN results r ON q.raceId = r.raceId AND q.driverId = r.driverId
LEFT JOIN status s ON r.statusId = s.statusId
WHERE q.q1_ms IS NULL
ORDER BY ra.year, ra.round, q.position
LIMIT 30
""",
        "limit": None,
    },
    {
        "block": "F",
        "query_id": "F2",
        "title": "Year distribution of null q1_ms",
        "question": "Are null qualifying times concentrated in a specific era?",
        "interpret": (
            "All in pre-2006 → expected, qualifying format was different.\n"
            "Post-2006 entries present → data gaps in modern qualifying records."
        ),
        "sql": """
SELECT
    ra.year,
    COUNT(*) AS null_q1_count
FROM qualifying q
JOIN races ra ON q.raceId = ra.raceId
WHERE q.q1_ms IS NULL
GROUP BY ra.year
ORDER BY ra.year
""",
        "limit": None,
    },

    # =========================================================
    # BLOCK G — pit_stops null duration (534 rows)
    # =========================================================
    {
        "block": "G",
        "query_id": "G1",
        "title": "Year breakdown of null pit durations",
        "question": "Are null pit durations an early-era timing gap or spread across all years?",
        "interpret": (
            "Concentrated in 2011-2012 → early pit stop data collection had gaps, expected.\n"
            "Spread across many years → systematic issue worth investigating."
        ),
        "sql": """
SELECT
    ra.year,
    COUNT(*) AS null_duration_count,
    COUNT(DISTINCT p.raceId) AS races_affected
FROM pit_stops p
JOIN races ra ON p.raceId = ra.raceId
WHERE p.pit_duration_ms IS NULL
GROUP BY ra.year
ORDER BY ra.year
""",
        "limit": None,
    },
    {
        "block": "G",
        "query_id": "G2",
        "title": "Races most affected by null pit durations",
        "question": "Are nulls from whole-race data feed failures or random individual stops?",
        "interpret": (
            "null_stops ≈ total_stops → entire race had no timing data (feed failure).\n"
            "null_stops << total_stops → individual stops missing, random gaps."
        ),
        "sql": """
SELECT
    ra.year,
    ra.round,
    ra.name AS race_name,
    p.raceId,
    COUNT(*) AS null_duration_stops,
    (SELECT COUNT(*) FROM pit_stops p2 WHERE p2.raceId = p.raceId) AS total_stops_in_race,
    ROUND(
        100.0 * COUNT(*) /
        (SELECT COUNT(*) FROM pit_stops p2 WHERE p2.raceId = p.raceId),
        1
    ) AS pct_null
FROM pit_stops p
JOIN races ra ON p.raceId = ra.raceId
WHERE p.pit_duration_ms IS NULL
GROUP BY p.raceId, ra.year, ra.round, ra.name
ORDER BY null_duration_stops DESC
LIMIT 20
""",
        "limit": None,
    },
]


# ===========================================================================
# Report helpers
# ===========================================================================

def _df_to_md_table(rows: list[tuple], columns: list[str]) -> str:
    """Convert query result rows to a markdown table string."""
    if not rows:
        return "_No rows returned._"

    # Format all values as strings, handle None
    def fmt(v) -> str:
        if v is None:
            return "—"
        if isinstance(v, float):
            # Show up to 2 decimal places, strip trailing zeros
            return f"{v:,.2f}".rstrip("0").rstrip(".")
        if isinstance(v, int):
            return f"{v:,}"
        return str(v)

    col_headers = " | ".join(columns)
    separator   = " | ".join("---" for _ in columns)
    header_row  = f"| {col_headers} |"
    sep_row     = f"| {separator} |"
    data_rows   = [
        "| " + " | ".join(fmt(v) for v in row) + " |"
        for row in rows
    ]
    return "\n".join([header_row, sep_row] + data_rows)


def _run_query(conn: sqlite3.Connection, sql: str, limit: int | None) -> tuple[list, list]:
    """Run a SQL query and return (rows, column_names). Applies row limit if set."""
    cursor = conn.cursor()
    cursor.execute(sql.strip())
    columns = [desc[0] for desc in cursor.description]
    rows    = cursor.fetchall()
    if limit is not None:
        rows = rows[:limit]
    return rows, columns


# ===========================================================================
# Report assembly
# ===========================================================================

def generate_diagnostics_report(db_path: Path, report_path: Path) -> None:
    """
    Connect to the SQLite DB, run all diagnostic queries, and write
    a structured markdown report.
    """
    if not db_path.exists():
        log.error("Database not found: %s", db_path)
        log.error("Run build_master_table.py first to create f1_database.db")
        sys.exit(1)

    log.info("Connecting to: %s", db_path)
    conn = sqlite3.connect(db_path)

    report_path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = [
        "# F1 Data Quality — Diagnostics Report",
        "",
        f"> **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ",
        f"> **Database:** `{db_path}`  ",
        "> **Purpose:** Classify each scorecard failure as DATA issue or SCRIPT issue",
        "",
        "---",
        "",
        "## How to read this report",
        "",
        "Each query block has an **Interpretation guide** explaining what the numbers mean.",
        "After reviewing, classify each finding as:",
        "",
        "- 🔴 **Data issue** — fix the source CSV or `clean_data.py`",
        "- 🟡 **Script issue** — fix `validate_data.py` or `constants.py`",
        "- 🟢 **Expected / justified** — no action needed, document and move on",
        "",
        "---",
        "",
    ]

    current_block = None
    total_queries  = len(QUERIES)
    failed_queries = 0

    for i, q in enumerate(QUERIES, 1):
        # Block header
        if q["block"] != current_block:
            current_block = q["block"]
            block_label = {
                "A": "BLOCK A — `results.position` null (Scorecard Check 1)",
                "B": "BLOCK B — `results.grid` null (Scorecard Check 1 secondary)",
                "C": "BLOCK C — Duplicate `raceId × driverId` (Scorecard Check 4)",
                "D": "BLOCK D — Lap times > 600s (Scorecard Check 5)",
                "E": "BLOCK E — Unclassified status labels (Scorecard Check 7)",
                "F": "BLOCK F — `qualifying.q1_ms` null 1.5% (Bonus)",
                "G": "BLOCK G — `pit_stops` null duration 4.7% (Bonus)",
            }.get(current_block, f"BLOCK {current_block}")
            lines += [f"## {block_label}", ""]

        # Query section
        lines += [
            f"### {q['query_id']}. {q['title']}",
            "",
            f"**Question:** {q['question']}",
            "",
            f"**Interpretation guide:**  ",
            q["interpret"],
            "",
        ]

        log.info("[%d/%d] Running %s: %s", i, total_queries, q["query_id"], q["title"])

        try:
            rows, columns = _run_query(conn, q["sql"], q["limit"])

            row_note = ""
            if q["limit"] is not None and len(rows) == q["limit"]:
                row_note = f" _(showing first {q['limit']} rows)_"

            lines += [
                f"**Results:** {len(rows):,} rows{row_note}",
                "",
                _df_to_md_table(rows, columns),
                "",
            ]

        except sqlite3.Error as exc:
            failed_queries += 1
            log.error("  Query %s failed: %s", q["query_id"], exc)
            lines += [
                f"> ⚠️ **Query failed:** `{exc}`  ",
                "> Check that the database schema matches expectations.",
                "",
            ]

        lines.append("---")
        lines.append("")

    # Footer
    lines += [
        "## Summary",
        "",
        f"- Queries run: **{total_queries}**",
        f"- Queries failed: **{failed_queries}**",
        f"- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "_Run `validate_data.py` after any fixes to regenerate the main quality report._",
    ]

    report_text = "\n".join(lines)
    report_path.write_text(report_text, encoding="utf-8")

    conn.close()

    log.info("=" * 55)
    log.info("Diagnostics report written -> %s", report_path)
    log.info("  Queries run    : %d", total_queries)
    log.info("  Queries failed : %d", failed_queries)
    log.info("=" * 55)


# ===========================================================================
# Entry point
# ===========================================================================

if __name__ == "__main__":
    log.info("=" * 55)
    log.info("F1 Data Quality Diagnostics")
    log.info("  DB     : %s", DB_PATH)
    log.info("  Report : %s", REPORT_PATH)
    log.info("=" * 55)

    generate_diagnostics_report(DB_PATH, REPORT_PATH)