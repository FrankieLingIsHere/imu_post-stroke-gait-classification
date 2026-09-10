# Controlled regularization and warm-up experiment

Locked 2026-09-09 before fits. Same VGA target,248 first-session participants,
84 normal-rated/164 impaired-rated,11 unknown, existing role splits/frame6 and
class/person/trial weights. No new labels, downloads or preprocessing choices.

Three arms, seeds42/137/202 and three outer folds:27 fits,40 epochs each, no early
stopping. Actual upstream CNN unchanged. Adam, batch32, learning rate cosine from
.001 to.00001 over40 epochs. `fixed` has zero weight decay; `decay` differs only
by decoupled weight_decay=.01 (including biases); `warmup` differs from fixed only
by multiplying the first five scheduled learning rates by(epoch+1)/5. No dropout,
clipping, augmentation or combined decay+warm-up arm in this isolation experiment.
These are selected experimental settings, not a demonstrated optimal recipe.

Every arm runs40 epochs. Save minimum-validation-loss weights, not final weights.
Log all epoch losses/LRs and best epoch. Report whether best validation loss occurs
after a simulated patience8 stop on the SAME new schedule. This is not an exact
counterfactual of the older ReduceLROnPlateau schedule. Historical early-stop results
are contextual; the controlled contrasts are decay vs fixed and warmup vs fixed.

Calibration uses the verified strict float32 normal-score cutoff (<=10% empirical
normal alerts). No validation/test data in scaling, no test-based epoch/arm selection.
Report every arm/seed, full/matched performance, healthy score0 and severity, and
frozen DUO-GAIT alerts. DUO-GAIT has no VGA labels. Same prototype gate:full normal
FPR<=10% and impairment sensitivity>=70% for every seed. No automatic model promotion
from reused development data, even if this gate passes. Preserve all previous runs.
