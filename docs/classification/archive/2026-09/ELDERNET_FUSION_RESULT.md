# ElderNet feature fusion: completed comparison

Executed 2026-09-09 under the [locked protocol](../../ELDERNET_FUSION_PROTOCOL.md).
Pretrained ElderNet feature fusion failed all four advancement comparisons.
The existing released models remain unchanged.

| Scope / arm | AUROC | Stroke detected | Healthy FP | Neurological FP | All other FP |
|---|---:|---:|---:|---:|---:|
| Available / main only | .707 | 44/44 | 6/12 | 49/71 | 58/90 |
| Available / random fusion | .700 | 42/44 | 5/12 | 59/71 | 63/90 |
| Available / pretrained fusion | .699 | 41/44 | 6/12 | 61/71 | 66/90 |
| Matched / main only | .860 | 38/44 | 1/4 | 21/57 | 21/57 |
| Matched / random fusion | .573 | 40/44 | 1/4 | 38/57 | 38/57 |
| Matched / pretrained fusion | .677 | 40/44 | 2/4 | 45/57 | 45/57 |

The matched main-only arm's lower FP count comes with six missed strokes; do not
claim a solved specificity problem or a model improvement from its AUROC alone.
Pretrained fusion detects two more strokes there but adds 24 neurological FP.
In the full available subset, it both misses more strokes and produces more FP.

## Implementation and verification

18 CUDA fits, three arms over the same three outer folds and two scopes. Each fit
used six epochs and 30 steps/epoch. The main branch is a newly trained compact
LowerBackDomainNet feature extractor, **not the frozen 15-member release ensemble**.
Each native ten-second interval supplies two five-second magnitude inputs at
100 Hz to the main branch, and actual XYZ resampled to 30 Hz to ElderNet.
Magnitude is computed from native XYZ after conversion from m/s² to g. Its
normalization uses fitting participants only and is identical across arms.

The main branch's two 64-dimensional vectors are averaged and LayerNorm-normalized.
Fusion concatenates this with a normalized 128-dimensional ElderNet representation.
The new binary head is trained jointly with the main branch and ElderNet's layer5
and FC layers. ElderNet layers1-4 and running BatchNorm statistics remain frozen.
No gait-speed prediction enters the classifier. Random-fusion controls auxiliary
architecture/input capacity under the same late-layer training policy.

Separate calibration participants supply no gradients. Calibration thresholds
target 90% stroke sensitivity, with no refit or test-driven tuning. Verified exact
split identity against the partial-adaptation experiment, prediction membership,
and threshold provenance. All 18 frozen/trainable-state checks passed. Three
existing unit/shape/calibration-split regression tests passed. A read-only NumPy
index warning occurred during fitting-statistic selection; that index is never
written to and does not change the numerical procedure.

Artifacts under `data/processed/eldernet_fusion_v1/`: source manifest, coverage,
splits, loss curves, state/normalization checks, calibration/test predictions,
thresholds, metrics, paired calls, per-pathology counts, decision and verification.
Runner: `scripts/classification/fuse_eldernet_lower_back.py`.

## Boundaries and decision

146/259 people contribute 1,785 complete ten-second walking windows. Only 12/72
healthy people are retained; the matched subset contains 105 people and only four
healthy people. All259 remain in the coverage ledger. Missing people are not
counted negative. This selected subset, small calibration groups and single seed
limit precision. Event annotations still determine walking intervals.

This is within-Voisard participant/pathology-held-out evaluation, not independent
cross-source validation. A failed fixed fusion recipe does not prove every fusion
method impossible, but provides no justification for promoting this one. Do not
repeat fusion as an unexecuted suggestion. Address duration/coverage compatibility
before another pretrained-model comparison on the intended cohort.

No new metadata, signals or model downloads. Reconstruction/preprocessing and
fusion training/evaluation complete. Existing checkpoints unchanged. Full end-to-end
ElderNet unfreezing and independent validation remain unexecuted.
