# MAREA full-cycle diffusion experiment

This experiment replaces the oversmoothing VAE with a compact temporal DDPM-style denoiser trained on complete phase-normalized MAREA Waist/LF/RF cycles. It generates healthy cycles only. The first run is unconditional and is a baseline for determining whether diffusion preserves variation; cadence and environment conditioning will be added only after this baseline is audited.

The generated cycles remain excluded from classifier training until distribution, spectral, bilateral-phase, memorization, and downstream pooled-training checks pass.

Quality audit: `python scripts/audit_marea_vae_cycles.py` with `VAE_CYCLES=marea_diffusion_synthetic_healthy_cycles_float32.npy`. The audit script is reused because both generators output complete 200-point cycles.

## Quality result

The unconditional diffusion baseline failed the cycle realism gate. Real cycles had standard deviation `8.461`, mean per-cycle variability `8.178`, and low-frequency power `216.287`; diffusion cycles had `4.088`, `4.045`, and `57.897`, respectively. The generated mean also shifted to `11.914` from `14.043`. No diffusion samples will enter classifier training. The next implementation must use explicit cadence/environment conditioning and a verified DDPM posterior sampler, with validation against held-out real MAREA cycles before any canonical-window conversion.
