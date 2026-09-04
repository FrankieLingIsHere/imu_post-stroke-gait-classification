# Follow-up review: improving synthetic-data utility

## Main conclusion

The latest evidence supports changing the role of synthetic gait data. Our v2/v3 signals can become more statistically plausible yet still damage the classifier. Therefore, synthetic cycles should first be used for self-supervised representation pretraining or domain-robustness stress testing, not directly as labelled healthy examples.

## Practices relevant to this project

1. **Pretrain, then fine-tune on real labels.** A 2025 Nature Communications study found synthetic musculoskeletal gaits useful for generalisation when used for synthetic pretraining and real-data adaptation across populations and sensor settings. This avoids forcing imperfect synthetic healthy signals directly onto the stroke decision boundary.
2. **Generate diversity from a causal/physics model.** That study varied musculoskeletal and gait parameters and simulated sensor settings, rather than copying a small real healthy cohort. For our public-only project, this suggests physics-plausible IMU augmentation or sensor-placement perturbations may be more defensible than unconstrained diffusion cycles.
3. **Require downstream utility, not only fidelity.** Recent wearable studies evaluate both statistical metrics and classifier improvement, and report that diffusion can help one dataset while degrading another. Our negative RevalExo ablation is therefore an important valid finding, not an implementation failure by itself.
4. **Use utility-aware sample selection.** A 2025 NeurIPS utility-centric framework proposes selecting/refining generated samples with downstream task feedback. A safe project adaptation is rejection sampling: generate candidates, score them using only training-fold statistics and a training-fold classifier, retain a small source-balanced subset, and validate once on the frozen external test.
5. **Control sensor-specific variability.** Wearable studies show that synthetic benefit depends on sensor placement and representation. Our lower-back-first RQ means synthetic candidates should be evaluated separately for the lower-back channel and for bilateral-foot channels; pooled score alone is not enough.

## Revised practical plan

1. Keep the real-only model as the final baseline.
2. Use phase-aware synthetic cycles for self-supervised masked reconstruction/contrastive pretraining only; fine-tune every classifier layer on real Voisard/Felius/Sint labels.
3. In parallel, test physically plausible transformations on real healthy cycles: orientation perturbation, amplitude/sensor-noise calibration, cadence-preserving time warps, and cross-channel phase-preserving perturbations. These are augmentation controls, not new participants.
4. If direct synthetic augmentation is revisited, use 5%, 10%, and 20% synthetic-to-real ratios with utility-based filtering and repeated participant-disjoint seeds.
5. Accept only if internal balanced accuracy, frozen RevalExo AUROC/Brier/balanced accuracy, healthy false positives, and calibration all improve or remain non-inferior.

## Decision

The strongest remaining improvement is to repurpose the generator for representation pretraining and use physics-plausible perturbations as the controlled augmentation baseline. Direct labelled synthetic healthy augmentation is currently rejected.

## Pretraining probe completed (2026-09-01)

An unsupervised masked-reconstruction encoder was trained on 4,964 real MAREA/DUO-GAIT cycles plus 1,500 phase-aware synthetic cycles, with no class labels. The CUDA run reduced masked reconstruction loss from 0.0650 to 0.0110. This is only a feasibility result; the encoder must still be fine-tuned on real labelled Voisard/Felius/Sint data and compared with the real-only baseline on frozen RevalExo.

The fine-tuning test then used real labelled Voisard/Felius/Sint data only. On frozen RevalExo it reached AUROC 0.871, Brier 0.182, balanced accuracy 0.643, and 5/7 healthy false positives, versus the official baseline AUROC 0.914, Brier 0.161, balanced accuracy 0.714, and 4/7 false positives. The current synthetic-pretraining recipe is therefore rejected. The failure may reflect representation/domain mismatch and the small, non-clinical synthetic source; it does not justify adding synthetic labels or replacing the baseline.

## References

- Utility of synthetic musculoskeletal gaits for generalizable healthcare applications (Nature Communications, 2025): https://www.nature.com/articles/s41467-025-61292-1
- A diffusion model for inertial based time series generation on scarce data availability (2025): https://pubmed.ncbi.nlm.nih.gov/40374800/
- UtilGen: Utility-Centric Generative Data Augmentation (NeurIPS 2025): https://papers.nips.cc/paper_files/paper/2025/hash/2ea07a4acbf7e38913062fd69a70805f-Abstract-Conference.html
- Enhancing Wearable Fall Detection System via Synthetic Data (Sensors, 2025): https://pmc.ncbi.nlm.nih.gov/articles/PMC12349139/
