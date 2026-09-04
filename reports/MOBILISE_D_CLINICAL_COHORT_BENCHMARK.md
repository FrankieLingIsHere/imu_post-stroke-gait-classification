# Mobilise-D clinical-cohort benchmark

This is a separate validity experiment. Mobilise-D CVS contains no stroke and no healthy-control cohort, so it cannot directly evaluate the current stroke-versus-healthy classifier. It tests whether participant-level digital mobility outcomes distinguish the four clinical cohorts.

## Protocol

- One median feature vector per participant; repeated visits are not independent samples.
- Five-fold participant-level stratified cross-validation.
- Median imputation, standardisation, and class-balanced multinomial logistic regression.
- No Mobilise-D data is added to the raw bilateral-IMU training set.

## Result

- Participants: 2315
- Features used: 22
- Mean feature missingness before imputation: 6.8%
- Balanced accuracy: 0.713
- Macro-F1: 0.710
- Cohorts: COPD, MS, PD, PFF

This result measures cohort separability, not stroke detection. A strong result supports Mobilise-D as a clinical-population stress-test resource, but a separate stroke-versus-healthy evaluation dataset remains necessary.
