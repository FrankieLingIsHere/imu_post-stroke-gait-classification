# Kiel Validation Dataset public subset

## What was acquired

The public repository releases 10 healthy participants: five younger and five
older adults. To avoid downloading unrelated optical, home, and split-belt
files, the local acquisition contains only the ten preferred-walking raw IMU
MATLAB files (7.7 MB) in `data/raw/kiel_validation_dataset/preferred_walking/`.

The source files hold acceleration in g, bilateral foot sensors, and a pelvis
sensor. Eight files are 200 Hz; two are 100 Hz. The parent protocol describes
a full-body system with pelvis, feet, and other segment sensors, but does not
document the pelvis sensor as the L4/L5 lower-back location required by this
project's LB/LF/RF classifier.

## Decision (2026-09-02)

Do **not** resample, score, pool, or synthesize from this source for the
three-channel classifier. Treating `pelvis` as `lower back` would silently
change the sensor-placement semantics. The data remain a documented public
healthy multi-sensor reference only; they are not an external specificity
result.

The repository's public release contains no stroke participants; additional
data are available only by request, which is outside this online-only project.
See `data/interim/kiel_validation_dataset/audit.csv` and
`scripts/audit_kiel_validation_dataset.py`.

Sources: [public repository](https://github.com/neurogeriatricskiel/Validation-dataset)
and [study protocol](https://doi.org/10.3390/s21175833).

