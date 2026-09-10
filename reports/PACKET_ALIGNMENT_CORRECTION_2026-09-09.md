# Native packet alignment correction and false-positive check

Executed 2026-09-09. **The timing defect is corrected in a versioned loader and
the false-positive issue persists.** This is now completed work, not a proposal
to rerun the prior audit.

## Direct frozen-model result

The same 15-member v0.2.0 weights scored the same 5,340 windows from the same
138 non-stroke participants before and after native signal alignment. Only the
input clock/interpolation changed. The 0.50 threshold and participant averaging
were unchanged. Every original window remained scoreable.

| Input version | Non-stroke participants called positive |
|---|---:|
| Historical raw-row input | 89/138 (64.5%) |
| Packet-aligned native input | 89/138 (64.5%) |

**Zero participant calls changed**, although individual scores moved by up to
0.0556. Counts by pathology also stayed unchanged: ACL 6/11, CIPN 11/19, HOA 9/15,
KOA 12/18, PD 15/24, RIL 36/51. This rules out this correction as a sufficient
fix for these errors; it does not prove the model never uses device artifacts.

This is a non-stroke stress test, not new stroke sensitivity evidence or an
independent final cohort. TVS was not rescored: this correction addresses Voisard's
packet clock, and does not establish a corresponding TVS defect. Its earlier
healthy false positives remain unresolved evidence.

## Implemented correction and verification

[Native loader](../src/data/voisard_aligned.py) uses the earliest first packet
among the four synchronized raw sensors as the common acquisition origin.
Absolute counters are mapped onto that timeline, with explicit 16-bit rollover
handling. Only bounded interior gaps of at most 150 samples are linearly
interpolated. Unsupported edges remain missing; duplicates and unexplained
backward counter resets are rejected. Floating-point counter noise is tolerated.
There is no gravity removal, filtering, axis substitution or learned alignment
in the corrected inference input. Native m/s² becomes g only at the frozen-model
input boundary.

The source of the common origin is acquisition counters, not reference events,
diagnosis or a score-optimized shift. One verified XSens example requires a
one-sample sensor offset as well as gap filling. The loader exposes a lower-level
`align_packets(frame, origin)` interface for an explicitly known acquisition
origin; matching this archive's annotations requires the shared clock metadata.

For independent signal-level verification, we applied the provider's 8th-order
14 Hz low-pass filter to the aligned native acceleration **in a separate check**,
then compared magnitudes with supplied processed LB acceleration. Magnitude avoids
the provider's sign/axis transformations. All 1,348 selected trials were checked:
maximum absolute discrepancy 0.000126 m/s²; median per-trial maximum discrepancy
approximately 4.3e-13 m/s². This verifies the clock reconstruction against the
provider processing, not against independent event truth.

The first execution rejected counter rollovers rather than silently compressing
them. A census identified conventional 65535-to-0/1 transitions; explicit unwrap
support was added and covered by a test before the completed run. Detector settings,
classification thresholds and model hyperparameters were not tuned.

## Regenerated feature comparison

Recomputed lower-back RMS for the existing 1,348 trial rows, then retained all
259 participants and their original folds. Cadence, stride variability, temporal
asymmetry and nuisance metadata were reused unchanged. Three unsupported trial
bounds now produce missing RMS rather than silently truncated slices; each of
those participants retains other valid trials. Trial validity is recorded, and
no participant was removed. Thus this feature correction includes explicit bound
validity handling as well as packet alignment.

Re-executed the 36 fixed logistic fits under the same two scopes and six arms:

| All-participant feature model | Other-pathology FPR, old → aligned | Stroke sensitivity, old → aligned |
|---|---:|---:|
| RMS only | 55.1% → 55.1% | 87.8% → 87.8% |
| Gait features | 56.5% → 56.5% | 75.5% → 75.5% |
| Combined gait + covariates | 50.7% → 50.7% | 87.8% → 87.8% |

The combined model's AUROC changes only from .7684 to .7681. RMS-only healthy
specificity drops from 90.3% to 88.9% (one additional false positive). Nuisance-only,
cadence-only and nuisance+cadence predictions are unchanged within 1e-10, as are
all strict device/protocol-matched predictions. The earlier matched RMS AUROC
.801 against healthy and .449 against other pathologies therefore remains.
These are development feature-model results, not performance of the frozen CNN.

## Artifacts and completion state

- [Executed runner](../scripts/run_packet_alignment_correction.py),
  [paired verification](../scripts/summarize_packet_alignment_correction.py),
  [four tests](../tests/test_voisard_aligned.py).
- [Frozen paired predictions](../data/processed/packet_alignment_v1/frozen_paired_comparison.csv),
  [corrected feature metrics](../data/processed/packet_alignment_v1/feature_metrics.csv),
  and [alignment audit](../data/processed/packet_alignment_v1/alignment_audit.csv).
- Protocol, trial/participant features, window coverage, corrected input tensor,
  pathology counts and verification hashes under `data/processed/packet_alignment_v1`.

Four tests passed: shared origin/interpolation, rollover with a missing packet,
rejection/preservation of unsupported gaps or resets, and exact gap-free values.
All original non-stroke windows were reconstructed against the saved old tensor
before paired scoring. Participant joins, unaffected-control predictions and
provider alignment checks passed. Historical source helpers, saved tensors and
results are preserved for reproducibility; new native extraction should use
`src/data/voisard_aligned.py`, not the historical raw-row helper.

Metadata and local raw acquisition were already complete; corrected preprocessing,
feature evaluation and frozen paired specificity evaluation are now complete.
No new download, model promotion or independent sensitivity validation occurred.
Frozen checkpoint SHA remains
`34df2abadf862d7838dcfca7917a13c872254bde8a9a6ff9f8554e7b8a3d3ea6`.

**Decision:** retain the preprocessing correction, reject any claim that it fixes
stroke specificity, and close the packet-alignment experiment. Further diagnostic
training needs a new clinically justified information source or target definition;
repeating normalization, threshold changes or this same correction is not a next
experiment. Broader native-input migration and independent measurement validation
must be explicitly versioned; the frozen release has not been silently retrained.
