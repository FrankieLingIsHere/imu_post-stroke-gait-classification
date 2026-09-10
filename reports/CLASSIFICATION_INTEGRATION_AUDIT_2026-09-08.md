# Classification integration audit — 2026-09-08

Historical initial audit. The absent-weight finding below was resolved later
the same day by the [completed freeze and verification](LOWER_BACK_RELEASE_FREEZE_2026-09-08.md).
Other uncompleted integration gates remain applicable.

Scope: package inspection and inference contract implementation, with no training,
external signal loading, cohort acquisition, or outreach.

## Findings and repair

- README and notebooks 29/30/34 select a lower-back ensemble. The old model card,
  package README and `models/predict.py` describe the historical three-channel model.
  Package documentation now distinguishes these explicitly. The old command remains
  available for historical reproducibility.
- `src/models/freeze_lower_back_ensemble.py` already builds 15 members with saved
  normalization, manifest hashes and synthetic smoke predictions. No corresponding
  checkpoint or manifest exists in the local `models/checkpoints/` directory.
- Added `models/predict_lower_back.py` with restricted checkpoint loading, checksum
  verification, strict contract/member validation, batched inference and smoke checks.
- Full-development fitted predictions must not be compared for equality with
  out-of-source predictions from notebook 29. They use different training sets.
  Inference equivalence must compare the same weights and inputs; OOF reproduction
  remains a separate validation requirement.
- The recruitment checklist is currently stored under ignored `data/interim/`, and
  its introductory development/adaptation language does not fully implement the
  plan's final-test acceptance gate. A tracked, executable intake gate is still needed.
- Bilateral feet are required by the planned cohort gate but not by the primary
  one-channel model. Keep this distinction explicit when discussing provider schemas;
  changing eligibility would require a documented protocol decision before test access.

## Remaining gates

Freeze and verify the actual ensemble on the established
development environment, reproduce the classical comparator and OOF evidence,
audit provenance/metadata and hard-negative results, then lock threshold,
calibration, abstention, participant manifests and software provenance. Do not
open a new cohort before those gates pass. Contact shortlist entries are unaccepted
leads. No new contact details or registry claims were verified in this code-only pass.

## Verification

Executed six synthetic unit tests successfully with
`C:/Users/frank/.venv-cu130/Scripts/python.exe` (Python 3.11.9,
PyTorch `2.14.0.dev20260707+cu130`, CUDA available). Checks cover valid inference
and batch invariance, probability averaging, duplicate members, invalid input,
invalid normalization, and checksum roundtrip/tamper rejection. CLI help also
executes successfully. Tests ran on CPU; actual release-weight equivalence and
GPU inference remain unverified because the release checkpoint is absent.

The initial sandbox could not see the installed Python interpreter. Escalated
discovery located both `.venv` and `.venv-cu130` under the user home directory;
no new environment or dependencies were installed.
