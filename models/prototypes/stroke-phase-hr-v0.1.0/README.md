# Stroke phase + HR research prototype

Executable **participant-feature classifier**, fitted on all 259 selected Voisard
participants. It does not accept raw IMU streams and does not autonomously recover
phase features. Frozen v0.2.0 remains unchanged.

## Run

From repository root, using the existing environment:

```powershell
& C:/Users/frank/.venv-cu130/Scripts/python.exe -m models.prototype_stroke_features --package models/prototypes/stroke-phase-hr-v0.1.0 --input models/prototypes/stroke-phase-hr-v0.1.0/examples/participants.csv --output models/prototypes/stroke-phase-hr-v0.1.0/examples/predictions.csv
```

Only load the locally built trusted package. The CLI verifies its checksum before
loading the joblib model; the manifest is provenance, not cryptographic authentication.
Builder: `scripts/classification/package_stroke_features.py`.

## Input CSV

One unique, nonempty `participant` ID per row plus these exact feature columns:

| Column | Contract |
|---|---|
| age | Years; may be missing, using training median imputation |
| xsens_fraction | Fraction of participant trials acquired with XSens, 0-1 |
| protocol_length_m | Mean one-way walking protocol length, metres |
| cadence | Existing event-derived participant cadence, steps/min |
| step_asymmetry | Absolute side-mean difference divided by bilateral mean |
| swing_asymmetry | Same normalization for swing duration |
| stance_asymmetry | Same normalization for stance duration |
| swing_fraction | Mean swing/stride fraction, 0-1 |
| double_support_fraction | Valid bilateral stance-overlap/stride fraction, 0-1 |
| ml_log_hr | Mean log1p nominal-Y odd/even harmonic amplitude ratio |

Use the unchanged `bilateral_phase_v1` and `directional_hr_v1` extraction contracts.
Participant features aggregate trials equally, not raw pooled contacts. Numeric
range checks cannot establish correct sensor placement, reference events or units.
Felius/Sint data are not automatically compatible with this feature contract.
Diagnosis and other extra columns are not predictors. Only age may be missing.
Rows with invalid values remain in output with null score and `unknown` decision.
Missing schema or duplicate IDs reject the input file with a clear error.

## Output and threshold

Output: participant, score, decision, status, age_imputed, threshold.
`research_positive` and `research_negative` are experimental classifier calls,
not diagnoses or confirmation of health. The score is not a clinical probability.
Unknown rows are not negative. The example contains three valid source rows and
one intentionally invalid row to demonstrate this behavior.

Threshold **0.3953767333929809** was selected for a 90% empirical stroke-sensitivity
target from existing full-scope participant OOF development scores. This happened
after those data had been inspected. It is an engineering operating point for a
full-data prototype, with **no untouched evaluation at this threshold**. Do not
average the old inner-fold thresholds or claim they validate this artifact.

Prior nested-threshold results for the same feature arm: full 45/49 stroke,
6/72 healthy FP, 56/138 other FP. Separately fitted matched scope: 44/49 stroke,
5/19 healthy FP, 47/76 other FP. Strict gates failed. These are historical
development comparisons, not performance estimates for the packaged model.
`examples/historical_oof_comparison.csv` retains baseline and feature-arm results.

## Completion

Full fit, serialization parity, real CSV CLI and input-contract tests completed.
No newly downloaded data or new independent validation. Model/manifest at package
root, small examples in `examples/`, batch smoke outputs in versioned processed data.


[Verified feature audit and held-out benchmark](../../../docs/classification/BENCHMARK.md):
all ten features reconstructed, 12 fold fits reproduced, ten tests passed.
No new independent validation of this full-data artifact or its threshold.
