"""
Exposes the primary functions from the modeling subpackage
so they can be imported directly from `src.modeling`.

Usage:
------
  from src.modeling import build_modeling_dataset
  from src.modeling import generate_report

  df = build_modeling_dataset()
  validation_passed = generate_report()
"""
from .build_modeling_dataset import build_modeling_dataset
from .validation_modeling_data import generate_report

__all__ = [
    "build_modeling_dataset",
    "generate_report",
]