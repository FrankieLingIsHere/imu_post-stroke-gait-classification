# Online-only data expansion strategy

## Dataset roles

Public datasets should be assigned a role based on labels, sensor compatibility, and metadata completeness.

| Dataset | Public content | Best role | Main limitation |
|---|---|---|---|
| Voisard | Healthy, neurological, orthopedic wearable gait signals with metadata | Internal development and subgroup analysis | Existing primary source; age-label imbalance remains |
| Felius | Healthy and post-stroke, three IMUs, feet/lower back, approximately 104 Hz | Primary pooled development source | Age metadata is not available in the public release |
| RevalExo | Healthy older adults, stroke, and sarcopenia; lower-body Xsens IMU | Held-out external test | Different sensor system and limited participants; individual ages unavailable |
| Zenodo stroke rehabilitation IMU dataset | Raw accelerometer/gyroscope data from stroke rehabilitation participants, demographic and clinical information | Stroke-only representation pretraining or robustness analysis | Does not provide a matched healthy control group for direct binary pooling |
| Healthy-only IMU datasets | Age-stratified healthy gait signals | Healthy specificity and age-domain analysis | Cannot add stroke labels; sensor/task compatibility must be audited |
| NONAN GaitPrint (staged audit acquired) | 126 healthy adults across young, middle-aged, and older cohorts; real Noraxon IMUs at lower spine, pelvis, and both feet | Highest-priority healthy-domain candidate | Healthy only; 200-Hz Noraxon and 200-m self-paced protocol differ from the current development sources |
| Kuopio gait dataset (screened; not acquired) | 51 healthy adults; 100-Hz Xsens accelerometry at posterior pelvis/sacrum and both feet, with participant metadata | Independent healthy-domain replication candidate | Healthy only; short laboratory walkway and posterior-pelvis placement, not documented L5 |
| GAITEX (2026) | 19 healthy adults; 100-Hz treadmill gait, synchronized full-body markers, IMU orientations, and OpenSim models | Physics-grounded virtual-IMU synthesis source | Healthy only; released IMUs are orientation data, so it is neither a direct binary source nor an external test |
| Optical motion-capture datasets | Age-spanning healthy and stroke kinematics | External biological plausibility or feature-level comparison | Not directly compatible with the raw-IMU classifier input |

## Recommended sequence

1. Keep lower-back acceleration magnitude as the primary research contract after the multi-source gate in [[evidence-gated-model-improvement]]. Retain the established three-channel magnitude model as a comparator; do not reverse this decision using one-sided component audits.
2. Treat Zenodo (stroke-only) and Carpinella (healthy-only lower back) as separate frozen sensitivity and specificity checks. Never calculate a joint binary metric across them.
3. Retain Sint Maartenskliniek as the first paired external stroke--healthy gait IMU examination and separately labelled training-sensitivity source. Screen only for a **second independent** paired cohort with documented placement, units, sampling rate, and walking segmentation, to test multi-site transportability. A verified lower-back paired cohort directly supports the primary track; bilateral-foot channels are useful when available for the secondary comparator.
4. Before admitting any source to training, validate its data contract per source, then use participant-disjoint source-held-out evaluation with source-by-label balancing. Do not fabricate channels or relabel naturalistic activity as gait.
5. Keep RevalExo untouched for the primary external benchmark. Carpinella and Zenodo are also frozen for their respective component checks; they are not calibration, threshold-selection, or training data.
6. If no compatible paired source is found, record that evidence and prioritize a prospectively recruited paired cohort rather than synthetic enrichment or incompatible pooling.

## Online-data acceptance rule

A dataset may enter binary training only if it has participant-level healthy/stroke labels, raw or reconstructable acceleration signals, documented units and sampling rate, usable walking segmentation, and a sensor configuration that can be mapped without guessing. Otherwise it is assigned to pretraining, specificity testing, or context only.

## Current public-cohort screen (2026-09-02)

### First priority: NONAN GaitPrint healthy reference series

The screened **NONAN GaitPrint** series is the strongest available public
healthy-cohort candidate. Its three compatible releases use the same
self-paced 200-m indoor-track protocol and Noraxon full-body IMUs: 35 healthy
young adults (19--35 years), 50 healthy middle-aged adults (36--55 years), and
41 healthy older adults (56+ years). The sensor map includes a pelvis/sacrum
sensor and bilateral dorsal-foot sensors, and the raw trial tables retain
acceleration. It therefore offers 126 real, age-labelled healthy participants,
rather than synthetic windows or a mixture of unrelated study protocols.

This is a **pelvis/sacrum proxy, not a documented L5 sensor**. It must never be
silently renamed as the project LB/L5 channel. Its 200-Hz Noraxon acquisition,
long self-paced trials, and device coordinate convention also differ from the
current sources. The acquisition plan is therefore deliberately staged:

1. Acquire metadata and a small, age-stratified participant sample first; audit
   channel names, physical units, sampling interval, placement, walking-only
   content, and participant identifiers.
2. Lock a predeclared participant subset as a **healthy-only external
   specificity examination** before any adapter or training choice is fitted.
3. Only if the source contract passes and the frozen subset shows credible
   specificity may the remaining NONAN participants enter a separate
   source-balanced healthy-enrichment sensitivity experiment. RevalExo remains
   untouched throughout. This experiment cannot create a new paired external
   AUROC because NONAN supplies healthy labels only.

The raw full series is large (the middle-aged and older releases alone are
about 66.7 GB and 53.8 GB respectively), so it should be acquired with a
participant-level manifest rather than duplicated wholesale until the initial
contract audit succeeds. Sources: [young cohort](https://doi.org/10.6084/m9.figshare.c.6415061.v1),
[middle-aged cohort](https://doi.org/10.6084/m9.figshare.29371796), and
[older cohort](https://springernature.figshare.com/articles/dataset/NONAN_GaitPrint_An_IMU_gait_database_of_healthy_older_adults/27815034). The first staged
contract audit is complete: three median-age participants (S030, S048, S103)
covering ages 24, 45, and 63 passed archive checksums, have explicit raw
lower-spine/LT-foot/RT-foot mG acceleration at 200 Hz, and have no non-finite
target samples over 54 trials. An isolated 25.082-g left-foot peak requires a
documented local artifact policy, but is two samples in one trial rather than
source-wide corruption. See [[nonan-gaitprint]].

### Second priority: Kuopio healthy gait dataset

The [Kuopio dataset](https://zenodo.org/records/10559504) is a strong
independent confirmation source: 51 healthy participants, raw/extracted
100-Hz Xsens IMU data, posterior pelvis/sacrum plus bilateral feet, demographic
metadata, and slow/comfortable/fast walking trials. It is narrower in age than
NONAN (reported mean 29.7 +/- 7.9 years) and uses a controlled short laboratory
walkway, so it is second priority for healthy-domain replication rather than
the first cohort for closing the age gap.

### Paired-cohort result

This screen still found **no newly cleared public paired stroke--healthy gait
IMU cohort** meeting the project's raw LB/pelvis + bilateral-foot acceleration
contract. The public STS release does contain stroke and healthy Xsens data at
pelvis/L5 and feet, but it is sit-to-stand rather than walking, so it is not a
gait-classifier training or test source. The unmet requirement remains a second
paired gait cohort; healthy-only acquisitions can reduce false-positive risk
and improve age-domain auditing, but cannot independently establish stroke
sensitivity.

## Evaluation governance: Sint is not a final-model test set

Sint Maartenskliniek had two deliberately separate roles. Its 30-participant
frozen examination (20 healthy, 10 stroke) was valid for the earlier
Felius+Voisard model because no Sint sample had affected training,
normalisation, calibration, threshold choice, or architecture selection at that
point. After that result was recorded, a separate source-balanced
Felius+Voisard+Sint sensitivity-training model was fitted. Sint is therefore
**training data for the expanded prototype**, not an external test set for that
prototype. Re-scoring the expanded model on Sint would be resubstitution, not
external validation.

The expanded prototype's only paired untouched external examination is RevalExo
(17 participants: 7 healthy and 10 stroke). Its AUROC 0.914 is encouraging but
the cohort is too small to support a clinical-ready performance claim. The next
required evaluation asset is a second, participant-independent paired
stroke--healthy gait IMU cohort. It must remain completely isolated from all
training, preprocessing-statistic fitting, threshold choice, and model
selection.

The 2026-09-02 checkpoint reproduction restored the canonical RevalExo result:
AUROC 0.9143, Brier 0.1611, and BA 0.7143. At 0.50, stroke detection is 10/10
(Wilson 95% interval 72.2%–100.0%) but healthy specificity is only 3/7 (15.8%
–75.0%). A prior output file had been overwritten by an unnamed later probe;
the benchmark now records checkpoint provenance and supports an output prefix.
The confirmed artifact is `full_expanded_inception_prototype_seed_42.pt`.

The targeted public-cohort screen found no cleared second paired cohort. Kiel
publishes ten healthy participants only and offers patient records only by
request; Wang et al. report an 8-stroke/7-healthy cycle-level lower-limb data
set, but its historic download URL timed out and it does not document the
three-channel acceleration contract. See
`reports/EXTERNAL_VALIDATION_STATUS_AND_PUBLIC_RECRUITMENT_2026-09-02.md`.

### Physics-grounded synthesis screen (2026-09-02)

The existing direct healthy-window diffusion route is now rejected twice. Its
original native-window implementation failed repeated participant-disjoint
utility testing; a corrected multi-resolution DDPM with participant-held-out
MAREA/DUO-GAIT people also failed time-series fidelity gates (real-vs-synthetic
feature AUC 0.998 for MAREA and 0.981 for DUO-GAIT). It must not be added to
training or described as additional healthy participants.

The **GAITEX** full CC-BY release was acquired, checksum-verified, and
extracted on 2026-09-02. It has 19 independent healthy people, normal treadmill
gait at three speeds, synchronized 100-Hz full-body motion capture, nine IMUs,
and per-person OpenSim models. The release checksum (`cc69aa2b8d1317430012252e5a58d2b5`)
matches the publisher's value. The normal-gait audit retained 18 participants.
Seventeen fully clear the target pelvis/left-foot/right-foot rigid-cluster QC;
`gregers` has localized left-foot marker loss but retains at least one
uninterrupted five-second run in every normal-gait segment, so it is retained
for marker-complete window selection. Initial warnings for `austra` and
`elodie` were traced to an overly strict rule that misread a valid single zero
coordinate as a missing marker. One participant has no complete normal-gait
asset set.

GAITEX remains a *physics-grounded virtual-IMU synthesis* candidate only. Its
released IMU stream is orientation, not raw acceleration, and its recorded trunk
sensor is pelvis rather than the project's documented lower-back/L5 channel. It
cannot enter direct binary pooling, threshold selection, or frozen external
testing. The next gate is to define and validate an explicit virtual L5
attachment using its OpenSim/marker assets, then derive virtual tri-axial
accelerations for normal gait only. The proposed role is self-supervised
synthesis/pretraining first, never a shortcut to an enlarged independent
clinical cohort. Full method rationale and predeclared gates:
`reports/SYNTHESIS_REALISM_REVIEW_2026-09-01.md`.

The public Kiel preferred-walking subset was subsequently acquired and audited
instead of assumed usable. It has bilateral feet but a **pelvis** sensor, not a
documented lower-back placement; eight files are 200 Hz and two are 100 Hz.
It is therefore ineligible for direct LB/LF/RF inference or pooling. Do not
resample and score it merely because its sensor names are superficially close.
See [[kiel-validation-dataset]].

## Current priority

Sint Maartenskliniek already supplies the first publicly available paired,
external gait examination: 20 healthy and 10 stroke participants with
documented lower-back and bilateral-foot Xsens signals. Its pre-registered
frozen external Inception result was AUROC 0.915, Brier 0.097, and balanced
accuracy 0.850. Only after this result was frozen was it used in a separately
labelled source-balanced training sensitivity experiment; that expanded
prototype reached RevalExo AUROC 0.914. See
`reports/SINT_MAARTENS_PUBLIC_DATASET_DECISION.md` and
`reports/SINT_SENSITIVITY_TRAINING.md`.

Zenodo stroke rehabilitation and the Carpinella 6MWT healthy data provide
complementary but **separate** component audits. Frozen baseline evaluation
found 9/10 three-channel and 10/10 lower-back Zenodo stroke detections at 0.50,
while the lower-back baseline made 0/60 Carpinella healthy false-positive calls
at the same reference. Do not combine these cohorts into a single AUROC or
external binary benchmark: their devices and walking protocols differ. The
remaining data priority is a **second independent paired** stroke/healthy gait
IMU cohort, or a matched 3-channel healthy source for the three-channel
specificity track.

The acquired Terrier/Piergiovanni older-healthy lower-back/one-foot cohort was
also assessed as a frozen lower-back-only healthy check. It produced 53/59
false-positive calls at 0.50, but its lumbar magnitude distribution is far
outside the checkpoint's gravity-inclusive input contract (median 0.578 g
versus model mean 1.016 g). This is a representation-compatibility failure,
not valid evidence of age bias and not a candidate for guessed rescaling or
binary pooling. See [[triaxial-older-healthy]].

## Acquisition status (updated 2026-09-02)

The Zenodo stroke-rehabilitation release has been acquired, audited, and materialized under `data/archive/raw/zenodo_stroke_rehab/`; it remains a stroke-only component-audit/pretraining source rather than binary training data. The Carpinella 6MWT lower-back healthy cohort has likewise been acquired and audited under `data/archive/raw/carpinella_2026/`; it remains a frozen healthy-specificity source. Sint Maartenskliniek has been acquired, locked as the first paired external examination, and subsequently used only in its labelled training-sensitivity stream. No downloads are currently in progress. The outstanding data need is a **second independent paired external stroke--healthy gait IMU cohort**, not another unpaired release.

## Full-release audit (2026-08-24)

The complete release is now downloaded and extracted under `data/archive/raw/zenodo_stroke_rehab/extracted/`. It contains 10 stroke participants aged 37–88 years (median 79.5), participant demographics and clinical scores, raw/interim/processed data, and five sensor labels: `LF`, `RF`, `LW`, `RW`, and `SA`. The sample CSVs contain tri-axial acceleration and gyroscope fields and have a median sampling rate of approximately 120 Hz.

This is not a direct binary-training addition because it contains stroke participants only and does not expose a clearly labelled lower-back sensor equivalent to the current LB contract. Its immediate role is stroke-only representation pretraining, robustness testing, and age/rehabilitation analysis. Any use for adaptation must preserve participant-level separation from the final RevalExo test.

The current sensor audit is implemented in `scripts/audit_zenodo_stroke_rehab.py` and writes `data/processed/zenodo_stroke_rehab_file_audit.csv`. The bilateral feet are `LF` and `RF`, and the lower-back signal is `SA`: the raw files are named `SA.csv` but carry the device tag `ST-3`. This explains the apparent `SA`/`ST` conflict: `ST` appears in some interim-derived outputs, but is not the consistently available raw sensor file. We therefore use `SA` as the lower-back source only after recording this alias explicitly; wrist channels remain excluded.

The Zenodo stroke dataset is now technically usable for a stroke-only adapter/pretraining stream: 10 participants, bilateral feet plus lower back, approximately 120 Hz, and participant ages 37–88. It is still not a direct binary-training source because it has no matched healthy controls. The next implementation step is to materialize quality-controlled, participant-separated stroke windows from `LF`, `RF`, and `SA`, then compare representation pretraining against the existing pooled model without changing the frozen RevalExo test.

## Materialization audit (2026-08-24)

The first adapter materialization produced 1,465 five-second windows of shape `(500, 18)` from all 10 participants. Windows are created only from visits containing all three required channels and are grouped by participant in `data/processed/zenodo_stroke_window_metadata.csv`; no windows are used as independent subjects. Values are finite. Accelerometer channels are in the expected approximately 1-g scale, while gyroscope channels include high-motion/spike values up to roughly 1,200 in the source units. Therefore the next step is a documented signal-quality and unit check, including robust clipping or artifact handling fitted on the training participants only, before any pretraining run. The materialized array is not yet approved as model input without that check.

The first quality audit (`scripts/audit_zenodo_stroke_windows.py`) shows that the large gyro values are present directly in the interim files, especially during foot motion, rather than being created by the windowing interpolation: approximately 33–48% of foot-gyro samples exceed 100 source units, while lower-back gyro rates are near zero to 0.7% at that threshold. The raw Xsens headers show values in rad/s and the interim values are consistent with conversion to degrees/s (approximately 57.3×). This is compatible with genuine foot rotational motion, so blind clipping at 100 would destroy gait signal. Preserve the values and compare fold-fitted robust scaling against a high-percentile cap in the pretraining ablation.

The five-fold participant-level preprocessing ablation is saved in `data/processed/zenodo_preprocessing_ablation.csv`. Standard fold-fitted mean/standard-deviation scaling produced the lowest held-out extreme-score burden (mean absolute z-score 99th percentile 3.69; 0.02% above |z|=10). Robust IQR scaling alone produced heavier tails, and 99.5/99.9% caps did not improve the standardized tail metric. The provisional adapter contract is therefore standard scaling fitted on the stroke-pretraining fold, with no universal raw-value clip; cap-based preprocessing remains a sensitivity experiment only.

## First representation-pretraining run (2026-08-24)

The first GPU run used a small 1-D convolutional masked-reconstruction encoder on the 18-channel Zenodo windows. Two participants were held out entirely for validation; normalization statistics were fitted on the other eight participants. Across 15 epochs on the NVIDIA RTX 5060 Laptop GPU, training loss decreased from 0.204 to 0.047 and validation loss reached 0.050 at epoch 13 before a small late fluctuation. This confirms that the stream is learnable and the pipeline/checkpoint works, but it is not evidence of stroke-vs-healthy discrimination. The checkpoint is `data/processed/zenodo_masked_encoder.pt`; transfer learning must next be compared against the same architecture trained from scratch on the binary development cohorts.

The first transfer comparison is saved in `data/processed/zenodo_transfer_binary_comparison.csv`. Across three participant-level folds on the existing binary development windows, the pretrained encoder reached mean AUROC 0.969 (SD 0.021), while the identical scratch model reached 0.969 (SD 0.019). This small experiment shows no measurable benefit from the current masked-reconstruction pretraining. Do not claim transfer improvement; retain the checkpoint as an exploratory artifact and prioritize a stronger self-supervised objective or direct binary training.

## Broader method search and next candidate

The failed transfer result should not be interpreted as evidence that all pretraining is ineffective. Recent wearable-IMU work emphasizes that the pretext task and augmentations must preserve physical meaning. Candidate directions are: temporal contrastive learning/CPC, cross-sensor prediction, and physically plausible augmentation rather than arbitrary noise or masking. CPC is designed to capture temporal structure in body-worn sensor streams ([ACM UbiComp paper](https://doi.org/10.1145/3463506)); recent IMU work reports that physically plausible augmentation can outperform conventional transformations when labels are scarce ([Knowledge-Based Systems, 2026](https://doi.org/10.1016/j.knosys.2026.116367)). The next experiment will therefore use a lightweight temporal contrastive objective with gait-safe augmentations: short time crop, amplitude scaling, small temporal warp, and synchronized sensor dropout. It will be evaluated by the same transfer protocol, with no claim accepted unless it beats the scratch baseline across participant folds.

The initial temporal-contrastive run completed on CUDA using amplitude jitter and sensor-preserving noise augmentations. Contrastive loss decreased from 2.40 to 1.04 over 15 epochs, and the encoder was saved as `data/processed/zenodo_temporal_contrastive_encoder.pt`. This is only a pretraining optimization result; downstream transfer evaluation is still required.

Downstream transfer is saved in `data/processed/zenodo_temporal_transfer_binary_comparison.csv`. On the same three participant-level folds, temporal-contrastive initialization reached mean AUROC 0.964 (SD 0.023), below the matched scratch baseline of 0.969 (SD 0.020). It is therefore not adopted as the main binary training initialization. The result supports keeping the online stroke-only dataset as a robustness/pretraining research stream rather than assuming more pretraining automatically improves the classifier.

## Revised multi-role pooling strategy

The previous accept/reject wording was too shallow. Dataset usefulness is not a single binary property. We will evaluate each source through separate pathways:

1. **Direct supervised pooling:** only sources with compatible healthy/stroke labels enter the binary loss, with source-by-label balancing and source-held-out reporting.
2. **Shared representation pretraining:** stroke-only Zenodo data may contribute to an encoder even without healthy controls, but only if transfer improves participant-level performance.
3. **Multi-source domain generalization:** retain source IDs and train a shared feature extractor with source-specific heads or domain-adversarial regularization; evaluate on a source held out during training.
4. **Target-aware adaptation:** use unlabeled RevalExo only in a separate adaptation experiment, never in the frozen external benchmark or threshold selection.
5. **Source-specific ensemble/adapters:** allow a common backbone with lightweight source-specific normalization/adapters when sensor/device distributions are too different for one global representation.

The next combined-data experiment will compare naive pooling, source-aware pooled training, shared-backbone/source-specific-head training, and a domain-adversarial variant. Zenodo will contribute as a stroke-labelled auxiliary domain or unlabeled auxiliary domain—not be relabeled as a healthy/stroke binary source.

## Revised source review (2026-08-24)

| Source | Direct binary label role | Shared representation role | Domain/adaptation role | Decision |
|---|---|---|---|---|
| Felius | Yes: healthy/stroke, 163 participants | Yes | Main supervised source | Keep in primary binary pool |
| Voisard | Yes: healthy/stroke, 121 participants | Yes | Main supervised source | Keep in primary binary pool with source-aware weighting |
| Zenodo stroke rehabilitation | No: stroke-only, 10 participants | Yes, as auxiliary stroke domain | Yes, as a source/domain task | Add through auxiliary loss or domain branch, not binary relabelling |
| RevalExo | No training role | No during model selection | Frozen external test only | Do not use for fitting, normalization, or adaptation in the primary result |

The local validated binary pool contains 18,511 windows from Felius and Voisard: 163 Felius participants (34 healthy, 129 stroke) and 121 Voisard participants (72 healthy, 49 stroke). Zenodo adds 1,465 windows from 10 stroke participants, but its value is concentrated in stroke-domain variation and age/rehabilitation coverage rather than independent binary class balance. The revised review therefore does not discard it; it assigns it an auxiliary role that can be tested without inventing healthy labels.

Feasible combined experiments, in order: (A) current source-balanced Felius+Voisard binary model; (B) add Zenodo with an auxiliary stroke-versus-source/domain objective while retaining the binary loss only on Felius+Voisard; (C) shared encoder with Felius, Voisard, and Zenodo source-specific heads; (D) domain-adversarial shared encoder; and (E) source-specific adapters or an ensemble if source-held-out validation shows incompatible representations. Every experiment must use participant-level folds, keep RevalExo frozen, and report Felius, Voisard, Zenodo, and source-held-out metrics separately.

The first quick auxiliary-loss pilot used Zenodo as positive stroke supervision with a shared binary head. It reduced mean AUROC to 0.756 versus 0.957 for the matched binary baseline, so this naive auxiliary formulation is rejected—not Zenodo itself. The likely issue is that the auxiliary task supplied only positive labels and allowed source/label imbalance to shift the shared decision boundary. The next implementation must use source-specific heads or a domain classifier, balanced losses, and explicit gradient weighting before judging the combined strategy.

The source-specific-head pilot is saved in `data/processed/source_specific_heads_comparison.csv`. It reached only 0.525 AUROC on Felius and 0.592 on Voisard, so this implementation is not useful yet. This is an implementation failure signal, not evidence against the strategy: the quick run used a short five-epoch schedule and did not reproduce the established source-by-label weighting. It should not replace the validated pooled baseline. The next correction is to preserve the validated pooled objective and add only a low-weight, balanced domain-invariance term.

The corrected domain-adversarial pilot (`scripts/multisource_domain_adversarial.py`) used balanced batches from Felius, Voisard, and Zenodo, applied binary loss only to Felius/Voisard, and applied a low-weight gradient-reversal source penalty. It reached mean AUROC 0.965 (SD 0.019) across three internal participant folds. This is promising relative to the quick binary reference of approximately 0.957, but it is not yet a confirmed improvement because the training schedule and architecture must be matched exactly to the validated pooled benchmark. Promote it to the next formal experiment, with source-specific metrics and frozen RevalExo evaluation.

The established robust pooled benchmark reports source-balanced global AUROC 0.930 overall, 0.930 for Felius and 0.982 for Voisard, using its validated Inception protocol and five participant folds. The quick domain-adversarial pilot's 0.965 is therefore encouraging but not directly comparable: it used a different compact CNN, three folds, and a shorter schedule. The next formal run must reproduce the Inception architecture, five-fold source-by-label weighting, and seed-stability protocol, then add the domain penalty as the only change.

Zenodo has now been converted to the exact benchmark input contract: three acceleration magnitudes in `LB, LF, RF` order, shape `(1465, 500, 3)`, using `SA→LB`, `LF→LF`, and `RF→RF`. The output is `data/processed/zenodo_benchmark_acceleration_magnitude_windows_float32.npy` with matching metadata. Its magnitude median is 1.02 and range 0.087–13.00, so it is structurally compatible for the formal domain experiment; fold-fitted normalization remains mandatory.

The first formal-script attempt is not accepted as a model result. After correcting an indexing bug, its short fixed-epoch run still produced baseline AUROC 0.642 and domain-adversarial AUROC 0.381, far below the established benchmark. This indicates the script has not yet reproduced notebook 17's participant/source weighting, early stopping, and data-loader behavior. The values are retained as a debugging artifact only; no domain-adversarial conclusion is drawn. The next correction is to port the validated training loop exactly before adding the domain branch.

The notebook-integrated domain run now reuses notebook 17's definitions and protocol. Its five-fold mean AUROC is 0.961 (SD 0.038), compared with the established source-balanced-global pooled AUROC 0.957 in `robust_pooling_strategy_summary.csv`. The apparent gain is small (about 0.004) and uncertainty overlaps; it is promising but not sufficient for adoption. The next gate is external evaluation using a model trained without RevalExo fitting, normalization, calibration, or threshold selection.

The frozen external test was run with the full-internal domain model. RevalExo was not used for training, normalization, calibration, or threshold selection. Participant-level AUROC was 0.593 across 17 participants, substantially below the established frozen baseline AUROC 0.871. Therefore the domain-adversarial addition is rejected for the primary model despite its small internal gain; it appears to improve internal source alignment without transferring to RevalExo. The baseline remains the selected model, while the domain model is retained as a negative adaptation result.

## Current baseline age/situation interpretation

The Obsidian age page already reports the relevant executed subgroup result: baseline participant AUROC was approximately 0.953 for ages 40–59 and 0.913 for ages 60+, but each age stratum contains only about 8.4 and 7.4 participants per outer fold. This is a robustness signal, not definitive age-specific validation. The wider healthy Voisard release spans 18–87 years, while stroke participants do not cover the same young-age range; RevalExo lacks individual ages. Consequently, the baseline is currently supported for the observed cohorts and protocols, not for all age groups or clinical situations.

The next action is not another architecture experiment. Use the baseline as the frozen reference and complete a structured subgroup report from existing predictions: age band where available, source/protocol, sex where available, and clinical/visit variables where available. Mark unsupported cells explicitly and preserve the baseline as primary. Zenodo remains an optional domain/OOD specialist, not part of the primary probability.

The first reproducible coverage audit is saved in `data/processed/baseline_subgroup_coverage_audit.csv`. After collapsing repeated outer-fold predictions to one participant-level mean, age metadata is available only for healthy Voisard participants: 42 under 40, 15 aged 40–59, 9 aged 60–74, and 6 aged 75+. There are no age-labelled stroke participants in this linked table, so no age-band AUROC is estimable. This confirms that the current data cannot answer age-specific stroke generalization; the previous 40–59/60+ figures remain exploratory strata from a different executed analysis, not definitive subgroup validation.

## Healthy-only age expansion audit (2026-08-24)

The wider healthy-only sources do improve the healthy reference picture, but unevenly. DUO-Gait has 16 participants with exact ages 21–35. OxWalk has 39 participants with age bands `19–30`, `31–44`, and `45–81`, but not exact ages. MAREA's local README documents signal/activity files but no participant-age table. Camargo's local README documents protocols and sensors but no participant-age table. These sources can support healthy age-domain and false-positive analysis after signal harmonization, but they cannot provide age-matched stroke sensitivity. DUO-Gait is the strongest immediate age-labelled healthy candidate; OxWalk is usable only at coarse age-band level.
