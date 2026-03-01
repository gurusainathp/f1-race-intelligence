# F1 Data Quality — Diagnostics Report

> **Generated:** 2026-03-01 17:14:12  
> **Database:** `data\processed\f1_database.db`  
> **Purpose:** Classify each scorecard failure as DATA issue or SCRIPT issue

---

## How to read this report

Each query block has an **Interpretation guide** explaining what the numbers mean.
After reviewing, classify each finding as:

- 🔴 **Data issue** — fix the source CSV or `clean_data.py`
- 🟡 **Script issue** — fix `validate_data.py` or `constants.py`
- 🟢 **Expected / justified** — no action needed, document and move on

---

## BLOCK A — `results.position` null (Scorecard Check 1)

### A1. Position null vs is_dnf cross-tab

**Question:** After the position backfill fix, are there any remaining classified finishers with null position?

**Interpretation guide:**  
**Expected after fix:** 'null position + NOT DNF' = 0 rows.
clean_data.py now backfills position from positionOrder for classified
finishers (positionText not in R/D/E/W/F/N). If this still shows > 0,
re-run clean_data.py and rebuild the database.

**Results:** 2 rows

| case_type | row_count |
| --- | --- |
| has position + finished (correct) | 15,808 |
| null position + DNF (correct) | 10,951 |

---

### A2. Status labels for null-position, non-DNF rows

**Question:** What statuses explain rows where position is null but is_dnf = 0?

**Interpretation guide:**  
'Not classified' is the expected answer — drivers who completed laps but weren't awarded a finishing position. If other statuses appear here, those are missing from the DNF classifier in constants.py.

**Results:** 0 rows

_No rows returned._

---

### A3. Null position count vs DNF flag count

**Question:** Does null_count(position) ≈ count(is_dnf = 1)?

**Interpretation guide:**  
Small difference (< 200) → the gap is explained by 'Not classified' entries; scorecard Check 1 failure is a **script bug** not a data problem.
Large difference → genuine data integrity issue.

**Results:** 1 rows

| position_null_count | dnf_flag_count | difference |
| --- | --- | --- |
| 10,951 | 10,951 | 0 |

---

## BLOCK B — `results.grid` null (Scorecard Check 1 secondary)

### B1. Status of drivers with null grid

**Question:** What were null-grid drivers doing — did they actually start?

**Interpretation guide:**  
If dominated by 'Did not qualify / prequalify' → pit-lane start conversion (grid=0→NULL) is working correctly.
If finished drivers appear here → data gap, grid was never recorded.

**Results:** 20 rows

| status | count |
| --- | --- |
| Did not qualify | 1,013 |
| Did not prequalify | 331 |
| Withdrew | 164 |
| +1 Lap | 27 |
| Finished | 22 |
| Accident | 20 |
| Injury | 8 |
| +2 Laps | 7 |
| Excluded | 6 |
| Engine | 6 |
| Disqualified | 6 |
| Retired | 3 |
| Collision damage | 3 |
| Suspension | 2 |
| Safety concerns | 2 |
| Power Unit | 2 |
| Injured | 2 |
| Fuel system | 2 |
| Brakes | 2 |
| 107% Rule | 2 |

---

### B2. Era breakdown of null-grid rows

**Question:** Are null grid positions concentrated in a specific era?

**Interpretation guide:**  
Concentration in pre-1980 → historic data gap, expected and acceptable.
Significant counts in modern era → unexplained data issue.

**Results:** 30 rows

| year | null_grid_count |
| --- | --- |
| 2,024 | 11 |
| 2,023 | 18 |
| 2,022 | 11 |
| 2,021 | 12 |
| 2,020 | 5 |
| 2,019 | 12 |
| 2,018 | 1 |
| 2,017 | 2 |
| 2,016 | 4 |
| 2,015 | 3 |
| 2,012 | 3 |
| 2,011 | 3 |
| 2,009 | 1 |
| 2,002 | 4 |
| 2,001 | 1 |
| 2,000 | 2 |
| 1,999 | 1 |
| 1,998 | 2 |
| 1,997 | 2 |
| 1,996 | 2 |
| 1,995 | 1 |
| 1,994 | 29 |
| 1,993 | 7 |
| 1,992 | 62 |
| 1,991 | 123 |
| 1,990 | 128 |
| 1,989 | 204 |
| 1,988 | 79 |
| 1,987 | 8 |
| 1,986 | 5 |

---

### B3. Null-grid rows that scored points

**Question:** How many null-grid drivers actually scored championship points?

**Interpretation guide:**  
0 → all null grids are DNS/DNQ entries, which legitimately have no grid.
> 0 → drivers started (they scored points) but grid was not recorded — genuine data gap.

**Results:** 1 rows

| null_grid_with_points | total_points_from_null_grid |
| --- | --- |
| 14 | 52 |

---

## BLOCK C — Duplicate `raceId × driverId` (Scorecard Check 4)

### C1. Actual year and name for top duplicate raceIds

**Question:** Do the high raceIds (700-800+) actually belong to 1950s races?

**Interpretation guide:**  
This is the key test for the year-lookup script bug.
If results show years 2021-2024 → **script bug** (year lookup was broken, these are Sprint weekends misclassified as 'Unexplained').
If results genuinely show 1950s years → the data itself has non-chronological raceIds (which is a known Kaggle dataset property) and the duplicates need a different explanation.

**Results:** 12 rows

| raceId | year | round | name | distinct_drivers | total_rows | duplicate_rows |
| --- | --- | --- | --- | --- | --- | --- |
| 839 | 1,950 | 7 | Italian Grand Prix | 27 | 29 | 2 |
| 828 | 1,951 | 4 | French Grand Prix | 23 | 26 | 3 |
| 809 | 1,953 | 2 | Indianapolis 500 | 37 | 47 | 10 |
| 800 | 1,954 | 2 | Indianapolis 500 | 42 | 55 | 13 |
| 792 | 1,955 | 1 | Argentine Grand Prix | 22 | 35 | 13 |
| 791 | 1,956 | 8 | Italian Grand Prix | 26 | 29 | 3 |
| 777 | 1,957 | 2 | Monaco Grand Prix | 21 | 23 | 2 |
| 780 | 1,957 | 5 | British Grand Prix | 19 | 22 | 3 |
| 766 | 1,958 | 2 | Monaco Grand Prix | 30 | 31 | 1 |
| 746 | 1,960 | 1 | Argentine Grand Prix | 22 | 23 | 1 |
| 745 | 1,961 | 8 | United States Grand Prix | 20 | 21 | 1 |
| 717 | 1,964 | 9 | United States Grand Prix | 19 | 20 | 1 |

---

### C2. Full detail on raceId 792 duplicate rows

**Question:** What exactly differs between the duplicate rows for this race?

**Interpretation guide:**  
Different constructorId across rows → dual-constructor (pre-1980s historical).
Different laps count across rows → sprint + main race entries.
Identical across all columns → true duplicate, data error.

**Results:** 35 rows

| resultId | driverId | full_name | constructorId | constructor | grid | position | laps | points | status | positionText |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 19,067 | 427 | Maurice Trintignant | 6 | Ferrari | 14 | — | 36 | 0 | Engine | R |
| 20,245 | 427 | Maurice Trintignant | 6 | Ferrari | 1 | 2 | 96 | 2 | Finished | 2 |
| 20,246 | 427 | Maurice Trintignant | 6 | Ferrari | 5 | 3 | 94 | 1.33 | +2 Laps | 3 |
| 19,069 | 475 | Stirling Moss | 131 | Mercedes | 8 | — | 29 | 0 | Fuel system | R |
| 20,249 | 475 | Stirling Moss | 131 | Mercedes | 10 | 4 | 94 | 1 | +2 Laps | 4 |
| 19,060 | 478 | Hans Herrmann | 131 | Mercedes | 10 | 4 | 94 | 1 | +2 Laps | 4 |
| 19,077 | 496 | Carlos Menditeguy | 105 | Maserati | 13 | — | 1 | 0 | Accident | R |
| 20,256 | 496 | Carlos Menditeguy | 105 | Maserati | 20 | — | 54 | 0 | Fuel pressure | R |
| 19,058 | 498 | José Froilán González | 6 | Ferrari | 1 | 2 | 96 | 2 | Finished | 2 |
| 19,062 | 501 | Harry Schell | 105 | Maserati | 7 | 6 | 88 | 0 | +8 Laps | 6 |
| 20,252 | 501 | Harry Schell | 105 | Maserati | 18 | 7 | 83 | 0 | +13 Laps | 7 |
| 20,255 | 501 | Harry Schell | 105 | Maserati | 20 | — | 54 | 0 | Fuel pressure | R |
| 19,073 | 554 | Jean Behra | 105 | Maserati | 4 | — | 2 | 0 | Accident | R |
| 20,250 | 554 | Jean Behra | 105 | Maserati | 7 | 6 | 88 | 0 | +8 Laps | 6 |
| 20,253 | 554 | Jean Behra | 105 | Maserati | 19 | — | 54 | 0 | Engine | R |
| 19,063 | 577 | Luigi Musso | 105 | Maserati | 18 | 7 | 83 | 0 | +13 Laps | 7 |
| 20,254 | 577 | Luigi Musso | 105 | Maserati | 19 | — | 54 | 0 | Engine | R |
| 19,057 | 579 | Juan Fangio | 131 | Mercedes | 3 | 1 | 96 | 9 | Finished | 1 |
| 19,068 | 608 | Eugenio Castellotti | 132 | Lancia | 12 | — | 35 | 0 | Accident | R |
| 20,247 | 620 | Umberto Maglioli | 6 | Ferrari | 5 | 3 | 94 | 1.33 | +2 Laps | 3 |
| 19,070 | 623 | Alberto Uria | 105 | Maserati | 21 | — | 22 | 0 | Out of fuel | R |
| 19,072 | 625 | Élie Bayol | 128 | Gordini | 15 | — | 7 | 0 | Transmission | R |
| 19,075 | 633 | Luigi Villoresi | 132 | Lancia | 11 | — | 2 | 0 | Fuel leak | R |
| 20,257 | 633 | Luigi Villoresi | 132 | Lancia | 12 | — | 35 | 0 | Accident | R |
| 19,059 | 642 | Nino Farina | 6 | Ferrari | 5 | 3 | 94 | 1.33 | +2 Laps | 3 |
| 20,244 | 642 | Nino Farina | 6 | Ferrari | 1 | 2 | 96 | 2 | Finished | 2 |
| 19,061 | 643 | Roberto Mieres | 105 | Maserati | 16 | 5 | 91 | 2 | +5 Laps | 5 |
| 19,064 | 644 | Sergio Mantovani | 105 | Maserati | 19 | — | 54 | 0 | Engine | R |
| 20,251 | 644 | Sergio Mantovani | 105 | Maserati | 18 | 7 | 83 | 0 | +13 Laps | 7 |
| 19,065 | 645 | Clemar Bucci | 105 | Maserati | 20 | — | 54 | 0 | Fuel pressure | R |
| 19,066 | 646 | Jesús Iglesias | 128 | Gordini | 17 | — | 38 | 0 | Transmission | R |
| 19,071 | 647 | Alberto Ascari | 132 | Lancia | 2 | — | 21 | 0 | Accident | R |
| 19,074 | 648 | Karl Kling | 131 | Mercedes | 6 | — | 2 | 0 | Accident | R |
| 20,248 | 648 | Karl Kling | 131 | Mercedes | 10 | 4 | 94 | 1 | +2 Laps | 4 |
| 19,076 | 649 | Pablo Birger | 128 | Gordini | 9 | — | 1 | 0 | Accident | R |

---

### C3. Classifier breakdown for all unexplained duplicate pairs

**Question:** For each duplicate pair, do rows differ by constructor, laps, or neither?

**Interpretation guide:**  
distinct_constructors = 2 → dual-constructor entry.
laps_difference > 0 → sprint vs main race (different race lengths).
Both = 0 → truly identical rows, genuine data corruption.

**Results:** 80 rows

| year | round | race_name | raceId | driverId | full_name | occurrences | distinct_constructors | laps_difference | max_points | constructors | laps_values | statuses | position_texts |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1,950 | 6 | French Grand Prix | 838 | 627 | Louis Rosier | 2 | 1 | 46 | 0 | Talbot-Lago / Talbot-Lago | 10 / 56 | Overheating / +8 Laps | R / 6 |
| 1,950 | 7 | Italian Grand Prix | 839 | 579 | Juan Fangio | 2 | 1 | 11 | 1 | Alfa Romeo / Alfa Romeo | 23 / 34 | Gearbox / Engine | R / R |
| 1,950 | 7 | Italian Grand Prix | 839 | 647 | Alberto Ascari | 2 | 1 | 59 | 3 | Ferrari / Ferrari | 21 / 80 | Engine / Finished | R / 2 |
| 1,951 | 4 | French Grand Prix | 828 | 579 | Juan Fangio | 2 | 1 | 22 | 5 | Alfa Romeo / Alfa Romeo | 55 / 77 | +22 Laps / Finished | 11 / 1 |
| 1,951 | 4 | French Grand Prix | 828 | 647 | Alberto Ascari | 2 | 1 | 67 | 3 | Ferrari / Ferrari | 77 / 10 | Finished / Gearbox | 2 / R |
| 1,951 | 4 | French Grand Prix | 828 | 786 | Luigi Fagioli | 2 | 1 | 22 | 4 | Alfa Romeo / Alfa Romeo | 77 / 55 | Finished / +22 Laps | 1 / 11 |
| 1,951 | 7 | Italian Grand Prix | 831 | 642 | Nino Farina | 2 | 1 | 73 | 3 | Alfa Romeo / Alfa Romeo | 6 / 79 | Engine / +1 Lap | R / 3 |
| 1,952 | 1 | Swiss Grand Prix | 817 | 642 | Nino Farina | 2 | 1 | 35 | 0 | Ferrari / Ferrari | 16 / 51 | Magneto / Magneto | R / R |
| 1,952 | 4 | French Grand Prix | 820 | 501 | Harry Schell | 2 | 1 | 27 | 0 | Maserati / Maserati | 7 / 34 | Gearbox / Brakes | R / R |
| 1,952 | 7 | Dutch Grand Prix | 823 | 759 | Jan Flinterman | 2 | 1 | 76 | 0 | Maserati / Maserati | 7 / 83 | Differential / +7 Laps | R / 9 |
| 1,953 | 2 | Indianapolis 500 | 809 | 509 | Jim Rathmann | 2 | 1 | 23 | 0 | Kurtis Kraft / Kurtis Kraft | 200 / 177 | Finished / Magneto | 7 / 15 |
| 1,953 | 2 | Indianapolis 500 | 809 | 512 | Johnny Thomson | 2 | 2 | 160 | 0 | Del Roy / Kurtis Kraft | 6 / 166 | Ignition / Oil leak | R / R |
| 1,953 | 2 | Indianapolis 500 | 809 | 518 | Duane Carter | 2 | 2 | 106 | 2 | Lesovsky / Kurtis Kraft | 94 / 200 | Ignition / Finished | R / 3 |
| 1,953 | 2 | Indianapolis 500 | 809 | 520 | Gene Hartley | 2 | 2 | 143 | 0 | Kurtis Kraft / Kuzma | 53 / 196 | Accident / Accident | R / 9 |
| 1,953 | 2 | Indianapolis 500 | 809 | 521 | Chuck Stevenson | 3 | 2 | 154 | 0 | Kuzma / Kuzma / Kurtis Kraft | 42 / 196 / 107 | Fuel leak / Accident / Overheating | R / 9 / R |
| 1,953 | 2 | Indianapolis 500 | 809 | 555 | Paul Russo | 2 | 1 | 111 | 1.5 | Kurtis Kraft / Kurtis Kraft | 89 / 200 | Magneto / Finished | R / 4 |
| 1,953 | 2 | Indianapolis 500 | 809 | 612 | Andy Linden | 3 | 2 | 174 | 0 | Stevens / Kurtis Kraft / Kurtis Kraft | 3 / 177 / 107 | Accident / Axle / Overheating | R / 16 / R |
| 1,953 | 2 | Indianapolis 500 | 809 | 702 | Bob Scott | 2 | 2 | 176 | 0 | Bromme / Kurtis Kraft | 14 / 190 | Oil leak / +10 Laps | R / 12 |
| 1,953 | 3 | Dutch Grand Prix | 810 | 498 | José Froilán González | 2 | 1 | 67 | 2 | Maserati / Maserati | 22 / 89 | Axle / +1 Lap | R / 3 |
| 1,953 | 4 | Belgian Grand Prix | 811 | 579 | Juan Fangio | 2 | 1 | 22 | 0 | Maserati / Maserati | 13 / 35 | Engine / Accident | R / R |
| 1,953 | 7 | German Grand Prix | 814 | 633 | Luigi Villoresi | 2 | 1 | 2 | 0 | Ferrari / Ferrari | 15 / 17 | Engine / +1 Lap | R / 8 |
| 1,953 | 7 | German Grand Prix | 814 | 647 | Alberto Ascari | 2 | 1 | 2 | 1 | Ferrari / Ferrari | 17 / 15 | +1 Lap / Engine | 8 / R |
| 1,953 | 8 | Swiss Grand Prix | 815 | 579 | Juan Fangio | 2 | 1 | 35 | 1.5 | Maserati / Maserati | 64 / 29 | +1 Lap / Engine | 4 / R |
| 1,953 | 8 | Swiss Grand Prix | 815 | 697 | Felice Bonetto | 2 | 1 | 35 | 1.5 | Maserati / Maserati | 29 / 64 | Engine / +1 Lap | R / 4 |
| 1,954 | 2 | Indianapolis 500 | 800 | 509 | Jim Rathmann | 2 | 1 | 81 | 0 | Kurtis Kraft / Kurtis Kraft | 110 / 191 | Accident / Spun off | R / R |
| 1,954 | 2 | Indianapolis 500 | 800 | 518 | Duane Carter | 2 | 1 | 4 | 1.5 | Kurtis Kraft / Kurtis Kraft | 196 / 200 | +4 Laps / Finished | 15 / 4 |
| 1,954 | 2 | Indianapolis 500 | 800 | 529 | Tony Bettenhausen | 2 | 1 | 91 | 0 | Kurtis Kraft / Kurtis Kraft | 105 / 196 | Wheel bearing / +4 Laps | R / 15 |
| 1,954 | 2 | Indianapolis 500 | 800 | 556 | Jimmy Daywalt | 2 | 2 | 54 | 0 | Kurtis Kraft / Nichels | 111 / 165 | Accident / Retired | R / R |
| 1,954 | 2 | Indianapolis 500 | 800 | 593 | Johnnie Parsons | 2 | 1 | 121 | 0 | Kurtis Kraft / Kurtis Kraft | 79 / 200 | Engine / Finished | R / 11 |
| 1,954 | 2 | Indianapolis 500 | 800 | 611 | Sam Hanks | 2 | 1 | 9 | 0 | Kurtis Kraft / Kurtis Kraft | 191 / 200 | Spun off / Finished | R / 11 |
| 1,954 | 2 | Indianapolis 500 | 800 | 612 | Andy Linden | 3 | 3 | 35 | 0 | Schroeder / Kurtis Kraft / Nichels | 165 / 200 / 165 | Suspension / Finished / Retired | R / 11 / R |
| 1,954 | 2 | Indianapolis 500 | 800 | 613 | Marshall Teague | 2 | 1 | 28 | 0 | Kurtis Kraft / Kurtis Kraft | 196 / 168 | +4 Laps / Clutch | 15 / R |
| 1,954 | 2 | Indianapolis 500 | 800 | 653 | Jimmy Davies | 2 | 1 | 9 | 0 | Kurtis Kraft / Kurtis Kraft | 200 / 191 | Finished / Spun off | 11 / R |
| 1,954 | 2 | Indianapolis 500 | 800 | 659 | Jerry Hoyt | 2 | 1 | 70 | 0 | Kurtis Kraft / Kurtis Kraft | 130 / 200 | Engine / Finished | R / 8 |
| 1,954 | 2 | Indianapolis 500 | 800 | 702 | Bob Scott | 2 | 2 | 28 | 0 | Stevens / Schroeder | 193 / 165 | +7 Laps / Suspension | 18 / R |
| 1,954 | 2 | Indianapolis 500 | 800 | 730 | George Fonder | 2 | 2 | 92 | 0 | Kurtis Kraft / Schroeder | 193 / 101 | +7 Laps / Brakes | 19 / R |
| 1,954 | 3 | Belgian Grand Prix | 801 | 498 | José Froilán González | 2 | 1 | 34 | 1.5 | Ferrari / Ferrari | 35 / 1 | +1 Lap / Engine | 4 / R |
| 1,954 | 5 | British Grand Prix | 803 | 647 | Alberto Ascari | 2 | 1 | 19 | 0 | Maserati / Maserati | 21 / 40 | Engine / Engine | R / R |
| 1,954 | 6 | German Grand Prix | 804 | 578 | Mike Hawthorn | 2 | 1 | 19 | 3 | Ferrari / Ferrari | 3 / 22 | Transmission / Finished | R / 2 |
| 1,954 | 8 | Italian Grand Prix | 806 | 498 | José Froilán González | 2 | 1 | 62 | 3 | Ferrari / Ferrari | 16 / 78 | Gearbox / +2 Laps | R / 3 |
| 1,955 | 1 | Argentine Grand Prix | 792 | 427 | Maurice Trintignant | 3 | 1 | 60 | 2 | Ferrari / Ferrari / Ferrari | 36 / 96 / 94 | Engine / Finished / +2 Laps | R / 2 / 3 |
| 1,955 | 1 | Argentine Grand Prix | 792 | 475 | Stirling Moss | 2 | 1 | 65 | 1 | Mercedes / Mercedes | 29 / 94 | Fuel system / +2 Laps | R / 4 |
| 1,955 | 1 | Argentine Grand Prix | 792 | 496 | Carlos Menditeguy | 2 | 1 | 53 | 0 | Maserati / Maserati | 1 / 54 | Accident / Fuel pressure | R / R |
| 1,955 | 1 | Argentine Grand Prix | 792 | 501 | Harry Schell | 3 | 1 | 34 | 0 | Maserati / Maserati / Maserati | 88 / 83 / 54 | +8 Laps / +13 Laps / Fuel pressure | 6 / 7 / R |
| 1,955 | 1 | Argentine Grand Prix | 792 | 554 | Jean Behra | 3 | 1 | 86 | 0 | Maserati / Maserati / Maserati | 2 / 88 / 54 | Accident / +8 Laps / Engine | R / 6 / R |
| 1,955 | 1 | Argentine Grand Prix | 792 | 577 | Luigi Musso | 2 | 1 | 29 | 0 | Maserati / Maserati | 83 / 54 | +13 Laps / Engine | 7 / R |
| 1,955 | 1 | Argentine Grand Prix | 792 | 633 | Luigi Villoresi | 2 | 1 | 33 | 0 | Lancia / Lancia | 2 / 35 | Fuel leak / Accident | R / R |
| 1,955 | 1 | Argentine Grand Prix | 792 | 642 | Nino Farina | 2 | 1 | 2 | 2 | Ferrari / Ferrari | 94 / 96 | +2 Laps / Finished | 3 / 2 |
| 1,955 | 1 | Argentine Grand Prix | 792 | 644 | Sergio Mantovani | 2 | 1 | 29 | 0 | Maserati / Maserati | 54 / 83 | Engine / +13 Laps | R / 7 |
| 1,955 | 1 | Argentine Grand Prix | 792 | 648 | Karl Kling | 2 | 1 | 92 | 1 | Mercedes / Mercedes | 2 / 94 | Accident / +2 Laps | R / 4 |
| 1,955 | 2 | Monaco Grand Prix | 793 | 554 | Jean Behra | 2 | 1 | 13 | 2 | Maserati / Maserati | 99 / 86 | +1 Lap / Spun off | 3 / R |
| 1,955 | 2 | Monaco Grand Prix | 793 | 607 | Cesare Perdisa | 2 | 1 | 13 | 2 | Maserati / Maserati | 86 / 99 | Spun off / +1 Lap | R / 3 |
| 1,955 | 4 | Belgian Grand Prix | 795 | 554 | Jean Behra | 2 | 1 | 32 | 1 | Maserati / Maserati | 3 / 35 | Spun off / +1 Lap | R / 5 |
| 1,955 | 6 | British Grand Prix | 797 | 501 | Harry Schell | 2 | 1 | 52 | 0 | Vanwall / Vanwall | 20 / 72 | Throttle / +18 Laps | R / 9 |
| 1,955 | 6 | British Grand Prix | 797 | 608 | Eugenio Castellotti | 2 | 1 | 71 | 0 | Ferrari / Ferrari | 16 / 87 | Transmission / +3 Laps | R / 6 |
| 1,956 | 1 | Argentine Grand Prix | 784 | 579 | Juan Fangio | 2 | 1 | 76 | 5 | Ferrari / Ferrari | 22 / 98 | Fuel pump / Finished | R / 1 |
| 1,956 | 2 | Monaco Grand Prix | 785 | 579 | Juan Fangio | 2 | 1 | 1 | 4 | Ferrari / Ferrari | 99 / 100 | +1 Lap / Finished | 4 / 2 |
| 1,956 | 2 | Monaco Grand Prix | 785 | 608 | Eugenio Castellotti | 2 | 1 | 85 | 1.5 | Ferrari / Ferrari | 14 / 99 | Clutch / +1 Lap | R / 4 |
| 1,956 | 4 | Belgian Grand Prix | 787 | 475 | Stirling Moss | 2 | 1 | 26 | 3 | Maserati / Maserati | 10 / 36 | Wheel / Finished | R / 3 |
| 1,956 | 5 | French Grand Prix | 788 | 475 | Stirling Moss | 2 | 1 | 47 | 1 | Maserati / Maserati | 12 / 59 | Gearbox / +2 Laps | R / 5 |
| 1,956 | 5 | French Grand Prix | 788 | 501 | Harry Schell | 2 | 1 | 51 | 0 | Vanwall / Vanwall | 5 / 56 | Engine / +5 Laps | R / 10 |
| 1,956 | 5 | French Grand Prix | 788 | 624 | Hernando da Silva Ramos | 2 | 2 | 17 | 0 | Gordini / Maserati | 57 / 40 | +4 Laps / Engine | 8 / R |
| 1,956 | 6 | British Grand Prix | 789 | 581 | Peter Collins | 2 | 1 | 36 | 3 | Ferrari / Ferrari | 64 / 100 | Oil pressure / +1 Lap | R / 2 |
| 1,956 | 6 | British Grand Prix | 789 | 606 | Alfonso de Portago | 2 | 1 | 8 | 3 | Ferrari / Ferrari | 100 / 92 | +1 Lap / +9 Laps | 2 / 10 |
| 1,956 | 8 | Italian Grand Prix | 791 | 554 | Jean Behra | 2 | 1 | 19 | 0 | Maserati / Maserati | 23 / 42 | Magneto / Steering | R / R |
| 1,956 | 8 | Italian Grand Prix | 791 | 579 | Juan Fangio | 2 | 1 | 4 | 3 | Ferrari / Ferrari | 46 / 50 | +4 Laps / Finished | 8 / 2 |
| 1,956 | 8 | Italian Grand Prix | 791 | 608 | Eugenio Castellotti | 2 | 1 | 37 | 0 | Ferrari / Ferrari | 9 / 46 | Tyre / +4 Laps | R / 8 |
| 1,957 | 1 | Argentine Grand Prix | 776 | 581 | Peter Collins | 2 | 1 | 72 | 0 | Ferrari / Ferrari | 26 / 98 | Clutch / +2 Laps | R / 6 |
| 1,957 | 2 | Monaco Grand Prix | 777 | 501 | Harry Schell | 2 | 1 | 41 | 0 | Maserati / Maserati | 23 / 64 | Suspension / Oil leak | R / R |
| 1,957 | 2 | Monaco Grand Prix | 777 | 578 | Mike Hawthorn | 2 | 1 | 91 | 0 | Ferrari / Ferrari | 4 / 95 | Accident / Engine | R / R |
| 1,957 | 4 | French Grand Prix | 779 | 356 | Jack Brabham | 2 | 1 | 64 | 0 | Cooper / Cooper | 4 / 68 | Accident / +9 Laps | R / 7 |
| 1,957 | 5 | British Grand Prix | 780 | 475 | Stirling Moss | 2 | 1 | 39 | 5 | Vanwall / Vanwall | 51 / 90 | Engine / Finished | R / 1 |
| 1,957 | 5 | British Grand Prix | 780 | 479 | Tony Brooks | 2 | 1 | 39 | 4 | Vanwall / Vanwall | 90 / 51 | Finished / Engine | 1 / R |
| 1,957 | 5 | British Grand Prix | 780 | 581 | Peter Collins | 2 | 1 | 35 | 0 | Ferrari / Ferrari | 53 / 88 | Water leak / +2 Laps | R / 4 |
| 1,957 | 8 | Italian Grand Prix | 783 | 501 | Harry Schell | 2 | 1 | 50 | 1 | Maserati / Maserati | 34 / 84 | Oil leak / +3 Laps | R / 5 |
| 1,958 | 6 | French Grand Prix | 770 | 479 | Tony Brooks | 2 | 1 | 19 | 0 | Vanwall / Vanwall | 16 / 35 | Engine / Engine | R / R |
| 1,958 | 10 | Italian Grand Prix | 774 | 566 | Carroll Shelby | 2 | 1 | 68 | 0 | Maserati / Maserati | 1 / 69 | Handling / +1 Lap | R / 4 |
| 1,960 | 1 | Argentine Grand Prix | 746 | 475 | Stirling Moss | 2 | 1 | 40 | 0 | Cooper-Climax / Cooper-Climax | 40 / 80 | Suspension / Finished | R / 3 |
| 1,961 | 8 | United States Grand Prix | 745 | 418 | Masten Gregory | 2 | 1 | 69 | 0 | Lotus-Climax / Lotus-Climax | 23 / 92 | Gearbox / +8 Laps | R / 11 |
| 1,964 | 9 | United States Grand Prix | 717 | 373 | Jim Clark | 2 | 1 | 48 | 0 | Lotus-Climax / Lotus-Climax | 102 / 54 | Out of fuel / Injection | 7 / R |

---

### C4. Circuit info for top duplicate races

**Question:** Are the duplicate races held at circuits that could explain dual entries?

**Interpretation guide:**  
Indianapolis Motor Speedway → the Kaggle dataset includes the Indy 500 as an F1 WC round 1950-1960; some drivers have dual entries.
Other circuits → check for sprint calendar or historical data issue.

**Results:** 11 rows

| raceId | year | round | race_name | circuit_name | location | country |
| --- | --- | --- | --- | --- | --- | --- |
| 839 | 1,950 | 7 | Italian Grand Prix | Autodromo Nazionale di Monza | Monza | Italy |
| 828 | 1,951 | 4 | French Grand Prix | Reims-Gueux | Reims | France |
| 809 | 1,953 | 2 | Indianapolis 500 | Indianapolis Motor Speedway | Indianapolis | United States |
| 800 | 1,954 | 2 | Indianapolis 500 | Indianapolis Motor Speedway | Indianapolis | United States |
| 792 | 1,955 | 1 | Argentine Grand Prix | Autódromo Juan y Oscar Gálvez | Buenos Aires | Argentina |
| 791 | 1,956 | 8 | Italian Grand Prix | Autodromo Nazionale di Monza | Monza | Italy |
| 777 | 1,957 | 2 | Monaco Grand Prix | Circuit de Monaco | Monte-Carlo | Monaco |
| 780 | 1,957 | 5 | British Grand Prix | Aintree | Liverpool | United Kingdom |
| 746 | 1,960 | 1 | Argentine Grand Prix | Autódromo Juan y Oscar Gálvez | Buenos Aires | Argentina |
| 745 | 1,961 | 8 | United States Grand Prix | Watkins Glen | New York State | United States |
| 717 | 1,964 | 9 | United States Grand Prix | Watkins Glen | New York State | United States |

---

## BLOCK D — Lap times > 600s (Scorecard Check 5)

### D1. All laps > 600s with context

**Question:** Show every corrupt lap with race, driver, lap number, and ratio to own average.

**Interpretation guide:**  
ratio_to_own_avg > 6 and race is old (pre-1990) → likely corrupt timing data from early electronic timing systems.
ratio_to_own_avg 3-6 and recent race → probable red-flag suspension (race stopped, clock kept running). These may warrant raising the corrupt threshold or adding a red-flag band.

**Results:** 0 rows

_No rows returned._

---

### D2. How many drivers affected on the same lap number

**Question:** Was the slow lap isolated to one driver or did the whole field slow down?

**Interpretation guide:**  
drivers_affected > 3 on the same lap → almost certainly a red flag or safety car period (real event, threshold may need raising).
drivers_affected = 1 → isolated to one driver, more likely corrupt timing.

**Results:** 0 rows

_No rows returned._

---

### D3. All driver lap times around the worst lap (raceId=340, laps 16-20)

**Question:** Was the 854s lap isolated or did multiple drivers slow on that lap?

**Interpretation guide:**  
Multiple drivers with very high times on the same lap → red flag event.
Only one driver with a high time → corrupt data point for that driver.

**Results:** 50 rows _(showing first 50 rows)_

| lap | driverId | full_name | lap_time_seconds | position |
| --- | --- | --- | --- | --- |
| 16 | 15 | Jarno Trulli | 112.4 | 16 |
| 16 | 812 | Karun Chandhok | 110.3 | 18 |
| 16 | 5 | Heikki Kovalainen | 108.9 | 14 |
| 16 | 811 | Bruno Senna | 108.2 | 17 |
| 16 | 30 | Michael Schumacher | 106.8 | 6 |
| 16 | 808 | Vitaly Petrov | 106.7 | 4 |
| 16 | 16 | Adrian Sutil | 106.2 | 9 |
| 16 | 4 | Fernando Alonso | 106 | 13 |
| 16 | 22 | Rubens Barrichello | 106 | 12 |
| 16 | 13 | Felipe Massa | 105.7 | 11 |
| 16 | 1 | Lewis Hamilton | 105.6 | 5 |
| 16 | 807 | Nico Hülkenberg | 105.5 | 15 |
| 16 | 9 | Robert Kubica | 105.2 | 3 |
| 16 | 18 | Jenson Button | 105 | 2 |
| 16 | 153 | Jaime Alguersuari | 105 | 10 |
| 16 | 3 | Nico Rosberg | 104.8 | 1 |
| 16 | 17 | Mark Webber | 104.3 | 8 |
| 16 | 20 | Sebastian Vettel | 103.7 | 7 |
| 17 | 15 | Jarno Trulli | 154.5 | 17 |
| 17 | 812 | Karun Chandhok | 118.2 | 18 |
| 17 | 811 | Bruno Senna | 117.2 | 16 |
| 17 | 5 | Heikki Kovalainen | 108.8 | 14 |
| 17 | 16 | Adrian Sutil | 107.1 | 9 |
| 17 | 807 | Nico Hülkenberg | 106.8 | 15 |
| 17 | 808 | Vitaly Petrov | 106.2 | 4 |
| 17 | 30 | Michael Schumacher | 106.1 | 7 |
| 17 | 153 | Jaime Alguersuari | 105.8 | 10 |
| 17 | 4 | Fernando Alonso | 105.6 | 13 |
| 17 | 13 | Felipe Massa | 105.6 | 11 |
| 17 | 22 | Rubens Barrichello | 105.6 | 12 |
| 17 | 9 | Robert Kubica | 104.7 | 3 |
| 17 | 18 | Jenson Button | 104.7 | 2 |
| 17 | 20 | Sebastian Vettel | 104.2 | 6 |
| 17 | 17 | Mark Webber | 104.1 | 8 |
| 17 | 3 | Nico Rosberg | 103.7 | 1 |
| 17 | 1 | Lewis Hamilton | 103.1 | 5 |
| 18 | 812 | Karun Chandhok | 135.5 | 17 |
| 18 | 811 | Bruno Senna | 132 | 16 |
| 18 | 22 | Rubens Barrichello | 116.8 | 13 |
| 18 | 5 | Heikki Kovalainen | 114.7 | 14 |
| 18 | 807 | Nico Hülkenberg | 113.5 | 15 |
| 18 | 16 | Adrian Sutil | 110.3 | 10 |
| 18 | 153 | Jaime Alguersuari | 109.6 | 9 |
| 18 | 13 | Felipe Massa | 107.4 | 11 |
| 18 | 4 | Fernando Alonso | 107.4 | 12 |
| 18 | 17 | Mark Webber | 107 | 8 |
| 18 | 30 | Michael Schumacher | 106.7 | 7 |
| 18 | 808 | Vitaly Petrov | 106.5 | 4 |
| 18 | 9 | Robert Kubica | 105.3 | 3 |
| 18 | 20 | Sebastian Vettel | 105.2 | 6 |

---

### D4. Lap time distribution for raceId 340

**Question:** What is the normal pace for this race, to contextualise the 854s outlier?

**Interpretation guide:**  
If avg is ~90s and max is 854s, the outlier is 9x normal pace — either a very long red flag or corrupt data. Check D3 to determine which.

**Results:** 1 rows

| min_s | avg_s | max_s | total_laps | sc_vsc_laps | over_corrupt_threshold |
| --- | --- | --- | --- | --- | --- |
| 102.1 | 116.4 | 174 | 983 | 0 | 0 |

---

## BLOCK E — Unclassified status labels (Scorecard Check 7)

### E1. All status labels not currently classified as Finished or DNF

**Question:** Which status labels are falling through the classifier?

**Interpretation guide:**  
Labels with positionText in (R,D,E,W,F,N) and no position → clearly DNFs, **script issue** (missing keyword in constants.py).
Labels with a filled position or points > 0 → driver finished, need to check if label is correct or if it's a data issue.

**Results:** 40 rows

| status | occurrences | position_texts | rows_with_position | rows_with_points |
| --- | --- | --- | --- | --- |
| Not classified | 172 | N,19 | 1 | 0 |
| Oil leak | 124 | R,9 | 1 | 0 |
| Out of fuel | 100 | R,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,19 | 79 | 26 |
| Fuel pump | 66 | R,W,5,7,10,11,20 | 5 | 2 |
| Collision damage | 60 | R,14,15,17,18,19,20 | 7 | 0 |
| Tyre | 55 | R,12,13,15,20 | 4 | 0 |
| Fuel leak | 51 | R,W,11 | 1 | 0 |
| Wheel bearing | 37 | R,5,16,19 | 3 | 1 |
| Fuel pressure | 35 | R,7,16,18,19,21 | 6 | 0 |
| Heat shield fire | 19 | R,13 | 1 | 0 |
| Oil pump | 14 | R | 0 | 0 |
| Oil pipe | 12 | R,8 | 1 | 0 |
| Driver unwell | 10 | R,W | 0 | 0 |
| Wheel nut | 9 | R,16 | 1 | 0 |
| Water pressure | 9 | R,14,15,17 | 3 | 0 |
| 107% Rule | 9 | F | 0 | 0 |
| Water pump | 7 | R | 0 | 0 |
| Injured | 7 | R,W | 0 | 0 |
| Technical | 5 | R,14 | 1 | 0 |
| Fuel | 4 | R | 0 | 0 |
| Wheel rim | 3 | R,11,12 | 2 | 0 |
| Water pipe | 3 | R | 0 | 0 |
| Fuel pipe | 3 | R,15 | 1 | 0 |
| Fatal accident | 3 | R,W | 0 | 0 |
| Stalled | 2 | R | 0 | 0 |
| Safety concerns | 2 | W | 0 | 0 |
| Oil line | 2 | R | 0 | 0 |
| Fuel rig | 2 | R | 0 | 0 |
| Underweight | 1 | E | 0 | 0 |
| Tyre puncture | 1 | 13 | 1 | 0 |
| Seat | 1 | R | 0 | 0 |
| Safety belt | 1 | R | 0 | 0 |
| Refuelling | 1 | R | 0 | 0 |
| Not restarted | 1 | R | 0 | 0 |
| Launch control | 1 | R | 0 | 0 |
| Eye injury | 1 | R | 0 | 0 |
| Engine misfire | 1 | R | 0 | 0 |
| Engine fire | 1 | R | 0 | 0 |
| Driver Seat | 1 | R | 0 | 0 |
| Cooling system | 1 | R | 0 | 0 |

---

### E2. Encoding check on Excluded / Disqualified labels

**Question:** Is 'Excluded' failing to match due to whitespace or encoding?

**Interpretation guide:**  
label_length > expected length OR first_3_bytes_hex != '457863' (Exc) → hidden characters, **data issue** in the status table itself.
All lengths normal → 'Excluded' is genuinely absent from keyword list, **script issue**.

**Results:** 2 rows

| statusId | status | label_length | first_3_bytes_hex | result_count |
| --- | --- | --- | --- | --- |
| 2 | Disqualified | 12 | 446973 | 147 |
| 96 | Excluded | 8 | 457863 | 8 |

---

### E3. Keyword coverage check against updated constants.py

**Question:** After the constants.py fix, which labels are now covered and which still need work?

**Interpretation guide:**  
'In updated MECHANICAL_KEYWORDS' → will be fixed once constants.py update is applied.
'Intentionally Other' → correctly left unclassified (Not classified, 107% Rule etc).
'Still missing from keywords' → requires another keyword addition.

**Results:** 35 rows

| status | count | coverage |
| --- | --- | --- |
| Not classified | 172 | Intentionally Other (review manually) |
| Ignition | 128 | Covered by updated MECHANICAL_KEYWORDS |
| Halfshaft | 99 | Covered by updated MECHANICAL_KEYWORDS |
| Handling | 54 | Covered by updated MECHANICAL_KEYWORDS |
| Steering | 48 | Covered by updated MECHANICAL_KEYWORDS |
| Radiator | 44 | Covered by updated MECHANICAL_KEYWORDS |
| Injection | 36 | Covered by updated MECHANICAL_KEYWORDS |
| Physical | 31 | Covered by updated driver-physical keywords |
| Chassis | 29 | Covered by updated MECHANICAL_KEYWORDS |
| Magneto | 26 | Covered by updated MECHANICAL_KEYWORDS |
| Axle | 22 | Covered by updated MECHANICAL_KEYWORDS |
| Power loss | 15 | Covered by updated MECHANICAL_KEYWORDS |
| Distributor | 14 | Covered by updated MECHANICAL_KEYWORDS |
| Broken wing | 11 | Covered by updated MECHANICAL_KEYWORDS |
| Driver unwell | 10 | Covered by updated driver-physical keywords |
| Rear wing | 10 | Covered by updated MECHANICAL_KEYWORDS |
| 107% Rule | 9 | Intentionally Other (review manually) |
| Excluded | 8 | Intentionally Other (review manually) |
| Injured | 7 | Covered by updated driver-physical keywords |
| ERS | 5 | Covered by updated MECHANICAL_KEYWORDS |
| Front wing | 5 | Covered by updated MECHANICAL_KEYWORDS |
| Supercharger | 5 | Covered by updated MECHANICAL_KEYWORDS |
| Undertray | 4 | Covered by updated MECHANICAL_KEYWORDS |
| Spark plugs | 3 | Covered by updated MECHANICAL_KEYWORDS |
| Drivetrain | 2 | Covered by updated MECHANICAL_KEYWORDS |
| Stalled | 2 | Intentionally Other (review manually) |
| Track rod | 2 | Covered by updated MECHANICAL_KEYWORDS |
| Brake duct | 1 | Covered by updated MECHANICAL_KEYWORDS |
| CV joint | 1 | Covered by updated MECHANICAL_KEYWORDS |
| Crankshaft | 1 | Covered by updated MECHANICAL_KEYWORDS |
| Driver Seat | 1 | Intentionally Other (review manually) |
| Launch control | 1 | Intentionally Other (review manually) |
| Not restarted | 1 | Intentionally Other (review manually) |
| Seat | 1 | Intentionally Other (review manually) |
| Underweight | 1 | Intentionally Other (review manually) |

---

## BLOCK F — `qualifying.q1_ms` null 1.5% (Bonus)

### F1. Sample of null q1_ms qualifying rows

**Question:** Are these DNS entries, DQ entries, or data gaps?

**Interpretation guide:**  
race_status = 'Did not qualify' / 'Did not prequalify' → driver didn't set a time, null is correct.
race_status = 'Finished' with null q1 → genuine data gap.

**Results:** 30 rows

| year | round | race_name | raceId | driverId | full_name | quali_position | q1_ms | q2_ms | q3_ms | race_status | grid | race_laps |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1,994 | 3 | San Marino Grand Prix | 259 | 22 | Rubens Barrichello | 28 | — | — | — | Injury | — | 0 |
| 1,995 | 16 | Japanese Grand Prix | 255 | 87 | Mark Blundell | 24 | — | — | — | +1 Lap | 23 | 52 |
| 1,995 | 17 | Australian Grand Prix | 256 | 55 | Jean Alesi | 5 | — | 76,305 | — | Collision | 5 | 23 |
| 1,996 | 2 | Brazilian Grand Prix | 225 | 58 | Tarso Marques | 21 | — | — | — | Spun off | 21 | 0 |
| 1,996 | 2 | Brazilian Grand Prix | 225 | 64 | Pedro Diniz | 22 | — | — | — | +2 Laps | 22 | 69 |
| 1,996 | 5 | San Marino Grand Prix | 228 | 85 | Andrea Montermini | 22 | — | — | — | 107% Rule | 22 | 0 |
| 1,997 | 9 | British Grand Prix | 215 | 82 | Norberto Fontana | 22 | — | — | — | +1 Lap | 14 | 58 |
| 1,998 | 9 | British Grand Prix | 199 | 23 | Ralf Schumacher | 21 | — | — | — | +1 Lap | 21 | 59 |
| 1,998 | 9 | British Grand Prix | 199 | 44 | Olivier Panis | 22 | — | — | — | Spun off | 22 | 40 |
| 1,999 | 2 | Brazilian Grand Prix | 176 | 35 | Jacques Villeneuve | 21 | — | — | — | Hydraulics | 21 | 49 |
| 2,003 | 1 | Australian Grand Prix | 108 | 51 | Justin Wilson | 19 | — | — | — | Radiator | 19 | 16 |
| 2,003 | 1 | Australian Grand Prix | 108 | 50 | Jos Verstappen | 20 | — | — | — | +1 Lap | 20 | 57 |
| 2,003 | 4 | San Marino Grand Prix | 111 | 50 | Jos Verstappen | 20 | — | — | — | Electrical | 20 | 38 |
| 2,003 | 5 | Spanish Grand Prix | 112 | 8 | Kimi Räikkönen | 20 | — | — | — | Collision | 20 | 0 |
| 2,003 | 6 | Austrian Grand Prix | 113 | 50 | Jos Verstappen | 20 | — | — | — | Clutch | 20 | 0 |
| 2,003 | 7 | Monaco Grand Prix | 114 | 18 | Jenson Button | 20 | — | — | — | Injured | 20 | 0 |
| 2,003 | 8 | Canadian Grand Prix | 115 | 8 | Kimi Räikkönen | 20 | — | — | — | Finished | 20 | 70 |
| 2,003 | 9 | European Grand Prix | 116 | 2 | Nick Heidfeld | 20 | — | — | — | +1 Lap | 20 | 59 |
| 2,003 | 11 | British Grand Prix | 118 | 18 | Jenson Button | 20 | — | — | — | Finished | 20 | 60 |
| 2,003 | 16 | Japanese Grand Prix | 123 | 23 | Ralf Schumacher | 19 | — | — | — | +1 Lap | 19 | 52 |
| 2,003 | 16 | Japanese Grand Prix | 123 | 15 | Jarno Trulli | 20 | — | — | — | Finished | 20 | 53 |
| 2,004 | 1 | Australian Grand Prix | 90 | 44 | Olivier Panis | 18 | — | — | — | +2 Laps | 18 | 56 |
| 2,004 | 1 | Australian Grand Prix | 90 | 32 | Christian Klien | 19 | — | — | — | +2 Laps | 19 | 56 |
| 2,004 | 1 | Australian Grand Prix | 90 | 46 | Gianmaria Bruni | 20 | — | — | — | Not classified | 20 | 43 |
| 2,004 | 2 | Malaysian Grand Prix | 91 | 4 | Fernando Alonso | 19 | — | — | — | Finished | 19 | 56 |
| 2,004 | 2 | Malaysian Grand Prix | 91 | 11 | Takuma Sato | 20 | — | — | — | +4 Laps | 20 | 52 |
| 2,004 | 3 | Bahrain Grand Prix | 92 | 8 | Kimi Räikkönen | 20 | — | — | — | Engine | 19 | 7 |
| 2,004 | 4 | San Marino Grand Prix | 93 | 21 | Giancarlo Fisichella | 19 | — | — | — | +1 Lap | 18 | 61 |
| 2,004 | 4 | San Marino Grand Prix | 93 | 8 | Kimi Räikkönen | 20 | — | — | — | +1 Lap | 20 | 61 |
| 2,004 | 7 | European Grand Prix | 96 | 14 | David Coulthard | 18 | — | — | — | Engine | 18 | 25 |

---

### F2. Year distribution of null q1_ms

**Question:** Are null qualifying times concentrated in a specific era?

**Interpretation guide:**  
All in pre-2006 → expected, qualifying format was different.
Post-2006 entries present → data gaps in modern qualifying records.

**Results:** 27 rows

| year | null_q1_count |
| --- | --- |
| 1,994 | 1 |
| 1,995 | 2 |
| 1,996 | 3 |
| 1,997 | 1 |
| 1,998 | 2 |
| 1,999 | 1 |
| 2,003 | 11 |
| 2,004 | 21 |
| 2,005 | 17 |
| 2,006 | 8 |
| 2,007 | 2 |
| 2,008 | 2 |
| 2,009 | 1 |
| 2,010 | 4 |
| 2,011 | 5 |
| 2,013 | 2 |
| 2,014 | 7 |
| 2,015 | 3 |
| 2,016 | 3 |
| 2,017 | 2 |
| 2,018 | 6 |
| 2,019 | 9 |
| 2,020 | 1 |
| 2,021 | 7 |
| 2,022 | 4 |
| 2,023 | 5 |
| 2,024 | 4 |

---

## BLOCK G — `pit_stops` null duration 4.7% (Bonus)

### G1. Year breakdown of null pit durations

**Question:** Are null pit durations an early-era timing gap or spread across all years?

**Interpretation guide:**  
Concentrated in 2011-2012 → early pit stop data collection had gaps, expected.
Spread across many years → systematic issue worth investigating.

**Results:** 12 rows

| year | null_duration_count | races_affected |
| --- | --- | --- |
| 2,011 | 19 | 10 |
| 2,012 | 12 | 8 |
| 2,013 | 3 | 2 |
| 2,014 | 22 | 1 |
| 2,016 | 72 | 4 |
| 2,017 | 21 | 1 |
| 2,018 | 1 | 1 |
| 2,020 | 61 | 3 |
| 2,021 | 107 | 5 |
| 2,022 | 67 | 4 |
| 2,023 | 99 | 5 |
| 2,024 | 50 | 3 |

---

### G2. Races most affected by null pit durations

**Question:** Are nulls from whole-race data feed failures or random individual stops?

**Interpretation guide:**  
null_stops ≈ total_stops → entire race had no timing data (feed failure).
null_stops << total_stops → individual stops missing, random gaps.

**Results:** 20 rows

| year | round | race_name | raceId | null_duration_stops | total_stops_in_race | pct_null |
| --- | --- | --- | --- | --- | --- | --- |
| 2,023 | 3 | Australian Grand Prix | 1,100 | 46 | 65 | 70.8 |
| 2,016 | 20 | Brazilian Grand Prix | 967 | 36 | 62 | 58.1 |
| 2,021 | 21 | Saudi Arabian Grand Prix | 1,072 | 35 | 47 | 74.5 |
| 2,020 | 9 | Tuscan Grand Prix | 1,039 | 25 | 66 | 37.9 |
| 2,014 | 15 | Japanese Grand Prix | 914 | 22 | 79 | 27.8 |
| 2,017 | 8 | Azerbaijan Grand Prix | 976 | 21 | 63 | 33.3 |
| 2,021 | 6 | Azerbaijan Grand Prix | 1,057 | 21 | 59 | 35.6 |
| 2,020 | 15 | Bahrain Grand Prix | 1,045 | 19 | 57 | 33.3 |
| 2,021 | 10 | British Grand Prix | 1,061 | 19 | 41 | 46.3 |
| 2,016 | 1 | Australian Grand Prix | 948 | 18 | 45 | 40 |
| 2,022 | 7 | Monaco Grand Prix | 1,080 | 18 | 53 | 34 |
| 2,022 | 18 | Japanese Grand Prix | 1,092 | 18 | 42 | 42.9 |
| 2,023 | 19 | Mexico City Grand Prix | 1,117 | 18 | 38 | 47.4 |
| 2,024 | 4 | Japanese Grand Prix | 1,124 | 18 | 54 | 33.3 |
| 2,016 | 13 | Belgian Grand Prix | 960 | 17 | 51 | 33.3 |
| 2,020 | 8 | Italian Grand Prix | 1,038 | 17 | 37 | 45.9 |
| 2,021 | 2 | Emilia Romagna Grand Prix | 1,053 | 17 | 56 | 30.4 |
| 2,022 | 10 | British Grand Prix | 1,083 | 17 | 47 | 36.2 |
| 2,023 | 13 | Dutch Grand Prix | 1,111 | 17 | 101 | 16.8 |
| 2,023 | 20 | São Paulo Grand Prix | 1,118 | 17 | 67 | 25.4 |

---

## BLOCK H — `grid_pit_lane` flag verification (OI-2)

### H1. grid_pit_lane: modern vs historic null-grid split

**Question:** Does grid_pit_lane correctly separate post-1995 pit-lane starts from pre-1996 data gaps?

**Interpretation guide:**  
Expected: grid_pit_lane = 1 only for year >= 1996 rows with null grid.
If grid_pit_lane = 1 appears in pre-1996 rows → merge_data.py year-guard failed.
If grid_pit_lane = 0 for all post-1995 null-grid rows → merge step not run yet.

**Results:** 2 rows

| era | grid_pit_lane | row_count |
| --- | --- | --- |
| historic (<1996) | 0 | 1,538 |
| modern (>=1996) | 1 | 100 |

---

### H2. grid_pit_lane = 1 rows that scored points

**Question:** Are any pit-lane-start rows scoring points with no grid — or are all of them historic data gaps?

**Interpretation guide:**  
Modern pit-lane starters (grid_pit_lane = 1) can score points — that is expected.
Pre-1996 rows with points AND grid IS NULL AND grid_pit_lane = 0 → historic data gap confirmed.
Pre-1996 rows with points AND grid_pit_lane = 1 → era-guard bug in merge_data.py.

**Results:** 7 rows

| year | grid_pit_lane | null_grid_rows_with_points | total_points |
| --- | --- | --- | --- |
| 2,015 | 1 | 1 | 1 |
| 2,019 | 1 | 4 | 13 |
| 2,020 | 1 | 1 | 1 |
| 2,021 | 1 | 2 | 14 |
| 2,022 | 1 | 2 | 3 |
| 2,023 | 1 | 3 | 18 |
| 2,024 | 1 | 1 | 2 |

---

## BLOCK I — New flag verification (OI-3, OI-5, OI-6, OI-7)

### I1. Out-of-fuel is_dnf override: classified finishers correctly marked is_dnf = 0

**Question:** Are drivers officially classified (numeric positionText) no longer flagged as DNF?

**Interpretation guide:**  
Expected after fix: 0 rows where status = 'Out of fuel' AND
positionText is numeric AND is_dnf = 1.
If rows remain → positionText override in merge_data.py did not run.

**Results:** 18 rows

| status | positionText | is_dnf | points | row_count |
| --- | --- | --- | --- | --- |
| Out of fuel | R | 1 | 0 | 21 |
| Out of fuel | 10 | 0 | 0 | 10 |
| Out of fuel | 7 | 0 | 0 | 10 |
| Out of fuel | 6 | 0 | 1 | 8 |
| Out of fuel | 8 | 0 | 0 | 8 |
| Out of fuel | 9 | 0 | 0 | 8 |
| Out of fuel | 5 | 0 | 2 | 7 |
| Out of fuel | 4 | 0 | 3 | 6 |
| Out of fuel | 11 | 0 | 0 | 5 |
| Out of fuel | 3 | 0 | 4 | 3 |
| Out of fuel | 12 | 0 | 0 | 2 |
| Out of fuel | 13 | 0 | 0 | 2 |
| Out of fuel | 15 | 0 | 0 | 2 |
| Out of fuel | 16 | 0 | 0 | 2 |
| Out of fuel | 19 | 0 | 0 | 2 |
| Out of fuel | 2 | 0 | 6 | 2 |
| Out of fuel | 14 | 0 | 0 | 1 |
| Out of fuel | 17 | 0 | 0 | 1 |

---

### I2. is_shared_drive: pre-1970 car-sharing rows flagged

**Question:** Are all duplicate raceId×driverId rows in the 1950s–60s correctly flagged?

**Interpretation guide:**  
Expected: all rows with is_shared_drive = 1 have race year < 1970.
If is_shared_drive = 1 appears in modern years → flag logic too broad.

**Results:** 42 rows

| year | race_name | shared_drive_rows | distinct_drivers |
| --- | --- | --- | --- |
| 1,950 | French Grand Prix | 2 | 1 |
| 1,950 | Indianapolis 500 | 2 | 1 |
| 1,950 | Italian Grand Prix | 4 | 2 |
| 1,951 | French Grand Prix | 6 | 3 |
| 1,951 | Italian Grand Prix | 2 | 1 |
| 1,952 | Dutch Grand Prix | 2 | 1 |
| 1,952 | French Grand Prix | 2 | 1 |
| 1,952 | Swiss Grand Prix | 2 | 1 |
| 1,953 | Belgian Grand Prix | 2 | 1 |
| 1,953 | Dutch Grand Prix | 2 | 1 |
| 1,953 | German Grand Prix | 4 | 2 |
| 1,953 | Indianapolis 500 | 18 | 8 |
| 1,953 | Swiss Grand Prix | 4 | 2 |
| 1,954 | Belgian Grand Prix | 2 | 1 |
| 1,954 | British Grand Prix | 2 | 1 |
| 1,954 | German Grand Prix | 2 | 1 |
| 1,954 | Indianapolis 500 | 25 | 12 |
| 1,954 | Italian Grand Prix | 2 | 1 |
| 1,955 | Argentine Grand Prix | 23 | 10 |
| 1,955 | Belgian Grand Prix | 2 | 1 |
| 1,955 | British Grand Prix | 4 | 2 |
| 1,955 | Monaco Grand Prix | 4 | 2 |
| 1,956 | Argentine Grand Prix | 2 | 1 |
| 1,956 | Belgian Grand Prix | 2 | 1 |
| 1,956 | British Grand Prix | 4 | 2 |
| 1,956 | French Grand Prix | 6 | 3 |
| 1,956 | Italian Grand Prix | 6 | 3 |
| 1,956 | Monaco Grand Prix | 4 | 2 |
| 1,957 | Argentine Grand Prix | 2 | 1 |
| 1,957 | British Grand Prix | 6 | 3 |
| 1,957 | French Grand Prix | 2 | 1 |
| 1,957 | Italian Grand Prix | 2 | 1 |
| 1,957 | Monaco Grand Prix | 4 | 2 |
| 1,958 | French Grand Prix | 2 | 1 |
| 1,958 | Italian Grand Prix | 2 | 1 |
| 1,958 | Monaco Grand Prix | 2 | 1 |
| 1,960 | Argentine Grand Prix | 2 | 1 |
| 1,961 | British Grand Prix | 2 | 1 |
| 1,961 | United States Grand Prix | 2 | 1 |
| 1,962 | British Grand Prix | 2 | 1 |
| 1,964 | United States Grand Prix | 2 | 1 |
| 1,978 | Italian Grand Prix | 2 | 1 |

---

### I3. pit_data_incomplete: races with >30% null pit duration flagged

**Question:** Which races are flagged as having incomplete pit stop data?

**Interpretation guide:**  
Expected: 2023 Australian GP (70.8% null), 2021 Saudi GP (74.5%),
2016 Brazilian GP (58.1%) among the flagged races.
Column only present in master_race_table, not raw results table.

**Results:** 19 rows

| year | round | race_name | pit_data_incomplete | drivers |
| --- | --- | --- | --- | --- |
| 2,016 | 1 | Australian Grand Prix | 1 | 22 |
| 2,016 | 13 | Belgian Grand Prix | 1 | 22 |
| 2,016 | 20 | Brazilian Grand Prix | 1 | 22 |
| 2,017 | 8 | Azerbaijan Grand Prix | 1 | 20 |
| 2,020 | 8 | Italian Grand Prix | 1 | 20 |
| 2,020 | 9 | Tuscan Grand Prix | 1 | 20 |
| 2,020 | 15 | Bahrain Grand Prix | 1 | 20 |
| 2,021 | 2 | Emilia Romagna Grand Prix | 1 | 20 |
| 2,021 | 6 | Azerbaijan Grand Prix | 1 | 20 |
| 2,021 | 10 | British Grand Prix | 1 | 20 |
| 2,021 | 21 | Saudi Arabian Grand Prix | 1 | 20 |
| 2,022 | 7 | Monaco Grand Prix | 1 | 20 |
| 2,022 | 10 | British Grand Prix | 1 | 20 |
| 2,022 | 18 | Japanese Grand Prix | 1 | 20 |
| 2,023 | 3 | Australian Grand Prix | 1 | 20 |
| 2,023 | 19 | Mexico City Grand Prix | 1 | 20 |
| 2,024 | 4 | Japanese Grand Prix | 1 | 20 |
| 2,024 | 8 | Monaco Grand Prix | 1 | 20 |
| 2,024 | 21 | São Paulo Grand Prix | 1 | 20 |

---

### I4. OI-7 status rows now classified as DNF

**Question:** Are Stalled/Seat/Driver Seat/Not restarted rows now is_dnf = 1?

**Interpretation guide:**  
Expected: all 6 confirmed resultIds show is_dnf = 1.
resultIds: 327 (Glock/Driver Seat), 1973 (Pizzonia/Launch control),
2622 (Häkkinen/Stalled), 20098 (Rathmann/Stalled),
3083 (de la Rosa/Not restarted), 23533 (Pérez/Seat).

**Results:** 6 rows

| resultId | year | race_name | full_name | positionText | status | is_dnf |
| --- | --- | --- | --- | --- | --- | --- |
| 327 | 2,008 | Japanese Grand Prix | Timo Glock | R | Driver Seat | 1 |
| 1,973 | 2,003 | Spanish Grand Prix | Antônio Pizzonia | R | Launch control | 1 |
| 2,622 | 2,001 | Brazilian Grand Prix | Mika Häkkinen | R | Stalled | 1 |
| 3,083 | 2,000 | Monaco Grand Prix | Pedro de la Rosa | R | Not restarted | 1 |
| 20,098 | 1,950 | Indianapolis 500 | Dick Rathmann | R | Stalled | 1 |
| 23,533 | 2,017 | Azerbaijan Grand Prix | Sergio Pérez | R | Seat | 1 |

---

## Summary

- Queries run: **27**
- Queries failed: **0**
- Generated: 2026-03-01 17:14:13

_Run `validate_data.py` after any fixes to regenerate the main quality report._