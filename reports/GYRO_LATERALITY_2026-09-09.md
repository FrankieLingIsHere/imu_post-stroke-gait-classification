# Conditional gyro laterality experiment, 2026-09-09

**Gate failed. This measures side assignment at supplied contact times, not stroke diagnosis.**

[Pre-fit protocol](../docs/GYRO_LATERALITY_PROTOCOL_2026-09-09.md).
Used six nominal vertical/AP gyro features: 0.5-2 Hz filtered values and
first/second sample gradients at reference heel strikes. Provider-processed
X/Z axes, with no per-person or diagnosis-driven sign reversal. Fresh linear
SVC C=1 and training-fold MinMaxScaler. Participant-equal weights split equally
between sides. Existing three outer participant/pathology folds, full and
matched scopes. This is inspired by Ullrich feature types, not an exact
reproduction or a run of its pretrained model. Six new fits.

Installed mobgap pretrained estimators emitted sklearn serialization-version
warnings (1.6.1 versus local 1.9.0). They were not used for predictions.
The existing environment was retained and no packages downgraded.

## Results

| Scope | Group | Participants | Participant-macro side accuracy | Contact coverage | Pass |
|---|---|---:|---:|---:|---|
| all_selected | healthy | 72 | 54.0% | 100.0% | False |
| all_selected | stroke | 49 | 71.4% | 100.0% | False |
| all_selected | ACL | 11 | 51.5% | 100.0% | False |
| all_selected | CIPN | 19 | 80.8% | 100.0% | False |
| all_selected | HOA | 15 | 46.2% | 100.0% | False |
| all_selected | KOA | 18 | 36.7% | 100.0% | False |
| all_selected | PD | 24 | 56.4% | 98.8% | False |
| all_selected | RIL | 51 | 58.5% | 99.7% | False |
| device_protocol_matched | healthy | 19 | 97.8% | 100.0% | True |
| device_protocol_matched | stroke | 49 | 89.6% | 100.0% | False |
| device_protocol_matched | CIPN | 18 | 95.9% | 100.0% | True |
| device_protocol_matched | PD | 19 | 96.6% | 100.0% | True |
| device_protocol_matched | RIL | 39 | 88.1% | 100.0% | False |

Usable contacts: 48,131/48,257. Three invalid
reference-bound trials remain in coverage. All 259 participants retained in
the main ledger. Missing participant accuracy would count zero.
Training single-side participant exclusions across fits: 0.
Two tests passed: feature dimensions/sign response and duplicate/out-of-range/
nonfinite rejection. All held-out participant/pathology checks passed.

## Limits and decision

References are algorithm-derived foot annotations. Contact times and straight
bout boundaries are supplied, so this is conditional agreement, not independent
measurement validity or autonomous contact accuracy. No final-contact, stance,
double-support or stroke-diagnostic accuracy is established. The nominal
processed-axis convention is used without per-trial anatomical calibration.
The fresh fit does not validate a transferable pretrained model. Matched and
full scopes overlap and are not independent replications.

The conditional feasibility gate failed. Do not attach this model to the event adapter or claim autonomous phase recovery. Do not globally flip test labels or retune on held-out cases. The saved per-group results locate the measurement limitation; independent event references remain needed.

No new stroke-classification result. Previous primary matched HR result remains
44/49 stroke detected, 5/19 healthy FP, 47/76 other FP. Frozen release unchanged.
Metadata/raw acquisition unchanged. Gyro feature extraction and conditional
evaluation complete. Autonomous laterality and independent validation not done.
No background job after completion.

Artifacts in `data/processed/gyro_laterality_v1/`: hashes, features, trial coverage,
contact predictions, fit counts, participant/group metrics and decision.
Run `scripts/run_gyro_laterality.py` then `scripts/summarize_gyro_laterality.py`.
