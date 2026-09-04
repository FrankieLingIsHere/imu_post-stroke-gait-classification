# Post-Stroke Gait Classification: Development Plan

## Overall flow

The project follows one decision sequence:

1. Understand and clean the current data.
2. Check whether the groups and signals are comparable.
3. Establish how well simple gait features already perform.
4. Train the CNN on the same inputs and splits.
5. Compare the CNN with the simpler methods.
6. Recruit more data if the result is weak, unstable or confounded.

Step 0 sets the rules for that later comparison. The first hands-on activity is
Step 2: auditing and freezing the data.

## What has already been completed in the notebook

The notebook is not an empty starting point. It already contains a seven-dataset exploratory analysis with feature extraction, placement comparisons, demographic checks and cross-dataset feature validation. The original EDA notebook did not train a classifier; the later modeling notebooks now provide the first reproducible baselines and CNN pilot.

### Current notebook analysis

1. Voisard feature extraction

- 488 healthy/CVA trials were processed.
- These came from 122 participants: 73 healthy and 49 CVA participants.
- Features were extracted from gait-event annotations and walking-only signal sections.
- Extracted features include cadence, mean stride time, stride-time variability, lower-back RMS, head RMS and bilateral foot RMS.
- Additional features include sample entropy, harmonic ratio and Poincare SD1.

2. Voisard demographic and confound analysis

- The healthy and CVA groups were not age matched. Mean age was approximately 39.7 years for healthy participants and 59.0 years for CVA participants.
- Participant-level age adjustment was performed rather than treating repeated trials as independent observations.
- After adjustment, foot RMS showed the strongest participant-level effect (rank-biserial r = 0.719), followed by lower-back RMS (r = 0.566), cadence (r = 0.419), mean stride time (r = -0.418) and head RMS (r = 0.305).
- Stride-time variability was weaker and did not pass the participant-level bootstrap significance test.

3. Felius replication analysis

- 377 complete three-sensor trials were processed from 166 participants: 132 stroke and 34 healthy participants.
- The signal-based stride-period detector failed on 56 trials, with failures concentrated in the stroke group.
- Participant-level placement analysis again found foot RMS stronger than lower-back RMS. The current executed table gives foot RMS r = 0.792 and lower-back RMS r = 0.611.
- Cadence, mean stride time and stride-time variability also showed strong within-dataset group differences, but their extraction method differs from Voisard’s event-based method.

4. Placement analysis across healthy datasets

- DUO-GAIT and Camargo showed the highest raw acceleration magnitude at the feet and the lowest, more stable magnitude at trunk/head placements.
- MAREA showed close agreement between waist and ankle timing, while wrist timing was noisier.
- These findings support testing both distal foot signals and lower-back signals in the raw-signal model rather than assuming one placement is best.

5. Cross-dataset feature validation

- Five healthy reference datasets contributed 335 trials from 107 participants.
- The pooled real stroke group contained 181 participants from Voisard and Felius after participant-level aggregation and duplicate handling.
- In the current executed pooled comparison, lower-back RMS, cadence and mean stride time separated the pooled groups with large effects: lower-back RMS r = 0.904, cadence r = 0.569 and mean stride time r = -0.558.
- Stride-time variability and sample entropy were not stable in the pooled comparison and need cautious interpretation because the healthy datasets use different protocols and estimators.
- A later foot-RMS analysis gave r = 0.848 when four healthy reference sources were pooled and r = 0.810 using only genuine-foot sources.

6. Simulated pathology analysis

- GaitMotion was summarized separately because its stroke condition was performed by healthy volunteers simulating stroke gait.
- It was not treated as clinical stroke evidence and was not pooled with the real Voisard/Felius stroke participants.

7. First modeling and generalization audit

- The validated common tensor contains 18,511 participant-linked 5-second windows with 18 synchronized channels.
- A participant-balanced, fold-normalized 1D CNN using the orientation-robust three-channel acceleration-magnitude representation reached mean five-fold AUROC = 0.964, balanced accuracy = 0.881 and F1 = 0.879.
- Cross-dataset CNN performance was asymmetric: Voisard-to-Felius AUROC = 0.879, while Felius-to-Voisard AUROC = 0.509.
- A simpler three-channel harmonized feature representation reduced that asymmetry: Voisard-to-Felius AUROC = 0.863 and Felius-to-Voisard AUROC = 0.826.
- The source-shift audit found large same-label distribution differences, especially in foot-signal variability. This means the CNN pilot is suitable for a research benchmark, but its within-dataset score is not evidence of clinical generalization.

### What these results mean for the next phase

The analysis has identified plausible raw-signal inputs, reproduced several features across two real stroke datasets, and completed a first CNN pilot. It has not shown reliable generalization across devices and protocols. The next phase must therefore reconcile the available public data and test whether any additional data improves performance on genuinely unseen participants rather than simply increasing the number of correlated windows.

The numerical values above are taken from the latest executed notebook cells. Some explanatory markdown cells contain older historical values, so the notebook should be re-run from a clean kernel before the modeling manifest is frozen.

## 0. Set the decision framework before analyzing data

Before cleaning the signals or training any model, we need to decide what a
successful first experiment would look like. The current datasets can produce
many sensor windows, but the independent evidence is still only a few hundred
participants. This means that two models may appear different because of
sampling variation, not because one has genuinely learned a better gait
pattern.

This step does not compare models yet. It defines the rules that will be used
later to compare the simple baselines with the CNN. It also separates a useful
research pilot from a result that would justify collecting more data or
starting external clinical validation.

0.1 Define model comparison using the participant-level bootstrap confidence
interval for the difference in AUROC. Treat two models as practically
equivalent only when the full confidence interval lies within a pre-specified
margin, such as ±0.03 AUROC. Confidence-interval overlap alone is not an
equivalence test.

0.2 Define the pilot success criteria before seeing the results. For example:

- AUROC reaches at least 0.75 in both Voisard-to-Felius and Felius-to-Voisard
  tests;
- sensitivity and specificity are each at least 0.65;
- performance is not explained entirely by age, sex or gait speed;
- the CNN provides a meaningful improvement over the demographic-only and
  engineered-feature baselines.

These values are initial decision thresholds, not clinical claims. A formal
power analysis and external validation are still required before deployment.

0.3 Define what result would stop or pause the project. Examples include:

- cross-dataset AUROC close to chance;
- performance that disappears after source or demographic adjustment;
- a CNN that performs no better than a much simpler baseline;
- unstable results across random seeds or participant splits.

0.4 Define primary and exploratory subgroup analyses before modeling. Dataset
and stroke side can be primary when sufficiently powered. Age, sex,
sensor-configuration intersections and cells with fewer than approximately 15
participants should remain exploratory.

## 1. Define the classification task

1.1 Define the target as binary classification:

- 0: healthy gait
- 1: gait from a person with stroke

1.2 Define the prediction unit as the participant, not the individual sensor window.

1.3 Define the intended use before modeling:

- research classification only during the first stage;
- no clinical diagnosis or deployment claim until external validation is complete.

1.4 Predefine the primary metrics:

- AUROC;
- AUPRC;
- sensitivity and specificity;
- balanced accuracy;
- F1 score;
- calibration and confidence intervals.

## 2. Audit and freeze the current data

2.1 Use the current real labeled data first:

- Voisard: 49 stroke and 73 healthy participants;
- Felius: 132 stroke and 34 healthy participants.

The full Voisard release is already stored locally and also contains CIPN,
PD, RIL, ACL, HOA and KOA cohorts. These cohorts are excluded from the
primary binary label definition rather than being treated as additional
stroke cases.

2.2 Treat the effective labeled sample as 288 participants. Do not count overlapping windows or repeated trials as independent participants.

2.3 Exclude or flag:

- incomplete sensor triplets;
- corrupted files;
- trials without enough walking data;
- trials with failed signal-quality checks;
- duplicate participant IDs;
- repeated visits that could leak information between training and testing.

2.4 Re-run the EDA notebook from a clean kernel and export one verified table containing participant ID, trial ID, dataset, label, sensor configuration, sampling rate, walking duration and quality flags.

2.5 Freeze this table as the first modeling manifest. Do not change labels or remove failed trials after seeing model results without recording the reason.

## 3. Standardize the signal inputs

3.1 Start with the sensor configuration shared by Voisard and Felius:

- lower-back IMU;
- left-foot IMU;
- right-foot IMU.

3.2 Use accelerometer and gyroscope channels where they are available in both datasets. Keep signal magnitude as an additional orientation-robust channel.

3.3 Convert all signals to common units:

- acceleration in g;
- gyroscope in degrees per second;
- sampling rate resampled to 100 Hz.

3.4 Remove non-walking sections using gait events where available. For datasets without gait events, use a documented walking-activity detector.

3.5 Apply only training-fold normalization. Do not calculate normalization statistics from the complete dataset.

3.6 Segment walking data into fixed windows:

- selected window: 5 seconds, based on the executed window-length audit;
- overlap: 50% during training only;
- no overlap between evaluation windows;
- aggregate all windows back to one participant-level prediction.

## 4. Create data splits before generating windows

4.1 Split by participant, never by window or trial.

4.2 Use nested subject-grouped cross-validation for model selection.

4.3 Reserve the following tests:

- Voisard-only internal test;
- Felius-only internal test;
- train on Voisard and test on Felius;
- train on Felius and test on Voisard.

4.4 Keep every participant’s trials and visits in the same split.

4.5 Report results separately by dataset, age group, sex, sensor configuration and stroke-side metadata where available.

## 5. Establish non-deep-learning baselines

5.1 Train a feature-based baseline using the EDA features:

- foot acceleration RMS;
- lower-back acceleration RMS;
- cadence;
- mean stride time;
- stride-time variability;
- selected nonlinear features as secondary candidates.

5.2 Compare:

- logistic regression;
- linear SVM;
- random forest;
- MiniROCKET with a linear classifier.

5.3 Use these baselines to determine whether a deep model learns useful raw gait patterns or only reproduces simple engineered-feature differences.

## 6. Train the first deep-learning model

6.1 Use PyTorch.

6.2 The first pilot should remain a small multivariate 1D CNN rather than a large architecture. The executed pilot used acceleration magnitude from the lower-back, left-foot and right-foot sensors, followed by compact convolutional blocks, normalization, pooling, global average pooling and dropout.

6.3 Initial architecture proposal (the executed pilot uses 5-second windows; the older 1,000-sample specification below must be updated before the next run):

- input shape: channels × 1,000 samples;
- 2–3 multi-scale convolution blocks;
- kernel sizes covering short, medium and approximately one gait-cycle patterns;
- 16–32 filters per block;
- residual connections;
- batch normalization and dropout;
- global average pooling;
- one sigmoid output for stroke probability.

6.4 Use class-weighted binary cross-entropy. Do not duplicate windows from the minority class without preserving participant-level weighting.

6.5 Use early stopping, a fixed validation protocol and multiple random seeds.

6.6 Aggregate window probabilities using the participant-level mean and median. Select the aggregation rule using validation data only.

6.7 The next architecture comparison should include the current compact CNN, an InceptionTime-style multi-scale CNN and MiniROCKET. The comparison must use the same participant splits, fold-specific normalization and external cross-dataset tests.

6.8 The first GPU-backed internal comparison is complete in [14_architecture_comparison.ipynb](notebooks/14_architecture_comparison.ipynb). Across five participant folds, MiniROCKET plus ridge reached mean AUROC = 0.972, balanced accuracy = 0.936 and F1 = 0.956. The compact CNN retrained on GPU reached AUROC = 0.973, balanced accuracy = 0.857 and F1 = 0.845. The small InceptionTime-style CNN reached AUROC = 0.962, balanced accuracy = 0.873 and F1 = 0.879. These are internal results only; MiniROCKET is the current candidate, not the final model.

6.9 The next model gate is cross-dataset evaluation of MiniROCKET and the InceptionTime-style CNN in both directions, using the existing Voisard-to-Felius and Felius-to-Voisard protocols. The model with the best internal score must not be selected if its external direction is unstable or near chance.

6.10 The cross-dataset gate is complete in [15_cross_dataset_architecture_validation.ipynb](notebooks/15_cross_dataset_architecture_validation.ipynb). The Inception-style CNN was the strongest external candidate: Voisard-to-Felius AUROC = 0.876 and Felius-to-Voisard AUROC = 0.790. The compact CNN reached 0.878 and 0.533, while MiniROCKET reached 0.673 and 0.579. Therefore, Inception is the current deep-learning candidate and MiniROCKET remains the non-deep-learning benchmark. This is still a fold-0 architecture gate, not final evidence; seed stability, calibration and an independent external cohort remain required.

6.11 The combined-versus-separate experiment is complete in [16_combined_vs_separate_stability.ipynb](notebooks/16_combined_vs_separate_stability.ipynb). A pooled Inception model was trained on the Voisard and Felius participants together, with participant-level five-fold validation, fold-specific normalization and source-specific reporting. The pooled model reached AUROC = 0.916 and balanced accuracy = 0.830 on Felius participants, and AUROC = 0.976 and balanced accuracy = 0.830 on Voisard participants. The corresponding separate-source cross-dataset results were AUROC = 0.876 / 0.790 and balanced accuracy = 0.711 / 0.737 for Felius / Voisard. These results favor a pooled model as the current training strategy, but they are not a strict apples-to-apples replacement for the leave-one-dataset-out test: pooled validation measures multi-source development performance, while the separate-source test measures transfer to an unseen dataset.

6.12 The pooled model showed seed sensitivity that still needs to be controlled: on the same fold, five seeds produced AUROC from 0.927 to 0.942 and balanced accuracy from 0.772 to 0.845. Calibration is not yet acceptable as a final clinical probability estimate: pooled Brier score = 0.120 and ECE-10 = 0.182, with worse calibration on Felius (Brier = 0.136, ECE-10 = 0.211) than Voisard (Brier = 0.099, ECE-10 = 0.142). The next model step is therefore source-balanced pooled training with repeated seeds, validation-only threshold/calibration fitting, and source-specific calibration reports. The final model must still be tested on a genuinely untouched external cohort.

6.13 The pooling strategy was then tested more rigorously in [08_robust_pooled_training.ipynb](../notebooks/08_robust_pooled_training.ipynb). Four contracts were compared on identical participant folds: naive pooled training, source/class-balanced pooled training with global fold normalization, source/class-balanced training with separate source normalization, and source/class-balanced per-window shape normalization. The source/class-balanced global-normalization strategy was best by the weaker-source AUROC: Felius AUROC = 0.930 and Voisard AUROC = 0.982, compared with 0.916 and 0.976 for naive pooling. Its source-specific balanced accuracy was 0.842 and 0.924. Separate source normalization reduced Felius AUROC to 0.911, while per-window shape normalization reduced both sources to 0.916 and 0.953. Therefore, the current pooled contract is not blind concatenation: use both datasets, keep fold-fitted global normalization, weight each source-by-label participant cell equally, and report every source separately.

6.14 The selected balanced pooled strategy also improved calibration relative to the initial pooled baseline: pooled Brier score = 0.091 and ECE-10 = 0.113, versus 0.120 and 0.182 previously. Five seeds on the same validation fold produced AUROC from 0.918 to 0.931 and balanced accuracy from 0.794 to 0.859. This is encouraging but not a final stability claim because the seed test uses one fold. Repeat the selected strategy across all folds and fit thresholds/calibration only within training folds before external evaluation.

6.15 Repeated outer validation is complete in [09_repeated_pooled_validation_calibration.ipynb](../notebooks/09_repeated_pooled_validation_calibration.ipynb). Across five participant folds and three seeds, raw and calibrated pooled AUROC were identical because calibration preserves ranking: mean AUROC = 0.944 overall, 0.920 on Felius and 0.973 on Voisard. The raw balanced accuracy means were 0.857 overall, 0.826 on Felius and 0.890 on Voisard. Inner-fold calibration reduced the mean pooled Brier score from 0.102 to 0.091 and ECE-10 from 0.141 to 0.112, although Felius remained less well calibrated than Voisard. The validation-derived thresholds ranged from 0.339 to 0.859 across the 15 outer runs. This threshold instability means that no single clinical operating threshold should be fixed yet; threshold selection must wait for a larger independent validation cohort and a predefined clinical cost function.

6.16 The project will now maintain two parallel prediction directions rather than forcing age into the stroke decision as a first-stage gate. The primary gait model remains a pooled healthy-versus-CVA classifier. A secondary age-from-gait model will estimate age-related gait structure, initially using only age-labeled healthy Voisard participants so that it learns normative aging rather than simply learning the stroke/age confounding pattern. The current manifest contains age for all 122 Voisard participants but no age for any of the 166 Felius participants. In the Voisard cohort, provisional bins of 18--39, 40--59 and 60+ contain 43, 15 and 15 healthy participants respectively; across all Voisard participants the bins contain 43, 42 and 37, but the youngest bin has no stroke participants. Therefore, age-group classification is exploratory and class-imbalanced; continuous age regression should be the primary age endpoint, with three-class age classification as a secondary analysis. The supplied review identifies the same issue: Voisard healthy participants averaged 39.7 years versus 59.0 for CVA, age correlated strongly with several signal features, and most feature effects remained after participant-level age adjustment. It therefore supports age auditing and age-stratified reporting, not automatic use of age as a stroke predictor.

6.17 Do not cascade the age classifier into the gait classifier until three checks pass: (1) the gait model is evaluated within feasible age-overlap strata; (2) its performance is compared with and without age adjustment; and (3) an age-complete, age-matched external cohort confirms that the stroke signal is not an age shortcut. A later multi-task model with a shared encoder, stroke head and age head may be tested only after age metadata are collected for both sources; missing-age masking on Felius would otherwise make the shared representation source-dependent. The age model is therefore a parallel explanatory and robustness direction first, and an input feature or staged gate only if those checks justify it.

6.18 The first age-classification feasibility test is complete in [10_age_classifier_feasibility.ipynb](../notebooks/10_age_classifier_feasibility.ipynb). Using healthy Voisard participants only and the provisional 18--39 / 40--59 / 60+ groups, the Inception-style age classifier achieved mean participant-level AUROC = 0.726, balanced accuracy = 0.451 and macro-F1 = 0.342 across five folds and three seeds. The standard deviations were 0.110, 0.097 and 0.105 respectively. This is evidence that the direction is worth studying, but it is not strong or stable enough to use as a staged gate or as an input to the stroke model. This motivated the interaction audit in item 6.19. The remaining age tasks are continuous age regression and age-matched external validation before attempting a multi-task or cascaded model.

6.19 The age-by-stroke interaction and age-overlap audit is complete in [20_age_group_interaction_analysis.ipynb](notebooks/20_age_group_interaction_analysis.ipynb). At participant level in Voisard, head RMS and lower-back RMS showed nominal interaction p-values of 0.039 and 0.049, but their Benjamini--Hochberg adjusted q-values were both 0.148 across the six tested features. Foot RMS, cadence, mean stride time and stride-time variability did not show a reliable group-specific age slope. Therefore age may modify some signal-feature relationships, but the present sample does not establish a stable, general age-dependent stroke signature. The youngest band contains 43 healthy participants and no CVA participants, so only the 40--59 and 60+ bands support within-age stroke-versus-healthy performance checks. In the repeated pooled gait model, raw AUROC averaged 0.953 in the middle band and 0.913 in the older band, with raw balanced accuracy of 0.891 and 0.816 respectively. These are small, fold-level strata rather than independent validation cohorts, so they support reporting and recruitment design, not a claim of equal clinical performance across age. Keep age as a parallel secondary endpoint, do not use it as a cascade gate, and prioritize continuous age regression plus an age-complete, age-matched external cohort.
6.20 Continuous age regression is complete in [21_continuous_age_regression.ipynb](notebooks/21_continuous_age_regression.ipynb). The full local Voisard release has 259 valid-age participants from 18 to 90 years across healthy, neurological and orthopedic cohorts, but the primary healthy/CVA subset has only 72 healthy participants with usable windows and no CVA participant below age 41. Across 15 repeated participant-level runs on healthy Voisard, engineered-feature Ridge achieved mean MAE = 12.86 years, RMSE = 15.46 years, R² = 0.310 and Spearman rho = 0.643. The GPU Inception-style regressor achieved MAE = 13.42 years, RMSE = 16.48 years, R² = 0.243 and Spearman rho = 0.580. The simpler baseline therefore outperforms the current deep age model. Treat age prediction as descriptive and exploratory, then prioritize age-balanced, age-complete external recruitment rather than a larger age network.

6.21 The age-adjusted stroke baseline is complete in [22_age_adjusted_gait_baseline.ipynb](notebooks/22_age_adjusted_gait_baseline.ipynb). Across 15 repeated participant-level runs on Voisard, raw gait features achieved mean AUROC = 0.973 and balanced accuracy = 0.921. Adding age achieved AUROC = 0.968 and balanced accuracy = 0.923, so age did not improve discrimination. Age alone achieved AUROC = 0.803, showing that it is a strong shortcut in this age-imbalanced subset. Fold-fitted age-residualized gait achieved AUROC = 0.882 and balanced accuracy = 0.786, so simple residualization removed useful signal for the current task. This does not prove age is irrelevant, but it supports keeping age out of the primary model until age-matched external validation is available.

## 7. Add self-supervised learning only after the baseline works

7.1 Pretrain the CNN encoder on unlabeled walking windows.

7.2 Compare supervised training from scratch against:

- TS2Vec-style hierarchical contrastive pretraining;
- SimCLR-style temporal contrastive pretraining.

7.3 Use physiologically plausible augmentations:

- low-amplitude noise;
- amplitude scaling;
- short time masking;
- limited time warping;
- sensor-channel dropout;
- small orientation perturbation where valid.

7.4 Do not use generated stroke signals as real stroke labels.

## 8. Decide whether additional data are required

8.1 The current data is enough for a research pilot and architecture comparison.

8.2 The current data is not enough for a strong clinical generalization claim because of:

- only two real stroke datasets;
- different hardware and protocols;
- Voisard’s age imbalance;
- incomplete demographic metadata in Felius;
- different gait-event extraction methods;
- repeated trials from the same participants.

8.3 Recruit a new independent cohort before deployment claims:

- preferred target: 50–100 stroke participants;
- preferred control group: 50–100 age- and sex-matched healthy participants;
- collection from a different site or device if possible.

8.4 Collect at minimum:

- raw synchronized IMU signals;
- lower-back and bilateral-foot placement;
- sampling rate and sensor model;
- age, sex, height and weight;
- paretic side;
- stroke chronicity;
- lower-extremity severity score;
- walking aid and gait speed;
- multiple walking bouts per participant.

8.5 Perform a formal power analysis after the first pilot estimates effect size, variance, class balance and expected external-test performance.

8.6 Public data-source investigation has now been performed before any large download. The complete Voisard release is already present in the workspace at `data/raw/voisard_2025/data`; no new archive download is required. It contains 1,356 trial metadata files from all 260 participants, with 360 healthy trials, 128 CVA trials, 98 CIPN trials, 160 PD trials, 398 RIL trials, 60 ACL trials, 74 HOA trials and 78 KOA trials. The participant folders contain 73 healthy, 49 CVA, 19 CIPN, 24 PD, 51 RIL, 11 ACL, 15 HOA and 18 KOA participants. The current modeling manifest intentionally uses only the healthy and CVA cohorts, which explains its 488-trial scope. The release structure and cohort definitions are documented in the [Voisard dataset paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC12546693/) and [official loader repository](https://github.com/CyrilVoisard/dataset_gait_1).

8.7 The next Voisard action is therefore a local metadata audit, not a download. That audit has now verified all 1,356 trials and all eight cohorts: every trial has the expected seven files (four raw sensor files, one processed file, one metadata file and one plot), with zero incomplete trials. The cohort decision is recorded in `data/interim/voisard_full_cohort_audit.csv`. The remaining comparison is label/manifest scope: decide whether the additional neurological and orthopedic cohorts should be used as a secondary multiclass or hard-negative experiment. They must not be relabeled as stroke. For the primary binary task, the local Voisard data already provides the relevant healthy/CVA participants; external recruitment is still needed for independent protocol diversity rather than for simply adding more Voisard windows.

8.8 The Chapman stroke/healthy dataset has now been checked as a secondary external-validation candidate, not a direct training merge. The accompanying study reports 14 stroke and 14 healthy adults, three consecutive days of passive naturalistic data, and one L5/S1 wearable IMU. The paper specifies a 100 Hz tri-axial accelerometer and tri-axial gyroscope, with approximately 25.92 million samples per channel over three days. The official page lists large raw OMX/H5 downloads and a CC BY 4.0 license. This is useful for an external low-back activity stress test, but it is not a direct test of the current three-IMU gait model because it lacks bilateral foot sensors and uses naturalistic ADL rather than labeled walking trials. The raw download/code package was not retrievable through the automated source check, so participant-file mapping, exact H5/OMX schema and walking-segment availability remain unconfirmed. Do not download the multi-gigabyte release until those fields can be inspected manually or through an accessible mirror. Sources: [Chapman data page](https://digitalcommons.chapman.edu/pt_data/3/), [accompanying study](https://digitalcommons.chapman.edu/pt_articles/166/) and [full article](https://www.mdpi.com/1424-8220/22/2/598).

8.9 The Zenodo stroke rehabilitation dataset contains raw accelerometer/gyroscope signals and clinical metadata from 10 stroke participants, but no healthy controls. It can be considered later for stroke-only self-supervised pretraining or robustness analysis, not for class balancing. The [Zenodo release](https://zenodo.org/records/10534055) must remain a separate source.

8.10 Other sources are auxiliary rather than direct solutions: Warmerdam includes neurological patients and healthy participants but restricts most patient data; REHAB contains 120 post-stroke patients but focuses on rehabilitation movements with a different sensor layout; the full-body stroke gait reference dataset uses motion capture, force plates and EMG rather than IMUs. These sources should not be merged into the raw IMU classifier without a separate research question.

8.11 No synthetic data should be introduced before the real-data reconciliation, a stable cross-dataset benchmark and an independent external test. Synthetic windows cannot increase the number of independent participants and may hide the source shift already observed.

8.12 Additional public stroke datasets were screened but do not replace the direct-match requirement. The [MUSC/ICPSR resource](https://www.icpsr.umich.edu/web/ICPSR/studies/37122/publications) has 27 post-stroke and 17 healthy participants with kinematic, kinetic, EMG and over-ground spatiotemporal measures, but it is not a raw three-IMU dataset and access includes restricted-data procedures. [STRIDE](https://digitalcommons.chapman.edu/pt_data/4/) is useful for heterogeneous post-stroke gait reference and power calculations, but it is also based on clinical gait-analysis measures rather than the current raw IMU configuration. These should remain auxiliary evidence, not be merged into the CNN tensor.

8.13 The frozen CNN was then evaluated on the six non-CVA Voisard cohorts in [13_non_cva_specificity_validation.ipynb](notebooks/13_non_cva_specificity_validation.ipynb). Mean participant-level stroke probabilities were low for ACL (0.220), HOA (0.226) and KOA (0.227), but higher for CIPN (0.441), PD (0.449) and RIL (0.502). At the inherited 0.5 stress-test threshold, 50.0% of PD participants and 56.9% of RIL participants were classified as stroke, compared with 42.1% of CIPN participants. This does not invalidate the binary pilot, but it shows that the model may be detecting neurological gait impairment rather than a stroke-specific signature. The primary claim must remain “healthy versus CVA within the studied data” until a matched non-stroke neurological control group and an independent clinical cohort are evaluated.

8.14 The external-validation audit found one newly relevant public candidate, RevalExo. Its README reports 10 stroke and 7 healthy participants with lower-body IMUs, pelvis and bilateral lower-limb sensors, 60 Hz sampling and annotated 12-second clips. Its cohort mean ages are 74.9 years for healthy controls and 57.6 years for stroke, with cohort-level rather than complete participant-level age/sex metadata. It is close enough for a frozen pelvis-plus-bilateral-foot protocol stress test after documented resampling, but it is too small and age-imbalanced for age-stratified validation. Do not merge it into training. The archive is split across multi-gigabyte packages, so inspect the trimmed schema and licensing first. The [external-validation-cohort wiki page](wiki/concepts/external-validation-cohort.md) records this decision. The official sources are the [KU Leuven dataset record](https://rdr.kuleuven.be/dataset.xhtml%3Bjsessionid%3Db3e07bde91bb2da987d0b857ee38?fileSortField=&fileSortOrder=&fileTag=&fileTypeGroupFacet=&folderPresort=true&persistentId=doi%3A10.48804%2FOWJOID&q=&tagPresort=false&version=) and [README file](https://rdr.kuleuven.be/file.xhtml?fileId=302387&toolType=PREVIEW&version=1.0).

## 9. Use the other datasets correctly

9.1 Use DUO-GAIT, OxWalk, MAREA and Camargo for healthy-domain robustness, placement analysis and unsupervised pretraining.

9.2 Do not merge their healthy labels directly into the main supervised dataset without recording device, protocol and population differences.

9.3 Use GaitMotion only for a separate simulated-pathology experiment or explicit pretraining ablation.

9.4 Do not use GANs, diffusion models or synthetic stroke generation before testing the real-data baseline. Synthetic data may be considered later only if it improves performance on an untouched real external cohort.

## 10. Validate and select the final model

10.1 Select the model using participant-level validation metrics, not window-level accuracy.

10.2 Use pooled Voisard+Felius training as the current default, but require consistent performance across both source-specific validation reports and a genuinely untouched external cohort. Keep leave-one-dataset-out results as a transfer stress test rather than treating them as interchangeable with pooled cross-validation.

10.3 Check calibration and decision thresholds separately from discrimination.

10.4 Use explainability methods such as integrated gradients or occlusion tests to identify which sensors and time regions drive predictions.

10.5 Compare the deep model against the engineered-feature and MiniROCKET baselines. Prefer the simpler model if performance is equivalent.

10.6 Treat age prediction as a parallel secondary endpoint. Report the gait model within age-overlap strata and with age-adjusted feature baselines; do not treat a successful age model as evidence that age should be fed into the stroke classifier.

## 11. Recommended implementation order

1. Audit the complete local Voisard release and compare it against the current 488-trial HS/CVA manifest.
2. Freeze the verified participant/trial/window manifest and document the excluded non-CVA cohorts.
3. Build the common 3-sensor preprocessing pipeline and retain the 5-second window decision.
4. Re-run the feature-based baselines and compact CNN from a clean kernel with fixed participant splits.
5. Completed internal GPU comparison of compact CNN, InceptionTime-style CNN and MiniROCKET; continue with cross-dataset evaluation.
6. Completed: run the non-CVA Voisard specificity stress test and check whether the model is neurological-general rather than stroke-specific.
7. Completed: run cross-dataset architecture validation; use Inception as the current deep-learning candidate and MiniROCKET as the benchmark.
8. Completed robust pooled training and repeated outer validation: use source/class-balanced global-normalization pooling as the current development contract, with calibration reported but no frozen clinical threshold.
9. Completed the age-classifier feasibility direction, age-overlap interaction audit, continuous age-regression comparison and age-adjusted versus unadjusted gait baseline without feeding age into the primary model. Next recruit an age-complete age-matched external cohort and compare the primary model on matched strata.
10. Inspect the RevalExo trimmed schema for a deliberately external pelvis-plus-foot stress test, keep Chapman as a low-back-only activity stress test, then recruit and evaluate an independent age-complete age- and sex-matched cohort.
11. Add self-supervised pretraining only after the real-data benchmark is stable.
12. Decide whether the model is ready for further clinical validation.
