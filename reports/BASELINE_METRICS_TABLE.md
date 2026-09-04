# Frozen baseline metrics

| Evaluation scope | Participants | AUROC | Balanced accuracy | F1 | Brier |
|---|---:|---:|---:|---:|---:|
| Felius + Voisard pooled | 284 | 0.957 | 0.886 | 0.904 | — |
| Felius only | 163 | 0.930 | 0.842 | 0.902 | — |
| Voisard only | 121 | 0.982 | 0.924 | 0.909 | — |
| RevalExo frozen external | 17 | 0.871 | — | — | 0.170 |

The external Brier score is descriptive only; no external calibration or clinical threshold was fitted. Window predictions were aggregated to participants before reporting.
