---
type: dataset
population: "16 healthy adults, single/dual-task, unfatigued/fatigued"
sensors: "head, chest, sacrum, bilateral wrist, bilateral shank, bilateral foot (128 Hz) — 9 sensors shipped, 7 used in the placement leaderboard here"
role: healthy-only-reference
---

DUO-GAIT (Zhou et al., 2023), *DUO-GAIT: A gait dataset for walking under dual-task and fatigue conditions with inertial measurement units*, *Scientific Data* 10:543. The review's richest healthy-population dataset for demographic-pattern mining and the only one with a genuine multi-placement leaderboard.

## Key findings (this review's own re-mining)

- Direct 7-sensor placement leaderboard (single-task overground walking): feet highest raw acceleration magnitude (~1.40g), wrists intermediate (~1.08g), trunk/head lowest and most stable (~1.02–1.04g). See [[sensor-placement]] for why "highest magnitude" ≠ "best discriminator."
- Demographic-pattern checks (age, sex, self-reported activity level): no significant feature for age or activity level. Sex, once actually tested (not just eyeballed from means), shows one nominally significant feature — stride length (p = .028) — that does not survive multiple-comparison correction.
- n=16 is underpowered for strong conclusions on any of these checks.
- **Contributes to the pooled independent healthy reference (RQ1, added 2026-07-22)**: DUO-GAIT's sacrum-sensor trials (single-task condition, 16 subjects) feed [[classification-methods]]'s cross-dataset check, pooled with [[marea]], [[oxwalk]], [[camargo-2021]], and [[gaitmotion]] to test whether [[voisard-2025]]/[[felius-dataset]]'s discriminative features generalize beyond the two datasets that identified them. DUO-GAIT gives the *only* head-sensor readings in the pooled reference besides Voisard's own, since it's the one other dataset here with a head sensor. (Two earlier, now-superseded versions of this check exist: testing DUO-GAIT against its own single-vs-dual-task label — a real result, 0.59 accuracy, near chance, removed once the user objected it didn't serve RQ1's actual question; then applying a Voisard/Felius-trained classifier to DUO-GAIT as an out-of-sample test, removed a second time once the review's scope was set to feature engineering only. See [[classification-methods]] for the full history.)

## Links

Anchors [[sensor-placement]]'s "feet carry raw dynamic range, trunk carries discriminative signal" distinction, contrasted against [[voisard-2025]] and [[felius-dataset]]'s actual pathology-discrimination findings.


Historical DUO-GAIT inventory is superseded by the completed magnitude test linked above; directional transfer remains pending.


Latest experiment (2026-09-09): [Controlled regularization and warm-up](../../docs/classification/VGA_REGULARIZATION_RESULT.md) completed and verified: 27 fits, all 40 epochs, same 248-person VGA impairment-screening target. Control normal false alerts16-17/84 and impairment detections91-101/164; decay16-18 and87-102; warm-up15-19 and89-103. Warm-up slightly improves paired full AUROC but increases false alerts in two seeds. All settings fail the prototype gate. Only2/27 runs improve after simulated patience8 stopping, best epochs1-24, none at40. No consistent specificity fix, no model promotion. Schedule/optimizer tests and source/label/split/threshold/metric/checkpoint verification passed. Metadata and raw acquisition unchanged, preprocessing reused, evaluation complete. DUO-GAIT remains a reused alert stress test without VGA labels. Do not rerun this completed comparison.

This week: [progress, benchmark tables and model structures](../../docs/classification/WEEKLY_PROGRESS_2026-09-07.md) (2026-09-07 through 2026-09-09). Separates the packaged stroke logistic model, stroke CNN comparisons and six-channel VGA screening reference. No new training or promotion. [Week 3 GitHub Pages report](https://frankielingishere.github.io/imu_post-stroke-gait-classification/reports/WEEK_03_PROGRESS.html) published and live-verified on 2026-09-09.
