---
type: study
year: 2022
pathway: IC4
population: "33-35 stroke inpatients, no healthy comparison group"
method: "Balanced Random Forest"
placement: "3 IMUs: pelvis, bilateral ankle"
---

O'Brien et al. (2022), *Wearable sensors improve prediction of post-stroke walking function following inpatient rehabilitation*, *IEEE Journal of Translational Engineering in Health and Medicine* 10:2100711. Predicts discharge ambulation category (household vs. community ambulator) from admission gait data — a genuinely clinically actionable outcome rather than a diagnostic label.

## Key findings

- Weighted F1 = 0.943, AUROC = 0.988.
- Chronicity: 9.5 ± 7.1 days post-admission (acute/early subacute) — one of only two studies (with [[sun-2025]]) reporting a numeric chronicity value.
- [[quality-assessment]] flags this study specifically: the authors **self-disclose partial data leakage** in their own leave-one-subject-out design ("models were optimized using data from all participants to select features and hyperparameters, resulting in some data leakage between the training and test sets") — a limitation reported directly in the source paper, not uncovered by this review.

## Links

Part of [[quality-assessment]]'s two headline findings, alongside [[sun-2025]]'s apparent lack of any train/test split at all.
