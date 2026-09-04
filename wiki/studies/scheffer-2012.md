---
type: study
year: 2012
pathway: IC1
population: "28 hemiparetic stroke (25-64y, mean 51.2±10.1) vs 30 able-bodied controls (19-25y, mean 22.6±1.9) — not age-matched"
method: "Backpropagation ANN (Levenberg-Marquardt), grouped with the classical family"
placement: "Full-body inertial motion capture suit (Xsens Moven, 16 sensors)"
---

Scheffer, C., & Cloete, T. (2012). *Inertial motion capture in conjunction with an artificial neural network can differentiate the gait patterns of hemiparetic stroke patients compared with able-bodied counterparts*. *Computer Methods in Biomechanics and Biomedical Engineering*, 15(3), 285–294. https://doi.org/10.1080/10255842.2010.527836. Verified via a real full-text fetch (Taylor & Francis). Found via the IEEE Xplore/Scopus supplementary search that added six more IC1-eligible studies; one of the two shallow-ANN studies (with [[iosa-2021]]) grouped with the classical-method family rather than deep learning, matching the multilayer perceptron Hsu et al. (2018) already establishes as the same-family precedent. Also this review's oldest included study by a decade — 2012, versus the next-oldest ([[mannini-2016]]) at 2016 — and its most sensor-dense: a 16-sensor full-body Xsens Moven inertial motion capture suit, far beyond every other included study's 1-4 IMU count.

## Key findings

- 99.4% classification accuracy distinguishing hemiparetic stroke from able-bodied gait (1 misclassified stride of 166 held-out test strides) — the highest single accuracy figure among the classical-method studies alongside Lee et al.'s (2018) 100%, though on a genuinely held-out test set rather than only cross-validation.
- The stroke and control cohorts are not age-matched (mean 51.2y vs 22.6y, a roughly 29-year gap) — the starkest unaddressed age gap among the classical-method studies, more extreme than Lee et al.'s (2025) ~37-year gap is for a *deep learning* study specifically, and neither age-matched nor statistically checked for comparability, unlike [[inui-2026]] or [[shin-2022]].
- [[quality-assessment]]: participant-level held-out split confirmed (25+22 participants trained, 5+5 held out for testing) — one of five of the six newly-assessed studies confirming a clean held-out/CV design. No code or data availability statement. Chronic hemiparesis described only qualitatively, no formal severity scale (no Fugl-Meyer, NIHSS, or equivalent). Not matched on the ~29-year age gap, bare demographics only, no statistical comparability check.
- Because the study is 2012-era and predates every other included study by years, it establishes that a full-body, high-density IMU rig can separate stroke from healthy gait at very high accuracy — but the 16-sensor rig itself is the least deployment-realistic sensor configuration in the whole review, in direct tension with [[placement-vs-practicality]]'s low-burden deployment interest, worth reading against [[future-directions]]'s trunk-vs-pocket head-to-head recommendation rather than as a standalone accuracy benchmark.

## Links

Corroborates [[classification-methods]]'s classical-method-dominance finding at its highest end (99.4%, second only to [[lee-2018]]'s 100%). Its unaddressed age gap is a specific instance of the pattern [[discriminative-features]]'s own age-confound work in [[voisard-2025]] independently demonstrates is a real risk for this literature. Grouped with [[iosa-2021]] as the review's two shallow-feedforward-ANN, hand-engineered-feature studies.
