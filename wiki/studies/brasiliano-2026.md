---
type: study
year: 2026
pathway: IC1
population: "85 stroke vs 97 healthy — the largest paired stroke-and-healthy sample in the review"
method: "k-NN, SVM, DT (sequential backward selection, 9 features)"
placement: "5 IMUs: forehead, sternum, lower back, bilateral distal tibia"
---

Brasiliano et al. (2026), *Identifying key gait features in stroke patients using wearable inertial sensors and supervised and unsupervised machine learning*, *Scientific Reports* 16:8908. The largest-scale multi-placement comparison in the review, and the direct methodological source for two techniques this review's own hands-on mining adopts.

## Key findings

- 94.1% / 96.7% / 89.1% accuracy (k-NN / SVM / DT) on a 9-feature set retained via sequential backward selection from a 5-placement array. **Corrected 2026-07-29**: a `journal-critic` adversarial re-review found the previously recorded figures (88.1% / 89.8% / 81.2%) did not match the published paper — verified directly against the source, which reports these three corrected values, SVM highest, decision tree lowest.
- Its sequential backward selection method and its k-medoids unsupervised cluster-validation approach are both reused directly in this review's own hands-on mining (see the manuscript's Section 3.8, 4.2.4).
- [[quality-assessment]]: held-out/CV confirmed (5-fold, repeated 10 times — the most rigorous repetition scheme of any included study), data available on request (no code), chronicity described only qualitatively ("sub-acute and chronic phase," no exact duration), severity via FAC≥3 inclusion threshold only, healthy controls with bare demographics and an unaddressed ~9-year age gap (57y stroke vs 48y healthy).

## Links

Methodological template for [[quality-assessment]]'s nested/single-level comparison logic and for the manuscript's own SBS+CV protocol. Part of the still-open multi-placement-vs-pocket gap in [[future-directions]], alongside [[pohl-2022]] and [[hsu-2018]].
