# Locked stance-duration variability experiment

Distinct unanswered question: incremental within-side stance-duration variability,
not the already tested mean side asymmetry. Targeted scripts/src/report search found
no executed equivalent comparison. No new dataset or architecture.

One new predictor: sample SD/mean of valid stance durations separately per side
and straight bout. Minimum five valid cycles per side/bout, average eligible bouts
within each side then average the two sides. Both sides required. This avoids
mistaking different side means or pre/post-turn means for cycle variability.
Five cycles is a feasibility floor, not established measurement reliability.
Use the existing phase extractor's cycle checks, exclude invalid reference-bound
trials from features but retain all ledger rows. Average usable trial CVs per person.

Before fitting, require >=95% participant CV availability within every pathology
and healthy/stroke group. If this fails, report coverage and stop model fitting.
Retain all participants using training-only imputation if coverage passes.

Two new arms: nuisance+cadence+phase+CV and combined+phase+CV. Reuse exact prior
baselines and outer folds in full and device/protocol matched scopes. Same weighted
C=1 logistic model and three participant-stratified inner folds, seed 20260909.
Choose thresholds from inner OOF stroke scores for >=90% empirical sensitivity,
exactly as the previous nested protocol. Outer labels never select thresholds.
Fixed-0.5 results descriptive only. Save all scores, thresholds, coverage, hashes.

Primary gate in BOTH scopes: nuisance+cadence+phase+CV must attain >=90% outer
stroke sensitivity, have no fewer detected strokes or additional healthy FP than
EITHER the previous phase baseline or original nuisance+cadence baseline, and
reduce other FPR by >=5 percentage points relative to BOTH. Secondary combined
comparison cannot rescue failure. No feature/threshold search after results.

This is reused-development, annotation-assisted feasibility. It neither establishes
causality nor validates IMU-only measurement or clinical diagnosis. Prior phase
and nested-threshold experiments remain closed. A failure closes this CV addition.
