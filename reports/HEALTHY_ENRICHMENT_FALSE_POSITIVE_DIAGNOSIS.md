# Diagnosis of increased healthy false positives

## Observed change

Adding the adapted MAREA/DUO-GAIT healthy pool changed RevalExo results from AUROC 0.914, Brier 0.161, balanced accuracy 0.714 to AUROC 0.929, Brier 0.177, balanced accuracy 0.571. Healthy false positives increased from 4/7 to 6/7; stroke false negatives stayed 0/10.

## Signal-distribution evidence

The added healthy sources are not identical to the original healthy training sources. Mean per-window magnitudes were:

| Healthy source | LB mean | LF mean | RF mean |
|---|---:|---:|---:|
| Felius | 1.023 | 1.740 | 1.790 |
| Voisard | 1.030 | 1.535 | 1.586 |
| DUO-GAIT | 1.032 | 1.649 | 1.704 |
| MAREA | 1.059 | 1.615 | 1.618 |

The MAREA lower-back magnitude is higher than the original healthy sources, while its foot magnitudes are lower and more symmetric. This is consistent with residual placement, hardware, protocol, or preprocessing-domain shift despite unit conversion and resampling.

## Most likely mechanism

The enrichment improved ranking slightly but shifted probability scores upward for most external healthy participants. That means the change is not simply loss of discriminative information: it is a combination of domain shift and probability/threshold miscalibration. Source-balanced sampling also changed the effective training distribution by adding two new healthy source domains.

## Decision

Do not reject healthy enrichment outright. Re-run it with source-aware validation and calibration:

1. Fit normalization using the training fold only and retain source-specific distribution summaries.
2. Compare global normalization against source-conditional normalization learned only from training data.
3. Test source-balanced weighting versus participant-balanced weighting.
4. Select the decision threshold on held-out internal validation, never on RevalExo.
5. Keep RevalExo frozen for the final comparison.

The current evidence supports “healthy enrichment changes domain calibration,” not “healthy enrichment is useless.”
