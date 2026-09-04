# Conservative synthetic healthy-data trial

## Rationale

The added healthy sources introduced legitimate but difficult-to-align variation. A synthetic healthy branch may help expose the classifier to intermediate healthy patterns, but it cannot create clinically new stroke phenotypes. The first trial therefore uses a transparent control rather than an opaque generator.

## Method

`scripts/synthesize_healthy_phase_mixed.py` creates 25% as many synthetic windows as real healthy windows within each source. Each synthetic window is a convex interpolation of two different real healthy windows from the same source. This is a conservative window-mixing control, not yet a phase-aligned or diffusion generator. The output remains exactly `500 x 3`, uses the current acceleration-magnitude representation, and carries synthetic provenance metadata. No validation or RevalExo data are used.

## Guardrails

Synthetic windows must be treated as training augmentation only. Parent participants must remain inside the training fold; synthetic samples must never be split across train and validation by parent leakage. The generator is not allowed to create stroke labels. Before classifier training, compare amplitude distributions, power spectra, autocorrelation, left/right relationships, and nearest-neighbour similarity against real healthy windows.

## Output

- `data/processed/synthetic_healthy_phase_mixed_windows_float32.npy`
- `data/processed/synthetic_healthy_phase_mixed_metadata.csv`
- `data/processed/synthetic_healthy_phase_mixed_summary.csv`

The next experiment is a controlled real-only versus real-plus-synthetic ablation at 10%, 25%, and 50% synthetic healthy ratios, evaluated with the same lower-back and three-channel tracks and frozen RevalExo.
