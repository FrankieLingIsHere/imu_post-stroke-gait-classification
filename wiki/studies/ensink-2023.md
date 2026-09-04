---
type: study
year: 2023
pathway: IC5
population: "10 stroke, chronic phase (61±11y) vs 20 healthy (59±12y)"
method: "Threshold-based/rule-based gait-event detection algorithm (non-machine-learning)"
placement: "4 IMUs: bilateral foot, sternum, lower back (100 Hz)"
---

Ensink et al. (2023), *Validation of an algorithm to assess regular and irregular gait using inertial sensors in healthy and stroke individuals*, *PeerJ* 11:e16641. One of nine records left pending after the original two search rounds — resolved through a supplementary screening pass and confirmed eligible via the same IC5 logic as [[avvenuti-2018]].

## Key findings

- Initial-contact timing error 10ms (stroke) / 15ms (healthy); stride time difference 0ms (SD 0.01–0.05s). Validated against 3D optical motion capture (26 markers), stride-by-stride Bland-Altman comparison.
- Severity: Functional Ambulation Category 3–5; chronicity described as "chronic phase after stroke."
- Code publicly available on GitHub.
- Exempt from [[quality-assessment]] by design (IC5-admitted, threshold-based method, no trained classifier).

## Links

Resolved via the same supplementary screening pass that also formally added [[felius-2024]] and [[wu-2025]] to Table 3 — see `log.md` for the exact ingest record. Parallels [[avvenuti-2018]] as a detection-method-evaluation study.
