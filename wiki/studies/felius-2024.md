---
type: study
year: 2024
pathway: IC5
population: "107 stroke (77 longitudinal + 30 test-retest) vs 37 healthy (26 adult + 11 elderly)"
method: "Convolutional variational autoencoder, 12 latent features (unsupervised)"
placement: "2 IMUs: bilateral foot (104 Hz, downsampled to 100 Hz)"
---

Felius et al. (2024), *Exploring unsupervised feature extraction of IMU-based gait data in stroke rehabilitation using a variational autoencoder*, *PLOS ONE* 19(10):e0304558. **Plays two distinct roles in this review**: it is both a formally included literature study (this page) and one of two real, paired stroke-and-healthy datasets independently re-mined in this review's own hands-on data mining (see [[felius-dataset]]). The two roles are kept clearly distinguished — this page covers what the *published paper* reports; [[felius-dataset]] covers what *this review's own re-mining* of its raw signal data found.

## Key findings (as a literature study)

- Reconstruction MSE = 0.004 (SD 0.003). 7 of 12 latent features significantly differed stroke vs. healthy, with the strongest feature effect size (Hedges' g = 3.00) exceeding gait speed's (g = 2.6).
- Applies deep learning in a wholly unsupervised way — no classification task, no accuracy figure comparable to [[wang-2021]], [[shin-2022]], or [[lee-2025]]'s supervised classifiers.
- Was already discussed narratively and already used in this review's own hands-on mining well before it was formally added to Table 3 — the supplementary screening pass that added it was closing an administrative gap, not a new discovery.
- Exempt from [[quality-assessment]] by design (IC5-admitted via the feature-extraction pathway, no trained classifier in the comparison sense).

## Links

See [[felius-dataset]] for this review's own independent re-mining of the same underlying data. Discussed in [[classification-methods]] as the clearest example of deep learning applied outside a classification task.
