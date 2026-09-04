# Lower-back-only versus three-channel benchmark

## Matched protocol

Both models used the same Felius + Voisard + Sint pooled windows, source/class-balanced sampling, five-fold participant-disjoint validation, fold-specific normalization, seed 42, and 12 training epochs on GPU.

## Participant-level internal results

| Model | Mean AUROC | Mean Brier score | Mean balanced accuracy |
|---|---:|---:|---:|
| Lower-back only | 0.933 | 0.121 | 0.829 |
| Three-channel LB/LF/RF | 0.966 | 0.074 | 0.926 |

## Interpretation

The lower-back-only model provides a credible practical single-sensor baseline, but it loses approximately 0.033 AUROC and 0.096 balanced accuracy relative to the matched three-channel model. The three-channel model therefore remains the performance model, while lower-back-only remains the primary deployment-oriented research question.

This comparison does not prove that lower back is clinically inferior. The original EDA showed that foot features can have larger within-dataset effects, while lower-back placement has stronger single-sensor practicality and broader domain rationale. External lower-back-only validation is still required before selecting a final prototype.

Detailed fold results: `data/processed/lower_back_vs_three_channel_matched_metrics.csv`.
