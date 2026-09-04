# Final model-selection gate

## Evidence summary

| Criterion | Inception CNN | MiniROCKET + calibrated Ridge |
|---|---|---|
| Internal discrimination | Strong; pooled AUROC approximately 0.944 in repeated validation | Strong; raw AUROC approximately 0.971 across five outer folds |
| Internal balanced accuracy | Competitive | Higher in both Felius and Voisard bootstrap comparison |
| Internal calibration | Brier 0.091 and ECE 0.113 in the selected robust pooled run | Calibrated Brier 0.060 and ECE 0.086 in five-fold calibration run |
| Frozen RevalExo AUROC | 0.871 | 0.874 mean across five fold models |
| Frozen RevalExo Brier | 0.170 | 0.215 mean across five fold models |
| Input contract | Direct 3-channel raw acceleration magnitude | Same 3-channel raw acceleration magnitude |
| External adapter | Existing and validated | Newly validated, but implemented in WSL due Windows Numba restriction |
| Interpretability | Channel occlusion available; lower-back channel most influential in fold 0 | No attribution result yet |
| Evidence limitation | External cohort only 17 participants | Same 17-participant limitation; calibration weaker externally |

## Revised decision

Do not declare Inception superior. The paired frozen-external comparison is underpowered: after averaging the five fold models per participant, AUROC was 0.871 for Inception and 0.886 for MiniROCKET, with a paired bootstrap AUROC-difference interval of -0.129 to +0.167. Brier scores were 0.185 and 0.214 respectively, with a difference interval of -0.021 to +0.086. Keep both as locked candidates until an adequately powered independent cohort supports equivalence or superiority testing.

## What is not concluded

- Neither model is clinically ready.
- The 17-participant RevalExo result is not a clinical validation study.
- Neither model has demonstrated independence from gait speed because direct speed is unavailable in the primary data.
- Synthetic data, age cascades, or source pooling changes are not justified by this gate.

## Next development phase

1. Lock the Inception preprocessing, calibration, checkpoint, and threshold-selection protocol.
2. Preserve MiniROCKET as a challenger in every future external evaluation.
3. Complete cross-fold Inception temporal attribution.
4. Obtain an age-, sex-, and speed-characterised independent cohort.
5. Re-run both locked candidates on that cohort before any clinical-readiness claim.
