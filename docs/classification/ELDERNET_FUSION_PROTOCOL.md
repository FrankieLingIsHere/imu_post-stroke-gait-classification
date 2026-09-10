# ElderNet feature fusion protocol

Locked before fitting, 2026-09-09. Compare the compact LowerBackDomainNet feature
extractor alone, plus a random ElderNet branch, and plus a pretrained ElderNet
branch. This is a newly trained single-network comparator, not the released
15-member ensemble. The initial main-branch weights and sampling are identical.

Reuse corrected native XYZ windows and the partial-adaptation participant and
calibration splits. The main branch receives acceleration magnitude in g at
100 Hz as the two consecutive five-second halves of each ten-second window;
average their 64-dimensional features. Normalize magnitude using fitting-window
mean/SD only. The ElderNet branch receives the same interval's actual XYZ in g
resampled to 30 Hz. Layers1-4 and all ElderNet BatchNorm statistics stay fixed;
layer5 and the 128-dimensional FC representation are adapted. No speed output.

Normalize each feature vector with non-affine LayerNorm, concatenate 64+128
features for fusion, and train a linear binary head. The main-only arm has the
same feature normalization and a 64-dimensional head. Main and fused heads start
at zero for matched initial logits. Main branch BatchNorm uses fitting batches
only and is in eval mode for calibration/testing.

Keep partial-adaptation settings: six epochs, 30 steps, batch32, AdamW decay1e-4,
main/head lr1e-3, ElderNet late lr1e-4, clipping1, same single seed and hierarchical
target/participant/trial/window sampler. Hold out calibration people from gradients,
target 90% calibration stroke sensitivity, no refit. No hyperparameter sweep.

Full available and matched available scopes retain 146 and 105 people, respectively.
Coverage for all259 remains explicit. Outer participant/pathology holdouts remain.
Advancement requires pretrained fusion to reduce neurological FPR >=5pp with no
extra stroke misses or healthy FP against BOTH controls in BOTH scopes. No release
promotion on this single-seed subset experiment alone. Save outputs and state checks.
This does not resolve ten-second coverage bias or establish cross-source validation.
