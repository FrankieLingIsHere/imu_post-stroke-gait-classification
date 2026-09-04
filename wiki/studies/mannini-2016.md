---
type: study
year: 2016
pathway: IC1
population: "15 post-stroke (mean age 61.3y) vs 10 healthy elderly (mean age 69.7y), plus 17 Huntington's disease"
method: "Hidden Markov Model + SVM"
placement: "bilateral shank, lumbar spine (128 Hz)"
---

Mannini et al. (2016), *A machine learning framework for gait classification using inertial sensors*, *Sensors* 16(1):134. The earliest and most complete illustration of the field's standard pipeline: sensor → feature extraction → classifier. A hidden Markov model extracts probabilistic features describing each group's characteristic movement pattern, then an SVM classifies from those features.

## Key findings

- 86.7–90.5% accuracy under leave-one-subject-out cross-validation (90.5% is the subject-level figure after majority voting across a walking bout; the paper separately reports 73.3% at the per-passage level and 66.7% for the HMM stage alone).
- Comparison groups are closer in age (61.3y vs 69.7y, ~8-year gap) than [[voisard-2025]]'s much larger 21-year gap, which limits age-confound risk relative to this review's own hands-on mining.
- **Corrected 2026-07-29**: this page and the manuscript previously described this study's "lumbar-spine sensor performing well independently" as one of the studies converging on [[sensor-placement]]'s trunk-placement finding. A third `journal-critic` adversarial review caught that this is wrong — verified directly against the full text: the study's seven-variable HMM feature vector draws six variables from a single shank sensor and only one (mediolateral acceleration) from the waist. No lumbar-only classification result is reported anywhere in the paper; shank and waist data are combined into one model throughout. This study is therefore shank-dominant, not lumbar-placement evidence, and was removed from [[sensor-placement]]'s trunk-convergence argument.
- **Corrected again 2026-07-30 (fourth `journal-critic` pass)**: the 2026-07-29 fix itself over-corrected by stating this study is "not genuine lumbar-placement evidence at all." That's not accurate either — the sensor placed at the waist genuinely is a lumbar-spine sensor, between L4 and S2, confirmed directly against the full text. The accurate statement is narrower: it's a real lumbar sensor that doesn't happen to produce lumbar-*dominant* evidence, since six of its seven features come from the shank. "Waist" and "lumbar spine" refer to the same physical sensor throughout this study and are used interchangeably in this review.
- **Introduction citation error, fixed 2026-07-30**: the manuscript's Introduction previously credited this study, alongside [[wu-2025]], with grading severity or tracking gait change over rehabilitation. Neither is accurate for this study — it performs binary diagnostic classification only, no severity grading and no longitudinal tracking. The claim was removed from the Introduction rather than re-attributed, since Wu et al. (2025) alone demonstrates severity grading, and no included study demonstrates tracking gait change over rehabilitation specifically.
- [[quality-assessment]]: held-out/CV confirmed (LOSO), no code/data availability statement, severity-only reporting (FAC = 3.2, SD 1.5), no explicit control-group age-matching statement despite the gap.

## Links

Discussed in [[discriminative-features]] for its 90-feature HMM+time-frequency approach. No longer linked from [[sensor-placement]]'s trunk-convergence list — see the correction note above.
