---
type: study
year: 2024
pathway: IC4
population: "55 stroke inpatients, no healthy comparison group (43 ambulatory / 12 nonambulatory at admission)"
method: "L1-penalized logistic regression, nested leave-one-subject-out CV"
placement: "3 IMUs: lumbar (L4-L5), bilateral ankle"
---

O'Brien et al. (2024), *Early prediction of poststroke rehabilitation outcomes using wearable sensors*, *Physical Therapy* 104(2):pzad183, https://doi.org/10.1093/ptj/pzad183. Found via a 2026-07-28 literature search targeting new RQ3 evidence. A distinct study from the same overlapping author group as [[obrien-2022]] — different journal, different classifier, different outcome framing, two years apart — not a duplicate.

## Key findings

- Predicts three discharge functional outcomes from admission-time data (10-Meter Walk Test and Berg Balance Scale sensor recordings plus functional assessment scores): ambulation, independence, and risk of falling, each a binary classification target rather than a diagnostic label.
- For the ambulatory-at-admission cohort (n=32 with usable sensor data): 84.4% accuracy for ambulation, 68.8% for independence, 65.9% for risk of falling.
- For the nonambulatory-at-admission cohort (n=8 tested, trained on n=50 combined ambulatory+nonambulatory data): sensor data recorded during simple balance tasks did **not** improve prediction over benchmark models — a negative result reported directly by the authors rather than omitted.
- Classical machine learning only (L1-penalized logistic regression) — no deep learning component anywhere in this study. Reinforces [[classification-methods]]'s existing classical-ML-dominance finding rather than closing its named classical-vs-deep-learning gap.
- [[quality-assessment]]: nested leave-one-subject-out CV confirmed (no self-disclosed leakage, unlike [[obrien-2022]]'s own LOSO design), no code or data availability statement anywhere in the paper, neither chronicity (time since stroke onset unreported, only "within 1 week of IRF admission" as an assessment-timing detail) nor a severity score (no NIHSS, Fugl-Meyer, or equivalent) reported, no healthy comparison group at all since this is a stroke-only IC4 design.

## Links

Companion to [[obrien-2022]] rather than a replacement — both come from overlapping authorship, both use lumbar/ankle IMU placement, but this one trains a different classifier (logistic regression vs. Balanced Random Forest) on a different, larger stroke-only cohort (55 vs. 33-35) predicting discharge outcomes framed around three distinct functional targets rather than a single ambulation category. Adds a second real-world negative result to [[quality-assessment]] alongside [[sun-2025]]'s overfitting risk and [[obrien-2022]]'s leakage — this one being an honest "sensor data didn't help" finding for the nonambulatory subgroup, worth keeping visible rather than only reporting studies' positive results.
