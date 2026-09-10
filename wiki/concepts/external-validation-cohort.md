---
type: concept
---

# External validation cohort

Current status: RevalExo has already been acquired and repeatedly evaluated. It is inspected stress evidence, not a new final-test candidate. Follow [[classification-project-status]] and [[mobilise-d-tvs]] for current acquisition.

The primary model still needs a genuinely untouched paired cohort with age and sex metadata. External sources are screened against five requirements: both healthy and stroke labels, raw wearable signals, compatible gait placement, participant-level demographics, and a protocol that can be documented well enough for a frozen test.

## Historical candidate and completed stress test: RevalExo

[RevalExo](https://doi.org/10.48804/OWJOID) is the strongest newly identified candidate for an external robustness test. Its README reports 10 stroke and 7 healthy participants with lower-body IMU recordings, pelvis and bilateral lower-limb sensors, 60 Hz sampling and annotated 12-second sliding clips. The official dataset description reports 7 healthy older adults and 6 stroke survivors with synchronized video and lower-body IMUs, plus 4 additional stroke participants with IMU-only recordings. The sensor configuration is close enough to map pelvis to the lower-back channel and retain bilateral foot channels after a deliberately documented resampling and channel-selection procedure.

It is not yet an age-validation cohort. The README gives cohort mean ages of 74.9 years for healthy controls and 57.6 years for stroke participants, plus cohort-level sex counts, but no complete participant-level age/sex table. The sample is also small and was collected for locomotion-intent recognition rather than the same 10 m turn protocol used by [[voisard-2025]]. Use it only as a frozen external stress test, not as a training merge or proof of age robustness. The public archive is split into raw packages of about 8 GB each and a trimmed archive of about 8.3 GB, so download only after the local schema and licensing decision is documented.

## Other screened sources

- [[felius-dataset]] is already part of the internal pooled model, not an external test. Its public release has no participant-level age metadata.
- The [Chapman naturalistic dataset](https://digitalcommons.chapman.edu/pt_data/3/) has stroke and healthy participants with a single L5/S1 IMU, but it lacks the bilateral-foot configuration and standardized walking labels needed for a direct test. It remains a low-back activity stress test.
- [STRIDE](https://digitalcommons.chapman.edu/pt_data/4/) and the [MUSC/ICPSR ARRA dataset](https://www.icpsr.umich.edu/web/ICPSR/studies/37122) provide valuable age- and sex-described stroke cohorts, but their primary data are clinical gait-analysis kinematics, kinetics, EMG and spatiotemporal measures rather than the current raw multi-IMU signal format.
- The [138-control and 50-stroke full-body gait dataset](https://pmc.ncbi.nlm.nih.gov/articles/PMC10692332/) has unusually useful lifespan coverage and matched biomechanical data, but uses motion capture, force plates and EMG rather than the current IMU tensor. It is suitable for age and gait-behavior corroboration, not direct CNN validation.
- The [Zenodo rehabilitation dataset](https://zenodo.org/records/10534055) contains raw IMUs and demographics for 10 stroke participants but no healthy controls. It is suitable for stroke-only representation learning or robustness checks, not binary external validation.

## Current decision

Do not reacquire or rerun RevalExo as an untouched validation study. TVS metadata
intake is complete for 40 participants, with two raw development samples and an
executed inference smoke test. The unfinished task is a common-task pilot protocol
and selected additional raw recordings, followed by quality checks and frozen
specificity evaluation. TVS has no stroke-positive group. Independent paired
stroke/healthy validation and adequate demographics remain unresolved.

## Extraction audit (2026-08-23)

The full RevalExo archives have been downloaded and extracted under `data/raw/revalexo/`. The extracted data contain 30 subject folders across the HC, ST, and SR groups, with HDF5 motion files, annotation CSV files, and selected video files. The primary binary validation cohort is HC versus ST; SR is excluded from the primary classifier.

The HDF5 files expose Xsens motion-tracker channels including acceleration, free acceleration, gyroscope, magnetometer, quaternion, and timestamps. Annotation files include level-ground walking intervals. The audit and adapter are implemented together in `notebooks/11_revalexo_external_validation_pipeline.ipynb`, with results written to `data/processed/revalexo_external_validation_audit.csv` and `data/processed/revalexo_external_window_metadata.csv`.

The audit found that the HDF5 field named `time_since_start_s` is numerically encoded in microseconds; converting it accordingly gives an effective sampling rate of approximately 58.9 Hz, consistent with the documented 60 Hz stream. Some annotation files contain timestamps but no frame indices, so timestamp-based alignment is required for those segments. The current audit identifies 1,358 HC, 844 ST, and 410 SR annotated walking segments; these are segment counts, not independent participants.

## Adapter checkpoint

This historical adapter checkpoint used 18 channels: lower-back, left-foot, and right-foot, each with 3-axis acceleration and gyroscope. The tracker ordering and adapter mapping are verified in the consolidated pipeline notebook.

The HDF5 metadata resolves this mapping: the tracker order is `Pelvis`, `Right Upper Leg`, `Right Lower Leg`, `Right Foot`, `Left Upper Leg`, `Left Lower Leg`, `Left Foot`. The project mapping is LB ← Pelvis, RF ← Right Foot, and LF ← Left Foot. Free acceleration is documented in m/s² and is converted to g. The HDF5 gyroscope label is inconsistent, but the unit is resolved below from Xsens documentation.

Xsens documentation resolves the unit ambiguity: MVNX angular velocity is exported in radians/second, so the adapter converts gyroscope values with `180/π`. The adapter also converts free acceleration from m/s² to g, resamples from approximately 58.9 Hz to 100 Hz, preserves the project’s 18-channel order, and creates 5-second windows with a 2.5-second hop. The resulting windows remain external-only.

The next evaluation uses the established 3-channel gravity-inclusive acceleration-magnitude representation, derived from the adapted lower-back and bilateral-foot `acceleration` channels. The gravity-removed `free_acceleration` channel is not used because it is incompatible with the internal magnitude contract. The selected pooled Inception model is fit on the complete internal development data and evaluated on RevalExo at participant level. RevalExo remains excluded from all fitting, normalization, calibration, and threshold selection.

The corrected frozen external evaluation produced participant-level AUROC **0.871** across 17 participants (7 HC, 10 ST). The raw Brier score was **0.170**; this is not treated as calibrated clinical probability because no RevalExo calibration or threshold fitting was permitted. Results are stored in `data/processed/revalexo_external_metrics.csv` and participant predictions in `data/processed/revalexo_external_participant_predictions.csv`.

The next diagnostic is implemented in `notebooks/13_revalexo_external_error_and_shift_analysis.ipynb`. It reports participant-level false positives/false negatives using 0.5 only as a descriptive reference and compares acceleration-magnitude quantiles between internal data and RevalExo. This is intended to distinguish clinical ambiguity from sensor/domain shift before any adaptation decision.

The diagnostic found 10/10 RevalExo stroke participants correctly ranked above the descriptive cutoff, while 5/7 healthy participants were false positives at 0.5. Internal-versus-external acceleration-magnitude quantiles were broadly comparable, although RevalExo lower-limb medians were slightly lower and its healthy predictions clustered closer to the stroke side. This suggests the next investigation should focus on healthy-subgroup specificity, age/cohort composition, and probability calibration—not immediate sensor rescaling or indiscriminate domain adaptation.

The available RevalExo metadata does not contain individual participant ages, so age-specific error analysis is not possible from this public release; only cohort-level age summaries are available. Applying an internal out-of-fold logistic calibration curve to the external raw logits increased the external Brier score to approximately 0.199, so internal calibration should not be transported as an externally validated probability mapping.

## Recruitment and adaptation decision

The current evidence supports targeted recruitment before domain adaptation. RevalExo reports a substantially older healthy cohort mean than stroke cohort mean, while the internal healthy age coverage is sparse in the 70+ groups. This makes the five healthy false positives compatible with an age/cohort-specificity problem, but individual-level ages are unavailable, so this remains a hypothesis rather than a demonstrated cause.

Priority data addition: recruit a healthy comparison group with age distribution centered around the external healthy cohort and collect the same lower-body sensor configuration where possible. A smaller, age-matched adaptation cohort may then be used to test recalibration or feature alignment, but it must be held separate from the final external test. Do not perform unsupervised or supervised domain adaptation on the current RevalExo test participants and still call the result external validation.

RevalExo remains training-external but repeatedly inspected research evidence, not a pristine final-validation cohort. It must not influence training folds, fold normalization, threshold selection, augmentation policy, or model selection. Poor results should first be investigated as sensor/body-location/sampling/domain shift before considering adaptation.
