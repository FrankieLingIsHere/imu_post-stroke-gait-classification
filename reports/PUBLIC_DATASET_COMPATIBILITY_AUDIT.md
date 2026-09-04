# Public dataset compatibility audit

Audit date: 2026-08-25. This is a role audit, not permission to merge all sources into supervised training.

| Source | Verified local evidence | Compatibility finding | Current role |
|---|---|---|---|
| Felius | Existing validated windows and participant metadata | Compatible primary contract | Supervised development |
| Voisard | Existing validated windows and participant metadata | Compatible primary contract | Supervised development |
| RevalExo | Existing adapted `(2228,500,18)` windows and corrected LB/LF/RF mapping | Compatible through documented adapter; independent cohort | Frozen external test |
| Sint Maartenskliniek | 10 CVA + 20 HC folders; raw Xsens exports; sensor spec names lumbar, leftfoot, rightfoot; published mapping gives 76 mapped trials, 75 locally available | Strong candidate; all 30 participants have complete selected sensors. One mapped healthy trial is absent from the public archive and is excluded, not guessed | External first; later sensitivity training |
| Zhou rehabilitation | Existing extracted raw/interim/processed data; stroke-only participants | No healthy controls | Stroke-only longitudinal/severity/OOD analysis |
| Triaxial healthy reference | 60 age rows (65–88 years), 527 CSV files, one foot (`FO`) plus lower back (`LB`) and walking-speed metadata | Healthy-only and lacks bilateral-foot channels; not directly compatible with the 3-channel classifier | Healthy age/speed/domain audit; optional SSL |
| DUO-GAIT | Existing 16 healthy participants with exact age | Healthy-only and non-equivalent input contract | Healthy age/domain analysis; optional SSL |
| OxWalk | Existing 39 healthy participants with coarse age bands | Healthy-only; hip/wrist rather than LB/LF/RF | Healthy OOD and age/domain analysis |
| MAREA | Existing healthy placement reference | Healthy-only, heterogeneous placement/protocol | Feature-level replication and SSL |
| Camargo | Existing healthy placement reference | Healthy-only, heterogeneous placement/protocol | Feature-level replication and SSL |
| GaitMotion | Existing healthy placement reference | Healthy-only and foot-substitute limitations | Feature-level replication and SSL |
| Mobilise-D | Not downloaded; multi-archive, >60 GB full release | Must select a relevant subgroup and audit schema before transfer | Deferred non-stroke specificity test |
| PiG | Public motion-capture/force/EMG dataset | Not wearable-IMU compatible | Biomechanical reference only |

## Findings that change the plan

1. Sint Maartenskliniek is the only newly acquired source currently suitable for a possible new supervised binary cohort, because it contains both stroke and healthy participants and names the required sensor locations.
2. The triaxial dataset materially improves older healthy coverage: its local metadata spans ages 65–88, but it cannot increase stroke representation. It should be used to test whether the current classifier produces age/domain false positives, not to manufacture labels.
3. Zhou is valuable despite not entering binary training: repeated stroke visits permit progression and representation-stability analysis.
4. The existing five healthy datasets remain useful. Their limitations are exactly why they should be kept as independent healthy stress tests rather than silently pooled into the stroke classifier.
5. Mobilise-D should not be downloaded in full until the project selects the smallest relevant non-stroke subgroup and confirms the license, schema, and available labels.

## Next execution order

1. Complete a formal Sint Maartenskliniek adapter audit and create model-ready windows without fitting any model.
2. Run the locked Inception and MiniROCKET candidates on the Sint external subset.
3. Run an older-healthy specificity audit using the triaxial dataset after its channel/unit audit.
4. Freeze both results.
5. Run the Sint sensitivity-training comparison against the original baseline and untouched RevalExo.
6. Use Zhou for longitudinal/severity analysis and Mobilise-D for non-stroke specificity once a targeted subgroup is selected.

## First frozen examination

The locked five-fold evaluation on the mapped Sint candidate produced AUROC 0.915 for Inception and 0.920 for MiniROCKET at participant level. Brier scores were 0.097 and 0.134 respectively. The result is encouraging but does not establish superiority; the cohort has 10 stroke participants and 20 controls.

The subsequent expanded Inception sensitivity model was evaluated once on untouched RevalExo: AUROC 0.914, Brier 0.162, balanced accuracy 0.714 across 17 participants. Relative to the original two-source Inception result (AUROC 0.871, Brier 0.170), discrimination and Brier score improved descriptively, but the small cohort and threshold-dependent balanced-accuracy result require paired participant-level error analysis before a final inclusion decision.

The triaxial healthy audit found 60 participant metadata rows aged 65–88. The raw files provide 290 lower-back recordings and 236 foot recordings across 59 participants, but no bilateral-foot pair. Therefore this dataset cannot receive a defensible direct stroke-classifier score under the established `LB/LF/RF` contract; it is retained for older-healthy signal/domain analysis and optional self-supervised pretraining.
