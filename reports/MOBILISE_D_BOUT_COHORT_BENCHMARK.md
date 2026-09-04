# Mobilise-D walking-bout cohort benchmark

## Protocol

- Five visit-level bout files were combined.
- Bouts were aggregated to one participant vector using median and mean statistics; bout count was retained as a feature.
- Repeated visits and bouts were therefore not treated as independent subjects.
- Five-fold participant-level stratified validation used imputation, standardisation, and class-balanced logistic regression.

## Result

- Walking bouts processed: 16055401
- Participants: 2281
- Features used: 17
- Mean missingness before imputation: 0.0%
- Balanced accuracy: 0.717
- Macro-F1: 0.715
- Cohorts: COPD, MS, PD, PFF

This remains a clinical-cohort separability experiment, not stroke detection. The representation is processed single-back DMO and must not be pooled into the bilateral raw-IMU classifier.

Compared with the visit-level DMO benchmark (balanced accuracy 0.713, macro-F1 0.710), bout-level aggregation reached balanced accuracy 0.717 and macro-F1 0.715. The improvement is small, so the walking-bout package does not currently justify a new training pathway; its value is mainly finer-grained clinical-population analysis.
