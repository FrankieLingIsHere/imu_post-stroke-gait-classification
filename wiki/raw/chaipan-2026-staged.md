---
type: staged
status: unresolved
reason: "full text WAS successfully retrieved (arxiv, not blocked) so the facts below are verified, but the study is a non-peer-reviewed arxiv preprint, matching the Sadeghsalehi 2026 verification-tier precedent already applied elsewhere in this project, plus its own primary framing and thin per-class sample reporting keep it from being a clean IC1 admit even before that question is settled"
---

Chaipan, C., & Aueawatthanaphisut, A. (2026). *Early Pre-Stroke Detection via Wearable IMU-Based Gait Variability and Postural Drift Analysis*. arXiv:2603.16178v1 (posted March 17, 2026, not peer-reviewed). https://arxiv.org/html/2603.16178

Surfaced via the 2026-07-28 search for new RQ3 evidence (query: "stroke gait classifier comparison SVM CNN wearable IMU"). Full text successfully fetched and read via the arxiv HTML mirror — this is a genuine full-text verification, not a snippet-derived summary, unlike the two other staged candidates from this same search pass.

## What the paper actually does (verified via full text)

- **Sensor**: single sacral-mounted IMU at the L5-S1 vertebral level, tri-axial accelerometer and gyroscope.
- **Population**: three groups — healthy controls, individuals in a "pre-stroke" stage, and stroke patients. Framed explicitly as a pilot/feasibility study. Per-group sample sizes are not stated in the extracted content.
- **Classification method**: Random Forest only (classical), three-class risk stratification (control / pre-stroke / stroke). No deep learning method anywhere in the paper.
- **Results**: overall accuracy 0.647, macro-averaged AUC 0.785. Per-class AUC: 0.84 (control), 0.65 (pre-stroke), 0.87 (stroke).
- Authors' own framing: "proof-of-concept and feasibility demonstration" for "a low-cost, non-invasive, and continuous screening tool," explicitly not a clinical diagnostic device.

## Why this is staged rather than decided

Content-wise this does include an actual stroke class classified against non-stroke comparison groups via a data-driven method, which is IC1-shaped on its face. Three separate concerns keep it from a clean Ingest even though the full text is genuinely verified: (1) it is a non-peer-reviewed arxiv preprint, the same verification tier the Sadeghsalehi 2026 candidate was excluded on elsewhere in this project, so a consistent call requires either excluding this one the same way or revisiting that precedent, not deciding this one in isolation, (2) its primary framing is pre-stroke risk screening across three classes rather than a post-stroke gait classification task the way this review's existing IC1 studies are framed, and (3) per-class sample sizes are not disclosed in the available text, and the overall accuracy (0.647) is well below every included study's headline figure. Flagged for a second look rather than decided unilaterally, consistent with how [[johansson-2025-staged]] was handled.
