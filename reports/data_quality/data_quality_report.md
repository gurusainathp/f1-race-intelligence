# Data Quality Report

> **Generated:** 2026-03-04 23:10:34  
> **Source (raw):** `data\interim`  
> **Source (features):** `data\processed\features`  
> **Tables loaded:** 9  
> **Feature tables loaded:** 6 / 6  

────────────────────────────────────────────────────────────


## 0. Quality Scorecard

**Overall:** ✅ PASS

| # | Check | Result |
|---|-------|:------:|
| 1 | No unjustified high-null columns | ✅ PASS |
| 2 | Schema: all expected columns present | ✅ PASS |
| 3 | Foreign key integrity | ✅ PASS |
| 4 | No unexplained duplicate race-driver records | ✅ PASS |
| 5 | Lap time: no corrupt values | ✅ PASS |
| 6 | Status integration with results intact | ✅ PASS |
| 7 | Feature tables: no duplicate composite keys | ✅ PASS |
| 8 | Feature values: no impossible values (FAIL checks) | ✅ PASS |
| 9 | Points reconciliation: no season delta > 5 pts | ✅ PASS |
| 10 | No data leakage: post-race features in pre-race tables | ✅ PASS |
| 11 | Target distribution: podium rate within expected band | ✅ PASS |


## 1. Dataset Inventory

| Table | Rows | Columns | Null Cells | Null % |
|-------|-----:|--------:|-----------:|-------:|
| `circuits` | 77 | 8 | 0 | 0.0% |
| `constructors` | 212 | 4 | 0 | 0.0% |
| `drivers` | 861 | 9 | 1,559 | 20.1% |
| `lap_times` | 588,455 | 5 | 0 | 0.0% |
| `pit_stops` | 11,371 | 5 | 534 | 0.9% |
| `qualifying` | 10,494 | 10 | 11,781 | 11.2% |
| `races` | 1,125 | 11 | 5,265 | 42.5% |
| `results` | 26,759 | 22 | 124,523 | 21.2% |
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
| `position` | int64 | 0 | 0.00% | ℹ️ Justified | ~41% null in results — expected: all DNFs have null position by design. Confirmed: null position count == DNF flag count (zero unexplained nulls). 2 lapped-finisher gaps in Kaggle source backfilled from positionOrder in clean_data.py |
| `lap_time_ms` | float64 | 0 | 0.00% | ✅ Clean | — |

### `pit_stops`
- **Rows:** 11,371  |  **Columns:** 5  |  **Columns with nulls:** 1

| Column | Type | Null Count | Null % | Severity | Note |
|--------|------|----------:|-------:|----------|------|
| `pit_duration_ms` | float64 | 534 | 4.70% | ℹ️ Justified | ~4.7% null in pit_stops — clustered feed failures in specific races (2023 Australian GP 70.8%, 2021 Saudi GP 74.5%, etc.). Not random — null means data was never recorded. Use pit_data_incomplete flag to exclude affected races from strategy models. Do NOT impute |
| `raceId` | int64 | 0 | 0.00% | ✅ Clean | — |
| `driverId` | int64 | 0 | 0.00% | ✅ Clean | — |
| `stop` | int64 | 0 | 0.00% | ✅ Clean | — |
| `lap` | int64 | 0 | 0.00% | ✅ Clean | — |

### `qualifying`
- **Rows:** 10,494  |  **Columns:** 10  |  **Columns with nulls:** 4

| Column | Type | Null Count | Null % | Severity | Note |
|--------|------|----------:|-------:|----------|------|
| `q3_ms` | float64 | 6,865 | 65.42% | ℹ️ Justified | Q3 only exists for top-10 qualifiers in 3-part format introduced 2006. Structural ~65% null for all post-2006 races; 100% null for all pre-2006 |
| `q2_ms` | float64 | 4,625 | 44.07% | ℹ️ Justified | Q2 null expected for single-session formats (pre-1996, 2003-2005). Post-2006: driver eliminated in Q1 or did not set a time (DNS/DQ/107%) |
| `best_quali_ms` | float64 | 157 | 1.50% | ℹ️ Justified | Mirrors q1_ms nulls exactly — derived as min(q1_ms, q2_ms, q3_ms). Null only where all session times are null (same causes as q1_ms above) |
| `q1_ms` | float64 | 134 | 1.28% | ℹ️ Justified | ~1.3% null in qualifying — confirmed data gaps: entire races missing from Kaggle source (patched where possible), 107% failures, DNS/injury before Q1, modern era DQ/crash/mechanical before setting a time. Not imputable |
| `raceId` | int64 | 0 | 0.00% | ✅ Clean | — |
| `qualifyId` | int64 | 0 | 0.00% | ✅ Clean | — |
| `position` | int64 | 0 | 0.00% | ℹ️ Justified | ~41% null in results — expected: all DNFs have null position by design. Confirmed: null position count == DNF flag count (zero unexplained nulls). 2 lapped-finisher gaps in Kaggle source backfilled from positionOrder in clean_data.py |
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
- **Rows:** 26,759  |  **Columns:** 22  |  **Columns with nulls:** 9

| Column | Type | Null Count | Null % | Severity | Note |
|--------|------|----------:|-------:|----------|------|
| `time` | object | 19,079 | 71.30% | ℹ️ Justified | Finish time only for classified finishers (DNFs = null by design) |
| `milliseconds` | float64 | 19,079 | 71.30% | ℹ️ Justified | Finish time only for classified finishers (DNFs = null by design) |
| `fastestLapSpeed` | float64 | 18,507 | 69.16% | ℹ️ Justified | Fastest lap data standardised from 2004 season only |
| `fastestLap` | float64 | 18,507 | 69.16% | ℹ️ Justified | Fastest lap data standardised from 2004 season only |
| `fastestLapTime_ms` | float64 | 18,507 | 69.16% | ℹ️ Justified | Fastest lap data standardised from 2004 season only |
| `rank` | float64 | 18,249 | 68.20% | ℹ️ Justified | Fastest lap ranking introduced from 2019 season only |
| `position` | float64 | 10,951 | 40.92% | ℹ️ Justified | ~41% null in results — expected: all DNFs have null position by design. Confirmed: null position count == DNF flag count (zero unexplained nulls). 2 lapped-finisher gaps in Kaggle source backfilled from positionOrder in clean_data.py |
| `grid` | float64 | 1,638 | 6.12% | ℹ️ Justified | ~6% null in results — grid=0 recoded to NaN. Two causes: (1) pre-1996 Kaggle missing-data sentinel (historic data gap, grid_pit_lane=0); (2) post-1995 genuine pit-lane starts (grid_pit_lane=1). Do NOT use grid alone for pre-1996 analysis |
| `number` | float64 | 6 | 0.02% | ℹ️ Justified | Permanent driver numbers introduced in 2014 only |
| `raceId` | int64 | 0 | 0.00% | ✅ Clean | — |
| `driverId` | int64 | 0 | 0.00% | ✅ Clean | — |
| `constructorId` | int64 | 0 | 0.00% | ✅ Clean | — |
| `resultId` | int64 | 0 | 0.00% | ✅ Clean | — |
| `points` | float64 | 0 | 0.00% | ✅ Clean | — |
| `laps` | int64 | 0 | 0.00% | ✅ Clean | — |
| `positionText` | object | 0 | 0.00% | ✅ Clean | — |
| `positionOrder` | int64 | 0 | 0.00% | ✅ Clean | — |
| `statusId` | int64 | 0 | 0.00% | ✅ Clean | — |
| `grid_pit_lane` | int64 | 0 | 0.00% | ℹ️ Justified | Binary flag: 1 = post-1995 pit-lane start, 0 = not a pit-lane start or pre-1996 data gap. Always filled — never null |
| `is_dnf` | int64 | 0 | 0.00% | ✅ Clean | — |
| `is_podium` | int64 | 0 | 0.00% | ✅ Clean | — |
| `is_shared_drive` | int64 | 0 | 0.00% | ✅ Clean | — |

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
| ℹ️ Justified | High null rate expected due to era/format/design constraints |
| 🔍 Investigate | Null rate requires manual review before modeling (none currently) |

## 3. Schema Drift Check

**Overall:** ✅ PASS

| Table | Missing Columns | Unexpected Columns | Result |
|-------|-----------------|-------------------|:------:|
| `constructors` | — | — | ✅ PASS |
| `drivers` | — | `code`, `dob`, `full_name`, `number` | ✅ PASS |
| `lap_times` | — | — | ✅ PASS |
| `races` | — | `fp1_date`, `fp2_date`, `fp3_date`, `quali_date`, `sprint_date` | ✅ PASS |
| `results` | — | `fastestLap`, `fastestLapSpeed`, `fastestLapTime_ms`, `is_dnf`, `is_podium`, `is_shared_drive`, `milliseconds`, `number`, `positionOrder`, `positionText`, `rank`, `time` | ✅ PASS |
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
**Duplicate pairs found:** 91
**Rows affected:** 176 / 26,759 (0.7%)

**Distinct races affected:** 42
**Affected raceIds:** `540`, `717`, `733`, `742`, `745`, `746`, `766`, `770`, `774`, `776`, `777`, `779`, `780`, `783`, `784`, `785`, `787`, `788`, `789`, `791`, `792`, `793`, `795`, `797`, `800`, `801`, `803`, `804`, `806`, `809` _(showing first 30 of 42)_

### Duplicate Root Cause Classification

| Category | Pairs | Interpretation | Scorecard |
|----------|------:|----------------|:---------:|
| 🏛️ Dual Constructor | 16 | Driver raced for 2 teams in same event — expected | ✅ Ignored |
| 🤝 Shared Drive | 69 | Same team, two result rows — expected | ✅ Ignored |
| ❓ Unexplained | 0 | constructorId absent or null | ✅ None |

**Overall:** ✅ PASS

## 6. Lap Time Validation

**Thresholds:**
- Hard fail: < 30 s or > 600 s
- Warning: 300–600 s (SC/VSC)
- Z-score outlier: |z| > 5σ

| Metric | Value |
|--------|------:|
| Total records | 588,455 |
| Valid (non-null) | 588,455 |
| Null / missing | 0 (0.0%) |
| Mean | 93.789 s |
| Median | 90.586 s |
| Min | 55.404 s |
| Max | 585.712 s |

| Check | Count | Severity | Result |
|-------|------:|----------|:------:|
| Negative values | 0 | ❌ Corrupt | ✅ PASS |
| < 30 s | 0 | ❌ Corrupt | ✅ PASS |
| SC/VSC laps | 82 | ⚠️ Warning | ℹ️ Expected |
| > 600 s | 0 | ❌ Corrupt | ✅ PASS |
| **Hard-fail total** | **0** | | **✅ PASS** |

## 7. Status & DNF Validation

**Unmapped statusId:** 0 → ✅ PASS

| Category | Count | % |
|----------|------:|--:|
| ✅ Finished | 15,161 | 56.7% |
| ❌ DNF | 11,409 | 42.6% |
| ❓ Other | 189 | 0.7% |

### Top 10 DNF Causes

| Cause | Count |
|-------|------:|
| Engine | 2,026 |
| Accident | 1,062 |
| Did not qualify | 1,025 |
| Collision | 854 |
| Gearbox | 810 |
| Spun off | 795 |
| Suspension | 431 |
| Did not prequalify | 331 |
| Transmission | 321 |
| Electrical | 316 |

## 8. Feature Table — Duplicate Key Check

| Table | Key Columns | Rows | Duplicate Pairs | Unexplained | Result |
|-------|-------------|-----:|----------------:|------------:|:------:|
| `driver_race_full` | `raceId`, `driverId` | 26,759 | 91 | 0 | ✅ PASS |
| `driver_race_pre` | `raceId`, `driverId` | 26,759 | 91 | 0 | ✅ PASS |
| `driver_season` | `driverId`, `race_year` | 3,211 | 0 | 0 | ✅ PASS |
| `constructor_season` | `constructorId`, `race_year` | 1,111 | 0 | 0 | ✅ PASS |
| `driver_race_rolling` | `raceId`, `driverId` | 26,759 | 91 | 0 | ✅ PASS |
| `constructor_race_rolling` | `constructorId`, `race_year`, `round` | 13,028 | 0 | 0 | ✅ PASS |

**Overall:** ✅ PASS

## 9. Feature Value Bounds Check

| Table | Column | Check | Violations | Severity | Result |
|-------|--------|-------|----------:|:--------:|:------:|
| `constructor_race_rolling` | `rolling_cumulative_points` | `rolling_cumulative_points` < 0 | 0 | ❌ FAIL | ✅ PASS |
| `constructor_race_rolling` | `rolling_dnf_rate` | `rolling_dnf_rate` < 0 | 0 | ❌ FAIL | ✅ PASS |
| `constructor_race_rolling` | `rolling_dnf_rate` | `rolling_dnf_rate` > 1 | 0 | ❌ FAIL | ✅ PASS |
| `constructor_race_rolling` | `rolling_races_counted` | `rolling_races_counted` < 0 | 0 | ❌ FAIL | ✅ PASS |
| `constructor_season` | `dnf_rate` | `dnf_rate` < 0 | 0 | ❌ FAIL | ✅ PASS |
| `constructor_season` | `dnf_rate` | `dnf_rate` > 1 | 0 | ❌ FAIL | ✅ PASS |
| `constructor_season` | `win_rate` | `win_rate` > 1 | 0 | ❌ FAIL | ✅ PASS |
| `constructor_season` | `driver_count` | `driver_count` < 1 | 0 | ❌ FAIL | ✅ PASS |
| `constructor_season` | `driver_spread_avg_finish` | `driver_spread_avg_finish` < 0 | 0 | ⚠️ WARN | ✅ PASS |
| `constructor_season` | `driver_spread_total_points` | `driver_spread_total_points` < 0 | 0 | ⚠️ WARN | ✅ PASS |
| `driver_race_full` | `grid` | `grid` < 0 | 0 | ❌ FAIL | ✅ PASS |
| `driver_race_full` | `finish_position` | `finish_position` < 1 | 0 | ❌ FAIL | ✅ PASS |
| `driver_race_full` | `positions_gained` | `positions_gained` < -30 | 0 | ❌ FAIL | ✅ PASS |
| `driver_race_full` | `positions_gained` | `positions_gained` > 33 | 0 | ❌ FAIL | ✅ PASS |
| `driver_race_full` | `points` | `points` < 0 | 0 | ❌ FAIL | ✅ PASS |
| `driver_race_full` | `pit_stop_count` | `pit_stop_count` < 0 | 0 | ❌ FAIL | ✅ PASS |
| `driver_race_full` | `avg_pit_duration_ms` | `avg_pit_duration_ms` < 0 | 0 | ❌ FAIL | ✅ PASS |
| `driver_race_full` | `is_dnf` | `is_dnf` < 0 | 0 | ❌ FAIL | ✅ PASS |
| `driver_race_full` | `is_dnf` | `is_dnf` > 1 | 0 | ❌ FAIL | ✅ PASS |
| `driver_race_pre` | `grid` | `grid` < 0 | 0 | ❌ FAIL | ✅ PASS |
| `driver_race_rolling` | `rolling_cumulative_points` | `rolling_cumulative_points` < 0 | 0 | ❌ FAIL | ✅ PASS |
| `driver_race_rolling` | `rolling_cumulative_podiums` | `rolling_cumulative_podiums` < 0 | 0 | ❌ FAIL | ✅ PASS |
| `driver_race_rolling` | `rolling_cumulative_wins` | `rolling_cumulative_wins` < 0 | 0 | ❌ FAIL | ✅ PASS |
| `driver_race_rolling` | `rolling_dnf_rate` | `rolling_dnf_rate` < 0 | 0 | ❌ FAIL | ✅ PASS |
| `driver_race_rolling` | `rolling_dnf_rate` | `rolling_dnf_rate` > 1 | 0 | ❌ FAIL | ✅ PASS |
| `driver_race_rolling` | `rolling_races_counted` | `rolling_races_counted` < 0 | 0 | ❌ FAIL | ✅ PASS |
| `driver_season` | `dnf_rate` | `dnf_rate` < 0 | 0 | ❌ FAIL | ✅ PASS |
| `driver_season` | `dnf_rate` | `dnf_rate` > 1 | 0 | ❌ FAIL | ✅ PASS |
| `driver_season` | `win_rate` | `win_rate` > 1 | 0 | ❌ FAIL | ✅ PASS |
| `driver_season` | `podium_rate` | `podium_rate` > 1 | 0 | ❌ FAIL | ✅ PASS |
| `driver_season` | `races_entered` | `races_entered` < 1 | 0 | ❌ FAIL | ✅ PASS |
| `driver_season` | `avg_finish_position` | `avg_finish_position` < 1 | 0 | ❌ FAIL | ✅ PASS |

**Overall (FAIL-severity checks only):** ✅ PASS

## 10. Points Reconciliation — Driver vs Constructor Totals

**Tolerance:** PASS ≤ 2.0 pts | WARN ≤ 5.0 pts | FAIL > 5.0 pts
**Scorecard:** ✅ PASS

| Season | Driver Total | Constructor Total | Delta | Result |
|-------:|-------------:|------------------:|------:|:------:|
| 1950 | 168.0 | 168.0 | 0.0 | ✅ PASS |
| 1951 | 192.0 | 192.0 | 0.0 | ✅ PASS |
| 1952 | 192.0 | 192.0 | 0.0 | ✅ PASS |
| 1953 | 216.0 | 216.0 | 0.0 | ✅ PASS |
| 1954 | 215.6 | 215.6 | 0.0 | ✅ PASS |
| 1955 | 168.0 | 168.0 | 0.0 | ✅ PASS |
| 1956 | 192.0 | 192.0 | 0.0 | ✅ PASS |
| 1957 | 192.0 | 192.0 | 0.0 | ✅ PASS |
| 1958 | 259.0 | 259.0 | 0.0 | ✅ PASS |
| 1959 | 216.0 | 216.0 | 0.0 | ✅ PASS |
| 1960 | 236.0 | 236.0 | 0.0 | ✅ PASS |
| 1961 | 200.0 | 200.0 | 0.0 | ✅ PASS |
| 1962 | 225.0 | 225.0 | 0.0 | ✅ PASS |
| 1963 | 246.0 | 246.0 | 0.0 | ✅ PASS |
| 1964 | 250.0 | 250.0 | 0.0 | ✅ PASS |
| 1965 | 250.0 | 250.0 | 0.0 | ✅ PASS |
| 1966 | 221.0 | 221.0 | 0.0 | ✅ PASS |
| 1967 | 275.0 | 275.0 | 0.0 | ✅ PASS |
| 1968 | 298.0 | 298.0 | 0.0 | ✅ PASS |
| 1969 | 275.0 | 275.0 | 0.0 | ✅ PASS |
| 1970 | 324.0 | 324.0 | 0.0 | ✅ PASS |
| 1971 | 275.0 | 275.0 | 0.0 | ✅ PASS |
| 1972 | 300.0 | 300.0 | 0.0 | ✅ PASS |
| 1973 | 375.0 | 375.0 | 0.0 | ✅ PASS |
| 1974 | 375.0 | 375.0 | 0.0 | ✅ PASS |
| 1975 | 325.0 | 325.0 | 0.0 | ✅ PASS |
| 1976 | 400.0 | 400.0 | 0.0 | ✅ PASS |
| 1977 | 425.0 | 425.0 | 0.0 | ✅ PASS |
| 1978 | 400.0 | 400.0 | 0.0 | ✅ PASS |
| 1979 | 375.0 | 375.0 | 0.0 | ✅ PASS |
| 1980 | 350.0 | 350.0 | 0.0 | ✅ PASS |
| 1981 | 375.0 | 375.0 | 0.0 | ✅ PASS |
| 1982 | 399.0 | 399.0 | 0.0 | ✅ PASS |
| 1983 | 369.0 | 369.0 | 0.0 | ✅ PASS |
| 1984 | 383.5 | 383.5 | 0.0 | ✅ PASS |
| 1985 | 400.0 | 400.0 | 0.0 | ✅ PASS |
| 1986 | 400.0 | 400.0 | 0.0 | ✅ PASS |
| 1987 | 398.0 | 398.0 | 0.0 | ✅ PASS |
| 1988 | 400.0 | 400.0 | 0.0 | ✅ PASS |
| 1989 | 400.0 | 400.0 | 0.0 | ✅ PASS |
| 1990 | 400.0 | 400.0 | 0.0 | ✅ PASS |
| 1991 | 403.0 | 403.0 | 0.0 | ✅ PASS |
| 1992 | 416.0 | 416.0 | 0.0 | ✅ PASS |
| 1993 | 416.0 | 416.0 | 0.0 | ✅ PASS |
| 1994 | 416.0 | 416.0 | 0.0 | ✅ PASS |
| 1995 | 442.0 | 442.0 | 0.0 | ✅ PASS |
| 1996 | 416.0 | 416.0 | 0.0 | ✅ PASS |
| 1997 | 442.0 | 442.0 | 0.0 | ✅ PASS |
| 1998 | 416.0 | 416.0 | 0.0 | ✅ PASS |
| 1999 | 416.0 | 416.0 | 0.0 | ✅ PASS |
| 2000 | 442.0 | 442.0 | 0.0 | ✅ PASS |
| 2001 | 442.0 | 442.0 | 0.0 | ✅ PASS |
| 2002 | 442.0 | 442.0 | 0.0 | ✅ PASS |
| 2003 | 624.0 | 624.0 | 0.0 | ✅ PASS |
| 2004 | 702.0 | 702.0 | 0.0 | ✅ PASS |
| 2005 | 738.0 | 738.0 | 0.0 | ✅ PASS |
| 2006 | 702.0 | 702.0 | 0.0 | ✅ PASS |
| 2007 | 663.0 | 663.0 | 0.0 | ✅ PASS |
| 2008 | 702.0 | 702.0 | 0.0 | ✅ PASS |
| 2009 | 643.5 | 643.5 | 0.0 | ✅ PASS |
| 2010 | 1,919.0 | 1,919.0 | 0.0 | ✅ PASS |
| 2011 | 1,919.0 | 1,919.0 | 0.0 | ✅ PASS |
| 2012 | 2,020.0 | 2,020.0 | 0.0 | ✅ PASS |
| 2013 | 1,919.0 | 1,919.0 | 0.0 | ✅ PASS |
| 2014 | 2,020.0 | 2,020.0 | 0.0 | ✅ PASS |
| 2015 | 1,919.0 | 1,919.0 | 0.0 | ✅ PASS |
| 2016 | 2,121.0 | 2,121.0 | 0.0 | ✅ PASS |
| 2017 | 2,020.0 | 2,020.0 | 0.0 | ✅ PASS |
| 2018 | 2,121.0 | 2,121.0 | 0.0 | ✅ PASS |
| 2019 | 2,140.0 | 2,140.0 | 0.0 | ✅ PASS |
| 2020 | 1,734.0 | 1,734.0 | 0.0 | ✅ PASS |
| 2021 | 2,189.5 | 2,189.5 | 0.0 | ✅ PASS |
| 2022 | 2,242.0 | 2,242.0 | 0.0 | ✅ PASS |
| 2023 | 2,242.0 | 2,242.0 | 0.0 | ✅ PASS |
| 2024 | 2,443.0 | 2,443.0 | 0.0 | ✅ PASS |

## 11. Data Leakage Detection

**Table:** `driver_race_pre.parquet`
**Leaked columns detected:** 0
**Result:** ✅ PASS


### Season & Rolling Tables (Advisory)

| Table | Columns | Risk | Notes |
|-------|---------|------|-------|
| `driver_season` | 27 | ✅ Low | Historical full-season aggregates (prior season). Low risk. |
| `constructor_season` | 22 | ✅ Low | Historical full-season aggregates (prior season). Low risk. |
| `driver_race_rolling` | 12 | ✅ Low | Cumulative within-season stats — shift(1) applied. Verified leakage-free by design. |
| `constructor_race_rolling` | 9 | ✅ Low | Cumulative within-season stats — shift(1) applied. Verified leakage-free by design. |

## 12. Target Distribution — `is_podium`

### Overall

| Metric | Value |
|--------|------:|
| Total driver-race rows | 26,759 |
| Podium (is_podium = 1) | 3,396 (12.69%) |
| Non-podium (is_podium = 0) | 23,363 (87.3%) |
| Class imbalance ratio | 6.9 : 1 |
| Expected band | [12%, 18%] |
| **Result** | **✅ PASS** |

### By Era (Pre-2000 vs Post-2000)

| Era | Rows | Podiums | Rate | Note |
|-----|-----:|--------:|-----:|------|
| Pre-2000 (1950–1999) | 16,680 | 1,959 | 11.74% | ⚠️ Below expected band — larger grids pre-2000 (up to 26 cars) |
| Post-2000 (2000–) | 10,079 | 1,437 | 14.26% | ✅ Within expected band |

### By Constructor Dominance Era

| Era | Years | Rows | Podiums | Rate |
|-----|-------|-----:|--------:|-----:|
| Pre-turbo (1950–1982) | 1950–1982 | 9,224 | 1,141 | 12.37% |
| Turbo era (1983–1988) | 1983–1988 | 2,586 | 284 | 10.98% |
| Normally aspirated (1989–2005) | 1989–2005 | 7,035 | 846 | 12.03% |
| V8 era (2006–2013) | 2006–2013 | 3,288 | 441 | 13.41% |
| Hybrid era (2014–2021) | 2014–2021 | 3,267 | 480 | 14.69% |
| Ground effect (2022–) | 2022–present | 1,359 | 204 | 15.01% |

### Top 10 Constructors by Podium Count

> Informational — shows constructor dominance. High concentration here is
> expected in F1 and is not a data quality issue.

| Rank | constructorId | Podiums | Podium Rate | Races Entered |
|-----:|--------------:|--------:|------------:|--------------:|
| 1 | 6 | 841 | 34.5% | 2,439 |
| 2 | 1 | 508 | 26.4% | 1,923 |
| 3 | 3 | 313 | 18.7% | 1,676 |
| 4 | 131 | 298 | 45.7% | 652 |
| 5 | 9 | 282 | 35.8% | 788 |
| 6 | 32 | 114 | 13.1% | 871 |
| 7 | 4 | 103 | 13.1% | 787 |
| 8 | 22 | 102 | 19.6% | 520 |
| 9 | 34 | 78 | 11.8% | 662 |
| 10 | 25 | 77 | 8.7% | 881 |

**Scorecard result:** ✅ PASS  _(fails only if overall podium rate is outside [12%, 18%])_

> ℹ️ Era-level and constructor-level breakdowns are advisory.
> Imbalanced classes are expected and handled at the modeling stage via class weighting or resampling — not by filtering data here.


────────────────────────────────────────────────────────────

_Generated by `validate_data.py`. Re-run at any time before modeling to verify data integrity._