# F1 Race-Level Podium Predictions

> **Generated:** 2026-03-07 16:54:55  
> **Filter:** Default: test set (2023–2024)  
> **Races:** 46  
> **Models:** Logistic Regression, XGBoost  
> **Task:** Predict the 3 most likely podium finishers per race  

────────────────────────────────────────────────────────────

## Summary — Precision@3 Across All Races

> Precision@3: fraction of the model's top-3 picks that actually finished on the podium.
> Averaged across all races where actual results are available.
> Maximum possible = 1.00 (all 3 picks correct every race).

| Model | Races Evaluated | Mean Precision@3 | Best Race | Worst Race |
|-------|----------------:|-----------------:|----------:|----------:|
| Logistic Regression | 46 | 60.14% | 100% | 0% |
| XGBoost | 46 | 65.22% | 100% | 0% |

────────────────────────────────────────────────────────────

## 2023 Bahrain GP  ·  Round 1 | 2023-03-05

**Drivers in race:** 20  
**Actuals available:** Yes

### Logistic Regression

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **90%** | ✅ Podium |
| 2 | Sergio Pérez | **84%** | ✅ Podium |
| 3 | Charles Leclerc | **80%** | ❌ No |

**Precision@3:** 67%  (1/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 89.8% | ✅ |
| 2 | Sergio Pérez | 83.7% | ✅ |
| 3 | Charles Leclerc | 80.4% | — |
| 4 | Carlos Sainz | 74.7% | — |
| 5 | George Russell | 64.1% | — |
| 6 | Lewis Hamilton | 60.6% | — |
| 7 | Fernando Alonso | 59.1% | ✅ |
| 8 | Lance Stroll | 42.4% | — |
| 9 | Esteban Ocon | 37.0% | — |
| 10 | Nico Hülkenberg | 32.9% | — |
| 11 | Lando Norris | 27.9% | — |
| 12 | Valtteri Bottas | 22.9% | — |
| 13 | Guanyu Zhou | 19.5% | — |
| 14 | Yuki Tsunoda | 16.6% | — |
| 15 | Alexander Albon | 13.8% | — |
| 16 | Logan Sargeant | 9.9% | — |
| 17 | Kevin Magnussen | 9.1% | — |
| 18 | Oscar Piastri | 6.4% | — |
| 19 | Nyck de Vries | 6.1% | — |
| 20 | Pierre Gasly | 4.9% | — |

</details>

### XGBoost

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **98%** | ✅ Podium |
| 2 | Sergio Pérez | **91%** | ✅ Podium |
| 3 | Charles Leclerc | **88%** | ❌ No |

**Precision@3:** 67%  (1/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 98.2% | ✅ |
| 2 | Sergio Pérez | 91.3% | ✅ |
| 3 | Charles Leclerc | 87.6% | — |
| 4 | Carlos Sainz | 70.3% | — |
| 5 | George Russell | 62.5% | — |
| 6 | Fernando Alonso | 45.3% | ✅ |
| 7 | Lewis Hamilton | 35.0% | — |
| 8 | Lance Stroll | 14.6% | — |
| 9 | Esteban Ocon | 11.6% | — |
| 10 | Lando Norris | 4.8% | — |
| 11 | Valtteri Bottas | 3.6% | — |
| 12 | Nico Hülkenberg | 3.0% | — |
| 13 | Kevin Magnussen | 1.6% | — |
| 14 | Yuki Tsunoda | 1.3% | — |
| 15 | Pierre Gasly | 1.2% | — |
| 16 | Guanyu Zhou | 0.9% | — |
| 17 | Alexander Albon | 0.8% | — |
| 18 | Logan Sargeant | 0.8% | — |
| 19 | Oscar Piastri | 0.4% | — |
| 20 | Nyck de Vries | 0.3% | — |

</details>

────────────────────────────────────────────────────────────

## 2023 Saudi Arabian GP  ·  Round 2 | 2023-03-19

**Drivers in race:** 20  
**Actuals available:** Yes

### Logistic Regression

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Sergio Pérez | **97%** | ✅ Podium |
| 2 | Fernando Alonso | **81%** | ✅ Podium |
| 3 | Max Verstappen | **72%** | ✅ Podium |

**Precision@3:** 100%  (3/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Sergio Pérez | 97.1% | ✅ |
| 2 | Fernando Alonso | 81.0% | ✅ |
| 3 | Max Verstappen | 72.3% | ✅ |
| 4 | Carlos Sainz | 56.1% | — |
| 5 | George Russell | 55.9% | — |
| 6 | Lance Stroll | 49.1% | — |
| 7 | Lewis Hamilton | 36.4% | — |
| 8 | Charles Leclerc | 24.9% | — |
| 9 | Esteban Ocon | 24.5% | — |
| 10 | Pierre Gasly | 9.2% | — |
| 11 | Nico Hülkenberg | 6.8% | — |
| 12 | Oscar Piastri | 6.5% | — |
| 13 | Guanyu Zhou | 6.1% | — |
| 14 | Valtteri Bottas | 3.6% | — |
| 15 | Kevin Magnussen | 3.1% | — |
| 16 | Yuki Tsunoda | 2.1% | — |
| 17 | Alexander Albon | 1.9% | — |
| 18 | Nyck de Vries | 1.1% | — |
| 19 | Lando Norris | 0.6% | — |
| 20 | Logan Sargeant | 0.0% | — |

</details>

### XGBoost

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Sergio Pérez | **98%** | ✅ Podium |
| 2 | Max Verstappen | **83%** | ✅ Podium |
| 3 | Charles Leclerc | **77%** | ❌ No |

**Precision@3:** 67%  (1/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Sergio Pérez | 98.1% | ✅ |
| 2 | Max Verstappen | 82.7% | ✅ |
| 3 | Charles Leclerc | 76.8% | — |
| 4 | Fernando Alonso | 71.9% | ✅ |
| 5 | George Russell | 65.2% | — |
| 6 | Carlos Sainz | 48.3% | — |
| 7 | Lance Stroll | 30.2% | — |
| 8 | Lewis Hamilton | 29.3% | — |
| 9 | Esteban Ocon | 28.3% | — |
| 10 | Pierre Gasly | 14.8% | — |
| 11 | Kevin Magnussen | 4.1% | — |
| 12 | Nico Hülkenberg | 3.3% | — |
| 13 | Guanyu Zhou | 3.1% | — |
| 14 | Oscar Piastri | 2.3% | — |
| 15 | Yuki Tsunoda | 1.0% | — |
| 16 | Valtteri Bottas | 0.9% | — |
| 17 | Alexander Albon | 0.4% | — |
| 18 | Lando Norris | 0.2% | — |
| 19 | Logan Sargeant | 0.2% | — |
| 20 | Nyck de Vries | 0.2% | — |

</details>

────────────────────────────────────────────────────────────

## 2023 Australian GP  ·  Round 3 | 2023-04-02

**Drivers in race:** 20  
**Actuals available:** Yes

### Logistic Regression

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **98%** | ✅ Podium |
| 2 | Fernando Alonso | **81%** | ✅ Podium |
| 3 | George Russell | **72%** | ❌ No |

**Precision@3:** 67%  (1/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 98.4% | ✅ |
| 2 | Fernando Alonso | 81.1% | ✅ |
| 3 | George Russell | 72.1% | — |
| 4 | Lewis Hamilton | 67.7% | ✅ |
| 5 | Carlos Sainz | 58.2% | — |
| 6 | Lance Stroll | 53.9% | — |
| 7 | Charles Leclerc | 50.7% | — |
| 8 | Pierre Gasly | 15.1% | — |
| 9 | Sergio Pérez | 13.9% | — |
| 10 | Esteban Ocon | 13.1% | — |
| 11 | Alexander Albon | 12.9% | — |
| 12 | Nico Hülkenberg | 10.7% | — |
| 13 | Yuki Tsunoda | 6.2% | — |
| 14 | Kevin Magnussen | 4.2% | — |
| 15 | Lando Norris | 3.3% | — |
| 16 | Nyck de Vries | 3.0% | — |
| 17 | Guanyu Zhou | 2.0% | — |
| 18 | Oscar Piastri | 1.6% | — |
| 19 | Logan Sargeant | 1.2% | — |
| 20 | Valtteri Bottas | 0.2% | — |

</details>

### XGBoost

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **97%** | ✅ Podium |
| 2 | George Russell | **86%** | ❌ No |
| 3 | Lewis Hamilton | **85%** | ✅ Podium |

**Precision@3:** 67%  (1/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 96.7% | ✅ |
| 2 | George Russell | 86.3% | — |
| 3 | Lewis Hamilton | 85.3% | ✅ |
| 4 | Carlos Sainz | 53.8% | — |
| 5 | Fernando Alonso | 51.0% | ✅ |
| 6 | Charles Leclerc | 45.8% | — |
| 7 | Sergio Pérez | 45.7% | — |
| 8 | Lance Stroll | 25.9% | — |
| 9 | Yuki Tsunoda | 8.9% | — |
| 10 | Pierre Gasly | 7.0% | — |
| 11 | Esteban Ocon | 2.1% | — |
| 12 | Nico Hülkenberg | 1.6% | — |
| 13 | Kevin Magnussen | 1.5% | — |
| 14 | Alexander Albon | 0.9% | — |
| 15 | Lando Norris | 0.6% | — |
| 16 | Oscar Piastri | 0.4% | — |
| 17 | Nyck de Vries | 0.3% | — |
| 18 | Guanyu Zhou | 0.3% | — |
| 19 | Logan Sargeant | 0.3% | — |
| 20 | Valtteri Bottas | 0.2% | — |

</details>

────────────────────────────────────────────────────────────

## 2023 Azerbaijan GP  ·  Round 4 | 2023-04-30

**Drivers in race:** 20  
**Actuals available:** Yes

### Logistic Regression

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **97%** | ✅ Podium |
| 2 | Sergio Pérez | **93%** | ✅ Podium |
| 3 | Charles Leclerc | **70%** | ✅ Podium |

**Precision@3:** 100%  (3/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 97.3% | ✅ |
| 2 | Sergio Pérez | 93.4% | ✅ |
| 3 | Charles Leclerc | 69.6% | ✅ |
| 4 | Fernando Alonso | 68.8% | — |
| 5 | Lewis Hamilton | 63.9% | — |
| 6 | Carlos Sainz | 49.3% | — |
| 7 | Lance Stroll | 31.6% | — |
| 8 | George Russell | 25.4% | — |
| 9 | Lando Norris | 12.3% | — |
| 10 | Yuki Tsunoda | 10.2% | — |
| 11 | Oscar Piastri | 5.9% | — |
| 12 | Alexander Albon | 4.1% | — |
| 13 | Valtteri Bottas | 3.6% | — |
| 14 | Guanyu Zhou | 2.4% | — |
| 15 | Logan Sargeant | 1.8% | — |
| 16 | Kevin Magnussen | 1.8% | — |
| 17 | Pierre Gasly | 1.4% | — |
| 18 | Nyck de Vries | 1.2% | — |
| 19 | Esteban Ocon | 0.2% | — |
| 20 | Nico Hülkenberg | 0.2% | — |

</details>

### XGBoost

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **97%** | ✅ Podium |
| 2 | Sergio Pérez | **94%** | ✅ Podium |
| 3 | Charles Leclerc | **87%** | ✅ Podium |

**Precision@3:** 100%  (3/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 96.6% | ✅ |
| 2 | Sergio Pérez | 94.3% | ✅ |
| 3 | Charles Leclerc | 87.0% | ✅ |
| 4 | Carlos Sainz | 55.3% | — |
| 5 | Fernando Alonso | 50.4% | — |
| 6 | Lewis Hamilton | 40.0% | — |
| 7 | George Russell | 25.8% | — |
| 8 | Yuki Tsunoda | 23.9% | — |
| 9 | Lando Norris | 19.3% | — |
| 10 | Lance Stroll | 11.0% | — |
| 11 | Esteban Ocon | 1.8% | — |
| 12 | Oscar Piastri | 0.7% | — |
| 13 | Pierre Gasly | 0.5% | — |
| 14 | Alexander Albon | 0.5% | — |
| 15 | Guanyu Zhou | 0.4% | — |
| 16 | Nico Hülkenberg | 0.3% | — |
| 17 | Valtteri Bottas | 0.3% | — |
| 18 | Nyck de Vries | 0.2% | — |
| 19 | Kevin Magnussen | 0.1% | — |
| 20 | Logan Sargeant | 0.0% | — |

</details>

────────────────────────────────────────────────────────────

## 2023 Miami GP  ·  Round 5 | 2023-05-07

**Drivers in race:** 20  
**Actuals available:** Yes

### Logistic Regression

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Sergio Pérez | **96%** | ✅ Podium |
| 2 | Max Verstappen | **90%** | ✅ Podium |
| 3 | Fernando Alonso | **79%** | ✅ Podium |

**Precision@3:** 100%  (3/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Sergio Pérez | 96.3% | ✅ |
| 2 | Max Verstappen | 90.2% | ✅ |
| 3 | Fernando Alonso | 79.3% | ✅ |
| 4 | Carlos Sainz | 60.1% | — |
| 5 | Charles Leclerc | 48.6% | — |
| 6 | George Russell | 44.7% | — |
| 7 | Lewis Hamilton | 21.4% | — |
| 8 | Kevin Magnussen | 19.2% | — |
| 9 | Pierre Gasly | 18.2% | — |
| 10 | Esteban Ocon | 12.4% | — |
| 11 | Valtteri Bottas | 5.9% | — |
| 12 | Lance Stroll | 5.0% | — |
| 13 | Alexander Albon | 4.9% | — |
| 14 | Nico Hülkenberg | 4.6% | — |
| 15 | Guanyu Zhou | 2.6% | — |
| 16 | Nyck de Vries | 2.3% | — |
| 17 | Lando Norris | 2.1% | — |
| 18 | Yuki Tsunoda | 1.6% | — |
| 19 | Oscar Piastri | 0.9% | — |
| 20 | Logan Sargeant | 0.5% | — |

</details>

### XGBoost

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Sergio Pérez | **97%** | ✅ Podium |
| 2 | Max Verstappen | **78%** | ✅ Podium |
| 3 | Fernando Alonso | **77%** | ✅ Podium |

**Precision@3:** 100%  (3/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Sergio Pérez | 97.0% | ✅ |
| 2 | Max Verstappen | 78.2% | ✅ |
| 3 | Fernando Alonso | 76.8% | ✅ |
| 4 | Carlos Sainz | 60.8% | — |
| 5 | Charles Leclerc | 56.0% | — |
| 6 | George Russell | 52.5% | — |
| 7 | Lewis Hamilton | 21.8% | — |
| 8 | Esteban Ocon | 14.4% | — |
| 9 | Lance Stroll | 8.6% | — |
| 10 | Pierre Gasly | 6.2% | — |
| 11 | Kevin Magnussen | 4.5% | — |
| 12 | Lando Norris | 1.4% | — |
| 13 | Valtteri Bottas | 1.4% | — |
| 14 | Yuki Tsunoda | 1.4% | — |
| 15 | Nico Hülkenberg | 1.3% | — |
| 16 | Alexander Albon | 0.8% | — |
| 17 | Oscar Piastri | 0.8% | — |
| 18 | Guanyu Zhou | 0.8% | — |
| 19 | Nyck de Vries | 0.2% | — |
| 20 | Logan Sargeant | 0.1% | — |

</details>

────────────────────────────────────────────────────────────

## 2023 Monaco GP  ·  Round 6 | 2023-05-28

**Drivers in race:** 20  
**Actuals available:** Yes

### Logistic Regression

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **98%** | ✅ Podium |
| 2 | Fernando Alonso | **83%** | ✅ Podium |
| 3 | Lewis Hamilton | **62%** | ❌ No |

**Precision@3:** 67%  (1/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 98.4% | ✅ |
| 2 | Fernando Alonso | 83.1% | ✅ |
| 3 | Lewis Hamilton | 62.1% | — |
| 4 | Carlos Sainz | 59.6% | — |
| 5 | Charles Leclerc | 55.4% | — |
| 6 | George Russell | 39.2% | — |
| 7 | Esteban Ocon | 33.8% | ✅ |
| 8 | Sergio Pérez | 33.4% | — |
| 9 | Pierre Gasly | 16.4% | — |
| 10 | Lance Stroll | 11.1% | — |
| 11 | Yuki Tsunoda | 9.4% | — |
| 12 | Lando Norris | 7.5% | — |
| 13 | Oscar Piastri | 4.9% | — |
| 14 | Nyck de Vries | 4.7% | — |
| 15 | Alexander Albon | 3.5% | — |
| 16 | Valtteri Bottas | 2.4% | — |
| 17 | Kevin Magnussen | 1.7% | — |
| 18 | Nico Hülkenberg | 1.4% | — |
| 19 | Logan Sargeant | 1.2% | — |
| 20 | Guanyu Zhou | 1.0% | — |

</details>

### XGBoost

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **96%** | ✅ Podium |
| 2 | Fernando Alonso | **90%** | ✅ Podium |
| 3 | Carlos Sainz | **60%** | ❌ No |

**Precision@3:** 67%  (1/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 95.7% | ✅ |
| 2 | Fernando Alonso | 90.4% | ✅ |
| 3 | Carlos Sainz | 60.4% | — |
| 4 | Lewis Hamilton | 60.0% | — |
| 5 | Charles Leclerc | 49.7% | — |
| 6 | Esteban Ocon | 28.8% | ✅ |
| 7 | George Russell | 21.7% | — |
| 8 | Sergio Pérez | 19.4% | — |
| 9 | Pierre Gasly | 8.7% | — |
| 10 | Lance Stroll | 5.4% | — |
| 11 | Yuki Tsunoda | 1.6% | — |
| 12 | Lando Norris | 0.6% | — |
| 13 | Kevin Magnussen | 0.5% | — |
| 14 | Alexander Albon | 0.4% | — |
| 15 | Valtteri Bottas | 0.3% | — |
| 16 | Logan Sargeant | 0.3% | — |
| 17 | Nico Hülkenberg | 0.2% | — |
| 18 | Oscar Piastri | 0.2% | — |
| 19 | Nyck de Vries | 0.2% | — |
| 20 | Guanyu Zhou | 0.1% | — |

</details>

────────────────────────────────────────────────────────────

## 2023 Spanish GP  ·  Round 7 | 2023-06-04

**Drivers in race:** 20  
**Actuals available:** Yes

### Logistic Regression

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **98%** | ✅ Podium |
| 2 | Sergio Pérez | **72%** | ❌ No |
| 3 | Carlos Sainz | **68%** | ❌ No |

**Precision@3:** 33%  (0/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 98.4% | ✅ |
| 2 | Sergio Pérez | 72.2% | — |
| 3 | Carlos Sainz | 68.2% | — |
| 4 | Lewis Hamilton | 67.0% | ✅ |
| 5 | Fernando Alonso | 60.6% | — |
| 6 | Lance Stroll | 46.5% | — |
| 7 | Lando Norris | 28.5% | — |
| 8 | Esteban Ocon | 27.6% | — |
| 9 | George Russell | 21.2% | ✅ |
| 10 | Nico Hülkenberg | 12.1% | — |
| 11 | Pierre Gasly | 11.4% | — |
| 12 | Oscar Piastri | 8.0% | — |
| 13 | Charles Leclerc | 6.3% | — |
| 14 | Guanyu Zhou | 3.6% | — |
| 15 | Nyck de Vries | 3.1% | — |
| 16 | Yuki Tsunoda | 2.6% | — |
| 17 | Valtteri Bottas | 1.9% | — |
| 18 | Kevin Magnussen | 1.6% | — |
| 19 | Alexander Albon | 1.1% | — |
| 20 | Logan Sargeant | 0.5% | — |

</details>

### XGBoost

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **96%** | ✅ Podium |
| 2 | Carlos Sainz | **76%** | ❌ No |
| 3 | Lewis Hamilton | **73%** | ✅ Podium |

**Precision@3:** 67%  (1/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 96.1% | ✅ |
| 2 | Carlos Sainz | 76.0% | — |
| 3 | Lewis Hamilton | 73.1% | ✅ |
| 4 | Sergio Pérez | 34.7% | — |
| 5 | Lance Stroll | 25.2% | — |
| 6 | Fernando Alonso | 21.6% | — |
| 7 | George Russell | 18.1% | ✅ |
| 8 | Lando Norris | 14.2% | — |
| 9 | Charles Leclerc | 10.9% | — |
| 10 | Esteban Ocon | 6.6% | — |
| 11 | Nico Hülkenberg | 3.5% | — |
| 12 | Yuki Tsunoda | 1.5% | — |
| 13 | Pierre Gasly | 0.9% | — |
| 14 | Nyck de Vries | 0.8% | — |
| 15 | Oscar Piastri | 0.8% | — |
| 16 | Guanyu Zhou | 0.4% | — |
| 17 | Kevin Magnussen | 0.4% | — |
| 18 | Alexander Albon | 0.3% | — |
| 19 | Valtteri Bottas | 0.2% | — |
| 20 | Logan Sargeant | 0.1% | — |

</details>

────────────────────────────────────────────────────────────

## 2023 Canadian GP  ·  Round 8 | 2023-06-18

**Drivers in race:** 20  
**Actuals available:** Yes

### Logistic Regression

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **99%** | ✅ Podium |
| 2 | Fernando Alonso | **82%** | ✅ Podium |
| 3 | Lewis Hamilton | **75%** | ✅ Podium |

**Precision@3:** 100%  (3/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 98.5% | ✅ |
| 2 | Fernando Alonso | 81.6% | ✅ |
| 3 | Lewis Hamilton | 75.3% | ✅ |
| 4 | George Russell | 64.6% | — |
| 5 | Sergio Pérez | 62.7% | — |
| 6 | Charles Leclerc | 27.6% | — |
| 7 | Esteban Ocon | 25.7% | — |
| 8 | Carlos Sainz | 24.3% | — |
| 9 | Nico Hülkenberg | 16.1% | — |
| 10 | Lando Norris | 14.7% | — |
| 11 | Oscar Piastri | 9.4% | — |
| 12 | Alexander Albon | 7.9% | — |
| 13 | Lance Stroll | 6.3% | — |
| 14 | Pierre Gasly | 3.0% | — |
| 15 | Kevin Magnussen | 2.9% | — |
| 16 | Valtteri Bottas | 2.4% | — |
| 17 | Nyck de Vries | 1.2% | — |
| 18 | Yuki Tsunoda | 0.9% | — |
| 19 | Guanyu Zhou | 0.6% | — |
| 20 | Logan Sargeant | 0.6% | — |

</details>

### XGBoost

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **93%** | ✅ Podium |
| 2 | Fernando Alonso | **85%** | ✅ Podium |
| 3 | Lewis Hamilton | **64%** | ✅ Podium |

**Precision@3:** 100%  (3/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 93.4% | ✅ |
| 2 | Fernando Alonso | 84.5% | ✅ |
| 3 | Lewis Hamilton | 64.3% | ✅ |
| 4 | George Russell | 56.2% | — |
| 5 | Carlos Sainz | 17.2% | — |
| 6 | Sergio Pérez | 14.6% | — |
| 7 | Charles Leclerc | 10.5% | — |
| 8 | Esteban Ocon | 5.3% | — |
| 9 | Alexander Albon | 3.2% | — |
| 10 | Lance Stroll | 2.9% | — |
| 11 | Lando Norris | 2.7% | — |
| 12 | Oscar Piastri | 1.7% | — |
| 13 | Nico Hülkenberg | 0.8% | — |
| 14 | Pierre Gasly | 0.2% | — |
| 15 | Yuki Tsunoda | 0.1% | — |
| 16 | Kevin Magnussen | 0.1% | — |
| 17 | Logan Sargeant | 0.0% | — |
| 18 | Guanyu Zhou | 0.0% | — |
| 19 | Valtteri Bottas | 0.0% | — |
| 20 | Nyck de Vries | 0.0% | — |

</details>

────────────────────────────────────────────────────────────

## 2023 Austrian GP  ·  Round 9 | 2023-07-02

**Drivers in race:** 20  
**Actuals available:** Yes

### Logistic Regression

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **98%** | ✅ Podium |
| 2 | Lewis Hamilton | **69%** | ❌ No |
| 3 | Charles Leclerc | **67%** | ✅ Podium |

**Precision@3:** 67%  (1/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 98.3% | ✅ |
| 2 | Lewis Hamilton | 68.8% | — |
| 3 | Charles Leclerc | 66.9% | ✅ |
| 4 | Carlos Sainz | 60.6% | — |
| 5 | Fernando Alonso | 60.0% | — |
| 6 | Sergio Pérez | 43.0% | ✅ |
| 7 | Lance Stroll | 34.6% | — |
| 8 | George Russell | 26.0% | — |
| 9 | Lando Norris | 21.1% | — |
| 10 | Pierre Gasly | 10.7% | — |
| 11 | Nico Hülkenberg | 8.2% | — |
| 12 | Esteban Ocon | 7.7% | — |
| 13 | Alexander Albon | 5.2% | — |
| 14 | Oscar Piastri | 2.7% | — |
| 15 | Valtteri Bottas | 2.3% | — |
| 16 | Yuki Tsunoda | 1.6% | — |
| 17 | Guanyu Zhou | 1.2% | — |
| 18 | Logan Sargeant | 0.7% | — |
| 19 | Nyck de Vries | 0.1% | — |
| 20 | Kevin Magnussen | 0.1% | — |

</details>

### XGBoost

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **94%** | ✅ Podium |
| 2 | Charles Leclerc | **87%** | ✅ Podium |
| 3 | Carlos Sainz | **70%** | ❌ No |

**Precision@3:** 67%  (1/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 93.6% | ✅ |
| 2 | Charles Leclerc | 87.4% | ✅ |
| 3 | Carlos Sainz | 70.1% | — |
| 4 | Lewis Hamilton | 63.9% | — |
| 5 | Fernando Alonso | 57.9% | — |
| 6 | Lance Stroll | 38.6% | — |
| 7 | Sergio Pérez | 20.0% | ✅ |
| 8 | George Russell | 12.3% | — |
| 9 | Lando Norris | 7.7% | — |
| 10 | Esteban Ocon | 1.4% | — |
| 11 | Pierre Gasly | 0.9% | — |
| 12 | Nico Hülkenberg | 0.6% | — |
| 13 | Oscar Piastri | 0.4% | — |
| 14 | Alexander Albon | 0.3% | — |
| 15 | Yuki Tsunoda | 0.2% | — |
| 16 | Valtteri Bottas | 0.2% | — |
| 17 | Logan Sargeant | 0.1% | — |
| 18 | Guanyu Zhou | 0.1% | — |
| 19 | Nyck de Vries | 0.1% | — |
| 20 | Kevin Magnussen | 0.1% | — |

</details>

────────────────────────────────────────────────────────────

## 2023 British GP  ·  Round 10 | 2023-07-09

**Drivers in race:** 20  
**Actuals available:** Yes

### Logistic Regression

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **99%** | ✅ Podium |
| 2 | Charles Leclerc | **68%** | ❌ No |
| 3 | Lewis Hamilton | **63%** | ✅ Podium |

**Precision@3:** 67%  (1/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 98.9% | ✅ |
| 2 | Charles Leclerc | 67.7% | — |
| 3 | Lewis Hamilton | 63.3% | ✅ |
| 4 | Carlos Sainz | 58.2% | — |
| 5 | George Russell | 56.3% | — |
| 6 | Fernando Alonso | 52.9% | — |
| 7 | Sergio Pérez | 44.5% | — |
| 8 | Lando Norris | 37.2% | ✅ |
| 9 | Oscar Piastri | 24.2% | — |
| 10 | Lance Stroll | 13.0% | — |
| 11 | Pierre Gasly | 10.7% | — |
| 12 | Alexander Albon | 10.2% | — |
| 13 | Esteban Ocon | 6.7% | — |
| 14 | Nico Hülkenberg | 4.8% | — |
| 15 | Logan Sargeant | 1.9% | — |
| 16 | Yuki Tsunoda | 1.5% | — |
| 17 | Guanyu Zhou | 1.2% | — |
| 18 | Nyck de Vries | 0.9% | — |
| 19 | Valtteri Bottas | 0.7% | — |
| 20 | Kevin Magnussen | 0.6% | — |

</details>

### XGBoost

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **97%** | ✅ Podium |
| 2 | Charles Leclerc | **68%** | ❌ No |
| 3 | George Russell | **46%** | ❌ No |

**Precision@3:** 33%  (0/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 97.3% | ✅ |
| 2 | Charles Leclerc | 67.9% | — |
| 3 | George Russell | 45.8% | — |
| 4 | Lewis Hamilton | 44.3% | ✅ |
| 5 | Carlos Sainz | 32.9% | — |
| 6 | Lando Norris | 28.4% | ✅ |
| 7 | Sergio Pérez | 22.1% | — |
| 8 | Fernando Alonso | 16.6% | — |
| 9 | Oscar Piastri | 9.2% | — |
| 10 | Lance Stroll | 2.3% | — |
| 11 | Pierre Gasly | 1.6% | — |
| 12 | Alexander Albon | 0.8% | — |
| 13 | Esteban Ocon | 0.3% | — |
| 14 | Yuki Tsunoda | 0.1% | — |
| 15 | Nico Hülkenberg | 0.1% | — |
| 16 | Valtteri Bottas | 0.1% | — |
| 17 | Logan Sargeant | 0.1% | — |
| 18 | Guanyu Zhou | 0.0% | — |
| 19 | Kevin Magnussen | 0.0% | — |
| 20 | Nyck de Vries | 0.0% | — |

</details>

────────────────────────────────────────────────────────────

## 2023 Hungarian GP  ·  Round 11 | 2023-07-23

**Drivers in race:** 20  
**Actuals available:** Yes

### Logistic Regression

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **99%** | ✅ Podium |
| 2 | Lewis Hamilton | **87%** | ❌ No |
| 3 | Sergio Pérez | **77%** | ✅ Podium |

**Precision@3:** 67%  (1/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 98.7% | ✅ |
| 2 | Lewis Hamilton | 87.4% | — |
| 3 | Sergio Pérez | 76.9% | ✅ |
| 4 | Charles Leclerc | 55.4% | — |
| 5 | Fernando Alonso | 55.3% | — |
| 6 | Lando Norris | 38.8% | ✅ |
| 7 | Carlos Sainz | 24.9% | — |
| 8 | Oscar Piastri | 23.2% | — |
| 9 | Guanyu Zhou | 16.7% | — |
| 10 | Valtteri Bottas | 11.8% | — |
| 11 | Lance Stroll | 8.3% | — |
| 12 | George Russell | 7.7% | — |
| 13 | Esteban Ocon | 7.7% | — |
| 14 | Nico Hülkenberg | 6.6% | — |
| 15 | Daniel Ricciardo | 4.8% | — |
| 16 | Pierre Gasly | 3.2% | — |
| 17 | Alexander Albon | 1.8% | — |
| 18 | Yuki Tsunoda | 1.3% | — |
| 19 | Kevin Magnussen | 0.8% | — |
| 20 | Logan Sargeant | 0.5% | — |

</details>

### XGBoost

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **96%** | ✅ Podium |
| 2 | Lewis Hamilton | **92%** | ❌ No |
| 3 | Lando Norris | **48%** | ✅ Podium |

**Precision@3:** 67%  (1/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 95.7% | ✅ |
| 2 | Lewis Hamilton | 91.7% | — |
| 3 | Lando Norris | 48.2% | ✅ |
| 4 | Charles Leclerc | 41.3% | — |
| 5 | Sergio Pérez | 33.2% | ✅ |
| 6 | Fernando Alonso | 32.1% | — |
| 7 | Lance Stroll | 10.3% | — |
| 8 | George Russell | 7.0% | — |
| 9 | Carlos Sainz | 6.5% | — |
| 10 | Oscar Piastri | 4.4% | — |
| 11 | Esteban Ocon | 2.6% | — |
| 12 | Guanyu Zhou | 1.7% | — |
| 13 | Pierre Gasly | 1.4% | — |
| 14 | Valtteri Bottas | 1.2% | — |
| 15 | Daniel Ricciardo | 0.5% | — |
| 16 | Nico Hülkenberg | 0.3% | — |
| 17 | Alexander Albon | 0.1% | — |
| 18 | Yuki Tsunoda | 0.1% | — |
| 19 | Logan Sargeant | 0.1% | — |
| 20 | Kevin Magnussen | 0.1% | — |

</details>

────────────────────────────────────────────────────────────

## 2023 Belgian GP  ·  Round 12 | 2023-07-30

**Drivers in race:** 20  
**Actuals available:** Yes

### Logistic Regression

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **98%** | ✅ Podium |
| 2 | Sergio Pérez | **94%** | ✅ Podium |
| 3 | Lewis Hamilton | **82%** | ❌ No |

**Precision@3:** 67%  (1/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 97.8% | ✅ |
| 2 | Sergio Pérez | 94.3% | ✅ |
| 3 | Lewis Hamilton | 82.3% | — |
| 4 | Charles Leclerc | 78.7% | ✅ |
| 5 | Carlos Sainz | 61.1% | — |
| 6 | Fernando Alonso | 46.7% | — |
| 7 | George Russell | 44.1% | — |
| 8 | Lando Norris | 25.5% | — |
| 9 | Oscar Piastri | 22.3% | — |
| 10 | Lance Stroll | 15.8% | — |
| 11 | Pierre Gasly | 3.3% | — |
| 12 | Yuki Tsunoda | 2.8% | — |
| 13 | Esteban Ocon | 2.0% | — |
| 14 | Valtteri Bottas | 1.6% | — |
| 15 | Kevin Magnussen | 0.8% | — |
| 16 | Alexander Albon | 0.6% | — |
| 17 | Guanyu Zhou | 0.3% | — |
| 18 | Logan Sargeant | 0.2% | — |
| 19 | Daniel Ricciardo | 0.2% | — |
| 20 | Nico Hülkenberg | 0.0% | — |

</details>

### XGBoost

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **86%** | ✅ Podium |
| 2 | Sergio Pérez | **79%** | ✅ Podium |
| 3 | Lewis Hamilton | **73%** | ❌ No |

**Precision@3:** 67%  (1/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 85.7% | ✅ |
| 2 | Sergio Pérez | 78.7% | ✅ |
| 3 | Lewis Hamilton | 73.4% | — |
| 4 | Charles Leclerc | 72.8% | ✅ |
| 5 | Carlos Sainz | 35.4% | — |
| 6 | Fernando Alonso | 19.0% | — |
| 7 | George Russell | 16.6% | — |
| 8 | Lando Norris | 6.5% | — |
| 9 | Oscar Piastri | 3.0% | — |
| 10 | Lance Stroll | 1.4% | — |
| 11 | Esteban Ocon | 0.5% | — |
| 12 | Pierre Gasly | 0.2% | — |
| 13 | Alexander Albon | 0.1% | — |
| 14 | Yuki Tsunoda | 0.1% | — |
| 15 | Daniel Ricciardo | 0.1% | — |
| 16 | Valtteri Bottas | 0.1% | — |
| 17 | Nico Hülkenberg | 0.1% | — |
| 18 | Guanyu Zhou | 0.0% | — |
| 19 | Kevin Magnussen | 0.0% | — |
| 20 | Logan Sargeant | 0.0% | — |

</details>

────────────────────────────────────────────────────────────

## 2023 Dutch GP  ·  Round 13 | 2023-08-27

**Drivers in race:** 20  
**Actuals available:** Yes

### Logistic Regression

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **99%** | ✅ Podium |
| 2 | Sergio Pérez | **83%** | ❌ No |
| 3 | George Russell | **66%** | ❌ No |

**Precision@3:** 33%  (0/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 99.1% | ✅ |
| 2 | Sergio Pérez | 83.4% | — |
| 3 | George Russell | 66.0% | — |
| 4 | Fernando Alonso | 63.0% | ✅ |
| 5 | Lando Norris | 47.0% | — |
| 6 | Carlos Sainz | 45.2% | — |
| 7 | Charles Leclerc | 36.5% | — |
| 8 | Alexander Albon | 18.3% | — |
| 9 | Lewis Hamilton | 14.5% | — |
| 10 | Oscar Piastri | 10.8% | — |
| 11 | Lance Stroll | 4.9% | — |
| 12 | Logan Sargeant | 2.3% | — |
| 13 | Pierre Gasly | 2.0% | ✅ |
| 14 | Esteban Ocon | 0.9% | — |
| 15 | Nico Hülkenberg | 0.9% | — |
| 16 | Guanyu Zhou | 0.6% | — |
| 17 | Yuki Tsunoda | 0.5% | — |
| 18 | Valtteri Bottas | 0.3% | — |
| 19 | Liam Lawson | 0.3% | — |
| 20 | Kevin Magnussen | 0.0% | — |

</details>

### XGBoost

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **96%** | ✅ Podium |
| 2 | George Russell | **72%** | ❌ No |
| 3 | Lando Norris | **55%** | ❌ No |

**Precision@3:** 33%  (0/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 96.5% | ✅ |
| 2 | George Russell | 71.6% | — |
| 3 | Lando Norris | 54.8% | — |
| 4 | Fernando Alonso | 45.3% | ✅ |
| 5 | Sergio Pérez | 21.9% | — |
| 6 | Carlos Sainz | 14.8% | — |
| 7 | Lewis Hamilton | 9.2% | — |
| 8 | Charles Leclerc | 4.3% | — |
| 9 | Lance Stroll | 1.7% | — |
| 10 | Oscar Piastri | 0.9% | — |
| 11 | Pierre Gasly | 0.6% | ✅ |
| 12 | Alexander Albon | 0.6% | — |
| 13 | Esteban Ocon | 0.3% | — |
| 14 | Nico Hülkenberg | 0.1% | — |
| 15 | Yuki Tsunoda | 0.1% | — |
| 16 | Liam Lawson | 0.1% | — |
| 17 | Valtteri Bottas | 0.1% | — |
| 18 | Logan Sargeant | 0.0% | — |
| 19 | Kevin Magnussen | 0.0% | — |
| 20 | Guanyu Zhou | 0.0% | — |

</details>

────────────────────────────────────────────────────────────

## 2023 Italian GP  ·  Round 14 | 2023-09-03

**Drivers in race:** 20  
**Actuals available:** Yes

### Logistic Regression

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **99%** | ✅ Podium |
| 2 | Sergio Pérez | **90%** | ✅ Podium |
| 3 | Carlos Sainz | **76%** | ✅ Podium |

**Precision@3:** 100%  (3/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 99.1% | ✅ |
| 2 | Sergio Pérez | 90.2% | ✅ |
| 3 | Carlos Sainz | 75.5% | ✅ |
| 4 | Charles Leclerc | 72.9% | — |
| 5 | George Russell | 62.5% | — |
| 6 | Lewis Hamilton | 59.3% | — |
| 7 | Fernando Alonso | 43.1% | — |
| 8 | Lando Norris | 19.0% | — |
| 9 | Oscar Piastri | 15.6% | — |
| 10 | Alexander Albon | 15.5% | — |
| 11 | Yuki Tsunoda | 4.7% | — |
| 12 | Nico Hülkenberg | 3.0% | — |
| 13 | Liam Lawson | 2.7% | — |
| 14 | Valtteri Bottas | 2.5% | — |
| 15 | Pierre Gasly | 2.3% | — |
| 16 | Esteban Ocon | 2.0% | — |
| 17 | Lance Stroll | 1.9% | — |
| 18 | Logan Sargeant | 1.6% | — |
| 19 | Guanyu Zhou | 1.6% | — |
| 20 | Kevin Magnussen | 0.7% | — |

</details>

### XGBoost

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **97%** | ✅ Podium |
| 2 | Charles Leclerc | **90%** | ❌ No |
| 3 | Carlos Sainz | **86%** | ✅ Podium |

**Precision@3:** 67%  (1/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 97.2% | ✅ |
| 2 | Charles Leclerc | 90.3% | — |
| 3 | Carlos Sainz | 86.3% | ✅ |
| 4 | George Russell | 67.8% | — |
| 5 | Sergio Pérez | 46.6% | ✅ |
| 6 | Lewis Hamilton | 21.1% | — |
| 7 | Fernando Alonso | 16.9% | — |
| 8 | Oscar Piastri | 4.4% | — |
| 9 | Lando Norris | 3.3% | — |
| 10 | Alexander Albon | 2.2% | — |
| 11 | Lance Stroll | 1.1% | — |
| 12 | Pierre Gasly | 0.5% | — |
| 13 | Yuki Tsunoda | 0.4% | — |
| 14 | Nico Hülkenberg | 0.3% | — |
| 15 | Esteban Ocon | 0.2% | — |
| 16 | Liam Lawson | 0.2% | — |
| 17 | Valtteri Bottas | 0.2% | — |
| 18 | Logan Sargeant | 0.1% | — |
| 19 | Kevin Magnussen | 0.0% | — |
| 20 | Guanyu Zhou | 0.0% | — |

</details>

────────────────────────────────────────────────────────────

## 2023 Singapore GP  ·  Round 15 | 2023-09-17

**Drivers in race:** 20  
**Actuals available:** Yes

### Logistic Regression

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **95%** | ❌ No |
| 2 | Carlos Sainz | **79%** | ✅ Podium |
| 3 | Charles Leclerc | **75%** | ❌ No |

**Precision@3:** 33%  (0/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 94.7% | — |
| 2 | Carlos Sainz | 79.0% | ✅ |
| 3 | Charles Leclerc | 75.0% | — |
| 4 | Lewis Hamilton | 73.6% | ✅ |
| 5 | George Russell | 73.5% | — |
| 6 | Sergio Pérez | 64.9% | — |
| 7 | Fernando Alonso | 58.5% | — |
| 8 | Lando Norris | 42.0% | ✅ |
| 9 | Esteban Ocon | 16.1% | — |
| 10 | Kevin Magnussen | 11.6% | — |
| 11 | Nico Hülkenberg | 7.2% | — |
| 12 | Pierre Gasly | 6.7% | — |
| 13 | Liam Lawson | 4.9% | — |
| 14 | Alexander Albon | 3.2% | — |
| 15 | Yuki Tsunoda | 2.3% | — |
| 16 | Oscar Piastri | 2.0% | — |
| 17 | Valtteri Bottas | 1.7% | — |
| 18 | Logan Sargeant | 0.8% | — |
| 19 | Lance Stroll | 0.3% | — |
| 20 | Guanyu Zhou | 0.1% | — |

</details>

### XGBoost

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Charles Leclerc | **90%** | ❌ No |
| 2 | George Russell | **90%** | ❌ No |
| 3 | Carlos Sainz | **88%** | ✅ Podium |

**Precision@3:** 33%  (0/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Charles Leclerc | 90.5% | — |
| 2 | George Russell | 89.9% | — |
| 3 | Carlos Sainz | 88.3% | ✅ |
| 4 | Lewis Hamilton | 60.4% | ✅ |
| 5 | Fernando Alonso | 52.8% | — |
| 6 | Max Verstappen | 50.8% | — |
| 7 | Lando Norris | 43.6% | ✅ |
| 8 | Sergio Pérez | 22.2% | — |
| 9 | Esteban Ocon | 5.1% | — |
| 10 | Pierre Gasly | 3.5% | — |
| 11 | Kevin Magnussen | 2.1% | — |
| 12 | Lance Stroll | 1.3% | — |
| 13 | Alexander Albon | 0.5% | — |
| 14 | Nico Hülkenberg | 0.4% | — |
| 15 | Liam Lawson | 0.4% | — |
| 16 | Yuki Tsunoda | 0.3% | — |
| 17 | Oscar Piastri | 0.2% | — |
| 18 | Valtteri Bottas | 0.1% | — |
| 19 | Logan Sargeant | 0.1% | — |
| 20 | Guanyu Zhou | 0.0% | — |

</details>

────────────────────────────────────────────────────────────

## 2023 Japanese GP  ·  Round 16 | 2023-09-24

**Drivers in race:** 20  
**Actuals available:** Yes

### Logistic Regression

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **99%** | ✅ Podium |
| 2 | Sergio Pérez | **89%** | ❌ No |
| 3 | Charles Leclerc | **70%** | ❌ No |

**Precision@3:** 33%  (0/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 99.3% | ✅ |
| 2 | Sergio Pérez | 89.5% | — |
| 3 | Charles Leclerc | 70.4% | — |
| 4 | Lewis Hamilton | 64.9% | — |
| 5 | Carlos Sainz | 59.4% | — |
| 6 | Lando Norris | 50.3% | ✅ |
| 7 | George Russell | 38.8% | — |
| 8 | Fernando Alonso | 36.7% | — |
| 9 | Oscar Piastri | 34.8% | ✅ |
| 10 | Yuki Tsunoda | 7.1% | — |
| 11 | Pierre Gasly | 6.6% | — |
| 12 | Esteban Ocon | 4.5% | — |
| 13 | Liam Lawson | 4.0% | — |
| 14 | Alexander Albon | 3.8% | — |
| 15 | Lance Stroll | 3.0% | — |
| 16 | Kevin Magnussen | 1.7% | — |
| 17 | Valtteri Bottas | 1.6% | — |
| 18 | Nico Hülkenberg | 1.0% | — |
| 19 | Guanyu Zhou | 0.8% | — |
| 20 | Logan Sargeant | 0.1% | — |

</details>

### XGBoost

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **98%** | ✅ Podium |
| 2 | Charles Leclerc | **65%** | ❌ No |
| 3 | Lando Norris | **49%** | ✅ Podium |

**Precision@3:** 67%  (1/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 97.9% | ✅ |
| 2 | Charles Leclerc | 64.7% | — |
| 3 | Lando Norris | 49.0% | ✅ |
| 4 | Sergio Pérez | 31.9% | — |
| 5 | Carlos Sainz | 26.3% | — |
| 6 | Fernando Alonso | 20.5% | — |
| 7 | Oscar Piastri | 16.8% | ✅ |
| 8 | Lewis Hamilton | 16.6% | — |
| 9 | George Russell | 14.1% | — |
| 10 | Lance Stroll | 1.6% | — |
| 11 | Pierre Gasly | 1.1% | — |
| 12 | Esteban Ocon | 0.7% | — |
| 13 | Yuki Tsunoda | 0.2% | — |
| 14 | Alexander Albon | 0.2% | — |
| 15 | Liam Lawson | 0.1% | — |
| 16 | Logan Sargeant | 0.1% | — |
| 17 | Valtteri Bottas | 0.1% | — |
| 18 | Kevin Magnussen | 0.1% | — |
| 19 | Nico Hülkenberg | 0.0% | — |
| 20 | Guanyu Zhou | 0.0% | — |

</details>

────────────────────────────────────────────────────────────

## 2023 Qatar GP  ·  Round 17 | 2023-10-08

**Drivers in race:** 20  
**Actuals available:** Yes

### Logistic Regression

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **99%** | ✅ Podium |
| 2 | Lewis Hamilton | **79%** | ❌ No |
| 3 | George Russell | **67%** | ❌ No |

**Precision@3:** 33%  (0/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 99.3% | ✅ |
| 2 | Lewis Hamilton | 79.1% | — |
| 3 | George Russell | 66.8% | — |
| 4 | Fernando Alonso | 64.3% | — |
| 5 | Charles Leclerc | 62.6% | — |
| 6 | Carlos Sainz | 24.7% | — |
| 7 | Lando Norris | 19.1% | ✅ |
| 8 | Oscar Piastri | 18.9% | ✅ |
| 9 | Pierre Gasly | 15.4% | — |
| 10 | Esteban Ocon | 12.9% | — |
| 11 | Valtteri Bottas | 5.9% | — |
| 12 | Yuki Tsunoda | 4.0% | — |
| 13 | Sergio Pérez | 3.7% | — |
| 14 | Alexander Albon | 3.0% | — |
| 15 | Lance Stroll | 2.8% | — |
| 16 | Nico Hülkenberg | 1.9% | — |
| 17 | Logan Sargeant | 1.2% | — |
| 18 | Liam Lawson | 0.9% | — |
| 19 | Kevin Magnussen | 0.7% | — |
| 20 | Guanyu Zhou | 0.6% | — |

</details>

### XGBoost

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **97%** | ✅ Podium |
| 2 | George Russell | **75%** | ❌ No |
| 3 | Lewis Hamilton | **74%** | ❌ No |

**Precision@3:** 33%  (0/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 97.2% | ✅ |
| 2 | George Russell | 75.4% | — |
| 3 | Lewis Hamilton | 74.2% | — |
| 4 | Fernando Alonso | 62.8% | — |
| 5 | Charles Leclerc | 39.0% | — |
| 6 | Sergio Pérez | 25.1% | — |
| 7 | Esteban Ocon | 9.5% | — |
| 8 | Lando Norris | 9.3% | ✅ |
| 9 | Pierre Gasly | 9.2% | — |
| 10 | Carlos Sainz | 8.6% | — |
| 11 | Oscar Piastri | 7.1% | ✅ |
| 12 | Lance Stroll | 1.5% | — |
| 13 | Valtteri Bottas | 1.2% | — |
| 14 | Yuki Tsunoda | 0.3% | — |
| 15 | Liam Lawson | 0.2% | — |
| 16 | Alexander Albon | 0.1% | — |
| 17 | Nico Hülkenberg | 0.1% | — |
| 18 | Logan Sargeant | 0.1% | — |
| 19 | Kevin Magnussen | 0.0% | — |
| 20 | Guanyu Zhou | 0.0% | — |

</details>

────────────────────────────────────────────────────────────

## 2023 United States GP  ·  Round 18 | 2023-10-22

**Drivers in race:** 20  
**Actuals available:** Yes

### Logistic Regression

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **98%** | ✅ Podium |
| 2 | Charles Leclerc | **82%** | ❌ No |
| 3 | Lewis Hamilton | **80%** | ❌ No |

**Precision@3:** 33%  (0/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 98.2% | ✅ |
| 2 | Charles Leclerc | 81.9% | — |
| 3 | Lewis Hamilton | 80.3% | — |
| 4 | Sergio Pérez | 74.0% | — |
| 5 | Carlos Sainz | 67.3% | ✅ |
| 6 | Lando Norris | 63.0% | ✅ |
| 7 | George Russell | 55.2% | — |
| 8 | Pierre Gasly | 16.8% | — |
| 9 | Esteban Ocon | 14.8% | — |
| 10 | Oscar Piastri | 11.7% | — |
| 11 | Yuki Tsunoda | 4.4% | — |
| 12 | Guanyu Zhou | 3.5% | — |
| 13 | Valtteri Bottas | 3.0% | — |
| 14 | Alexander Albon | 2.2% | — |
| 15 | Daniel Ricciardo | 2.1% | — |
| 16 | Fernando Alonso | 1.7% | — |
| 17 | Logan Sargeant | 1.1% | — |
| 18 | Lance Stroll | 0.4% | — |
| 19 | Nico Hülkenberg | 0.2% | — |
| 20 | Kevin Magnussen | 0.2% | — |

</details>

### XGBoost

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Charles Leclerc | **95%** | ❌ No |
| 2 | Max Verstappen | **81%** | ✅ Podium |
| 3 | Lewis Hamilton | **80%** | ❌ No |

**Precision@3:** 33%  (0/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Charles Leclerc | 94.5% | — |
| 2 | Max Verstappen | 80.7% | ✅ |
| 3 | Lewis Hamilton | 79.6% | — |
| 4 | Lando Norris | 65.1% | ✅ |
| 5 | Carlos Sainz | 56.1% | ✅ |
| 6 | Sergio Pérez | 32.7% | — |
| 7 | George Russell | 25.6% | — |
| 8 | Fernando Alonso | 7.5% | — |
| 9 | Pierre Gasly | 5.4% | — |
| 10 | Esteban Ocon | 4.6% | — |
| 11 | Oscar Piastri | 1.2% | — |
| 12 | Lance Stroll | 1.0% | — |
| 13 | Valtteri Bottas | 0.3% | — |
| 14 | Daniel Ricciardo | 0.2% | — |
| 15 | Alexander Albon | 0.1% | — |
| 16 | Guanyu Zhou | 0.1% | — |
| 17 | Yuki Tsunoda | 0.1% | — |
| 18 | Kevin Magnussen | 0.1% | — |
| 19 | Nico Hülkenberg | 0.1% | — |
| 20 | Logan Sargeant | 0.0% | — |

</details>

────────────────────────────────────────────────────────────

## 2023 Mexico City GP  ·  Round 19 | 2023-10-29

**Drivers in race:** 20  
**Actuals available:** Yes

### Logistic Regression

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **99%** | ✅ Podium |
| 2 | Sergio Pérez | **89%** | ❌ No |
| 3 | Charles Leclerc | **84%** | ✅ Podium |

**Precision@3:** 67%  (1/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 99.3% | ✅ |
| 2 | Sergio Pérez | 88.8% | — |
| 3 | Charles Leclerc | 84.4% | ✅ |
| 4 | Carlos Sainz | 81.4% | — |
| 5 | Lewis Hamilton | 71.2% | ✅ |
| 6 | George Russell | 44.6% | — |
| 7 | Oscar Piastri | 23.6% | — |
| 8 | Fernando Alonso | 23.1% | — |
| 9 | Daniel Ricciardo | 18.5% | — |
| 10 | Pierre Gasly | 9.0% | — |
| 11 | Valtteri Bottas | 8.1% | — |
| 12 | Guanyu Zhou | 6.2% | — |
| 13 | Lando Norris | 6.2% | — |
| 14 | Esteban Ocon | 3.9% | — |
| 15 | Nico Hülkenberg | 3.7% | — |
| 16 | Alexander Albon | 3.2% | — |
| 17 | Kevin Magnussen | 1.4% | — |
| 18 | Yuki Tsunoda | 1.2% | — |
| 19 | Logan Sargeant | 0.8% | — |
| 20 | Lance Stroll | 0.2% | — |

</details>

### XGBoost

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Charles Leclerc | **94%** | ✅ Podium |
| 2 | Max Verstappen | **91%** | ✅ Podium |
| 3 | Carlos Sainz | **82%** | ❌ No |

**Precision@3:** 67%  (1/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Charles Leclerc | 93.7% | ✅ |
| 2 | Max Verstappen | 91.2% | ✅ |
| 3 | Carlos Sainz | 82.5% | — |
| 4 | Sergio Pérez | 48.4% | — |
| 5 | Lewis Hamilton | 36.9% | ✅ |
| 6 | George Russell | 15.4% | — |
| 7 | Fernando Alonso | 7.6% | — |
| 8 | Oscar Piastri | 6.6% | — |
| 9 | Lando Norris | 2.6% | — |
| 10 | Daniel Ricciardo | 1.8% | — |
| 11 | Lance Stroll | 1.1% | — |
| 12 | Pierre Gasly | 0.9% | — |
| 13 | Valtteri Bottas | 0.3% | — |
| 14 | Alexander Albon | 0.2% | — |
| 15 | Nico Hülkenberg | 0.2% | — |
| 16 | Esteban Ocon | 0.1% | — |
| 17 | Guanyu Zhou | 0.1% | — |
| 18 | Yuki Tsunoda | 0.1% | — |
| 19 | Logan Sargeant | 0.0% | — |
| 20 | Kevin Magnussen | 0.0% | — |

</details>

────────────────────────────────────────────────────────────

## 2023 São Paulo GP  ·  Round 20 | 2023-11-05

**Drivers in race:** 20  
**Actuals available:** Yes

### Logistic Regression

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **100%** | ✅ Podium |
| 2 | Lewis Hamilton | **75%** | ❌ No |
| 3 | Sergio Pérez | **74%** | ❌ No |

**Precision@3:** 33%  (0/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 99.5% | ✅ |
| 2 | Lewis Hamilton | 75.0% | — |
| 3 | Sergio Pérez | 73.6% | — |
| 4 | Fernando Alonso | 63.8% | ✅ |
| 5 | Carlos Sainz | 57.8% | — |
| 6 | Lando Norris | 48.4% | ✅ |
| 7 | George Russell | 41.8% | — |
| 8 | Lance Stroll | 34.5% | — |
| 9 | Oscar Piastri | 12.5% | — |
| 10 | Esteban Ocon | 4.7% | — |
| 11 | Nico Hülkenberg | 4.3% | — |
| 12 | Pierre Gasly | 3.8% | — |
| 13 | Alexander Albon | 3.7% | — |
| 14 | Kevin Magnussen | 3.2% | — |
| 15 | Yuki Tsunoda | 1.7% | — |
| 16 | Daniel Ricciardo | 1.4% | — |
| 17 | Charles Leclerc | 1.1% | — |
| 18 | Valtteri Bottas | 1.1% | — |
| 19 | Logan Sargeant | 0.7% | — |
| 20 | Guanyu Zhou | 0.7% | — |

</details>

### XGBoost

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **91%** | ✅ Podium |
| 2 | Fernando Alonso | **58%** | ✅ Podium |
| 3 | Lewis Hamilton | **48%** | ❌ No |

**Precision@3:** 67%  (1/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 91.4% | ✅ |
| 2 | Fernando Alonso | 57.8% | ✅ |
| 3 | Lewis Hamilton | 48.1% | — |
| 4 | Charles Leclerc | 36.3% | — |
| 5 | Sergio Pérez | 33.4% | — |
| 6 | Lance Stroll | 30.4% | — |
| 7 | Lando Norris | 28.8% | ✅ |
| 8 | Carlos Sainz | 26.5% | — |
| 9 | George Russell | 22.9% | — |
| 10 | Oscar Piastri | 2.8% | — |
| 11 | Pierre Gasly | 1.9% | — |
| 12 | Esteban Ocon | 1.1% | — |
| 13 | Daniel Ricciardo | 0.9% | — |
| 14 | Alexander Albon | 0.4% | — |
| 15 | Valtteri Bottas | 0.3% | — |
| 16 | Nico Hülkenberg | 0.3% | — |
| 17 | Yuki Tsunoda | 0.2% | — |
| 18 | Guanyu Zhou | 0.2% | — |
| 19 | Kevin Magnussen | 0.2% | — |
| 20 | Logan Sargeant | 0.1% | — |

</details>

────────────────────────────────────────────────────────────

## 2023 Las Vegas GP  ·  Round 21 | 2023-11-19

**Drivers in race:** 20  
**Actuals available:** Yes

### Logistic Regression

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **99%** | ✅ Podium |
| 2 | Charles Leclerc | **82%** | ✅ Podium |
| 3 | George Russell | **64%** | ❌ No |

**Precision@3:** 67%  (1/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 99.4% | ✅ |
| 2 | Charles Leclerc | 82.2% | ✅ |
| 3 | George Russell | 64.1% | — |
| 4 | Sergio Pérez | 60.2% | ✅ |
| 5 | Lewis Hamilton | 46.2% | — |
| 6 | Fernando Alonso | 37.7% | — |
| 7 | Carlos Sainz | 31.6% | — |
| 8 | Pierre Gasly | 27.0% | — |
| 9 | Alexander Albon | 15.8% | — |
| 10 | Lando Norris | 10.9% | — |
| 11 | Valtteri Bottas | 9.2% | — |
| 12 | Logan Sargeant | 8.6% | — |
| 13 | Kevin Magnussen | 6.4% | — |
| 14 | Nico Hülkenberg | 2.4% | — |
| 15 | Esteban Ocon | 2.4% | — |
| 16 | Daniel Ricciardo | 2.1% | — |
| 17 | Oscar Piastri | 1.9% | — |
| 18 | Lance Stroll | 1.6% | — |
| 19 | Guanyu Zhou | 1.0% | — |
| 20 | Yuki Tsunoda | 0.5% | — |

</details>

### XGBoost

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **96%** | ✅ Podium |
| 2 | Charles Leclerc | **93%** | ✅ Podium |
| 3 | George Russell | **74%** | ❌ No |

**Precision@3:** 67%  (1/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 95.7% | ✅ |
| 2 | Charles Leclerc | 93.1% | ✅ |
| 3 | George Russell | 74.0% | — |
| 4 | Sergio Pérez | 22.8% | ✅ |
| 5 | Fernando Alonso | 19.8% | — |
| 6 | Carlos Sainz | 16.9% | — |
| 7 | Pierre Gasly | 15.8% | — |
| 8 | Lewis Hamilton | 10.3% | — |
| 9 | Valtteri Bottas | 6.9% | — |
| 10 | Lance Stroll | 6.7% | — |
| 11 | Lando Norris | 3.7% | — |
| 12 | Kevin Magnussen | 2.8% | — |
| 13 | Logan Sargeant | 1.9% | — |
| 14 | Alexander Albon | 1.5% | — |
| 15 | Daniel Ricciardo | 1.2% | — |
| 16 | Oscar Piastri | 0.8% | — |
| 17 | Nico Hülkenberg | 0.7% | — |
| 18 | Esteban Ocon | 0.2% | — |
| 19 | Guanyu Zhou | 0.1% | — |
| 20 | Yuki Tsunoda | 0.1% | — |

</details>

────────────────────────────────────────────────────────────

## 2023 Abu Dhabi GP  ·  Round 22 | 2023-11-26

**Drivers in race:** 20  
**Actuals available:** Yes

### Logistic Regression

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **100%** | ✅ Podium |
| 2 | Charles Leclerc | **82%** | ✅ Podium |
| 3 | Sergio Pérez | **74%** | ❌ No |

**Precision@3:** 67%  (1/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 99.6% | ✅ |
| 2 | Charles Leclerc | 82.4% | ✅ |
| 3 | Sergio Pérez | 74.3% | — |
| 4 | George Russell | 61.5% | ✅ |
| 5 | Lando Norris | 55.6% | — |
| 6 | Fernando Alonso | 50.0% | — |
| 7 | Lewis Hamilton | 43.9% | — |
| 8 | Oscar Piastri | 36.8% | — |
| 9 | Carlos Sainz | 16.5% | — |
| 10 | Yuki Tsunoda | 12.6% | — |
| 11 | Pierre Gasly | 10.3% | — |
| 12 | Nico Hülkenberg | 7.6% | — |
| 13 | Esteban Ocon | 7.1% | — |
| 14 | Lance Stroll | 6.6% | — |
| 15 | Alexander Albon | 3.0% | — |
| 16 | Daniel Ricciardo | 1.9% | — |
| 17 | Kevin Magnussen | 1.1% | — |
| 18 | Valtteri Bottas | 1.1% | — |
| 19 | Guanyu Zhou | 0.8% | — |
| 20 | Logan Sargeant | 0.5% | — |

</details>

### XGBoost

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **98%** | ✅ Podium |
| 2 | Charles Leclerc | **88%** | ✅ Podium |
| 3 | George Russell | **50%** | ✅ Podium |

**Precision@3:** 100%  (3/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 97.8% | ✅ |
| 2 | Charles Leclerc | 87.5% | ✅ |
| 3 | George Russell | 49.7% | ✅ |
| 4 | Fernando Alonso | 39.5% | — |
| 5 | Oscar Piastri | 35.1% | — |
| 6 | Lando Norris | 30.7% | — |
| 7 | Sergio Pérez | 20.5% | — |
| 8 | Lewis Hamilton | 12.7% | — |
| 9 | Carlos Sainz | 9.2% | — |
| 10 | Lance Stroll | 6.3% | — |
| 11 | Pierre Gasly | 2.4% | — |
| 12 | Yuki Tsunoda | 2.0% | — |
| 13 | Esteban Ocon | 2.0% | — |
| 14 | Daniel Ricciardo | 0.6% | — |
| 15 | Nico Hülkenberg | 0.4% | — |
| 16 | Valtteri Bottas | 0.4% | — |
| 17 | Alexander Albon | 0.3% | — |
| 18 | Kevin Magnussen | 0.2% | — |
| 19 | Guanyu Zhou | 0.1% | — |
| 20 | Logan Sargeant | 0.0% | — |

</details>

────────────────────────────────────────────────────────────

## 2024 Bahrain GP  ·  Round 1 | 2024-03-02

**Drivers in race:** 20  
**Actuals available:** Yes

### Logistic Regression

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **91%** | ✅ Podium |
| 2 | Charles Leclerc | **80%** | ❌ No |
| 3 | George Russell | **71%** | ❌ No |

**Precision@3:** 33%  (0/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 91.4% | ✅ |
| 2 | Charles Leclerc | 79.7% | — |
| 3 | George Russell | 71.1% | — |
| 4 | Sergio Pérez | 70.2% | ✅ |
| 5 | Carlos Sainz | 67.8% | ✅ |
| 6 | Fernando Alonso | 64.6% | — |
| 7 | Lando Norris | 58.2% | — |
| 8 | Oscar Piastri | 46.3% | — |
| 9 | Lewis Hamilton | 46.1% | — |
| 10 | Nico Hülkenberg | 33.5% | — |
| 11 | Yuki Tsunoda | 28.4% | — |
| 12 | Lance Stroll | 24.5% | — |
| 13 | Alexander Albon | 20.5% | — |
| 14 | Daniel Ricciardo | 17.3% | — |
| 15 | Kevin Magnussen | 14.2% | — |
| 16 | Valtteri Bottas | 11.5% | — |
| 17 | Guanyu Zhou | 9.6% | — |
| 18 | Logan Sargeant | 7.9% | — |
| 19 | Esteban Ocon | 6.8% | — |
| 20 | Pierre Gasly | 5.5% | — |

</details>

### XGBoost

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **98%** | ✅ Podium |
| 2 | Charles Leclerc | **92%** | ❌ No |
| 3 | George Russell | **71%** | ❌ No |

**Precision@3:** 33%  (0/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 98.1% | ✅ |
| 2 | Charles Leclerc | 92.3% | — |
| 3 | George Russell | 71.3% | — |
| 4 | Sergio Pérez | 68.1% | ✅ |
| 5 | Carlos Sainz | 54.7% | ✅ |
| 6 | Fernando Alonso | 51.5% | — |
| 7 | Lewis Hamilton | 49.3% | — |
| 8 | Lando Norris | 44.7% | — |
| 9 | Oscar Piastri | 27.2% | — |
| 10 | Lance Stroll | 12.7% | — |
| 11 | Yuki Tsunoda | 10.1% | — |
| 12 | Alexander Albon | 8.7% | — |
| 13 | Nico Hülkenberg | 4.8% | — |
| 14 | Pierre Gasly | 4.3% | — |
| 15 | Esteban Ocon | 3.0% | — |
| 16 | Kevin Magnussen | 2.8% | — |
| 17 | Daniel Ricciardo | 1.6% | — |
| 18 | Valtteri Bottas | 1.2% | — |
| 19 | Guanyu Zhou | 1.0% | — |
| 20 | Logan Sargeant | 0.8% | — |

</details>

────────────────────────────────────────────────────────────

## 2024 Saudi Arabian GP  ·  Round 2 | 2024-03-09

**Drivers in race:** 20  
**Actuals available:** Yes

### Logistic Regression

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **98%** | ✅ Podium |
| 2 | Sergio Pérez | **95%** | ✅ Podium |
| 3 | Charles Leclerc | **77%** | ✅ Podium |

**Precision@3:** 100%  (3/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 98.4% | ✅ |
| 2 | Sergio Pérez | 94.6% | ✅ |
| 3 | Charles Leclerc | 76.9% | ✅ |
| 4 | Fernando Alonso | 42.5% | — |
| 5 | Lando Norris | 36.7% | — |
| 6 | Oscar Piastri | 33.8% | — |
| 7 | George Russell | 30.1% | — |
| 8 | Lewis Hamilton | 25.9% | — |
| 9 | Oliver Bearman | 22.5% | — |
| 10 | Lance Stroll | 10.0% | — |
| 11 | Yuki Tsunoda | 8.4% | — |
| 12 | Kevin Magnussen | 3.2% | — |
| 13 | Alexander Albon | 2.9% | — |
| 14 | Daniel Ricciardo | 2.8% | — |
| 15 | Nico Hülkenberg | 2.3% | — |
| 16 | Valtteri Bottas | 1.4% | — |
| 17 | Esteban Ocon | 0.9% | — |
| 18 | Pierre Gasly | 0.7% | — |
| 19 | Guanyu Zhou | 0.7% | — |
| 20 | Logan Sargeant | 0.6% | — |

</details>

### XGBoost

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **99%** | ✅ Podium |
| 2 | Sergio Pérez | **87%** | ✅ Podium |
| 3 | Charles Leclerc | **74%** | ✅ Podium |

**Precision@3:** 100%  (3/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 99.0% | ✅ |
| 2 | Sergio Pérez | 87.0% | ✅ |
| 3 | Charles Leclerc | 74.1% | ✅ |
| 4 | Oscar Piastri | 27.8% | — |
| 5 | Fernando Alonso | 26.8% | — |
| 6 | Lando Norris | 22.5% | — |
| 7 | George Russell | 21.5% | — |
| 8 | Lewis Hamilton | 19.7% | — |
| 9 | Oliver Bearman | 8.2% | — |
| 10 | Lance Stroll | 7.0% | — |
| 11 | Yuki Tsunoda | 5.9% | — |
| 12 | Nico Hülkenberg | 0.9% | — |
| 13 | Alexander Albon | 0.8% | — |
| 14 | Kevin Magnussen | 0.7% | — |
| 15 | Guanyu Zhou | 0.6% | — |
| 16 | Daniel Ricciardo | 0.6% | — |
| 17 | Valtteri Bottas | 0.2% | — |
| 18 | Pierre Gasly | 0.1% | — |
| 19 | Esteban Ocon | 0.1% | — |
| 20 | Logan Sargeant | 0.1% | — |

</details>

────────────────────────────────────────────────────────────

## 2024 Australian GP  ·  Round 3 | 2024-03-24

**Drivers in race:** 19  
**Actuals available:** Yes

### Logistic Regression

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **99%** | ❌ No |
| 2 | Sergio Pérez | **92%** | ❌ No |
| 3 | Carlos Sainz | **85%** | ✅ Podium |

**Precision@3:** 33%  (0/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 98.8% | — |
| 2 | Sergio Pérez | 92.2% | — |
| 3 | Carlos Sainz | 85.2% | ✅ |
| 4 | Charles Leclerc | 78.4% | ✅ |
| 5 | Lando Norris | 57.5% | ✅ |
| 6 | Oscar Piastri | 40.9% | — |
| 7 | George Russell | 31.5% | — |
| 8 | Fernando Alonso | 22.8% | — |
| 9 | Lewis Hamilton | 16.7% | — |
| 10 | Lance Stroll | 16.5% | — |
| 11 | Yuki Tsunoda | 11.0% | — |
| 12 | Alexander Albon | 4.5% | — |
| 13 | Kevin Magnussen | 3.5% | — |
| 14 | Valtteri Bottas | 2.8% | — |
| 15 | Nico Hülkenberg | 2.3% | — |
| 16 | Esteban Ocon | 1.9% | — |
| 17 | Pierre Gasly | 1.3% | — |
| 18 | Daniel Ricciardo | 1.2% | — |
| 19 | Guanyu Zhou | 0.7% | — |

</details>

### XGBoost

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **98%** | ❌ No |
| 2 | Charles Leclerc | **80%** | ✅ Podium |
| 3 | Carlos Sainz | **71%** | ✅ Podium |

**Precision@3:** 67%  (1/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 97.9% | — |
| 2 | Charles Leclerc | 80.3% | ✅ |
| 3 | Carlos Sainz | 70.8% | ✅ |
| 4 | Lando Norris | 63.1% | ✅ |
| 5 | Sergio Pérez | 61.9% | — |
| 6 | Lewis Hamilton | 24.7% | — |
| 7 | George Russell | 23.3% | — |
| 8 | Oscar Piastri | 18.1% | — |
| 9 | Fernando Alonso | 8.5% | — |
| 10 | Lance Stroll | 8.3% | — |
| 11 | Yuki Tsunoda | 4.5% | — |
| 12 | Alexander Albon | 1.7% | — |
| 13 | Kevin Magnussen | 0.6% | — |
| 14 | Nico Hülkenberg | 0.3% | — |
| 15 | Esteban Ocon | 0.3% | — |
| 16 | Valtteri Bottas | 0.3% | — |
| 17 | Daniel Ricciardo | 0.2% | — |
| 18 | Guanyu Zhou | 0.1% | — |
| 19 | Pierre Gasly | 0.1% | — |

</details>

────────────────────────────────────────────────────────────

## 2024 Japanese GP  ·  Round 4 | 2024-04-07

**Drivers in race:** 20  
**Actuals available:** Yes

### Logistic Regression

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **98%** | ✅ Podium |
| 2 | Sergio Pérez | **94%** | ✅ Podium |
| 3 | Carlos Sainz | **88%** | ✅ Podium |

**Precision@3:** 100%  (3/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 97.7% | ✅ |
| 2 | Sergio Pérez | 93.7% | ✅ |
| 3 | Carlos Sainz | 87.8% | ✅ |
| 4 | Charles Leclerc | 75.3% | — |
| 5 | Lando Norris | 73.8% | — |
| 6 | Fernando Alonso | 49.7% | — |
| 7 | Oscar Piastri | 46.8% | — |
| 8 | Lewis Hamilton | 27.7% | — |
| 9 | George Russell | 18.9% | — |
| 10 | Yuki Tsunoda | 10.1% | — |
| 11 | Daniel Ricciardo | 6.9% | — |
| 12 | Nico Hülkenberg | 6.8% | — |
| 13 | Lance Stroll | 4.8% | — |
| 14 | Alexander Albon | 3.7% | — |
| 15 | Valtteri Bottas | 3.5% | — |
| 16 | Esteban Ocon | 2.4% | — |
| 17 | Kevin Magnussen | 1.9% | — |
| 18 | Pierre Gasly | 1.6% | — |
| 19 | Logan Sargeant | 1.1% | — |
| 20 | Guanyu Zhou | 0.7% | — |

</details>

### XGBoost

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **98%** | ✅ Podium |
| 2 | Sergio Pérez | **93%** | ✅ Podium |
| 3 | Lando Norris | **71%** | ❌ No |

**Precision@3:** 67%  (1/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 97.6% | ✅ |
| 2 | Sergio Pérez | 93.1% | ✅ |
| 3 | Lando Norris | 70.7% | — |
| 4 | Carlos Sainz | 54.0% | ✅ |
| 5 | Charles Leclerc | 42.6% | — |
| 6 | Oscar Piastri | 34.7% | — |
| 7 | Fernando Alonso | 33.3% | — |
| 8 | Lewis Hamilton | 17.9% | — |
| 9 | George Russell | 1.9% | — |
| 10 | Yuki Tsunoda | 1.3% | — |
| 11 | Lance Stroll | 1.0% | — |
| 12 | Nico Hülkenberg | 0.6% | — |
| 13 | Alexander Albon | 0.3% | — |
| 14 | Daniel Ricciardo | 0.2% | — |
| 15 | Esteban Ocon | 0.2% | — |
| 16 | Kevin Magnussen | 0.2% | — |
| 17 | Valtteri Bottas | 0.2% | — |
| 18 | Guanyu Zhou | 0.1% | — |
| 19 | Logan Sargeant | 0.0% | — |
| 20 | Pierre Gasly | 0.0% | — |

</details>

────────────────────────────────────────────────────────────

## 2024 Chinese GP  ·  Round 5 | 2024-04-21

**Drivers in race:** 20  
**Actuals available:** Yes

### Logistic Regression

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **98%** | ✅ Podium |
| 2 | Sergio Pérez | **94%** | ✅ Podium |
| 3 | Charles Leclerc | **77%** | ❌ No |

**Precision@3:** 67%  (1/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 98.0% | ✅ |
| 2 | Sergio Pérez | 94.3% | ✅ |
| 3 | Charles Leclerc | 76.9% | — |
| 4 | Carlos Sainz | 76.4% | — |
| 5 | Lando Norris | 64.8% | ✅ |
| 6 | Fernando Alonso | 57.2% | — |
| 7 | Oscar Piastri | 46.9% | — |
| 8 | George Russell | 21.2% | — |
| 9 | Nico Hülkenberg | 11.0% | — |
| 10 | Lance Stroll | 10.8% | — |
| 11 | Valtteri Bottas | 5.9% | — |
| 12 | Daniel Ricciardo | 5.4% | — |
| 13 | Esteban Ocon | 3.1% | — |
| 14 | Lewis Hamilton | 3.0% | — |
| 15 | Alexander Albon | 3.0% | — |
| 16 | Pierre Gasly | 2.1% | — |
| 17 | Kevin Magnussen | 1.9% | — |
| 18 | Guanyu Zhou | 1.5% | — |
| 19 | Yuki Tsunoda | 1.4% | — |
| 20 | Logan Sargeant | 0.6% | — |

</details>

### XGBoost

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **98%** | ✅ Podium |
| 2 | Sergio Pérez | **88%** | ✅ Podium |
| 3 | Lando Norris | **84%** | ✅ Podium |

**Precision@3:** 100%  (3/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 98.1% | ✅ |
| 2 | Sergio Pérez | 88.0% | ✅ |
| 3 | Lando Norris | 84.0% | ✅ |
| 4 | Charles Leclerc | 74.7% | — |
| 5 | Fernando Alonso | 59.7% | — |
| 6 | Oscar Piastri | 51.4% | — |
| 7 | Carlos Sainz | 33.5% | — |
| 8 | George Russell | 5.4% | — |
| 9 | Lance Stroll | 3.3% | — |
| 10 | Lewis Hamilton | 3.1% | — |
| 11 | Nico Hülkenberg | 1.4% | — |
| 12 | Valtteri Bottas | 0.5% | — |
| 13 | Alexander Albon | 0.2% | — |
| 14 | Kevin Magnussen | 0.2% | — |
| 15 | Daniel Ricciardo | 0.2% | — |
| 16 | Esteban Ocon | 0.2% | — |
| 17 | Yuki Tsunoda | 0.2% | — |
| 18 | Pierre Gasly | 0.1% | — |
| 19 | Logan Sargeant | 0.0% | — |
| 20 | Guanyu Zhou | 0.0% | — |

</details>

────────────────────────────────────────────────────────────

## 2024 Miami GP  ·  Round 6 | 2024-05-05

**Drivers in race:** 20  
**Actuals available:** Yes

### Logistic Regression

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **98%** | ✅ Podium |
| 2 | Sergio Pérez | **91%** | ❌ No |
| 3 | Charles Leclerc | **84%** | ✅ Podium |

**Precision@3:** 67%  (1/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 98.1% | ✅ |
| 2 | Sergio Pérez | 91.3% | — |
| 3 | Charles Leclerc | 84.4% | ✅ |
| 4 | Carlos Sainz | 82.0% | — |
| 5 | Lando Norris | 62.3% | ✅ |
| 6 | Oscar Piastri | 38.9% | — |
| 7 | George Russell | 22.4% | — |
| 8 | Lewis Hamilton | 19.1% | — |
| 9 | Nico Hülkenberg | 9.1% | — |
| 10 | Lance Stroll | 8.4% | — |
| 11 | Fernando Alonso | 7.6% | — |
| 12 | Yuki Tsunoda | 7.3% | — |
| 13 | Pierre Gasly | 3.7% | — |
| 14 | Esteban Ocon | 3.0% | — |
| 15 | Alexander Albon | 2.5% | — |
| 16 | Valtteri Bottas | 1.5% | — |
| 17 | Kevin Magnussen | 1.3% | — |
| 18 | Logan Sargeant | 1.1% | — |
| 19 | Daniel Ricciardo | 0.8% | — |
| 20 | Guanyu Zhou | 0.7% | — |

</details>

### XGBoost

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **99%** | ✅ Podium |
| 2 | Charles Leclerc | **86%** | ✅ Podium |
| 3 | Carlos Sainz | **82%** | ❌ No |

**Precision@3:** 67%  (1/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 98.6% | ✅ |
| 2 | Charles Leclerc | 85.7% | ✅ |
| 3 | Carlos Sainz | 82.0% | — |
| 4 | Sergio Pérez | 81.7% | — |
| 5 | Lando Norris | 52.7% | ✅ |
| 6 | Oscar Piastri | 43.1% | — |
| 7 | Lewis Hamilton | 25.3% | — |
| 8 | George Russell | 21.0% | — |
| 9 | Fernando Alonso | 6.0% | — |
| 10 | Lance Stroll | 4.4% | — |
| 11 | Nico Hülkenberg | 3.0% | — |
| 12 | Kevin Magnussen | 1.9% | — |
| 13 | Yuki Tsunoda | 1.3% | — |
| 14 | Esteban Ocon | 1.2% | — |
| 15 | Alexander Albon | 1.0% | — |
| 16 | Pierre Gasly | 0.6% | — |
| 17 | Logan Sargeant | 0.6% | — |
| 18 | Valtteri Bottas | 0.4% | — |
| 19 | Daniel Ricciardo | 0.3% | — |
| 20 | Guanyu Zhou | 0.1% | — |

</details>

────────────────────────────────────────────────────────────

## 2024 Emilia Romagna GP  ·  Round 7 | 2024-05-19

**Drivers in race:** 20  
**Actuals available:** Yes

### Logistic Regression

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **98%** | ✅ Podium |
| 2 | Charles Leclerc | **85%** | ✅ Podium |
| 3 | Lando Norris | **83%** | ✅ Podium |

**Precision@3:** 100%  (3/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 98.2% | ✅ |
| 2 | Charles Leclerc | 84.5% | ✅ |
| 3 | Lando Norris | 82.6% | ✅ |
| 4 | Carlos Sainz | 78.2% | — |
| 5 | Sergio Pérez | 67.7% | — |
| 6 | Oscar Piastri | 48.2% | — |
| 7 | George Russell | 29.7% | — |
| 8 | Lewis Hamilton | 21.4% | — |
| 9 | Yuki Tsunoda | 15.3% | — |
| 10 | Daniel Ricciardo | 8.7% | — |
| 11 | Nico Hülkenberg | 8.0% | — |
| 12 | Lance Stroll | 5.6% | — |
| 13 | Esteban Ocon | 4.2% | — |
| 14 | Fernando Alonso | 2.5% | — |
| 15 | Alexander Albon | 2.4% | — |
| 16 | Pierre Gasly | 2.2% | — |
| 17 | Valtteri Bottas | 1.5% | — |
| 18 | Kevin Magnussen | 1.2% | — |
| 19 | Guanyu Zhou | 1.1% | — |
| 20 | Logan Sargeant | 0.8% | — |

</details>

### XGBoost

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **98%** | ✅ Podium |
| 2 | Lando Norris | **91%** | ✅ Podium |
| 3 | Charles Leclerc | **89%** | ✅ Podium |

**Precision@3:** 100%  (3/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 98.0% | ✅ |
| 2 | Lando Norris | 91.5% | ✅ |
| 3 | Charles Leclerc | 89.2% | ✅ |
| 4 | Carlos Sainz | 73.1% | — |
| 5 | Oscar Piastri | 47.7% | — |
| 6 | Sergio Pérez | 25.0% | — |
| 7 | George Russell | 12.1% | — |
| 8 | Lewis Hamilton | 5.3% | — |
| 9 | Yuki Tsunoda | 3.2% | — |
| 10 | Fernando Alonso | 1.1% | — |
| 11 | Lance Stroll | 0.5% | — |
| 12 | Nico Hülkenberg | 0.5% | — |
| 13 | Alexander Albon | 0.4% | — |
| 14 | Daniel Ricciardo | 0.3% | — |
| 15 | Esteban Ocon | 0.3% | — |
| 16 | Pierre Gasly | 0.1% | — |
| 17 | Valtteri Bottas | 0.1% | — |
| 18 | Kevin Magnussen | 0.1% | — |
| 19 | Guanyu Zhou | 0.1% | — |
| 20 | Logan Sargeant | 0.0% | — |

</details>

────────────────────────────────────────────────────────────

## 2024 Monaco GP  ·  Round 8 | 2024-05-26

**Drivers in race:** 20  
**Actuals available:** Yes

### Logistic Regression

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **96%** | ❌ No |
| 2 | Charles Leclerc | **92%** | ✅ Podium |
| 3 | Carlos Sainz | **83%** | ✅ Podium |

**Precision@3:** 67%  (1/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 96.1% | — |
| 2 | Charles Leclerc | 91.8% | ✅ |
| 3 | Carlos Sainz | 83.5% | ✅ |
| 4 | Lando Norris | 81.7% | — |
| 5 | Oscar Piastri | 69.6% | ✅ |
| 6 | Sergio Pérez | 40.4% | — |
| 7 | George Russell | 40.2% | — |
| 8 | Lewis Hamilton | 31.0% | — |
| 9 | Yuki Tsunoda | 15.2% | — |
| 10 | Fernando Alonso | 8.9% | — |
| 11 | Alexander Albon | 8.2% | — |
| 12 | Pierre Gasly | 7.5% | — |
| 13 | Lance Stroll | 6.1% | — |
| 14 | Esteban Ocon | 6.0% | — |
| 15 | Daniel Ricciardo | 5.7% | — |
| 16 | Logan Sargeant | 1.8% | — |
| 17 | Nico Hülkenberg | 1.5% | — |
| 18 | Valtteri Bottas | 1.3% | — |
| 19 | Kevin Magnussen | 1.0% | — |
| 20 | Guanyu Zhou | 0.9% | — |

</details>

### XGBoost

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Charles Leclerc | **93%** | ✅ Podium |
| 2 | Carlos Sainz | **85%** | ✅ Podium |
| 3 | Oscar Piastri | **81%** | ✅ Podium |

**Precision@3:** 100%  (3/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Charles Leclerc | 93.4% | ✅ |
| 2 | Carlos Sainz | 85.3% | ✅ |
| 3 | Oscar Piastri | 81.0% | ✅ |
| 4 | Lando Norris | 63.3% | — |
| 5 | Max Verstappen | 54.8% | — |
| 6 | Sergio Pérez | 23.8% | — |
| 7 | Lewis Hamilton | 13.8% | — |
| 8 | George Russell | 11.8% | — |
| 9 | Yuki Tsunoda | 2.5% | — |
| 10 | Fernando Alonso | 0.8% | — |
| 11 | Daniel Ricciardo | 0.3% | — |
| 12 | Lance Stroll | 0.3% | — |
| 13 | Alexander Albon | 0.3% | — |
| 14 | Pierre Gasly | 0.3% | — |
| 15 | Nico Hülkenberg | 0.2% | — |
| 16 | Esteban Ocon | 0.2% | — |
| 17 | Kevin Magnussen | 0.1% | — |
| 18 | Guanyu Zhou | 0.1% | — |
| 19 | Logan Sargeant | 0.1% | — |
| 20 | Valtteri Bottas | 0.1% | — |

</details>

────────────────────────────────────────────────────────────

## 2024 Canadian GP  ·  Round 9 | 2024-06-09

**Drivers in race:** 20  
**Actuals available:** Yes

### Logistic Regression

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **97%** | ✅ Podium |
| 2 | Lando Norris | **83%** | ✅ Podium |
| 3 | Oscar Piastri | **61%** | ❌ No |

**Precision@3:** 67%  (1/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 97.5% | ✅ |
| 2 | Lando Norris | 82.7% | ✅ |
| 3 | Oscar Piastri | 61.0% | — |
| 4 | George Russell | 59.3% | ✅ |
| 5 | Charles Leclerc | 58.5% | — |
| 6 | Carlos Sainz | 42.9% | — |
| 7 | Fernando Alonso | 32.2% | — |
| 8 | Sergio Pérez | 31.0% | — |
| 9 | Lewis Hamilton | 29.0% | — |
| 10 | Daniel Ricciardo | 19.5% | — |
| 11 | Yuki Tsunoda | 13.8% | — |
| 12 | Lance Stroll | 11.2% | — |
| 13 | Alexander Albon | 6.1% | — |
| 14 | Kevin Magnussen | 3.0% | — |
| 15 | Logan Sargeant | 2.7% | — |
| 16 | Pierre Gasly | 2.3% | — |
| 17 | Nico Hülkenberg | 1.7% | — |
| 18 | Esteban Ocon | 1.2% | — |
| 19 | Valtteri Bottas | 0.1% | — |
| 20 | Guanyu Zhou | 0.1% | — |

</details>

### XGBoost

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **90%** | ✅ Podium |
| 2 | Lando Norris | **88%** | ✅ Podium |
| 3 | Oscar Piastri | **60%** | ❌ No |

**Precision@3:** 67%  (1/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 90.3% | ✅ |
| 2 | Lando Norris | 88.4% | ✅ |
| 3 | Oscar Piastri | 60.2% | — |
| 4 | George Russell | 58.8% | ✅ |
| 5 | Charles Leclerc | 27.3% | — |
| 6 | Sergio Pérez | 25.0% | — |
| 7 | Lewis Hamilton | 16.5% | — |
| 8 | Carlos Sainz | 16.3% | — |
| 9 | Fernando Alonso | 13.2% | — |
| 10 | Daniel Ricciardo | 3.4% | — |
| 11 | Yuki Tsunoda | 1.8% | — |
| 12 | Alexander Albon | 0.8% | — |
| 13 | Valtteri Bottas | 0.3% | — |
| 14 | Logan Sargeant | 0.3% | — |
| 15 | Kevin Magnussen | 0.3% | — |
| 16 | Lance Stroll | 0.3% | — |
| 17 | Esteban Ocon | 0.3% | — |
| 18 | Pierre Gasly | 0.2% | — |
| 19 | Nico Hülkenberg | 0.2% | — |
| 20 | Guanyu Zhou | 0.1% | — |

</details>

────────────────────────────────────────────────────────────

## 2024 Spanish GP  ·  Round 10 | 2024-06-23

**Drivers in race:** 20  
**Actuals available:** Yes

### Logistic Regression

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **98%** | ✅ Podium |
| 2 | Lando Norris | **90%** | ✅ Podium |
| 3 | Charles Leclerc | **82%** | ❌ No |

**Precision@3:** 67%  (1/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 97.9% | ✅ |
| 2 | Lando Norris | 89.7% | ✅ |
| 3 | Charles Leclerc | 81.7% | — |
| 4 | Carlos Sainz | 70.4% | — |
| 5 | Sergio Pérez | 56.3% | — |
| 6 | Lewis Hamilton | 51.9% | ✅ |
| 7 | George Russell | 49.3% | — |
| 8 | Oscar Piastri | 35.8% | — |
| 9 | Fernando Alonso | 17.8% | — |
| 10 | Pierre Gasly | 12.5% | — |
| 11 | Esteban Ocon | 10.2% | — |
| 12 | Lance Stroll | 4.5% | — |
| 13 | Nico Hülkenberg | 4.3% | — |
| 14 | Valtteri Bottas | 3.6% | — |
| 15 | Yuki Tsunoda | 2.1% | — |
| 16 | Kevin Magnussen | 1.9% | — |
| 17 | Guanyu Zhou | 1.7% | — |
| 18 | Daniel Ricciardo | 1.5% | — |
| 19 | Logan Sargeant | 0.7% | — |
| 20 | Alexander Albon | 0.1% | — |

</details>

### XGBoost

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **96%** | ✅ Podium |
| 2 | Lando Norris | **95%** | ✅ Podium |
| 3 | Charles Leclerc | **69%** | ❌ No |

**Precision@3:** 67%  (1/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 96.0% | ✅ |
| 2 | Lando Norris | 95.3% | ✅ |
| 3 | Charles Leclerc | 69.1% | — |
| 4 | Lewis Hamilton | 56.4% | ✅ |
| 5 | Carlos Sainz | 48.7% | — |
| 6 | Oscar Piastri | 33.9% | — |
| 7 | George Russell | 25.2% | — |
| 8 | Sergio Pérez | 17.9% | — |
| 9 | Fernando Alonso | 3.9% | — |
| 10 | Yuki Tsunoda | 1.9% | — |
| 11 | Daniel Ricciardo | 1.4% | — |
| 12 | Pierre Gasly | 0.6% | — |
| 13 | Lance Stroll | 0.5% | — |
| 14 | Alexander Albon | 0.4% | — |
| 15 | Nico Hülkenberg | 0.3% | — |
| 16 | Esteban Ocon | 0.3% | — |
| 17 | Guanyu Zhou | 0.2% | — |
| 18 | Valtteri Bottas | 0.2% | — |
| 19 | Kevin Magnussen | 0.2% | — |
| 20 | Logan Sargeant | 0.2% | — |

</details>

────────────────────────────────────────────────────────────

## 2024 Austrian GP  ·  Round 11 | 2024-06-30

**Drivers in race:** 20  
**Actuals available:** Yes

### Logistic Regression

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **98%** | ❌ No |
| 2 | Lando Norris | **86%** | ❌ No |
| 3 | Charles Leclerc | **72%** | ❌ No |

**Precision@3:** 0%  (0/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 98.2% | — |
| 2 | Lando Norris | 86.3% | — |
| 3 | Charles Leclerc | 72.0% | — |
| 4 | Carlos Sainz | 71.9% | ✅ |
| 5 | Sergio Pérez | 63.6% | — |
| 6 | George Russell | 51.3% | ✅ |
| 7 | Lewis Hamilton | 41.0% | — |
| 8 | Oscar Piastri | 39.8% | ✅ |
| 9 | Nico Hülkenberg | 7.4% | — |
| 10 | Esteban Ocon | 5.8% | — |
| 11 | Fernando Alonso | 5.2% | — |
| 12 | Daniel Ricciardo | 4.8% | — |
| 13 | Kevin Magnussen | 3.6% | — |
| 14 | Pierre Gasly | 3.2% | — |
| 15 | Yuki Tsunoda | 3.1% | — |
| 16 | Lance Stroll | 1.8% | — |
| 17 | Alexander Albon | 1.2% | — |
| 18 | Valtteri Bottas | 0.8% | — |
| 19 | Logan Sargeant | 0.6% | — |
| 20 | Guanyu Zhou | 0.5% | — |

</details>

### XGBoost

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **95%** | ❌ No |
| 2 | Lando Norris | **88%** | ❌ No |
| 3 | Carlos Sainz | **76%** | ✅ Podium |

**Precision@3:** 33%  (0/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 95.4% | — |
| 2 | Lando Norris | 88.0% | — |
| 3 | Carlos Sainz | 75.7% | ✅ |
| 4 | Charles Leclerc | 75.7% | — |
| 5 | George Russell | 67.0% | ✅ |
| 6 | Lewis Hamilton | 47.3% | — |
| 7 | Oscar Piastri | 30.5% | ✅ |
| 8 | Sergio Pérez | 29.9% | — |
| 9 | Fernando Alonso | 1.1% | — |
| 10 | Daniel Ricciardo | 0.7% | — |
| 11 | Yuki Tsunoda | 0.6% | — |
| 12 | Nico Hülkenberg | 0.2% | — |
| 13 | Alexander Albon | 0.2% | — |
| 14 | Pierre Gasly | 0.2% | — |
| 15 | Lance Stroll | 0.1% | — |
| 16 | Esteban Ocon | 0.1% | — |
| 17 | Kevin Magnussen | 0.1% | — |
| 18 | Valtteri Bottas | 0.1% | — |
| 19 | Logan Sargeant | 0.1% | — |
| 20 | Guanyu Zhou | 0.0% | — |

</details>

────────────────────────────────────────────────────────────

## 2024 British GP  ·  Round 12 | 2024-07-07

**Drivers in race:** 20  
**Actuals available:** Yes

### Logistic Regression

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **97%** | ✅ Podium |
| 2 | Lando Norris | **86%** | ✅ Podium |
| 3 | George Russell | **75%** | ❌ No |

**Precision@3:** 67%  (1/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 96.9% | ✅ |
| 2 | Lando Norris | 85.6% | ✅ |
| 3 | George Russell | 74.6% | — |
| 4 | Lewis Hamilton | 66.7% | ✅ |
| 5 | Carlos Sainz | 65.5% | — |
| 6 | Oscar Piastri | 59.9% | — |
| 7 | Charles Leclerc | 49.5% | — |
| 8 | Nico Hülkenberg | 18.0% | — |
| 9 | Fernando Alonso | 16.3% | — |
| 10 | Lance Stroll | 13.3% | — |
| 11 | Alexander Albon | 6.7% | — |
| 12 | Yuki Tsunoda | 4.5% | — |
| 13 | Logan Sargeant | 3.0% | — |
| 14 | Daniel Ricciardo | 2.5% | — |
| 15 | Guanyu Zhou | 2.0% | — |
| 16 | Kevin Magnussen | 0.9% | — |
| 17 | Valtteri Bottas | 0.8% | — |
| 18 | Sergio Pérez | 0.6% | — |
| 19 | Esteban Ocon | 0.6% | — |
| 20 | Pierre Gasly | 0.3% | — |

</details>

### XGBoost

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Lando Norris | **86%** | ✅ Podium |
| 2 | Max Verstappen | **86%** | ✅ Podium |
| 3 | Lewis Hamilton | **86%** | ✅ Podium |

**Precision@3:** 100%  (3/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Lando Norris | 86.5% | ✅ |
| 2 | Max Verstappen | 86.3% | ✅ |
| 3 | Lewis Hamilton | 86.3% | ✅ |
| 4 | George Russell | 85.6% | — |
| 5 | Oscar Piastri | 45.3% | — |
| 6 | Charles Leclerc | 43.1% | — |
| 7 | Carlos Sainz | 31.6% | — |
| 8 | Sergio Pérez | 15.0% | — |
| 9 | Nico Hülkenberg | 4.6% | — |
| 10 | Fernando Alonso | 3.9% | — |
| 11 | Lance Stroll | 2.0% | — |
| 12 | Yuki Tsunoda | 0.8% | — |
| 13 | Alexander Albon | 0.3% | — |
| 14 | Logan Sargeant | 0.1% | — |
| 15 | Esteban Ocon | 0.1% | — |
| 16 | Daniel Ricciardo | 0.1% | — |
| 17 | Pierre Gasly | 0.1% | — |
| 18 | Kevin Magnussen | 0.1% | — |
| 19 | Valtteri Bottas | 0.0% | — |
| 20 | Guanyu Zhou | 0.0% | — |

</details>

────────────────────────────────────────────────────────────

## 2024 Hungarian GP  ·  Round 13 | 2024-07-21

**Drivers in race:** 20  
**Actuals available:** Yes

### Logistic Regression

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **98%** | ❌ No |
| 2 | Lando Norris | **91%** | ✅ Podium |
| 3 | Carlos Sainz | **76%** | ❌ No |

**Precision@3:** 33%  (0/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 97.5% | — |
| 2 | Lando Norris | 90.6% | ✅ |
| 3 | Carlos Sainz | 76.2% | — |
| 4 | Oscar Piastri | 74.3% | ✅ |
| 5 | Charles Leclerc | 70.5% | — |
| 6 | Lewis Hamilton | 56.5% | ✅ |
| 7 | Fernando Alonso | 26.2% | — |
| 8 | Sergio Pérez | 19.5% | — |
| 9 | Lance Stroll | 13.1% | — |
| 10 | Daniel Ricciardo | 8.5% | — |
| 11 | Yuki Tsunoda | 8.1% | — |
| 12 | George Russell | 7.1% | — |
| 13 | Nico Hülkenberg | 6.9% | — |
| 14 | Valtteri Bottas | 3.2% | — |
| 15 | Alexander Albon | 2.9% | — |
| 16 | Kevin Magnussen | 2.4% | — |
| 17 | Logan Sargeant | 2.0% | — |
| 18 | Esteban Ocon | 0.9% | — |
| 19 | Guanyu Zhou | 0.7% | — |
| 20 | Pierre Gasly | 0.1% | — |

</details>

### XGBoost

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **95%** | ❌ No |
| 2 | Oscar Piastri | **92%** | ✅ Podium |
| 3 | Lando Norris | **89%** | ✅ Podium |

**Precision@3:** 67%  (1/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 95.3% | — |
| 2 | Oscar Piastri | 91.9% | ✅ |
| 3 | Lando Norris | 89.2% | ✅ |
| 4 | Carlos Sainz | 72.4% | — |
| 5 | Lewis Hamilton | 44.8% | ✅ |
| 6 | Charles Leclerc | 43.1% | — |
| 7 | Sergio Pérez | 10.6% | — |
| 8 | Fernando Alonso | 8.0% | — |
| 9 | George Russell | 1.9% | — |
| 10 | Lance Stroll | 1.5% | — |
| 11 | Yuki Tsunoda | 1.2% | — |
| 12 | Alexander Albon | 0.6% | — |
| 13 | Nico Hülkenberg | 0.6% | — |
| 14 | Daniel Ricciardo | 0.5% | — |
| 15 | Kevin Magnussen | 0.4% | — |
| 16 | Valtteri Bottas | 0.2% | — |
| 17 | Logan Sargeant | 0.2% | — |
| 18 | Pierre Gasly | 0.1% | — |
| 19 | Esteban Ocon | 0.1% | — |
| 20 | Guanyu Zhou | 0.0% | — |

</details>

────────────────────────────────────────────────────────────

## 2024 Belgian GP  ·  Round 14 | 2024-07-28

**Drivers in race:** 20  
**Actuals available:** Yes

### Logistic Regression

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **89%** | ❌ No |
| 2 | Charles Leclerc | **89%** | ✅ Podium |
| 3 | Lando Norris | **87%** | ❌ No |

**Precision@3:** 33%  (0/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 89.0% | — |
| 2 | Charles Leclerc | 88.6% | ✅ |
| 3 | Lando Norris | 86.8% | — |
| 4 | Sergio Pérez | 85.6% | — |
| 5 | Lewis Hamilton | 72.5% | ✅ |
| 6 | Oscar Piastri | 68.0% | ✅ |
| 7 | Carlos Sainz | 64.2% | — |
| 8 | George Russell | 51.4% | — |
| 9 | Fernando Alonso | 24.3% | — |
| 10 | Esteban Ocon | 8.3% | — |
| 11 | Alexander Albon | 6.0% | — |
| 12 | Pierre Gasly | 4.7% | — |
| 13 | Daniel Ricciardo | 4.3% | — |
| 14 | Lance Stroll | 3.2% | — |
| 15 | Valtteri Bottas | 2.3% | — |
| 16 | Nico Hülkenberg | 2.3% | — |
| 17 | Kevin Magnussen | 1.4% | — |
| 18 | Yuki Tsunoda | 1.0% | — |
| 19 | Logan Sargeant | 0.7% | — |
| 20 | Guanyu Zhou | 0.5% | — |

</details>

### XGBoost

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Charles Leclerc | **85%** | ✅ Podium |
| 2 | Max Verstappen | **84%** | ❌ No |
| 3 | Sergio Pérez | **78%** | ❌ No |

**Precision@3:** 33%  (0/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Charles Leclerc | 85.2% | ✅ |
| 2 | Max Verstappen | 84.4% | — |
| 3 | Sergio Pérez | 77.6% | — |
| 4 | Lewis Hamilton | 70.0% | ✅ |
| 5 | Lando Norris | 64.1% | — |
| 6 | Oscar Piastri | 40.8% | ✅ |
| 7 | Carlos Sainz | 28.2% | — |
| 8 | Fernando Alonso | 9.3% | — |
| 9 | George Russell | 7.0% | — |
| 10 | Alexander Albon | 0.4% | — |
| 11 | Esteban Ocon | 0.4% | — |
| 12 | Pierre Gasly | 0.2% | — |
| 13 | Daniel Ricciardo | 0.1% | — |
| 14 | Nico Hülkenberg | 0.1% | — |
| 15 | Lance Stroll | 0.1% | — |
| 16 | Valtteri Bottas | 0.1% | — |
| 17 | Yuki Tsunoda | 0.1% | — |
| 18 | Kevin Magnussen | 0.1% | — |
| 19 | Logan Sargeant | 0.0% | — |
| 20 | Guanyu Zhou | 0.0% | — |

</details>

────────────────────────────────────────────────────────────

## 2024 Dutch GP  ·  Round 15 | 2024-08-25

**Drivers in race:** 20  
**Actuals available:** Yes

### Logistic Regression

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **97%** | ✅ Podium |
| 2 | Lando Norris | **91%** | ✅ Podium |
| 3 | Oscar Piastri | **75%** | ❌ No |

**Precision@3:** 67%  (1/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 97.4% | ✅ |
| 2 | Lando Norris | 91.2% | ✅ |
| 3 | Oscar Piastri | 74.6% | — |
| 4 | Sergio Pérez | 69.5% | — |
| 5 | Charles Leclerc | 69.4% | ✅ |
| 6 | George Russell | 56.6% | — |
| 7 | Carlos Sainz | 41.2% | — |
| 8 | Fernando Alonso | 24.0% | — |
| 9 | Lewis Hamilton | 19.9% | — |
| 10 | Lance Stroll | 11.5% | — |
| 11 | Pierre Gasly | 6.9% | — |
| 12 | Yuki Tsunoda | 5.7% | — |
| 13 | Nico Hülkenberg | 4.5% | — |
| 14 | Daniel Ricciardo | 3.0% | — |
| 15 | Esteban Ocon | 1.8% | — |
| 16 | Valtteri Bottas | 1.1% | — |
| 17 | Logan Sargeant | 0.8% | — |
| 18 | Alexander Albon | 0.8% | — |
| 19 | Guanyu Zhou | 0.7% | — |
| 20 | Kevin Magnussen | 0.1% | — |

</details>

### XGBoost

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **89%** | ✅ Podium |
| 2 | Oscar Piastri | **89%** | ❌ No |
| 3 | Lando Norris | **85%** | ✅ Podium |

**Precision@3:** 67%  (1/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 89.1% | ✅ |
| 2 | Oscar Piastri | 88.6% | — |
| 3 | Lando Norris | 85.2% | ✅ |
| 4 | George Russell | 60.6% | — |
| 5 | Sergio Pérez | 59.9% | — |
| 6 | Charles Leclerc | 51.7% | ✅ |
| 7 | Lewis Hamilton | 17.6% | — |
| 8 | Carlos Sainz | 9.8% | — |
| 9 | Fernando Alonso | 7.3% | — |
| 10 | Lance Stroll | 1.9% | — |
| 11 | Yuki Tsunoda | 0.8% | — |
| 12 | Pierre Gasly | 0.6% | — |
| 13 | Guanyu Zhou | 0.3% | — |
| 14 | Esteban Ocon | 0.2% | — |
| 15 | Alexander Albon | 0.2% | — |
| 16 | Valtteri Bottas | 0.1% | — |
| 17 | Nico Hülkenberg | 0.1% | — |
| 18 | Kevin Magnussen | 0.1% | — |
| 19 | Logan Sargeant | 0.1% | — |
| 20 | Daniel Ricciardo | 0.1% | — |

</details>

────────────────────────────────────────────────────────────

## 2024 Italian GP  ·  Round 16 | 2024-09-01

**Drivers in race:** 20  
**Actuals available:** Yes

### Logistic Regression

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **94%** | ❌ No |
| 2 | Lando Norris | **93%** | ✅ Podium |
| 3 | Charles Leclerc | **82%** | ✅ Podium |

**Precision@3:** 67%  (1/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 94.1% | — |
| 2 | Lando Norris | 93.3% | ✅ |
| 3 | Charles Leclerc | 82.1% | ✅ |
| 4 | Oscar Piastri | 81.5% | ✅ |
| 5 | Carlos Sainz | 71.5% | — |
| 6 | George Russell | 64.9% | — |
| 7 | Lewis Hamilton | 61.2% | — |
| 8 | Sergio Pérez | 57.2% | — |
| 9 | Fernando Alonso | 12.9% | — |
| 10 | Nico Hülkenberg | 7.5% | — |
| 11 | Alexander Albon | 6.3% | — |
| 12 | Daniel Ricciardo | 4.4% | — |
| 13 | Kevin Magnussen | 3.2% | — |
| 14 | Pierre Gasly | 2.8% | — |
| 15 | Esteban Ocon | 2.2% | — |
| 16 | Yuki Tsunoda | 2.1% | — |
| 17 | Lance Stroll | 2.0% | — |
| 18 | Franco Colapinto | 1.2% | — |
| 19 | Valtteri Bottas | 0.7% | — |
| 20 | Guanyu Zhou | 0.5% | — |

</details>

### XGBoost

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Lando Norris | **86%** | ✅ Podium |
| 2 | Oscar Piastri | **85%** | ✅ Podium |
| 3 | George Russell | **75%** | ❌ No |

**Precision@3:** 67%  (1/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Lando Norris | 85.6% | ✅ |
| 2 | Oscar Piastri | 84.6% | ✅ |
| 3 | George Russell | 75.4% | — |
| 4 | Charles Leclerc | 72.9% | ✅ |
| 5 | Max Verstappen | 65.9% | — |
| 6 | Lewis Hamilton | 63.8% | — |
| 7 | Carlos Sainz | 34.5% | — |
| 8 | Sergio Pérez | 25.0% | — |
| 9 | Fernando Alonso | 4.4% | — |
| 10 | Nico Hülkenberg | 0.7% | — |
| 11 | Lance Stroll | 0.6% | — |
| 12 | Alexander Albon | 0.5% | — |
| 13 | Kevin Magnussen | 0.4% | — |
| 14 | Esteban Ocon | 0.3% | — |
| 15 | Yuki Tsunoda | 0.2% | — |
| 16 | Daniel Ricciardo | 0.2% | — |
| 17 | Pierre Gasly | 0.2% | — |
| 18 | Franco Colapinto | 0.2% | — |
| 19 | Valtteri Bottas | 0.1% | — |
| 20 | Guanyu Zhou | 0.0% | — |

</details>

────────────────────────────────────────────────────────────

## 2024 Azerbaijan GP  ·  Round 17 | 2024-09-15

**Drivers in race:** 20  
**Actuals available:** Yes

### Logistic Regression

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **94%** | ❌ No |
| 2 | Charles Leclerc | **91%** | ✅ Podium |
| 3 | Oscar Piastri | **82%** | ✅ Podium |

**Precision@3:** 67%  (1/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 94.3% | — |
| 2 | Charles Leclerc | 90.6% | ✅ |
| 3 | Oscar Piastri | 82.2% | ✅ |
| 4 | Carlos Sainz | 78.0% | — |
| 5 | Sergio Pérez | 73.3% | — |
| 6 | George Russell | 51.7% | ✅ |
| 7 | Lando Norris | 37.7% | — |
| 8 | Fernando Alonso | 23.5% | — |
| 9 | Alexander Albon | 5.8% | — |
| 10 | Yuki Tsunoda | 5.3% | — |
| 11 | Oliver Bearman | 5.2% | — |
| 12 | Franco Colapinto | 5.2% | — |
| 13 | Nico Hülkenberg | 4.3% | — |
| 14 | Lance Stroll | 3.8% | — |
| 15 | Daniel Ricciardo | 2.4% | — |
| 16 | Lewis Hamilton | 1.3% | — |
| 17 | Pierre Gasly | 1.1% | — |
| 18 | Valtteri Bottas | 1.0% | — |
| 19 | Guanyu Zhou | 0.7% | — |
| 20 | Esteban Ocon | 0.1% | — |

</details>

### XGBoost

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **79%** | ❌ No |
| 2 | Charles Leclerc | **79%** | ✅ Podium |
| 3 | Oscar Piastri | **73%** | ✅ Podium |

**Precision@3:** 67%  (1/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 79.3% | — |
| 2 | Charles Leclerc | 78.6% | ✅ |
| 3 | Oscar Piastri | 72.7% | ✅ |
| 4 | Carlos Sainz | 69.7% | — |
| 5 | Sergio Pérez | 69.4% | — |
| 6 | Lando Norris | 28.3% | — |
| 7 | George Russell | 20.3% | ✅ |
| 8 | Fernando Alonso | 17.4% | — |
| 9 | Lewis Hamilton | 17.4% | — |
| 10 | Franco Colapinto | 6.4% | — |
| 11 | Alexander Albon | 1.2% | — |
| 12 | Oliver Bearman | 0.6% | — |
| 13 | Yuki Tsunoda | 0.5% | — |
| 14 | Nico Hülkenberg | 0.2% | — |
| 15 | Lance Stroll | 0.2% | — |
| 16 | Pierre Gasly | 0.1% | — |
| 17 | Esteban Ocon | 0.1% | — |
| 18 | Valtteri Bottas | 0.1% | — |
| 19 | Guanyu Zhou | 0.1% | — |
| 20 | Daniel Ricciardo | 0.1% | — |

</details>

────────────────────────────────────────────────────────────

## 2024 Singapore GP  ·  Round 18 | 2024-09-22

**Drivers in race:** 20  
**Actuals available:** Yes

### Logistic Regression

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **98%** | ✅ Podium |
| 2 | Lando Norris | **94%** | ✅ Podium |
| 3 | Oscar Piastri | **77%** | ✅ Podium |

**Precision@3:** 100%  (3/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 97.6% | ✅ |
| 2 | Lando Norris | 94.2% | ✅ |
| 3 | Oscar Piastri | 77.1% | ✅ |
| 4 | Lewis Hamilton | 74.6% | — |
| 5 | Charles Leclerc | 68.4% | — |
| 6 | George Russell | 62.8% | — |
| 7 | Carlos Sainz | 45.2% | — |
| 8 | Sergio Pérez | 28.2% | — |
| 9 | Fernando Alonso | 26.5% | — |
| 10 | Nico Hülkenberg | 16.4% | — |
| 11 | Yuki Tsunoda | 11.2% | — |
| 12 | Alexander Albon | 4.8% | — |
| 13 | Franco Colapinto | 3.1% | — |
| 14 | Kevin Magnussen | 2.8% | — |
| 15 | Esteban Ocon | 2.2% | — |
| 16 | Lance Stroll | 1.9% | — |
| 17 | Daniel Ricciardo | 1.8% | — |
| 18 | Pierre Gasly | 1.2% | — |
| 19 | Valtteri Bottas | 0.6% | — |
| 20 | Guanyu Zhou | 0.5% | — |

</details>

### XGBoost

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **88%** | ✅ Podium |
| 2 | Lando Norris | **85%** | ✅ Podium |
| 3 | Lewis Hamilton | **84%** | ❌ No |

**Precision@3:** 67%  (1/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 87.7% | ✅ |
| 2 | Lando Norris | 84.7% | ✅ |
| 3 | Lewis Hamilton | 84.0% | — |
| 4 | Charles Leclerc | 48.8% | — |
| 5 | Oscar Piastri | 46.7% | ✅ |
| 6 | George Russell | 37.6% | — |
| 7 | Carlos Sainz | 31.1% | — |
| 8 | Sergio Pérez | 14.0% | — |
| 9 | Fernando Alonso | 5.7% | — |
| 10 | Nico Hülkenberg | 1.2% | — |
| 11 | Yuki Tsunoda | 0.9% | — |
| 12 | Franco Colapinto | 0.5% | — |
| 13 | Alexander Albon | 0.5% | — |
| 14 | Esteban Ocon | 0.3% | — |
| 15 | Lance Stroll | 0.3% | — |
| 16 | Kevin Magnussen | 0.1% | — |
| 17 | Daniel Ricciardo | 0.1% | — |
| 18 | Pierre Gasly | 0.1% | — |
| 19 | Valtteri Bottas | 0.0% | — |
| 20 | Guanyu Zhou | 0.0% | — |

</details>

────────────────────────────────────────────────────────────

## 2024 United States GP  ·  Round 19 | 2024-10-20

**Drivers in race:** 20  
**Actuals available:** Yes

### Logistic Regression

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **98%** | ✅ Podium |
| 2 | Lando Norris | **94%** | ❌ No |
| 3 | Charles Leclerc | **84%** | ✅ Podium |

**Precision@3:** 67%  (1/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 97.6% | ✅ |
| 2 | Lando Norris | 94.4% | — |
| 3 | Charles Leclerc | 83.5% | ✅ |
| 4 | Oscar Piastri | 75.6% | — |
| 5 | Carlos Sainz | 75.1% | ✅ |
| 6 | Sergio Pérez | 43.2% | — |
| 7 | Fernando Alonso | 23.4% | — |
| 8 | Pierre Gasly | 12.0% | — |
| 9 | Lewis Hamilton | 10.5% | — |
| 10 | Kevin Magnussen | 7.7% | — |
| 11 | Yuki Tsunoda | 6.3% | — |
| 12 | Nico Hülkenberg | 5.3% | — |
| 13 | George Russell | 5.0% | — |
| 14 | Lance Stroll | 3.6% | — |
| 15 | Esteban Ocon | 3.4% | — |
| 16 | Alexander Albon | 2.1% | — |
| 17 | Franco Colapinto | 1.4% | — |
| 18 | Liam Lawson | 1.3% | — |
| 19 | Valtteri Bottas | 1.0% | — |
| 20 | Guanyu Zhou | 0.6% | — |

</details>

### XGBoost

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **94%** | ✅ Podium |
| 2 | Lando Norris | **86%** | ❌ No |
| 3 | Carlos Sainz | **81%** | ✅ Podium |

**Precision@3:** 67%  (1/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 94.2% | ✅ |
| 2 | Lando Norris | 86.3% | — |
| 3 | Carlos Sainz | 80.9% | ✅ |
| 4 | Charles Leclerc | 79.4% | ✅ |
| 5 | Oscar Piastri | 57.4% | — |
| 6 | Lewis Hamilton | 13.3% | — |
| 7 | George Russell | 8.9% | — |
| 8 | Sergio Pérez | 6.7% | — |
| 9 | Fernando Alonso | 5.5% | — |
| 10 | Pierre Gasly | 0.9% | — |
| 11 | Lance Stroll | 0.3% | — |
| 12 | Yuki Tsunoda | 0.3% | — |
| 13 | Liam Lawson | 0.3% | — |
| 14 | Esteban Ocon | 0.2% | — |
| 15 | Nico Hülkenberg | 0.2% | — |
| 16 | Franco Colapinto | 0.2% | — |
| 17 | Alexander Albon | 0.1% | — |
| 18 | Kevin Magnussen | 0.1% | — |
| 19 | Valtteri Bottas | 0.0% | — |
| 20 | Guanyu Zhou | 0.0% | — |

</details>

────────────────────────────────────────────────────────────

## 2024 Mexico City GP  ·  Round 20 | 2024-10-27

**Drivers in race:** 20  
**Actuals available:** Yes

### Logistic Regression

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **98%** | ❌ No |
| 2 | Lando Norris | **92%** | ✅ Podium |
| 3 | Charles Leclerc | **86%** | ✅ Podium |

**Precision@3:** 67%  (1/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 97.8% | — |
| 2 | Lando Norris | 91.7% | ✅ |
| 3 | Charles Leclerc | 86.4% | ✅ |
| 4 | Carlos Sainz | 84.9% | ✅ |
| 5 | Lewis Hamilton | 55.8% | — |
| 6 | George Russell | 55.8% | — |
| 7 | Oscar Piastri | 18.6% | — |
| 8 | Kevin Magnussen | 9.8% | — |
| 9 | Sergio Pérez | 9.5% | — |
| 10 | Pierre Gasly | 8.1% | — |
| 11 | Fernando Alonso | 7.9% | — |
| 12 | Nico Hülkenberg | 6.8% | — |
| 13 | Alexander Albon | 6.3% | — |
| 14 | Yuki Tsunoda | 5.3% | — |
| 15 | Liam Lawson | 3.4% | — |
| 16 | Lance Stroll | 3.0% | — |
| 17 | Valtteri Bottas | 1.3% | — |
| 18 | Franco Colapinto | 1.1% | — |
| 19 | Guanyu Zhou | 0.5% | — |
| 20 | Esteban Ocon | 0.1% | — |

</details>

### XGBoost

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Carlos Sainz | **89%** | ✅ Podium |
| 2 | Max Verstappen | **83%** | ❌ No |
| 3 | Lando Norris | **69%** | ✅ Podium |

**Precision@3:** 67%  (1/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Carlos Sainz | 88.6% | ✅ |
| 2 | Max Verstappen | 82.8% | — |
| 3 | Lando Norris | 69.2% | ✅ |
| 4 | Charles Leclerc | 69.1% | ✅ |
| 5 | George Russell | 31.1% | — |
| 6 | Lewis Hamilton | 30.4% | — |
| 7 | Oscar Piastri | 12.5% | — |
| 8 | Sergio Pérez | 10.4% | — |
| 9 | Fernando Alonso | 1.7% | — |
| 10 | Alexander Albon | 1.0% | — |
| 11 | Lance Stroll | 0.6% | — |
| 12 | Pierre Gasly | 0.5% | — |
| 13 | Liam Lawson | 0.4% | — |
| 14 | Yuki Tsunoda | 0.3% | — |
| 15 | Franco Colapinto | 0.2% | — |
| 16 | Nico Hülkenberg | 0.2% | — |
| 17 | Kevin Magnussen | 0.2% | — |
| 18 | Esteban Ocon | 0.1% | — |
| 19 | Valtteri Bottas | 0.1% | — |
| 20 | Guanyu Zhou | 0.0% | — |

</details>

────────────────────────────────────────────────────────────

## 2024 São Paulo GP  ·  Round 21 | 2024-11-03

**Drivers in race:** 20  
**Actuals available:** Yes

### Logistic Regression

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Lando Norris | **96%** | ❌ No |
| 2 | Charles Leclerc | **84%** | ❌ No |
| 3 | George Russell | **75%** | ❌ No |

**Precision@3:** 0%  (0/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Lando Norris | 96.0% | — |
| 2 | Charles Leclerc | 84.3% | — |
| 3 | George Russell | 75.5% | — |
| 4 | Oscar Piastri | 64.6% | — |
| 5 | Max Verstappen | 58.9% | ✅ |
| 6 | Yuki Tsunoda | 27.4% | — |
| 7 | Sergio Pérez | 22.3% | — |
| 8 | Esteban Ocon | 19.1% | ✅ |
| 9 | Fernando Alonso | 18.7% | — |
| 10 | Liam Lawson | 15.9% | — |
| 11 | Lewis Hamilton | 12.0% | — |
| 12 | Alexander Albon | 11.1% | — |
| 13 | Lance Stroll | 6.6% | — |
| 14 | Valtteri Bottas | 3.1% | — |
| 15 | Pierre Gasly | 2.1% | ✅ |
| 16 | Carlos Sainz | 1.2% | — |
| 17 | Oliver Bearman | 1.1% | — |
| 18 | Nico Hülkenberg | 0.9% | — |
| 19 | Franco Colapinto | 0.7% | — |
| 20 | Guanyu Zhou | 0.3% | — |

</details>

### XGBoost

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Lando Norris | **85%** | ❌ No |
| 2 | George Russell | **68%** | ❌ No |
| 3 | Charles Leclerc | **56%** | ❌ No |

**Precision@3:** 0%  (0/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Lando Norris | 85.0% | — |
| 2 | George Russell | 68.2% | — |
| 3 | Charles Leclerc | 56.0% | — |
| 4 | Lewis Hamilton | 38.0% | — |
| 5 | Max Verstappen | 35.5% | ✅ |
| 6 | Carlos Sainz | 17.7% | — |
| 7 | Oscar Piastri | 10.4% | — |
| 8 | Sergio Pérez | 6.7% | — |
| 9 | Fernando Alonso | 3.4% | — |
| 10 | Alexander Albon | 3.3% | — |
| 11 | Yuki Tsunoda | 2.6% | — |
| 12 | Liam Lawson | 1.8% | — |
| 13 | Esteban Ocon | 1.0% | ✅ |
| 14 | Lance Stroll | 0.2% | — |
| 15 | Franco Colapinto | 0.2% | — |
| 16 | Oliver Bearman | 0.2% | — |
| 17 | Nico Hülkenberg | 0.1% | — |
| 18 | Pierre Gasly | 0.1% | ✅ |
| 19 | Valtteri Bottas | 0.1% | — |
| 20 | Guanyu Zhou | 0.0% | — |

</details>

────────────────────────────────────────────────────────────

## 2024 Las Vegas GP  ·  Round 22 | 2024-11-23

**Drivers in race:** 20  
**Actuals available:** Yes

### Logistic Regression

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **96%** | ❌ No |
| 2 | Charles Leclerc | **87%** | ❌ No |
| 3 | Lando Norris | **85%** | ❌ No |

**Precision@3:** 0%  (0/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 96.0% | — |
| 2 | Charles Leclerc | 86.6% | — |
| 3 | Lando Norris | 84.9% | — |
| 4 | Carlos Sainz | 82.6% | ✅ |
| 5 | George Russell | 75.0% | ✅ |
| 6 | Oscar Piastri | 57.8% | — |
| 7 | Lewis Hamilton | 34.4% | ✅ |
| 8 | Pierre Gasly | 23.0% | — |
| 9 | Sergio Pérez | 13.1% | — |
| 10 | Yuki Tsunoda | 11.4% | — |
| 11 | Nico Hülkenberg | 7.9% | — |
| 12 | Esteban Ocon | 4.9% | — |
| 13 | Fernando Alonso | 3.6% | — |
| 14 | Kevin Magnussen | 3.5% | — |
| 15 | Liam Lawson | 2.1% | — |
| 16 | Guanyu Zhou | 1.7% | — |
| 17 | Lance Stroll | 1.1% | — |
| 18 | Alexander Albon | 1.0% | — |
| 19 | Valtteri Bottas | 0.5% | — |
| 20 | Franco Colapinto | 0.1% | — |

</details>

### XGBoost

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Carlos Sainz | **86%** | ✅ Podium |
| 2 | George Russell | **76%** | ✅ Podium |
| 3 | Charles Leclerc | **75%** | ❌ No |

**Precision@3:** 67%  (1/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Carlos Sainz | 86.5% | ✅ |
| 2 | George Russell | 76.5% | ✅ |
| 3 | Charles Leclerc | 75.3% | — |
| 4 | Max Verstappen | 73.7% | — |
| 5 | Lando Norris | 44.1% | — |
| 6 | Lewis Hamilton | 21.8% | ✅ |
| 7 | Oscar Piastri | 16.6% | — |
| 8 | Sergio Pérez | 8.2% | — |
| 9 | Yuki Tsunoda | 4.9% | — |
| 10 | Pierre Gasly | 3.6% | — |
| 11 | Fernando Alonso | 1.2% | — |
| 12 | Esteban Ocon | 0.9% | — |
| 13 | Nico Hülkenberg | 0.7% | — |
| 14 | Kevin Magnussen | 0.4% | — |
| 15 | Guanyu Zhou | 0.3% | — |
| 16 | Franco Colapinto | 0.2% | — |
| 17 | Lance Stroll | 0.2% | — |
| 18 | Liam Lawson | 0.1% | — |
| 19 | Alexander Albon | 0.1% | — |
| 20 | Valtteri Bottas | 0.0% | — |

</details>

────────────────────────────────────────────────────────────

## 2024 Qatar GP  ·  Round 23 | 2024-12-01

**Drivers in race:** 20  
**Actuals available:** Yes

### Logistic Regression

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **98%** | ✅ Podium |
| 2 | Lando Norris | **91%** | ❌ No |
| 3 | Charles Leclerc | **84%** | ✅ Podium |

**Precision@3:** 67%  (1/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 97.8% | ✅ |
| 2 | Lando Norris | 91.1% | — |
| 3 | Charles Leclerc | 83.9% | ✅ |
| 4 | George Russell | 77.7% | — |
| 5 | Oscar Piastri | 75.1% | ✅ |
| 6 | Carlos Sainz | 62.3% | — |
| 7 | Lewis Hamilton | 56.3% | — |
| 8 | Sergio Pérez | 34.1% | — |
| 9 | Fernando Alonso | 17.3% | — |
| 10 | Kevin Magnussen | 5.0% | — |
| 11 | Pierre Gasly | 4.7% | — |
| 12 | Yuki Tsunoda | 2.6% | — |
| 13 | Guanyu Zhou | 2.1% | — |
| 14 | Lance Stroll | 2.0% | — |
| 15 | Valtteri Bottas | 1.8% | — |
| 16 | Alexander Albon | 1.2% | — |
| 17 | Nico Hülkenberg | 1.1% | — |
| 18 | Liam Lawson | 1.0% | — |
| 19 | Esteban Ocon | 0.6% | — |
| 20 | Franco Colapinto | 0.5% | — |

</details>

### XGBoost

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | George Russell | **85%** | ❌ No |
| 2 | Max Verstappen | **84%** | ✅ Podium |
| 3 | Lando Norris | **75%** | ❌ No |

**Precision@3:** 33%  (0/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | George Russell | 85.2% | — |
| 2 | Max Verstappen | 84.4% | ✅ |
| 3 | Lando Norris | 75.1% | — |
| 4 | Charles Leclerc | 63.7% | ✅ |
| 5 | Lewis Hamilton | 44.4% | — |
| 6 | Oscar Piastri | 41.9% | ✅ |
| 7 | Carlos Sainz | 36.0% | — |
| 8 | Fernando Alonso | 9.3% | — |
| 9 | Sergio Pérez | 7.7% | — |
| 10 | Yuki Tsunoda | 1.0% | — |
| 11 | Lance Stroll | 0.9% | — |
| 12 | Valtteri Bottas | 0.6% | — |
| 13 | Kevin Magnussen | 0.4% | — |
| 14 | Pierre Gasly | 0.3% | — |
| 15 | Guanyu Zhou | 0.3% | — |
| 16 | Alexander Albon | 0.3% | — |
| 17 | Nico Hülkenberg | 0.1% | — |
| 18 | Liam Lawson | 0.1% | — |
| 19 | Esteban Ocon | 0.1% | — |
| 20 | Franco Colapinto | 0.1% | — |

</details>

────────────────────────────────────────────────────────────

## 2024 Abu Dhabi GP  ·  Round 24 | 2024-12-08

**Drivers in race:** 20  
**Actuals available:** Yes

### Logistic Regression

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Max Verstappen | **97%** | ❌ No |
| 2 | Lando Norris | **95%** | ✅ Podium |
| 3 | Oscar Piastri | **85%** | ❌ No |

**Precision@3:** 33%  (0/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Max Verstappen | 97.5% | — |
| 2 | Lando Norris | 94.6% | ✅ |
| 3 | Oscar Piastri | 85.4% | — |
| 4 | Carlos Sainz | 81.9% | ✅ |
| 5 | George Russell | 58.5% | — |
| 6 | Sergio Pérez | 32.9% | — |
| 7 | Charles Leclerc | 25.9% | ✅ |
| 8 | Fernando Alonso | 20.3% | — |
| 9 | Pierre Gasly | 18.7% | — |
| 10 | Lewis Hamilton | 13.9% | — |
| 11 | Nico Hülkenberg | 13.4% | — |
| 12 | Yuki Tsunoda | 5.7% | — |
| 13 | Valtteri Bottas | 4.9% | — |
| 14 | Liam Lawson | 3.5% | — |
| 15 | Lance Stroll | 3.5% | — |
| 16 | Kevin Magnussen | 2.6% | — |
| 17 | Jack Doohan | 1.5% | — |
| 18 | Guanyu Zhou | 1.3% | — |
| 19 | Alexander Albon | 1.0% | — |
| 20 | Franco Colapinto | 0.5% | — |

</details>

### XGBoost

**Top 3 Podium Picks:**

| # | Driver | Probability | Actual |
|---|--------|------------:|--------|
| 1 | Lando Norris | **84%** | ✅ Podium |
| 2 | Carlos Sainz | **84%** | ✅ Podium |
| 3 | Oscar Piastri | **75%** | ❌ No |

**Precision@3:** 67%  (1/3 correct)

<details>
<summary>Full field probabilities</summary>

| Rank | Driver | Probability | Actual |
|-----:|--------|------------:|--------|
| 1 | Lando Norris | 83.6% | ✅ |
| 2 | Carlos Sainz | 83.6% | ✅ |
| 3 | Oscar Piastri | 74.9% | — |
| 4 | Max Verstappen | 65.0% | — |
| 5 | George Russell | 25.8% | — |
| 6 | Charles Leclerc | 18.4% | ✅ |
| 7 | Lewis Hamilton | 15.7% | — |
| 8 | Fernando Alonso | 7.8% | — |
| 9 | Sergio Pérez | 5.6% | — |
| 10 | Nico Hülkenberg | 1.5% | — |
| 11 | Pierre Gasly | 0.9% | — |
| 12 | Lance Stroll | 0.6% | — |
| 13 | Alexander Albon | 0.6% | — |
| 14 | Liam Lawson | 0.4% | — |
| 15 | Jack Doohan | 0.3% | — |
| 16 | Yuki Tsunoda | 0.3% | — |
| 17 | Valtteri Bottas | 0.3% | — |
| 18 | Franco Colapinto | 0.2% | — |
| 19 | Guanyu Zhou | 0.1% | — |
| 20 | Kevin Magnussen | 0.1% | — |

</details>

────────────────────────────────────────────────────────────

────────────────────────────────────────────────────────────

_Generated by `predict_race_podium.py`.  
Re-run after retraining to refresh predictions._