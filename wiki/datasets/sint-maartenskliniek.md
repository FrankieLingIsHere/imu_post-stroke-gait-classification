---
type: dataset
population: "20 healthy controls and 10 people with stroke"
sensors: "Xsens Awinda: lumbar, bilateral feet, plus shank/sternum exports"
role: "paired development source; original lower-back 6-DoF adapter verified"
---

# Sint Maartenskliniek IMU Gait Analysis

The public `IMU_GaitAnalysis` release provides paired healthy/stroke Xsens
gait recordings with a release-defined `lumbar` sensor and bilateral foot
sensors. In this project it first served as a locked external examination, then
was admitted into a separately labelled Felius+Voisard+Sint prototype training
sensitivity stream. It is therefore **development data**, not a valid external
test for the expanded prototype.

## Lower-back 6-DoF contract (audited 2026-09-02)

`26_sint_6dof_lower_back_adapter_audit.ipynb` read every locally mapped trial
through the release's `sensorspec.json.txt`, rather than hard-coding a guessed
file location. All 79 mapped trials from 30 people passed:

- the named lumbar export is the release mapping ending `00B40A8D.txt`;
- all have `Acc_X/Y/Z` and `Gyr_X/Y/Z` with finite values;
- lumbar packets overlap both foot exports at least 99.9%; and
- the release-defined Vicon-to-Xsens mapping and trial labels are retained.

The audit found a real preprocessing exception: the authors' own importer
identifies the two GRAIL trials for healthy `900_V_01` as 40 Hz and resamples
them to 100 Hz. The 2MWT export for that participant is not part of that
exception. Any new Sint tensor must reproduce this handling rather than assume
100 Hz universally.

## Versioned lower-back tensor

`27_materialize_sint_lower_back_accel_gyro.ipynb` created, without overwriting
the existing three-channel magnitude tensor:

- `data/processed/sint_lower_back_accel_gyro_windows_v1_float32.npy`;
- shape `(4053, 500, 2)` with channels `[LB acceleration magnitude (g), LB
  gyroscope magnitude (deg/s)]`;
- `3,069` healthy windows from 20 people and `984` stroke windows from 10
  people; and
- packet-intersection synchronisation before windowing; resampling only the
  two documented 40 Hz trials.

Acceleration is converted m/s²→g and Xsens gyroscope rad/s→deg/s so its
numerical convention matches the established Voisard lower-back loader. This
does not establish that devices, placement, task, or signal filtering are
clinically equivalent; every model comparison still needs fold-fitted
normalisation and source-held-out evidence.

## Three-source lower-back transport result

The GPU-executed `28_lower_back_6dof_three_source_transport_benchmark.ipynb`
held out one complete source at a time and compared lower-back acceleration
alone against acceleration+gyroscope across seeds 42, 137, and 202. It used
the same source/class-balanced sampling, network, epochs, participant-level
aggregation, and training-fold-only normalisation for both views.

Adding gyroscope was not transport-stable:

| Held-out source | Acceleration AUROC | Acceleration + gyroscope AUROC | Key implication |
|---|---:|---:|---|
| Felius | 0.850 | 0.859 | Small discrimination gain, but worse Brier score (0.178→0.270). |
| Sint | 0.870 | 0.772 | Material degradation: healthy specificity 0.750→0.433 and Brier 0.157→0.287. |
| Voisard | 0.892 | 0.864 | AUROC loss, despite a modest healthy-specificity increase (0.611→0.681). |

A bounded released-pipeline-inspired low-pass check (17 Hz acceleration,
15 Hz gyroscope) did **not** cure the Sint failure (AUROC 0.763, Brier 0.257).
This rules out a simple unfiltered-noise explanation under the current
magnitude representation. It does not invalidate Sint or gyroscope gait
information; it means unadapted pooled gyroscope magnitude is not yet a safe
replacement for the acceleration-only lower-back baseline.

## Current role

Keep Sint in the existing three-channel acceleration-magnitude prototype under
its documented sensitivity-training status. Keep the lower-back acceleration
model as the primary minimal-sensor research track. The new 6-DoF tensor is a
versioned resource for future source-adapter or self-supervised representation
work, not an automatically admitted feature set.
