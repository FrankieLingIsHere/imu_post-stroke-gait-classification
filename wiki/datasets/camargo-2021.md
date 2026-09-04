---
type: dataset
population: "22 healthy adults, level-ground/ramp/stair/treadmill locomotion"
sensors: "Trunk, thigh, shank, foot (200 Hz)"
role: healthy-only-reference
---

Camargo, J., Ramanathan, A., Flanagan, W., & Young, A. (2021), *A comprehensive, open-source dataset of lower limb biomechanics in multiple conditions of stairs, ramps, and level-ground ambulation and transitions*, *Journal of Biomechanics* 119:110320, https://doi.org/10.1016/j.jbiomech.2021.110320. No stroke cohort — used here as a healthy-only reference. Documents the widest range of simultaneous placements among the audited datasets (trunk, thigh, shank, foot).

## Unblocked 2026-07-22

Previously excluded from every signal-derived comparison in this review, and from this page's own summary above that line until this date: every signal-bearing file (IMU, goniometer, force plate) serializes MATLAB's `table` class as an MCOS object, an undocumented binary layout neither `scipy.io.loadmat` nor `pymatreader` can decode into real column data — both return only the raw byte pointers (confirmed directly: `s0`/`s1`/`s2`/`arr` keys containing literally `[b'data', b'MCOS', b'table', ...]`, not signal). Trial-level metadata (subject, speed, turn direction, per-timestep activity label) *does* decode correctly through both libraries, since those files are plain MATLAB structs, not tables — only the sensor waveforms themselves were blocked.

Re-attempted after a direct user challenge to that conclusion, in a session asking why only 2 of 7 audited datasets were contributing to RQ1/RQ3. The `mat-io` package (`matio`, https://github.com/foreverallama/matio) correctly reconstructs MATLAB table objects as pandas DataFrames — a library neither this project nor the earlier "blocked" conclusion had tried. Confirmed directly against decoded output, not assumed: sampling interval exactly 200 Hz, trunk accelerometer magnitude averaging ~1.03g with plausible walking-scale variance — both matching the dataset's own documentation, not corrupted output. All 22 subjects' data, previously fully downloaded and sitting unused, is now usable. New loader module: `src/features/camargo.py`.

## Key findings (this review's own re-mining)

- **Placement (RQ2)**: across 880 level-ground trials (all 22 subjects), foot carries the highest raw acceleration magnitude (2.10g), ahead of shank (1.59g) and thigh (1.36g), with trunk lowest and most variable (1.33g) — the same foot-highest, trunk-lowest ordering [[duo-gait]]'s independent 7-sensor comparison already found, now corroborated by a second, entirely different dataset, hardware platform, and protocol.
- **Contributes to the pooled independent healthy reference (RQ1, added 2026-07-22)**: Camargo's trunk-sensor level-ground trials (110 trials, all 22 subjects) feed [[classification-methods]]'s cross-dataset check, pooled with [[marea]], [[duo-gait]], [[oxwalk]], and [[gaitmotion]] to test whether [[voisard-2025]]/[[felius-dataset]]'s discriminative features generalize beyond the two datasets that identified them. (Three earlier, now-superseded versions of this check exist, in order: training a 4-class level-ground/ramp/stair/treadmill locomotion-mode classifier on all 3,147 trials — a real result, 0.70 accuracy, removed once the user objected it didn't serve RQ1's actual question; applying a Voisard/Felius-trained classifier to Camargo as an out-of-sample test instead; then removing that too once the review's scope was set to feature engineering only, no classifier training of its own. See [[classification-methods]] for the full history.)

**A second real bug caught while building the pooled reference**: Camargo's gyroscope is in radians per second (confirmed: walking-magnitude ~0.85, same order as [[voisard-2025]]'s own rad/s gyro), not degrees per second like [[duo-gait]]/[[gaitmotion]]/[[felius-dataset]]. Left unconverted, this alone was enough (combined with an accelerometer-unit mismatch elsewhere) to make an early version of the cross-dataset comparison classify 100% of 335 independent healthy people as "stroke". Fixed in `src/features/cross_dataset.py`, not in `src/features/camargo.py` itself, since Camargo's *own* locomotion-mode and placement analyses never needed cross-dataset unit consistency in the first place.

## Links

Part of the 2026-07-22 cross-dataset healthy-reference expansion alongside [[marea]], [[duo-gait]], [[oxwalk]], and [[gaitmotion]] — all triggered by the same user question about why only 2 of 7 datasets were contributing to RQ1/RQ3, then corrected a second time after the user objected that the first version of that expansion tested unrelated per-dataset tasks instead of the actual stroke-vs-healthy question. See [[classification-methods]] for the full reasoning. No longer the dataset marked "not assessable" in [[sensor-placement]]'s synthesis table — that page's own note needs updating to match (see its entry for this correction).
