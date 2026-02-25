"""
Data ingestion module for F1 Race Intelligence System.

Downloads dataset from Kaggle and stores selected CSV files
into data/raw directory in a structured way.
"""

import shutil
from pathlib import Path
import kagglehub

from src.config import CONFIG


REQUIRED_FILES = [
    "circuits.csv",
    "drivers.csv",
    "races.csv",
    "results.csv",
    "qualifying.csv",
    "lap_times.csv",
    "pit_stops.csv",
    "constructors.csv",
    "status.csv",
]


def download_dataset() -> Path:
    """
    Download dataset using kagglehub.

    Returns:
        Path: Local path to downloaded dataset.
    """
    print("Downloading F1 dataset from Kaggle...")
    dataset_path = kagglehub.dataset_download(
        "rohanrao/formula-1-world-championship-1950-2020"
    )
    print(f"Dataset downloaded to: {dataset_path}")
    return Path(dataset_path)


def ensure_raw_directory() -> Path:
    """
    Ensure raw data directory exists.

    Returns:
        Path: Raw data directory path.
    """
    raw_dir = Path(CONFIG["paths"]["raw_data"])
    raw_dir.mkdir(parents=True, exist_ok=True)
    return raw_dir


def move_required_files(source_path: Path, destination_path: Path) -> None:
    """
    Move only required CSV files into data/raw.

    Args:
        source_path (Path): Path to downloaded dataset.
        destination_path (Path): data/raw directory.
    """
    print("Moving required CSV files to data/raw...")

    for file_name in REQUIRED_FILES:
        source_file = source_path / file_name
        dest_file = destination_path / file_name

        if not source_file.exists():
            print(f"Warning: {file_name} not found in dataset.")
            continue

        shutil.copy2(source_file, dest_file)
        print(f"Copied: {file_name}")

    print("Data ingestion completed successfully.")


def run_data_ingestion():
    """
    Complete pipeline to download and store dataset.
    """
    dataset_path = download_dataset()
    raw_dir = ensure_raw_directory()
    move_required_files(dataset_path, raw_dir)


if __name__ == "__main__":
    run_data_ingestion()