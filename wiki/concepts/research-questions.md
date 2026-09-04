---
type: concept
---

**Merged 2026-07-23**: the manuscript's own Section 3.1 now states three research questions, not four. The former RQ3 (classification methods) and RQ4 (datasets used) are combined into a single question, since answering "how have classifiers performed" was never separable in practice from "on what datasets" — every classification-performance claim throughout Section 4 already names its dataset. This page keeps datasets' own detailed answer as a distinct section below for navigability, but it is now a sub-thread of RQ3, not a fourth top-level question, matching the manuscript exactly. Don't re-split this back into four without a matching manuscript change first.

The three research questions anchoring the whole review, moving from what distinguishes stroke gait at the feature level, through placement, to which classifiers and datasets have been used and how well they perform together.

## RQ1 — Discriminative features

How have gait features (spatiotemporal, kinematic, raw signal-level) been used to differentiate healthy from post-stroke gait? Answered by [[discriminative-features]], drawing on both the literature synthesis and this review's own re-mining of [[voisard-2025]] and [[felius-dataset]].

## RQ2 — Sensor placement

How do sensor placement, orientation, and position affect classification accuracy? Answered by [[sensor-placement]] and, on the deployment-practicality side, [[placement-vs-practicality]].

## RQ3 — Classification methods and the datasets behind them

How have datasets, data mining, machine learning, and deep learning techniques been used to classify and validate post-stroke gait, and how well do they perform? Answered by [[classification-methods]], whose primary evidence is the fourteen included literature studies that report a trained classification or regression model — the hands-on-mining strand's own literature-informed classification pass is a bounded exception, not the primary evidence source. The dataset-usage side of this question is answered across all 17 pages in `studies/` and all 7 pages in `datasets/`, synthesized in `synthesis.md`. The manuscript states the explicit tally in Section 4.1.1 rather than leaving it only derivable from Table 3: 11 of the 17 included studies pair a stroke sample against a genuine healthy control group collected under the same protocol (the other 6 either have no comparison arm, compare stroke against a different diagnosis, or have no stroke population at all), matching the "eleven of seventeen" figure the Conclusion already cites.

## Links

Every page in `studies/` and `datasets/` maps to at least one of these four questions. [[eligibility-criteria]] defines what counted as evidence for answering them in the first place.
