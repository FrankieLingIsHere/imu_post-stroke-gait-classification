# Triaxial older-healthy gait cohort

## Role

Public older-healthy IMU cohort for data-contract and lower-back
healthy-specificity investigation. It is **not** a direct addition to the
three-channel binary pool: it records lower back plus only one foot, so an
LB/LF/RF input would require an invented channel.

## Source contract

The [Zenodo release](https://doi.org/10.5281/zenodo.10148824) documents 60
older adults (65–88 years), 256-Hz triaxial acceleration in g, normal and
metronome corridor walking, and a lower-back (L4–L5) plus one foot sensor.
Locally, 59 participants provide normal lower-back corridor recordings under
`data/raw/triaxial_accelerometer/extracted/`.

## Frozen audit (2026-09-02)

The secondary frozen lower-back checkpoint was run on author-segmented normal
corridor walking only, after transparent 256-to-100-Hz polyphase resampling.
At the unchanged 0.50 reference, 53/59 healthy people were false positive
(89.8%; Wilson 95% interval 79.5%–95.3%). This does **not** establish an
age-related model failure: the input distribution is strongly shifted from the
gravity-inclusive training contract (median magnitude 0.578 g, compared with
the checkpoint mean 1.016 g and Carpinella median 1.021 g). No guessed unit
or gravity correction is allowed.

Decision: keep the release out of training, threshold choice, and the
three-channel external score. It is evidence that the lower-back secondary
track still needs verified cross-device representation compatibility.

See [[../reports/TRIAXIAL_OLDER_HEALTHY_LOWER_BACK_FROZEN_AUDIT_2026-09-02]].

