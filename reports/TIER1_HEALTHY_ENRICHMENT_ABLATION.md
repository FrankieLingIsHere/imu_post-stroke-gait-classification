# Tier 1 healthy-enrichment ablation

This experiment compares the established Felius + Voisard + Sint training pool with the same pool plus the adapted MAREA/DUO-GAIT healthy windows. Both models use the same GPU Inception-style network, source/class-balanced sampling, train-set normalization, 15 epochs, seed 42, and untouched RevalExo evaluation.

Results are written to `data/processed/tier1_healthy_enrichment_ablation_metrics.csv`. The experiment tests whether additional healthy population diversity reduces external healthy false positives without degrading stroke sensitivity.

## Result

| Training condition | Participants | Windows | External AUROC | Brier score | Balanced accuracy |
|---|---:|---:|---:|---:|---:|
| Established pooled baseline | 314 | 22,506 | 0.914 | 0.161 | 0.714 |
| + adapted MAREA/DUO-GAIT healthy pool | 350 | 28,444 | 0.929 | 0.177 | 0.571 |

The enriched model improved AUROC by 0.014, but worsened Brier score and threshold balanced accuracy. Healthy false positives increased from 4/7 to 6/7, while stroke false negatives remained 0/10. The extra healthy domains therefore changed ranking slightly but did not solve the healthy false-positive problem and made the default threshold less reliable.

## Decision

Do not adopt this enrichment as the final training recipe. Retain the adapted pool for domain analysis and investigate calibration, source weighting, and healthy-domain mismatch before another training attempt.
