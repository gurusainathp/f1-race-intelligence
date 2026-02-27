# Data Quality Report

> **Generated:** 2026-02-28 00:36:42  
> **Source:** `data\interim`  
> **Tables loaded:** 9  

────────────────────────────────────────────────────────────


## 0. Quality Scorecard

**Overall:** ❌ FAIL

| # | Check | Result |
|---|-------|:------:|
| 1 | No unjustified high-null columns | ✅ PASS |
| 2 | Schema: all expected columns present | ✅ PASS |
| 3 | Foreign key integrity | ✅ PASS |
| 4 | No unexplained duplicate race-driver records | ✅ PASS |
| 5 | Lap time: no corrupt values | ❌ FAIL |
| 6 | Status integration with results intact | ✅ PASS |


## 1. Dataset Inventory

| Table | Rows | Columns | Null Cells | Null % |
|-------|-----:|--------:|-----------:|-------:|
| `circuits` | 77 | 8 | 0 | 0.0% |
| `constructors` | 212 | 4 | 0 | 0.0% |
| `drivers` | 861 | 9 | 1,559 | 20.1% |
| `lap_times` | 588,455 | 5 | 0 | 0.0% |
| `pit_stops` | 11,371 | 5 | 534 | 0.9% |
| `qualifying` | 10,494 | 10 | 11,826 | 11.3% |
| `races` | 1,125 | 11 | 5,265 | 42.5% |
| `results` | 26,759 | 21 | 124,525 | 22.2% |
| `status` | 139 | 2 | 0 | 0.0% |

## 2. Null Value Analysis

### `circuits`
- **Rows:** 77  |  **Columns:** 8  |  **Columns with nulls:** 0

| Column | Type | Null Count | Null % | Severity | Note |
|--------|------|----------:|-------:|----------|------|
| `circuitId` | int64 | 0 | 0.00% | ✅ Clean | — |
| `circuitRef` | object | 0 | 0.00% | ✅ Clean | — |
| `name` | object | 0 | 0.00% | ✅ Clean | — |
| `location` | object | 0 | 0.00% | ✅ Clean | — |
| `country` | object | 0 | 0.00% | ✅ Clean | — |
| `lat` | float64 | 0 | 0.00% | ✅ Clean | — |
| `lng` | float64 | 0 | 0.00% | ✅ Clean | — |
| `alt` | int64 | 0 | 0.00% | ✅ Clean | — |

### `constructors`
- **Rows:** 212  |  **Columns:** 4  |  **Columns with nulls:** 0

| Column | Type | Null Count | Null % | Severity | Note |
|--------|------|----------:|-------:|----------|------|
| `constructorId` | int64 | 0 | 0.00% | ✅ Clean | — |
| `constructorRef` | object | 0 | 0.00% | ✅ Clean | — |
| `name` | object | 0 | 0.00% | ✅ Clean | — |
| `nationality` | object | 0 | 0.00% | ✅ Clean | — |

### `drivers`
- **Rows:** 861  |  **Columns:** 9  |  **Columns with nulls:** 2

| Column | Type | Null Count | Null % | Severity | Note |
|--------|------|----------:|-------:|----------|------|
| `number` | float64 | 802 | 93.15% | ℹ️ Justified | Permanent driver numbers introduced in 2014 only |
| `code` | object | 757 | 87.92% | ℹ️ Justified | 3-letter driver codes formalised in modern era only |
| `driverId` | int64 | 0 | 0.00% | ✅ Clean | — |
| `driverRef` | object | 0 | 0.00% | ✅ Clean | — |
| `forename` | object | 0 | 0.00% | ✅ Clean | — |
| `surname` | object | 0 | 0.00% | ✅ Clean | — |
| `dob` | object | 0 | 0.00% | ✅ Clean | — |
| `nationality` | object | 0 | 0.00% | ✅ Clean | — |
| `full_name` | object | 0 | 0.00% | ✅ Clean | — |

### `lap_times`
- **Rows:** 588,455  |  **Columns:** 5  |  **Columns with nulls:** 0

| Column | Type | Null Count | Null % | Severity | Note |
|--------|------|----------:|-------:|----------|------|
| `raceId` | int64 | 0 | 0.00% | ✅ Clean | — |
| `driverId` | int64 | 0 | 0.00% | ✅ Clean | — |
| `lap` | int64 | 0 | 0.00% | ✅ Clean | — |
| `position` | int64 | 0 | 0.00% | ✅ Clean | — |
| `lap_time_ms` | float64 | 0 | 0.00% | ✅ Clean | — |

### `pit_stops`
- **Rows:** 11,371  |  **Columns:** 5  |  **Columns with nulls:** 1

| Column | Type | Null Count | Null % | Severity | Note |
|--------|------|----------:|-------:|----------|------|
| `pit_duration_ms` | float64 | 534 | 4.70% | 🔍 Investigate | 4.7% null in pit_stops — clustered in specific modern races (partial feed failures in Kaggle source, e.g. 2023 Australian GP 70.8% null, 2021 Saudi GP 74.5% null). Not random. Do NOT impute — null means data was never recorded, not a fast/slow stop |
| `raceId` | int64 | 0 | 0.00% | ✅ Clean | — |
| `driverId` | int64 | 0 | 0.00% | ✅ Clean | — |
| `stop` | int64 | 0 | 0.00% | ✅ Clean | — |
| `lap` | int64 | 0 | 0.00% | ✅ Clean | — |

### `qualifying`
- **Rows:** 10,494  |  **Columns:** 10  |  **Columns with nulls:** 4

| Column | Type | Null Count | Null % | Severity | Note |
|--------|------|----------:|-------:|----------|------|
| `q3_ms` | float64 | 6,865 | 65.42% | ℹ️ Justified | Q3 only exists for top-10 qualifiers post-2006 (structural ~65% null) |
| `q2_ms` | float64 | 4,647 | 44.28% | ℹ️ Justified | Q2 only exists in 3-part qualifying introduced in 2006 |
| `best_quali_ms` | float64 | 157 | 1.50% | 🔍 Investigate | 1.5% null in qualifying — mirrors q1_ms nulls exactly (derived as min of q1/q2/q3) |
| `q1_ms` | float64 | 157 | 1.50% | 🔍 Investigate | 1.5% null in qualifying — spans 1994-2024 including modern seasons. Known causes: entire races missing from Kaggle source (e.g. 1995 Australian GP — full grid null), 107% rule failures, injury/DNS entries. Not fixable in pipeline |
| `raceId` | int64 | 0 | 0.00% | ✅ Clean | — |
| `qualifyId` | int64 | 0 | 0.00% | ✅ Clean | — |
| `position` | int64 | 0 | 0.00% | ✅ Clean | — |
| `number` | int64 | 0 | 0.00% | ℹ️ Justified | Permanent driver numbers introduced in 2014 only |
| `constructorId` | int64 | 0 | 0.00% | ✅ Clean | — |
| `driverId` | int64 | 0 | 0.00% | ✅ Clean | — |

### `races`
- **Rows:** 1,125  |  **Columns:** 11  |  **Columns with nulls:** 5

| Column | Type | Null Count | Null % | Severity | Note |
|--------|------|----------:|-------:|----------|------|
| `sprint_date` | object | 1,107 | 98.40% | ℹ️ Justified | Sprint sessions only from 2021 (~6% of races) |
| `fp3_date` | object | 1,053 | 93.60% | ℹ️ Justified | Session dates only recorded from 2021 era |
| `fp1_date` | object | 1,035 | 92.00% | ℹ️ Justified | Session dates only recorded from 2021 era |
| `quali_date` | object | 1,035 | 92.00% | ℹ️ Justified | Session dates only recorded from 2021 era |
| `fp2_date` | object | 1,035 | 92.00% | ℹ️ Justified | Session dates only recorded from 2021 era |
| `raceId` | int64 | 0 | 0.00% | ✅ Clean | — |
| `year` | int64 | 0 | 0.00% | ✅ Clean | — |
| `round` | int64 | 0 | 0.00% | ✅ Clean | — |
| `date` | object | 0 | 0.00% | ✅ Clean | — |
| `circuitId` | int64 | 0 | 0.00% | ✅ Clean | — |
| `name` | object | 0 | 0.00% | ✅ Clean | — |

### `results`
- **Rows:** 26,759  |  **Columns:** 21  |  **Columns with nulls:** 9

| Column | Type | Null Count | Null % | Severity | Note |
|--------|------|----------:|-------:|----------|------|
| `time` | object | 19,079 | 71.30% | ℹ️ Justified | Finish time only for classified finishers (DNFs = null by design) |
| `milliseconds` | float64 | 19,079 | 71.30% | ℹ️ Justified | Finish time only for classified finishers (DNFs = null by design) |
| `fastestLapSpeed` | float64 | 18,507 | 69.16% | ℹ️ Justified | Fastest lap data standardised from 2004 season only |
| `fastestLap` | float64 | 18,507 | 69.16% | ℹ️ Justified | Fastest lap data standardised from 2004 season only |
| `fastestLapTime_ms` | float64 | 18,507 | 69.16% | ℹ️ Justified | Fastest lap data standardised from 2004 season only |
| `rank` | float64 | 18,249 | 68.20% | ℹ️ Justified | Fastest lap ranking introduced from 2019 season only |
| `position` | float64 | 10,953 | 40.93% | 🔍 Investigate | 41% null in results — expected: all DNFs have null position. Diagnostics confirmed difference = 2 (two lapped finishers with null position in Kaggle source — use positionOrder as reliable ordering column) |
| `grid` | float64 | 1,638 | 6.12% | 🔍 Investigate | 6% null in results — grid=0 recoded to NaN with grid_pit_lane flag. Pre-1996: 0 was a missing-data sentinel (517 rows, 14 scored points). Modern: genuine pit-lane starts. Do NOT use grid alone for pre-1996 analysis |
| `number` | float64 | 6 | 0.02% | ℹ️ Justified | Permanent driver numbers introduced in 2014 only |
| `constructorId` | int64 | 0 | 0.00% | ✅ Clean | — |
| `driverId` | int64 | 0 | 0.00% | ✅ Clean | — |
| `raceId` | int64 | 0 | 0.00% | ✅ Clean | — |
| `resultId` | int64 | 0 | 0.00% | ✅ Clean | — |
| `points` | float64 | 0 | 0.00% | ✅ Clean | — |
| `laps` | int64 | 0 | 0.00% | ✅ Clean | — |
| `positionText` | object | 0 | 0.00% | ✅ Clean | — |
| `positionOrder` | int64 | 0 | 0.00% | ✅ Clean | — |
| `statusId` | int64 | 0 | 0.00% | ✅ Clean | — |
| `grid_pit_lane` | int64 | 0 | 0.00% | ℹ️ Justified | Binary flag added by clean_data.py: 1 = post-1995 pit-lane start, 0 = not a pit-lane start or pre-1996 data gap. Always filled — never null |
| `is_dnf` | int64 | 0 | 0.00% | ✅ Clean | — |
| `is_podium` | int64 | 0 | 0.00% | ✅ Clean | — |

### `status`
- **Rows:** 139  |  **Columns:** 2  |  **Columns with nulls:** 0

| Column | Type | Null Count | Null % | Severity | Note |
|--------|------|----------:|-------:|----------|------|
| `statusId` | int64 | 0 | 0.00% | ✅ Clean | — |
| `status` | object | 0 | 0.00% | ✅ Clean | — |

### Null Classification Legend

| Label | Meaning |
|-------|---------|
| ✅ Clean | No nulls |
| ⚠️ Minor | < 5% null, no action needed |
| 🔶 Moderate | 5–20% null, monitor |
| ❌ High | > 20% null, unjustified — fix required |
| ℹ️ Justified | High null rate expected due to era/format constraints |
| 🔍 Investigate | Null rate requires manual review before modeling |

## 3. Schema Drift Check

**Overall:** ✅ PASS

| Table | Missing Columns | Unexpected Columns | Result |
|-------|-----------------|-------------------|:------:|
| `constructors` | — | — | ✅ PASS |
| `drivers` | — | `code`, `dob`, `full_name`, `number` | ✅ PASS |
| `lap_times` | — | — | ✅ PASS |
| `races` | — | `fp1_date`, `fp2_date`, `fp3_date`, `quali_date`, `sprint_date` | ✅ PASS |
| `results` | — | `fastestLap`, `fastestLapSpeed`, `fastestLapTime_ms`, `is_dnf`, `is_podium`, `milliseconds`, `number`, `positionOrder`, `positionText`, `rank`, `time` | ✅ PASS |
| `status` | — | — | ✅ PASS |

> _Unexpected columns are informational only and do not fail this check._

## 4. Foreign Key Validation

**Overall:** ✅ PASS

| Relationship | Rows Checked | Orphan Rows | Orphan % | Result |
|---|---:|---:|---:|:---:|
| `results.raceId` → `races.raceId` | 26,759 | 0 | 0.0% | ✅ PASS |
| `results.driverId` → `drivers.driverId` | 26,759 | 0 | 0.0% | ✅ PASS |
| `results.constructorId` → `constructors.constructorId` | 26,759 | 0 | 0.0% | ✅ PASS |
| `results.statusId` → `status.statusId` | 26,759 | 0 | 0.0% | ✅ PASS |

## 5. Duplicate Race-Driver Records

**Composite key:** `raceId × driverId`
**Duplicate pairs found:** 91  →  ❌ FAIL
**Rows affected:** 176 / 26,759 (0.7%)

**Distinct races affected:** 42
**Affected raceIds:** `540`, `717`, `733`, `742`, `745`, `746`, `766`, `770`, `774`, `776`, `777`, `779`, `780`, `783`, `784`, `785`, `787`, `788`, `789`, `791`, `792`, `793`, `795`, `797`, `800`, `801`, `803`, `804`, `806`, `809` _(showing first 30 of 42)_

### Duplicate Root Cause Classification

| Category | Race Count | Interpretation | Action |
|----------|----------:|----------------|--------|
| 🏎️ Sprint Race (2021+) | 0 | Sprint + Main race share same raceId | Add `session_type` column or separate table |
| 🏛️ Dual Constructor | 8 | Driver raced for 2 teams in same event | Extend key with `constructorId` |
| 🤝 Car Sharing (pre-1970) | 37 | 1950s–60s shared-drive stints — expected historical data | Add `is_shared_drive` flag |
| ❓ Unexplained | 0 | No structural reason found | **Investigate immediately** |

> ℹ️ **Car-sharing duplicates are expected historical data.** In 1950s–60s F1, multiple drivers shared one car in stints. Each stint is a separate row. For main-race analysis, use the row with the highest `laps` value (final driver to take the wheel). Consider adding an `is_shared_drive` flag.

**Top affected races (up to 15):**

| raceId | Year | Duplicate Pairs | Category |
|-------:|-----:|----------------:|----------|
| 792 | 1955 | 13 | 🤝 Car Sharing |
| 800 | 1954 | 13 | 🏛️ Dual Constructor |
| 809 | 1953 | 10 | 🏛️ Dual Constructor |
| 780 | 1957 | 3 | 🤝 Car Sharing |
| 788 | 1956 | 3 | 🏛️ Dual Constructor |
| 791 | 1956 | 3 | 🤝 Car Sharing |
| 828 | 1951 | 3 | 🤝 Car Sharing |
| 789 | 1956 | 2 | 🤝 Car Sharing |
| 797 | 1955 | 2 | 🤝 Car Sharing |
| 793 | 1955 | 2 | 🤝 Car Sharing |
| 815 | 1953 | 2 | 🤝 Car Sharing |
| 814 | 1953 | 2 | 🤝 Car Sharing |
| 785 | 1956 | 2 | 🤝 Car Sharing |
| 839 | 1950 | 2 | 🤝 Car Sharing |
| 777 | 1957 | 2 | 🤝 Car Sharing |

**All duplicate pairs (up to 20):**

| raceId | driverId | Occurrences |
|-------:|---------:|------------:|
| 809 | 521 | 3 |
| 800 | 612 | 3 |
| 792 | 427 | 3 |
| 792 | 554 | 3 |
| 792 | 501 | 3 |
| 809 | 612 | 3 |
| 766 | 541 | 2 |
| 746 | 475 | 2 |
| 774 | 566 | 2 |
| 776 | 581 | 2 |
| 777 | 501 | 2 |
| 777 | 578 | 2 |
| 779 | 356 | 2 |
| 780 | 475 | 2 |
| 780 | 479 | 2 |
| 770 | 479 | 2 |
| 540 | 229 | 2 |
| 717 | 373 | 2 |
| 733 | 465 | 2 |
| 742 | 475 | 2 |

### Recommended Fix

**If duplicates are Sprint races (2021+):**
```python
# Add session_type to differentiate Sprint from Main Race
results['session_type'] = results.groupby(['raceId','driverId']).cumcount()
results['session_type'] = results['session_type'].map({0: 'main', 1: 'sprint'})
```

**If duplicates are Car Sharing (pre-1970):**
```python
# Keep only the final stint (highest laps = last driver in the car)
results = results.sort_values('laps', ascending=False)
results = results.drop_duplicates(subset=['raceId', 'driverId'], keep='first')
# Or: flag all shared-drive rows for separate analysis
results['is_shared_drive'] = results.duplicated(
    subset=['raceId', 'driverId'], keep=False).astype('int8')
```

## 6. Lap Time Validation

**Thresholds:**
- Hard fail: < 30 s (impossible) or > 600 s (corrupt)
- Warning: 300–600 s (Safety Car / VSC / formation lap — real events, not errors)
- Z-score outlier: |z| > 5σ

### Descriptive Statistics

| Metric | Value |
|--------|------:|
| Total records | 588,455 |
| Valid (non-null) | 588,455 |
| Null / missing | 0 (0.0%) |
| Mean | 93.789 s |
| Median | 90.586 s |
| Std dev | 17.076 s |
| Min | 55.404 s |
| Max | 585.712 s |
| p5 | 74.777 s |
| p95 | 121.437 s |

### Threshold Check

| Check | Count | % of Valid | Severity | Result |
|-------|------:|-----------:|----------|:------:|
| Negative values | 0 | 0.0% | ❌ Corrupt | ✅ PASS |
| < 30 s (too fast) | 0 | 0.0% | ❌ Corrupt | ✅ PASS |
| 300–600 s (SC/VSC laps) | 82 | 0.0% | ⚠️ Warning | ℹ️ Expected |
| > 600 s (corrupt) | 0 | 0.0% | ❌ Corrupt | ✅ PASS |
| **Hard-fail total** | **0** | **0.0%** | | **✅ PASS** |

> ℹ️ **SC/VSC laps are not data errors.** Safety Car and Virtual Safety Car periods routinely produce lap times of 3–5 minutes. These should be **excluded from race-pace modeling** but retained for full-race analysis.

**Recommended handling in pipeline:**
```python
# Flag SC/VSC laps rather than dropping them
lap_times['is_slow_lap'] = lap_times['lap_time_ms'] > 300000
# Use only normal laps for pace analysis
normal_laps = lap_times[~lap_times['is_slow_lap']]
```

### Statistical Outlier Detection (Z-Score)

> Flags lap times where |z| > 5 (more than 5 standard deviations from the mean).

| Metric | Value |
|--------|------:|
| Mean ± 1σ | 93.8 s ± 17.1 s |
| Total outliers (\|z\| > 5) | 1,442 (0.2%) |
| Of those: SC/VSC overlap (already flagged above) | 82 |
| Genuinely unexplained outliers | 1,360 |
| Outlier check | ❌ FAIL |

**Top outlier records (up to 10):**

| raceId | driverId | Lap | lap_time_s | z-score | Likely cause |
|-------:|---------:|----:|-----------:|--------:|--------------|
| 83 | 13 | 43 | 585.7 | +28.81 | SC/VSC or red flag |
| 167 | 23 | 10 | 564.0 | +27.54 | SC/VSC or red flag |
| 1100 | 856 | 54 | 558.6 | +27.22 | SC/VSC or red flag |
| 1092 | 830 | 3 | 553.8 | +26.94 | SC/VSC or red flag |
| 1092 | 839 | 3 | 553.3 | +26.91 | SC/VSC or red flag |
| 1092 | 844 | 3 | 552.8 | +26.88 | SC/VSC or red flag |
| 1092 | 1 | 3 | 552.2 | +26.85 | SC/VSC or red flag |
| 1092 | 815 | 3 | 552.0 | +26.83 | SC/VSC or red flag |
| 1092 | 4 | 3 | 551.3 | +26.79 | SC/VSC or red flag |
| 1092 | 847 | 3 | 550.8 | +26.76 | SC/VSC or red flag |

## 7. Status & DNF Validation

**Status integration:** ✅ PASS
**Total result entries mapped:** 26,759
**Unmapped statusId (orphan):** 0 (0.0%)  →  ✅ PASS

### Race Outcome Summary

| Category | Count | % of Results |
|----------|------:|-------------:|
| ✅ Finished (incl. lapped) | 15,161 | 56.7% |
| ❌ DNF / Retirement | 11,404 | 42.6% |
| ❓ Other / Unclassified | 194 | 0.7% |
| **Total** | **26,759** | **100%** |

### ❓ Unclassified Status Breakdown

> These 194 records (0.7%) did not match Finished or DNF classifiers. Review and reclassify as needed.

| Status | Count | % of Other |
|--------|------:|-----------:|
| Not classified | 172 | 88.7% |
| 107% Rule | 9 | 4.6% |
| Injured | 7 | 3.6% |
| Stalled | 2 | 1.0% |
| Driver Seat | 1 | 0.5% |
| Not restarted | 1 | 0.5% |
| Underweight | 1 | 0.5% |
| Seat | 1 | 0.5% |

### Top 10 DNF Causes

| Cause | Count | % of All DNFs |
|-------|------:|--------------:|
| Engine | 2,026 | 17.8% |
| Accident | 1,062 | 9.3% |
| Did not qualify | 1,025 | 9.0% |
| Collision | 854 | 7.5% |
| Gearbox | 810 | 7.1% |
| Spun off | 795 | 7.0% |
| Suspension | 431 | 3.8% |
| Did not prequalify | 331 | 2.9% |
| Transmission | 321 | 2.8% |
| Electrical | 316 | 2.8% |

### Finished Status Breakdown

| Status | Count | % of Finished |
|--------|------:|--------------:|
| Finished | 7,674 | 50.6% |
| +1 Lap | 4,037 | 26.6% |
| +2 Laps | 1,613 | 10.6% |
| +3 Laps | 731 | 4.8% |
| +4 Laps | 405 | 2.7% |
| +5 Laps | 221 | 1.5% |
| +6 Laps | 153 | 1.0% |
| +7 Laps | 100 | 0.7% |
| +8 Laps | 52 | 0.3% |
| +9 Laps | 38 | 0.3% |
| +10 Laps | 32 | 0.2% |
| +11 Laps | 17 | 0.1% |
| +13 Laps | 13 | 0.1% |
| +12 Laps | 12 | 0.1% |
| +14 Laps | 12 | 0.1% |
| +15 Laps | 9 | 0.1% |
| +17 Laps | 7 | 0.0% |
| +16 Laps | 7 | 0.0% |
| +24 Laps | 4 | 0.0% |
| +18 Laps | 4 | 0.0% |
| +22 Laps | 4 | 0.0% |
| +19 Laps | 4 | 0.0% |
| +25 Laps | 3 | 0.0% |
| +26 Laps | 1 | 0.0% |
| +44 Laps | 1 | 0.0% |
| +29 Laps | 1 | 0.0% |
| +30 Laps | 1 | 0.0% |
| +23 Laps | 1 | 0.0% |
| +21 Laps | 1 | 0.0% |
| +42 Laps | 1 | 0.0% |
| +46 Laps | 1 | 0.0% |
| +20 Laps | 1 | 0.0% |


────────────────────────────────────────────────────────────

_Generated by `validate_data.py`. Re-run at any time before modeling to verify data integrity._