# Stance variability feasibility and next measurement prerequisite

The locked coverage gate failed. **No classifier was fitted and no new accuracy
claim is made.** This closes the current five-cycle-per-side/bout estimator as an
admissible full-cohort experiment. It does not disprove stance variability utility.

[Pre-fit protocol](../docs/STANCE_VARIABILITY_PROTOCOL_2026-09-09.md).
Implemented sample SD/mean within each side and straight bout, then averaged bouts
within side and sides equally. This is distinct from the completed mean-asymmetry
test and avoids treating different left/right or pre/post-turn means as variability.
Minimum five valid cycles per side/bout is a feasibility floor, not an established
reliability standard. Existing event checks and invalid-reference exclusions apply.

| Group | Participants with CV | Coverage |
|---|---:|---:|
| Healthy | 68/72 | 94.4% |
| Stroke | 49/49 | 100% |
| ACL | 9/11 | 81.8% |
| CIPN | 19/19 | 100% |
| HOA | 13/15 | 86.7% |
| KOA | 18/18 | 100% |
| PD | 24/24 | 100% |
| RIL | 51/51 | 100% |

1,259/1,348 trials have usable CV. All 259 participants and trial ledger rows
remain accounted for. The protocol required >=95% availability in every group.
Healthy, ACL and HOA fail. Do not lower this rule after inspecting coverage or drop
the unavailable participants to obtain a favorable classification result.
Four new tests passed: separation of side/bout means from variability, known CV
and side swap, coverage/invalid durations, and unchanged default phase extraction.
The existing four phase-extraction tests also pass after the optional detail API.

## Next priority: directional measurement feasibility

A schema screen of every selected lower-back raw file found acceleration,
gyroscope and magnetometer XYZ columns in all 1,348 files: 561 XSens and 787
TechnoConcept trials. This verifies column availability, not channel quality or
anatomical orientation. No metadata key matching orientation/calibration/quaternion/
heading/axis was found in the selected trial JSONs. This does not establish that
provider documentation elsewhere lacks calibration information.

Existing `src/features/voisard.py` explicitly documents unconfirmed sensor-axis
orientation and computes magnitude harmonic ratio. That existing feature is not
a verified medio-lateral harmonic ratio. Do not rename raw X/Y/Z as anatomical
axes or treat gravity alignment alone as a heading solution.

The next concrete step is to resolve the provider's anatomical-axis convention
and device mapping before implementing directional harmonic ratio. This prerequisite
also governs later gyro-assisted laterality work. Gyro extraction is measurement
validation, not an automatic diagnostic-specificity fix. OOD remains lower priority
and must preserve rejected-stroke and unknown coverage accounting.

## Saved artifacts and state

`data/processed/stance_variability_v1/`: hashed inputs/protocol/code, trial and
participant CV features, per-pathology coverage, gate decision and directional
schema screen. Runner `scripts/run_stance_variability.py` enforces coverage before
fitting and contains the predeclared comparison for reproducibility.

Metadata acquisition and raw downloads unchanged. CV preprocessing complete.
Classifier evaluation not run because coverage failed. Directional schema screen
complete, directional preprocessing and evaluation not implemented. No background
job, no release changes. Latest nested matched combined+phase result remains
45/49 stroke detected, 62/76 other FP and 13/19 healthy FP. Frozen CNN remains
historically 89/138 other FP, not rerun here.
