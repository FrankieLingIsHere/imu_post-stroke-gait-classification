# Final channel ablation and false-positive localization

Locked before new fits, 2026-09-09. Reuse completed frame6/magnitude results;
do not retrain those arms. Train acc3 and gyro3 using the identical waveform frame,
cycles, participant splits, two validation-selected recipes and three seeds.
36 new fits. Gyro3 contains only angular velocity values, but its coordinate frame
is estimated from acceleration: it is not an accelerometer-free measurement system.
No test-selected settings, normalization or thresholds. Existing frame protocol
applies, including reference-assisted strides and approximate gravity limitations.

Compare each new arm against saved frame6, paired by seed/participant. Same gate:
>=5pp lower neurological FPR with no extra stroke misses or healthy false positives
in full and matched scopes, across every seed. External DUO-GAIT remains a reused
healthy stress test and never selects recipes. No claim of independent validation.

Localize false positives using all saved arms: participant IDs and margins,
pathology-specific denominators, consistency across seeds, per-fold thresholds,
paired DUO-GAIT condition changes and score overlap. Attribute model/fold differences
descriptively; pathology and outer fold are entangled by design. Fixed.5 versus
calibrated thresholds is an operating-point comparison, not a threshold-only
causal experiment. Do not identify signal biomarkers from feature ablation alone.
This is the final planned exploratory sweep in this sequence; retain models only
as research baselines if specificity remains inadequate. No post-result rescue sweep.
