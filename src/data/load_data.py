"""
src/data/load_data.py
---------------------
Data ingestion module for the F1 Race Intelligence System.

Downloads the Formula 1 dataset from Kaggle via kagglehub and copies
the required CSV files into data/raw/ for downstream cleaning.

Requires:
  - kagglehub installed  (pip install kagglehub)
  - Kaggle API credentials configured:
      ~/.kaggle/kaggle.json  OR  KAGGLE_USERNAME / KAGGLE_KEY env vars

Run from the project root:
  python src/data/load_data.py

Or as a module:
  python -m src.data.load_data
"""

import logging
import shutil
import sys
from pathlib import Path

import kagglehub

# ---------------------------------------------------------------------------
# Path-safe config import
# ---------------------------------------------------------------------------
# Supports three invocation styles without requiring PYTHONPATH to be set:
#   1. python src/data/load_data.py          (direct run from project root)
#   2. python -m src.data.load_data          (module run from project root)
#   3. import from another module in src/    (standard import)
#
# We resolve the project root as two levels above this file's location
# (src/data/load_data.py  ->  project root) and insert it into sys.path
# only if it isn't already there.
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from src.config import CONFIG  # noqa: E402  (import after sys.path fix)

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
# Dataset identifier
# ---------------------------------------------------------------------------
KAGGLE_DATASET = "rohanrao/formula-1-world-championship-1950-2020"

REQUIRED_FILES = [
    "circuits.csv",
    "constructors.csv",
    "drivers.csv",
    "lap_times.csv",
    "pit_stops.csv",
    "qualifying.csv",
    "races.csv",
    "results.csv",
    "status.csv",
]


# ===========================================================================
# Steps
# ===========================================================================

def download_dataset() -> Path:
    """
    Download the F1 dataset from Kaggle via kagglehub.

    kagglehub caches downloads locally — re-running this when the dataset
    has not changed is a fast no-op (returns the cached path immediately).

    Returns:
        Path to the directory containing the downloaded CSV files.

    Raises:
        RuntimeError: If the download fails or returns an empty path.
    """
    log.info("Downloading F1 dataset: %s", KAGGLE_DATASET)
    try:
        dataset_path = kagglehub.dataset_download(KAGGLE_DATASET)
    except Exception as exc:
        raise RuntimeError(
            f"Kaggle download failed: {exc}\n"
            "Ensure kaggle.json is at ~/.kaggle/kaggle.json or "
            "KAGGLE_USERNAME / KAGGLE_KEY env vars are set."
        ) from exc

    path = Path(dataset_path)
    if not path.exists():
        raise RuntimeError(f"kagglehub returned a path that does not exist: {path}")

    log.info("Dataset available at: %s", path)
    return path


def ensure_raw_directory() -> Path:
    """
    Create data/raw/ if it does not already exist.

    Returns:
        Path to the raw data directory.
    """
    raw_dir = Path(CONFIG["paths"]["raw_data"])
    raw_dir.mkdir(parents=True, exist_ok=True)
    log.info("Raw data directory: %s", raw_dir.resolve())
    return raw_dir


def copy_required_files(source_path: Path, dest_path: Path) -> list[str]:
    """
    Copy only the required CSV files from the download cache to data/raw/.

    Skips files that are already present and identical in size to avoid
    unnecessary I/O on repeated runs (idempotent).

    Args:
        source_path: Directory containing the downloaded CSVs.
        dest_path:   data/raw/ directory.

    Returns:
        List of file names that were actually copied (empty if all up-to-date).

    Raises:
        FileNotFoundError: If any required file is missing from the download.
    """
    copied  = []
    skipped = []
    missing = []

    for file_name in REQUIRED_FILES:
        src  = source_path / file_name
        dest = dest_path   / file_name

        if not src.exists():
            missing.append(file_name)
            continue

        # Skip copy if destination already exists with the same size
        if dest.exists() and dest.stat().st_size == src.stat().st_size:
            skipped.append(file_name)
            continue

        shutil.copy2(src, dest)
        copied.append(file_name)
        log.info("  Copied  : %s  (%s)", file_name, _human_size(src.stat().st_size))

    if skipped:
        log.info("  Skipped (already up-to-date): %s", ", ".join(skipped))

    if missing:
        raise FileNotFoundError(
            f"The following required files were not found in the downloaded dataset:\n"
            f"  {', '.join(missing)}\n"
            f"Source path: {source_path}\n"
            f"Available files: {[f.name for f in source_path.glob('*.csv')]}"
        )

    return copied


def validate_raw_files(raw_dir: Path) -> None:
    """
    Quick sanity check — verify all required files landed in data/raw/
    and are non-empty.

    Raises:
        RuntimeError: If any file is missing or empty.
    """
    problems = []
    for file_name in REQUIRED_FILES:
        path = raw_dir / file_name
        if not path.exists():
            problems.append(f"Missing : {file_name}")
        elif path.stat().st_size == 0:
            problems.append(f"Empty   : {file_name}")

    if problems:
        raise RuntimeError(
            "Raw data validation failed:\n" + "\n".join(f"  {p}" for p in problems)
        )

    log.info("Validation passed — all %d required files present.", len(REQUIRED_FILES))


# ===========================================================================
# Helpers
# ===========================================================================

def _human_size(n_bytes: int) -> str:
    """Return a human-readable file size string."""
    for unit in ("B", "KB", "MB", "GB"):
        if n_bytes < 1024:
            return f"{n_bytes:.1f} {unit}"
        n_bytes /= 1024
    return f"{n_bytes:.1f} TB"


# ===========================================================================
# Orchestrator
# ===========================================================================

def run_data_ingestion() -> None:
    """
    Full ingestion pipeline:
      1. Download dataset from Kaggle (cached if unchanged)
      2. Ensure data/raw/ exists
      3. Copy required CSV files (skips up-to-date files)
      4. Validate all required files are present and non-empty
    """
    log.info("=" * 55)
    log.info("F1 Data Ingestion")
    log.info("=" * 55)

    dataset_path = download_dataset()
    raw_dir      = ensure_raw_directory()
    copied       = copy_required_files(dataset_path, raw_dir)

    if copied:
        log.info("%d file(s) copied to %s", len(copied), raw_dir)
    else:
        log.info("All files already up-to-date in %s — nothing copied.", raw_dir)

    validate_raw_files(raw_dir)

    log.info("=" * 55)
    log.info("Ingestion complete. Next step: python src/data/clean_data.py")
    log.info("=" * 55)


# ===========================================================================
# Entry point
# ===========================================================================

if __name__ == "__main__":
    run_data_ingestion()