"""
src/data/constants.py
---------------------
Single source of truth for F1 status / DNF classification
AND shared numeric thresholds used across the pipeline.

Imported by:
  - clean_data.py
  - validate_data.py
  - merge_data.py
  - build_master_table.py

DO NOT duplicate these values elsewhere. Change them here and every
script in the pipeline picks up the update automatically.
"""

# ---------------------------------------------------------------------------
# Numeric thresholds — shared across clean_data.py and validate_data.py
# Changing a value here propagates to both cleaning and validation automatically.
# ---------------------------------------------------------------------------

# Lap time bounds (milliseconds)
# 30 s  — absolute floor used in cleaning (formation / pit-exit laps recorded
#          in some older datasets fall between 30–40 s; we keep them in the
#          cleaned CSV and let validate_data flag anything below 40 s separately)
LAP_TIME_MIN_MS     = 30_000    # cleaning lower bound
LAP_TIME_WARN_MS    = 300_000   # validation warning threshold (SC/VSC laps)
LAP_TIME_CORRUPT_MS = 600_000   # validation / cleaning hard upper bound
LAP_TIME_MAX_MS     = LAP_TIME_CORRUPT_MS   # alias used in clean_data.py

# Pit stop duration bounds (milliseconds)
PIT_STOP_MIN_MS = 15_000    # 15 s — world-record territory
PIT_STOP_MAX_MS = 300_000   # 5 min — beyond this is repair / drive-through

# Z-score threshold for lap time outlier detection in validate_data.py
LAP_Z_THRESHOLD = 5

# GPS coordinate validity bounds
LAT_MIN, LAT_MAX = -90.0, 90.0
LNG_MIN, LNG_MAX = -180.0, 180.0

# ---------------------------------------------------------------------------
# positionText DNF codes  (used in clean_data.py → clean_results)
# These are the raw codes in the Kaggle dataset's positionText column.
# R=Retired, D=Disqualified, E=Excluded, W=Withdrew, F=Failed to qualify,
# N=Not classified
# NOTE: is_dnf is recomputed from the status label downstream (merge /
# build_master_table), so this is only used for the interim flag in
# results_clean.csv. Keep it in sync with the status-label classifiers above.
# ---------------------------------------------------------------------------
POSITION_TEXT_DNF_CODES: frozenset[str] = frozenset({"R", "D", "E", "W", "F", "N"})

# ---------------------------------------------------------------------------
# DNF keyword classifier
# Matches against the 'status' string (case-insensitive substring match).
# Covers mechanical failures, crashes, disqualifications, and administrative
# non-starts. Source: full status table from the F1 dataset (~139 categories).
# ---------------------------------------------------------------------------
DNF_KEYWORDS: list[str] = [
    # Mechanical failures (subset — full list in MECHANICAL_KEYWORDS)
    "engine", "gearbox", "transmission", "hydraulics", "brakes", "clutch",
    "suspension", "electrical", "oil", "water", "fuel", "tyre", "wheel",
    "exhaust", "power unit", "turbo", "compressor", "pneumatic", "cooling",
    "alternator", "electronics", "driveshaft", "differential", "radiator",
    "vibrations", "battery", "throttle", "fire", "overheating", "ignition",
    "halfshaft", "handling", "steering", "injection", "chassis", "mechanical",
    "magneto", "axle", "power loss", "distributor", "broken wing", "rear wing",
    "front wing", "supercharger", "ers", "undertray", "spark plugs", "track rod",
    "drivetrain", "crankshaft", "cv joint", "brake duct",
    # Crashes / incidents
    "accident", "collision", "spun off", "damage", "puncture",
    # Driver / team decisions
    "retired", "withdrew", "illness", "injury",
    # Driver physical
    "physical", "unwell",
    # Administrative
    "disqualified", "did not", "excluded",
    # Catch-all
    "debris", "safety",
]

# ---------------------------------------------------------------------------
# Mechanical DNF sub-classifier
# Subset of DNF_KEYWORDS that represent purely mechanical/technical causes.
# Used for dnf_type = "mechanical".
# ---------------------------------------------------------------------------
MECHANICAL_KEYWORDS: list[str] = [
    # Powertrain
    "engine", "gearbox", "transmission", "clutch", "turbo", "compressor",
    "supercharger", "throttle", "fuel", "injection", "ignition", "magneto",
    "spark plugs", "distributor", "launch control", "power unit", "ers",
    # Cooling / fluids
    "hydraulics", "oil", "water", "cooling", "overheating", "radiator",
    # Electrical / electronics
    "electrical", "alternator", "electronics", "battery",
    # Suspension / steering / handling
    "suspension", "steering", "handling", "brakes",
    # Drivetrain / axles
    "driveshaft", "differential", "drivetrain", "halfshaft", "axle",
    "cv joint", "track rod",
    # Wheels / tyres / body
    "tyre", "wheel", "exhaust", "pneumatic",
    # Structural / aero
    "chassis", "broken wing", "front wing", "rear wing", "undertray",
    "brake duct", "vibrations", "crankshaft",
    # Misc mechanical catch-alls
    "mechanical", "power loss", "fire",
]

# ---------------------------------------------------------------------------
# Crash DNF sub-classifier
# ---------------------------------------------------------------------------
CRASH_KEYWORDS: list[str] = [
    "accident", "collision", "spun off", "damage", "puncture",
]

# ---------------------------------------------------------------------------
# Classified finisher patterns
# A driver is a "Finished" entry if their status is literally "Finished" OR
# they were classified as a lapped finisher (+N Laps / +N Lap).
# ---------------------------------------------------------------------------
FINISH_KEYWORDS: list[str] = ["finished"]

# Handles "+1 Lap", "+2 Laps", "+1 lap", "lapped", "lap down" etc.
LAPPED_PATTERNS: list[str] = [
    "+1 lap", "+2 lap", "+3 lap", "+4 lap", "+5 lap",
    "+6 lap", "+7 lap", "+8 lap", "+9 lap",
    "lapped", "lap down",
]


# ---------------------------------------------------------------------------
# Classification functions
# ---------------------------------------------------------------------------

def is_dnf(status: str) -> bool:
    """Return True if the status label represents a DNF of any kind."""
    if not isinstance(status, str):
        return False
    ll = status.lower()
    # Lapped finishers are classified finishers, not DNFs
    if ll.startswith("+") and "lap" in ll:
        return False
    return any(kw in ll for kw in DNF_KEYWORDS)


def is_finish(status: str) -> bool:
    """
    Return True if the driver was a classified finisher.
    Includes both 'Finished' and lapped finishers (+N Laps).
    """
    if not isinstance(status, str):
        return False
    ll = status.lower()
    if any(kw in ll for kw in FINISH_KEYWORDS):
        return True
    if ll.startswith("+") and "lap" in ll:
        return True
    if any(pat in ll for pat in LAPPED_PATTERNS):
        return True
    return False


def classify_dnf_type(status: str) -> str | None:
    """
    For DNF entries, return a sub-category string:
      'mechanical' — technical/car failure
      'crash'      — accident or collision
      'other'      — retired, withdrew, disqualified, did not qualify, etc.
      None         — not a DNF (finished or lapped)
    """
    if not isinstance(status, str) or not is_dnf(status):
        return None
    ll = status.lower()
    if any(kw in ll for kw in MECHANICAL_KEYWORDS):
        return "mechanical"
    if any(kw in ll for kw in CRASH_KEYWORDS):
        return "crash"
    return "other"


def compute_is_dnf_series(status_series) -> "pd.Series":
    """
    Vectorised is_dnf over a pandas Series of status strings.
    Returns an int8 Series (1 = DNF, 0 = not DNF).
    """
    import pandas as pd
    return status_series.apply(
        lambda s: int(is_dnf(str(s))) if pd.notna(s) else 0
    ).astype("int8")


def compute_dnf_type_series(status_series) -> "pd.Series":
    """
    Vectorised classify_dnf_type over a pandas Series of status strings.
    Returns an object Series with values: 'mechanical', 'crash', 'other', or None.
    """
    import pandas as pd
    return status_series.apply(
        lambda s: classify_dnf_type(str(s)) if pd.notna(s) else None
    )