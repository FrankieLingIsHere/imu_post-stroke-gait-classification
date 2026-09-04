# Public dataset role matrix

The project should use public datasets by **role**, not by forcing every source into the supervised stroke classifier.

| Dataset | Labels / coverage | Sensor compatibility | Recommended role | Immediate action |
|---|---|---|---|---|
| Felius + Voisard | Healthy + stroke; current pooled development set | Established `LB/LF/RF` contract | Primary supervised development | Keep as baseline |
| RevalExo | Healthy + stroke; 17-person frozen cohort | Adapter completed | Primary external stress test | Keep untouched |
| Sint Maartenskliniek | 10 stroke + 20 healthy; raw Xsens | Promising, pending channel audit | External test first, then sensitivity training | Acquire and audit |
| Zhou rehabilitation | Stroke only; repeated visits | Raw IMUs, different protocol | Severity, progression, longitudinal robustness | Do not use for binary labels |
| Mobilise-D | Healthy and non-stroke clinical groups | Lower-back IMU, different task | Non-stroke specificity / OOD false-positive test | Use after schema audit |
| DUO-GAIT | Healthy only; exact ages | Does not match primary sensor contract | Healthy age/speed domain analysis or SSL pretraining | Do not supervised-pool |
| OxWalk | Healthy only; coarse age bands | Hip/wrist, not `LB/LF/RF` | Healthy OOD and age/sensor-shift analysis | Do not supervised-pool |
| MAREA, Camargo, GaitMotion | Healthy reference data | Heterogeneous placements/protocols | Feature-level replication and SSL pretraining | Keep separate |
| Triaxial accelerometer dataset | Healthy only | Foot + lower-back; different rate/task | Healthy sensor/domain robustness | Optional secondary test |
| PiG | Healthy + stroke, but motion capture/force/EMG | Not wearable IMU-compatible | Literature/biomechanical reference, not classifier input | Do not merge |

## Training rule

Only a dataset with compatible raw channels and trustworthy participant-level healthy/stroke labels can enter a supervised sensitivity-training experiment. Healthy-only data may be used for unlabeled representation pretraining, but must not be assigned synthetic stroke labels.

## Examination rule

Every independent healthy/stroke public dataset must be frozen before model tuning. If a dataset is used to choose preprocessing, architecture, calibration, threshold, or augmentation, it is no longer a clean external test and must be reported as development or sensitivity evidence.

## Recommended sequence

1. Sint Maartenskliniek: audit and freeze an external examination subset.
2. Run the locked Inception and MiniROCKET candidates on it.
3. Freeze the result, then test a source-balanced Felius + Voisard + Sint sensitivity model.
4. Use RevalExo as the final untouched stress test for that sensitivity experiment.
5. Add Zhou and Mobilise-D only as specialist robustness analyses.
6. Keep healthy-only datasets separate, with optional self-supervised pretraining experiments.
