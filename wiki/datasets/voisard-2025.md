---
type: dataset
population: "260 participants: 73 HS, 143 neuro (49 CVA/stroke, 19 CIPN, 24 Parkinson's, 51 RIL), 44 ortho (ACL/HOA/KOA)"
sensors: "head, lower back, bilateral foot, 100 Hz"
role: primary
---

Voisard, C. et al. (2025), *A dataset of clinical gait signals with wearable sensors from healthy, neurological, and orthopedic cohorts*, *Scientific Data* 12:1674. The review's **primary** hands-on-mining dataset — the largest, richest-metadata real stroke-vs-healthy source, and the only one of the two real stroke datasets with any participant-level demographic data at all.

## Key findings (this review's own re-mining)

- HS/CVA comparison uses 73 healthy + 49 CVA participants (488 trials). **Not age-matched**: HS averages 37.7y (SD 19.5) vs. CVA 59.0y (SD 8.8), a ~21-year gap.
- Raw cadence looked discriminative (p < .001) but reversed to non-significant (p = .315) after age-adjustment via linear residualization — the review's central demographic-confound finding. **Collinearity check added 2026-07-29** (after a `journal-critic` review questioned whether age and group were too correlated for the regression to separate them): point-biserial r = 0.48 between age and group, VIF approximately 1.3 — moderate, not severe by conventional thresholds — and every CVA participant's age falls within the HS group's own broader range, confirming enough within-group age variation exists for the adjustment to be meaningful rather than an artifact of near-perfect collinearity.
- Lower back RMS, head RMS, mean stride time, and stride-time CV all remain significant after age-adjustment (rank-biserial r = 0.58, 0.30, -0.43, -0.32) and anchor [[sensor-placement]]'s trunk-placement finding.
- The age-by-stroke interaction audit used one participant-level row per Voisard participant. Head RMS and lower-back RMS had nominal interaction p-values of 0.039 and 0.049, but both became q = 0.148 after Benjamini--Hochberg correction across six features. The result supports age-stratified auditing, not an age-gated stroke classifier. See [[age-and-stroke-gait]].
- The provisional age bands contain 43 healthy and 0 CVA participants at 18--39, 15 healthy and 27 CVA participants at 40--59, and 15 healthy and 22 CVA participants at 60+. Only the latter two bands support within-band binary performance checks.
- The complete release has 259 participants with valid ages from 18 to 90 years across healthy, neurological and orthopedic cohorts. One participant has an invalid or missing age value. The primary healthy/CVA subset has 72 healthy participants with usable validated windows and ages 18--87, while CVA participants begin at age 41. This is broad overall coverage but not broad age overlap for the binary stroke task.
- Continuous age regression on healthy Voisard participants was exploratory. A Ridge model using engineered gait features reached mean MAE 12.86 years and R² 0.310 across repeated participant-level folds. The GPU Inception-style regression reached MAE 13.42 years and R² 0.243. See [[age-and-stroke-gait]].
- In the age-adjusted stroke baseline, raw gait features reached AUROC 0.973, gait plus age reached 0.968 and age alone reached 0.803 across repeated participant-level folds. Age-residualized gait fell to AUROC 0.882. This is a shortcut audit on the current age-imbalanced subset, not evidence for clinical deployment. See [[age-and-stroke-gait]].
- A **second**, independently discovered confound: HS gender effect is real on cadence and both stride-time measures even after age-adjustment, but the two accelerometer-RMS gender effects are age artifacts. See the manuscript's Section 4.2.2 for the full age-adjusted gender breakdown.
- Voisard's per-trial Fugl-Meyer LE and Timed-Up-and-Go scores remain under-exploited — not yet used beyond the binary healthy-vs-stroke comparison. Flagged as a specific gap in [[future-directions]].
- Nested SBS+CV: 0.89 accuracy (SD 0.06). Single-level CV: 0.92 (SVM) / 0.95 (RF). Cluster purity 0.76, adjusted Rand index 0.27.

## Links

Paired directly against [[felius-dataset]] throughout [[discriminative-features]] and [[sensor-placement]] as the review's two real stroke-vs-healthy sources. The age and gender confounds discovered here are the review's most-cited original findings — see `synthesis.md`.
