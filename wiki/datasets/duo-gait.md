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
