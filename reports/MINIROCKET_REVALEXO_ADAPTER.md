# MiniROCKET RevalExo adapter status

## Channel mapping verified

The existing RevalExo window array has shape `(2228, 500, 18)`. Its documented construction order is:

1. lower-back acceleration XYZ;
2. lower-back gyroscope XYZ;
3. right-foot acceleration XYZ;
4. right-foot gyroscope XYZ;
5. left-foot acceleration XYZ;
6. left-foot gyroscope XYZ.

The defensible MiniROCKET input mapping is therefore acceleration magnitude in the order `LB`, `LF`, `RF`, producing `(2228, 500, 3)` and matching the primary model contract.

## Execution status

The first adapter attempt failed because the external array was sliced along the time axis instead of the channel axis, producing `(2228, 3, 3)` rather than `(2228, 500, 3)`. The slicing was corrected to `E[:, :, channels]`. A WSL refit using the same internal folds, normalization, 2,000 kernels, 16 dilations and Ridge configuration then completed successfully, with calibration fitted only on inner training participants.

RevalExo remained frozen and no external data was used for fitting or tuning.

## Frozen external result

| Model | External participants | Mean AUROC across five fold models | Mean Brier |
|---|---:|---:|---:|
| MiniROCKET + calibrated Ridge | 17 | 0.874 | 0.215 |
| Inception CNN | 17 | 0.871 | 0.170 |

MiniROCKET has similar external discrimination to Inception, but worse probability calibration. The small 17-participant cohort makes this comparison uncertain; it is a stress test, not clinical validation.

## Required next action

Pin the WSL adapter environment and hash the resulting prediction file before reuse. Do not tune either model on the RevalExo outcomes.
