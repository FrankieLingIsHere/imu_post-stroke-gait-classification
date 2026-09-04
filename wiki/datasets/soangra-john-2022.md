---
type: dataset
population: "Public release observed locally: 13 stroke (CK) and 19 healthy (SUP) lower-back recordings; verify against the study's reported cohort before analysis"
sensors: "DynaPort lower-back IMU: 3-axis accelerometer and 3-axis gyroscope at 100 Hz; magnetometer 10 Hz, pressure and temperature 1 Hz"
role: activity_domain_context_only
---

Soangra & John (2022) is the project's first downloaded independent paired
stroke/healthy **lower-back IMU** cohort beyond the primary Voisard/Felius
development sources. It does **not** supply a gait-labelled protocol: the
release records three days of naturalistic activities of daily living and the
author code constructs group-labelled three-second movement segments. It
therefore cannot directly enlarge or externally validate the gait classifier,
in addition to lacking left/right foot channels.

## Local acquisition audit — 2026-09-01

- The raw release is organised at
  `data/raw/soangra_john_2022/data/{stroke,healthy}/<participant>/DATA0000.OMX`.
- There are 32 observed files: 13 CK stroke and 19 SUP healthy. This differs
  from counts reported in the associated paper, so all evaluation must record
  the exact analysed-file count rather than assume publication-level numbers.
- Every raw header specifies a 100 Hz ±8 g accelerometer and a 100 Hz ±2000
  deg/s gyroscope. It is therefore a real six-axis lower-back IMU source,
  its setting is naturalistic ADL rather than a verified gait protocol.
- The files are DynaPort-specific binary `.OMX`, not HDF5/OpenMatrix. The
  supplied Python code uses optional HDF5 derivatives; no conversion has been
  claimed. A validated `OMX_readFile`-compatible decoder (or the official HDF5
  derivative release) is required before any signal analysis, preprocessing,
  or model score.

## Role decision

Do not use this cohort in supervised gait training, gait threshold tuning, or
gait external validation. After validated decoding, it may support a separately
reported lower-back activity-domain analysis or self-supervised pretraining
only if a leakage-safe transfer experiment is predeclared. It does not provide
bilateral-foot coverage or an immediate cure for the main model's healthy false
positives.

Source: [Chapman University dataset record](https://digitalcommons.chapman.edu/pt_data/3/);
study: Soangra & John, 2022, PMCID: PMC8780832.
