"""
Configuration loader for F1 Race Intelligence System
"""

from pathlib import Path
import yaml


# Root directory (project root)
ROOT_DIR = Path(__file__).resolve().parent.parent


def load_config(config_path: str = "config.yaml") -> dict:
    """
    Load YAML configuration file.

    Args:
        config_path (str): Path to config file relative to project root.

    Returns:
        dict: Parsed configuration dictionary.
    """
    config_file = ROOT_DIR / config_path

    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_file}")

    with open(config_file, "r") as file:
        config = yaml.safe_load(file)

    return config


# Load once globally (optional convenience)
CONFIG = load_config()