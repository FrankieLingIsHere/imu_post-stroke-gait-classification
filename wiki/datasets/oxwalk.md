---
type: dataset
population: "39 healthy adults, free-living"
sensors: "hip, wrist (100/25 Hz)"
role: healthy-only-reference
---

OxWalk (Small et al., 2022), *OxWalk: Wrist and hip-based activity tracker dataset for free-living step detection and gait recognition*, University of Oxford. Both placements worn concurrently, sharing the same annotated steps — a placement-agreement sanity check as much as a placement-effect finding.

## Key findings (this review's own re-mining)

- Hip and wrist cadence estimates match closely (~99.7 steps/min at both sites), as expected given they derive from the same annotated steps.
- Sex, once actually tested, shows one nominally significant feature — cadence (p = .0095) — that does not survive multiple-comparison correction, alongside [[duo-gait]]'s stride-length finding.
- Wrist-related noisiness elsewhere in this review (see [[marea]]) does not show up here, since both placements agree by construction on this dataset.
- **Contributes to the pooled independent healthy reference (RQ1, added 2026-07-22)**: OxWalk's hip-sensor data (39 subjects, the largest single subject count of any source in the pool) feeds [[classification-methods]]'s cross-dataset check, pooled with [[marea]], [[duo-gait]], [[camargo-2021]], and [[gaitmotion]] to test whether [[voisard-2025]]/[[felius-dataset]]'s discriminative features generalize beyond the two datasets that identified them. Its own raw triaxial accelerometer signal, previously unused (only the annotation-derived cadence was used elsewhere in this review), was extracted for the first time for this check — real, usable data that had simply never been read from the raw file before. (A now-superseded version of this check also applied a Voisard/Felius-trained classifier to OxWalk as an out-of-sample test — OxWalk had the *lowest* false-positive rate of the five sources, 15% — removed once the review's scope was set to feature engineering only, no classifier training of its own. See [[classification-methods]] for the full history.)

## Links

Paired with [[marea]], [[duo-gait]], and [[camargo-2021]] as one of four healthy-only reference datasets used for placement checks in [[sensor-placement]], and — unlike an earlier version of this session's work, which excluded it — now also part of the pooled cross-dataset check in [[classification-methods]].
