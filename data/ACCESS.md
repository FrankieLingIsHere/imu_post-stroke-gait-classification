# Collaborator data access

This repository deliberately does **not** distribute sensor recordings or derived participant-level data. The preferred workflow is for each collaborator to obtain public sources from their original record, under the source provider's own terms, then place them in the documented local `data/` layout.

## Recommended route: obtain from the original source

| Dataset | Role in this project | Official access route | Local target |
| --- | --- | --- | --- |
| Felius et al. (2024) | Primary stroke/healthy development source | [Zenodo record](https://doi.org/10.5281/zenodo.11045239) | `data/raw/felius_2024/` |
| Voisard et al. (2025) | Primary stroke/healthy development source | [Figshare record](https://doi.org/10.6084/m9.figshare.28806086) | `data/raw/voisard_2025/` |
| RevalExo | Frozen paired external evaluation | [KU Leuven record](https://rdr.kuleuven.be/dataset.xhtml?persistentId=doi:10.48804/OWJOID) | `data/raw/revalexo/` |
| NONAN GaitPrint | Healthy-domain audit / predeclared partitions | [Figshare collection](https://doi.org/10.6084/m9.figshare.c.6415061.v1) | `data/raw/nonan_gaitprint/` |
| Carpinella et al. (2026) | Healthy lower-back external check | [Figshare record](https://doi.org/10.6084/m9.figshare.29665850.v1) | `data/archive/raw/carpinella_2026/` |
| DUO-GAIT (2023) | Healthy reference / separate analysis stream | [Zenodo record](https://doi.org/10.5281/zenodo.7415758) | `data/archive/raw/duogait_2023/` |

The project includes download helpers for Felius, Voisard, and DUO-GAIT in `src/data/`. Always inspect the provider's current licence, attribution, and any click-through conditions before downloading or using a dataset.

## Sources that must not be casually copied

Some locally held sources—including Sint Maartenskliniek and Mobilise-D CVS material—are not listed above as independently reproducible public downloads in this project. Treat them as **authorised-access only** unless the project owner confirms their redistribution terms in writing. Do not email archives, upload them to public cloud folders, include them in GitHub releases, or mirror them in a personal repository.

## If a shared copy is permitted

Use an institution-approved, access-controlled service (for example a university SharePoint/OneDrive team site, approved research drive, or secure object storage), with access granted only to named authorised collaborators.

1. Confirm that each source licence permits this form of team sharing.
2. Store untouched source archives in a read-only `source_packages/` area and retain provider citations/checksums.
3. Give each collaborator their own local clone and working `data/` directory; do not share derived folds, predictions, or checkpoints unless their participant-data terms allow it.
4. Preserve the project’s split roles: RevalExo and frozen healthy cohorts remain evaluation-only regardless of who has storage access.
5. Record the source version and checksum in the local acquisition manifest.

## Never use GitHub for data delivery

Do not use GitHub commits, Git LFS, Releases, Issues, pull-request attachments, or a public GitHub Pages site to distribute datasets or checkpoints. GitHub hosts the code, documentation, rendered notebooks, and report artefacts only.

## First-time collaborator checklist

1. Clone the repository and create the Python environment described in the root `README.md`.
2. Read the relevant source's wiki note and this guide before downloading.
3. Obtain the source from its official link or receive authorised institutional access.
4. Place it under the target shown above, then run the documented local validation/normalisation step.
5. Start with the rendered reports or executed notebooks; only run an analysis after the required sources are available locally.

