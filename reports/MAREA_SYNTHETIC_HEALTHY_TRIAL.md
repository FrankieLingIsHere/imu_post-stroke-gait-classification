# MAREA-only synthetic healthy trial

MAREA is the first external source admitted to the canonical synthetic branch because its verified subset was already mapped to Waist/LF/RF, resampled to 100 Hz, converted to acceleration magnitude, and windowed as 500 × 3.

The trial creates 20% additional windows within each MAREA participant by convexly mixing two distinct real MAREA windows. This is a transparent control before attempting a diffusion generator. Synthetic participant IDs retain both parent IDs and cannot be used as independent subjects for validation.

Outputs are `data/processed/marea_synthetic_healthy_windows_float32.npy`, `marea_synthetic_healthy_metadata.csv`, and `marea_synthetic_healthy_quality_summary.csv`. The artifact is not yet admitted to classifier training; waveform, spectrum, autocorrelation, parent-neighbour similarity, and downstream ablation checks must pass first.

Run the quality gate with `python scripts/audit_marea_synthetic_quality.py`. It writes `marea_synthetic_quality_summary.csv` and `marea_synthetic_nearest_neighbour_audit.csv`.

## Quality-gate result

The windows pass structural checks and preserve the MAREA mean (`1.430` synthetic vs `1.432` real) with similar lag-25 autocorrelation (`-0.483` vs `-0.506`). Nearest-neighbour distance is slightly smaller than the real-to-real reference (`23.65` vs `25.49`), but does not indicate exact duplication. They fail the completeness check for variability and spectral energy: overall standard deviation is `0.661` synthetic vs `0.882` real, and mean spectral energy is `0.0058` vs `0.0139`. Decision: do not train the classifier with this artifact yet. The generator needs a variance-preserving method, such as phase-aligned cycle recombination or a small conditional diffusion model, followed by the same gate.
