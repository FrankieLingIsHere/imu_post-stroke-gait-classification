# Mobilise-D CVS compatibility audit

## Decision

Mobilise-D CVS should **not** be pooled into the current binary stroke classifier. It is a strong candidate for clinical-specificity and population-robustness evaluation, because it provides demographic and clinical metadata across large non-stroke mobility cohorts. However, the released CVS sensor material is processed digital mobility outcome data from a single back-worn device, whereas the current classifier expects bilateral LB/LF/RF wearable-IMU windows.

## Local audit performed

The small clinical-data and data-dictionary packages were downloaded and extracted into `data/raw/mobilise_d_cvs/`. The release contains participant-level clinical tables, age/gender fields, cohort/site labels, and sensor metadata. The full walking-bout archive was deliberately not downloaded yet.

The smaller `Main datasets for analysis` package has now also been downloaded and extracted. Its combined CSV contains 10,280 participant-visit rows from 2,315 unique participants: COPD 607, MS 602, PD 601, and PFF 505. Age is available for 9,823 rows and ranges from 21–96 years. Gender is available for 2,315 rows: 1,158 male, 1,156 female, and 1 prefer-not-to-say; the remaining rows are missing at visit level. Reported sensor metadata includes AX6, MM+, and one DP7 record. Walking-speed and bout-duration DMO fields are populated for roughly 7,800–7,900 rows.

## Recommended use

1. Use Mobilise-D as a non-stroke clinical specificity benchmark after selecting a compatible outcome representation.
2. Use its demographic and clinical tables to test population coverage and confounding.
3. Do not convert processed DMO values into fabricated bilateral raw IMU channels.
4. Only consider training or transfer learning after a separate representation-matching experiment demonstrates that the target signal is comparable and leakage-safe.

## Updated decision after the main-package audit

The main package is valuable enough to proceed with a **separate clinical-specificity benchmark** using participant-level DMO features. It is still not suitable for direct pooling with the current raw bilateral-IMU window model. The 955 MB walking-bout package is therefore deferred until the DMO benchmark establishes that a larger bout-level analysis is necessary.

The walking-bout package has now been downloaded and extracted. It contains five visit-level CSV files (`T1`–`T5`) with participant ID, walking-bout ID, visit/day information, duration, stride count, cadence, turning, stride speed, stride length, and stride-duration variables. This adds bout-level resolution, but remains processed back-sensor DMO rather than raw bilateral IMU.

The dataset is released for research use under CC BY-NC-ND 4.0; licensing and attribution must be preserved.
