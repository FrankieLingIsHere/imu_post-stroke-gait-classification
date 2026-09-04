# Prior-method code alignment audit — 2026-09-03

## Decision first

The concern was justified: several previous negative experiments were interpreted more broadly than their implementations support. Most of them validly reject a particular local configuration, but they do **not** reject the named research method as a whole.

The current lower-back ensemble remains the empirical incumbent because notebook 29 evaluated it under complete-source holdouts, five seeds, participant-safe inner validation, and no frozen external selection. Its name must remain precise: it is a compact Inception-style ensemble containing ERM, HAROOD-style CORAL, and an ERM++-style optimization member. It is not canonical InceptionTime and does not reproduce full ERM++.

## Audit method

Repository implementations were compared with primary papers and shallow clones of official repositories. Exact upstream commits are recorded in `data/processed/prior_method_upstream_commits.csv`; local implementation hashes are rendered in executed notebook 33. RevalExo and NONAN signals were not loaded.

## Code-level verdicts

| Family | What prior researchers actually implemented | What this repository implemented | Valid conclusion |
|---|---|---|---|
| InceptionTime | Six Inception modules, residual after each group of three, kernels about 40/20/10, 32 filters per branch, ReLU, long optimization, and five-network ensembling | Two modules, residual every module, kernels 7/15/25, 16 filters, GELU, short source-selected training | Valid compact CNN baseline. Canonical InceptionTime has not been tested. |
| MiniROCKET | Default 10,000 features, maximum 32 dilations, feature scaling, RidgeClassifierCV across logarithmic alpha values | Historical runs used 2,000 features, 16 dilations, fixed Ridge alpha 1.0; notebook 31 used fixed logistic regression for probabilities | Valid reduced MiniROCKET results only. They do not reject canonical MiniROCKET. |
| HAROOD CORAL | Classification loss per source plus all-pairs source feature mean/covariance alignment | Same mean-plus-covariance loss and source-pair averaging, with binary BCE substituted appropriately; lambda fixed at 1 | Strong core match. Result is credible for this backbone and lambda, but not an exhaustive CORAL search. |
| ERM++ | Pretrained initialization, linear probing, stronger regularization, SMA, validation-selected duration, then retraining on all source data | Randomly initialized compact CNN with head warm-up, higher weight decay, and SMA | Correctly labelled `ERM++-style`; not full ERM++. Its local ensemble contribution remains valid. |
| GroupDRO | One adversarial weight per source-domain minibatch, exponentially increased for high-loss domains | Weights over source×class cells, one seed, fixed duration | Core q-update is recognizable, but the grouped object differs. Previous result does not reject source-domain GroupDRO. |
| Attention MIL | Gated `tanh(Vh) × sigmoid(Uh)` attention, softmax over instances, one bag-level Bernoulli loss | Same operator and loss over participant bags | Operator is faithful. Participant-diagnosis bag semantics and 16-window subsampling are project-specific; result rejects this adaptation only. |
| IMUDiffusion | Six-axis 160-step sequences transformed with STFT; three-block ResNet/self-attention U-Net; separate sensor schedules; 3,000 denoising steps; 4,500 epochs; Smooth-L1; one unconditioned model per activity inside LOSO | Time-domain 200/500-point acceleration magnitudes; 100–200 steps; about 80–100 epochs; no self-attention; joint source conditioning; MSE | Local DDPM failures do not reject IMUDiffusion. They are not reproductions of that method. |
| IMUEval realism framework | C-FID, JS/MMD, R2R/R2S/S2S DTW, discriminative and predictive scores | Spectra, roughness, correlation, nearest-neighbour and discriminator gates | Useful partial realism audit, not the complete published framework. |
| PPDA/WIMUSim-style physics | Motion/body/placement/hardware parameter modelling using paired kinematics and IMU | Hand-set gain, noise and temporal scaling | Rejects those perturbation ranges only; it was not physics-based synthesis. |
| HAR-Bench normalization | Per-window instance normalization in the representation pipeline | Training-fold global z-score and robust scaling | Different normalization question. Furthermore, the normalization comparison script repeatedly loaded RevalExo, so its external rows are descriptive only and cannot select a transform. |
| Hard-negative exposure | No single upstream method was claimed | Project-specific binary exposure plus separate pathology holdouts | Valid clinical trade-off experiment, but not a replication claim. |

## What remains trustworthy

- Participant-disjoint and complete-source-held-out results from notebook 29.
- The exact HAROOD mean-plus-covariance CORAL objective at the tested weight.
- The accepted ensemble as a local empirical model.
- Failures of the specific small DDPM, hand-set augmentation, reduced MiniROCKET/logistic fusion, and participant-bag MIL configurations.
- The conclusion that current external evidence is too small for clinical claims.

## Claims that must be corrected

- The compact CNN must not be called a reproduction of InceptionTime.
- The `ERM++-style` member must not be shortened to full ERM++.
- The source×class GroupDRO result must not be used to reject source-domain GroupDRO.
- The 2,000-feature MiniROCKET variants must not be used to reject canonical MiniROCKET.
- The local time-domain DDPMs must not be described as IMUDiffusion implementations.
- RevalExo rows from the normalization-variant script must not influence model or transform selection.

## One corrective benchmark—not another rotation

The only justified next modeling action is one locked benchmark with three arms:

1. the incumbent compact lower-back ensemble, unchanged;
2. canonical-mechanics lower-back InceptionTime: six modules, residual every three modules, 40/20/10 kernels, 32 filters, ReLU, and a five-model ensemble;
3. canonical lower-back MiniROCKET: 10,000 features, maximum 32 dilations, `StandardScaler(with_mean=False)`, and `RidgeClassifierCV(alphas=10^-3…10^3)`.

All arms must use the notebook-29 data contract: three complete source holdouts, participant-safe inner validation, five predeclared seeds, training-fold-only preprocessing, participant-level aggregation, and no RevalExo/NONAN access. Ridge probability calibration, needed for Brier score, must use only inner-training participants and must be reported separately from its canonical decision-score classification.

The gate remains clinical rather than accuracy-only: both mean FP and mean FN must not increase; worst-source balanced accuracy, sensitivity, specificity, AUROC and Brier must remain non-inferior; and total errors must fall materially. If neither canonical arm passes, architecture rotation stops and the project proceeds to new paired-cohort evaluation.

## Primary sources and official code

- [InceptionTime paper](https://arxiv.org/abs/1909.04939) and [official implementation](https://github.com/hfawaz/InceptionTime)
- [MiniROCKET official implementation](https://github.com/angus924/minirocket)
- [HAROOD official benchmark](https://github.com/AIFrontierLab/HAROOD)
- [ERM++ paper](https://openaccess.thecvf.com/content/WACV2025/papers/Teterwak_ERM_An_Improved_Baseline_for_Domain_Generalization_WACV_2025_paper.pdf) and [official implementation](https://github.com/piotr-teterwak/erm_plusplus)
- [Attention-based Deep MIL official implementation](https://github.com/AMLab-Amsterdam/AttentionDeepMIL)
- [GroupDRO paper](https://arxiv.org/abs/1911.08731) and [official implementation](https://github.com/kohpangwei/group_DRO)
- [IMUDiffusion primary paper](https://www.nature.com/articles/s41598-025-01614-x)
- [IMUEval official implementation](https://github.com/H-IAAC/synth-imu-eval)
- [HAR-Bench official implementation](https://github.com/saiketa/HAR-Bench)

## Evidence files

- `../notebooks/33_prior_method_code_alignment_audit.ipynb`
- `../data/processed/prior_method_code_alignment_audit.csv`
- `../data/processed/prior_method_code_alignment_decision.json`
- `../data/processed/prior_method_upstream_commits.csv`

