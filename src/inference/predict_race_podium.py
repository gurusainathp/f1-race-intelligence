"""
src/inference/predict_race_podium.py
--------------------------------------
Race-level podium predictions.

For each race, ranks all drivers by their predicted podium probability
and surfaces the top 3 as the model's podium picks.

TWO MODES
---------

1. Dataset mode (default)
   Reads from modeling_dataset.parquet — covers all historical races the
   pipeline has processed (typically up to 2024).

2. Fixture mode  ← use this for 2025 races not yet in the dataset
   Reads a user-supplied CSV with one row per driver and the minimum
   pre-race features needed. Rolling in-season features are automatically
   set to 0 (identical to how Round 1 rows are handled during training).

   Run the built-in 2025 Australian GP fixture:
     python src/inference/predict_race_podium.py \
       --fixture data/fixtures/2025_australian_gp.csv

   Run any custom fixture:
     python src/inference/predict_race_podium.py --fixture path/to/fixture.csv

   Required fixture CSV columns:
     driver_name       — free-text, used only for display
     grid_imputed      — qualifying position (1 = pole)
     qualifying_gap_ms — gap to pole in milliseconds (pole = 0)
     best_quali_ms     — driver's best qualifying lap in ms
     grid_pit_lane     — 1 if starting from pit lane, else 0
     prev_season_points      — driver's total points in prior season
     prev_season_podium_rate — driver's podium rate in prior season (0–1)
     has_prev_season   — 1 if driver raced in F1 last season, else 0

   Optional fixture columns (defaults applied if absent):
     race_year    — default 2025
     round        — default 1
     circuitId    — default 1 (Albert Park)
     pit_data_incomplete — default 0

Example output (reports/race_podium_predictions.md):

  ## 2025 Australian GP  ·  Round 1
  | # | Driver | Probability |
  |---|--------|------------:|
  | 1 | Lando Norris | 74% |
  | 2 | Max Verstappen | 68% |
  | 3 | George Russell | 52% |

Usage
-----
  # Predict all test-set races (default, 2023–2024):
  python src/inference/predict_race_podium.py

  # Predict a specific year from the dataset:
  python src/inference/predict_race_podium.py --year 2024

  # Predict a specific race by name substring (case-insensitive):
  python src/inference/predict_race_podium.py --year 2024 --race bahrain

  # 2025 Australian GP via built-in fixture:
  python src/inference/predict_race_podium.py \
    --fixture data/fixtures/2025_australian_gp.csv

  # Choose model (lr | xgb | both):
  python src/inference/predict_race_podium.py --model xgb

  # Include full-field probabilities:
  python src/inference/predict_race_podium.py --full-field

Inputs
------
  models/logistic_regression.pkl
  models/xgboost_podium_model.pkl   (or sklearn_gb_podium_model.pkl)
  data/processed/modeling/modeling_dataset.parquet   ← dataset mode
  data/fixtures/2025_australian_gp.csv               ← fixture mode
  data/processed/master_race_table.csv               ← driver/race names (dataset mode)

Output
------
  reports/race_podium_predictions.md

IMPORTANT NOTE ON ROUND 1 PREDICTIONS
--------------------------------------
At Round 1 all within-season rolling features are 0 by design — the model
has no in-season history yet. It was trained on thousands of Round 1 rows
with the same 0-fill, so this is expected behaviour, not a bug.

The model relies on:
  - Qualifying position / gap (strongest single signal)
  - Prior season points and podium rate
  - Constructor / circuit encoding
  - grid_pit_lane flag

This mirrors how a real analyst would approach a season opener: fall back
entirely on historical form and qualifying pace.
"""

import argparse
import logging
import sys
import warnings
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

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
# Paths
# ---------------------------------------------------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODELING_DATASET_PATH  = _PROJECT_ROOT / "data" / "processed" / "modeling" / "modeling_dataset.parquet"
MASTER_TABLE_PATH      = _PROJECT_ROOT / "data" / "processed" / "master_race_table.csv"
MODELS_DIR             = _PROJECT_ROOT / "models"
REPORT_DIR             = _PROJECT_ROOT / "reports"
DEFAULT_REPORT_PATH    = REPORT_DIR / "race_podium_predictions.md"

# Model file candidates (xgboost first, sklearn fallback)
LR_MODEL_PATH          = MODELS_DIR / "logistic_regression.pkl"
XGB_MODEL_PATHS        = [
    MODELS_DIR / "xgboost_podium_model.pkl",
    MODELS_DIR / "sklearn_gb_podium_model.pkl",
]

# Default: predict test-set seasons
DEFAULT_TEST_MIN_YEAR = 2023

# Fixtures directory (user-supplied CSVs for future races not yet in the dataset)
FIXTURES_DIR = _PROJECT_ROOT / "data" / "fixtures"

# Rolling features that are always 0 at Round 1 / for fixture rows
# (matches the 0-fill applied in build_modeling_dataset.py)
FIXTURE_ROLLING_COLS: list[str] = [
    "rolling_cumulative_points",
    "rolling_podium_rate",
    "rolling_dnf_rate",
    "rolling_avg_finish_position",
    "rolling_avg_qualifying_position",
    "con_rolling_cumulative_points",
    "con_rolling_podium_rate",
    "con_rolling_win_rate",
    "con_rolling_dnf_rate",
    "con_rolling_avg_finish_position",
]

# Fixture CSV columns that map directly to feature columns
FIXTURE_REQUIRED_COLS: list[str] = [
    "driver_name",           # display only — not a model feature
    "grid_imputed",
    "qualifying_gap_ms",
    "best_quali_ms",
    "grid_pit_lane",
    "prev_season_points",
    "prev_season_podium_rate",
    "has_prev_season",
]

FIXTURE_OPTIONAL_DEFAULTS: dict[str, int | float] = {
    "race_year":            2025,
    "round":                1,
    "circuitId":            1,    # Albert Park (Ergast default for Australian GP)
    "pit_data_incomplete":  0,
}

# ---------------------------------------------------------------------------
# Feature columns — must match train_models.py exactly
# ---------------------------------------------------------------------------
FEATURE_COLS: list[str] = [
    "race_year", "round", "circuitId",
    "grid_imputed", "qualifying_gap_ms", "best_quali_ms",
    "rolling_cumulative_points",
    "rolling_podium_rate",
    "rolling_dnf_rate",
    "rolling_avg_finish_position",
    "rolling_avg_qualifying_position",
    "con_rolling_cumulative_points",
    "con_rolling_podium_rate",
    "con_rolling_win_rate",
    "con_rolling_dnf_rate",
    "con_rolling_avg_finish_position",
    "prev_season_points",
    "prev_season_podium_rate",
    "has_prev_season",
    "pit_data_incomplete",
    "grid_pit_lane",
]

TOP_K = 3   # podium spots


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_model(path: Path, label: str):
    if not path.exists():
        raise FileNotFoundError(
            f"{label} model not found at {path}\n"
            "Run train_models.py first."
        )
    model = joblib.load(path)
    log.info("  Loaded %-30s ← %s", label, path.name)
    return model


def _find_gb_model():
    """Find whichever gradient-boosting model file exists."""
    for p in XGB_MODEL_PATHS:
        if p.exists():
            label = "XGBoost" if "xgboost" in p.name else "HistGradientBoosting (sklearn)"
            return _load_model(p, label), label
    raise FileNotFoundError(
        f"No gradient-boosting model found. Tried:\n"
        + "\n".join(f"  {p}" for p in XGB_MODEL_PATHS)
        + "\nRun train_models.py first."
    )


def _load_name_lookup() -> tuple[dict[int, str], dict[int, dict]]:
    """
    Returns:
      driver_names : {driverId -> full_name}
      race_info    : {raceId  -> {name, year, round, date}}
    """
    if not MASTER_TABLE_PATH.exists():
        log.warning(
            "master_race_table.csv not found at %s — "
            "driver and race names will show as IDs.",
            MASTER_TABLE_PATH,
        )
        return {}, {}

    log.info("  Loading name lookup from master_race_table.csv ...")
    master = pd.read_csv(MASTER_TABLE_PATH, low_memory=False)

    # Driver names
    driver_names: dict[int, str] = {}
    name_col = "full_name" if "full_name" in master.columns else None
    ref_col  = "driverRef" if "driverRef" in master.columns else None
    if name_col and "driverId" in master.columns:
        driver_names = (
            master[["driverId", name_col]]
            .dropna(subset=[name_col])
            .drop_duplicates("driverId")
            .set_index("driverId")[name_col]
            .to_dict()
        )
    elif ref_col and "driverId" in master.columns:
        # Fallback: capitalise driverRef
        driver_names = (
            master[["driverId", ref_col]]
            .dropna(subset=[ref_col])
            .drop_duplicates("driverId")
            .set_index("driverId")[ref_col]
            .str.replace("_", " ").str.title()
            .to_dict()
        )

    # Race info
    race_info: dict[int, dict] = {}
    if "raceId" in master.columns:
        race_cols = {
            "name":  "race_name" if "race_name" in master.columns else None,
            "year":  "year"      if "year"      in master.columns else None,
            "round": "round"     if "round"     in master.columns else None,
            "date":  "date"      if "date"      in master.columns else None,
        }
        keep = [c for c in race_cols.values() if c]
        if keep:
            race_sub = (
                master[["raceId"] + keep]
                .drop_duplicates("raceId")
                .set_index("raceId")
            )
            for race_id, row in race_sub.iterrows():
                race_info[int(race_id)] = {
                    "name":  row.get("race_name", f"Race {race_id}"),
                    "year":  int(row["year"]) if "year" in row and pd.notna(row["year"]) else "?",
                    "round": int(row["round"]) if "round" in row and pd.notna(row["round"]) else "?",
                    "date":  str(row["date"])  if "date" in row and pd.notna(row["date"]) else "",
                }

    log.info(
        "  Name lookup ready — %d drivers, %d races",
        len(driver_names), len(race_info),
    )
    return driver_names, race_info


def _driver_label(driver_id: int, driver_names: dict[int, str]) -> str:
    return driver_names.get(driver_id, f"Driver {driver_id}")


def _race_label(race_id: int, race_info: dict[int, dict]) -> str:
    info = race_info.get(race_id)
    if not info:
        return f"Race {race_id}"
    name = str(info.get("name", f"Race {race_id}"))
    # Strip "Grand Prix" → "GP" for conciseness
    name = name.replace("Grand Prix", "GP")
    return name


def _race_title(race_id: int, race_info: dict[int, dict]) -> str:
    info = race_info.get(race_id)
    if not info:
        return f"Race {race_id}"
    year  = info.get("year",  "")
    rnd   = info.get("round", "")
    name  = str(info.get("name", f"Race {race_id}")).replace("Grand Prix", "GP")
    date  = info.get("date",  "")
    parts = [str(year), name]
    sub   = []
    if rnd:
        sub.append(f"Round {rnd}")
    if date:
        sub.append(str(date))
    title = " ".join(p for p in parts if p)
    if sub:
        title += f"  ·  {' | '.join(sub)}"
    return title


# ---------------------------------------------------------------------------
# Core prediction logic
# ---------------------------------------------------------------------------

def predict_race(
    race_id: int,
    race_df: pd.DataFrame,
    models: dict[str, object],
    driver_names: dict[int, str],
    race_info: dict[int, dict],
) -> dict:
    """
    Run all loaded models on a single race's driver rows.
    Returns a dict with race metadata and per-model ranked predictions.
    """
    missing_feats = [c for c in FEATURE_COLS if c not in race_df.columns]
    if missing_feats:
        raise ValueError(f"Race {race_id}: missing feature columns: {missing_feats}")

    X = race_df[FEATURE_COLS]

    race_result = {
        "race_id":    race_id,
        "race_title": _race_title(race_id, race_info),
        "race_label": _race_label(race_id, race_info),
        "year":       race_info.get(race_id, {}).get("year", "?"),
        "round":      race_info.get(race_id, {}).get("round", "?"),
        "date":       race_info.get(race_id, {}).get("date",  ""),
        "n_drivers":  len(race_df),
        "has_actuals": "is_podium" in race_df.columns and race_df["is_podium"].notna().any(),
        "model_predictions": {},
    }

    for model_label, model in models.items():
        probs = model.predict_proba(X)[:, 1]

        ranked = (
            race_df[["driverId"]]
            .copy()
            .assign(
                driver_name = lambda d: d["driverId"].map(
                    lambda i: _driver_label(int(i), driver_names)
                ),
                prob        = probs,
                actual_podium = (
                    race_df["is_podium"].astype(int).values
                    if "is_podium" in race_df.columns
                    else np.zeros(len(race_df), dtype=int)
                ),
            )
            .sort_values("prob", ascending=False)
            .reset_index(drop=True)
        )
        ranked["rank"] = ranked.index + 1

        # Precision@3 for this race
        top3        = ranked.head(TOP_K)
        precision_3 = float(top3["actual_podium"].sum()) / TOP_K if race_result["has_actuals"] else None

        race_result["model_predictions"][model_label] = {
            "ranked":      ranked,
            "top_k":       top3,
            "precision_3": precision_3,
        }

    return race_result


# ---------------------------------------------------------------------------
# Markdown report
# ---------------------------------------------------------------------------

def _hr(char: str = "─", width: int = 60) -> str:
    return char * width


def _render_race_block(race_result: dict, show_full_field: bool = False) -> list[str]:
    """Render one race's predictions as markdown lines."""
    lines: list[str] = []
    has_actuals = race_result["has_actuals"]

    lines += [
        f"## {race_result['race_title']}",
        "",
        f"**Drivers in race:** {race_result['n_drivers']}  ",
        f"**Actuals available:** {'Yes' if has_actuals else 'No (future race)'}",
        "",
    ]

    for model_label, preds in race_result["model_predictions"].items():
        ranked = preds["ranked"]
        top_k  = preds["top_k"]
        p3     = preds["precision_3"]

        lines.append(f"### {model_label}")
        lines.append("")

        # Top-3 podium picks
        lines += [
            f"**Top {TOP_K} Podium Picks:**",
            "",
        ]

        if has_actuals:
            lines += [
                f"| # | Driver | Probability | Actual |",
                f"|---|--------|------------:|--------|",
            ]
            for _, row in top_k.iterrows():
                actual_str = "✅ Podium" if row["actual_podium"] == 1 else "❌ No"
                lines.append(
                    f"| {int(row['rank'])} | {row['driver_name']} "
                    f"| **{row['prob']:.0%}** | {actual_str} |"
                )
            if p3 is not None:
                lines += [
                    "",
                    f"**Precision@3:** {p3:.0%}  "
                    f"({'3/3' if p3 == 1.0 else '2/3' if p3 >= 0.667 else '1/3' if p3 >= 0.334 else '0/3'} correct)",
                ]
        else:
            lines += [
                f"| # | Driver | Probability |",
                f"|---|--------|------------:|",
            ]
            for _, row in top_k.iterrows():
                lines.append(
                    f"| {int(row['rank'])} | {row['driver_name']} "
                    f"| **{row['prob']:.0%}** |"
                )

        # Full field (optional)
        if show_full_field and len(ranked) > TOP_K:
            lines += [
                "",
                "<details>",
                "<summary>Full field probabilities</summary>",
                "",
            ]
            if has_actuals:
                lines += [
                    "| Rank | Driver | Probability | Actual |",
                    "|-----:|--------|------------:|--------|",
                ]
                for _, row in ranked.iterrows():
                    actual_str = "✅" if row["actual_podium"] == 1 else "—"
                    lines.append(
                        f"| {int(row['rank'])} | {row['driver_name']} "
                        f"| {row['prob']:.1%} | {actual_str} |"
                    )
            else:
                lines += [
                    "| Rank | Driver | Probability |",
                    "|-----:|--------|------------:|",
                ]
                for _, row in ranked.iterrows():
                    lines.append(
                        f"| {int(row['rank'])} | {row['driver_name']} "
                        f"| {row['prob']:.1%} |"
                    )
            lines += ["", "</details>"]

        lines.append("")

    lines.append(_hr())
    lines.append("")
    return lines


def _generate_report(
    race_results: list[dict],
    models: dict[str, object],
    year_filter: int | None,
    race_filter: str | None,
    show_full_field: bool,
) -> str:
    timestamp   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    model_names = list(models.keys())
    n_races     = len(race_results)

    # Aggregate Precision@3 per model across all races with actuals
    agg_p3: dict[str, list[float]] = {m: [] for m in model_names}
    for rr in race_results:
        for m, preds in rr["model_predictions"].items():
            if preds["precision_3"] is not None:
                agg_p3[m].append(preds["precision_3"])

    sections: list[str] = []

    # ── Header ────────────────────────────────────────────────────────────────
    filter_desc = []
    if year_filter:
        filter_desc.append(f"Year = {year_filter}")
    if race_filter:
        filter_desc.append(f'Race filter = "{race_filter}"')
    if not filter_desc:
        filter_desc.append("Default: test set (2023–2024)")

    header_lines = [
        "# F1 Race-Level Podium Predictions",
        "",
        f"> **Generated:** {timestamp}  ",
        f"> **Filter:** {' | '.join(filter_desc)}  ",
        f"> **Races:** {n_races}  ",
        f"> **Models:** {', '.join(model_names)}  ",
        f"> **Task:** Predict the 3 most likely podium finishers per race  ",
        "",
        _hr(),
        "",
    ]
    sections.append("\n".join(header_lines))

    # ── Summary table ─────────────────────────────────────────────────────────
    summary_lines = [
        "## Summary — Precision@3 Across All Races",
        "",
        "> Precision@3: fraction of the model's top-3 picks that actually finished on the podium.",
        "> Averaged across all races where actual results are available.",
        "> Maximum possible = 1.00 (all 3 picks correct every race).",
        "",
        "| Model | Races Evaluated | Mean Precision@3 | Best Race | Worst Race |",
        "|-------|----------------:|-----------------:|----------:|----------:|",
    ]
    for m in model_names:
        vals = agg_p3[m]
        if vals:
            mean_p3  = np.mean(vals)
            best_p3  = max(vals)
            worst_p3 = min(vals)
            summary_lines.append(
                f"| {m} | {len(vals)} | {mean_p3:.2%} | {best_p3:.0%} | {worst_p3:.0%} |"
            )
        else:
            summary_lines.append(f"| {m} | 0 | N/A (no actuals) | — | — |")
    summary_lines += ["", _hr(), ""]
    sections.append("\n".join(summary_lines))

    # ── Per-race blocks ───────────────────────────────────────────────────────
    for rr in race_results:
        sections.append("\n".join(_render_race_block(rr, show_full_field=show_full_field)))

    # ── Footer ────────────────────────────────────────────────────────────────
    sections.append("\n".join([
        _hr(),
        "",
        "_Generated by `predict_race_podium.py`.  ",
        "Re-run after retraining to refresh predictions._",
    ]))

    return "\n".join(sections)



# ---------------------------------------------------------------------------
# Fixture loader — for races not yet in the modeling dataset
# ---------------------------------------------------------------------------

def _load_fixture(fixture_path: Path) -> tuple[pd.DataFrame, dict, dict]:
    """
    Load a user-supplied fixture CSV representing a single future race.

    Returns
    -------
    df          : DataFrame ready for predict_race() — all FEATURE_COLS present
    driver_names: {synthetic_id -> driver_name}  for display
    race_info   : {synthetic_race_id -> {name, year, round, date}}
    """
    if not fixture_path.exists():
        raise FileNotFoundError(
            f"Fixture CSV not found: {fixture_path}\n"
            "Check the path or create the file using the template in data/fixtures/."
        )

    log.info("  Loading fixture: %s", fixture_path.name)
    fix = pd.read_csv(fixture_path)

    # Validate required columns
    missing = [c for c in FIXTURE_REQUIRED_COLS if c not in fix.columns]
    if missing:
        raise ValueError(
            f"Fixture CSV is missing required columns: {missing}\n"
            f"Required: {FIXTURE_REQUIRED_COLS}"
        )

    # Apply optional column defaults
    for col, default_val in FIXTURE_OPTIONAL_DEFAULTS.items():
        if col not in fix.columns:
            fix[col] = default_val
            log.info("    Applied default: %s = %s", col, default_val)

    # Set all rolling features to 0 (Round 1 / no in-season history)
    for col in FIXTURE_ROLLING_COLS:
        fix[col] = 0.0
    log.info("    Set %d rolling feature cols to 0 (Round 1 / no in-season history)", len(FIXTURE_ROLLING_COLS))

    # Assign synthetic IDs so predict_race() works unchanged
    SYNTHETIC_RACE_ID = 99999
    fix["raceId"]    = SYNTHETIC_RACE_ID
    fix["driverId"]  = range(9000, 9000 + len(fix))   # synthetic, display-only
    fix["is_podium"] = np.nan                          # no actuals for future race

    # Build name lookup from the driver_name column
    driver_names = dict(zip(fix["driverId"].tolist(), fix["driver_name"].tolist()))

    # Infer race metadata from the fixture columns
    year  = int(fix["race_year"].iloc[0])
    rnd   = int(fix["round"].iloc[0])
    # Try to read race name from optional column, else derive from filename
    if "race_name" in fix.columns:
        race_name = str(fix["race_name"].iloc[0])
    else:
        # e.g. "2025_australian_gp.csv" → "Australian GP"
        stem      = fixture_path.stem                          # "2025_australian_gp"
        parts     = stem.split("_")[1:]                        # ["australian", "gp"]
        race_name = " ".join(p.capitalize() for p in parts)   # "Australian Gp" → "Australian GP"
        race_name = race_name.replace(" Gp", " GP")

    date_str = str(fix["date"].iloc[0]) if "date" in fix.columns else ""

    race_info = {
        SYNTHETIC_RACE_ID: {
            "name":  race_name,
            "year":  year,
            "round": rnd,
            "date":  date_str,
        }
    }

    log.info(
        "  Fixture loaded: %d drivers | %s Round %d %d",
        len(fix), race_name, rnd, year,
    )

    # Validate all feature columns are present
    missing_feats = [c for c in FEATURE_COLS if c not in fix.columns]
    if missing_feats:
        raise ValueError(
            f"After applying defaults and rolling fills, fixture is still missing "
            f"feature columns: {missing_feats}\nCheck that your CSV has all required columns."
        )

    return fix, driver_names, race_info


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _print_console_preview(last: dict, report_path: Path) -> None:
    """Print a compact console summary for the last (or only) race."""
    print(f"\n{'─' * 55}")
    print(f"  {last['race_title']}")
    print(f"{'─' * 55}")
    for model_label, preds in last["model_predictions"].items():
        print(f"\n  {model_label} — Top {TOP_K} Podium Picks:")
        for _, row in preds["top_k"].iterrows():
            prob_bar = "█" * int(row["prob"] * 20)
            actual   = ""
            if last["has_actuals"]:
                actual = "  ✅" if row["actual_podium"] == 1 else "  ❌"
            print(f"    {int(row['rank'])}. {row['driver_name']:<25} {row['prob']:.0%}  {prob_bar}{actual}")
        if preds["precision_3"] is not None:
            print(f"    Precision@3: {preds['precision_3']:.0%}")
    print(f"\n  Full report → {report_path}\n")


def run(
    year_filter: int | None    = None,
    race_filter: str | None    = None,
    model_choice: str          = "both",
    report_path: Path          = DEFAULT_REPORT_PATH,
    show_full_field: bool      = False,
    fixture_path: Path | None  = None,
) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    log.info("=" * 55)
    log.info("F1 RACE-LEVEL PODIUM PREDICTIONS")
    log.info("=" * 55)

    # ── Load models ───────────────────────────────────────────────────────────
    log.info("Loading models ...")
    models: dict[str, object] = {}

    if model_choice in ("lr", "both"):
        models["Logistic Regression"] = _load_model(LR_MODEL_PATH, "Logistic Regression")

    if model_choice in ("xgb", "both"):
        gb_model, gb_label = _find_gb_model()
        models[gb_label]   = gb_model

    if not models:
        log.error("No models loaded. Specify --model lr, xgb, or both.")
        sys.exit(1)

    # ── FIXTURE MODE — bypass historical dataset entirely ─────────────────────
    if fixture_path is not None:
        log.info("FIXTURE MODE — loading from %s", fixture_path)
        fix_df, driver_names, race_info = _load_fixture(Path(fixture_path))

        SYNTHETIC_RACE_ID = 99999
        race_results: list[dict] = []
        result = predict_race(SYNTHETIC_RACE_ID, fix_df, models, driver_names, race_info)
        race_results.append(result)

        log.info("Writing markdown report ...")
        report_md = _generate_report(
            race_results, models,
            year_filter  = None,
            race_filter  = None,
            show_full_field = show_full_field,
        )
        report_path.write_text(report_md, encoding="utf-8")
        log.info("  Saved → %s", report_path)

        # Console preview
        _print_console_preview(race_results[-1], report_path)
        return

    # ── DATASET MODE ──────────────────────────────────────────────────────────
    log.info("Loading modeling dataset ...")
    if not MODELING_DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Modeling dataset not found at {MODELING_DATASET_PATH}\n"
            "Run build_modeling_dataset.py first."
        )
    df = pd.read_parquet(MODELING_DATASET_PATH)
    log.info("  Loaded: %d rows × %d cols", *df.shape)

    driver_names, race_info = _load_name_lookup()

    # ── Filter races ──────────────────────────────────────────────────────────
    if year_filter:
        df = df[df["race_year"] == year_filter]
        log.info("  Filtered to year %d: %d rows", year_filter, len(df))
    else:
        # Default: test set only (future-season predictions)
        df = df[df["race_year"] >= DEFAULT_TEST_MIN_YEAR]
        log.info(
            "  Using default test set (race_year >= %d): %d rows",
            DEFAULT_TEST_MIN_YEAR, len(df),
        )

    if len(df) == 0:
        log.error("No rows remaining after year filter. Check --year argument.")
        sys.exit(1)

    if race_filter:
        matched_race_ids = {
            rid for rid, info in race_info.items()
            if race_filter.lower() in str(info.get("name", "")).lower()
        }
        df = df[df["raceId"].isin(matched_race_ids)]
        log.info(
            "  Filtered to races matching '%s': %d rows (%d races)",
            race_filter, len(df), df["raceId"].nunique(),
        )
        if len(df) == 0:
            log.error(
                "No races matched '%s'. "
                "Try a shorter substring, e.g. 'bahrain', 'monaco', 'british'.",
                race_filter,
            )
            sys.exit(1)

    # ── Predict per race ──────────────────────────────────────────────────────
    race_ids = sorted(df["raceId"].unique())
    log.info("Running predictions for %d races ...", len(race_ids))

    race_results = []
    for race_id in race_ids:
        race_df = df[df["raceId"] == race_id].copy()
        try:
            result = predict_race(race_id, race_df, models, driver_names, race_info)
            race_results.append(result)
        except Exception as exc:
            log.warning("  Skipped race %d — %s", race_id, exc)

    if not race_results:
        log.error("No races were successfully predicted.")
        sys.exit(1)

    log.info("  Predictions complete: %d races", len(race_results))

    # ── Write report ──────────────────────────────────────────────────────────
    log.info("Writing markdown report ...")
    report_md = _generate_report(
        race_results, models, year_filter, race_filter, show_full_field
    )
    report_path.write_text(report_md, encoding="utf-8")
    log.info("  Saved → %s", report_path)

    _print_console_preview(race_results[-1], report_path)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Predict F1 podium finishers per race.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Historical races from the dataset:
  python src/inference/predict_race_podium.py
  python src/inference/predict_race_podium.py --year 2024
  python src/inference/predict_race_podium.py --year 2024 --race bahrain

  # Future race via fixture CSV (e.g. 2025 Australian GP):
  python src/inference/predict_race_podium.py \\
    --fixture data/fixtures/2025_australian_gp.csv

  # Options:
  python src/inference/predict_race_podium.py --model xgb --full-field
        """,
    )
    parser.add_argument(
        "--fixture", type=Path, default=None,
        help=(
            "Path to a fixture CSV for a race not yet in the dataset (e.g. 2025 R1). "
            "See data/fixtures/2025_australian_gp.csv for the template. "
            "When provided, --year and --race are ignored."
        ),
    )
    parser.add_argument(
        "--year", type=int, default=None,
        help="Filter to a specific season (e.g. 2024). Default: all test-set races.",
    )
    parser.add_argument(
        "--race", type=str, default=None,
        help="Filter to races whose name contains this substring (case-insensitive). "
             "E.g. 'bahrain', 'monaco', 'british'.",
    )
    parser.add_argument(
        "--model", choices=["lr", "xgb", "both"], default="both",
        help="Which model(s) to use. Default: both.",
    )
    parser.add_argument(
        "--output", type=Path, default=DEFAULT_REPORT_PATH,
        help=f"Output markdown path. Default: {DEFAULT_REPORT_PATH}",
    )
    parser.add_argument(
        "--full-field", action="store_true",
        help="Include collapsible full-field probability table for every race.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    run(
        fixture_path    = args.fixture,
        year_filter     = args.year,
        race_filter     = args.race,
        model_choice    = args.model,
        report_path     = args.output,
        show_full_field = args.full_field,
    )