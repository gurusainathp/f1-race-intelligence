"""
src/modeling/train_models.py
-----------------------------
Train and evaluate two models for predicting `is_podium`.

Task
----
  Binary classification: will this driver finish on the podium? (Yes / No)
  Target: is_podium (1 = podium, 0 = no podium)

Models
------
  1. Logistic Regression   — baseline, interpretable, coefficient analysis
  2. XGBoost               — main model, handles nonlinear racing dynamics

Time-based split (NO random shuffle — simulates predicting future seasons)
--------------------------------------------------------------------------
  Train      : race_year 2000 – 2019  (20 seasons)
  Validation : race_year 2020 – 2022  (3 seasons, hyperparameter reference)
  Test        : race_year 2023 – 2024  (2 seasons, held-out final evaluation)

Evaluation metrics
------------------
  Primary  : ROC-AUC
  Also     : Precision, Recall, F1, Precision@3 (3 podium spots per race)
  Reports  : Classification report + confusion matrix + Precision@3 table

Outputs
-------
  models/logistic_regression.pkl
  models/xgboost_podium_model.pkl    (or sklearn_gb_podium_model.pkl if xgboost absent)
  reports/model_evaluation.md

Run
---
  python src/modeling/train_models.py
"""

import logging
import sys
import warnings
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

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

MODELING_DATASET_PATH = _PROJECT_ROOT / "data" / "processed" / "modeling" / "modeling_dataset.parquet"
MODELS_DIR            = _PROJECT_ROOT / "models"
REPORT_DIR            = _PROJECT_ROOT / "reports"
REPORT_PATH           = REPORT_DIR / "model_evaluation.md"

# ---------------------------------------------------------------------------
# Feature groups (per lead sign-off — 21 features total)
# ---------------------------------------------------------------------------
FEATURE_COLS: list[str] = [
    # Race context
    "race_year", "round", "circuitId",
    # Starting performance
    "grid_imputed", "qualifying_gap_ms", "best_quali_ms",
    # Driver form (rolling within-season, shift-1 applied)
    "rolling_cumulative_points",
    "rolling_podium_rate",
    "rolling_dnf_rate",
    "rolling_avg_finish_position",
    "rolling_avg_qualifying_position",
    # Constructor form
    "con_rolling_cumulative_points",
    "con_rolling_podium_rate",
    "con_rolling_win_rate",
    "con_rolling_dnf_rate",
    "con_rolling_avg_finish_position",
    # Experience
    "prev_season_points",
    "prev_season_podium_rate",
    "has_prev_season",
    # Race conditions
    "pit_data_incomplete",
    "grid_pit_lane",
]

TARGET = "is_podium"

# Time-based split boundaries
TRAIN_MAX_YEAR = 2019
VAL_MIN_YEAR   = 2020
VAL_MAX_YEAR   = 2022
TEST_MIN_YEAR  = 2023

# Precision@K — number of podium spots per race
K = 3


# ---------------------------------------------------------------------------
# XGBoost import — graceful fallback to sklearn HistGradientBoosting
# ---------------------------------------------------------------------------
try:
    from xgboost import XGBClassifier
    _XGB_AVAILABLE = True
    GB_MODEL_NAME  = "xgboost_podium_model"
    log.info("XGBoost available ✅")
except ImportError:
    from sklearn.ensemble import HistGradientBoostingClassifier as _HGBC
    _XGB_AVAILABLE = False
    GB_MODEL_NAME  = "sklearn_gb_podium_model"
    log.warning(
        "xgboost not installed — using sklearn HistGradientBoostingClassifier as substitute. "
        "Install xgboost with: pip install xgboost"
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_dataset() -> pd.DataFrame:
    if not MODELING_DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Modeling dataset not found at {MODELING_DATASET_PATH}\n"
            "Run build_modeling_dataset.py first."
        )
    df = pd.read_parquet(MODELING_DATASET_PATH)
    log.info("Loaded dataset: %d rows × %d cols", *df.shape)
    return df


def _time_split(df: pd.DataFrame) -> tuple[
    pd.DataFrame, pd.Series,
    pd.DataFrame, pd.Series,
    pd.DataFrame, pd.Series,
    pd.DataFrame,
]:
    """
    Split into train / val / test by race_year.
    Also returns the full test DataFrame (with raceId, driverId) for Precision@3.
    """
    train_mask = df["race_year"] <= TRAIN_MAX_YEAR
    val_mask   = (df["race_year"] >= VAL_MIN_YEAR) & (df["race_year"] <= VAL_MAX_YEAR)
    test_mask  = df["race_year"] >= TEST_MIN_YEAR

    missing = [c for c in FEATURE_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing feature columns in dataset: {missing}")

    X_train = df.loc[train_mask, FEATURE_COLS]
    y_train = df.loc[train_mask, TARGET]
    X_val   = df.loc[val_mask,   FEATURE_COLS]
    y_val   = df.loc[val_mask,   TARGET]
    X_test  = df.loc[test_mask,  FEATURE_COLS]
    y_test  = df.loc[test_mask,  TARGET]
    test_df = df.loc[test_mask].copy()   # full rows — needed for Precision@3

    log.info(
        "Split — Train: %d rows (%d–%d) | Val: %d rows (%d–%d) | Test: %d rows (%d–%d)",
        len(X_train), TRAIN_MAX_YEAR - 19, TRAIN_MAX_YEAR,
        len(X_val),   VAL_MIN_YEAR,  VAL_MAX_YEAR,
        len(X_test),  TEST_MIN_YEAR, int(df["race_year"].max()),
    )
    log.info(
        "Class balance — Train: %.1f%% podium | Val: %.1f%% | Test: %.1f%%",
        y_train.mean() * 100, y_val.mean() * 100, y_test.mean() * 100,
    )

    return X_train, y_train, X_val, y_val, X_test, y_test, test_df


def _precision_at_k(test_df: pd.DataFrame, prob_col: str, k: int = K) -> float:
    """
    Precision@K: for each race, take the top-K drivers by predicted probability.
    Precision = fraction of those top-K that actually finished on the podium.
    Averaged across all races in the test set.
    """
    if "raceId" not in test_df.columns:
        return float("nan")

    race_precisions: list[float] = []
    for _, race in test_df.groupby("raceId"):
        top_k    = race.nlargest(k, prob_col)
        prec     = top_k[TARGET].sum() / k
        race_precisions.append(prec)

    return float(np.mean(race_precisions)) if race_precisions else float("nan")


def _evaluate(
    name: str,
    model,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    test_df: pd.DataFrame,
    prob_col: str = "_prob",
) -> dict:
    """
    Run full evaluation suite and return a metrics dict.
    """
    y_pred  = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    auc     = roc_auc_score(y_test, y_proba)
    report  = classification_report(y_test, y_pred, output_dict=True)
    cm      = confusion_matrix(y_test, y_pred)

    # Attach predicted probabilities to test_df for Precision@3
    test_df_copy            = test_df.copy()
    test_df_copy[prob_col]  = y_proba
    p_at_k                  = _precision_at_k(test_df_copy, prob_col, K)

    podium_metrics = report.get("1", report.get(1, {}))
    precision  = podium_metrics.get("precision", float("nan"))
    recall     = podium_metrics.get("recall",    float("nan"))
    f1         = podium_metrics.get("f1-score",  float("nan"))

    log.info("─" * 55)
    log.info("%-25s  ROC-AUC : %.4f", name, auc)
    log.info("%-25s  P@%d     : %.4f", name, K, p_at_k)
    log.info("%-25s  Precision: %.4f  Recall: %.4f  F1: %.4f",
             name, precision, recall, f1)
    log.info("Confusion matrix (TN FP / FN TP):\n%s", cm)

    return {
        "name":       name,
        "auc":        auc,
        "precision":  precision,
        "recall":     recall,
        "f1":         f1,
        "p_at_k":     p_at_k,
        "cm":         cm,
        "report":     report,
        "y_proba":    y_proba,
        "y_pred":     y_pred,
    }


# ---------------------------------------------------------------------------
# Model builders
# ---------------------------------------------------------------------------

def _build_logistic_regression() -> Pipeline:
    """
    Logistic Regression pipeline with StandardScaler.
    class_weight='balanced' compensates for the ~14% podium rate.
    max_iter=1000 ensures convergence on 21 features.
    """
    return Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(
            class_weight="balanced",
            max_iter=1000,
            random_state=42,
            solver="lbfgs",
            C=0.1,       # moderate regularisation — prevents overfitting on cumulative stats
        )),
    ])


def _build_gradient_boosting():
    """
    XGBoost if available, else sklearn HistGradientBoostingClassifier.
    scale_pos_weight compensates for class imbalance (~6:1 ratio).
    """
    if _XGB_AVAILABLE:
        return XGBClassifier(
            n_estimators=400,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            scale_pos_weight=6,    # approx non_podium / podium ratio
            eval_metric="auc",
            random_state=42,
            verbosity=0,
            use_label_encoder=False,
        )
    else:
        return _HGBC(
            max_iter=400,
            max_depth=4,
            learning_rate=0.05,
            class_weight="balanced",
            random_state=42,
        )


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def _hr(char: str = "─", width: int = 60) -> str:
    return char * width


def _cm_table(cm: np.ndarray) -> str:
    """Render confusion matrix as a markdown table."""
    tn, fp, fn, tp = cm.ravel()
    lines = [
        "| | Predicted: No Podium | Predicted: Podium |",
        "|---|---:|---:|",
        f"| **Actual: No Podium** | {tn:,} (TN) | {fp:,} (FP) |",
        f"| **Actual: Podium**    | {fn:,} (FN) | {tp:,} (TP) |",
    ]
    return "\n".join(lines)


def _coef_table(model: Pipeline, top_n: int = 15) -> str:
    """Extract top-N logistic regression coefficients."""
    coefs = model.named_steps["clf"].coef_[0]
    pairs = sorted(zip(FEATURE_COLS, coefs), key=lambda x: abs(x[1]), reverse=True)[:top_n]
    lines = [
        f"| Rank | Feature | Coefficient | Direction |",
        "|-----:|---------|------------:|----------|",
    ]
    for i, (feat, coef) in enumerate(pairs, 1):
        direction = "📈 Increases podium prob" if coef > 0 else "📉 Decreases podium prob"
        lines.append(f"| {i} | `{feat}` | {coef:+.4f} | {direction} |")
    return "\n".join(lines)


def _xgb_importance_table(model, top_n: int = 15) -> str:
    """Extract top-N XGBoost feature importances."""
    if _XGB_AVAILABLE:
        importances = model.feature_importances_
    else:
        importances = model.feature_importances_

    pairs = sorted(zip(FEATURE_COLS, importances), key=lambda x: x[1], reverse=True)[:top_n]
    lines = [
        "| Rank | Feature | Importance |",
        "|-----:|---------|----------:|",
    ]
    for i, (feat, imp) in enumerate(pairs, 1):
        bar = "█" * max(1, int(imp * 100))
        lines.append(f"| {i} | `{feat}` | {imp:.4f} {bar} |")
    return "\n".join(lines)


def _generate_report(
    lr_metrics: dict,
    gb_metrics: dict,
    lr_model: Pipeline,
    gb_model,
    split_info: dict,
) -> str:
    timestamp  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    gb_label   = "XGBoost" if _XGB_AVAILABLE else "HistGradientBoosting (sklearn)"

    sections = []

    # ── Header ────────────────────────────────────────────────────────────────
    sections.append("\n".join([
        "# F1 Podium Prediction — Model Evaluation Report",
        "",
        f"> **Generated:** {timestamp}",
        f"> **Task:** Binary classification — `is_podium` (1 = podium, 0 = no podium)",
        f"> **Features:** {len(FEATURE_COLS)}",
        f"> **Train:** {split_info['n_train']:,} rows  "
        f"({split_info['train_years']})",
        f"> **Val:** {split_info['n_val']:,} rows  "
        f"({split_info['val_years']})",
        f"> **Test:** {split_info['n_test']:,} rows  "
        f"({split_info['test_years']})",
        f"> **Podium rate (test):** {split_info['test_podium_rate']:.1%}",
        "",
        _hr(),
    ]))

    # ── Model Comparison ──────────────────────────────────────────────────────
    sections.append("\n".join([
        "## 0. Model Comparison Summary",
        "",
        f"| Metric | Logistic Regression | {gb_label} |",
        "|--------|--------------------:|" + "-" * 22 + ":|",
        f"| **ROC-AUC** | **{lr_metrics['auc']:.4f}** | **{gb_metrics['auc']:.4f}** |",
        f"| Precision@{K} | {lr_metrics['p_at_k']:.4f} | {gb_metrics['p_at_k']:.4f} |",
        f"| Precision (podium) | {lr_metrics['precision']:.4f} | {gb_metrics['precision']:.4f} |",
        f"| Recall (podium) | {lr_metrics['recall']:.4f} | {gb_metrics['recall']:.4f} |",
        f"| F1 (podium) | {lr_metrics['f1']:.4f} | {gb_metrics['f1']:.4f} |",
        "",
        "> **ROC-AUC** is the primary metric. Random baseline = 0.50.",
        f"> **Precision@{K}**: fraction of the top-{K} predicted drivers per race "
        f"that actually finished on the podium. Max = 1.0.",
    ]))

    # ── Split Info ─────────────────────────────────────────────────────────────
    sections.append("\n".join([
        "## 1. Dataset Split",
        "",
        "Time-based split — no data leakage across seasons.",
        "",
        "| Split | Years | Rows | Podium % |",
        "|-------|-------|-----:|---------:|",
        f"| Train | {split_info['train_years']} | {split_info['n_train']:,} | {split_info['train_podium_rate']:.1%} |",
        f"| Val   | {split_info['val_years']}   | {split_info['n_val']:,}   | {split_info['val_podium_rate']:.1%} |",
        f"| Test  | {split_info['test_years']}  | {split_info['n_test']:,}  | {split_info['test_podium_rate']:.1%} |",
        "",
        "> Validation set is used as a reference only. ",
        "> Final evaluation is reported on the **test set** exclusively.",
    ]))

    # ── Logistic Regression ───────────────────────────────────────────────────
    sections.append("\n".join([
        "## 2. Logistic Regression (Baseline)",
        "",
        "**Purpose:** Interpretable baseline. Coefficients reveal feature direction.",
        "**Scaling:** StandardScaler applied (required for regularised LR).",
        "**Class weight:** balanced (compensates for ~14% podium rate).",
        "",
        "### Metrics (Test Set)",
        "",
        "| Metric | Value |",
        "|--------|------:|",
        f"| ROC-AUC | {lr_metrics['auc']:.4f} |",
        f"| Precision@{K} | {lr_metrics['p_at_k']:.4f} |",
        f"| Precision (podium class) | {lr_metrics['precision']:.4f} |",
        f"| Recall (podium class) | {lr_metrics['recall']:.4f} |",
        f"| F1 (podium class) | {lr_metrics['f1']:.4f} |",
        "",
        "### Confusion Matrix",
        "",
        _cm_table(lr_metrics["cm"]),
        "",
        "### Top Feature Coefficients",
        "",
        "> Positive = increases predicted podium probability.",
        "> Negative = decreases it. Magnitude reflects strength after scaling.",
        "",
        _coef_table(lr_model),
    ]))

    # ── Gradient Boosting ─────────────────────────────────────────────────────
    sections.append("\n".join([
        f"## 3. {gb_label} (Main Model)",
        "",
        "**Purpose:** Captures nonlinear racing dynamics and interaction effects.",
        "**Class imbalance:** scale_pos_weight=6 (approx non-podium / podium ratio).",
        "",
        "### Metrics (Test Set)",
        "",
        "| Metric | Value |",
        "|--------|------:|",
        f"| ROC-AUC | {gb_metrics['auc']:.4f} |",
        f"| Precision@{K} | {gb_metrics['p_at_k']:.4f} |",
        f"| Precision (podium class) | {gb_metrics['precision']:.4f} |",
        f"| Recall (podium class) | {gb_metrics['recall']:.4f} |",
        f"| F1 (podium class) | {gb_metrics['f1']:.4f} |",
        "",
        "### Confusion Matrix",
        "",
        _cm_table(gb_metrics["cm"]),
        "",
        "### Feature Importances (Top 15)",
        "",
        "> Gain-based importance: how much each feature reduces prediction error.",
        "",
        _xgb_importance_table(gb_model),
    ]))

    # ── Feature Reference ─────────────────────────────────────────────────────
    sections.append("\n".join([
        "## 4. Feature Reference",
        "",
        "| Group | Features |",
        "|-------|---------|",
        "| Race context | `race_year`, `round`, `circuitId` |",
        "| Starting performance | `grid_imputed`, `qualifying_gap_ms`, `best_quali_ms` |",
        "| Driver form | `rolling_cumulative_points`, `rolling_podium_rate`, `rolling_dnf_rate`, `rolling_avg_finish_position`, `rolling_avg_qualifying_position` |",
        "| Constructor form | `con_rolling_cumulative_points`, `con_rolling_podium_rate`, `con_rolling_win_rate`, `con_rolling_dnf_rate`, `con_rolling_avg_finish_position` |",
        "| Experience | `prev_season_points`, `prev_season_podium_rate`, `has_prev_season` |",
        "| Race conditions | `pit_data_incomplete`, `grid_pit_lane` |",
    ]))

    # ── Footer ────────────────────────────────────────────────────────────────
    sections.append("\n".join([
        _hr(),
        "",
        "_Generated by `train_models.py`. "
        "Re-run after any change to `build_modeling_dataset.py` or feature engineering._",
    ]))

    return "\n\n".join(sections)


# ---------------------------------------------------------------------------
# Main training pipeline
# ---------------------------------------------------------------------------

def train() -> None:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    log.info("=" * 55)
    log.info("F1 PODIUM PREDICTION — MODEL TRAINING")
    log.info("=" * 55)

    # ── Load ──────────────────────────────────────────────────────────────────
    log.info("Loading modeling dataset ...")
    df = _load_dataset()

    # ── Split ─────────────────────────────────────────────────────────────────
    log.info("Applying time-based split ...")
    X_train, y_train, X_val, y_val, X_test, y_test, test_df = _time_split(df)

    split_info = {
        "n_train":           len(X_train),
        "n_val":             len(X_val),
        "n_test":            len(X_test),
        "train_years":       f"2000–{TRAIN_MAX_YEAR}",
        "val_years":         f"{VAL_MIN_YEAR}–{VAL_MAX_YEAR}",
        "test_years":        f"{TEST_MIN_YEAR}–{int(df['race_year'].max())}",
        "train_podium_rate": float(y_train.mean()),
        "val_podium_rate":   float(y_val.mean()),
        "test_podium_rate":  float(y_test.mean()),
    }

    # ── Model 1: Logistic Regression ─────────────────────────────────────────
    log.info("=" * 55)
    log.info("Training Logistic Regression ...")
    lr_model = _build_logistic_regression()
    lr_model.fit(X_train, y_train)
    log.info("  Training complete.")

    log.info("Evaluating Logistic Regression on test set ...")
    lr_metrics = _evaluate("Logistic Regression", lr_model, X_test, y_test, test_df)

    lr_path = MODELS_DIR / "logistic_regression.pkl"
    joblib.dump(lr_model, lr_path)
    log.info("  Saved → %s", lr_path)

    # ── Model 2: Gradient Boosting ────────────────────────────────────────────
    log.info("=" * 55)
    log.info("Training %s ...", "XGBoost" if _XGB_AVAILABLE else "HistGradientBoostingClassifier")
    gb_model = _build_gradient_boosting()
    gb_model.fit(X_train, y_train)
    log.info("  Training complete.")

    log.info("Evaluating %s on test set ...", GB_MODEL_NAME)
    gb_metrics = _evaluate(GB_MODEL_NAME, gb_model, X_test, y_test, test_df)

    gb_path = MODELS_DIR / f"{GB_MODEL_NAME}.pkl"
    joblib.dump(gb_model, gb_path)
    log.info("  Saved → %s", gb_path)

    # ── Report ────────────────────────────────────────────────────────────────
    log.info("=" * 55)
    log.info("Writing evaluation report ...")
    report_md = _generate_report(lr_metrics, gb_metrics, lr_model, gb_model, split_info)
    REPORT_PATH.write_text(report_md, encoding="utf-8")
    log.info("  Saved → %s", REPORT_PATH)

    # ── Final summary ─────────────────────────────────────────────────────────
    log.info("=" * 55)
    log.info("RESULTS SUMMARY")
    log.info("  %-35s  AUC=%.4f  P@%d=%.4f", "Logistic Regression",
             lr_metrics["auc"], K, lr_metrics["p_at_k"])
    log.info("  %-35s  AUC=%.4f  P@%d=%.4f", GB_MODEL_NAME,
             gb_metrics["auc"], K, gb_metrics["p_at_k"])
    log.info("=" * 55)
    log.info("Models saved → %s", MODELS_DIR)
    log.info("Report saved → %s", REPORT_PATH)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    train()