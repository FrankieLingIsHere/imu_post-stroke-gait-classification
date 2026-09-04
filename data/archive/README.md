# Archived raw datasets

> **GitHub release policy:** this index is public, but the archived recordings,
> source files, provenance packages, and audit outputs it describes remain
> local and are not included in a repository clone.

This directory contains reversible, completed exploratory sources. They are
not deleted: their original files, provenance, and related audit outputs remain
available for report reproduction or future work. The active prototype sources
remain under `data/raw/`.

| Dataset | Why archived | Current role |
|---|---|---|
| `gaitex_2026` | Physics-derived virtual healthy signals did not improve the matched SSL baseline | Reproducible negative synthesis evidence |
| `camargo_2021`, `duogait_2023`, `marea_2017`, `oxwalk_2022`, `gaitmotion_2025` | Noncanonical healthy/reference sources | Context, separate audits, future pretraining only |
| `soangra_john_2022` | Paired lower-back ADL, not gait-labelled | Activity-domain context only |
| `zenodo_stroke_rehab` | Stroke-only source | Severity/pretraining research only |
| `triaxial_accelerometer`, `carpinella_2026`, `kiel_validation_dataset` | Component/reference cohorts without the final LB/LF/RF binary contract | Frozen component or placement audits |

To reactivate a source, move its folder back to `data/raw/`, update its catalog
storage state if necessary, and rerun `python src/data/build_dataset_catalog.py`.
