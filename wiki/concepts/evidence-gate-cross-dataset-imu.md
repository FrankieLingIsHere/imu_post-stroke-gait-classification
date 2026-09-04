---
type: concept
status: active
updated: 2026-09-03
---

# Evidence gate for cross-dataset IMU experiments

No new normalization, pooling, domain-generalization, self-supervised, or
synthetic-data experiment starts from a headline claim alone. It must first be
traced through the primary paper and official implementation, then matched to
this project's disease label, sensor contract, participant split, target-data
access, and clinical decision metrics.

## What the deep audit established

- Generic HAR, gait detection, and stroke-versus-healthy diagnosis are
  different tasks. High accuracy on the first two is not an expected score for
  the third.
- Recent cross-dataset benchmarks show no universal domain-generalization
  winner. ERM can outperform specialized objectives depending on the shift and
  backbone.
- Accelerometer-only input can outperform accelerometer plus gyroscope in
  cross-dataset evaluation. The current lower-back acceleration result is
  therefore plausible, not automatically evidence of a failed implementation.
- Domain adaptation that uses target samples is not valid evidence for the
  source-only deployment setting.
- Synthetic IMU windows can improve some held-out people while harming others.
  They must be generated inside each training fold, used only for training,
  evaluated against real held-out people, and never counted as new subjects.
- Window-wise instance normalization may improve sensor invariance but may also
  erase lower-back amplitude/RMS information that remains stroke-discriminative
  after age adjustment. It is an ablation, not a default fix.

## Mandatory gate

Before a run, document:

1. task/claim and participant-level inference unit;
2. sensor placement, channels, axes/magnitude, units, sample rate, gravity,
   filtering, windows, overlap, and events;
3. participant- and source-disjoint splits;
4. training-only fitting for adapters, normalization, feature selection,
   generation, calibration, and early stopping;
5. official-paper/code mapping and local deviations;
6. matched ERM comparator;
7. participant-level discrimination, calibration, sensitivity, specificity,
   false positives, confidence intervals, and worst-source results; and
8. for synthesis, fidelity, spectra, phase/correlation, diversity, nearest
   neighbors, discriminative score, TSTR/TRTS, and real-only versus augmented
   utility.

RevalExo and frozen NONAN must not select or tune future methods. Synthetic
windows remain auxiliary samples and cannot replace a new untouched paired
stroke/healthy external cohort.

The complete study-by-study evidence matrix, code audit, and ranked candidate
pathways are in
`../../reports/EVIDENCE_GATE_CROSS_DATASET_IMU_2026-09-03.md`.
