# Reusable source modules

`src/` contains reusable, dataset-aware Python code that is shared across notebooks and scripts.

- `src/data/` — acquisition helpers, data-layout normalization, catalogue generation, and local validation.
- `src/features/` — signal-processing helpers and dataset-specific feature/preprocessing adapters.

Modules should not embed local absolute paths, participant identifiers, credentials, or data artefacts. Paths must be resolved relative to the repository root and the documented `data/` contract.

