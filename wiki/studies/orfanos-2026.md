---
type: study
year: 2026
pathway: IC1
population: "16 stroke vs 16 age-matched healthy = 32 total"
method: "Multiple classifiers compared; best = Random Forest (F1=0.94, AUC=0.98)"
placement: "Bilateral shank gyroscopes (MBIENTLAB IMU)"
---

Orfanos, S., Sanghan, T., Menychtas, A., Panagopoulos, C., Maglogiannis, I., & Chatpun, S. (2026). *A lightweight machine learning framework for post-stroke gait abnormality classification using wearable gyroscope features*. *Sensors*, 26(10), 3143. https://doi.org/10.3390/s26103143. Verified via a real full-text fetch (MDPI, open access). Found via the same IEEE Xplore/Scopus supplementary search as [[scheffer-2012]], [[iosa-2021]], and [[tas-2024]]. One of three studies testing a shank placement alone, alongside [[shih-2021]] (bilateral shank IMU) — both contribute to the shank-versus-lower-back comparison [[hsu-2018]]'s own literature result anchors.

## Key findings

- Gyroscope-only feature set (z-axis angular velocity, bilateral shank), a deliberately minimal, "lightweight" feature design distinct from every other included study's accelerometer-led or mixed-signal approach — explicitly framed by the authors as suited to real-world, computationally constrained wearable and remote-monitoring deployment.
- Best result: Random Forest, F1 = 0.94, AUC = 0.98, near-perfect class separability in the confusion matrix. Support vector machine models also reached AUC = 0.98; XGBoost reached AUC = 0.97 — multiple classifiers converge on high, closely-clustered performance rather than one model dominating, a genuine multi-classifier comparison within a single study.
- One of two of the six newly-assessed studies (with itself and [[iosa-2021]]) recruiting an explicitly age-matched control group, rather than bare demographics with no stated matching rationale — the strongest control-matching practice among the six.
- [[quality-assessment]]: participant-level leave-one-out cross-validation confirmed. Data availability is partial — available on reasonable request, not open by default, a middle position between the "no statement" majority and [[pohl-2022]]/[[inui-2026]]'s public code sharing. Severity not reported (binary healthy/abnormal classification only, no graded score). Explicitly age-matched control group, the strongest comparability practice among the six newly-assessed studies alongside Iosa's explicit p>0.05 age check.

## Links

Corroborates [[shih-2021]]'s shank-placement evidence and, through it, [[hsu-2018]]'s own shank-leading literature finding discussed in [[sensor-placement]]. Its gyroscope-only, minimal-feature design is a distinct methodological contribution worth citing in [[future-directions]]'s low-burden-deployment discussion alongside [[placement-vs-practicality]]'s pocket-carried-sensor thread — both aim at the same practical-deployment goal from different angles (feature minimalism here, placement convenience there).
