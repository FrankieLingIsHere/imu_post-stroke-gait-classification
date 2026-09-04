# Baseline next actions and plan reconciliation

## Scope protection

The pasted roadmap is retained as a methodological guide, but its dataset and project-status statements are stale relative to the current implementation. No existing accepted result is being replaced by this audit.

### Current implementation takes precedence

| Topic | Pasted roadmap | Current verified state |
|---|---|---|
| Classifier status | CNN still to be trained | Pooled Inception CNN, compact CNN, and MiniROCKET have already been evaluated |
| Primary development data | 288 participants described as the effective sample | Current materialised modeling comparison contains 284 participants: 163 Felius and 121 Voisard |
| Primary window | Proposed 10-second windows | Current validated baseline uses 5-second windows, 500 samples, three magnitude channels |
| External data | Recruit/evaluate a new cohort | RevalExo is already available as a frozen external stress test |
| Age | Age/speed confound audit proposed | Age audit is complete; direct speed is unavailable in all 865 primary trials |
| Model candidate | InceptionTime proposed as first model | Inception remains the deep candidate, but MiniROCKET and compact CNN are competitive and must remain in comparison |

The difference between 288 manifest participants and 284 modeling-comparison participants must be preserved as an inclusion/materialisation distinction, not silently reconciled by changing historical results.

## Current model comparison

Using the existing participant-level architecture comparison outputs:

| Model | Felius AUROC | Voisard AUROC | Overall mean AUROC across folds |
|---|---:|---:|---:|
| Compact CNN | 0.916 | 0.963 | 0.973 ± 0.024 |
| Inception CNN | 0.924 | 0.971 | 0.962 ± 0.028 |
| MiniROCKET + ridge | 0.950 | 0.969 | 0.972 ± 0.021 |

These values are not a final model-selection claim. They show that MiniROCKET currently has the strongest Felius participant-level AUROC in this comparison, while the CNNs are competitive. A new primary model must not be selected from pooled mean AUROC alone.

## Protected findings

- Source-balanced pooled training remains the development contract.
- RevalExo remains frozen and excluded from training, normalization, calibration, threshold selection, and model selection.
- Age remains outside the primary stroke classifier.
- Gait speed is an unresolved limitation, not a variable that may be reconstructed from cadence/RMS.
- GaitMotion and healthy-only datasets are not to be merged into the real supervised stroke task.
- Participant-level evaluation remains mandatory.

## Next experiments, in order

1. Reconcile the 288-to-284 participant accounting and document the exact exclusions/materialisation rule.
2. Produce participant-level error tables for MiniROCKET, compact CNN, and Inception CNN by dataset and label.
3. Add age-overlap strata where age is available; do not invent Felius ages.
4. Run cadence/RMS-associated error analysis as an indirect speed-sensitivity stress test, clearly labelled as indirect.
5. Run a locked cross-dataset comparison and participant-bootstrap AUROC differences before selecting a primary candidate.
6. Run attribution/occlusion analysis for the Inception CNN only after the comparison contract is locked.
7. Search official supplements for direct speed records; if unavailable, require measured speed in the independent cohort.
8. Consider conservative augmentation or self-supervised pretraining only after these real-data analyses are complete.

No retraining, label change, exclusion change, or external-data pooling is justified by the pasted roadmap alone.
