# Pathology-balanced negative weighting

Protocol locked before fitting on 2026-09-09. The unanswered question is whether
unequal pathology contributions within the current phase+HR logistic model's
negative training class contribute to neurological false positives. Historical
raw-signal hard-negative exposure experiments do not answer this representation-
specific weighting comparison. This is a development experiment, not independent
validation or proof of the underlying disease mechanism.

Keep all ten packaged features, preprocessing, logistic C=1, participant folds,
outer pathology holdouts and training-only 90% sensitivity threshold selection.
Keep total training masses healthy 0.25, stroke 0.50, other 0.25. Only divide the
other mass equally among pathology groups present in each training subset,
then equally among their participants. Diagnosis is used for training weights
and evaluation only, never as an inference feature or routing rule.

One candidate, no weight/threshold sweep. Evaluate all 259 participants and the
existing 144-person device/protocol-matched subset. Reuse verified baseline OOF
predictions. Save inner predictions, thresholds, outer predictions and training
weight totals. No participant exclusion or new feature extraction.

Replacement rule, fixed before fitting: in BOTH scopes, at least a five percentage
point reduction in neurological (CIPN/PD/RIL) FPR, no additional missed strokes,
no increase in healthy false positives, and no increase in total other false
positives. This tests improvement relative to the accepted prototype, not clinical
admission. Keep the existing prototype if the rule fails. Do not retune after
seeing results. The same reused development cohorts limit generalization claims.
