# Sint sensitivity-training experiment

The first expanded training experiment has completed using Felius + Voisard + Sint Maartenskliniek.

Configuration:

- participant-disjoint stratified 5-fold validation;
- GPU-capable Inception-style CNN;
- source/class-balanced sampling;
- fold-specific normalization;
- 12-epoch fixed training budget;
- no RevalExo data used for fitting or tuning;
- the earlier Sint external examination result was not used for model selection.

| Fold | Participants | AUROC | Brier | Balanced accuracy |
|---:|---:|---:|---:|---:|
| 0 | 63 | 0.984 | 0.066 | 0.941 |
| 1 | 63 | 0.978 | 0.044 | 0.981 |
| 2 | 63 | 0.958 | 0.081 | 0.894 |
| 3 | 63 | 0.975 | 0.089 | 0.840 |
| 4 | 62 | 0.934 | 0.094 | 0.864 |
| Mean | 62.8 | **0.966** | **0.075** | **0.904** |

These are internal expanded-development results only. They do not establish that Sint should remain in the final model. The required next gate is evaluation of the saved sensitivity checkpoints on untouched RevalExo, followed by source-specific error and calibration comparison against the original two-source baseline.

## Untouched RevalExo gate

The expanded checkpoints were evaluated once on the untouched 17-participant RevalExo cohort. Result: AUROC **0.914**, Brier **0.162**, and balanced accuracy **0.714**. The original two-source Inception result was AUROC 0.871 and Brier 0.170. This is an encouraging discrimination/calibration improvement, but the small external cohort and lower descriptive balanced accuracy require participant-level error analysis before accepting Sint into the final training pool.

### Paired error analysis

The expanded model reduced RevalExo healthy false positives from **6/7 to 4/7**, while retaining **10/10 stroke participants correctly above the 0.5 descriptive cutoff**. Two healthy participants changed from false positive to correct; no stroke participant changed from correct to false negative. Mean healthy probability decreased from 0.587 to 0.547, while mean stroke probability increased from 0.771 to 0.811. This is directionally favorable, but it is still based on only seven healthy controls and ten stroke participants.

### Paired bootstrap gate

Across 19,995 valid paired participant bootstrap replicates, the expanded-minus-original AUROC difference was +0.044 with 95% CI [0.000, 0.171]. The Brier difference was -0.022 with 95% CI [-0.040, -0.002]. This supports retaining Sint as a prototype training candidate, but not claiming clinical superiority because RevalExo contains only 17 participants.
