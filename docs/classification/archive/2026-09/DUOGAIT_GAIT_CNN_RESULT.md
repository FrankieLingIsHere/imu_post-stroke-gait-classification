# Frozen gait_cnn DUO-GAIT result

> Subsequent execution: [waveform-frame six-channel training and DUO-GAIT evaluation](GAIT_FRAME_RESULT.md) completed and failed its primary gate. Anatomical calibration remains unverified. Historical pending statements below do not mean that this waveform-frame experiment is still pending.
2026-09-09. Completed external healthy-condition test of the lower-back magnitude
arm only. Nine frozen models (three outer folds times three seeds), unchanged
Voisard scalers and calibration thresholds, no fitting or model selection.

All 16 participants retained in all four conditions, 64 sessions, 15,485 cycles
and 576 participant-condition-model predictions. These are repeated observations
of 16 people, not 576 independent subjects. No dataset was downloaded.

| Condition | False positives /16, range across nine models |
|---|---:|
| Single-task control | 1–12 |
| Single-task fatigue | 0–7 |
| Dual-task control | 2–11 |
| Dual-task fatigue | 2–13 |

These are model ranges, not confidence intervals. Fold1 is consistently more
positive than folds0/2, so do not report the best fold as the external result.
Both fitted models and thresholds differ across folds; this does not isolate a
calibration-only cause. Full per-model results and paired changes are saved.

Mean within-person score change for single-task fatigue versus control is
negative in every model (-.120 to -.083). Dual-task control changes range from
-.000155 to +.0508. Thus these observations do not support a blanket claim that
fatigue raises stroke scores. They demonstrate unstable external healthy
specificity in this magnitude model. They neither test neurological specificity
nor estimate stroke sensitivity. This architecture's upstream DUO-GAIT fatigue
task is distinct from our frozen stroke-task transfer test.

## Adapter and verification

Sacral acceleration is already in g, matching the training magnitude after its
Voisard m/s2-to-g conversion. Native128Hz signals are filtered at physical10Hz
within contiguous eligible intervals and Fourier-resampled to200 phase points.
The official event table row describes the interval from `timestamps` to
`ic_samples`, with `fo_samples` inside. All outlier, turning-step, turning-interval
and interrupted flags exclude that row. Timing and duration consistency checks
apply; filtering does not bridge excluded intervals.

Initial verification caught unequal foot/sacrum timestamp arrays. The first pass
is explicitly INVALID in `gait_cnn_duogait_v1/INVALID.txt`. The accepted v2 maps
foot event samples to foot timestamps and then into sacrum time, accepting endpoint
discrepancies at most4ms. It excludes106 unsupported alignments and retains all64
sessions. This is a conservative timestamp adapter, not a claim of independent
biomechanical contact validation. Event/exclusion checks, complete participant
coverage, unique prediction identities and unchanged thresholds passed.

## Directional arms remain pending

The trained six/eighteen-channel models used native Voisard coordinates. Prior
provider/file audits document raw-axis sign differences within that training
source; DUO-GAIT mounting coordinates are different again. A direct XYZ feed is
not an anatomically harmonized comparison. No directional external performance
claim is made. Magnitude is invariant to orthogonal axis changes but remains
sensitive to physical placement, mounting and signal transfer differences.

Next implementation gap: harmonize directional coordinates consistently on both
training and external data using a label-independent measurement contract,
then retrain under locked participant splits. Do not select an external rotation
because it minimizes healthy positives. The new finding qualifies the earlier
multichannel benchmark: it remains a native-coordinate within-source comparison,
not a validated cross-device representation. Existing models are unchanged.

Runner: `scripts/classification/evaluate_duogait_gait_cnn.py`. Accepted outputs:
`data/processed/gait_cnn_duogait_v2/` contains protocol, source/checkpoint hashes,
coverage, cycle intervals, predictions, per-model metrics, paired changes and
verification JSON. Metadata/raw acquisition unchanged; magnitude preprocessing
and evaluation complete; directional preprocessing/evaluation and independent
stroke-cohort validation remain incomplete.
