---
type: dataset
population: "10 healthy volunteers (avg age 24.8) simulating Normal, Parkinsonian, and stroke gait"
sensors: "foot (per simulated condition)"
role: simulated
---

GaitMotion (Zhang et al., 2024), *GaitMotion: A multitask dataset for pathological gait forecasting*, arXiv:2405.09569 (Version 1), https://arxiv.org/abs/2405.09569v1. **Not real patient data** — confirmed against its published methods. Kept strictly separate from genuine stroke evidence everywhere in this review, never pooled with [[voisard-2025]] or [[felius-dataset]].

**Citation pinned to v1, 2026-07-21**: the generic arXiv DOI (`10.48550/arXiv.2405.09569`) now resolves to a later-revised version of this same work, retitled *"Real-time forecasting of pathological gait via IMU navigation: a few-shot and generative learning framework for wearable devices"* and formally published in *Discover Electronics* (Springer, 2025, DOI `10.1007/s44291-025-00093-8`), with one author (Jing Wang) dropped from that later version. In that revision, "GaitMotion" is reframed as the name of the few-shot-learning *framework*, not the dataset — confirmed directly against the current arXiv abstract page, not just a search snippet. Since this review cites and re-mines the original v1 dataset-description content specifically, the reference was pinned to the version-specific v1 URL rather than swapped to the 2025 framework paper, which describes a different contribution. Do not "fix" this back to the generic DOI or the 2025 citation without re-checking this reasoning first.

## Key findings (this review's own re-mining)

- Simulated stroke gait: mean step time 0.92s (SD 0.22), stride length 61.7cm (SD 10.2), step-time CV 0.16 (SD 0.17) — slower and shorter-stepping than normal gait, only modestly more irregular.
- Simulated Parkinsonian gait: step time 0.59s (SD 0.15), stride length 45.0cm (SD 8.2), step-time CV 0.34 (SD 0.19) — shortest stepping, most irregular.
- Normal gait baseline: step time 0.67s (SD 0.09), stride length 112.5cm (SD 11.6), step-time CV 0.13 (SD 0.15).
- Directionally consistent with the clinical literature on each condition, but since participants are healthy volunteers imitating a gait pattern rather than people with the diagnosis, this contributes a methodological reference point, not stroke-population evidence.
- **Contributes to the pooled independent healthy reference (RQ1, added 2026-07-22)**: only the real "Normal" condition (150 trials, all 10 subjects) feeds [[classification-methods]]'s cross-dataset check, pooled with [[marea]], [[duo-gait]], [[oxwalk]], and [[camargo-2021]] to test whether [[voisard-2025]]/[[felius-dataset]]'s discriminative features generalize beyond the two datasets that identified them — the simulated Shuffle/Stroke conditions are never used here, consistent with this page's own "never pooled with genuine stroke evidence" rule. This is the only source in the pool using foot placement rather than trunk, flagged explicitly as a placement mismatch, not silently pooled as equivalent. Cadence and harmonic ratio excluded — this dataset's sampling rate still isn't confirmed, so only sampling-rate-independent features (RMS, sample entropy, Poincare SD1) are used. (Two earlier, now-superseded versions of this check exist: training a 3-class Normal/Shuffle/Stroke classifier on the simulated conditions — a real result, 0.65 accuracy, removed once the user objected it didn't serve RQ1's actual question; then applying a Voisard/Felius-trained classifier to the real Normal condition as an out-of-sample test, removed a second time once the review's scope was set to feature engineering only. See [[classification-methods]] for the full history.)

## Links

Contrasts with [[voisard-2025]] and [[felius-dataset]] as the review's one explicitly non-real-patient source — see the "role: simulated" distinction maintained throughout `synthesis.md`.
