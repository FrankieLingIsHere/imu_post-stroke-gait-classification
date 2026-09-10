# Gyro raw-to-processed transfer audit

**No gyro-specific axis or multiplicative scale mismatch was found in the 1,294
comparable trials.** No corrective retraining or test-label flipping is justified
by this audit. The other 54 trials remain unsupported for this comparison.

## Executed comparison

Checked all 1,348 selected trials on the existing packet clock, with bounded
interior interpolation and explicit nonfinite/length exclusions. Applied the
provider eighth-order 14-Hz filter and compared all six axis permutations,
axis signs, a common scale and constant per-axis offsets. No contact labels or
diagnoses selected transformations.

| Device | Gyro mapping | Trials |
|---|---|---:|
| XSens | +X +Y +Z | 507 |
| XSens | Unsupported length/nonfinite | 54 |
| TechnoConcept | +X +Y +Z | 37 |
| TechnoConcept | -X -Y +Z | 750 |

All comparable gyro mappings agree with the independently audited acceleration
mappings. Estimated multiplicative scale is 1 to numerical precision. After
constant offsets, maximum reconstruction RMSE is 2.1e-14 in stored gyro units.
Without offsets, median RMSE is 0.0126 for XSens and 0.0511 for TechnoConcept.

The [provider paper](https://www.nature.com/articles/s41597-025-05959-w) explicitly
describes subtraction of mean static-phase gyro offsets. Constant offsets fully
account for these residuals. This audit estimates the offsets from paired streams;
it does not independently verify the exact standing interval used by the provider.
The earlier laterality model already used processed gyro and bandpass filtering.
There is no newly discovered missing correction to apply to its input.

## Remaining transfer evidence

Reused saved OOF laterality predictions, without fitting or relabeling. Averaging
within participant/device first, full-cohort side accuracy is 41.2% for 115 XSens
participant-device records and 71.0% for 154 TechnoConcept records. These counts
overlap: ten participants have both devices. For those ten participants, mean
accuracy is 25.9% on XSens and 78.9% on TechnoConcept.

That paired observation weakens a simple explanation based only on different
participant identities, but does not isolate device hardware. Sessions, mounting,
protocol, impairment state and reference behavior can still differ. These are
exploratory summaries of existing predictions, not independent validation.
Neither below-chance accuracy nor sign conventions authorize flipping held-out
left/right labels. Raw-to-processed consistency does not establish anatomical
handedness, cross-device angular-rate units or independent reference correctness.

## Decision and continuation

Close this raw-to-processed gyro transformation check. The conditional laterality
candidate remains rejected. Do not repeat it with guessed signs or threshold
changes. A new cross-device mapping intervention needs independent sensor/body
frame evidence or a separately defined calibration procedure first. The known
matched-device result is still stroke 89.6% and RIL 88.1%, below the 90% gate.

No new diagnostic experiment: primary matched HR remains 44/49 stroke detected,
5/19 healthy FP, 47/76 other FP. OOD is still a separate task and must be scoped
against the existing abstention experiments before another implementation.

## Artifacts and completion

`scripts/audit_voisard_gyro_axes.py`, two passing mapping tests (signed permutation,
scale/offset and identity). `data/processed/gyro_axis_v1/` contains input/code hashes,
per-trial mappings/residuals/offsets and saved participant/device comparisons.
All 1,348 trial rows retained, 1,294 comparable, 54 unresolved. No dataset download,
environment change, new fit or model promotion. Metadata/raw acquisition unchanged.
Gyro transformation audit complete; independent anatomy/reference validation not
completed. No running job.
