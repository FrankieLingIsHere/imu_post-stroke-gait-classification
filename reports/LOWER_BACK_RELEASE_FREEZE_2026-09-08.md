# Lower-back ensemble freeze — 2026-09-08

## Prior-work check

Before training, inspected checkpoints in `models/` and `data/processed/`,
searched project notebooks/scripts/reports for the release ID and freezer calls,
and searched Documents and Downloads for lower-back ensemble artifacts.
Found the historical single-member `full_expanded_lower_back_only_seed_42.pt`
and notebook-29 prediction/decision tables, but no v0.2.0 ensemble checkpoint,
release manifest, freeze tuning table or completed freeze run. This establishes
absence in the searched locations, not in every possible backup or machine.
Earlier references to a frozen ensemble meant a frozen selection decision.

## Audited procedure

Uses the existing notebook-29 `train_model`, unchanged methods, seeds, optimizer
settings, source/class window balancing, training-only normalization and epoch
ranking. A participant-disjoint 20% validation split within each of the six
source/class cells selects full-development duration. This differs from OOF
evaluation, where an entire source is excluded. It does not create new unbiased
performance estimates.

Data: 22,506 windows, 314 participants, Felius/Voisard/Sint only. All three methods
selected eight epochs. Fifteen members comprise ERM, CORAL and ERM++-style for
seeds 42, 137, 202, 314 and 515. Each uses only channel zero, lower-back magnitude.

Repairs made before execution: refuse existing freeze artifacts, enforce source
identity and consistent participant labels, record participant tuning assignments,
hash input metadata and implementation files, and compare training/package
inference for every member on 48 development windows across six source/class cells.
No external cohort was loaded, and no architecture or threshold search was added.

## Runtime and verification

Environment: `C:/Users/frank/.venv-cu130/Scripts/python.exe`, Python 3.11.9,
PyTorch 2.14.0.dev20260707+cu130, RTX 5060 Laptop GPU. Installed missing pandas
and scikit-learn dependencies in that existing environment. Exact versions are
recorded in the release manifest.

Nine synthetic tests passed, including recipe equality, participant-disjoint
splits, identical architecture outputs, input/member validation, checksum tamper
rejection and probability averaging.

Release execution and post-save verification: complete. CPU and GPU packaged
inference matched the training implementation on 96 development windows with
maximum absolute differences 1.27e-7 and 1.34e-7, respectively. The real CLI
passed with maximum difference 1.27e-7. Smoke checks passed at the original 1e-6
tolerance. These are numerical equivalence checks, not performance evaluation.

The first post-training smoke check failed at 3.87e-6 because cuDNN TF32 inference
was enabled. Disabling TF32 reduced the CPU/GPU discrepancy below tolerance.
Preserved the original checkpoint and training-source snapshot, regenerated smoke
expectations in float32, and finalized the manifest without retraining any member.
The recovery provenance is recorded in the manifest. Both the predictor and
future freezer verification explicitly disable TF32 convolution for inference;
the original training recipe remains unchanged. The final small freezer repair
aligns its reference verification precision too; that updated freezer was not
used to retrain the completed checkpoint.

Final checkpoint SHA-256:
`34df2abadf862d7838dcfca7917a13c872254bde8a9a6ff9f8554e7b8a3d3ea6`.

## Reproduction and artifact locations

```powershell
& C:/Users/frank/.venv-cu130/Scripts/python.exe -m src.models.freeze_lower_back_ensemble
& C:/Users/frank/.venv-cu130/Scripts/python.exe scripts/verify_lower_back_release.py
& C:/Users/frank/.venv-cu130/Scripts/python.exe -m unittest discover -s tests -v
```

The freezer refuses to overwrite prior artifacts. Verify an existing release
instead of rerunning training. Checkpoint and manifest live in `models/checkpoints/`.
Private split/tuning/verification files and the run log live in `data/processed/`.
These artifacts remain Git-ignored; no participant data or weights are published.

This work freezes model weights and saved normalization. Final-test threshold,
calibration, abstention, clinical metadata/provenance and cohort-acceptance gates
remain separate unfinished requirements. No new classification-performance claim
is supported by this full-development fit.
