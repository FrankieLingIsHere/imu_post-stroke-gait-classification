# Locked TVS optical-reference laterality development test

Use existing local cohort_hallway_v1/raw MAT files plus two original HA/PD schema
samples, deduplicated by participant. No downloads. Explicitly a new laterality
classifier, not a stroke classifier: no local TVS stroke group exists. These
participants have been used in earlier research and are not untouched final tests.

Use laboratory Test5/6/7/10 recordings, all recorded trials, optical Stereophoto
ContinuousWalkingPeriod initial-contact times and explicit Left/Right labels.
Deduplicate repeated contacts within a trial; conflicting side labels reject that
trial. Require optical raw marker fields and finite lower-back gyro, declared 100Hz.
Convert reference seconds to samples round(t*100)-1, the project's established
MATLAB indexing convention. Reject out-of-bounds/duplicate sample contacts.

Reference audit: ordered one-to-one optical/INDIP contact matching within 150ms,
report coverage, side agreement and timing. This is cross-reference agreement,
not proof that either reference is error-free. Shared processing can induce
correlated reference errors. INDIP labels never select or change optical labels.

New model uses all three native gyro axes: fourth-order 0.5-2Hz bandpass filtered
signal and first/second sample gradients at supplied optical contact times (nine
features). No anatomical-axis assumption, feature sweep or label inversion.
MinMaxScaler + linear SVC C=1. Three participant-stratified folds by HA/PD, shuffled
seed 20260909. Equal participant mass, half to each side in training. Imputation
not used for malformed signals. Report every source trial and participant.

Proceed to fitting only if >=95% expected optical contacts have valid gyro features
in each cohort and >=3 participants per cohort have both sides. Missing participant
accuracy counts zero. Feasibility gate >=90% participant-macro accuracy in each
cohort, and no participant dropped. No thresholds tuned after seeing results.
Passing would justify predicted-contact measurement evaluation, never clinical
stroke diagnosis or proof of Voisard's frame convention. Save artifacts and folds.
