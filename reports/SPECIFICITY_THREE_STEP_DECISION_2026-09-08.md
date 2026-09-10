# Three-step specificity decision

Executed from saved predictions on 2026-09-08; no inference, training or threshold
search. This is paired error attribution, not a repeat of the stress test.

1. **Matched errors:** 138 participants, 65 positive in both models, 42 negative
   in both, 24 new false positives and seven corrected false positives with
   v0.2.0. New/corrected errors: ACL 3/1, CIPN 2/1, HOA 5/0, KOA 5/0, PD 2/2,
   RIL 7/3. Regression is not confined to one pathology. The exploratory exact
   two-sided paired binomial p-value is 0.00333; this does not make inspected
   data independent or isolate sensor count as the cause.
2. **Nuisance checks:** score has Spearman correlation 0.321 with age (137
   participants) and 0.541 with window count (138). Pathology, age, impairment
   and duration can covary, so these are not causal findings. Window count is
   not measured walking speed. Equal trial weighting changes only two decisions,
   leaving 87/138 positive calls instead of 89/138. That pooling change is not
   an adequate explanation or remedy and is not adopted.
3. **Decision:** retain v0.2.0 as the development-selected research artifact,
   but do not promote it as a stroke-specific classifier. No threshold/pooling
   change is admitted because this cohort cannot measure stroke sensitivity.
   A future intervention needs a defined stroke-versus-non-stroke task with
   clinically identified comparisons and independent paired validation.
   Historical negative-exposure experiments already failed their gates; do
   not repeat them under another name. Any proposal must state what differs
   and how independent evidence will test that difference.

The practical next route is provider evidence through the implemented intake
gate and prepared requests. No accuracy improvement is claimed. The concrete
outcome is identification of 24 new errors and rejection of a pooling-only fix.

Implementation: `scripts/explain_lower_back_specificity_regression.py`.
Local results: `data/processed/lower_back_specificity_regression_*`, including
matched participant records, pathology/age tables and hashed input provenance.
