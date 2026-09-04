---
type: dataset
population: "60 healthy adults, age 21–75 years, balanced by age decade and sex"
sensors: "One lower-back/pelvis G-Walk IMU: 3-axis acceleration and gyroscope at 100 Hz"
role: external_healthy_lower_back_only
---

Carpinella et al. (2026) is a controlled, standardised 6-Minute Walk Test
(6MWT) dataset for 60 healthy adults. It is the credible public healthy-gait
cohort needed to test whether the lower-back representation falsely labels
age-diverse healthy walking as stroke.

## Local audit — 2026-09-01

- Download checksum matched the Figshare MD5 exactly.
- All 60 `Data.mat` files provide raw 100 Hz three-axis acceleration and
  gyroscope signals, straight-walking/turn segmentation, gait events, and
  participant-level metadata.
- Five files have a longer timestamp vector than sensor tensors; this is a
  small, explicit adapter requirement, not an invitation to alter raw data.
  See `data/raw/carpinella_2026/metadata/LOCAL_AUDIT.md`.
- The frozen lower-back-only baseline was evaluated without retraining,
  calibration, model selection, or threshold tuning. It yielded 0/60 healthy
  participant false positives at the pre-existing 0.50 decision reference
  (6,109 five-second straight-walking windows; 95% Wilson upper bound 6.0%).
  This is healthy-specificity evidence only: no AUROC or sensitivity can be
  estimated from a healthy-only cohort.

## Role decision

Use it as a participant-disjoint **external healthy specificity** cohort for a
lower-back-only model and to audit age-related false positives. It cannot be
directly pooled with the three-channel baseline because bilateral foot IMUs are
absent, and it cannot supply a stroke class because all 60 participants are
healthy. Do not fabricate left/right foot channels.

Sources: [Figshare release](https://doi.org/10.6084/m9.figshare.29665850.v1),
[data descriptor](https://doi.org/10.1038/s41597-025-06506-3).
