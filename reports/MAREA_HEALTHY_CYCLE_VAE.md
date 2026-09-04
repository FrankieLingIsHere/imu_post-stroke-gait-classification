# MAREA healthy full-cycle VAE

The first generative model operates on complete phase-normalized MAREA gait cycles, not arbitrary 5-second windows. It learns synchronized Waist/LF/RF magnitude waveforms with 200 phase points and samples new healthy cycles. A compact convolutional VAE is used because the annotated MAREA subset contains 11 participants; a large diffusion model would have higher memorization risk at this stage.

Outputs are `data/processed/marea_vae_synthetic_healthy_cycles_float32.npy`, its metadata CSV, and the VAE checkpoint. These cycles are not yet added to classifier training. They must pass waveform, spectral, bilateral-phase, latent memorization, and downstream pooled-training tests first.
