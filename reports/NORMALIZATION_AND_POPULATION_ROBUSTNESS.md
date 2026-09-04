# Normalization and population robustness decision

## Decision

Normalization should be tested as a robustness component, but it must not be treated as a way to erase age or testing-condition effects automatically. Age, walking speed, cadence, variability, asymmetry, and trunk smoothness may be part of the biological distinction between healthy and post-stroke gait. The safe objective is to reduce measurement and protocol shift while retaining clinically meaningful gait variation.

The current model already uses fold-fitted global normalization. The next controlled comparison is:

1. Existing pooled global mean/standard-deviation normalization (locked baseline).
2. Robust global median/IQR normalization (less sensitive to outliers).
3. Subject/recording-level unsupervised robust scaling, only if the deployment scenario permits a short unlabeled calibration segment.
4. Source-conditional normalization learned on training sources only, used as a diagnostic rather than an assumed deployment solution.
5. Nuisance augmentation (small amplitude, offset, orientation and time-scale perturbations) after the transform is selected.

Per-window z-scoring is not the default candidate because it can remove amplitude and energy information that may encode impairment. Speed normalization is also deferred until direct speed metadata are available; cadence or RMS must not be used as an invented speed proxy.

## Current evidence from this project

The healthy-enrichment false-positive analysis already identified residual domain shift after unit conversion and resampling: MAREA had higher lower-back magnitude and lower, more symmetric foot magnitudes than the original healthy sources. The added pool improved external AUROC from 0.914 to 0.929 but worsened Brier score from 0.161 to 0.177 and healthy false positives from 4/7 to 6/7. This is exactly the situation where normalization and calibration must be evaluated together rather than judged by AUROC alone.

The lower-back-first research question remains protected. The primary track will keep a lower-back-only model; the three-channel model is the comparator and potential performance ceiling. A normalization variant cannot be accepted if it improves pooled AUROC only by worsening lower-back external specificity or by exploiting source identity.

## What the audit does

`scripts/audit_normalization_strategies.py` records raw source distributions and the residual source shift under global z-score and global robust scaling. It does not fit on RevalExo, use labels for scaling, or overwrite any existing artifact. Its output is `data/processed/normalization_strategy_audit.csv`.

## Acceptance criteria for the next model experiment

- All scaling statistics are fitted inside each training fold.
- RevalExo remains frozen for model selection and threshold selection.
- Report AUROC, balanced accuracy, Brier score, calibration error, and healthy false-positive count at the pre-registered threshold.
- Report lower-back-only and three-channel results separately.
- Use leave-one-source-out or frozen external testing to detect source shortcuts.
- Reject a transform if it improves ranking but increases calibration error or healthy false positives without a clinically defensible explanation.

## Recent literature boundary (2022--2026)

Recent inertial-sensor work confirms that age, body characteristics, and walking pace can bias gait measures, so population robustness cannot be assumed from a single pooled score. A 2024 cross-sectional IMU study reported age-associated differences in gait velocity and joint angles. A 2022 body-worn-sensor validation study found that double-support validity was jointly affected by age, height, weight, and walking pace. Recent post-stroke wearable studies continue to use speed, symmetry, variability, and trunk/upper-body smoothness as meaningful impairment descriptors; these should be preserved and audited, not normalized away.

## References

- [Inertial measurement unit sensor-based gait analysis in adults and older adults (2024)](https://www.sciencedirect.com/science/article/pii/S0966636223014522)
- [Validation of body-worn sensors for gait analysis during a 2-min walk test in children (2022)](https://pmc.ncbi.nlm.nih.gov/articles/PMC10398795/)
- [Identifying key gait features in stroke patients using wearable inertial sensors and supervised and unsupervised machine learning (2026)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12987975/)
- [Data-driven quantitation of movement abnormality after stroke (2023)](https://pmc.ncbi.nlm.nih.gov/articles/PMC10294965/)
