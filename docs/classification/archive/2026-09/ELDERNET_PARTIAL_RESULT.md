# Partial ElderNet adaptation: completed comparison

> Follow-up: [feature fusion](ELDERNET_FUSION_RESULT.md) is now completed and
> failed its advancement criteria. The unexecuted-fusion statements below are
> historical to this partial-adaptation report.

Executed 2026-09-09 under the [pre-fit protocol](../../ELDERNET_PARTIAL_PROTOCOL.md).
Unfreezing the last convolutional stage and FC representation improved AUROC over
the simultaneously trained frozen control, but did not deliver the required
specificity improvement while retaining stroke detection. No model promoted.

| Scope / arm | AUROC | Stroke detected | Healthy FP | Neurological FP | All other FP |
|---|---:|---:|---:|---:|---:|
| Available / pretrained frozen | .596 | 42/44 | 8/12 | 63/71 | 82/90 |
| Available / pretrained partial | .719 | 39/44 | 7/12 | 61/71 | 65/90 |
| Available / random partial | .604 | 42/44 | 6/12 | 61/71 | 61/90 |
| Matched / pretrained frozen | .478 | 44/44 | 4/4 | 56/57 | 56/57 |
| Matched / pretrained partial | .642 | 41/44 | 4/4 | 51/57 | 51/57 |
| Matched / random partial | .516 | 38/44 | 3/4 | 44/57 | 44/57 |

The matched random control misses more strokes than the partial pretrained model;
its lower FP count therefore cannot be interpreted in isolation as a better model.
The full-subset adapted model's total other-FP reduction versus frozen includes
orthopedic controls; neurological FP only decreases by two people. Both scopes
fail the locked advancement rule against both controls.

## What was trained and checked

18 CUDA training fits, six epochs and 30 steps per epoch each. Layers 1-4 stayed
frozen. Layer5 and the FC representation were trainable in the partial arms, and
a new linear stroke head was trained in all arms. All BatchNorm running statistics
remained fixed. The random control uses the same architecture and trainable layers,
not a fully trained-from-scratch network. Neither arm uses the original speed head.

The same initial new head and participant/trial/window sampling were used across
arms. Each outer training fold reserved separate participants for threshold
calibration; those people supplied no gradients. Outer participant and non-stroke
pathology holdouts were enforced. Thresholds targeted 90% calibration stroke
sensitivity, with no refit or test-driven threshold change. Saved predictions and
split IDs were cross-checked for all arms.

All 18 frozen/late-state checks passed. Three regression tests passed for physical
units, input windows and disjoint calibration splits with small target groups.
Loss traces, splits, calibration predictions, thresholds, test predictions, paired
calls, per-pathology counts and decisions are saved in
`data/processed/eldernet_partial_v1/`. Existing models and checkpoints are unchanged.

## Interpretation and limitations

This is evidence that partial adaptation can improve discrimination relative to
this frozen neural-head control. It does not establish a reliable stroke-specific
representation, a clinical operating point or a gain over the deployed prototype.
The previous frozen experiment used logistic regression and nested OOF thresholds;
its numbers are not an attribution baseline for this training recipe. The frozen
control in the table above was trained alongside the partial models.

Coverage is unchanged: 1,785 actual XYZ windows from 146/259 participants, including
12/72 healthy people; matched subset 105 participants, only four healthy. The
ten-second requirement causes substantial selection. Short bouts were not padded,
stretched or concatenated across turns. All 259 remain in the coverage ledger.
Calibration stroke groups are small, and single-seed results have high uncertainty.
This is within-Voisard evaluation; no new independent cross-source validation.

No fusion experiment was performed. Do not automatically add fusion or repeat
epochs after this result. A broader-coverage temporal input contract remains the
main prerequisite for evaluating this transfer approach on the intended cohort.

Metadata and raw acquisition unchanged. Existing windows reconstructed with verified
raw hashes and m/s²-to-g conversion. Partial adaptation and held-out evaluation
complete. Full end-to-end unfreezing, feature fusion and independent validation
remain unexecuted.
