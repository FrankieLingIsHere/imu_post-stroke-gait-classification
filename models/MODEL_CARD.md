# Model card: stroke-gait-inception-v0.1.0

## Intended purpose

This is a research prototype that estimates a window-level post-stroke-gait probability from three wearable-IMU acceleration-magnitude channels. It is suitable only for technical reproducibility experiments on data that match the documented input contract.

It is **not** a medical device, diagnostic tool, triage system, or clinical decision-support system. It must not be used for individual diagnosis, treatment, risk assessment, or unsupervised clinical deployment.

## Model and input contract

- Architecture: two Inception-style 1-D convolution blocks followed by global average pooling and a linear logit head (29,962 parameters).
- Input: a finite NumPy array shaped `(n_windows, 500, 3)`.
- Sampling/windowing: 100 Hz; 5-second windows; no channel is optional.
- Channel order: `LB`, `LF`, `RF` — lower-back acceleration magnitude, left-foot acceleration magnitude, right-foot acceleration magnitude.
- Normalisation: use the mean and standard deviation stored inside the trusted checkpoint. Never estimate them from the test data.
- Output: sigmoid-transformed window-level probability. Participant-level research analyses aggregate windows by participant before computing evaluation metrics.

## Training provenance

The release candidate was fit on source/class-balanced windows from Felius, Voisard, and Sint Maartenskliniek: 314 participants and 22,506 healthy/stroke windows. Training used seed 42, 15 GPU epochs, and full-development normalisation. The full checkpoint is a prototype fit, not an internally unbiased final-performance estimate.

## Evidence snapshot

The checkpoint was evaluated once on the untouched RevalExo paired external cohort (17 participants: 7 healthy, 10 stroke). At the descriptive 0.50 reference threshold it recorded AUROC 0.9143, Brier score 0.1611, and balanced accuracy 0.7143. RevalExo is small; its threshold-dependent uncertainty is wide. These values are research results for that cohort, not general clinical performance claims.

## Known limitations

- The operating threshold and deployment calibration are not locked for clinical use.
- External paired validation is small and cannot establish population-wide generalisation.
- The model has only been assessed under the stated sensor placement, walking protocol, preprocessing, and cohort conditions.
- Healthy-population enrichment and distribution-shift work remain active research areas.
- Raw recordings and derived participant data are not distributed with this model.

## Safe distribution

Publish the checkpoint only as an immutable, checksum-verified research artefact with this model card, `stroke_gait_inception.py`, `predict.py`, exact dependency versions, and the original dataset citations/licence notices. Do not publish training data, predictions, participant metadata, or frozen-evaluation data alongside it.

