# Partial ElderNet adaptation protocol

Locked before fitting, 2026-09-09. Three matched arms: pretrained frozen encoder
with new neural head, pretrained encoder with layer5 and FC layers unfrozen,
and random encoder with the same late layers unfrozen. Earlier layers stay frozen
and all BatchNorm running statistics stay fixed. No gait-speed head is used.

Reuse exactly the corrected probe's 1,785 ten-second XYZ windows in g and its
146 available people (105 matched). Preserve all 259 in the coverage ledger.
This deliberately isolates adaptation on the same duration-selected subset;
it does not solve the severe healthy coverage loss or evaluate whole cohorts.

Three original outer folds with participant/pathology holdouts. Within each outer
training fold reserve 25% of each target group (ceil, minimum one, leave at least
one fitting participant) for threshold calibration, using seed 20260909 + fold.
No calibration participant contributes gradients. No refit after calibration.
Threshold is the largest calibration stroke score retaining at least 90% of
calibration strokes. Test labels never select training settings or thresholds.

Fixed six epochs, 30 steps/epoch, batch32. Sample targets with mass healthy .25,
stroke .50, other .25; uniform participant, uniform trial, uniform window.
AdamW weight_decay .0001, late layers lr .0001 and new linear128-to1 head lr .001.
BCEWithLogitsLoss, gradient clip1. Single seed, no early stopping or tuning.
Aggregate sigmoid scores per trial, then per participant. Same samples and initial
new-head parameters across arms. One frozen feature cache per encoder identity.

Report AUROC, stroke TP/FN, healthy/other/neurological FP and paired calls for both
scopes. Advancement requires pretrained partial adaptation to lower neurological
FPR by >=5 percentage points with no additional stroke misses or healthy FP
against BOTH controls in BOTH scopes. This exploratory gate is not clinical
validation. No automatic deployment, fusion sweep or extra epochs after results.

Save splits, calibration/test predictions, thresholds, loss curves and checks
that frozen parameters remain fixed while intended late parameters update.
The previous logistic-head results used different fitting/threshold procedures;
the new simultaneously trained frozen neural-head control is the attribution
baseline. TVS checkpoint-training overlap remains, and this is within-Voisard
evaluation, not independent cross-source validation.
