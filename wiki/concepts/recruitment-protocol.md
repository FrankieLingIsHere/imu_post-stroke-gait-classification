# Recruitment protocol for age-robust gait classification

## Purpose

The current external result has good discrimination but reduced healthy specificity. The next data collection should test whether this is related to age/cohort composition and should improve transportability without contaminating the final external evaluation.

## Priority design

Recruit participants into overlapping age-by-label cells rather than recruiting one broad convenience sample:

| Age band | Healthy | Post-stroke |
|---|---:|---:|
| 40–59 | target matched cells | target matched cells |
| 60–69 | target matched cells | target matched cells |
| 70–89 | target matched cells | target matched cells |

The exact sample size should be set by a formal power calculation once the primary endpoint and expected AUROC are fixed. For an initial feasibility/adaptation cohort, prioritize balanced cells and participant diversity over generating many overlapping windows from a small number of people. Windows are not independent participants.

## Acquisition contract

- Use lower-back/pelvis and bilateral-foot IMUs whenever possible.
- Record raw acceleration and gyroscope with sensor units and sampling rate preserved.
- Collect level-ground walking long enough to produce multiple independent 5-second segments per participant.
- Record walking protocol, assistance/device use, walking speed instructions, footwear, surface, and fatigue or rest periods.
- Record participant-level age, sex, stroke status, time since stroke, side affected, impairment/severity measures, walking aid, and relevant comorbidities.
- Preserve raw files and a machine-readable participant/trial manifest.

## Dataset roles

1. Development data: model fitting and internal participant-level cross-validation.
2. Adaptation/calibration cohort: optional, used only for a pre-specified domain-adaptation or calibration experiment.
3. Final external test: untouched until the model, preprocessing, calibration policy, and threshold policy are frozen.

Never use the same participants for adaptation and final external reporting.

## Minimum acceptance checks

Before adding new data to training, verify sensor placement, units, sampling rate, channel order, walking annotation quality, age-by-label overlap, missingness, and participant-level leakage. A recruitment dataset should first reproduce the existing 18-channel preprocessing contract and then be evaluated as a separate source before any pooling decision.

## Current decision

Recruitment is the preferred next investment. Domain adaptation remains a secondary experiment after an age-overlapping cohort exists; it should not be used to hide poor healthy specificity on the current external cohort.

## Immediate project artifacts

Use `data/interim/recruitment_manifest_template.csv` for participant/trial metadata and `data/interim/recruitment_acceptance_checklist.md` before admitting any new participant into development or adaptation data.
