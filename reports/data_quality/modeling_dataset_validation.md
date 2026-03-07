# Modeling Dataset Validation Report

> **Generated:** 2026-03-07 15:13:41  
> **Dataset:** `E:\PyCharm Projects\f1-race-intelligence\data\processed\modeling\modeling_dataset.parquet`  
> **Rows:** 10,079  |  **Columns:** 33  
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

> ℹ️ Correlation audit (Section 5) is advisory and does not affect the scorecard.

## 1. Dataset Inventory

| Metric | Value |
|--------|------:|
| Rows | 10,079 |
| Columns | 33 |
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
| 7 | `grid` | float64 |
| 8 | `grid_pit_lane` | int64 |
| 9 | `qualifying_position` | float64 |
| 10 | `qualifying_gap_ms` | float64 |
| 11 | `best_quali_ms` | float64 |
| 12 | `pit_data_incomplete` | int64 |
| 13 | `constructorId_drv_roll` | int64 |
| 14 | `race_year_drv_roll` | int64 |
| 15 | `round_drv_roll` | int64 |
| 16 | `rolling_cumulative_points` | float64 |
| 17 | `rolling_cumulative_podiums` | float64 |
| 18 | `rolling_dnf_rate` | float64 |
| 19 | `rolling_avg_finish_position` | float64 |
| 20 | `rolling_avg_qualifying_position` | float64 |
| 21 | `rolling_races_counted` | int64 |
| 22 | `con_rolling_cumulative_points` | float64 |
| 23 | `con_rolling_podium_rate` | float64 |
| 24 | `con_rolling_win_rate` | float64 |
| 25 | `con_rolling_dnf_rate` | float64 |
| 26 | `con_rolling_avg_finish_position` | float64 |
| 27 | `con_rolling_races_counted` | int64 |
| 28 | `prev_season_points` | float64 |
| 29 | `prev_season_podium_rate` | float64 |
| 30 | `is_podium` | int8 |
| 31 | `rolling_podium_rate` | float64 |
| 32 | `grid_imputed` | float64 |
| 33 | `has_prev_season` | int8 |

## 2. Duplicate Key Check

**Composite key:** `raceId × driverId`
**Total rows:** 10,079
**Duplicate pairs:** 0
**Result:** ✅ PASS

## 3. Forbidden Column Check

**Forbidden columns defined:** 22
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
| `grid` | 93 | 0.92% | Null OK if grid_pit_lane=1 only | ✅ PASS (93 pit-lane justified, 0 unexplained) |
| `grid_pit_lane` | 0 | 0.00% | Must be 0 | ✅ PASS |
| `qualifying_position` | 981 | 9.73% | Advisory — null for pit-lane starts, penalties, early era | ℹ️ Minor (expected) |
| `qualifying_gap_ms` | 1,105 | 10.96% | Advisory | 🔶 Moderate |
| `best_quali_ms` | 1,105 | 10.96% | Advisory | 🔶 Moderate |
| `pit_data_incomplete` | 0 | 0.00% | Advisory | ✅ Clean |
| `constructorId_drv_roll` | 0 | 0.00% | Advisory | ✅ Clean |
| `race_year_drv_roll` | 0 | 0.00% | Advisory | ✅ Clean |
| `round_drv_roll` | 0 | 0.00% | Advisory | ✅ Clean |
| `rolling_cumulative_points` | 0 | 0.00% | Must be 0 (build fills round-1) | ✅ PASS |
| `rolling_cumulative_podiums` | 0 | 0.00% | Must be 0 (build fills round-1) | ✅ PASS |
| `rolling_dnf_rate` | 0 | 0.00% | Must be 0 (build fills round-1) | ✅ PASS |
| `rolling_avg_finish_position` | 0 | 0.00% | Advisory — DNF/pit-lane nulls expected | ✅ Clean |
| `rolling_avg_qualifying_position` | 0 | 0.00% | Advisory — DNF/pit-lane nulls expected | ✅ Clean |
| `rolling_races_counted` | 0 | 0.00% | Must be 0 (build fills round-1) | ✅ PASS |
| `con_rolling_cumulative_points` | 0 | 0.00% | Must be 0 (build fills round-1) | ✅ PASS |
| `con_rolling_podium_rate` | 0 | 0.00% | Must be 0 (build fills round-1) | ✅ PASS |
| `con_rolling_win_rate` | 532 | 5.28% | Advisory | 🔶 Moderate |
| `con_rolling_dnf_rate` | 0 | 0.00% | Must be 0 (build fills round-1) | ✅ PASS |
| `con_rolling_avg_finish_position` | 0 | 0.00% | Advisory — DNF/pit-lane nulls expected | ✅ Clean |
| `con_rolling_races_counted` | 0 | 0.00% | Must be 0 (build fills round-1) | ✅ PASS |
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
| Advisory | Informational only — does not affect scorecard |

## 5. Correlation Audit (Pearson)

**Features analysed:** 24
**Threshold:** |r| > 0.9
**High-correlation pairs found:** 9
**Result:** ⚠️ WARN — review pairs below

> ⚠️ These pairs are **flagged for manual review only**.
> Do NOT drop automatically — confirm redundancy before removing.
> Common legitimate causes in F1 data: cumulative points correlates
> with cumulative podiums; constructor and driver stats co-move
> during dominant seasons.

| Feature A | Feature B | Pearson r | Strength |
|-----------|-----------|----------:|----------|
| `grid` | `grid_imputed` | +1.0000 | 🔴 Very high |
| `round_drv_roll` | `con_rolling_races_counted` | +0.9974 | 🔴 Very high |
| `grid` | `qualifying_position` | +0.9679 | 🟠 High |
| `qualifying_position` | `grid_imputed` | +0.9631 | 🟠 High |
| `rolling_cumulative_points` | `con_rolling_cumulative_points` | +0.9602 | 🟠 High |
| `round_drv_roll` | `rolling_races_counted` | +0.9485 | 🟠 High |
| `rolling_races_counted` | `con_rolling_races_counted` | +0.9465 | 🟠 High |
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

| | `grid` | `qualifying_position` | `qualifying_gap_ms` | `best_quali_ms` | `pit_data_incomplete` | `constructorId_drv_roll` | `race_year_drv_roll` | `round_drv_roll` | `rolling_cumulative_points` | `rolling_cumulative_podiums` | `rolling_dnf_rate` | `rolling_avg_finish_position` | `rolling_avg_qualifying_position` | `rolling_races_counted` | `con_rolling_cumulative_points` | `con_rolling_podium_rate` | `con_rolling_win_rate` | `con_rolling_dnf_rate` | `con_rolling_avg_finish_position` | `con_rolling_races_counted` | `prev_season_points` | `prev_season_podium_rate` | `rolling_podium_rate` | `grid_imputed` |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `grid` | 1.00 | **0.97** | 0.59 | 0.14 | -0.01 | 0.19 | -0.05 | -0.01 | -0.47 | -0.48 | 0.21 | 0.56 | 0.60 | -0.05 | -0.46 | -0.56 | -0.47 | 0.26 | 0.60 | -0.01 | -0.50 | -0.51 | -0.53 | **1.00** |
| `qualifying_position` | **0.97** | 1.00 | 0.61 | 0.14 | -0.01 | 0.21 | -0.04 | -0.01 | -0.50 | -0.49 | 0.22 | 0.58 | 0.67 | -0.05 | -0.50 | -0.57 | -0.47 | 0.26 | 0.63 | -0.01 | -0.53 | -0.51 | -0.54 | **0.96** |
| `qualifying_gap_ms` | 0.59 | 0.61 | 1.00 | 0.35 | -0.04 | 0.19 | -0.03 | -0.01 | -0.28 | -0.27 | 0.12 | 0.34 | 0.41 | -0.04 | -0.28 | -0.33 | -0.27 | 0.15 | 0.38 | -0.01 | -0.30 | -0.29 | -0.31 | 0.58 |
| `best_quali_ms` | 0.14 | 0.14 | 0.35 | 1.00 | -0.03 | 0.05 | -0.04 | 0.05 | -0.03 | -0.04 | 0.03 | 0.05 | 0.09 | 0.04 | -0.03 | -0.07 | -0.05 | 0.04 | 0.07 | 0.05 | -0.06 | -0.07 | -0.07 | 0.13 |
| `pit_data_incomplete` | -0.01 | -0.01 | -0.04 | -0.03 | 1.00 | 0.09 | 0.23 | 0.02 | 0.05 | 0.01 | -0.08 | 0.02 | -0.00 | 0.02 | 0.05 | 0.00 | 0.00 | -0.10 | 0.02 | 0.02 | 0.07 | 0.01 | 0.01 | -0.01 |
| `constructorId_drv_roll` | 0.19 | 0.21 | 0.19 | 0.05 | 0.09 | 1.00 | 0.38 | 0.06 | -0.02 | -0.07 | -0.08 | 0.24 | 0.22 | 0.05 | -0.02 | -0.09 | -0.05 | -0.09 | 0.26 | 0.06 | -0.01 | -0.10 | -0.09 | 0.19 |
| `race_year_drv_roll` | -0.05 | -0.04 | -0.03 | -0.04 | 0.23 | 0.38 | 1.00 | 0.15 | 0.27 | 0.06 | -0.34 | 0.13 | 0.07 | 0.16 | 0.28 | 0.02 | 0.01 | -0.42 | 0.13 | 0.15 | 0.34 | 0.02 | 0.02 | -0.04 |
| `round_drv_roll` | -0.01 | -0.01 | -0.01 | 0.05 | 0.02 | 0.06 | 0.15 | 1.00 | 0.41 | 0.31 | -0.03 | 0.25 | 0.16 | **0.95** | 0.42 | 0.06 | 0.00 | -0.03 | 0.23 | **1.00** | 0.05 | 0.00 | 0.05 | -0.01 |
| `rolling_cumulative_points` | -0.47 | -0.50 | -0.28 | -0.03 | 0.05 | -0.02 | 0.27 | 0.41 | 1.00 | 0.87 | -0.27 | -0.40 | -0.40 | 0.44 | **0.96** | 0.63 | 0.55 | -0.30 | -0.41 | 0.41 | 0.66 | 0.52 | 0.64 | -0.46 |
| `rolling_cumulative_podiums` | -0.48 | -0.49 | -0.27 | -0.04 | 0.01 | -0.07 | 0.06 | 0.31 | 0.87 | 1.00 | -0.22 | -0.45 | -0.44 | 0.33 | 0.83 | 0.76 | 0.67 | -0.24 | -0.46 | 0.31 | 0.56 | 0.58 | 0.81 | -0.48 |
| `rolling_dnf_rate` | 0.21 | 0.22 | 0.12 | 0.03 | -0.08 | -0.08 | -0.34 | -0.03 | -0.27 | -0.22 | 1.00 | 0.11 | 0.28 | -0.03 | -0.25 | -0.24 | -0.22 | 0.82 | 0.19 | -0.04 | -0.26 | -0.19 | -0.27 | 0.21 |
| `rolling_avg_finish_position` | 0.56 | 0.58 | 0.34 | 0.05 | 0.02 | 0.24 | 0.13 | 0.25 | -0.40 | -0.45 | 0.11 | 1.00 | 0.80 | 0.24 | -0.38 | -0.53 | -0.52 | 0.16 | 0.90 | 0.25 | -0.44 | -0.47 | -0.52 | 0.55 |
| `rolling_avg_qualifying_position` | 0.60 | 0.67 | 0.41 | 0.09 | -0.00 | 0.22 | 0.07 | 0.16 | -0.40 | -0.44 | 0.28 | 0.80 | 1.00 | 0.15 | -0.39 | -0.51 | -0.50 | 0.30 | 0.81 | 0.16 | -0.45 | -0.47 | -0.50 | 0.60 |
| `rolling_races_counted` | -0.05 | -0.05 | -0.04 | 0.04 | 0.02 | 0.05 | 0.16 | **0.95** | 0.44 | 0.33 | -0.03 | 0.24 | 0.15 | 1.00 | 0.45 | 0.08 | 0.03 | -0.06 | 0.19 | **0.95** | 0.08 | 0.03 | 0.08 | -0.05 |
| `con_rolling_cumulative_points` | -0.46 | -0.50 | -0.28 | -0.03 | 0.05 | -0.02 | 0.28 | 0.42 | **0.96** | 0.83 | -0.25 | -0.38 | -0.39 | 0.45 | 1.00 | 0.66 | 0.57 | -0.31 | -0.43 | 0.43 | 0.63 | 0.49 | 0.60 | -0.46 |
| `con_rolling_podium_rate` | -0.56 | -0.57 | -0.33 | -0.07 | 0.00 | -0.09 | 0.02 | 0.06 | 0.63 | 0.76 | -0.24 | -0.53 | -0.51 | 0.08 | 0.66 | 1.00 | 0.87 | -0.30 | -0.58 | 0.06 | 0.58 | 0.63 | **0.91** | -0.56 |
| `con_rolling_win_rate` | -0.47 | -0.47 | -0.27 | -0.05 | 0.00 | -0.05 | 0.01 | 0.00 | 0.55 | 0.67 | -0.22 | -0.52 | -0.50 | 0.03 | 0.57 | 0.87 | 1.00 | -0.28 | -0.58 | 0.00 | 0.54 | 0.60 | 0.79 | -0.47 |
| `con_rolling_dnf_rate` | 0.26 | 0.26 | 0.15 | 0.04 | -0.10 | -0.09 | -0.42 | -0.03 | -0.30 | -0.24 | 0.82 | 0.16 | 0.30 | -0.06 | -0.31 | -0.30 | -0.28 | 1.00 | 0.24 | -0.04 | -0.31 | -0.21 | -0.27 | 0.25 |
| `con_rolling_avg_finish_position` | 0.60 | 0.63 | 0.38 | 0.07 | 0.02 | 0.26 | 0.13 | 0.23 | -0.41 | -0.46 | 0.19 | 0.90 | 0.81 | 0.19 | -0.43 | -0.58 | -0.58 | 0.24 | 1.00 | 0.23 | -0.45 | -0.48 | -0.53 | 0.60 |
| `con_rolling_races_counted` | -0.01 | -0.01 | -0.01 | 0.05 | 0.02 | 0.06 | 0.15 | **1.00** | 0.41 | 0.31 | -0.04 | 0.25 | 0.16 | **0.95** | 0.43 | 0.06 | 0.00 | -0.04 | 0.23 | 1.00 | 0.05 | 0.00 | 0.05 | -0.01 |
| `prev_season_points` | -0.50 | -0.53 | -0.30 | -0.06 | 0.07 | -0.01 | 0.34 | 0.05 | 0.66 | 0.56 | -0.26 | -0.44 | -0.45 | 0.08 | 0.63 | 0.58 | 0.54 | -0.31 | -0.45 | 0.05 | 1.00 | 0.82 | 0.58 | -0.49 |
| `prev_season_podium_rate` | -0.51 | -0.51 | -0.29 | -0.07 | 0.01 | -0.10 | 0.02 | 0.00 | 0.52 | 0.58 | -0.19 | -0.47 | -0.47 | 0.03 | 0.49 | 0.63 | 0.60 | -0.21 | -0.48 | 0.00 | 0.82 | 1.00 | 0.64 | -0.51 |
| `rolling_podium_rate` | -0.53 | -0.54 | -0.31 | -0.07 | 0.01 | -0.09 | 0.02 | 0.05 | 0.64 | 0.81 | -0.27 | -0.52 | -0.50 | 0.08 | 0.60 | **0.91** | 0.79 | -0.27 | -0.53 | 0.05 | 0.58 | 0.64 | 1.00 | -0.53 |
| `grid_imputed` | **1.00** | **0.96** | 0.58 | 0.13 | -0.01 | 0.19 | -0.04 | -0.01 | -0.46 | -0.48 | 0.21 | 0.55 | 0.60 | -0.05 | -0.46 | -0.56 | -0.47 | 0.25 | 0.60 | -0.01 | -0.49 | -0.51 | -0.53 | 1.00 |


────────────────────────────────────────────────────────────

_Generated by `validate_modeling_dataset.py`.
Re-run after any change to `build_modeling_dataset.py`._