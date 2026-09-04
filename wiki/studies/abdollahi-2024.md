---
type: study
year: 2024
pathway: IC4
population: "21 stroke survivors (11 fallers, 10 non-fallers), no healthy comparison group"
method: "Random Forest"
placement: "8 IMUs: feet, shanks, thighs, low back, sternum"
---

Abdollahi et al. (2024), *Fall risk assessment in stroke survivors: A machine learning model using detailed motion data from common clinical tests and motor-cognitive dual-tasking*, *Sensors* 24(3):812. Classifies high- vs. low-fall-risk from dual-task balance-sway and Timed-Up-and-Go features, then shows a single thorax sensor performs comparably to the full 8-sensor array.

## Key findings

- 91% accuracy, 0.82 sensitivity, 1.0 specificity using the full array; a single thorax sensor performs comparably on its own — direct evidence that a clinically useful classifier doesn't always need the full placement burden its own training configuration might suggest.
- [[quality-assessment]]: held-out/CV confirmed (LOSO), data available on request (no code), chronicity given only as an inclusion threshold (≥6 months post-stroke, chronic) with no exact distribution, no standardized severity score (FES-I/pain/unsteadiness questionnaires instead), no comparison group by design (fallers vs. non-fallers within the stroke population).

## Links

Corroborates [[sensor-placement]]'s trunk/thorax finding alongside [[hsu-2021]], [[lee-2018]], and [[inui-2026]] ([[mannini-2016]] removed from this list 2026-07-29 — verified shank-dominant, not lumbar-placement evidence) — four studies converging on trunk placement despite different populations, hardware, and protocols, though none besides this study itself is a genuine placement comparison rather than a single-placement result.
