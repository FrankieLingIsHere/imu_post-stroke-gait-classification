# Revised model-selection gate

The previous gate was rejected because it mixed non-equivalent external summaries. This revised gate compares the same 17 RevalExo participants using the same `LB/LF/RF` input tensor and fold-matched Inception and MiniROCKET predictions.

## Paired frozen-external comparison

Predictions from the five fold models were averaged per participant before the final comparison. A paired participant bootstrap with 20,000 replicates estimated model differences.

| Metric | Inception | MiniROCKET | MiniROCKET − Inception 95% CI |
|---|---:|---:|---:|
| AUROC | 0.871 | 0.886 | −0.129 to +0.167 |
| Brier score | 0.185 | 0.214 | −0.021 to +0.086 |

The AUROC difference is uncertain and compatible with either model being better. The Brier difference favours Inception directionally, but its confidence interval also includes zero. With 17 participants, this cohort cannot support a definitive model-selection claim.

## Correct decision

Do not declare either model superior. Keep both as locked candidates:

- Inception: primary raw-signal candidate with better current calibration evidence and completed attribution.
- MiniROCKET: challenger with stronger internal balanced accuracy and comparable external discrimination.

This is a protocol decision, not a final scientific winner. Any selection based only on the point estimates would be unreliable.

## Required decisive test

Use a new independent cohort with enough participants for a paired non-inferiority/equivalence design. Pre-specify:

1. Primary endpoint: participant-level AUROC difference.
2. Secondary endpoints: Brier score, ECE, sensitivity, specificity, and false-negative rate at a validation-locked threshold.
3. Equivalence margin: e.g. ±0.03 AUROC, justified by power analysis before data collection.
4. One locked preprocessing and calibration protocol for both models.
5. Participant-level bootstrap confidence intervals and a paired permutation test.
6. Prespecified age, sex, speed, device, and stroke-severity subgroup analyses.

Until that cohort exists, report both models and avoid a definitive superiority statement.
