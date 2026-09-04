# Contributing

Thank you for contributing to this research repository. The project prioritises transparent, leakage-safe evidence over headline performance.

## Before changing an experiment

1. Read the active [notebook workflow](notebooks/README.md), the relevant dataset note in `wiki/datasets/`, and the associated report.
2. Keep participants—not windows—independent between development and evaluation partitions.
3. Treat frozen external cohorts as evaluation-only. Do not use them for feature selection, normalization fitting, calibration, threshold selection, or early stopping.
4. Record material analysis work in the next appropriate active notebook. Do not create a new numbered notebook unless the work is a distinct primary stage.
5. Update the relevant Obsidian wiki note and a report when a decision or result changes.

## Data and privacy

Never commit raw sensor recordings, participant metadata, archive downloads, derived arrays, predictions, checkpoints, credentials, or files subject to a dataset provider's access terms. Follow `data/README.md` and the source licence for every dataset.

## Pull requests

Describe the research question, data role, split strategy, preprocessing fitted on each fold, and the exact notebook/report changed. Include only results reproducible from publicly available code plus locally obtained source data.

## Issues

Please avoid posting participant-level information or local filesystem paths. For a result discrepancy, state the notebook/script, data version, seed, environment, and observed behaviour.

