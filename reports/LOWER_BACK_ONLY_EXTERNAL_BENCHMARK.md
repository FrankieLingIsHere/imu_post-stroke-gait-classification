# Lower-back-only external benchmark

The lower-back-only model was trained on the complete internal Felius + Voisard + Sint development set using source/class-balanced sampling and GPU training. RevalExo remained untouched until evaluation.

Results are written to `data/processed/full_expanded_lower_back_only_revalexo_metrics.csv`; participant predictions are written to `data/processed/full_expanded_lower_back_only_revalexo_participant_predictions.csv`.

## Result

| Model | AUROC | Brier score | Balanced accuracy |
|---|---:|---:|---:|
| Lower-back only | 0.757 | 0.217 | 0.571 |
| Existing expanded three-channel comparator | 0.914 | 0.161 | 0.714 |

RevalExo contains 17 participants (7 healthy, 10 stroke). The lower-back-only model does not pass the external robustness gate: it is substantially weaker than the three-channel comparator and is poorly calibrated on this small external cohort.

## Consequence for last week's limitations

The next improvement should not be more lower-back-only training. It should be external calibration and error analysis, followed by a sensor-ablation investigation to determine whether the failure is caused by missing foot information, domain shift, or the small external sample. The lower-back-only model remains useful as a transparent baseline, not as the final prototype.
