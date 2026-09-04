# Speed-confound audit

## Status

The planned speed-confound audit has been started against the frozen modeling manifest. A direct gait-speed variable is not currently available in the primary Voisard/Felius data release.

## Verified manifest coverage

| Dataset | Class | Participants | Trials | Trials with recorded speed |
|---|---:|---:|---:|---:|
| Voisard | Healthy | 73 | 360 | 0 |
| Voisard | Stroke | 49 | 128 | 0 |
| Felius | Healthy | 34 | 59 | 0 |
| Felius | Stroke | 132 | 318 | 0 |
| **Total** | — | **288** | **865** | **0** |

The manifest contains the planned `gait_speed_m_s` column, but all 865 values are missing. Age is available for Voisard but not Felius.

## Interpretation

The proposed age-plus-speed confound model cannot yet be fitted honestly. RMS and cadence remain speed-sensitive features, but the current public releases do not provide the distance/time or trial-level speed metadata required to measure speed directly. A speed value must not be imputed from the classifier target, cadence, or other gait features because that would circularly reproduce the signal being audited.

The baseline therefore remains suitable for a research pilot, but the claim that it is independent of gait speed is currently unresolved rather than confirmed.

## Required next action

1. Search the original dataset documentation and supplementary files for a separate walking-speed or 10-metre-walk record.
2. If no such record exists, mark speed as unavailable in the baseline limitations and use cadence/RMS sensitivity and error-by-cadence analyses as indirect stress tests only.
3. Add measured speed, walking-aid use, and clinical severity to the requirements for the independent external cohort.
4. Do not fabricate or back-calculate a speed covariate from the same accelerometer features used by the classifier.

## Consequence for model comparison

The next valid comparison is the existing gait-feature, compact-CNN, Inception-CNN, and age-only baselines, with explicit reporting that speed adjustment was not possible. A true age-plus-speed baseline must wait for a cohort with recorded speed.
