# Locked nominal lower-back Y harmonic-ratio experiment

One new feature, no architecture/threshold sweep. Provider-processed LB_Acc_Y,
100 Hz, nominal ML axis (not calibrated anatomy). Use existing selected 1348 trials
and 259 participants. Provider processing preserves the event clock. Three invalid
reference-bound trials contribute missing features. No downloads.

Within each pre/post-turn segment, a stride runs between successive same-foot
heel strikes, with ordered TO/HS and exactly one opposite HS inside. No intervals
cross turns or malformed rows. Require >=50 original samples, finite signal,
and >=2 valid strides per trial. Resample each stride to 128 phase samples,
subtract mean, sum first 10 harmonic amplitudes: ML HR=odd/even. Denominator <=
1e-8 of total harmonic amplitude, or flat signal, yields missing. Average log1p(HR)
over both-side strides and then equally over trials. Overlapping side cycles are
not independent observations; model unit remains participant. This estimator is
a declared experiment, not an exact reproduction of another paper's pipeline.

Main feature includes all reference-valid trials. Sensitivity variant uses only
trials with comparable raw/processed axes and abs(initial X gravity fraction)>=.9.
This is a quality proxy, not a validated standstill test. Retain every participant
in both variants; report missingness and train-fold impute. Before fitting main,
require >=95% participant feature coverage in every pathology and healthy/stroke
group. Screened variant is descriptive even if coverage is lower.

Add feature to nuisance+cadence+phase and combined+phase. Same existing outer
participant/pathology folds and matched-device subset. Same weighted C=1 logistic
model, inner three participant-stratified folds seed 20260909, thresholds at 90%
inner OOF stroke sensitivity. Outer labels never choose thresholds. Reuse prior
baseline predictions. No diagnosis, deficit-side or quality flag as new predictors.

Primary main HR addition must have >=90% outer stroke sensitivity, no fewer stroke
detections or additional healthy FP, and >=5pp reduction in other FPR versus BOTH
nuisance+cadence and nuisance+cadence+phase, in BOTH full and matched scopes.
Combined arm and quality-screened results cannot rescue a failed main gate.
Save per-trial coverage, predictions, thresholds, inner splits, metrics and hashes.
Any success remains development evidence requiring independent measurement/cohort
validation. Frozen release unchanged.
