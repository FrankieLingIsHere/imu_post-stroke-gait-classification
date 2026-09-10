# Bilateral phase-feature experiment, 2026-09-09

> Reporting migration (2026-09-10): [saved-output notebook](../notebooks/36_phase_measurement_saved_results.ipynb). Historical script commands below refer to the original Git revision recorded in that notebook; no new experiment was run.

**Executed: primary gate failed in both scopes. False positives remain.**

The five annotation-derived phase features improve out-of-fold AUROC and reduce
false positives, but the primary comparison loses stroke detections. This is
evidence of incremental predictive information in this development sample,
not proof of a causal mechanism or an independently validated model.

[Pre-fit protocol](../docs/BILATERAL_PHASE_PROTOCOL_2026-09-09.md).
Four fixed arms, three existing participant/pathology folds, fixed threshold 0.5.
All 259 selected participants retained, including the 144-person device/protocol
subset (49 stroke, 19 healthy, 76 other). This subset is not age matched.

| Scope | Arm | Stroke detected / 49 | Healthy FP | Other FP | AUROC |
|---|---|---:|---:|---:|---:|
| all_selected | combined | 43/49 | 13/72 | 70/138 | 0.768 |
| all_selected | combined_phase | 42/49 | 11/72 | 64/138 | 0.820 |
| all_selected | nuisance_cadence | 43/49 | 13/72 | 73/138 | 0.798 |
| all_selected | nuisance_cadence_phase | 41/49 | 11/72 | 64/138 | 0.836 |
| device_protocol_matched | combined | 31/49 | 3/19 | 43/76 | 0.606 |
| device_protocol_matched | combined_phase | 31/49 | 2/19 | 31/76 | 0.687 |
| device_protocol_matched | nuisance_cadence | 34/49 | 4/19 | 35/76 | 0.671 |
| device_protocol_matched | nuisance_cadence_phase | 30/49 | 2/19 | 26/76 | 0.727 |

The primary nuisance+cadence+phase arm reduces other FP by 9/138 in the
full sample and 9/76 in the matched subset, but loses two and four stroke
detections respectively. Both fail the locked sensitivity-preserving gate.
The secondary combined+phase arm reduces matched other FP from 43 to 31
without changing 31/49 stroke detections. Its full-sample comparison loses
one stroke detection (43 to 42), so this does not rescue the primary decision.

## Measurement and verification

- 1348 selected trials processed, 1345 with complete phase features.
- Three previously invalid reference-bound trials remain in the ledger with missing phase features.
- All 259 participants have complete aggregated phase features. No participant was dropped.
- Invalid cycles are counted by pathology. No diagnosis or deficit-side field enters predictors.
- Features use TO/HS annotations, not newly estimated single-sensor events.
- Double support uses fully covered left HS-to-HS cycles and stance intersections.
  Finite-bout coverage can depend on the reference side. No paretic-side inference is used.
- Four synthetic unit tests passed: symmetric gait/support, equal-stride unequal-step
  timing with side swap, turns/missing contacts, malformed/empty events.
- Reproduced all 806 baseline participant predictions, maximum score difference 3.16e-15.
- Protocol and input hashes, per-trial metadata hashes, features, predictions,
  pathology counts and coverage are saved in `data/processed/bilateral_phase_v1/`.

## Conditional uncertainty

Paired 2,000-resample participant bootstrap of fixed OOF calls, new minus baseline.
These intervals do not include model retraining or uncertainty across new cohorts.

| Scope | Measure | Change, percentage points | 95% interval |
|---|---|---:|---:|
| all_selected | healthy_fpr_change | -2.8 | -6.9 to 0.0 |
| all_selected | stroke_sensitivity_change | -4.1 | -14.3 to 6.1 |
| all_selected | other_fpr_change | -6.5 | -11.6 to -1.4 |
| device_protocol_matched | healthy_fpr_change | -10.5 | -26.3 to 0.0 |
| device_protocol_matched | stroke_sensitivity_change | -8.2 | -20.4 to 4.1 |
| device_protocol_matched | other_fpr_change | -11.8 | -25.0 to 1.3 |

## Decision and next unresolved question

Do not promote this candidate or repeat the same fixed-threshold comparison.
The next bounded question is whether the added information improves specificity
at a sensitivity target selected entirely within training folds. That requires
a separately locked nested validation design and the same baseline control.
Selecting a threshold on these outer-fold labels would invalidate that test.
Even a successful development result would still need independent cohort and
sensor-only measurement validation. Missing phase information is not established
as the unique cause of the frozen CNN errors.

Metadata and raw acquisition: unchanged, no downloads. Phase preprocessing and
the 24 logistic fits: completed. Frozen model: unchanged, historical 89/138
other-pathology positives still apply, not rerun here. No clinical release.

Reproduce with the existing Python environment:

```powershell
& C:/Users/frank/.venv-cu130/Scripts/python.exe -m unittest discover -s tests -p test_bilateral_phase.py
& C:/Users/frank/.venv-cu130/Scripts/python.exe scripts/run_bilateral_phase_comparison.py
& C:/Users/frank/.venv-cu130/Scripts/python.exe scripts/summarize_bilateral_phase_comparison.py
```
