# Baseline requirements audit

Updated: 2026-08-24

| Requirement | Status | Evidence / limitation |
|---|---|---|
| Participant-level healthy/stroke labels | Fulfilled | Felius + Voisard pooled development data |
| Common 5-second, 3-sensor input | Fulfilled | LB/LF/RF acceleration-magnitude contract |
| Participant-disjoint validation | Fulfilled | Fixed folds and participant-level aggregation |
| Source-balanced pooled training | Fulfilled | Established source-balanced-global benchmark |
| Internal discrimination | Fulfilled | Pooled AUROC approximately 0.957 |
| Untouched external cohort | Fulfilled | RevalExo held out; participant AUROC 0.871 |
| External calibration | Partial | External Brier 0.170, but no validated clinical calibration/threshold |
| Age-specific stroke validation | Not fulfilled | Linked age audit has healthy ages only; no age-labelled stroke bands |
| Broad age coverage | Partial | Healthy coverage is wider; stroke ages do not overlap sufficiently |
| Clinical-severity generalization | Not fulfilled | Severity/chronicity/walking-aid metadata are incomplete across sources |
| Healthy older-adult specificity | Partial | RevalExo has older healthy participants but no individual ages; 5/7 descriptive false positives |
| Explainability | Partial | Diagnostic work exists; formal final-model attribution remains required |
| Simpler-model comparison | Fulfilled | Engineered/MiniROCKET baselines already compared |
| Leakage controls | Fulfilled | Participant split, fold normalization, RevalExo exclusion audits passed |

## Decision

The baseline is suitable as the current research prototype and frozen reference model. It is not yet sufficient for claims of age-general or clinically broad deployment. The next work should focus on healthy age-domain specificity using DUO-Gait/OxWalk where metadata permits, plus an age-complete stroke comparison from an online source or future cohort. Do not add age to the primary model or use Zenodo in the primary probability at this stage.
