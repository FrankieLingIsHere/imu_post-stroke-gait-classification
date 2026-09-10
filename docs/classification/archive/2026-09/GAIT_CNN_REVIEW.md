# Linn39 gait_cnn: source review and executed stroke benchmark

Date: 2026-09-09. This is a research adaptation of the released architecture,
not a reproduction of the original paper or an independently validated classifier.

## Finding

The architecture is relevant and has now been trained, not rejected on a wrist
transfer test. Its stride representation retains all 259 previously selected
Voisard participants, with 21,800 usable cycles. Richer sensor inputs improve
discrimination over the same CNN receiving acceleration magnitude alone. However,
neurological false positives remain substantial and no richer-input arm satisfies
the prespecified improvement rule across every seed and both reporting scopes.
This supports further controlled work on stride representations. It does not
support replacing the existing prototype or declaring this architecture exhausted.

## What the upstream project actually provides

The [repository](https://github.com/Linn39/gait_cnn) identifies Zhou, Fischer,
Brahms, Granacher and Arnrich's paper, *Using Transparent Neural Networks and
Wearable Inertial Sensors to Generate Physiologically-Relevant Insights for Gait*,
ICMLA 2022, pages 1274–1280, DOI
[10.1109/ICMLA55696.2022.00204](https://doi.org/10.1109/ICMLA55696.2022.00204).
The [official conference program](https://www.icmla-conference.org/icmla22/IEEE-ICMLA-2022-Conference-Program.pdf)
corroborates its bibliographic identity. The complete paper was not obtained in
this review, so its numerical results and original experimental details are not
claimed as independently checked. The executable code is the principal technical
source here. Its README explicitly says it has changed since the paper.

The [institutional thesis abstract](https://hpi.de/en/arnrich/teaching/fischer/)
describes a related study of 16 young healthy participants performing fatigue and
dual-task conditions with nine sensor locations. It reports feet and sacrum inputs,
including acceleration and angular velocity, and describes different preferred
sensor combinations for within-person and unknown-person testing. That makes this
a relevant gait CNN baseline, but does not establish stroke-versus-other-disease
specificity. The abstract supplies no transferable stroke checkpoint.

We cloned commit `689cc9baa99e3fdd0be96c6f634280d34f752c17` into
`models/research/gait_cnn-689cc9b`, preserving the MIT license. The inspected tree
contains source and example result images, but no trained weight artifact or raw
example signals. This experiment therefore trains from scratch. DUO-GAIT and
STROKE-GAIT are already documented project candidates, not newly discovered data.
The current upstream configuration uses stroke rehabilitation visits; a stroke-only
visit comparison cannot by itself supply healthy controls for our target task.
No new cohort files were downloaded for this experiment.

## Architecture and preprocessing, verified from code

The pinned [model builder](https://github.com/Linn39/gait_cnn/blob/689cc9baa99e3fdd0be96c6f634280d34f752c17/src/models/train_model.py)
constructs a 32-filter, width-five Conv1D with valid padding and ReLU, followed by
global maximum pooling and a two-output softmax dense layer. Additional convolution
layers are supported, but the current configuration selects one. The resulting
parameter counts are 258, 1,058, 2,018 and 2,978 for our 1-, 6-, 12- and 18-channel
inputs. It is a compact classifier, not a large pretrained gait foundation model.

The pinned [feature builder](https://github.com/Linn39/gait_cnn/blob/689cc9baa99e3fdd0be96c6f634280d34f752c17/src/features/FeatureBuilder.py)
uses annotated same-foot initial-contact cycles, supports Fourier resampling to
200 points, and smooths sensor channels using a third-order 10 Hz low-pass filter.
Stride normalization preserves waveform shape in gait phase while removing
absolute stride duration from the time axis. Thus the experiment does not test
whether adding explicit duration or cadence would improve this representation.

Global max pooling retains the strongest detected local pattern but discards its
explicit location. As an architectural inference, this may limit direct encoding
of long-range bilateral phase relationships with only one short convolution.
It is not proof that the network cannot learn useful asymmetric patterns.
LRP is an explanation component of the repository, not evidence of causal or
diagnostic validity. No LRP-based physiological claim is made here.

## Why the original evaluation wrapper needed adaptation

The pinned [main script](https://github.com/Linn39/gait_cnn/blob/689cc9baa99e3fdd0be96c6f634280d34f752c17/src/main_classification_cv.py)
currently compares visit 1 against visit 2 inside individual stroke participants.
Its splits operate on rows within each person. That answers a different question
from recognizing stroke in an unseen person with a potentially unseen pathology.
Using those splits for our diagnostic benchmark would be inappropriate even if
they served the original task's purpose.

There is also a concrete target-dependence problem: `normalize_2d_data` fits a
separate StandardScaler for each target class, and validation/prediction selects
the scaler using the true class. The
[prediction code](https://github.com/Linn39/gait_cnn/blob/689cc9baa99e3fdd0be96c6f634280d34f752c17/src/models/predict_model.py)
uses this feature preparation. An unknown patient's label cannot select their
preprocessing. We repaired this with one fitting-participant scaler per channel.
This finding concerns the inspected code, not an assertion about an inaccessible
paper's reported results.

Likewise, paretic-side segmentation is meaningful in known stroke rehabilitation,
but cannot be a diagnosis-derived input to our unknown-diagnosis classifier. We
use the fixed left foot. Filtering is performed within finite straight segments,
not across concatenated trials or turns. These changes retain the network while
making its measurement and evaluation contract appropriate for this project.

## Executed protocol and fidelity

The [protocol](../../GAIT_CNN_PROTOCOL.md) was written and hashed before fitting.
The runner extracts and executes the actual upstream Keras builder through Python
AST; it does not substitute a vaguely similar PyTorch network. Keras 3.15.1 runs
on the existing PyTorch CUDA environment. Backend differences mean this is not a
bitwise replication of the upstream TensorFlow environment.

We retained Adam learning rate .02, batch size 32, maximum 25 epochs, validation
loss early stopping with patience three, and learning-rate halving with patience
two and minimum .001. We restore the best validation weights, unlike upstream's
default last weights. Actual stopping was at 4–16 epochs. This tests the released
training recipe after task repairs; it does not establish that these optimizer
settings are optimal for stroke classification.

All arms use exactly the same eligible cycles. Native 100 Hz lower-back and foot
acceleration/gyroscope signals share the audited packet clock. Acceleration is
converted to g, gyro retains provider-native units, and each channel is standardized
using fitting participants only. Scaling statistics are calculated on the resampled
cycles, an explicit departure from fitting upstream statistics on raw rows.
No clinical side, age, diagnosis or device identifier enters the network.

Three original outer folds hold out participants and entire non-stroke pathology
groups. Within each outer training fold, separate participant sets provide fitting,
validation and calibration. Calibration sets a threshold targeting 90% empirical
stroke sensitivity. It is not a guarantee of 90% sensitivity in the outer test set.
Training balances target classes, people, trials and cycles. Predictions average
cycles within trials and then trials within participants. Seeds 42, 137 and 202
produce 36 fits across four input arms. The matched subset uses the same held-out
predictions, not separately optimized matched models.

## Results

Ranges below show the three seeds, not confidence intervals. Denominators in the
full cohort are 49 stroke, 72 healthy and 138 other-pathology participants, including
94 neurological controls. Thresholds are selected on calibration participants.

| Input | AUROC | Stroke detected /49 | Healthy FP /72 | Other FP /138 | Neurological FP /94 |
|---|---:|---:|---:|---:|---:|
| Lower-back magnitude | .637–.653 | 44 | 23–26 | 105–108 | 78–81 |
| Lower-back acceleration + gyro | .768–.798 | 44–47 | 14 | 66–77 | 66–77 |
| Both feet acceleration + gyro | .799–.858 | 43–47 | 14–15 | 90–92 | 80–82 |
| Lower back + both feet | .825–.837 | 47–48 | 10–19 | 67–87 | 67–82 |

The combined representation consistently improves overall ranking and stroke
detection over magnitude in this recipe. Feet alone can rank participants well
while still producing many neurological positives at the calibrated threshold.
AUROC and operating-point specificity answer different questions.

The matched-device/protocol subset has 144 participants: all 49 stroke, 19 healthy
and 76 neurological controls. These small healthy counts require particular care.

| Input | Matched AUROC | Healthy FP /19 | Neurological FP /76 |
|---|---:|---:|---:|
| Lower-back magnitude | .358–.383 | 15–18 | 70–72 |
| Lower-back acceleration + gyro | .515–.588 | 13–14 | 65–69 |
| Both feet acceleration + gyro | .612–.731 | 10–12 | 69–72 |
| Lower back + both feet | .643–.666 | 10–13 | 60–71 |

The matched drop is consistent with composition/device sensitivity, but does not
isolate a unique cause: the subset also changes pathology and participant mix.
Held-out pathology tests are development generalization tests within this source,
not independent cross-cohort validation. Repeated use of these development data
also limits claims of an untouched final test.

The locked rule required at least five percentage points lower neurological FPR
without additional stroke misses or healthy FP, for every seed in both scopes.
Lower-back six-channel input passes four of six comparisons; combined input passes
two of six; feet input passes none. No arm meets the complete rule. This is more
informative than calling every arm simply a failure: richer signals help, but the
neurological specificity gain is not yet robust.

These numbers are not a controlled improvement over the historical frozen model
or phase-feature prototype. Those used different representations and fitting
recipes. In particular, the historical 89/138 false-positive count should not be
subtracted from this table and described as a validated model upgrade.

## Verification and remaining work

Three unit tests passed: malformed/turn-crossing cycle exclusion, hierarchical
weights, and agreement of the actual upstream forward pass with an independent
NumPy convolution/pooling/softmax calculation for all four input widths. The saved
evidence verifier confirms 36 fits, finite losses, participant and pathology split
separation, calibration-derived thresholds and source/protocol hashes. Four
checkpoint reload spot checks reproduce saved participant scores within 1e-6
using the original evaluation batch arrangement. A different batch arrangement
showed a roughly 8e-5 score difference in one check; exact batching is retained for
reproduction. Optimizer-state continuation was not validated by these inference
reloads.

The useful next question is whether a validation-only optimizer/early-stopping
comparison improves this stride CNN, with the magnitude and six-channel controls
kept and the outer results hidden during selection. Many fits stopped early under
the upstream .02 learning rate; this warrants investigation, not a retrospective
claim that optimization caused the false positives. Any subsequent experiment
must be separately locked and reported as continued development on reused data.
An independent compatible cohort remains necessary before claiming robust transfer.
Reference-assisted segmentation must also be replaced and validated before a
sensor-only deployment claim. A multisensor result cannot validate one lower-back
sensor. No existing deployed model was replaced.

## Reproduction and evidence files

Run with `C:/Users/frank/.venv-cu130/Scripts/python.exe`:

```text
scripts/classification/benchmark_gait_cnn.py
scripts/classification/verify_gait_cnn.py
-m unittest discover -s tests -p test_gait_cnn.py
```

The benchmark refuses to overwrite its completed decision. Outputs are under
`data/processed/gait_cnn_v1`: cycle and coverage tables, raw hashes, source manifest,
split identities, histories, calibration/test predictions, all seed metrics at
calibrated and fixed .5 thresholds, pathology counts, decision and verification
JSON, and 36 weight/scaler pairs. Existing metadata and raw acquisition are
unchanged. Stride preprocessing and this evaluation are complete. Independent
validation and sensor-only event measurement remain incomplete.
