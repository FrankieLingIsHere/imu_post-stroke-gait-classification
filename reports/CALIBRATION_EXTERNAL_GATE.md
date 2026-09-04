# Calibration and external-evaluation gate

## Calibration audit

Computed from the existing participant-level architecture-comparison predictions. No retraining or recalibration was performed.

| Model | Dataset | Brier score | ECE-10 |
|---|---|---:|---:|
| Compact CNN | Felius | 0.134 | 0.193 |
| Compact CNN | Voisard | 0.097 | 0.107 |
| Inception CNN | Felius | 0.117 | 0.185 |
| Inception CNN | Voisard | 0.087 | 0.114 |
| MiniROCKET + ridge | Felius | 0.129 | 0.290 |
| MiniROCKET + ridge | Voisard | 0.129 | 0.266 |

The Inception CNN has the best descriptive Brier scores. MiniROCKET's discrimination advantage is not accompanied by better probability calibration in this output. ECE estimates are exploratory because the number of independent participants per dataset is small.

## Frozen external evaluation

The existing RevalExo external result remains:

- 17 participants
- AUROC 0.871
- Brier score 0.170

This evaluates the validated Inception/raw-signal adapter. MiniROCKET cannot currently be evaluated fairly on RevalExo because its existing implementation consumes engineered features and there is no validated RevalExo feature-extraction adapter matching the training contract. It must not be evaluated by substituting incompatible features or by using RevalExo to tune a new adapter.

## Decision

Do not replace the Inception development contract yet. Current evidence is mixed: MiniROCKET has stronger discrimination/balanced accuracy, while Inception has better calibration and an existing frozen external evaluation. The next valid step is either:

1. build and validate a source-independent engineered-feature adapter for RevalExo without touching the frozen test decision, or
2. complete Inception attribution/occlusion analysis and treat MiniROCKET as an internal comparator only.

No final model-selection claim is justified until both candidates have comparable external evidence or the limitation is explicitly accepted.
