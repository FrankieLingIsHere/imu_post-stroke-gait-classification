# Specificity-first strategy for false positives

## Current evidence

On the frozen 17-person RevalExo cohort, the current full expanded model assigns probabilities from 0.311 to 0.895 to healthy participants and 0.762 to 0.989 to stroke participants. The highest healthy score is 0.895; four stroke participants are below that score. Thus, a threshold high enough to produce zero observed false positives on this cohort would classify only 6/10 stroke participants as positive. Zero false positives and high stroke sensitivity cannot both be achieved with the current score separation.

## Recommended operating design

1. Keep the model's probability output continuous; do not hard-code 0.5 as a clinical threshold.
2. Select a specificity-first threshold using nested participant-level validation, not the frozen external test. The primary constraint should be an upper confidence-bound false-positive rate, not zero observed errors in a seven-person healthy sample.
3. Use three decisions: likely healthy, indeterminate/confirm, and likely stroke. The indeterminate band should trigger repeat walking measurement or clinician review rather than an automatic stroke label.
4. Report sensitivity at the specificity-first threshold and the complete precision-recall/sensitivity-specificity trade-off.
5. Add healthy hard negatives from age-matched public cohorts and non-stroke mobility-impairment cohorts for specificity testing. Do not pool them blindly as stroke labels.
6. Treat source/domain as a risk factor: retain source-balanced training, but add domain-aware calibration or a source-robust representation only inside development folds.
7. Repeat the final gate on a second independent healthy/stroke wearable cohort. RevalExo has only seven healthy participants, so zero observed false positives there would not establish clinical zero-FP performance.

## What not to do

- Do not tune the threshold on RevalExo.
- Do not oversample synthetic healthy data after the previous negative utility result.
- Do not claim zero false positives from a small external sample.
- Do not remove healthy participants whose gait is difficult for the model; those are precisely the cases needed for specificity improvement.

## Immediate experiment

Run a nested threshold analysis on the real development pool using participant-level out-of-fold probabilities. Produce sensitivity, specificity, NPV, false-positive rate, and abstention rate across thresholds. Then test the chosen specificity-first threshold once on frozen RevalExo and record the result without retuning.

## Development-only participant OOF operating-rule audit (2026-09-01)

Five participant-disjoint folds across the real Voisard, Felius, and Sint development pool generated one held-out probability per participant (`n=314`: 126 healthy, 188 stroke). Within every fold, normalization and source/class-balanced model fitting used the other participants only; RevalExo was excluded. The out-of-fold AUROC was 0.948 and Brier score 0.097.

The rule selection was deliberately hardened after inspecting source strata. A positive ("likely stroke") threshold must have both (a) a pooled 95% Wilson lower bound for healthy specificity of at least 90% and (b) at least 90% *observed* healthy specificity in every source. The most sensitive eligible threshold is **0.78**.

| Source | Healthy / stroke participants | Specificity at 0.78 | Healthy FP | Sensitivity at 0.78 | Stroke FN |
|---|---:|---:|---:|---:|---:|
| Felius | 34 / 129 | 91.2% | 3 | 64.3% | 46 |
| Sint | 20 / 10 | 100.0% | 0 | 60.0% | 4 |
| Voisard | 72 / 49 | 98.6% | 1 | 63.3% | 18 |
| Pooled | 126 / 188 | 96.8% (95% LCB 92.1%) | 4 | 63.8% | 68 |

This threshold can only be described as a **high-specificity referral rule**. It is not acceptable as the sole stroke-screening threshold because the worst-source sensitivity is 60.0%. A uniform "auto-healthy" boundary was not emitted: no threshold simultaneously achieved the 90% pooled sensitivity confidence-bound requirement and 90% observed sensitivity in every source. Consequently, sub-threshold cases must remain indeterminate/require repeat measurement or clinical review until a larger, more representative healthy/stroke cohort supports a safe two-sided triage boundary.

The threshold is now locked for one descriptive RevalExo check. Its external result will be reported without adjustment and will not be used to alter the threshold.

## Locked external RevalExo check (no retuning)

The 0.78 threshold was applied once to the already saved full-expanded prototype participant probabilities (`full_expanded_prototype_revalexo_participant_predictions.csv`). It was not changed after seeing these results.

| Operating threshold | Healthy TN / FP (n=7) | Stroke TP / FN (n=10) | Specificity | Sensitivity | Balanced accuracy |
|---:|---:|---:|---:|---:|---:|
| 0.50 | 1 / 6 | 10 / 0 | 14.3% | 100.0% | 57.1% |
| 0.78 (development locked) | 6 / 1 | 7 / 3 | 85.7% | 70.0% | 77.9% |

The locked high-specificity threshold markedly reduces observed false positives, but it still leaves one healthy false positive and defers/misses three stroke participants if used as a binary action. With only seven external healthy people, this does **not** establish reliable 85.7% specificity. It corroborates the decision not to promise zero false positives and not to use a single threshold as the final clinical pathway. The appropriate next data action is real, age-overlapping healthy and non-stroke hard-negative evaluation; the appropriate modeling action is confidence-aware deferral, evaluated prospectively with that data.
