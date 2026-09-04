# Native healthy-window synthesis

## Why this experiment was changed

Earlier synthesis generated 200-point event-normalized cycles and interpolated them to the classifier's 500-sample window contract. That introduced a preventable representation mismatch. This experiment trains directly on the real MAREA/DUO-GAIT healthy window pool (`500 x 3`, 100 Hz, acceleration magnitude) and generates directly in the same contract.

## Results

The CUDA diffusion run generated 600 MAREA-conditioned and 600 DUO-GAIT-conditioned windows.

| Source | Real mean | Synthetic mean | Real SD | Synthetic SD | Synthetic NN mean | Real-to-real NN mean | Real roughness | Synthetic roughness |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| MAREA | 1.431 | 1.421 | 0.880 | 0.748 | 31.27 | 25.96 | 0.279 | 0.227 |
| DUO-GAIT | 1.462 | 1.449 | 0.914 | 0.800 | 34.41 | 26.45 | 0.312 | 0.302 |

This is a substantial improvement over the previous phase-cycle generator. It removes the 200-to-500 interpolation mismatch, matches source-specific means closely, and nearly matches DUO-GAIT temporal roughness. Mild under-dispersion and excess nearest-neighbour distance remain, so the data is not yet accepted for training.

## Next utility experiment

Test only 5%, 10%, and 20% synthetic-to-real ratios, source-balanced and grouped separately from real participants. Use the current real-only classifier as control and evaluate internal participant-level metrics plus frozen RevalExo AUROC, Brier, balanced accuracy, and healthy false positives. Synthetic samples are admitted only if the complete gate passes.

## Internal ratio selection

The ratio experiment used only Voisard/Felius participant-disjoint folds. RevalExo was not used, preventing the external cohort from becoming a tuning set. The sampler retained equal mass for the four real source-by-class cells and assigned the stated mass equally across the MAREA and DUO-GAIT synthetic healthy conditions.

| Synthetic fraction | Mean AUROC | Mean Brier | Mean balanced accuracy |
|---|---:|---:|---:|
| 0% (real-only control) | 0.9826 | 0.0655 | 0.9112 |
| 5% | 0.9747 | 0.0683 | 0.9210 |
| 10% | 0.9784 | 0.0696 | 0.8982 |
| 20% | 0.9726 | 0.0748 | 0.9016 |

Only 5% improved balanced accuracy, but it lowered AUROC and slightly worsened Brier. Ten and twenty percent are rejected. The 5% condition is a cautious candidate only: repeat it against the real-only control across additional seeds before one predeclared frozen-RevalExo comparison. It is not admitted to final training yet.

## Repeated-seed confirmation

The 0% and 5% conditions were repeated across seeds 42, 43, and 44. Aggregate fold-level results:

| Synthetic fraction | AUROC mean (SD) | Brier mean (SD) | Balanced accuracy mean (SD) |
|---|---:|---:|---:|
| 0% | 0.9777 (0.0154) | 0.0712 (0.0270) | 0.9076 (0.0480) |
| 5% | 0.9731 (0.0204) | 0.0715 (0.0229) | 0.9082 (0.0374) |

The apparent 5% gain is not stable or clinically material: balanced accuracy differs by only +0.0006, while AUROC is lower by 0.0046 and Brier is marginally worse. Direct synthetic healthy enrichment therefore fails the repeated internal utility gate. RevalExo is intentionally not used for another ratio comparison.
