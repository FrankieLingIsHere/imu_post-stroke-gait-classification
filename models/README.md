# Research checkpoint package

This directory makes the selected research-prototype checkpoint testable without distributing any participant data.

## Release candidate

| Field | Value |
| --- | --- |
| Identifier | `stroke-gait-inception-v0.1.0` |
| Weight source | `full_expanded_inception_prototype_seed_42.pt` |
| Architecture | two-block Inception-style 1-D CNN, 29,962 parameters |
| Input | `(windows, 500, 3)` float array: 5 seconds at 100 Hz, acceleration magnitudes ordered `LB, LF, RF` |
| Training sources | Felius + Voisard + Sint Maartenskliniek |
| Development cohort | 314 participants, 22,506 healthy/stroke windows |
| Seed / training | 42 / 15 GPU epochs / source-class-balanced sampling |
| Checkpoint SHA-256 | `5ea8c249814dc80cb478f4a26ac45e6d01248b7df127f1db1caa537a6bd0d02d` |

Read [MODEL_CARD.md](MODEL_CARD.md) before use. It explains what the checkpoint can and cannot support.

## Obtain the weight

The public repository intentionally does not include model weights. Before the first release, upload the checkpoint unchanged to a versioned research-artifact service such as Zenodo or Hugging Face, then replace the placeholder below with the immutable release URL and DOI.

```text
Release URL: PENDING — publish only after licence, author list, and model-card review
Expected filename: stroke-gait-inception-v0.1.0.pt
```

Put the downloaded file in `models/checkpoints/stroke-gait-inception-v0.1.0.pt` and verify its SHA-256 before loading it.

```powershell
Get-FileHash models\checkpoints\stroke-gait-inception-v0.1.0.pt -Algorithm SHA256
```

## Test inference

The input must be a NumPy `.npy` array of finite, already harmonised acceleration magnitudes with shape `(n_windows, 500, 3)`. The script returns per-window stroke probabilities; it does not make clinical decisions or impose a deployment threshold.

```powershell
python models\predict.py `
  --checkpoint models\checkpoints\stroke-gait-inception-v0.1.0.pt `
  --windows path\to\lb_lf_rf_windows.npy `
  --output predictions.csv
```

The preprocessing contract is strict. Do not substitute pelvis for lower back, reorder the channels, use raw axes in place of magnitudes, or fit new normalisation statistics on the test input.

