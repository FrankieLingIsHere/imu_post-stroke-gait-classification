# Conditional gait comparison — executed 2026-09-09

Later completion: [native alignment correction and paired FP results](PACKET_ALIGNMENT_CORRECTION_2026-09-09.md)
now resolves the pending implementation correction. Frozen positives remain 89/138;
original evidence and then-pending decisions below are historical.


Subsequent qualification: [event/timeline validation](LOWER_BACK_EVENT_VALIDATION_2026-09-09.md)
found packet gaps in 513 selected trials/115 people. Mixed-cohort raw RMS
interpretation is provisional pending aligned extraction; the strict matched
subset has zero packet-gap trials. Original results below are preserved.


**Decision:** the tested interpretable features do not establish stroke-specific
discrimination from other gait disorders. Do not promote a replacement. The
implementation now distinguishes healthy-control discrimination from differential
diagnosis using the same participants and recorded device/protocol information.

## Completed implementation

[Runner](../scripts/run_conditional_gait_comparison.py),
[contrast summary](../scripts/summarize_conditional_gait_contrasts.py),
[tests](../tests/test_conditional_gait_comparison.py), and
[artifacts](../data/processed/conditional_gait_v1/participant_contract.csv).

- Metadata census: 1,356 local trials, 260 participants. The previously locked
  CNN scope contains 1,348 represented trials and 259 participants: 72 healthy,
  49 stroke and 138 other-pathology participants. HS_58 is outside that existing
  scope; this comparison did not introduce a new feature-based exclusion.
- Raw signals: reused existing lower-back files; no acquisition. Metadata and
  selected raw-file hashes are recorded in the trial census/feature table.
- Preprocessing: reused the corrected event/turn helpers and walking-bound RMS.
  All four selected gait features are present in every selected trial. One other
  participant has missing age, retained with training-fold imputation.
- Evaluation: 36 logistic fits completed, six fixed feature arms by three existing
  folds by two scopes; 2,418 participant predictions. No tuning or new thresholds.
  Three focused tests passed using the existing Python 3.11 environment's unittest
  runner (pytest is not installed there).

The participant contract preserves mixed devices and protocols; it does not choose
an arbitrary first device for a person. Ten participants have both devices across
selected trials. All 49 stroke participants use TechnoConcept. The matched scope
requires **every selected trial** to use TechnoConcept and the exact
`10.0m - uturn - 10.0m` protocol: 19 healthy, 49 stroke, 76 other (144 total).
The remaining other pathologies there are CIPN, PD and RIL; ACL/HOA/KOA have no
eligible device-matched recordings. Therefore matching also changes case mix.

## Comparison contract

The existing three participant folds are reused. Whole other-pathology groups
remain excluded from training in their test fold. Device/protocol matching is a
fixed metadata rule applied before fitting, not a score-selected subset. Models
are refit separately within each scope. Matching is not age matching: mean ages
are approximately 55.9 healthy, 59.0 stroke and 64.9 other in the restricted scope.
One restricted test fold contains no other-pathology participants; pooled OOF
metrics retain all participants rather than pretending each fold has every group.

Nuisance features: age, fraction of selected trials recorded on XSens, mean
protocol-leg distance. Gait features: annotation-derived cadence, mean bilateral
stride-time CV, absolute relative difference between left/right mean stride times,
and lower-back acceleration-magnitude RMS. Each participant is one row, with trial
means. No diagnosis-derived metadata or pathology name is an input.

The event-derived features use supplied reference annotations. They are **not**
proof that a lower-back-only autonomous detector can extract these values. The
asymmetry feature is a left/right temporal descriptor, not a paretic-side label.
Cadence is not measured walking speed. Actual speed was not manufactured from
nominal course length and an incomplete event span.

All imputation/scaling fits inside training folds. Logistic regression has fixed
C=1; positive total training weight is 0.5, with 0.25 healthy and 0.25 other.
The fixed score threshold is 0.5. Brier scores are reported, but class-weighted
scores are not claimed to be prevalence-calibrated clinical probabilities.

## Results

| Scope / model | AUROC, stroke vs all negatives | Stroke sensitivity | Healthy specificity | Other-pathology FPR |
|---|---:|---:|---:|---:|
| All 259 / nuisance | .669 | 100.0% | 73.6% | 56.5% |
| All 259 / nuisance + cadence | .798 | 87.8% | 81.9% | 52.9% |
| All 259 / RMS only | .729 | 87.8% | 90.3% | 55.1% |
| All 259 / gait | .700 | 75.5% | 87.5% | 56.5% |
| All 259 / combined | .768 | 87.8% | 81.9% | 50.7% |
| Matched 144 / nuisance | .379 | 44.9% | 42.1% | 64.5% |
| Matched 144 / nuisance + cadence | .671 | 69.4% | 78.9% | 46.1% |
| Matched 144 / RMS only | .520 | 65.3% | 84.2% | 69.7% |
| Matched 144 / gait | .605 | 63.3% | 84.2% | 55.3% |
| Matched 144 / combined | .606 | 63.3% | 84.2% | 56.6% |

The strongest interpretation comes from separating the negatives:

| Matched 144 model | AUROC stroke vs healthy (68 people) | AUROC stroke vs other (125 people) |
|---|---:|---:|
| RMS only | .801 | .449 |
| Nuisance + cadence | .806 | .637 |
| Combined | .810 | .555 |

Thus RMS still carries healthy-versus-stroke information on matched hardware and
protocol. Its failure against other disorders explains why a useful group marker
can be inadequate for differential diagnosis. This does not contradict historical
device-matched healthy-versus-stroke feature-effect results.

Paired 1,000-resample participant bootstrap, stratified by target, finds combined
minus nuisance+cadence AUROC differences of -.029 overall (95% interval
[-.056, -.003]) and -.065 matched ([-.120, -.011]). Matched other FPR difference is
+10.5 percentage points, interval [+1.3, +19.7]. These are conditional on the
already fitted OOF models, not uncertainty from retraining or new sites; contrasts
are exploratory and not multiplicity-adjusted. Other metrics are saved alongside.

Existing binary-exposure CNN OOF scores, averaged across its three prior seeds,
are joined for context: AUROC .826 overall and .647 on the matched subset; matched
other FPR 63.2%. These CNN models were trained on the full-device folds, whereas
the matched feature models were refit in the restricted scope. This is descriptive
context, not a controlled claim that either architecture wins. These scores are
also distinct from the frozen 15-member ensemble and from mean-per-seed metrics.

## What changed in our understanding

Verified: device/label overlap is limited, apparently strong healthy-control
discrimination is much weaker against other pathologies, and adding the tested
variability/asymmetry/RMS features beyond cadence and covariates does not help.
The tested nuisance features can themselves predict labels in the mixed cohort.
This demonstrates a shortcut opportunity, not that the frozen CNN necessarily
uses those covariates. Matching changes training size, ages and pathology mix;
the AUROC drop cannot be assigned causally to hardware alone.

Completed: participant contract, overlap accounting, reference-assisted feature
comparison and sensitivity-preserving improvement check (not passed). Still open:
autonomous event measurement validation, richer validated directional/side-specific
features, and independent cross-source conditional validation. None is claimed
complete by these within-Voisard results.

**Next bounded implementation:** validate an autonomous lower-back event/cadence
adapter against the existing reference events with diagnosis-stratified failure
coverage, before fitting another diagnostic classifier. This can establish which
measurements the intended sensor actually supports. Adding the present feature
set to the CNN is not justified by these results. If stronger measurements remain
non-specific, narrow the endpoint to gait impairment assessment.

Frozen v0.2.0 SHA-256 remains
`34df2abadf862d7838dcfca7917a13c872254bde8a9a6ff9f8554e7b8a3d3ea6`.
No new package, data download or model promotion occurred. No job remains running.
