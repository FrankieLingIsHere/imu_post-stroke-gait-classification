# Test-set credibility audit

Date: 2026-09-03

## Verdict

The current three-source leave-one-source-out design is credible for
**development model selection**, but the repository does not yet contain a
credible final clinical test set for the newly selected model.

Development credibility comes from complete-source holdout, participant-level
separation and aggregation, training-only normalization, five repeated seeds,
source-specific FP/FN reporting, and untouched frozen signals during model
selection. It is not final validation because Felius, Voisard, and Sint all
influenced the model-selection decision.

The 17-person paired RevalExo cohort is independent but contains only seven
healthy and ten stroke participants. It has also been examined repeatedly in
historical experiments. It can provide a small locked external check, but not
a precise or pristine pivotal test. Healthy-only and stroke-only component
cohorts cannot be combined into one binary accuracy estimate because their
devices and protocols differ.

## Comparison with published practice

- Felius et al. (2024) used participant-level 70/20/10 splits repeated ten
  times. This is appropriate internal split discipline, but not a separate-site
  final test.
- A 2025 Frontiers study trained on 129 healthy and 27 stroke participants and
  held out 58 healthy and 12 stroke participants. Its KNN/SVM result was TN=57,
  FP=1, TP=8, FN=4. Overall accuracy was 92.9%, while stroke sensitivity was
  only 66.7%, demonstrating why FP/FN and class-specific metrics are required.
- A 2026 STAT-GCN study kept every participant's gait cycles within one of five
  stratified folds and applied augmentation only to training folds. This is a
  sound internal-validation pattern, but remains single-cohort evidence.
- BMJ external-validation guidance warns that many studies are too small. One
  hundred events and one hundred non-events is a starting rule rather than a
  universal solution; sample size should target precision for discrimination,
  calibration, and clinical utility.
- FDA diagnostic-test guidance asks for 2x2 counts and two-sided 95% intervals,
  complete participant accounting, site and demographic subgroup results, and
  representation of disease severity and clinically relevant confounders.

Sources and exact links are embedded in executed notebook 30.

## Quantitative planning target

Using the current development-consensus rates only as planning assumptions,
approximately 257 independent healthy/non-stroke participants and 222
independent stroke participants are needed for a two-sided 95% Wilson interval
with total width at most 0.10 for specificity and sensitivity respectively.
This is not a universal regulatory requirement. It illustrates why 7 healthy
and 10 stroke participants are inadequate for a reliability claim.

## Required final-test contract

1. Freeze architecture, preprocessing, ensemble members, equal averaging,
   threshold, exclusions, and handling of indeterminate signals before access.
2. Use participants absent from all training, tuning, representation choice,
   and threshold selection, preferably from multiple independent sites and
   devices.
3. Treat one participant as the statistical unit. Never count windows or gait
   cycles as independent test subjects.
4. Represent age, sex, stroke severity/chronicity, walking speed, walking aids,
   and clinically relevant non-stroke gait disorders.
5. Use an independent clinical reference diagnosis and account for every
   included, excluded, failed, and indeterminate participant.
6. Report TN/FP/FN/TP as counts and fractions, sensitivity, specificity, AUROC,
   calibration/Brier, and two-sided 95% intervals overall, by site, and by
   predefined subgroup.
7. Perform no model or threshold update after opening the final test. Any later
   update requires a new untouched evaluation cohort.

