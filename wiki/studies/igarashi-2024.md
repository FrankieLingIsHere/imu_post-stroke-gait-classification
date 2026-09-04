---
type: study
year: 2024
pathway: IC5
population: "35 subacute stroke inpatients (dependent n=12, independent n=23 per Functional Ambulation Category), age 75.5±9.8 — single-population, no healthy comparison group"
method: "ROC/AUC discriminant analysis with Youden-index cutoff — threshold-based, no trained classifier"
placement: "Single trunk accelerometer, L3 spine"
---

Igarashi, T., Tani, Y., Takeda, R., & Asakura, T. (2024). *Accelerometer-based gait characteristics and their discrimination of gait independence in inpatients with subacute stroke*. *Gait & Posture*, 110, 138–143. https://doi.org/10.1016/j.gaitpost.2024.04.001. Verified via a real full-text fetch (Elsevier/ScienceDirect). A seventh gap found alongside the six studies ingested 2026-08-05 — confirmed present in the manuscript's Table 3 (row 23) and cited repeatedly in Sections 4.1.3, 4.1.4, and especially 5.1, but had no wiki page until this ingest. IC5-exempt (threshold-based, no trained classifier against a comparison group), the same exemption class as [[avvenuti-2018]], [[ensink-2023]], and [[felius-2024]] — not part of [[quality-assessment]]'s four-criterion assessment.

## Key findings

- **This review's most direct external, third-party corroboration of the trunk-RMS finding from its own hands-on re-mining** — see [[discriminative-features]] and Section 5.1. Normalized root-mean-square trunk acceleration separates ambulation-dependent from ambulation-independent subacute stroke inpatients with AUC = 0.833 (vertical direction) and AUC = 0.819 (mediolateral), both "excellent" discrimination by conventional AUC benchmarks. Cutoffs: 2.20 m²/s² vertical (sensitivity 0.783, specificity 0.833) and 2.82 m²/s² mediolateral (sensitivity 0.739, specificity 0.833).
- **Two qualifications the manuscript's own Section 5.1 states directly, both worth preserving here rather than treating the AUC figures alone as unqualified corroboration**: (1) this is a within-stroke comparison, dependent-versus-independent ambulation, not stroke-versus-healthy — it corroborates trunk RMS as a graded *functional* signal, not as a diagnostic one distinguishing pathology from health. (2) It trains no classifier at all — a single-sample ROC/AUC cutoff analysis with no held-out test set, which gives an optimistic estimate of how well that specific cutoff would transport to a new sample. Because it reports no trained model, its AUC is directly comparable in kind to this review's own feature-level effect sizes in Section 4.2.2, not to the classifier accuracy figures in Table 3.
- One of three studies testing a trunk-region sensor alone, alongside [[iosa-2021]] (single sacral IMU) and [[tas-2024]] (single waist/lumbosacral accelerometer) — none of the three runs a placement comparison within its own study, so all three are read the same way: independent success at that placement, not comparative evidence it beats an alternative site.
- Functional Ambulation Category is its severity/function grouping — one of the ten included studies (of 26) reporting a severity- or function-relevant grouping rather than only a binary diagnosis label, per Section 4.1.3's tally.

## Links

The single strongest piece of external literature corroboration for [[sensor-placement]]'s trunk-RMS finding — see that page's trunk-alone-studies section and Section 5.1's discussion directly. Read alongside [[voisard-2025]]'s and [[felius-dataset]]'s own trunk-RMS effect sizes (r = 0.57 Voisard, r = 0.61 Felius raw) as feature-level, not classifier-level, evidence for the same underlying placement. Its dependent-vs-independent framing is a distinct severity/function angle from [[tas-2024]]'s Brunnstrom-stage framing and [[yang-2026]]'s SPPB framing, all three worth reading together as this review's severity-grouping literature.
