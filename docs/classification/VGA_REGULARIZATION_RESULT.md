# Controlled regularization and warm-up: executed results

2026-09-09. All 27 fits completed 40 epochs. This tests clinician-observed gait impairment (VGA 0 versus 1-4), separately from stroke diagnosis. No existing model was replaced.

**Result: neither tested change gives a consistent reduction in false alerts.** Warm-up slightly improves full-population AUROC over the cosine control in all three seeds, but increases normal-rated alerts in two seeds. Weight decay corrects none of the control's normal-rated false alerts and introduces two additional alerts in seed 42. Every setting fails the fixed operating-point gate. Lower validation loss did not provide a reliable screening improvement.

The previous VGA recipe had full AUROC 0.790-0.797, versus 0.769-0.784 across these new settings. That is historical context, not an isolated comparison of regularization: the schedule and recipe-selection procedure also differ. The controlled contrasts here are decay versus fixed and warmup versus fixed.

## Design and actual settings

The [protocol](VGA_REGULARIZATION_PROTOCOL.md) was saved and hashed before fitting. Three settings, three seeds (42, 137, 202), three participant-disjoint outer folds. The same 248 earliest-session participants, 84 normal-rated and 164 impaired-rated, were used in all settings. Eleven missing ratings remain unknown in the coverage ledger. Labels and participant metadata match the [previous VGA baseline](VGA_SCREEN_RESULT.md).

The actual upstream CNN remains Conv1D(32, kernel 5, ReLU), global max pooling and a two-class softmax. Inputs are six lower-back accelerometer/gyroscope channels in the existing waveform frame, with reference-assisted stride segmentation and 200 samples per cycle. Scaling uses fitting participants only. Class, participant and trial weighting is unchanged.

All settings use Adam, batch size 32 and a cosine learning-rate schedule from 0.001 to 0.00001 over 40 epochs. `fixed` has zero weight decay. `decay` changes only decoupled weight decay to 0.01, including biases. `warmup` has zero weight decay and multiplies the first five scheduled rates by (epoch+1)/5, starting at 0.0002. Schedules match from the fifth epoch onward. No early stopping, dropout, augmentation or gradient clipping was used. Warm-up changes learning rate, not a separate gradient operation.

Minimum validation-loss checkpoints are evaluated. Calibration alone sets the strict float32 cutoff for at most 10% empirical normal-rated alerts. No held-out or DUO-GAIT score selects epochs, thresholds or a winning setting. The gate is normal-rated FPR <=10% and impairment sensitivity >=70% in every seed. These are project prototype criteria, not clinical standards.

## Held-out participant results

Each row pools the three outer folds, with every participant appearing once per seed and setting. Counts preserve the tradeoff between false alerts and missed impairment. Seeds reuse participants and are not independent cohorts.

### Full population

| Setting | Seed | AUROC | Normal false alerts | Impaired detected | Healthy, VGA 0 false alerts |
| --- | --- | --- | --- | --- | --- |
| decay | 42 | 0.778 | 18/84 (21.4%) | 98/164 (59.8%) | 9/65 (13.8%) |
| decay | 137 | 0.769 | 16/84 (19.0%) | 87/164 (53.0%) | 7/65 (10.8%) |
| decay | 202 | 0.778 | 17/84 (20.2%) | 102/164 (62.2%) | 8/65 (12.3%) |
| fixed | 42 | 0.777 | 16/84 (19.0%) | 96/164 (58.5%) | 7/65 (10.8%) |
| fixed | 137 | 0.769 | 16/84 (19.0%) | 91/164 (55.5%) | 7/65 (10.8%) |
| fixed | 202 | 0.779 | 17/84 (20.2%) | 101/164 (61.6%) | 8/65 (12.3%) |
| warmup | 42 | 0.778 | 19/84 (22.6%) | 95/164 (57.9%) | 9/65 (13.8%) |
| warmup | 137 | 0.779 | 15/84 (17.9%) | 89/164 (54.3%) | 7/65 (10.8%) |
| warmup | 202 | 0.784 | 19/84 (22.6%) | 103/164 (62.8%) | 9/65 (13.8%) |

### Matched population

| Setting | Seed | AUROC | Normal false alerts | Impaired detected | Healthy, VGA 0 false alerts |
| --- | --- | --- | --- | --- | --- |
| decay | 42 | 0.669 | 14/28 (50.0%) | 77/110 (70.0%) | 5/12 (41.7%) |
| decay | 137 | 0.642 | 13/28 (46.4%) | 69/110 (62.7%) | 4/12 (33.3%) |
| decay | 202 | 0.668 | 12/28 (42.9%) | 82/110 (74.5%) | 3/12 (25.0%) |
| fixed | 42 | 0.672 | 12/28 (42.9%) | 76/110 (69.1%) | 3/12 (25.0%) |
| fixed | 137 | 0.646 | 13/28 (46.4%) | 72/110 (65.5%) | 4/12 (33.3%) |
| fixed | 202 | 0.682 | 12/28 (42.9%) | 81/110 (73.6%) | 3/12 (25.0%) |
| warmup | 42 | 0.656 | 16/28 (57.1%) | 75/110 (68.2%) | 6/12 (50.0%) |
| warmup | 137 | 0.680 | 12/28 (42.9%) | 70/110 (63.6%) | 4/12 (33.3%) |
| warmup | 202 | 0.687 | 15/28 (53.6%) | 80/110 (72.7%) | 5/12 (41.7%) |

Gate-passing settings: **none**. No automatic promotion follows this reused development benchmark.

## Validation and training duration

![Training and validation curves for every fold and seed](../../data/processed/vga_regularization_v1/training_curves.png)

| arm | best_epoch_min | best_epoch_max | best_after_patience8 | best_at_epoch40 |
| --- | --- | --- | --- | --- |
| decay | 1 | 21 | 1 | 0 |
| fixed | 1 | 21 | 0 | 0 |
| warmup | 5 | 24 | 1 | 0 |

Two of 27 runs show late recovery. None selects epoch 40. The substantial train/validation separation, especially in fold 0, is consistent with overfitting. These results do not support insufficient epochs as a sufficient explanation of the remaining false alerts.

| run | simulated_patience8_stop | best_epoch | minimum_before_stop | minimum_full |
| --- | --- | --- | --- | --- |
| warmup_fold1_seed137 | 15 | 22 | 0.585531 | 0.581231 |
| decay_fold1_seed202 | 11 | 19 | 0.571689 | 0.566356 |

`decay` versus `fixed`: lower best validation loss in 4/9 paired fits. Mean loss difference -0.00184, range -0.01453 to +0.00768. These are descriptive comparisons, not an independent significance test.

`warmup` versus `fixed`: lower best validation loss in 6/9 paired fits. Mean loss difference -0.00325, range -0.02435 to +0.02494. These are descriptive comparisons, not an independent significance test.

The patience-eight stopping point is simulated on each completed run. A later best checkpoint is evidence that this stopping rule would have missed recovery on the new cosine schedule. It is not an exact counterfactual for the previous ReduceLROnPlateau recipe. Forty completed epochs do not prove convergence beyond the tested budget. Full train/validation histories and final-five-epoch changes are saved.

## Paired changes in held-out calls

Compared with `fixed`, positive-to-negative corrects a false alert for normal-rated people but loses a detection for impaired-rated people. Negative-to-positive has the opposite effect. This exposes changes that net counts can hide.

| seed | arm | label | n | positive_to_negative | negative_to_positive |
| --- | --- | --- | --- | --- | --- |
| 42 | decay | normal | 84 | 0 | 2 |
| 42 | decay | impaired | 164 | 0 | 2 |
| 42 | warmup | normal | 84 | 1 | 4 |
| 42 | warmup | impaired | 164 | 4 | 3 |
| 137 | decay | normal | 84 | 0 | 0 |
| 137 | decay | impaired | 164 | 4 | 0 |
| 137 | warmup | normal | 84 | 2 | 1 |
| 137 | warmup | impaired | 164 | 4 | 2 |
| 202 | decay | normal | 84 | 0 | 0 |
| 202 | decay | impaired | 164 | 0 | 1 |
| 202 | warmup | normal | 84 | 1 | 3 |
| 202 | warmup | impaired | 164 | 3 | 5 |

## Impairment severity

Counts below span the three seeds. VGA 4 contains only two people and cannot support a general severity-performance claim.

| arm | vga | n | min_detected | max_detected |
| --- | --- | --- | --- | --- |
| decay | 0.0 | 84 | 16 | 18 |
| decay | 1.0 | 62 | 20 | 31 |
| decay | 2.0 | 63 | 37 | 39 |
| decay | 3.0 | 37 | 28 | 30 |
| decay | 4.0 | 2 | 2 | 2 |
| fixed | 0.0 | 84 | 16 | 17 |
| fixed | 1.0 | 62 | 22 | 30 |
| fixed | 2.0 | 63 | 38 | 39 |
| fixed | 3.0 | 37 | 28 | 30 |
| fixed | 4.0 | 2 | 2 | 2 |
| warmup | 0.0 | 84 | 15 | 19 |
| warmup | 1.0 | 62 | 21 | 32 |
| warmup | 2.0 | 63 | 37 | 40 |
| warmup | 3.0 | 37 | 28 | 29 |
| warmup | 4.0 | 2 | 2 | 2 |

## DUO-GAIT stress test

Sixteen people per condition, nine fold/seed models per setting. These are alert-count ranges, not confidence intervals or verified VGA false-positive rates: DUO-GAIT has no matching VGA labels and was already used in development. It cannot establish external impaired-case sensitivity.

| arm | condition | n | min_alerts | max_alerts |
| --- | --- | --- | --- | --- |
| decay | OG_dt_control | 16 | 0 | 4 |
| decay | OG_dt_fatigue | 16 | 3 | 7 |
| decay | OG_st_control | 16 | 0 | 5 |
| decay | OG_st_fatigue | 16 | 1 | 6 |
| fixed | OG_dt_control | 16 | 0 | 4 |
| fixed | OG_dt_fatigue | 16 | 3 | 7 |
| fixed | OG_st_control | 16 | 0 | 5 |
| fixed | OG_st_fatigue | 16 | 1 | 6 |
| warmup | OG_dt_control | 16 | 0 | 5 |
| warmup | OG_dt_fatigue | 16 | 2 | 8 |
| warmup | OG_st_control | 16 | 1 | 5 |
| warmup | OG_st_fatigue | 16 | 0 | 6 |

## Verification and reproducibility

The verifier checks 27 complete finite 40-epoch histories, checkpoint selection, the exact learning-rate schedules, unchanged source hashes, baseline label identity, all four participant-role separations, calibration membership and alert budgets, exported calls, metrics and the gate decision. Three checkpoint spot checks (fold 0, seed 42, all settings) reproduce scores within 1e-5 with zero changed calls. Maximum spot-check error: 5.93e-07. Two unit tests separately check the schedule and an actual zero-gradient Keras Adam update, confirming that decoupled weight decay operates.

Use `C:/Users/frank/.venv-cu130/Scripts/python.exe` with the following scripts in order. The training runner refuses to overwrite a completed experiment.

```text
scripts/classification/benchmark_vga_regularization.py
scripts/classification/verify_vga_regularization.py
scripts/classification/report_vga_regularization.py
-m unittest discover -s tests -p test_vga_regularization.py
```

Artifacts: `data/processed/vga_regularization_v1/` contains checkpoints, fold scalers, manifests, label coverage, predictions, calibration, metrics, severity, external alerts, training dynamics, paired comparisons and the post-run Python/package/GPU environment record.

## Limits and project status

This isolates one weight-decay setting and one warm-up duration. It does not test every regularizer or establish a unique cause of false positives. Architecture, subjective labels, small calibration groups, disease/device composition and measurement transfer remain possible limitations. Repeated development on the same outer folds limits claims of independent generalization.

Metadata and raw acquisition are unchanged. Previously verified labels and preprocessing are reused. This training/evaluation comparison is complete. Independent positive-cohort validation, sensor-only event extraction and stroke-specific diagnostic validity remain unresolved.
