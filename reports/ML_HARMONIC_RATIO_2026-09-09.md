# Nominal medio-lateral harmonic ratio: executed comparison

**Improved development results, but both locked primary gates failed. No promotion.**

[Pre-fit protocol](../docs/ML_HARMONIC_RATIO_PROTOCOL_2026-09-09.md).
One added predictor: mean log1p of stride-resolved odd/even harmonic amplitude ratio
from provider-processed nominal lower-back Y. This is not calibrated anatomical
acceleration or an exact replication of a literature pipeline. Annotation-assisted
stride boundaries remain necessary. Both-side overlapping cycles are aggregated
to trials and then participants, not treated as independent training observations.

## Main nested-threshold results

| Scope | Model | Stroke detected /49 | Healthy FP | Other FP |
|---|---|---:|---:|---:|
| Full | Nuisance+cadence | 44 | 12/72 | 61/138 |
| Full | Nuisance+cadence+phase | 41 | 11/72 | 59/138 |
| Full | Nuisance+cadence+phase+HR | 45 | 6/72 | 56/138 |
| Full | Combined+phase | 43 | 12/72 | 62/138 |
| Full | Combined+phase+HR | 45 | 8/72 | 52/138 |
| Matched | Nuisance+cadence | 44 | 15/19 | 69/76 |
| Matched | Nuisance+cadence+phase | 42 | 13/19 | 61/76 |
| Matched | Nuisance+cadence+phase+HR | 44 | 5/19 | 47/76 |
| Matched | Combined+phase | 45 | 13/19 | 62/76 |
| Matched | Combined+phase+HR | 45 | 9/19 | 56/76 |

The primary matched HR addition reduces other FP by 14/76 and healthy FP by 8/19
while detecting two more stroke participants than the phase baseline. However,
44/49 sensitivity is 89.8%, below the locked 90% requirement. Full-sample primary
other FPR reduction is 3/138 (2.17pp) versus phase and 5/138 (3.62pp) versus original
nuisance+cadence, both below the five-point requirement. These gates are not relaxed.
Secondary combined+HR results cannot rescue the failed primary decision.

## Coverage and orientation sensitivity

All 259 participants have main HR features, from 1,345/1,348 trials. Three invalid
reference-bound trials remain in the ledger with missing values. No participant
is excluded. The orientation proxy accepts 1,165 trial rows. The screened variant
has participant HR available for 245/259: healthy 68/72, stroke 47/49, ACL 11/11,
CIPN 19/19, HOA 15/15, KOA 17/18, PD 23/24, RIL 45/51. All participants remain in
the screened model, with missing values imputed only within training folds.

Screened primary HR results: full 42/49 stroke, 6/72 healthy FP, 53/138 other FP;
matched 42/49 stroke, 6/19 healthy FP, 48/76 other FP. Screened combined+HR matched
results deteriorate to 44/49 stroke, 8/19 healthy FP, 67/76 other FP. Thus the gains
are not uniformly robust to the quality proxy. This comparison changes feature
availability as well as trial composition and does not identify a causal
orientation effect. The initial-second gravity proxy is not validated standstill.

## Verification and uncertainty

Three synthetic tests passed: known ratio and sign/scale/offset invariance,
invalid/flat/short signals, and turn/bounds handling. Main coverage gate passed in
every group. Existing baselines were reused unchanged. Ran 72 inner and 24 outer
logistic fits, with train-only imputation/scaling and inner-selected thresholds.
Outer participant/pathology holdout is asserted. Inner folds are participant
stratified, not pathology-disjoint, matching the prior protocol.

Paired 2,000-resample participant bootstrap of fixed OOF calls, HR minus phase:
matched other FPR change -18.4pp (95% interval -31.6 to -5.3), stroke sensitivity
+4.1pp (-6.1 to +14.3). Full other FPR change -2.2pp (-9.4 to +5.1).
Intervals are conditional on fitted models and do not capture retraining or new
cohort uncertainty. Reused development data and overlapping scopes are not
independent validation.

## Decision and continuation

Retain HR as a promising research feature, not a released diagnostic improvement.
False positives remain substantial: main primary matched 47/76 other positive.
Do not repeat a threshold sweep or lower the sensitivity requirement. Next priority
is gyro-assisted measurement validation, starting with the laterality contract and
independent event-reference availability. A validated event-side classifier would
not itself establish stroke specificity. OOD remains a separate lower-priority task.

Saved `data/processed/directional_hr_v1/` contains protocol/input/code hashes,
signal/metadata hashes, trial features, both participant tables, coverage, inner
predictions, thresholds, 4,836 outer prediction rows, pathology counts, metrics,
paired uncertainty and gate decision. Runner: `scripts/run_directional_hr.py`.
Metadata/raw acquisition unchanged. HR preprocessing and evaluation complete.
Frozen release unchanged, no background job. Its historical 89/138 other FP is a
different model result and was not rerun here.
