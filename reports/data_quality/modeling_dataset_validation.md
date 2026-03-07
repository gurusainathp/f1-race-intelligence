# Modeling Dataset Validation Report

> **Generated:** 2026-03-07 15:57:45  
> **Dataset:** `E:\PyCharm Projects\f1-race-intelligence\data\processed\modeling\modeling_dataset.parquet`  
> **Rows:** 10,079  |  **Columns:** 25  
> **Year range:** 2000 – 2024  

────────────────────────────────────────────────────────────


## 0. Quality Scorecard

**Overall:** ✅ PASS

| # | Check | Result |
|---|-------|:------:|
| 1 | No duplicate (raceId, driverId) keys | ✅ PASS |
| 2 | No forbidden / post-race columns present | ✅ PASS |
| 3 | Null audit: zero nulls in required columns | ✅ PASS |
| 4 | Correlation audit (advisory) | ✅ PASS |
| 5 | VIF audit (advisory) | ✅ PASS |

> ℹ️ Correlation audit (Section 5) and VIF audit (Section 6) are advisory and do not affect the scorecard.

## 1. Dataset Inventory

| Metric | Value |
|--------|------:|
| Rows | 10,079 |
| Columns | 25 |
| Season range | 2000 – 2024 |
| Unique races | 479 |
| Unique drivers | 126 |
| Unique constructors | 38 |
| Podium rows (is_podium=1) | 1,437 (14.26%) |
| Non-podium rows (is_podium=0) | 8,642 (85.74%) |
| Class imbalance ratio | 6.0 : 1 |
| Rookie rows (has_prev_season=0) | 1,890 (18.75%) |

### Column List

| # | Column | dtype |
|---|--------|-------|
| 1 | `raceId` | int64 |
| 2 | `driverId` | int64 |
| 3 | `constructorId` | int64 |
| 4 | `race_year` | int64 |
| 5 | `round` | int64 |
| 6 | `circuitId` | int64 |
| 7 | `grid_pit_lane` | int64 |
| 8 | `qualifying_gap_ms` | float64 |
| 9 | `best_quali_ms` | float64 |
| 10 | `pit_data_incomplete` | int64 |
| 11 | `rolling_cumulative_points` | float64 |
| 12 | `rolling_dnf_rate` | float64 |
| 13 | `rolling_avg_finish_position` | float64 |
| 14 | `rolling_avg_qualifying_position` | float64 |
| 15 | `con_rolling_cumulative_points` | float64 |
| 16 | `con_rolling_podium_rate` | float64 |
| 17 | `con_rolling_win_rate` | float64 |
| 18 | `con_rolling_dnf_rate` | float64 |
| 19 | `con_rolling_avg_finish_position` | float64 |
| 20 | `prev_season_points` | float64 |
| 21 | `prev_season_podium_rate` | float64 |
| 22 | `is_podium` | int8 |
| 23 | `rolling_podium_rate` | float64 |
| 24 | `grid_imputed` | float64 |
| 25 | `has_prev_season` | int8 |

## 2. Duplicate Key Check

**Composite key:** `raceId × driverId`
**Total rows:** 10,079
**Duplicate pairs:** 0
**Result:** ✅ PASS

## 3. Forbidden Column Check

**Forbidden columns defined:** 30
**Forbidden columns present in dataset:** 0
**Result:** ✅ PASS

> ✅ No forbidden columns detected. Dataset is leakage-free.

## 4. Null Audit

| Column | Null Count | Null % | Rule | Result |
|--------|----------:|-------:|------|:------:|
| `raceId` | 0 | 0.00% | Must be 0 | ✅ PASS |
| `driverId` | 0 | 0.00% | Must be 0 | ✅ PASS |
| `constructorId` | 0 | 0.00% | Must be 0 | ✅ PASS |
| `race_year` | 0 | 0.00% | Must be 0 | ✅ PASS |
| `round` | 0 | 0.00% | Must be 0 | ✅ PASS |
| `circuitId` | 0 | 0.00% | Must be 0 | ✅ PASS |
| `grid_pit_lane` | 0 | 0.00% | Must be 0 | ✅ PASS |
| `qualifying_gap_ms` | 0 | 0.00% | Must be 0 | ✅ PASS |
| `best_quali_ms` | 0 | 0.00% | Must be 0 | ✅ PASS |
| `pit_data_incomplete` | 0 | 0.00% | Must be 0 | ✅ PASS |
| `rolling_cumulative_points` | 0 | 0.00% | Must be 0 (build fills round-1) | ✅ PASS |
| `rolling_dnf_rate` | 0 | 0.00% | Must be 0 (build fills round-1) | ✅ PASS |
| `rolling_avg_finish_position` | 0 | 0.00% | Advisory — DNF/pit-lane nulls expected | ✅ Clean |
| `rolling_avg_qualifying_position` | 0 | 0.00% | Advisory — DNF/pit-lane nulls expected | ✅ Clean |
| `con_rolling_cumulative_points` | 0 | 0.00% | Must be 0 (build fills round-1) | ✅ PASS |
| `con_rolling_podium_rate` | 0 | 0.00% | Must be 0 (build fills round-1) | ✅ PASS |
| `con_rolling_win_rate` | 0 | 0.00% | Must be 0 | ✅ PASS |
| `con_rolling_dnf_rate` | 0 | 0.00% | Must be 0 (build fills round-1) | ✅ PASS |
| `con_rolling_avg_finish_position` | 0 | 0.00% | Advisory — DNF/pit-lane nulls expected | ✅ Clean |
| `prev_season_points` | 0 | 0.00% | Must be 0 | ✅ PASS |
| `prev_season_podium_rate` | 0 | 0.00% | Must be 0 | ✅ PASS |
| `is_podium` | 0 | 0.00% | Must be 0 | ✅ PASS |
| `rolling_podium_rate` | 0 | 0.00% | Must be 0 (build fills round-1) | ✅ PASS |
| `grid_imputed` | 0 | 0.00% | Must be 0 | ✅ PASS |
| `has_prev_season` | 0 | 0.00% | Must be 0 | ✅ PASS |

**Overall (FAIL-level checks only):** ✅ PASS

### Null Rule Legend

| Rule | Meaning |
|------|---------|
| Must be 0 | Zero nulls required — FAIL if any present |
| Must be 0 (build fills round-1) | Rolling cols filled by build script — FAIL if any remain |
| Null OK if grid_pit_lane=1 only | Raw grid — null justified only for pit-lane starters |
| Advisory — DNF/pit-lane nulls expected | Position rolling cols — nulls OK, do not fail |
| Advisory — null for pit-lane starts, penalties, early era | Qualifying cols — nulls OK, do not fail |
| Advisory | Informational only — does not affect scorecard |

## 5. Correlation Audit (Pearson)

**Features analysed:** 16
**Threshold:** |r| > 0.9
**High-correlation pairs found:** 3
**Result:** ⚠️ WARN — review pairs below

> ⚠️ These pairs are **flagged for manual review only**.
> Do NOT drop automatically — confirm redundancy before removing.
> Common legitimate causes in F1 data: cumulative points correlates
> with cumulative podiums; constructor and driver stats co-move
> during dominant seasons.

| Feature A | Feature B | Pearson r | Strength |
|-----------|-----------|----------:|----------|
| `rolling_cumulative_points` | `con_rolling_cumulative_points` | +0.9602 | 🟠 High |
| `con_rolling_podium_rate` | `rolling_podium_rate` | +0.9086 | 🟡 Moderate-high |
| `rolling_avg_finish_position` | `con_rolling_avg_finish_position` | +0.9041 | 🟡 Moderate-high |

### Suggested Investigation

For each flagged pair, ask:
1. Do they measure the same underlying signal?
2. Does one have more predictive signal than the other?
3. Does VIF confirm multicollinearity in the logistic regression?

Remove the weaker feature only after answering the above.

### Full Pearson Correlation Matrix

> Values shown to 2 decimal places.

| | `qualifying_gap_ms` | `best_quali_ms` | `pit_data_incomplete` | `rolling_cumulative_points` | `rolling_dnf_rate` | `rolling_avg_finish_position` | `rolling_avg_qualifying_position` | `con_rolling_cumulative_points` | `con_rolling_podium_rate` | `con_rolling_win_rate` | `con_rolling_dnf_rate` | `con_rolling_avg_finish_position` | `prev_season_points` | `prev_season_podium_rate` | `rolling_podium_rate` | `grid_imputed` |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `qualifying_gap_ms` | 1.00 | 0.35 | -0.03 | -0.27 | 0.08 | 0.33 | 0.38 | -0.27 | -0.31 | -0.24 | 0.11 | 0.37 | -0.28 | -0.28 | -0.29 | 0.53 |
| `best_quali_ms` | 0.35 | 1.00 | -0.02 | -0.02 | 0.02 | 0.05 | 0.08 | -0.02 | -0.07 | -0.05 | 0.03 | 0.07 | -0.06 | -0.06 | -0.06 | 0.12 |
| `pit_data_incomplete` | -0.03 | -0.02 | 1.00 | 0.05 | -0.08 | 0.02 | -0.00 | 0.05 | 0.00 | 0.00 | -0.10 | 0.02 | 0.07 | 0.01 | 0.01 | -0.01 |
| `rolling_cumulative_points` | -0.27 | -0.02 | 0.05 | 1.00 | -0.27 | -0.40 | -0.40 | **0.96** | 0.63 | 0.55 | -0.30 | -0.41 | 0.66 | 0.52 | 0.64 | -0.46 |
| `rolling_dnf_rate` | 0.08 | 0.02 | -0.08 | -0.27 | 1.00 | 0.11 | 0.28 | -0.25 | -0.24 | -0.19 | 0.82 | 0.19 | -0.26 | -0.19 | -0.27 | 0.21 |
| `rolling_avg_finish_position` | 0.33 | 0.05 | 0.02 | -0.40 | 0.11 | 1.00 | 0.80 | -0.38 | -0.53 | -0.43 | 0.16 | 0.90 | -0.44 | -0.47 | -0.52 | 0.55 |
| `rolling_avg_qualifying_position` | 0.38 | 0.08 | -0.00 | -0.40 | 0.28 | 0.80 | 1.00 | -0.39 | -0.51 | -0.42 | 0.30 | 0.81 | -0.45 | -0.47 | -0.50 | 0.60 |
| `con_rolling_cumulative_points` | -0.27 | -0.02 | 0.05 | **0.96** | -0.25 | -0.38 | -0.39 | 1.00 | 0.66 | 0.57 | -0.31 | -0.43 | 0.63 | 0.49 | 0.60 | -0.46 |
| `con_rolling_podium_rate` | -0.31 | -0.07 | 0.00 | 0.63 | -0.24 | -0.53 | -0.51 | 0.66 | 1.00 | 0.87 | -0.30 | -0.58 | 0.58 | 0.63 | **0.91** | -0.56 |
| `con_rolling_win_rate` | -0.24 | -0.05 | 0.00 | 0.55 | -0.19 | -0.43 | -0.42 | 0.57 | 0.87 | 1.00 | -0.24 | -0.48 | 0.53 | 0.58 | 0.79 | -0.45 |
| `con_rolling_dnf_rate` | 0.11 | 0.03 | -0.10 | -0.30 | 0.82 | 0.16 | 0.30 | -0.31 | -0.30 | -0.24 | 1.00 | 0.24 | -0.31 | -0.21 | -0.27 | 0.25 |
| `con_rolling_avg_finish_position` | 0.37 | 0.07 | 0.02 | -0.41 | 0.19 | 0.90 | 0.81 | -0.43 | -0.58 | -0.48 | 0.24 | 1.00 | -0.45 | -0.48 | -0.53 | 0.60 |
| `prev_season_points` | -0.28 | -0.06 | 0.07 | 0.66 | -0.26 | -0.44 | -0.45 | 0.63 | 0.58 | 0.53 | -0.31 | -0.45 | 1.00 | 0.82 | 0.58 | -0.49 |
| `prev_season_podium_rate` | -0.28 | -0.06 | 0.01 | 0.52 | -0.19 | -0.47 | -0.47 | 0.49 | 0.63 | 0.58 | -0.21 | -0.48 | 0.82 | 1.00 | 0.64 | -0.51 |
| `rolling_podium_rate` | -0.29 | -0.06 | 0.01 | 0.64 | -0.27 | -0.52 | -0.50 | 0.60 | **0.91** | 0.79 | -0.27 | -0.53 | 0.58 | 0.64 | 1.00 | -0.53 |
| `grid_imputed` | 0.53 | 0.12 | -0.01 | -0.46 | 0.21 | 0.55 | 0.60 | -0.46 | -0.56 | -0.45 | 0.25 | 0.60 | -0.49 | -0.51 | -0.53 | 1.00 |

## 6. VIF — Variance Inflation Factor

**Features analysed:** 15
**Rows used (complete cases):** 10,079

| Feature | VIF | Assessment |
|---------|----:|-----------|
| `con_rolling_avg_finish_position` | 33.1 | ❌ High — multicollinearity concern |
| `con_rolling_cumulative_points` | 29.6 | ❌ High — multicollinearity concern |
| `rolling_cumulative_points` | 29.3 | ❌ High — multicollinearity concern |
| `rolling_avg_finish_position` | 27.2 | ❌ High — multicollinearity concern |
| `con_rolling_podium_rate` | 18.0 | ❌ High — multicollinearity concern |
| `rolling_avg_qualifying_position` | 13.6 | ❌ High — multicollinearity concern |
| `best_quali_ms` | 13.2 | ❌ High — multicollinearity concern |
| `rolling_podium_rate` | 12.0 | ❌ High — multicollinearity concern |
| `grid_imputed` | 9.0 | ⚠️ Moderate — monitor |
| `con_rolling_dnf_rate` | 8.2 | ⚠️ Moderate — monitor |
| `rolling_dnf_rate` | 6.5 | ⚠️ Moderate — monitor |
| `prev_season_points` | 5.9 | ⚠️ Moderate — monitor |
| `prev_season_podium_rate` | 5.1 | ⚠️ Moderate — monitor |
| `con_rolling_win_rate` | 5.1 | ⚠️ Moderate — monitor |
| `qualifying_gap_ms` | 2.5 | ✅ Low |

**High-VIF features (> 10):** 8

> ℹ️ VIF is advisory — high values do not automatically require dropping a feature.
> Interpret alongside the correlation audit (Section 5).
> XGBoost is robust to multicollinearity; Logistic Regression is not.
> For Logistic Regression: consider dropping or PCA-transforming features
> with VIF > 10 before fitting.


────────────────────────────────────────────────────────────

_Generated by `validate_modeling_dataset.py`.
Re-run after any change to `build_modeling_dataset.py`._