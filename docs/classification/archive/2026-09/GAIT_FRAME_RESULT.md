# Waveform-frame six-channel experiment

Execution status: complete, 36 fits and18 validation-selected models. The primary
improvement gate failed. Protocol: [locked specification](../../GAIT_FRAME_PROTOCOL.md).

## Results and decision

Ranges below are across three seeds, not confidence intervals. Calibrated
thresholds were chosen on separate participants, targeting90% empirical stroke
sensitivity. The lower-rate recipe was selected for7/9 frame6 models and1/9
magnitude models. This demonstrates that optimizer choice affects validation
performance; it does not demonstrate that optimization caused external errors.

| Full259 cohort | AUROC | Stroke TP/49 | Healthy FP/72 | Other FP/138 | Neurological FP/94 |
|---|---:|---:|---:|---:|---:|
| Magnitude | .635–.644 | 44–45 | 23–26 | 104–108 | 78–79 |
| Waveform-frame6 | .756–.768 | 45–47 | 16–23 | 95–102 | 80–82 |

The frame improves ranking and stroke detection relative to the controlled
magnitude comparator but slightly increases full-cohort neurological positives.
Matched144 AUROC is .546–.571 for frame6 versus .358–.396 for magnitude.
Matched neurological FP are67–69/76 versus70–71/76, and healthy FP11–14/19 versus
15–16/19. Only one of six seed/scope gate comparisons passes. Matched composition
changes alongside device/protocol restriction; this does not identify a unique
hardware or pathology effect. No replacement is supported.

External DUO-GAIT, all16 healthy participants in each condition. Ranges below
span nine selected fold/seed models; they are not independent-cohort replications.

| Condition | Magnitude FP/16 | Frame6 FP/16 |
|---|---:|---:|
| Single-task control | 1–12 | 3–16 |
| Single-task fatigue | 0–9 | 7–16 |
| Dual-task control | 2–14 | 4–14 |
| Dual-task fatigue | 1–13 | 10–15 |

Coordinate invariance does not solve these external false positives. This does
not establish that all anatomical six-axis representations or gait CNNs fail.
The custom per-stride frame can itself lose useful heading/side information or
be unstable, and source/mounting effects remain. Unlike the earlier magnitude-only
test, these results now include an explicitly rotation-equivariant six-channel
representation and validation-selected optimization. Keep that distinction in
future planning; do not repeat this experiment as still pending.

Subsequent execution: [the channel decomposition and false-positive localization](GAIT_CHANNEL_ABLATION_RESULT.md) are complete. Both ablations failed every paired gate; do not restart them from this historical recommendation.

The then-proposed next gap was a controlled decomposition of the six-channel result into
acceleration-only, gyro-only and combined inputs under the same frame and split
contract. That would test whether gyro adds transferable signal or increases
condition/source sensitivity. This is a proposed follow-up, not executed here,
and must be locked separately without selecting settings from DUO-GAIT outcomes.
Independent anatomical calibration and an independent stroke cohort remain open.
Do not interpret this negative gate as proof that sensor orientation is irrelevant.

## What changed

The six-channel input is acceleration XYZ and angular velocity XYZ from one
lower-back IMU. A per-stride waveform frame replaces native sensor coordinates.
Mean acceleration defines approximate vertical. Principal horizontal acceleration
defines a motion axis, signed by its strongest absolute projection. Cross product
defines the remaining axis. Acceleration and gyro receive the same proper rotation.
This is a custom rotation-equivariant representation, not independently calibrated
anatomical forward/sideways motion. It deliberately removes absolute mounting
orientation information. It does not remove physical placement or attachment effects.

The largest horizontal eigenvalue can be close to the second, making the motion
axis unstable. Sign choice can also be unstable near equally strong opposite
excursions. These are measurement limitations, not established error causes.
Zero-motion/unidentifiable frames are rejected explicitly. No tested stride was
rejected: all21,800 Voisard cycles from259 participants and15,485 DUO-GAIT cycles
from16 participants/four conditions remain. Minimum relative eigenvalue gaps were
.00487 and .00412 respectively. Mean-acceleration magnitudes span .863–1.237g in
Voisard and .511–1.153g in DUO-GAIT, emphasizing that dynamic averages are not
independent static gravity calibration. No quality feature enters the classifier.

Two unit tests establish proper-rotation invariance and vector-norm preservation
on synthetic data, and rejection of an unidentifiable static frame. A further proper-rotation check on218 actual cycles reproduced the frame exactly at float32 output precision. These checks do not
establish anatomical validity or clinical classification benefit.

## Controlled comparison

Actual upstream Keras CNN, same participant/pathology folds and training weights,
separate fitting/validation/calibration participants, no refitting. Magnitude and
six-channel frame each have two fixed training recipes and three seeds. Minimum
weighted validation loss selects recipe/weights. Calibration participants supply
the90%-empirical-stroke-sensitivity threshold. Both recipes' histories and weights
are preserved. No external result selects a recipe or rotation.

DUO-GAIT sacral six-axis signals use the previously corrected timestamp-mapped
cycle intervals. Acceleration is in g and gyro is converted degrees/s to radians/s.
Physical10Hz filtering at128Hz precedes200-point Fourier resampling; the frame
is calculated after resampling in both sources. Existing Voisard inputs are g
and provider-native gyro units supported as radians/s by prior turn-integral
checks. No new bias correction is applied to either source.

These are reused development cohorts. Held-out neurological pathologies and
DUO-GAIT stress testing are valuable checks but not untouched cross-source stroke
validation. Prior native-six-channel scores are contextual: a difference from
them cannot isolate the frame effect because the new experiment also selects
between two training recipes. The controlled comparator here is magnitude under
the same new recipe-selection procedure.

Cycle boundaries still come from reference foot-event annotations. A lower-back-only deployment requires a separately validated event extractor; this experiment does not supply that measurement validation.

## Artifacts

`scripts/classification/benchmark_gait_frame.py` and `verify_gait_frame.py`;
outputs in `data/processed/gait_frame_v1/`. Metadata and raw acquisition unchanged.
Frame preprocessing and training/evaluation complete. No new acquisition or
deployment occurred. Two unit tests passed, plus the218-real-cycle rotation check.
The evidence verifier checked36 fit artifacts,18 recipe selections against
validation minima, participant/pathology split separation, calibration threshold
provenance, source hashes,1,554 held-out predictions and1,152 external predictions.
Two selected checkpoints were reloaded and compared across the first test fold.
Maximum score discrepancies were1.97e-6 for magnitude and8.35e-7 for frame6, with
zero changed calls. The initial1e-6 numerical tolerance was exceeded by magnitude;
the verification records a1e-5 tolerance and unchanged decisions rather than
claiming bitwise identity. Optimizer-state training continuation was not tested.
