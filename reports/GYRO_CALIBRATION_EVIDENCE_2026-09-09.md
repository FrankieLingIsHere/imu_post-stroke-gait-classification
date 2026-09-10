# Calibration hypotheses: physical evidence and remaining limits

Executed on all 1,348 selected trials. No model fitting or corrections chosen from
left/right labels. These checks distinguish internal physical consistency from
independent calibration proof.

| Hypothesis | Executed evidence | Decision |
|---|---|---|
| Device units differ by degrees/radians | Median absolute gyro integral projected on initial gravity during annotated U-turn: XSens 3.074892, TechnoConcept 3.067800. Both close to pi for a nominal half-turn. | Strongly inconsistent with a gross 57.3-fold unit mismatch. Supports radians/s, not traceable sensor calibration. |
| Unremoved constant gyro bias explains transfer | Median processed initial-2s mean gyro vector norm: XSens 0.000038, TechnoConcept 0.000055 in stored units. Native first-200-row means reconstruct provider offsets to <1e-8 for 450/507 comparable XSens and 787/787 TechnoConcept trials. | No broad missing bias correction found. Remaining 57 XSens differences need packet-clock/static-window care, not automatic re-centering. |
| Head/back turn direction is internally inconsistent | Signed gravity-projected turn integrals agree in 561/561 XSens and 782/782 jointly usable TechnoConcept trials. Five TechnoConcept head checks unavailable. | No internal head/back turn-sign contradiction. Cannot determine absolute left/right handedness or turn direction without an external reference. |
| Same-participant device gap isolates hardware | All ten paired-device participants use different recorded sessions across devices; nine have the same stated distance protocol, RIL_46 differs (8m vs 10m). | Hardware is entangled with visit time/mounting and potentially clinical changes. This is not a controlled paired-device experiment. |
| Raw-to-processed axis/scale bug | Prior completed mapping audit: 1,294 comparable trials, identical acceleration/gyro permutations, unit scale and constant offsets reconstruct processed gyro. | Closed. Do not repeat or infer anatomical calibration from file consistency. |

## Why this changes the interpretation

The ten paired-device participants previously showed mean saved OOF laterality
accuracy 25.9% XSens versus 78.9% TechnoConcept. Metadata now establishes that
device changes occurred across different sessions, not simultaneous or same-session
measurements. For example, PD_20 changes from day 0 to 191 and RIL_24 from day 0
to 241. The descriptive accuracy gap is real, but does not isolate a hardware
effect. HS_6 has several session IDs sharing a single reported day offset, so
metadata timing precision should not be overstated.

Median U-turn integrals near pi support scale consistency; individual ranges are
1.34-5.53 for XSens and 1.42-4.81 for TechnoConcept. Gravity-projected integrals are
proxies affected by mounting, motion and annotated turn bounds. No per-trial scale
was adjusted to force pi. This would risk removing actual movement differences.

The first two seconds are the provider-assumed standing interval, not independently
verified immobility. Native first 200 rows can differ from 200 shared-clock samples
when packets are missing. Constant-offset reconstruction tests and projected-turn
checks should not be confused with independent bias/heading calibration.

## What remains unproved

Absolute anatomical handedness, precise cross-device gain/axis calibration,
left/right foot-label correctness and contact timing against independent ground
truth remain unresolved. Definitive proof requires a documented known-direction
calibration motion, video/force reference, or simultaneous sensors on the same
movement. Existing foot-derived annotations cannot independently validate their
own timing or side labels. Do not flip test labels, rescale to pi, or retune models
to manufacture agreement.

The next justified continuation is to establish availability of those independent
references from existing provider materials before a new calibration intervention.
If unavailable, mark the calibration claim unverified and keep the gyro candidate
unadmitted. OOD is separate and cannot repair measurement validity by itself.

## Artifacts and current results

Runner `scripts/check_gyro_calibration_evidence.py`. Saved input/code hashes,
per-trial physical checks, summaries and paired-device session/protocol ledger in
`data/processed/gyro_calibration_evidence_v1/`. No new acquisition or classifier fit.
Physical checks complete, independent calibration not established. Gyro conditional
matched accuracy remains stroke 89.6%, RIL 88.1%. Primary matched stroke HR model
remains 44/49 stroke detected, 5/19 healthy FP, 47/76 other FP. Frozen release
unchanged. No background work after completion.
