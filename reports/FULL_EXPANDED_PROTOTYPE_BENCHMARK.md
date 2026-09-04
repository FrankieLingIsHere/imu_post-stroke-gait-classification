# Full expanded prototype benchmark

The full-data expanded Inception checkpoint was evaluated once on untouched RevalExo at participant level.

| Model | Training scope | RevalExo participants | AUROC | Brier | Balanced accuracy |
|---|---|---:|---:|---:|---:|
| Original Inception | Felius + Voisard | 17 | 0.871 | 0.185 | descriptive |
| Expanded sensitivity Inception | Felius + Voisard + Sint, fold models | 17 | 0.914 | 0.162 | 0.714 |
| Full expanded prototype | Felius + Voisard + Sint, full-data fit | 17 | **0.914** | **0.161** | 0.714 |

The full-data checkpoint reproduces the expanded sensitivity result closely and slightly improves its Brier score. This supports using Sint in the prototype training pool. RevalExo remains a small external stress test rather than clinical validation, and the full-data checkpoint must not be evaluated on the development pool as if that were an unbiased benchmark.

Files:

- `data/processed/full_expanded_prototype_revalexo_metrics.csv`
- `data/processed/full_expanded_prototype_revalexo_participant_predictions.csv`
