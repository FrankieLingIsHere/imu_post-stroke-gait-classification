# Directional axis convention verified against provider and local files

The nominal lower-back anatomical mapping is now supported: **X vertical,
Y medio-lateral, Z anterior-posterior**. This resolves the documentation question,
not per-trial anatomical calibration or classification validity.

## Provider evidence

The [provider paper](https://www.nature.com/articles/s41597-025-05959-w), Figure 2,
shows the lower-back axes. Its validation section describes initial standing
alignment checks and axis interchanges for database consistency. The local README
and quick-start loader do not document those conventions. The provider's current
[processing code](https://github.com/CyrilVoisard/dataset_gait_1/blob/main/process_data/filter.py)
contains the eighth-order 14-Hz Butterworth filter, without the axis interchange
logic. Thus the previous metadata-only screen was incomplete, not evidence that
the provider had no orientation convention.

## Executed file-level check

All 1,348 selected trials screened. Applied the provider filter to packet-aligned
native acceleration and compared signed axis permutations to processed XYZ.

| Device | Comparison | Trials |
|---|---|---:|
| XSens | Identity +X +Y +Z | 507 |
| XSens | Unsupported length/nonfinite, no mapping inferred | 54 |
| TechnoConcept | Identity +X +Y +Z | 37 |
| TechnoConcept | -X -Y +Z | 750 |

All 1,294 comparable trials match to numerical precision (maximum best RMSE below
2.1e-13 m/s2). This verifies the transformation between the two stored versions,
not independent anatomical truth. Do not generalize a single sign rule to every
TechnoConcept trial. No label-dependent mapping was used.

Initial-second median gravity is X-dominant in 1,347 trials and Z-dominant in one.
This is a screening proxy, not guaranteed standstill or proof of horizontal heading.
It does not validate every participant's mounting alignment. The 54 unsupported
comparisons remain explicitly unresolved instead of being silently excluded from
an eventual cohort experiment.

## Consequence for the next experiment

Directional harmonic ratio may now be tested as a **nominal sensor-aligned ML
feature using Y**, with orientation quality sensitivity analysis. Multiplying Y
by -1 does not change Fourier amplitudes and therefore does not change an
amplitude-based HR. This is distinct from the existing acceleration-magnitude HR.
No need to redo threshold experiments or download raw data.

Before fitting, lock the stride segmentation, odd/even harmonic convention,
minimum signal coverage and treatment of orientation flags. Use existing
participant/pathology folds and sensitivity-preserving comparison. Do not claim
this is fully calibrated anatomical acceleration. Gyro laterality remains a
separate measurement task, where axis signs and calibration do matter.

## Reproducibility and current state

Runner: `scripts/audit_voisard_directional_axes.py`.
Artifacts: `data/processed/directional_axis_v1/axis_audit.csv`, archived provider
article HTML and inspected Figure 2 image. No raw acquisition, classifier fitting,
new diagnostic metric or release change. Axis audit complete. Directional HR
extraction/evaluation remains pending. Prior nested matched combined+phase result
is still 45/49 stroke detected, 62/76 other FP and 13/19 healthy FP.
