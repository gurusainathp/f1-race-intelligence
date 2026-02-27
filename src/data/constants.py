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
    # ── Powertrain ────────────────────────────────────────────────────────────
    "engine", "gearbox", "transmission", "clutch", "turbo", "compressor",
    "supercharger", "throttle", "injection", "ignition", "magneto",
    "spark plugs", "distributor", "launch control", "power unit", "ers",
    "exhaust", "alternator", "battery", "electronics", "electrical",
    "vibrations", "pneumatic",
    # ── Oil system ────────────────────────────────────────────────────────────
    # NOTE: bare "oil" intentionally kept — catches "oil pressure", "oil pump"
    # etc.  Do NOT remove; it also matches any future "oil *" status labels.
    "oil",
    # ── Fuel system ──────────────────────────────────────────────────────────
    # NOTE: bare "fuel" catches "fuel pump", "fuel leak", "fuel pressure" etc.
    # "out of fuel" is matched via this keyword.  See classify_dnf_type() for
    # the special-case note: some "out of fuel" rows have a finishing position
    # (driver was classified despite running dry).  is_dnf() correctly returns
    # True for all of them; the positionText / position columns distinguish
    # whether the driver was ultimately classified.
    "fuel",
    # ── Cooling / water system ────────────────────────────────────────────────
    "hydraulics", "cooling", "overheating", "radiator",
    "water",   # catches "water pressure", "water pump", "water pipe", "water leak"
    "heat shield",
    # ── Suspension / steering / handling ──────────────────────────────────────
    "suspension", "steering", "handling", "brakes",
    # ── Drivetrain / axles ────────────────────────────────────────────────────
    "driveshaft", "differential", "drivetrain", "halfshaft", "axle",
    "cv joint", "track rod",
    # ── Wheels / tyres / body ────────────────────────────────────────────────
    "tyre",    # catches "tyre" and "tyre puncture"
    "wheel",   # catches "wheel bearing", "wheel nut", "wheel rim"
    # ── Structural / aero ─────────────────────────────────────────────────────
    "chassis", "broken wing", "front wing", "rear wing", "undertray",
    "brake duct", "crankshaft",
    # ── Misc mechanical catch-alls ────────────────────────────────────────────
    "mechanical", "power loss", "fire",   # "fire" also catches "engine fire", "heat shield fire"
    "technical",                           # generic technical retirement
    "cooling system",
    # ── Crashes / incidents ───────────────────────────────────────────────────
    "accident",          # includes "fatal accident"
    "collision",         # includes "collision damage"
    "spun off",
    "damage",
    "puncture",
    # ── Driver / team decisions ───────────────────────────────────────────────
    "retired", "withdrew", "illness", "injury",
    # ── Driver physical ───────────────────────────────────────────────────────
    "physical", "unwell",
    "eye injury",        # not caught by bare "injury" (different token order)
    # ── Safety / other retirements ────────────────────────────────────────────
    "safety belt",
    "safety concerns",
    "refuelling",        # pit-lane equipment failure → retirement
    "fuel rig",
    # ── Administrative DNF ────────────────────────────────────────────────────
    "disqualified", "did not", "excluded",
    # ── Debris / environmental ────────────────────────────────────────────────
    "debris", "safety",
]

# ---------------------------------------------------------------------------
# Mechanical DNF sub-classifier
# Subset of DNF_KEYWORDS that represent purely mechanical/technical causes.
# Used for dnf_type = "mechanical".
#
# Must stay a superset of any mechanical keyword also in DNF_KEYWORDS.
# When adding a new mechanical keyword to DNF_KEYWORDS, add it here too.
# ---------------------------------------------------------------------------
MECHANICAL_KEYWORDS: list[str] = [
    # ── Powertrain ────────────────────────────────────────────────────────────
    "engine",          # includes "engine misfire", "engine fire"
    "gearbox", "transmission", "clutch", "turbo", "compressor",
    "supercharger", "throttle", "injection", "ignition", "magneto",
    "spark plugs", "distributor", "launch control", "power unit", "ers",
    "exhaust", "vibrations",
    # ── Oil system ────────────────────────────────────────────────────────────
    "oil",             # catches "oil leak", "oil pump", "oil pipe", "oil line",
                       # "oil pressure" — bare keyword intentional, see DNF_KEYWORDS note
    # ── Fuel system ──────────────────────────────────────────────────────────
    # NOTE on "out of fuel": some rows with this status have a finishing position
    # and championship points, meaning the driver was classified despite running
    # dry (push-start or recovered).  classify_dnf_type() correctly assigns
    # dnf_type = "mechanical" for all of them; use positionText / position to
    # determine whether the driver was ultimately a finisher or a DNF.
    "fuel",            # catches "fuel pump", "fuel leak", "fuel pressure",
                       # "fuel pipe", "fuel rig", "out of fuel", "fuel system"
    # ── Cooling / water system ────────────────────────────────────────────────
    "hydraulics", "cooling", "overheating", "radiator",
    "water",           # catches "water pressure", "water pump", "water pipe",
                       # "water leak", "cooling system"
    "heat shield",
    "cooling system",
    # ── Electrical / electronics ─────────────────────────────────────────────
    "electrical", "alternator", "electronics", "battery",
    # ── Suspension / steering / handling ──────────────────────────────────────
    "suspension", "steering", "handling", "brakes",
    # ── Drivetrain / axles ────────────────────────────────────────────────────
    "driveshaft", "differential", "drivetrain", "halfshaft", "axle",
    "cv joint", "track rod",
    # ── Wheels / tyres ────────────────────────────────────────────────────────
    "tyre",            # catches "tyre", "tyre puncture"
    "wheel",           # catches "wheel bearing", "wheel nut", "wheel rim"
    "exhaust", "pneumatic",
    # ── Structural / aero ─────────────────────────────────────────────────────
    "chassis", "broken wing", "front wing", "rear wing", "undertray",
    "brake duct", "crankshaft",
    # ── Misc mechanical catch-alls ────────────────────────────────────────────
    "mechanical", "power loss",
    "fire",            # catches "fire", "engine fire", "heat shield fire"
    "technical",       # generic technical retirement
    "safety belt",     # harness failure
    "refuelling",      # pit equipment failure
    "fuel rig",
]

# ---------------------------------------------------------------------------
# Crash DNF sub-classifier
# ---------------------------------------------------------------------------
CRASH_KEYWORDS: list[str] = [
    "accident",        # includes "fatal accident"
    "collision",       # includes "collision damage"
    "spun off",
    "damage",
    "puncture",
    "eye injury",      # driver injury from debris/crash
    "fatal",           # "fatal accident" — belt-and-braces match
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