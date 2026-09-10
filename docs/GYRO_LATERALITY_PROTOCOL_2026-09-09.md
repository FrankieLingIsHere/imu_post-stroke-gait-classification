# Locked conditional gyro laterality feasibility

Use selected 259 participants/1348 trial ledger, existing outer participant/pathology
folds, full and device/protocol matched scopes. No diagnosis or deficit-side input.
Reference times and left/right labels are algorithm-derived foot annotations,
not independent gold standard. This isolates laterality conditional on supplied
initial-contact times; it cannot validate event detection, final contacts or support.

Provider-processed LB_Gyr_X and LB_Gyr_Z are nominal vertical and AP axes. Train a
fresh model on these consistent stored axes, with no label-driven sign reversal.
This is inspired by Ullrich feature types, not reproduction of its pretrained model.
Per straight reference bout: fourth-order 0.5-2 Hz zero-phase Butterworth, filtered
values and first/second sample gradients at each HS (six predictors). Keep samples
inside bout only. Invalid/nonfinite bouts retained as missing events in coverage.
Invalid reference-bound trials provide no feature rows. Duplicate IC times within
a bout are rejected, not labeled by ordering. No alternating-step labels inferred.

Fresh MinMaxScaler + linear SVC C=1 per outer training fold. Participant-equal total
weights, split equally between left/right within each training participant. Both
sides required for training, report any exclusion. No hyperparameter search. Use
held-out predictions for participant-macro accuracy by each pathology and scope.

Feasibility gate: >=90% participant-macro side accuracy and >=95% eligible contact
coverage in every group in both scopes. Missing participants count zero accuracy.
This threshold is a project screening rule, not a clinical standard. Do not flip
labels after seeing results. Save per-contact predictions, coverage, fold counts,
input/code hashes. Even passing only justifies a later predicted-contact test.
No pretrained sklearn pickle, no environment downgrade, no release changes.
