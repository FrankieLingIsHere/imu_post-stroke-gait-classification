# gait_cnn stroke adaptation protocol

Locked before model fitting. Upstream commit689cc9baa99e3fdd0be96c6f634280d34f752c17.
Use the actual get_CNN_model function from Linn39/gait_cnn via AST extraction,
Keras3 torch backend on the existing CUDA Python environment. No architectural
substitution: Conv1D32 filters, width5, valid padding, ReLU, GlobalMaxPooling1D,
Dense2 softmax, categorical crossentropy, Adam initial lr.02 and batch32.
Twenty-five maximum epochs; validation-loss early stopping patience3, LR halving
patience2 minimum.001. Restore best validation weights (explicit departure from
upstream's last-weight behavior). Seeds42,137,202; no test-driven hyperparameter
sweep. Upstream currently specifies one convolutional layer.

Task is stroke versus healthy/other pathology, not the upstream visit classifier.
Use the previously selected259 Voisard participants and1348 trials. Fixed LEFT
heel-strike-to-heel-strike cycles, never diagnosis-dependent side selection.
Require ordered adjacent event pairs, next toe-off inside the cycle, and no turn
crossing. Retain malformed/missing coverage. Use all eligible cycles, no arbitrary
per-person cap. Native LB/LF/RF XYZ acceleration and gyro on their shared packet
clock, bounded interpolation as in existing audited loader. Acceleration converted
from m/s² to g. Gyro retained in provider-native units and standardized per channel.
Third-order10Hz Butterworth filtfilt within each finite straight segment, then
Fourier-resample each stride to200 points as supported upstream. No ten-second
requirement or padding. This is annotation-assisted segmentation.

Four prespecified inputs: lower-back acceleration magnitude1 channel; lower-back
acceleration+gyro6; bilateral feet12; all three sensors18. Identical eligible
strides and participants across arms. Multisensor results do not validate a
single-lower-back device. One scaler per fitting split/channel, never selected
using a target label. Do not reproduce upstream class-conditioned normalization.

Original three participant-disjoint outer folds, entire non-stroke pathology
groups held out. Inside each outer training fold, target-stratified fixed20%
validation and20% calibration participants, leaving60% fitting. Validation chooses
epoch/LR only. Calibration chooses threshold at90% empirical stroke sensitivity.
No final refit, to preserve calibration independence. Include fixed.5 results.
Both this split and lack of label-dependent scaling intentionally replace the
upstream subject-specific raw-row splitting recipe.

Training weights give healthy/stroke/other masses.25/.50/.25, equal people per
target, equal trials per person, equal cycles per trial. Validation loss uses the
same hierarchy. Prediction: mean cycle probability within trial then mean trials
within person. No age/device/diagnosis/deficit-side inputs.

36 fits:4 input arms x3 seeds x3 outer folds. Report full available cohort and
matched-device/protocol subset of SAME held-out predictions (not separately fit
models), all seeds and per-pathology counts. Preserve all259 coverage denominators.
Matched subset is descriptive and small. Compare sensor arms to the magnitude
arm, not directly to historical models with different training recipes. A candidate
is promising if every seed reduces neurological FPR>=5pp with no extra stroke
misses or healthy FP versus magnitude, in both reported scopes. Also report
AUROC and tradeoffs when this rule fails. No promotion from reused development
data alone. No claim of original-paper replication, clinical validation or LRP
causal explanation. Save checkpoints, normalization, histories, predictions and
split/source manifests. LRP visualization is separate from predictive validity.
