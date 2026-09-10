# Predeclared v0.2.0 non-stroke stress test

Recorded before inference on 2026-09-08. No existing v0.2.0 result was found.

- Checkpoint: `stroke-gait-lower-back-ensemble-v0.2.0`, SHA-256
  `34df2abadf862d7838dcfca7917a13c872254bde8a9a6ff9f8554e7b8a3d3ea6`.
- Cohort: previously inspected Voisard ACL/CIPN/HOA/KOA/PD/RIL participants.
  Reuse `magnitude_windows` from the historical evaluator, select channel zero.
  Require identical participant identities, pathology labels and window counts
  to the historical 138-person, 5,340-window cohort before inference.
- Verify participant keys against the saved full-development freeze manifest.
  This is an identifier-based overlap check, not proof against undisclosed aliases.
- Inputs: lower-back magnitude in g, 100 Hz, 500 samples, existing straight-walk
  bounds, 250-sample hop. Saved member normalization only.
- Score: equal probability average of 15 members, then mean over all windows
  per participant. Positive if score >= 0.50, descriptive reference only.
- No calibration, abstention, threshold selection, retraining or outcome-based
  exclusions. Never apply the historical 0.78 rule to the new ensemble.
- Report non-stroke positive-call counts/rates and 95% Wilson intervals by
  pathology and pooled; retain trial failure/exclusion accounting and missing age.
- Historical 0.50 counts may be shown for context on matched participants,
  without a superiority claim. Stroke sensitivity cannot be measured here.
- Abort before scoring on identity/count mismatch, failed loading or leakage.
  Write new versioned outputs, never overwrite historical predictions.
- Save checkpoint/protocol/adapter/input hashes, software versions and results.

This is a same-protocol, already-inspected research stress test. Participants
also appeared in historical exposure experiments. It cannot provide untouched
external validation or resolve clinical stroke specificity by itself.
