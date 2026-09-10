# Research checkpoint package

The selected research model is the one-channel, 15-member lower-back ensemble
`stroke-gait-lower-back-ensemble-v0.2.0`. The checkpoint was trained and verified
locally on 2026-09-08, following the earlier audit that found it absent.
All 15 members use eight epochs. CPU, GPU and CLI inference passed against the
training implementation. See [the freeze report](../reports/LOWER_BACK_RELEASE_FREEZE_2026-09-08.md).
This is a local research artifact, not a published or clinically validated release.

Checkpoint SHA-256: `34df2abadf862d7838dcfca7917a13c872254bde8a9a6ff9f8554e7b8a3d3ea6`.

Once a trusted checkpoint and its manifest have been produced and verified:

```powershell
python -m models.predict_lower_back --checkpoint models/checkpoints/stroke-gait-lower-back-ensemble-v0.2.0.pt --manifest models/checkpoints/stroke-gait-lower-back-ensemble-v0.2.0.manifest.json --windows lower_back_windows.npy --output probabilities.csv
```

Input is finite `(n_windows, 500, 1)` lower-back acceleration magnitude in g,
100 Hz, five seconds. Normalization comes only from each saved member.
The command verifies the checksum, contract, member composition and saved smoke
predictions before inference. Obtain the manifest from a trusted release source;
a checksum alone does not authenticate its publisher. Output is window probability,
which must be averaged by participant before evaluation. No threshold or calibration
is applied. This command does not establish source placement or walking provenance.

## Historical three-channel package

The remaining instructions describe the historical comparator only.
`predict.py` intentionally remains its checksum-pinned inference entry point.

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

Downloaded ElderNet and gait_cnn implementations under `models/pretrained/` and
`models/research/` remain local dependencies. Their pinned sources and revisions
are documented in [ElderNet transfer](../docs/classification/archive/2026-09/ELDERNET_TRANSFER.md)
and [gait_cnn review](../docs/classification/archive/2026-09/GAIT_CNN_REVIEW.md). Git excludes these
downloaded directories, locally fitted prototype `model.joblib` files and generated
prototype examples. These files remain on disk, but are not bundled with a source
checkout. Prototype manifests, builders and input contracts remain reviewable.

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

