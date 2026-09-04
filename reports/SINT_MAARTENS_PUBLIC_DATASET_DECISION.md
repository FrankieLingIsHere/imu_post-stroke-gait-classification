# Sint Maartenskliniek public dataset: use decision

## Decision

Do **not** immediately merge this dataset into the primary training set.

Use it first as a **locked, independent external examination cohort**. After that examination is frozen, run one separately labelled sensitivity experiment in which compatible trials may be added to development training. The sensitivity experiment must never replace the locked external result.

## Why this is the safest useful decision

The public release is independent of the current Felius + Voisard development pool and contains raw Xsens sensor files. The repository audit found:

| Property | Finding |
|---|---|
| Stroke participants | 10 `900_CVA_##` folders |
| Healthy participants | 20 `900_V_##` folders |
| Raw modality | Xsens `.mtb` and exported `.txt` sensor files |
| Additional reference | Vicon files are included for many trials |
| Trial conditions | Regular/irregular gait, self-paced/fixed-speed conditions are described by the associated study |
| Public source | Zenodo release v1.1.0 and GitHub repository |

## Post-download audit

The archive was downloaded and extracted on 2026-08-25. Its published MD5 matched exactly (`68ad912e8f8345ffa33ae6a923d0e6f6`). The extracted release contains 10 CVA/stroke participant folders, 20 healthy-control folders, 100 MTB trial files, 693 exported sensor text files, and 150 Vicon files.

The Xsens exports provide acceleration, free acceleration, gyroscope, magnetometer, quaternion and orientation columns. The included sensor specification identifies `leftfoot`, `rightfoot`, `lumbar`, `leftlateralankle`, `rightlateralankle`, and `sternum`, making a defensible lower-back plus bilateral-foot mapping plausible. However, the project still needs to verify export units, exact sampling frequency, trial-condition selection, and axis/sign handling before evaluation. This is a compatibility candidate, not yet a model-ready tensor.

The first raw-export audit is now complete (`scripts/audit_sint_maartenskliniek.py`). All 30 participants have complete lumbar/left-foot/right-foot exports, covering 99 complete trials. The three selected sensors have matched row counts within each trial; trial lengths range from 1,969 to 23,372 samples, with a median of 12,213 samples. This confirms usable coverage, but not yet semantic equivalence to the project’s 5-second window contract. The audit artifact is `data/processed/sint_maartenskliniek_export_audit.csv`.

The release's own `gaittool` source identifies the Xsens/Awinda default as 100 Hz and uses the `Acc_X/Y/Z` fields as sensor-frame acceleration. The published validation code also supplies explicit Vicon-to-Xsens export mappings and distinguishes regular, irregular, self-paced and fixed-speed trials. The external-only materializer now uses that provenance manifest rather than every complete export folder. It converts `Acc_X/Y/Z` from m/s² to g, computes LB/LF/RF acceleration magnitudes, and creates 500-sample windows with a 250-sample hop. It produced 3,995 finite windows from 30 participants (3,011 healthy; 984 stroke). These outputs are explicitly marked `external_candidate_only` and have not entered model fitting or normalization: `data/processed/sint_maartenskliniek_external_windows_float32.npy` and `data/processed/sint_maartenskliniek_external_window_metadata.csv`.

This is a preprocessing result, not an external performance result. The one unavailable mapped export is `900_V_pp11_SP01.c3d` → `900_V_11/exported011`; the local archive contains `exported001`, `exported012`, and `exported013` for that participant but no `exported011`. It is excluded rather than guessed or substituted. The remaining 30 participants and 75 available mapped trials are sufficient to proceed to the frozen examination, with this missing trial disclosed.

The triaxial healthy reference archive was also downloaded and extracted. It contains 60 participant metadata rows and 527 CSV signal files with lower-back and foot recordings plus age and walking-speed metadata. It is healthy-only and therefore cannot increase supervised stroke labels; it is reserved for healthy-domain/speed robustness and optional unlabeled pretraining.

The dataset increases participant coverage, but it does not solve the small-stroke-cohort problem by itself. Adding 10 stroke participants can improve representation, while also introducing a new sensor/site/protocol domain. If it is pooled before an independent test is frozen, the project loses the cleanest evidence of transportability.

## Two pre-registered roles

### Role A — primary external examination

Before any Sint Maartenskliniek samples enter fitting, normalization, calibration, threshold selection, augmentation, or model selection:

1. Audit the trial and sensor schema.
2. Map only defensible lower-back and bilateral-foot acceleration channels into the established `LB/LF/RF` contract.
3. Preserve participant IDs and split at participant level.
4. Apply the already locked Inception and MiniROCKET pipelines without tuning on this cohort.
5. Report participant-level AUROC, balanced accuracy, sensitivity, specificity, Brier score, calibration, and errors by walking condition.

This result is the strongest public-only test of independent binary generalisation currently available to the project.

### Role B — sensitivity training experiment

Only after Role A is frozen, run a separate experiment with:

- Felius + Voisard + Sint Maartenskliniek;
- source-balanced sampling so the new cohort cannot dominate through trial count;
- participant-disjoint outer folds;
- source-stratified reporting;
- training-only normalization;
- no use of Role A predictions for tuning;
- comparison against the existing two-source baseline on the same outer folds and the frozen RevalExo cohort.

The dataset should be retained in the final training set only if it improves or preserves performance across **all** of these checks: pooled internal AUROC, Felius AUROC, Voisard AUROC, RevalExo AUROC, calibration, and healthy-control specificity. A gain on pooled windows alone is not sufficient.

## Compatibility gate before either role

The dataset must pass these checks before model evaluation:

1. Confirm sampling rate, units, axis conventions, sensor locations, and whether acceleration is gravity-inclusive or free acceleration.
2. Confirm that the three selected channels correspond to lower back/sacrum and left/right feet, rather than using a convenient but biologically mismatched sensor.
3. Confirm that the same participant does not appear in any existing local dataset.
4. Exclude non-walking, transition, calibration, and unsupported trial types from the primary binary analysis.
5. Quantify usable seconds and windows per participant, but never treat windows as independent subjects.
6. Compare signal distributions and gait-condition composition against Felius, Voisard, and RevalExo before deciding on resampling or adapter rules.

If the sensor mapping cannot be defended, the dataset remains useful for gait-feature validation or self-supervised pretraining, but it must not be used for supervised stroke classification.

## Final recommendation

The best public-only design is therefore:

`Felius + Voisard development → Sint Maartenskliniek locked examination → Sint Maartenskliniek sensitivity training → RevalExo final frozen stress test`

The locked examination prevents a larger public cohort from quietly becoming another training-tuned result. The sensitivity experiment still allows the additional 30 participants to contribute to the eventual prototype if the evidence shows that pooling improves real generalisation rather than only internal scores.

## Locked external examination result

Using the five existing fold checkpoints/artifacts, with fold-specific internal normalization and participant-level aggregation, the first Sint examination produced:

| Model | Participants | AUROC | Brier | Balanced accuracy at 0.5 |
|---|---:|---:|---:|---:|
| Inception CNN | 30 | 0.915 | 0.097 | 0.850 |
| MiniROCKET + Ridge | 30 | 0.920 | 0.134 | 0.900 |

These are descriptive frozen-examination results, not clinical validation or a final model-selection decision. Sint outcomes were not used for fitting, normalization, calibration, threshold selection, or architecture selection.

## Sources

- [Zenodo public release](https://zenodo.org/records/8198714)
- [GitHub repository and data structure](https://github.com/SintMaartenskliniek/IMU_GaitAnalysis)
- [Associated validation study](https://pmc.ncbi.nlm.nih.gov/articles/PMC10726747/)
