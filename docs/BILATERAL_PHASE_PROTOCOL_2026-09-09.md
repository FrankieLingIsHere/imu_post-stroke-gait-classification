# Locked bilateral phase feasibility protocol

Written before fitting this experiment. Research feasibility, not release admission.
Reuse all 259 selected participants, existing three participant/pathology folds,
and corrected packet-alignment covariates. Repeat on the existing 144-person
device/protocol-matched subset. No acquisition or release-weight changes.

Four fixed arms: nuisance+cadence, that baseline+five phase features, previous
combined gait+covariates, previous combined+phase. Same class weights, median
training-fold imputation with indicators, standard scaling and C=1 logistic
regression as the corrected comparison. Fixed decision threshold 0.5.

Primary gate: baseline+phase must reduce other-pathology false-positive rate by
at least 5 percentage points, with zero additional missed stroke participants and
zero additional healthy false positives, in BOTH scopes. Combined+phase is a
secondary comparison and cannot rescue a failed primary gate. This is a project
decision rule, not a clinical standard. No threshold or feature selection after
seeing results. Report counts, AUROC, per-pathology results and missing coverage.

Features: normalized absolute side-mean step/swing/stance duration differences,
mean swing/stride fraction, mean double-support/stride fraction. Each cycle
requires ordered same-foot TO, HS, next TO, next HS and exactly one intervening
opposite HS. No cycle crosses turns or explicitly malformed rows. Step pairs
derive from opposite HS within those cycles. Double support is the intersection
of stance intervals and requires opposite-foot valid cycles covering the entire
reference left HS-to-HS cycle. At least two observations per side for asymmetry,
four cycle fractions and two support cycles per trial. Trial features are averaged
equally per participant, retaining NaNs and reporting coverage. No diagnosis or
deficit-side information enters the extractor or predictor list.

Annotations alone supply phase information, so this does not validate raw-signal
recovery or event measurement accuracy. Preserve every selected trial and person
in the accounting, including annotations flagged invalid in the earlier signal
bounds check: these trials contribute missing phase features. Algorithm-derived
annotations and reused development data limit causal and generalization claims.
