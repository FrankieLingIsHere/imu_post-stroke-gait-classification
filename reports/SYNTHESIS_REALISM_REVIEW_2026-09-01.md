# Synthetic gait realism review

## What the latest evidence says

The current source-conditioned baseline failed because it produced low-amplitude, low-variation cycles for both source conditions. The failure is therefore broader than source mixing: the denoiser/sampler is not retaining the distribution's temporal and between-subject variability.

Recent primary studies suggest the following practices are relevant:

1. **Use a real time-series diffusion architecture and sampler.** IMUDiffusion adapts diffusion specifically for multivariate inertial signals rather than treating the task as a generic small-vector generation problem. The current project model is a minimal Conv denoiser and uses a simplified reverse update, so it is not yet a fair implementation of that practice.
2. **Model multiple temporal resolutions.** The ICLR 2024 multi-resolution diffusion work separates trend/coarse structure from finer temporal detail. This directly addresses our low-frequency-power deficit and should be tested before increasing the synthetic sample count.
3. **Condition on meaningful continuous gait variables.** Time Weaver supports heterogeneous metadata conditioning. For this project, cadence/cycle duration, per-channel amplitude, and source should be supplied; a source ID alone cannot control the large healthy-person variation observed in MAREA and DUO-GAIT.
4. **Evaluate held-out subjects and downstream utility.** GaitDynamics evaluates on held-out participants and studies whether generated signals support a downstream task. Matching mean and SD alone is insufficient; synthetic data must improve or preserve participant-disjoint classifier performance without increasing external false positives.
5. **Use multi-domain fidelity checks.** The audit should include marginal statistics, cross-channel correlation, PSD by frequency band, cadence/duration, phase alignment, nearest-neighbour distance, and a train-on-real/test-on-real-vs-synthetic utility test. A synthetic set that only passes global mean/SD is not accepted.

## Revised experiment sequence

1. Freeze the current real-data baseline and external RevalExo test.
2. Replace the simplified reverse step with the standard DDPM posterior equations and a cosine noise schedule; verify reconstruction on held-out real cycles first.
3. Add duration/cadence and channel-amplitude conditioning, with conditioning values computed only from each training cycle.
4. Add a multi-resolution branch (coarse phase trajectory plus fine residual) or a proven temporal diffusion backbone; compare against the corrected single-resolution baseline.
5. Split MAREA and DUO-GAIT by participant before training and audit each condition separately.
6. Apply the realism gate, then add only a small synthetic fraction to the classifier training set. Compare against real-only training using repeated participant-disjoint seeds.
7. Retain synthetic data only if it improves healthy sensitivity/false-positive behaviour on the frozen external test and does not reduce calibration or balanced accuracy.

## Decision

There is a plausible path to improvement, but the present generator is not suitable for augmentation. The next implementation target is a corrected DDPM sampler plus explicit cadence/amplitude conditioning and multi-resolution temporal modeling. More generated cycles before those changes would only amplify an under-dispersed distribution.

## Participant-held-out DDPM-v2 result (2026-09-02)

The proposed correction was implemented as a separate experiment rather than
replacing any baseline. It used a cosine-schedule DDPM posterior, a
source-conditioned multi-resolution temporal denoiser, and six continuous
conditions (per-channel log amplitude and dominant walking-band frequency).
Most importantly, it held out entire MAREA and DUO-GAIT participants before
fitting the generator. Seven people (four MAREA, three DUO-GAIT) were never
used for fitting or to choose generation conditions.

| Source | Held-out real windows | Synthetic windows | SD ratio | PSD relative L1 | Cross-channel correlation MAE | Synthetic/real nearest-neighbour ratio | Real-vs-synthetic feature AUC | Pass |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| MAREA | 498 | 400 | 1.303 | 0.535 | 0.454 | 1.686 | 0.998 | No |
| DUO-GAIT | 452 | 400 | 1.565 | 0.315 | 0.206 | 2.301 | 0.981 | No |

The gates deliberately check distributional spread, spectral structure,
cross-channel coherence, diversity and a held-out real-versus-synthetic
discriminator. Neither source passes. This is a clearer rejection than the
earlier direct-augmentation result: even a corrected sampler and richer
conditioning do not make a small IMU-only source pool sufficient for realistic
new healthy gait generation. No v2 synthetic window may enter classifier
training, pretraining, threshold selection, or any reported subject count.

Artifacts: `scripts/train_heldout_conditional_healthy_diffusion.py`,
`data/processed/healthy_window_ddpm_v2_heldout_fidelity.csv`, and
`data/processed/healthy_window_ddpm_v2_heldout_split.json`.

## Fresh framework screen (2026-09-02)

Recent work shifts the credible next synthesis strategy away from a generator
learnt only from our small MAREA/DUO-GAIT window pool and toward
**physics-grounded virtual IMU generation**. The best currently identified
asset is GAITEX: an openly licensed 17.66-GB release with 19 independent
healthy adults, normal treadmill walking at three speeds, constrained-knee
gait, synchronized 100-Hz full-body optical markers, nine IMUs, per-person
OpenSim models, inverse-kinematics output and timestamps. Its raw released IMU
stream is orientation, not a ready acceleration tensor, so it is *not* a
drop-in binary training or external-test source. Its marker/model information
is precisely what is required to produce virtual acceleration at documented
lower-back and bilateral-foot locations, then audit it against the existing
three-channel magnitude contract.

| Candidate framework | Why it is relevant | Decision in this project |
|---|---|---|
| GAITEX + physics-based virtual IMU simulation | Independent healthy motion trajectories, 100-Hz timing, OpenSim models, and normal gait speed ranges can support whole-gait simulation rather than window recombination | **Best next synthesis candidate**; acquire and audit before any generation |
| WIMUSim / physically plausible augmentation | Explicitly models body, dynamics, placement and hardware; needs 3D motion plus placement calibration | Feasible only after GAITEX audit; existing MAREA/DUO-GAIT IMU-only sources lack the required whole-body dynamics |
| Generative GaitNet + virtual sensors | Research-grade musculoskeletal gait simulator with controllable body, cadence and muscle conditions; open source | Conceptually strongest, but a separate C++/Python-3.6/Ray toolchain plus virtual-sensor implementation; use only after a smaller GAITEX feasibility probe succeeds |
| IMUDiffusion with similarity-score monitoring | Published multiaxial-IMU diffusion approach; follow-up uses similarity scores during training | Retain only as a generative baseline. The reported work trains for thousands of epochs and often per recording, which cannot create independent people or solve our held-out fidelity failure by itself |
| Diff-TSD recurrence-plot diffusion | Recent triaxial-sensor diffusion baseline | Not selected: it converts time series to images and has evidence only on generic HAR, not clinical gait or cross-sensor gait coherence |
| POSE2IMU / text-to-IMU | Produces virtual IMU from generated or video-derived pose | Not practical in the current environment: its documented Linux workflow recommends at least 21 GB GPU memory; the available GPU has 8 GB |

### Predeclared GAITEX feasibility protocol

1. Download and checksum the original release; keep it isolated as a
   simulation-source dataset.
2. Audit subject IDs, normal-gait speed intervals, marker completeness and
   whether the model/marker labels provide unambiguous L5/lower-back, left-foot
   and right-foot attachment coordinates. Reject a missing placement rather
   than guessing one.
3. Generate only normal-gait virtual accelerations at those three placements.
   Fit any sensor/hardware calibration from *training-fold primary data only*;
   RevalExo and all frozen external cohorts remain inaccessible.
4. Compare GAITEX virtual signals with held-out real primary healthy
   participants using time-domain, PSD, cadence, correlation, C-FID/MMD,
   discriminator, TSTR/TRTS, and privacy/nearest-neighbour checks.
5. If and only if the synthesis gates pass, test the signals as a
   self-supervised pretraining source first. They never increase the claimed
   number of original primary-training participants. Direct labelled healthy
   augmentation needs a separate repeated participant-disjoint utility gate.

This protocol adopts the evaluation principle used in recent synthetic-health
time-series work (TSTR/TRTS plus fidelity/diversity) and avoids confusing
high-fidelity within-subject copies with new population coverage.

## Primary references

- Oppel & Munz, *IMUDiffusion* (2024): https://arxiv.org/abs/2411.02954
- Shen & Kwok, *TimeDiff* (ICML 2023): https://proceedings.mlr.press/v202/shen23d.html
- *Multi-resolution Diffusion Models for Time Series Forecasting* (ICLR 2024): https://proceedings.iclr.cc/paper_files/paper/2024/file/d64740dd69bcc90ba225a182984b81ba-Paper-Conference.pdf
- *GaitDynamics* (2025): https://pmc.ncbi.nlm.nih.gov/articles/PMC11957236/
- *GAITEX* (Scientific Data, 2026): https://doi.org/10.1038/s41597-025-06439-x
- WIMUSim (2025): https://doi.org/10.3389/fcomp.2025.1514933
- Generative GaitNet (SIGGRAPH, 2022): https://github.com/namjohn10/GenerativeGaitNet
- IMUEval evaluation framework: https://github.com/H-IAAC/synth-imu-eval
