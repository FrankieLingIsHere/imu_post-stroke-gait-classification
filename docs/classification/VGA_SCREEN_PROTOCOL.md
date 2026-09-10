# Clinician-observed gait deterioration screening protocol

2026-09-09, locked before fitting. New target, separate from stroke classification.
Provider Table1 defines visual gait assessment0 none,1 mild,2 moderate,3 severe,
4 very severe. Primary source: https://www.nature.com/articles/s41597-025-05959-w
Table5 calls the key visualGaitEvaluation; actual local JSON uses
visualGaitAssessment. Use actual score values, not diagnosis as a proxy.

Choose each existing participant's earliest session with cached usable cycles
without inspecting its score; no fallback to later sessions for missing labels.
Require complete consistent binary scores in that session. Missing/ambiguous
sessions remain unknown and appear in the ledger. No imputation from diagnosis.
Target0=VGA0, target1=VGA1-4. First-session inventory:84 score0,164 score1-4,
11 unknown among259 participants. Rater scores are subjective observations,
not an independent diagnostic gold standard or proof of etiology.

Use only the already tested six-channel waveform frame, actual upstream CNN,
and original participant-disjoint fitting/validation/calibration/test roles,
intersected with eligible first-session participants. No clinical score/diagnosis
as input. Equal target mass.5/.5, equal people/trials/cycles. Two existing recipes
and seeds42,137,202, three outer folds:18 fits. Select minimum weighted validation
loss. No refit or post-result sweep.

Calibrate for <=10% empirical alert rate among calibration VGA0 participants:
sort their scores ascending, choose ceil(.9*n)-th score, and classify only scores
strictly above that value as positive. Store a nextafter threshold for >= use.
This is a prototype policy, not a clinical requirement or population guarantee.
Small calibration counts and achievable discrete rates must be reported. Unlike
the prior stroke sensitivity rule, this prioritizes normal-score specificity.

Report held-out VGA0 false alerts, VGA1-4 detection and severity breakdown,
AUROC, healthy-group alerts, disease-with-VGA0 alerts, matched subset, all seeds.
Prototype gate: full held-out VGA0 false-alert rate<=10% and VGA1-4 sensitivity
>=70% in every seed. No claim of clinical validation if this development gate passes.
DUO-GAIT remains frozen reused healthy-condition stress testing with no VGA labels:
report alerts by condition, not validated VGA errors or stroke sensitivity.
No checkpoint replaces the stroke prototype. Save source/label/split/checkpoint
provenance and clearly distinguish acquisition, preprocessing and evaluation.
