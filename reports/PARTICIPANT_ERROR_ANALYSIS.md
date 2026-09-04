# Participant-level error analysis

This audit uses the existing `architecture_comparison_participant_predictions.csv`. It does not retrain models or alter participant splits. The 0.5 probability threshold is descriptive only; threshold selection remains a separate validation task.

## Results by dataset

| Model | Dataset | AUROC | Balanced accuracy | Sensitivity | Specificity | FP | FN |
|---|---|---:|---:|---:|---:|---:|---:|
| Compact CNN | Felius | 0.916 | 0.830 | 0.806 | 0.853 | 5 | 25 |
| Compact CNN | Voisard | 0.963 | 0.830 | 0.673 | 0.986 | 1 | 16 |
| Inception CNN | Felius | 0.924 | 0.845 | 0.837 | 0.853 | 5 | 21 |
| Inception CNN | Voisard | 0.971 | 0.867 | 0.776 | 0.958 | 3 | 11 |
| MiniROCKET + ridge | Felius | 0.950 | 0.904 | 0.984 | 0.824 | 6 | 2 |
| MiniROCKET + ridge | Voisard | 0.969 | 0.931 | 0.918 | 0.944 | 4 | 4 |

## Findings

1. MiniROCKET has the strongest descriptive participant-level balanced accuracy and sensitivity in both datasets.
2. MiniROCKET reduces false negatives substantially, but produces slightly more false positives than the CNNs, especially in Felius.
3. The Inception CNN is directionally better than the compact CNN, but the difference is not yet an equivalence-tested model-selection result.
4. Model predictions agree on the final 0.5 decision for approximately 80.6% of participants; disagreement is therefore concentrated enough to justify an error review rather than a simple majority vote.
5. Dataset shift remains visible: the CNNs have lower sensitivity in Voisard than Felius, while MiniROCKET is more balanced across sources.

## Decision

Do not replace the current pooled Inception development contract yet. However, MiniROCKET must be promoted to a co-primary candidate for the next locked comparison. The next comparison must use participant-bootstrap AUROC and balanced-accuracy differences, source-specific results, calibration, and the frozen RevalExo test—not pooled averages alone.

## Limitations

The current prediction file does not contain direct gait speed, clinical severity, or complete age metadata for every participant. These results therefore cannot establish speed independence or clinical-severity generalization.
