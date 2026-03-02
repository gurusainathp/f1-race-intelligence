# Data Quality Report

> **Generated:** 2026-03-02 22:34:24  
> **Source (raw):** `data\interim`  
> **Source (features):** `data\processed`  
> **Tables loaded:** 9  
> **Feature tables loaded:** 3 / 3  

────────────────────────────────────────────────────────────


## 0. Quality Scorecard

**Overall:** ❌ FAIL

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
| 10 | No data leakage: post-race features in pre-race tables | ❌ FAIL |


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
| 🤝 Shared Drive | 69 | Same team, two result rows — expected (classic car-sharing or teammate-swap stint) | ✅ Ignored |
| ❓ Unexplained | 0 | constructorId absent or null — cannot classify | ✅ None |

> ℹ️ **Shared-drive duplicates are expected.** Each row represents a separate stint entry: either the classic pre-1970 car-sharing format or a driver who later took over their teammate's car in the same race.

**Top affected races (up to 15):**

| raceId | Dual Constructor | Shared Drive | Unexplained |
|-------:|----------------:|-------------:|------------:|
| 800 | 4 | 8 | 0 |
| 792 | 0 | 10 | 0 |
| 809 | 6 | 2 | 0 |
| 791 | 0 | 3 | 0 |
| 788 | 1 | 2 | 0 |
| 828 | 0 | 3 | 0 |
| 780 | 0 | 3 | 0 |
| 777 | 0 | 2 | 0 |
| 785 | 0 | 2 | 0 |
| 797 | 0 | 2 | 0 |
| 839 | 0 | 2 | 0 |
| 789 | 0 | 2 | 0 |
| 814 | 0 | 2 | 0 |
| 815 | 0 | 2 | 0 |
| 793 | 0 | 2 | 0 |

**All duplicate pairs:**

| raceId | driverId | Category |
|-------:|---------:|----------|
| 540 | 229 | 🏛️ Dual Constructor |
| 717 | 373 | 🤝 Shared Drive |
| 733 | 465 | 🏛️ Dual Constructor |
| 742 | 475 | 🏛️ Dual Constructor |
| 745 | 418 | 🤝 Shared Drive |
| 746 | 475 | 🤝 Shared Drive |
| 766 | 541 | 🏛️ Dual Constructor |
| 770 | 479 | 🤝 Shared Drive |
| 774 | 566 | 🤝 Shared Drive |
| 776 | 581 | 🤝 Shared Drive |
| 777 | 501 | 🤝 Shared Drive |
| 777 | 578 | 🤝 Shared Drive |
| 779 | 356 | 🤝 Shared Drive |
| 780 | 475 | 🤝 Shared Drive |
| 780 | 479 | 🤝 Shared Drive |
| 780 | 581 | 🤝 Shared Drive |
| 783 | 501 | 🤝 Shared Drive |
| 784 | 579 | 🤝 Shared Drive |
| 785 | 579 | 🤝 Shared Drive |
| 785 | 608 | 🤝 Shared Drive |
| 787 | 475 | 🤝 Shared Drive |
| 788 | 475 | 🤝 Shared Drive |
| 788 | 501 | 🤝 Shared Drive |
| 788 | 624 | 🏛️ Dual Constructor |
| 789 | 581 | 🤝 Shared Drive |
| 789 | 606 | 🤝 Shared Drive |
| 791 | 554 | 🤝 Shared Drive |
| 791 | 579 | 🤝 Shared Drive |
| 791 | 608 | 🤝 Shared Drive |
| 792 | 427 | 🤝 Shared Drive |
| 792 | 475 | 🤝 Shared Drive |
| 792 | 496 | 🤝 Shared Drive |
| 792 | 501 | 🤝 Shared Drive |
| 792 | 554 | 🤝 Shared Drive |
| 792 | 577 | 🤝 Shared Drive |
| 792 | 633 | 🤝 Shared Drive |
| 792 | 642 | 🤝 Shared Drive |
| 792 | 644 | 🤝 Shared Drive |
| 792 | 648 | 🤝 Shared Drive |
| 793 | 554 | 🤝 Shared Drive |
| 793 | 607 | 🤝 Shared Drive |
| 795 | 554 | 🤝 Shared Drive |
| 797 | 501 | 🤝 Shared Drive |
| 797 | 608 | 🤝 Shared Drive |
| 800 | 509 | 🤝 Shared Drive |
| 800 | 518 | 🤝 Shared Drive |
| 800 | 529 | 🤝 Shared Drive |
| 800 | 556 | 🏛️ Dual Constructor |
| 800 | 593 | 🤝 Shared Drive |
| 800 | 611 | 🤝 Shared Drive |
_(showing first 50 of 85 pairs)_

**Overall:** ✅ PASS

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

> ℹ️ **SC/VSC laps are not data errors.** Safety Car and Virtual Safety Car periods routinely produce lap times of 3–5 minutes.

```python
lap_times['is_slow_lap'] = lap_times['lap_time_ms'] > 300000
normal_laps = lap_times[~lap_times['is_slow_lap']]
```

### Statistical Outlier Detection (Z-Score) — Advisory

> Flags lap times where |z| > 5. Advisory only — does not affect scorecard.

| Metric | Value |
|--------|------:|
| Mean ± 1σ | 93.8 s ± 17.1 s |
| Total outliers (\|z\| > 5) | 1,442 (0.2%) |
| Of those: SC/VSC overlap (already flagged above) | 82 |
| Genuinely unexplained outliers (<300s) | 1,360 |
| Outlier check | ℹ️ Advisory (1360 unexplained) |

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
| ❌ DNF / Retirement | 11,409 | 42.6% |
| ❓ Other / Unclassified | 189 | 0.7% |
| **Total** | **26,759** | **100%** |

### ❓ Unclassified Status Breakdown

> These 189 records (0.7%) did not match Finished or DNF classifiers. Review and reclassify as needed.

| Status | Count | % of Other |
|--------|------:|-----------:|
| Not classified | 172 | 91.0% |
| 107% Rule | 9 | 4.8% |
| Injured | 7 | 3.7% |
| Underweight | 1 | 0.5% |

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

## 8. Feature Table — Duplicate Key Check

| Table | Key Columns | Rows | Duplicate Pairs | Unexplained | Result |
|-------|-------------|-----:|----------------:|------------:|:------:|
| `driver_race` | `raceId`, `driverId` | 26,759 | 91 | 0 | ✅ PASS |

**`driver_race` duplicate classification** (91 pairs total):

| Category | Pairs | Interpretation | Scorecard |
|----------|------:|----------------|:---------:|
| 🏛️ Dual Constructor | 16 | Driver raced for 2 teams in same event — expected | ✅ Ignored |
| 🤝 Shared Drive | 69 | Same team, two result rows (car-sharing or teammate-swap) — expected | ✅ Ignored |
| ❓ Unexplained | 0 | constructorId absent or null — cannot classify | ✅ None |

| `driver_season` | `driverId`, `race_year` | 3,211 | 0 | 0 | ✅ PASS |
| `constructor_season` | `constructorId`, `race_year` | 1,111 | 0 | 0 | ✅ PASS |

**Overall:** ✅ PASS

> ℹ️ For `driver_race`, dual-constructor and shared-drive duplicates are structurally expected (mirrors Section 5 logic). Only duplicates where `constructorId` is absent or null fail the scorecard.

## 9. Feature Value Bounds Check

| Table | Column | Check | Violations | Severity | Result |
|-------|--------|-------|----------:|:--------:|:------:|
| `constructor_season` | `dnf_rate` | `dnf_rate` < 0 | 0 | ❌ FAIL | ✅ PASS |
| `constructor_season` | `dnf_rate` | `dnf_rate` > 1 | 0 | ❌ FAIL | ✅ PASS |
| `constructor_season` | `win_rate` | `win_rate` > 1 | 0 | ❌ FAIL | ✅ PASS |
| `constructor_season` | `driver_count` | `driver_count` < 1 | 0 | ❌ FAIL | ✅ PASS |
| `constructor_season` | `driver_spread_avg_finish` | `driver_spread_avg_finish` < 0 | 0 | ⚠️ WARN | ✅ PASS |
| `constructor_season` | `driver_spread_total_points` | `driver_spread_total_points` < 0 | 0 | ⚠️ WARN | ✅ PASS |
| `driver_race` | `grid` | `grid` < 0 | 0 | ❌ FAIL | ✅ PASS |
| `driver_race` | `finish_position` | `finish_position` < 1 | 0 | ❌ FAIL | ✅ PASS |
| `driver_race` | `positions_gained` | `positions_gained` < -30 | 0 | ❌ FAIL | ✅ PASS |
| `driver_race` | `positions_gained` | `positions_gained` > 33 | 0 | ❌ FAIL | ✅ PASS |
| `driver_race` | `points` | `points` < 0 | 0 | ❌ FAIL | ✅ PASS |
| `driver_race` | `pit_stop_count` | `pit_stop_count` < 0 | 0 | ❌ FAIL | ✅ PASS |
| `driver_race` | `avg_pit_duration_ms` | `avg_pit_duration_ms` < 0 | 0 | ❌ FAIL | ✅ PASS |
| `driver_race` | `is_dnf` | `is_dnf` < 0 | 0 | ❌ FAIL | ✅ PASS |
| `driver_race` | `is_dnf` | `is_dnf` > 1 | 0 | ❌ FAIL | ✅ PASS |
| `driver_season` | `dnf_rate` | `dnf_rate` < 0 | 0 | ❌ FAIL | ✅ PASS |
| `driver_season` | `dnf_rate` | `dnf_rate` > 1 | 0 | ❌ FAIL | ✅ PASS |
| `driver_season` | `win_rate` | `win_rate` > 1 | 0 | ❌ FAIL | ✅ PASS |
| `driver_season` | `podium_rate` | `podium_rate` > 1 | 0 | ❌ FAIL | ✅ PASS |
| `driver_season` | `races_entered` | `races_entered` < 1 | 0 | ❌ FAIL | ✅ PASS |
| `driver_season` | `avg_finish_position` | `avg_finish_position` < 1 | 0 | ❌ FAIL | ✅ PASS |

**Overall (FAIL-severity checks only):** ✅ PASS

> _WARN-severity violations are advisory and do not affect the scorecard._

## 10. Points Reconciliation — Driver vs Constructor Totals

**Tolerance bands:**  PASS ≤ 2.0 pts  |  WARN ≤ 5.0 pts  |  FAIL > 5.0 pts

### Season-Level Summary

| Outcome | Seasons | % of Seasons |
|---------|--------:|-------------:|
| ✅ PASS (delta ≤ 2.0) | 75 | 100.0% |
| ⚠️ WARN (2.0 < delta ≤ 5.0) | 0 | 0.0% |
| ❌ FAIL (delta > 5.0) | 0 | 0.0% |

**Scorecard result:** ✅ PASS  _(fails only on delta > 5.0)_

### Per-Season Detail

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
> ℹ️ **WARN seasons are advisory.** Small deltas (2–5 pts) are common in pre-1980 seasons due to car-sharing and dropped-scores rules. They do not affect model accuracy for post-1990 analysis.

## 11. Data Leakage Detection

**Table:** `driver_race_features` (race-level grain: one row per driver per race)
**Total columns:** 26
**Post-race features (outcome/execution data):** 24 defined
**Leaked columns detected:** 10

❌ **FAIL** — Found 10 post-race features in `driver_race_features`:

| Leaked Column | Classification | Severity |
|----------------|----------------|----------|
| `avg_pit_duration_ms` | Race execution event | 🟠 High |
| `fastest_lap_rank` | Post-race derived metric | 🟡 Medium |
| `finish_position` | Direct outcome / target variable | 🔴 Critical |
| `is_dnf` | Direct outcome / target variable | 🔴 Critical |
| `is_podium` | Post-race derived metric | 🟡 Medium |
| `is_points_finish` | Post-race derived metric | 🟡 Medium |
| `is_winner` | Post-race derived metric | 🟡 Medium |
| `pit_stop_count` | Race execution event | 🟠 High |
| `points` | Direct outcome / target variable | 🔴 Critical |
| `positions_gained` | Race execution event | 🟠 High |

### Recommended Actions

1. **Review feature engineering code** in `src/feature_engineering/build_features.py`
   Look for where these columns are being added or merged into `driver_race`.

2. **Identify the source** of each leaked column:
   ```python
   # Check which source table contributes each leaked column
   for col in leaked_cols:
       print(f'{col}: {driver_race_features[col].dtype}, sample:',              driver_race_features[col].iloc[0])
   ```

3. **Remove or separate** post-race features:
   - Use them ONLY for post-race analysis (model explainability, audit)
   - Create separate `driver_race_post_analysis` table if needed
   - Keep `driver_race_features` clean for training only

4. **Re-validate** after fixes by re-running this check

### Common Leakage Patterns in F1 Data

- Merging `results` table (with `points`, `position`) into feature table
- Including pit stop counts/durations from actual race execution
- Using fastest lap data from race history lookups
- Computing position deltas (positions_gained) vs qualifying grid

### Season-Level Tables (Advisory)

| Table | Columns | Risk | Notes |
|-------|---------|------|-------|
| `driver_season` | 27 | ⚠️ High: 1 leaked | Aggregates derived from historical races (low leakage risk). By design, season stats are accumulated from past races. |
| `constructor_season` | 22 | ⚠️ High: 1 leaked | Aggregates derived from historical races (low leakage risk). By design, season stats are accumulated from past races. |

> ℹ️ Season-level tables are generally safe because they aggregate historical data.
> Leakage there is harder to accomplish accidentally (happens via explicit joins).


────────────────────────────────────────────────────────────

_Generated by `validate_data.py`. Re-run at any time before modeling to verify data integrity._