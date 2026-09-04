---
type: staged
status: unresolved
reason: "ambiguous fit against IC5 — genuinely uses wearable IMU-based feature extraction on real stroke patients, but its primary framing is a clinical-intervention case series (augmented rehabilitation feedback), not a methodology evaluation the way IC5's three existing studies (avvenuti-2018, ensink-2023, felius-2024) are. n=4, no within-study control group."
---

Johansson, G. M., & Öhberg, F. (2025). Augmented Feedback in Post-Stroke Gait Rehabilitation Derived from Sensor-Based Gait Reports—A Longitudinal Case Series. *Sensors*, 25(10), 3109. https://doi.org/10.3390/s25103109

Surfaced via the user's Zotero library during a 2026-07-22 citation-accuracy check (not from a fresh literature search), then screened here against [[eligibility-criteria]] at the user's direct request. Full text verified via PMC (PMCID PMC12115626), not just the abstract.

## What the paper actually does

- **Sensors**: seven wearable IMUs (accelerometer + gyroscope; magnetometer excluded due to environmental interference), strapped to the pelvis, both thighs, both shanks, both feet.
- **Population**: 4 chronic stroke patients (ages 25-57), varied motor impairment and sensory deficits (documented via Fugl-Meyer Assessment). No within-study control group — gait parameters are instead compared against an external reference database of 100 healthy participants (ages 40-75) and against established minimal-detectable-change (MDC) thresholds.
- **Design**: longitudinal case series, four assessment timepoints, paired with a 10-day intensive constraint-induced movement therapy intervention. Individualized "augmented feedback" was given to each participant at follow-ups, based on comparing their own gait-report curves (hip/knee sagittal-plane joint angles, gait speed, cadence, walking time) against the reference data, distinguishing genuine motor recovery from compensatory movement patterns.
- **Classification method**: none. Confirmed directly — "purely descriptive... no machine learning or classification algorithms." Every reported value is a spatiotemporal or kinematic feature compared against a fixed threshold or reference curve, not a trained model's output.

## Why this is staged rather than decided

Real wearable-IMU feature extraction on real, diagnosed stroke patients is exactly the kind of substance [[felius-2024]] (IC5, unsupervised feature extraction) is admitted for. But IC5's own definition and its three existing admits ([[avvenuti-2018]], [[ensink-2023]], [[felius-2024]]) are all framed as answering a *methodology* question relevant to this review's own RQs (does a placement work, does a detection algorithm hold up, what structure does unsupervised feature extraction find) — not as a clinical-intervention case series that happens to use IMU-derived features to build a patient feedback report. Whether "features extracted specifically to power an augmented-feedback rehabilitation report" counts as IC5's own "feature extraction" pathway, or whether IC5 is meant more narrowly for studies whose primary contribution *is* the methodology itself, is a genuine judgment call this staging entry is deferring rather than making unilaterally. The n=4, no-control-group design would also make it a thin addition to Table 3 even if included.

## Links

Companion candidate from the same 2026-07-22 check: Hosoi et al. (2023), excluded outright rather than staged (no wearable component at all — see `log.md` for the full reason, no wiki page since exclusion was clear-cut).
