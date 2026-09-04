# Evidence gate for cross-dataset IMU stroke classification

Date: 2026-09-03

## Decision first

No new model, adapter, normalization rule, or synthetic-data experiment should
start until it passes the evidence gate in this document. The literature does
not support blindly transplanting a high-scoring HAR method into the current
stroke-versus-healthy task. The closest reproducible studies show that:

1. cross-dataset wearable-IMU generalization is substantially harder than
   within-dataset validation;
2. no domain-generalization method wins consistently across shifts or
   backbones;
3. accelerometer-only input can generalize better than acceleration plus
   gyroscope;
4. target-aware adaptation is not evidence of source-only generalization; and
5. synthetic IMU data can improve some held-out people, but it can also harm
   specific people and becomes less effective as sensors and classes increase.

The current lower-back acceleration baseline is therefore not obsolete. The
next experiment must be justified by an exact task/sensor/split match, an
official-code trace, and a predeclared validation protocol. This audit did not
train a model or read any frozen test signal.

## 1. The project claim that must be protected

The intended final output is a binary stroke-versus-healthy classifier using
wearable IMU gait. The minimal-sensor research question is lower-back-first;
the established three-channel prototype uses acceleration magnitude from lower
back, left foot, and right foot. The current development sources are Felius,
Voisard, and Sint. RevalExo and frozen NONAN results must not be used for
hyperparameter, adapter, threshold, or architecture selection.

This is a disease-status problem. It is not equivalent to:

- walking versus non-walking activity recognition;
- classification of known daily activities;
- stroke gait severity or gait-pattern subtype prediction;
- within-person generation of additional windows; or
- target-aware domain adaptation where target samples are available at train
  time.

Any paper solving one of those problems is supporting evidence only, not a
direct performance comparator.

## 2. What recent researchers actually did

| Work | Actual task and data | Preprocessing/model protocol | Validation and target access | What genuinely transfers here | What does not transfer |
|---|---|---|---|---|---|
| BenchHAR (2026) | Common-activity HAR over 14 datasets, about 258k windows and more than 300 subjects | Harmonized 6-second, 20-Hz windows; instance-normalized input for self-supervised encoders; frozen embeddings followed by a classifier | Dataset-group folds hold complete datasets out; source classifier code also performs a random 80/20 embedding split | Large-scale source-only SSL, frozen-encoder evaluation, complete-dataset holdout, explicit acceleration-only ablation | Activity labels, body locations, sample scale, and 20-Hz/6-second contract differ from stroke gait. Its source validation split must not replace participant grouping here |
| HAROOD (KDD 2026) | Generic HAR under cross-person, position, device, time, and dataset shifts | Unified CNN/Transformer benchmark over 16 OOD algorithms; source-domain validation and matched tuning | Domain-held-out testing; oracle target selection is separately identified as invalid for deployment | Compare ERM before complex DG; evaluate methods over several shifts/backbones; report worst-domain behavior | No algorithm ranking can be copied directly. DANN, GroupDRO, and other methods are not reliably superior across settings |
| ContrastSense (2024) | Source-only domain-generalized HAR using user/device/dataset and timestamp metadata | Two-stage contrastive pretraining, source-domain queues, momentum encoder, hard negatives, then Fisher-weighted supervised fine-tuning | Cross-domain and leave-one-domain-out experiments; no target needed for its DG claim | A concrete metadata-aware source-only SSL design | The official cross-dataset preprocessing merges common activity classes and uses a random 85/15 split of source windows. Its released cross-dataset entry point also requires careful argument/class-count checking; it is not plug-and-play for binary clinical labels |
| CALDA/CALDG (2024) | Contrastive adversarial domain learning for HAR | Domain-adversarial and contrastive objectives | Some official examples use target-domain adaptation and `best_target` selection; the DG variant must be separated from those runs | Contrastive/domain objectives as controlled research comparators | Target-aware CALDA results cannot justify a model that must generalize without target data |
| DAGHAR (2024) | Harmonization of six smartphone IMU HAR datasets | Dataset-specific adapters to a common intermediate representation containing sensor axes, user, trial, activity, placement, and source | Standardized downstream evaluation after explicit harmonization | The adapter-first principle: preserve provenance and resolve sampling rate, units, gravity, labels, and partitions before pooling | Harmonization does not eliminate intrinsic population/protocol shift and the activity task is different |
| Brasiliano et al. (Scientific Reports, 2026) | 85 stroke and 97 age/sex-matched controls; five synchronized MIMUs during repeated 10-m walks | Static frame calibration, gravity alignment/removal, low-pass filtering, gait-event extraction, participant-level feature aggregation, correlation culling, sequential backward selection, SVM/KNN/tree models | Participant-level repeated splits; no independent external site. Initial feature filtering used the 144-person feature-selection pool before repeated 70/30 partitions | Clinical preprocessing, age/sex matching, participant aggregation, interpretable lower-back gait features, simple-model comparator | Its five-sensor/event-feature pipeline cannot be claimed for our lower-back magnitude stream. Reported scores are not independent cross-site validation |
| Zhang et al. (2025) | Walking versus non-walking, trained on 20 older adults and tested on 47 stroke survivors | Lower-back 2-second windows, per-axis mean subtraction, CNN, rotation augmentation | Participant split in training; Felius balance tasks represent non-walking and 2MWT represents walking | Lower-back IMU can support robust gait detection | Disease status is not the label. Protocol-separated activities make the near-perfect external result irrelevant to stroke-versus-healthy classification |
| IMUDiffusion (Scientific Reports, 2025) | Four/eight activity classes from RealDISP; one or three 6-axis IMUs | 160-sample windows with 40-sample shift; axis-wise standardization; STFT; one unconditioned DDPM per activity; 3-block ResNet/attention U-Net; 3000 diffusion steps; 4500 epochs | Synthetic data is added only to training in LOSO classification; real held-out participant is the test. 3840 sequences are generated per class and LOSO step | Generator fitting must be fold-local; test data stays real; synthetic ratio and per-person effects must be reported | It synthesizes activity windows, not new healthy people. Some participants deteriorate; benefit drops with more sensors/classes; realism assessment is mainly visual plus classifier utility and the authors request better objective metrics |
| PPDA/WIMUSim (2025) | Generic activity/workout HAR using paired motion and real IMU | Fits body, dynamics, placement, and hardware parameters from synchronized motion-plus-IMU, then perturbs physically meaningful parameters | Cross-subject HAR comparisons against signal transforms | A technically grounded route to placement/hardware/motion variation when synchronized kinematics exist | MAREA/DUO-GAIT IMU alone cannot identify the required physical model. The evidence is generic HAR and the 2025 paper is still a preprint |
| IMUEval (2025 software) | Reproducible synthetic-IMU model/evaluation toolkit | C-FID, JS, MMD, DTW R2R/R2S/S2S, discriminative and predictive scores; several GAN/diffusion baselines | Software case study, not a clinical validation paper | Useful metric implementation reference | It cannot establish clinical realism or population expansion by itself |

## 3. Reproducibility findings from official code

The official repositories were inspected rather than relying only on abstracts.
Three details materially affect interpretation:

1. BenchHAR applies `InstanceNorm1d` to each input window for embedding
   extraction, switches the pretrained encoder to evaluation mode, extracts
   embeddings under `no_grad`, and trains the downstream classifier without a
   second instance-normalization step. Its generic classifier code performs a
   stratified random 80/20 embedding split. For this project, participant IDs
   must override that random split.
2. ContrastSense's cross-dataset builder holds out one dataset but randomly
   divides pooled source windows 85/15. Its public cross-dataset runner defaults
   to evaluation mode, constructs a five-class model in that entry point, and
   uses several `argparse type=bool` flags. A faithful port therefore requires
   unit tests for the split, class count, and command-line booleans before a
   scientific run.
3. HAROOD explicitly exposes ERM, DANN, CORAL, MMD, GroupDRO, Fish/Fishr,
   ERM++, and other methods under one pipeline. Its paper finds that method
   rankings change by shift and backbone. This supports a matched benchmark,
   not selecting one method by reputation.

These are not accusations that the releases are invalid. They show why direct
copying can silently create a different experiment from the one reported in a
paper.

## 4. Why our earlier negative results are plausible

### 4.1 More channels are not automatically better

Our three-source lower-back test found acceleration plus gyroscope less stable
than acceleration alone, especially on held-out Sint. BenchHAR independently
reports several cross-dataset settings where accelerometer-only input exceeds
acceleration plus gyroscope. Sensor fusion can increase source/device
identifiability as well as biological information. The result does not prove
gyroscope is useless; it rejects unadapted gyroscope magnitude under the
current contract.

### 4.2 Generic domain objectives can trade sensitivity for specificity

Our GroupDRO run improved Sint discrimination but increased healthy false
positives and harmed other sources. HAROOD reports no universal winner and
frequent dependence on backbone and shift. This is consistent with the
literature. A pooled average gain is not enough for a clinical binary rule.

### 4.3 The first synthetic generators were not faithful implementations

The early VAE/minimal denoiser, simplified reverse update, and cycle-to-window
conversion were weaker than IMUDiffusion or physics-based systems. Those runs
cannot reject diffusion as a family. Later experiments corrected the posterior,
added conditioning, generated directly in the 500 x 3 classifier contract, and
used participant-held-out realism checks. They still produced under-dispersion,
high real-versus-synthetic separability, or no repeatable classifier benefit.
Those later failures are meaningful for the available MAREA/DUO-GAIT data and
the tested architecture; they still do not prove that every generator must
fail.

### 4.4 Synthetic windows do not create synthetic participants

IMUDiffusion demonstrates that generated training windows can help a classifier
on some unseen participants. It does not demonstrate that the generator creates
new independent demographic or clinical subjects. MAREA/DUO-GAIT healthy-only
generation cannot add age, device, protocol, comorbidity, or post-stroke
variation that is absent or unlabelled in the source. It can regularize the
healthy manifold; it cannot establish population coverage or external clinical
validity.

### 4.5 Normalization can erase both nuisance and disease signal

Window-wise instance normalization is credible in generic cross-dataset SSL,
but lower-back RMS/amplitude is one of this project's age-adjusted
stroke-discriminative findings. Therefore instance normalization is an ablation,
not an automatic fix. Every normalization branch must report which clinical
features it removes and must use statistics fitted only from training data.

### 4.6 Headline studies often answer a different question

The 2025 lower-back CNN's external success concerns walking detection, not
stroke diagnosis. The 2026 clinical stroke study uses calibrated axes,
gait-event features, age/sex matching, and five sensors, not magnitude-only
fixed windows. These papers justify components and controls, not direct expected
accuracy for this repository.

## 5. Mandatory evidence gate before another experiment

Every proposed experiment must have a one-page protocol answering all items
below. A missing item means the run does not start.

### A. Claim match

- Is the cited task stroke versus healthy, generic HAR, gait detection,
  severity, or synthesis?
- Is the intended inference unit a window, trial, or participant?
- Does the paper demonstrate an unseen participant, an unseen dataset/site, or
  only a random split?

### B. Sensor and preprocessing match

- Exact body placement, modality, signed axes versus magnitude, units, sample
  rate, gravity convention, filtering, window duration, overlap, and event
  definition.
- Dataset-specific adapter test showing channel order, unit conversion,
  synchronization, and labels before pooling.
- A statement of which disease-relevant features a normalization step removes.

### C. Split and leakage match

- Participant IDs are indivisible across train/validation/test.
- A complete source is held out for transport testing when source
  generalization is claimed.
- Preprocessing statistics, feature selection, generator fitting, synthetic
  conditions, calibration, and early stopping use training data only.
- Source validation, not target performance, selects hyperparameters.
- RevalExo and frozen NONAN are not used to choose or iterate the method.

### D. Official implementation trace

- Link the primary paper and official code.
- Map every local stage to a released function/configuration or explicitly mark
  it as a project-specific adaptation.
- Unit-test class count, input shape, sampling rate, normalization, split IDs,
  target access, and CLI defaults.
- Compare against matched ERM before claiming a specialized objective helps.

### E. Clinical decision metrics

- Participant-level AUROC, Brier score, balanced accuracy, sensitivity,
  specificity, false-positive count, and confidence intervals.
- Per-source and worst-source results, not only pooled means.
- Age/protocol/device strata where metadata permits.
- Non-stroke clinical hard negatives remain a separate differential-specificity
  evaluation unless a new training protocol is predeclared.

### F. Additional synthetic-data requirements

- Train a generator separately inside each training fold; never train on a
  validation/test participant.
- Add synthetic samples to training only. Validation and test remain real.
- Do not count synthetic windows as new participants.
- Evaluate fidelity (C-FID or embedding-FID, MMD/JS), spectra, cadence,
  cross-channel phase/correlation, diversity (R2R/R2S/S2S DTW), nearest-neighbor
  privacy/memorization, discriminative score, TSTR, TRTS, and downstream TRTR
  versus TRSTR.
- Report each held-out participant/source because average improvement can hide
  harmed people.
- Test fixed synthetic ratios selected on source-only validation; do not tune
  the ratio on RevalExo or NONAN.

## 6. Evidence-ranked pathways after this gate

These are candidates for protocol drafting, not permission to run them yet.

1. **Highest priority: exact source-only benchmark.** Reproduce ERM first, then
   a small set of HAROOD comparators (CORAL and ERM++) under identical
   participant/source folds. Keep lower-back acceleration as the primary track
   and three-channel acceleration as the secondary track. No target data is
   available during fitting.
2. **High priority: clinical feature baseline.** Implement training-fold-only
   lower-back features supported by the 2026 stroke study and this wiki (RMS,
   timing/variability where events are reliable) with logistic/SVM models. This
   checks whether the deep model is learning a clinical signal or a source
   shortcut.
3. **Conditional priority: source-only SSL.** A BenchHAR-style frozen encoder
   can be tested using task-relevant real walking data, acceleration-only first.
   It must retain participant grouping and compare window-wise instance
   normalization against a gravity/amplitude-preserving branch.
4. **Research branch: ContrastSense-style metadata-aware SSL.** Eligible only
   after its source queues, time-aware negatives, class count, and split logic
   are ported and unit-tested. It should not be approximated by a generic DANN.
5. **Quarantined branch: synthetic enrichment.** IMUDiffusion is a defensible
   generative baseline, and PPDA is a defensible physics route only where
   synchronized kinematics and sensor calibration exist. Neither can be used to
   claim additional participants or replace a second paired external cohort.

## 7. What is ruled out now

- Blind concatenation of public datasets after global normalization.
- Selecting an approach because its paper reports higher accuracy on a
  different task.
- Target-aware DANN/CALDA while describing the result as domain generalization.
- Repeating generic gain/noise/time-warp augmentation without a new physical
  model and a predeclared held-out-source test.
- Adding synthetic healthy windows directly because their global mean and SD
  look similar.
- Using RevalExo, frozen NONAN, or any external cohort repeatedly as a model
  development scoreboard.
- Claiming clinical readiness without a new untouched paired stroke/healthy
  external cohort.

## 8. Research conclusion

The accumulated negative results do not show that all public datasets or all
advanced methods are useless. They show that source shift, task mismatch, and
validation design dominate the apparent benefit. The literature supports a
more disciplined sequence: adapter verification, matched ERM, source-held-out
selection, clinically interpretable comparator, then one faithfully reproduced
source-only method. Synthetic data remains an auxiliary training intervention,
not evidence of a larger cohort.

### Exact-code correction added 2026-09-03

Executed notebook 33 subsequently compared local code with fixed commits of the
official repositories. It confirmed that the compact CNN is not canonical
InceptionTime, the ERM++ member is only an ERM++-style subset, the earlier
GroupDRO run grouped source×class rather than source domains, all project
MiniROCKET runs used a reduced 2,000-feature configuration rather than the
canonical 10,000-feature scaled RidgeCV pipeline, and the local time-domain
DDPMs are not IMUDiffusion reproductions. These negative results therefore
reject their exact local configurations, not the complete method families.
See `PRIOR_METHOD_CODE_ALIGNMENT_AUDIT_2026-09-03.md`.

## Primary sources and official implementations

- [BenchHAR paper](https://arxiv.org/html/2605.08296) and [official code](https://github.com/saiketa/HAR-Bench)
- [HAROOD paper](https://arxiv.org/abs/2512.10807) and [official code](https://github.com/AIFrontierLab/HAROOD)
- [ContrastSense paper](https://tanrui.github.io/pub/ContrastSense.pdf) and [official code](https://github.com/MaginaDai/ContrastSense-Public)
- [CALDA paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC10805953/) and [official code](https://github.com/floft/calda)
- [DAGHAR dataset harmonization paper](https://www.nature.com/articles/s41597-024-03951-4)
- [Brasiliano et al. stroke classification study](https://www.nature.com/articles/s41598-026-43666-7)
- [Zhang et al. lower-back walking-recognition study](https://link.springer.com/content/pdf/10.1007/s11517-025-03466-z.pdf)
- [IMUDiffusion paper](https://www.nature.com/articles/s41598-025-01614-x)
- [PPDA paper](https://arxiv.org/abs/2508.13284) and [official code](https://github.com/STRCWearlab/PPDA)
- [IMUEval software](https://github.com/H-IAAC/synth-imu-eval)
- [2024 post-stroke gait-classification systematic review](https://www.sciencedirect.com/science/article/pii/S0966636224000559)
