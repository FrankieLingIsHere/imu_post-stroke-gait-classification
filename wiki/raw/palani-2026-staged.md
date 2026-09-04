---
type: staged
status: unresolved
reason: "full text blocked (ACM Digital Library 403, ResearchGate 403) — screening below is built from a single WebSearch snippet only, not a fetched primary source, and the sensor-modality description available raises a likely EC1 concern (joint angles / center of mass sound like optical-motion-capture-derived features, not wearable IMU) that could not be confirmed either way"
---

Palani, P., Renganathan, G., & Kurita, Y. (2026). *Multi-modal Feature-based Classification of Post-Stroke Motor Impairment using Bi-directional LSTM*. Proceedings of the Augmented Humans International Conference 2026. https://doi.org/10.1145/3795011.3797386

Surfaced via the 2026-07-28 search for new RQ3 evidence (found while chasing a companion candidate, [[pinheiro-2026-staged|Pinheiro et al. 2026]], in a related search). Full text could not be retrieved: ACM Digital Library page and a ResearchGate mirror both returned HTTP 403. The single available fact-bearing snippet is reported below as unverified.

## What the one available snippet suggests (unverified)

- Large sample for this field: 380 participants, 120 healthy and 260 post-stroke, each contributing one leg.
- Feature inputs described as "joint angles, centre of mass, and temporal components of muscle synergies," the latter extracted via non-negative matrix factorization from surface EMG. No wearable IMU (accelerometer/gyroscope) is mentioned anywhere in the available snippet.
- Classifier is a Bi-directional LSTM (deep learning). No classical ML baseline is mentioned as being compared within the same paper in the available snippet, though this could not be ruled out without the full text.

## Why this is staged rather than decided

Two blockers: (1) full text is inaccessible after two real attempts, and (2) "joint angles" and "centre of mass" as feature inputs, with no IMU mentioned at all, sound like they come from an optical motion-capture system rather than a wearable sensor, which would be a straightforward [[eligibility-criteria|EC1]] exclusion (non-wearable modality) if confirmed. Given the large, genuinely interesting sample size (260 post-stroke), this is worth a second look if full-text access becomes available, specifically to confirm the sensing modality and check whether a classical-ML comparison exists in the same paper — but nothing here should be treated as verified or cited yet.
