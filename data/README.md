# Dataset Layout

> **GitHub release policy:** this file documents the local data contract only.
> Raw recordings, source archives, participant metadata, intermediate arrays,
> predictions, and checkpoints are intentionally excluded from version control.
> Obtain every source from its original provider under its own licence before
> placing it in this layout.

For a collaborator-friendly list of official source links, authorised-sharing
rules, and local placement targets, see [ACCESS.md](ACCESS.md).

The project now uses one consistent storage contract for each ready dataset.

The current retention and cleanup decision is documented in
[`../reports/DATA_STORAGE_RETENTION_AUDIT_2026-09-03.md`](../reports/DATA_STORAGE_RETENTION_AUDIT_2026-09-03.md).
It distinguishes active classifier sources from reproducible processed evidence
and completed/rejected raw sources. Do not remove Felius, Voisard, extracted
Sint, RevalExo, `processed/`, or manifests as part of space recovery.

Tier A was completed on 2026-09-03: 114.753 GiB of rejected NONAN source
archives and redundant Sint/Mobilise-D ZIPs were removed. The retained data
tree is 153.928 GiB. Tier B sources remain present pending a separate decision.

```text
data/
  raw/
    <active_dataset_id>/
      data/       # usable repository data for EDA and feature work
      archives/   # original compressed downloads, when retained
      metadata/   # readmes, manifests, figures, and side files
  archive/
    raw/<dataset_id>/ # completed exploratory sources retained for provenance
  interim/
    dataset_catalog.json
    <dataset_id>/manifest.json
  processed/
    <dataset_id>/ # future ML-ready feature matrices and splits
```

Within `data/`, files stay only if they carry usable signal, subject, or label
content (e.g. `SubjectInfo.mat`, `metadata.csv`, or a dataset's own analysis
code such as Felius's `Main.py`/`Functions/`). Pure documentation (readmes,
citations, repo scaffolding like `.gitignore`/`CITATION.cff`) lives in
`metadata/` instead, so a glob over `data/` never picks up non-data files.

## Dataset data roots

Every ready dataset can be entered at the same path pattern:

```text
data/raw/<active_dataset_id>/data
data/archive/raw/<archived_dataset_id>/data
```

The active prototype sources are `felius_2024`, `voisard_2025`,
`sint_maartenskliniek`, `revalexo`, and the current public-cohort candidate
`mobilise_d_cvs`. `nonan_gaitprint` is an active **frozen healthy-specificity
evaluation** source: 29 MD5-verified participant archives have been
materialized to a three-channel `(500, 3)` magnitude contract and scored once
by the fixed canonical checkpoint (2/29 false positives at the descriptive
0.50 reference), but it is not a training, normalization, calibration, or
threshold-selection source.
Completed exploratory sources are indexed in
[`data/archive/README.md`](archive/README.md); retain them there for provenance
rather than treating them as active training material.

| Dataset ID | Main Contents Under `data/` |
| --- | --- |
| `voisard_2025` | `healthy/`, `neuro/`, `ortho/` |
| `duogait_2023` | `repository_raw/`, `repository_interim/`, `repository_processed/` |
| `camargo_2021` | `AB*` subject folders, `SubjectInfo.mat` |
| `carpinella_2026` | `Subject */Data.mat` — 60 healthy, controlled 6MWT lower-back IMU recordings; external lower-back healthy track |
| `oxwalk_2022` | `Hip_100Hz/`, `Hip_25Hz/`, `Wrist_100Hz/`, `Wrist_25Hz/`, `metadata.csv` |
| `felius_2024` | `Raw_data/`, `Functions/`, `Results/`, project files |
| `gaitmotion_2025` | `Normal/`, `Shuffle/`, `Stroke/` (simulated, healthy volunteers -- see notebook caveats) |
| `gaitex_2026` | verified GAITEX full release: normal-gait marker trajectories, Xsens orientations, and OpenSim models for virtual-IMU feasibility only; recorded pelvis is **not** lower back and no raw accelerations are released |
| `marea_2017` | `Subject Data_txt format/`, `Subject Data_mat format/`, `Activity Timings/`, `GroundTruth.mat` |
| `kiel_validation_dataset` | `preferred_walking/pp*_imu_walk_preferred.mat` — 10 healthy public full-body IMU recordings; bilateral feet plus pelvis, **not** a documented lower-back channel; audited but ineligible for direct LB/LF/RF inference or pooling |
| `soangra_john_2022` | `stroke/CK*/DATA0000.OMX`, `healthy/SUP*/DATA0000.OMX` — raw lower-back DynaPort naturalistic-activity IMU; decoder pending; not gait-labelled |

## Generated Catalogs

- Combined catalog: `data/interim/dataset_catalog.json`
- Per-dataset manifests: `data/interim/<dataset_id>/manifest.json`

## Maintenance Commands

Normalize ready dataset folders to the unified layout:

```powershell
python src\data\normalize_dataset_layout.py
```

Rebuild local manifests:

```powershell
python src\data\build_dataset_catalog.py
```

Validate all ready datasets and remaining zip archives:

```powershell
python src\data\validate_local_datasets.py
```
