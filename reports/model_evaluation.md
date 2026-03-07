# F1 Podium Prediction — Model Evaluation Report

> **Generated:** 2026-03-07 16:06:21
> **Task:** Binary classification — `is_podium` (1 = podium, 0 = no podium)
> **Features:** 21
> **Train:** 7,940 rows  (2000–2019)
> **Val:** 1,220 rows  (2020–2022)
> **Test:** 919 rows  (2023–2024)
> **Podium rate (test):** 15.0%

────────────────────────────────────────────────────────────

## 0. Model Comparison Summary

| Metric | Logistic Regression | XGBoost |
|--------|--------------------:|----------------------:|
| **ROC-AUC** | **0.9235** | **0.9297** |
| Precision@3 | 0.6014 | 0.6522 |
| Precision (podium) | 0.4747 | 0.5573 |
| Recall (podium) | 0.8841 | 0.7754 |
| F1 (podium) | 0.6177 | 0.6485 |

> **ROC-AUC** is the primary metric. Random baseline = 0.50.
> **Precision@3**: fraction of the top-3 predicted drivers per race that actually finished on the podium. Max = 1.0.

## 1. Dataset Split

Time-based split — no data leakage across seasons.

| Split | Years | Rows | Podium % |
|-------|-------|-----:|---------:|
| Train | 2000–2019 | 7,940 | 14.1% |
| Val   | 2020–2022   | 1,220   | 15.0% |
| Test  | 2023–2024  | 919  | 15.0% |

> Validation set is used as a reference only. 
> Final evaluation is reported on the **test set** exclusively.

## 2. Logistic Regression (Baseline)

**Purpose:** Interpretable baseline. Coefficients reveal feature direction.
**Scaling:** StandardScaler applied (required for regularised LR).
**Class weight:** balanced (compensates for ~14% podium rate).

### Metrics (Test Set)

| Metric | Value |
|--------|------:|
| ROC-AUC | 0.9235 |
| Precision@3 | 0.6014 |
| Precision (podium class) | 0.4747 |
| Recall (podium class) | 0.8841 |
| F1 (podium class) | 0.6177 |

### Confusion Matrix

| | Predicted: No Podium | Predicted: Podium |
|---|---:|---:|
| **Actual: No Podium** | 646 (TN) | 135 (FP) |
| **Actual: Podium**    | 16 (FN) | 122 (TP) |

### Top Feature Coefficients

> Positive = increases predicted podium probability.
> Negative = decreases it. Magnitude reflects strength after scaling.

| Rank | Feature | Coefficient | Direction |
|-----:|---------|------------:|----------|
| 1 | `grid_imputed` | -1.2974 | 📉 Decreases podium prob |
| 2 | `con_rolling_avg_finish_position` | -0.4259 | 📉 Decreases podium prob |
| 3 | `rolling_cumulative_points` | +0.4140 | 📈 Increases podium prob |
| 4 | `prev_season_podium_rate` | +0.2816 | 📈 Increases podium prob |
| 5 | `qualifying_gap_ms` | -0.2647 | 📉 Decreases podium prob |
| 6 | `con_rolling_podium_rate` | +0.2106 | 📈 Increases podium prob |
| 7 | `con_rolling_cumulative_points` | -0.1796 | 📉 Decreases podium prob |
| 8 | `rolling_podium_rate` | +0.1732 | 📈 Increases podium prob |
| 9 | `rolling_avg_qualifying_position` | -0.1594 | 📉 Decreases podium prob |
| 10 | `grid_pit_lane` | -0.1287 | 📉 Decreases podium prob |
| 11 | `round` | -0.1058 | 📉 Decreases podium prob |
| 12 | `race_year` | -0.0913 | 📉 Decreases podium prob |
| 13 | `con_rolling_win_rate` | +0.0852 | 📈 Increases podium prob |
| 14 | `has_prev_season` | +0.0609 | 📈 Increases podium prob |
| 15 | `con_rolling_dnf_rate` | -0.0596 | 📉 Decreases podium prob |

## 3. XGBoost (Main Model)

**Purpose:** Captures nonlinear racing dynamics and interaction effects.
**Class imbalance:** scale_pos_weight=6 (approx non-podium / podium ratio).

### Metrics (Test Set)

| Metric | Value |
|--------|------:|
| ROC-AUC | 0.9297 |
| Precision@3 | 0.6522 |
| Precision (podium class) | 0.5573 |
| Recall (podium class) | 0.7754 |
| F1 (podium class) | 0.6485 |

### Confusion Matrix

| | Predicted: No Podium | Predicted: Podium |
|---|---:|---:|
| **Actual: No Podium** | 696 (TN) | 85 (FP) |
| **Actual: Podium**    | 31 (FN) | 107 (TP) |

### Feature Importances (Top 15)

> Gain-based importance: how much each feature reduces prediction error.

| Rank | Feature | Importance |
|-----:|---------|----------:|
| 1 | `grid_imputed` | 0.3418 ██████████████████████████████████ |
| 2 | `con_rolling_podium_rate` | 0.1236 ████████████ |
| 3 | `con_rolling_avg_finish_position` | 0.0650 ██████ |
| 4 | `prev_season_podium_rate` | 0.0537 █████ |
| 5 | `rolling_podium_rate` | 0.0431 ████ |
| 6 | `qualifying_gap_ms` | 0.0403 ████ |
| 7 | `con_rolling_win_rate` | 0.0295 ██ |
| 8 | `prev_season_points` | 0.0287 ██ |
| 9 | `rolling_avg_qualifying_position` | 0.0282 ██ |
| 10 | `rolling_avg_finish_position` | 0.0273 ██ |
| 11 | `con_rolling_cumulative_points` | 0.0241 ██ |
| 12 | `race_year` | 0.0239 ██ |
| 13 | `circuitId` | 0.0236 ██ |
| 14 | `rolling_dnf_rate` | 0.0232 ██ |
| 15 | `rolling_cumulative_points` | 0.0223 ██ |

## 4. Feature Reference

| Group | Features |
|-------|---------|
| Race context | `race_year`, `round`, `circuitId` |
| Starting performance | `grid_imputed`, `qualifying_gap_ms`, `best_quali_ms` |
| Driver form | `rolling_cumulative_points`, `rolling_podium_rate`, `rolling_dnf_rate`, `rolling_avg_finish_position`, `rolling_avg_qualifying_position` |
| Constructor form | `con_rolling_cumulative_points`, `con_rolling_podium_rate`, `con_rolling_win_rate`, `con_rolling_dnf_rate`, `con_rolling_avg_finish_position` |
| Experience | `prev_season_points`, `prev_season_podium_rate`, `has_prev_season` |
| Race conditions | `pit_data_incomplete`, `grid_pit_lane` |

────────────────────────────────────────────────────────────

_Generated by `train_models.py`. Re-run after any change to `build_modeling_dataset.py` or feature engineering._