# Source-conditioned MAREA + DUO-GAIT generator

The harmonized complete-cycle pool is used with a source condition, allowing MAREA and DUO-GAIT domain differences to be represented rather than averaged away. Generated cycles are healthy-only and remain excluded from classifier training until quality and downstream gates pass.

## Quality audit (2026-09-01)

The 1,500 generated cycles were split by requested source condition (750 MAREA-conditioned and 750 DUO-GAIT-conditioned) and compared with the corresponding real full-cycle distributions. This is a **failed realism gate** for both conditions:

| Group | Mean | SD | Between-cycle mean SD | 2nd-difference roughness | Low-frequency power |
|---|---:|---:|---:|---:|---:|
| MAREA real | 14.010 | 8.411 | 1.282 | 0.757 | 908.899 |
| DUO-GAIT real (m/s²) | 14.510 | 9.057 | 0.926 | 1.128 | 1004.889 |
| MAREA-conditioned synthetic | 11.786 | 4.104 | 0.333 | 0.495 | 288.258 |
| DUO-conditioned synthetic | 12.183 | 4.553 | 0.413 | 0.822 | 229.137 |

Both conditional outputs have approximately half the real amplitude variation and substantially lower low-frequency power. The source condition therefore did not preserve the domain-specific distributions; the model still generated an over-smoothed, under-dispersed average healthy gait. These cycles must not be added to classifier training. The failure is attributable to the current generator/sampler and conditioning design, not evidence that MAREA or DUO-GAIT cannot be pooled. The audit is stored in `data/processed/marea_duogait_conditioned_cycle_quality.csv`.

## Decision

Keep the checkpoint as a reproducible baseline only. Before another synthesis attempt, revise the generator to condition on cadence/duration and amplitude statistics, use a proper DDPM posterior reverse update, and evaluate held-out participants with per-source distribution and nearest-neighbour checks. Real MAREA and DUO-GAIT cycles remain eligible for separate source-aware preprocessing and real-data experiments.

## Revised sampler/conditioning run (2026-09-01)

The implementation was corrected to use the standard DDPM posterior variance term and to condition on source, cycle duration, and three channel-amplitude statistics. It ran on CUDA and produced 1,500 cycles. Compared with the prior run, the generated distributions improved substantially:

| Group | SD | Between-cycle mean SD | 2nd-difference roughness |
|---|---:|---:|---:|
| MAREA real | 8.411 | 1.282 | 0.757 |
| MAREA-conditioned v2 | 6.675 | 0.938 | 0.537 |
| DUO-GAIT real | 9.057 | 0.926 | 1.128 |
| DUO-conditioned v2 | 7.592 | 0.780 | 1.056 |

This is an improvement, not a pass. Amplitude and inter-cycle variability are now directionally credible, and DUO-GAIT temporal roughness is close to real data. MAREA remains too smooth, and no held-out-subject or downstream classifier gate has yet been run. Keep v2 quarantined until those tests pass.

## Participant-level similarity check (2026-09-01)

Flattened-cycle nearest-neighbour distances were compared with a real-to-real reference. Synthetic cycles were not suspiciously close to individual real cycles, but they were substantially farther from the real manifold:

| Source condition | Synthetic-to-real mean distance | Median | Real-to-real reference mean |
|---|---:|---:|---:|
| MAREA | 169.822 | 170.018 | 68.803 |
| DUO-GAIT | 192.548 | 191.309 | 77.346 |

This rules against simple memorisation but confirms inadequate waveform fidelity. The next gate is therefore not “generate more”; it is to improve manifold fidelity with a proper temporal/multi-resolution denoiser, then repeat this check and run the downstream classifier ablation.

## Multi-resolution denoiser run (2026-09-01)

A coarse branch (4x temporal pooling followed by interpolation) was added to the corrected DDPM denoiser. It ran on CUDA under the same conditions. Results:

| Condition | Synthetic SD | Roughness | Synthetic NN mean | Real-to-real NN mean |
|---|---:|---:|---:|---:|
| MAREA | 6.536 | 0.536 | 166.021 | 70.042 |
| DUO-GAIT | 7.599 | 1.028 | 197.605 | 77.268 |

This did not improve manifold fidelity: nearest-neighbour distances remain more than twice the real-to-real reference. The architecture is therefore not admitted for augmentation. The result suggests that a simple pooled branch is insufficient; the next credible alternative is a phase-aware temporal architecture with a proper multi-resolution loss or a pretrained inertial-motion backbone. All classifier baselines and external tests remain unchanged.

## Phase-aware denoiser run (2026-09-01)

Fixed circular gait-phase embeddings were added while retaining the corrected DDPM sampler and source/duration/amplitude conditions. The CUDA run produced MAREA synthetic SD 6.060, roughness 0.636, nearest-neighbour mean 119.901 versus real-to-real 70.042; DUO-GAIT SD 7.325, roughness 1.215, nearest-neighbour mean 129.191 versus 77.268. This is the strongest candidate so far, but remains quarantined pending held-out-participant and downstream classifier gates.

## Downstream classifier ablation (2026-09-01)

The phase-aware synthetic cycles were resampled to the canonical 500x3 window contract and added as healthy data, with 60 grouped synthetic parent IDs. The model was retrained on CUDA and evaluated on frozen RevalExo:

| Training set | AUROC | Brier | Balanced accuracy |
|---|---:|---:|---:|
| Real-only baseline | 0.914 | 0.161 | 0.714 |
| + phase-aware synthetic healthy | 0.900 | 0.197 | 0.571 |

The synthetic augmentation fails the downstream utility gate and is rejected for final classifier training. This does not invalidate the improved waveform diagnostics; it shows that distributional resemblance was still insufficient to improve the clinical decision boundary. Keep the checkpoint and all audit outputs for reproducibility, but use real data only for the final classifier.
