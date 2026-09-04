# Post-Stroke Gait Classification from Wearable IMUs

[![Research status](https://img.shields.io/badge/status-active%20research-blue)](#project-status)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](#environment)

An evidence-led research prototype for distinguishing post-stroke and healthy gait from wearable inertial measurement unit (IMU) signals. The primary modelling contract uses one lower-back acceleration-magnitude channel. Synchronized lower-back, left-foot, and right-foot magnitudes remain a secondary performance and specificity comparator.

> **Research use only.** This repository is not a medical device, is not clinically validated, and must not be used to diagnose, treat, or make decisions about an individual.

## Project status

The project has established a participant-grouped, source-aware baseline and a locked external-evaluation workflow. The current development-selected lower-back candidate is a fixed equal-probability ensemble of compact Inception-style ERM, HAROOD-style CORAL, and an ERM++-style optimization variant. It passed a five-seed leave-one-source-out development gate. Subsequent threshold, participant-level MIL, canonical-mechanics InceptionTime, canonical 10,000-feature MiniROCKET, and fixed-fusion audits did not safely reduce both false-positive and false-negative errors across every source. Architecture rotation on the existing 314 development participants is therefore closed; the next requirement is a new untouched paired cohort and frozen-model evaluation. The model has not earned a new external-validation claim. Every result should be interpreted as research evidence with documented dataset, population, and validation limitations—not as a claim of clinical readiness.

The current external reference evaluation is a fixed RevalExo cohort. It is never used for threshold selection, calibration, or model selection. The current healthy-only NONAN GaitPrint set is similarly frozen for specificity checks. See the [data documentation](data/README.md), [notebook sequence](notebooks/README.md), and [research wiki](wiki/README.md) for exact roles and safeguards.

## Repository layout

```text
.
├── data/        # local data contract and acquisition guidance (raw data is excluded)
├── docs/        # public project plans and technical requirements
├── models/      # release-ready inference code and model documentation (weights external)
├── notebooks/   # numbered, executed research evidence workflow
├── reports/     # curated, human-readable findings and presentation assets
├── scripts/     # reusable acquisition, audit, training, evaluation, and rendering tools
├── slides/      # Slidev presentation source
├── src/         # reusable dataset and signal-processing modules
└── wiki/        # Obsidian-compatible research decisions and dataset notes
```

## Data access and governance

No participant-level recordings, source archives, intermediate arrays, predictions, or model checkpoints are stored in Git. They are large, may be license-restricted, and can contain sensitive metadata.

To reproduce an analysis:

1. Read [data/ACCESS.md](data/ACCESS.md) and [data/README.md](data/README.md) to identify the required dataset, its role, licence/access route, and local target.
2. Obtain each dataset from its original provider and comply with its terms.
3. Place it only under the documented local `data/` contract.
4. Run the relevant numbered notebook or reusable script.

Do not commit raw, interim, processed, or archive data to a fork or derivative repository.

## Environment

Use Python 3.10 or newer. GPU-backed PyTorch is recommended for deep-learning experiments. After installing the base environment, use the official PyTorch installer to select the wheel compatible with the local CUDA driver when GPU execution is required.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

The requirements file intentionally lists project-level Python dependencies. Hardware-specific PyTorch installation is left explicit so contributors do not accidentally install an incompatible CUDA build.

## Reproducible research path

First-time readers should open [Notebook entry point](notebooks/00_READ_THIS_FIRST.md).
It gives a five-notebook route through the data, selected model, error profile,
and next decision. The full set of 34 numbered notebooks is the authoritative
audit trail; it is **not** necessary to read or run all 34 in order. The
phase-by-phase catalog and execution status are maintained in
[notebooks/README.md](notebooks/README.md).

Reusable operations live in [scripts/README.md](scripts/README.md). Scripts support notebook work; they do not replace the notebook evidence record for material findings.

## Testing the research checkpoint

The reproducible inference code and model card are in [models/README.md](models/README.md). The checkpoint itself is deliberately distributed as a versioned external research artefact rather than stored in Git. This preserves the data/code boundary and allows checksum-verified testing without implying a clinical deployment.

## Findings and presentations

The `reports/` directory contains curated analysis artefacts, including the [population robustness matrix](reports/POPULATION_ROBUSTNESS_MATRIX.html), [demographic and clinical coverage summary](reports/DEMOGRAPHIC_CLINICAL_POPULATION_COVERAGE.html), and [Week 01 presentation](reports/WEEK_01_PRESENTATION.html). Their evidence sources and intended use are indexed in [reports/README.md](reports/README.md).

## Browse results without running code

The published repository is designed for two audiences:

- **Readers:** open the GitHub Pages results portal for the high-level story and browser-ready dashboards; no local setup is required.
- **Reviewers:** open the rendered notebooks in GitHub to inspect the complete calculations, figures, and saved outputs without re-running them.
- **Reproducers:** follow the [data-access](#data-access-and-governance) and [environment](#environment) instructions to acquire the licensed source data and execute the workflow locally.

After the first GitHub Pages deployment, the portal is available at `https://<github-owner>.github.io/<repository-name>/`. Its source and deployment workflow live in [`site/`](site/) and [`.github/workflows/publish-results.yml`](.github/workflows/publish-results.yml).

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening an issue or pull request. In particular, preserve participant-level split boundaries, do not tune on frozen external sets, and never upload local datasets or model artefacts.

## Licence and citation

The repository licence and citation metadata will be added before the first public release, after the project owner selects the intended licence and author list. Dataset licences remain independent and are governed by their original providers.
