---
type: dataset
population: "20 healthy adults (12M/8F, avg age 33.4), indoor/outdoor/treadmill"
sensors: "waist, wrist, bilateral ankle (128 Hz)"
role: healthy-only-reference
---

MAREA (Khandelwal & Wickstrom, 2017), *Evaluation of the performance of accelerometer-based gait event detection algorithms in different real-world scenarios using the MAREA gait database*, *Gait and Posture* 51:84–90. MAREA stands for Movement Analysis in Real-world Environments using Accelerometers (verified via the dataset's own CAISR documentation). Subjects 1–11 walked indoors and on a treadmill; subjects 12–20 walked outdoors, letting the same people be compared across environments.

## Key findings (this review's own re-mining)

- **A genuine signal-processing failure, caught and fixed.** An initial naive Fourier-domain peak-picking approach locked onto a spectrally stronger second harmonic rather than the true fundamental stride frequency, returning physiologically implausible cadence estimates. Switching to autocorrelation-based detection resolved this cleanly. (Corrected 2026-07-22: earlier drafts of this page and the manuscript stated specific ranges, 225–270 and 110–135 steps/min, for this failure that were not traceable to any printed notebook output — only single point estimates for the *separate* waist-channel finding below actually appear in the notebook. Removed rather than guessed at, per this project's never-fabricate-a-number rule.)
- **A second, related finding**: a waist sensor's dominant signal period reflects one bounce per step, while a single ankle sensor's reflects one cycle per stride — the same step-vs-stride conversion factor cannot be applied uniformly across placements. Applying the ankle-appropriate factor to the waist channel unadjusted produced an implausible 246 steps/min; correcting for placement brought waist/left-ankle/right-ankle into close agreement (~121.5–122.9 steps/min).
- Wrist remains both higher on average and markedly more variable (M=130.2, SD=29.6, vs. SD<6 elsewhere) — consistent with greater between-person variability in arm-swing than leg motion.
- Cadence differs modestly by environment even within the same people: ~9–10 steps/min slower indoors than treadmill/outdoor.
- **Contributes to the pooled independent healthy reference (RQ1, added 2026-07-22)**: MAREA's waist-sensor trials feed [[classification-methods]]'s cross-dataset check — 20 subjects' worth of features pooled with [[duo-gait]], [[oxwalk]], [[camargo-2021]], and [[gaitmotion]] to stress-test whether [[voisard-2025]]/[[felius-dataset]]'s discriminative features generalize beyond the two datasets that identified them. (Two earlier versions of this check were tried and superseded the same day: first, testing MAREA against its own indoor-vs-treadmill environment label — a real result, 0.73 accuracy, removed once the user objected it didn't serve RQ1's actual question. Then, applying a Voisard/Felius-trained classifier to MAREA as an out-of-sample test — MAREA had the worst false-positive rate of any source, 100% — removed a second time once the review's scope was set to feature engineering only, no classifier training of its own. See [[classification-methods]] for the full history.)

## Links

The source of [[sensor-placement]]'s "wrist is the least reliable single placement observed" finding, and the step-vs-stride periodicity fix flagged as a testable hypothesis against the wider published literature in [[future-directions]].

## Source-conditioned synthesis audit (2026-09-01)

A GPU-trained diffusion baseline generated 750 MAREA-conditioned and 750 DUO-GAIT-conditioned healthy full gait cycles. Both groups were under-dispersed (SD 4.104 and 4.553 versus 8.411 and 9.057 in corresponding real data) and had much lower low-frequency power (288.258 and 229.137 versus 908.899 and 1004.889). Conditioning did not preserve source-specific realism, so synthetic cycles remain quarantined and are not used for classifier training. This is a generator/sampler failure, not a rejection of the real MAREA or DUO-GAIT datasets.

The follow-up literature review recommends correcting the DDPM posterior sampler, adding cadence/duration and amplitude conditioning, and testing multi-resolution temporal diffusion before any further augmentation. See [[../reports/SYNTHESIS_REALISM_REVIEW_2026-09-01]] for the experiment sequence and references.

The corrected v2 run (2026-09-01) used the standard DDPM posterior variance term plus source, duration, and channel-amplitude conditioning. It improved synthetic SD to 6.675 (MAREA condition) and 7.592 (DUO condition), versus real SD 8.411 and 9.057. DUO temporal roughness also approached real data, but MAREA remained oversmoothed. v2 is therefore promising but quarantined pending held-out-subject and downstream classifier tests.

The participant-level nearest-neighbour check found no memorisation, but synthetic cycles remained far from the real manifold (mean distance 169.822 for MAREA and 192.548 for DUO-GAIT, compared with real-to-real references 68.803 and 77.346). This confirms that variance recovery alone is insufficient; temporal/multi-resolution architecture improvement is required before augmentation.

The phase-aware follow-up improved nearest-neighbour fidelity to 119.901 (MAREA) and 129.191 (DUO-GAIT), compared with real-to-real references 70.042 and 77.268. It is the leading synthetic candidate but remains quarantined pending held-out-participant and downstream classifier gates.

The downstream ablation failed: adding 1,500 phase-aware synthetic healthy cycles reduced frozen RevalExo AUROC from 0.914 to 0.900, worsened Brier from 0.161 to 0.197, and left balanced accuracy at 0.571 versus 0.714. Synthetic data is therefore rejected for final classifier training; the real MAREA and DUO-GAIT cycles remain usable for source-aware analysis.

The follow-up review recommends repurposing synthetic cycles for self-supervised representation pretraining, then fine-tuning on real labelled data. It also recommends physics-plausible real-signal perturbations and utility-aware sample selection before any direct synthetic augmentation. See [[../reports/SYNTHESIS_LIMITATIONS_REVIEW_2026-09-01]].

A masked-reconstruction pretraining probe completed on CUDA using 4,964 real MAREA/DUO-GAIT cycles plus 1,500 synthetic cycles without labels; loss decreased from 0.0650 to 0.0110. This is not evidence of classifier benefit yet. The encoder remains a candidate pending fine-tuning on real labelled data and frozen RevalExo evaluation.

Fine-tuning that encoder on real labelled data only failed the frozen external gate: AUROC 0.871, Brier 0.182, balanced accuracy 0.643, and 5/7 healthy false positives versus baseline AUROC 0.914, Brier 0.161, balanced accuracy 0.714, and 4/7 false positives. The current synthetic-pretraining recipe is rejected, while the checkpoint is retained for reproducibility.

A simple pooled multi-resolution denoiser was tested on 2026-09-01. It preserved variance but did not improve nearest-neighbour fidelity (MAREA 166.021 vs real-to-real 70.042; DUO-GAIT 197.605 vs 77.268), so it was not admitted. A phase-aware architecture or pretrained inertial-motion backbone is now required before another augmentation decision.
