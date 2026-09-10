# Pre-fit protocol: phase features at training-selected sensitivity thresholds

This follows the completed fixed-0.5 experiment. It is a development comparison,
not an untouched final evaluation. No feature or architecture selection.

Reuse the exact 259-person phase table, four arms, three outer folds and 144-person
matched subset. Keep outer participant and other-pathology separation unchanged.
Within each outer training set use three participant-stratified folds (target
0/1/2, shuffled seed 20260909). Inner pathology overlap is allowed: the matched
outer training set can contain only one other pathology. Outer pathology holdout
remains enforced. Imputation/scaling/model fitting occur inside each inner fit.
Use the previous class weighting and logistic C=1, seed 20260909.

For each arm select the largest threshold detecting at least 90% of pooled inner
OOF stroke participants: the kth largest stroke score, k=ceil(0.9*n_stroke).
Calls use score >= threshold, including ties. No outer labels or negative scores
select the threshold. This empirical inner target is not a sensitivity guarantee.
Apply to the existing exact outer-model predictions, which are identical to
refitting the unchanged model on all outer training participants.

Primary comparison: nuisance+cadence+phase versus nuisance+cadence using their
own inner-selected thresholds. Pass only if BOTH scopes have at least 90% outer
stroke sensitivity, no fewer stroke detections than baseline, no additional
healthy false positives, and at least 5 percentage points lower other-pathology
FPR. Secondary combined+phase comparison is descriptive and cannot rescue failure.
No threshold sweep or changes to these rules after observing results.

Save inner predictions, split membership, thresholds, achieved inner sensitivity,
outer predictions/calls, per-pathology counts and decision. All participants stay
in the evaluation. Acquisition and phase measurement unchanged. Clinical release
and single-sensor recovery remain outside this experiment.
