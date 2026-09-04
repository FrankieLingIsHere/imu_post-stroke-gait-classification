# Pipeline comparison and processing audit

## Bottom line

The pipeline is stronger than many published stroke-gait studies in participant-level evaluation, source-aware pooling, leakage controls, frozen external testing, and explicit negative-result tracking. It is not yet a clinical-ready benchmark. The current negative synthesis results are not enough to conclude that the model architecture is the limiting factor, because several preprocessing and experimental-contract issues still need a controlled audit.

## Comparison with similar research

| Dimension | This project | Common published practice | Assessment |
|---|---|---|---|
| Clinical task | Stroke vs healthy, explicitly defined | Often gait subtype, severity, or threshold-derived “normal” labels | Clearer binary target, but not stroke-specific against other diseases |
| Input | Three acceleration-magnitude channels: lower back, left foot, right foot | Frequently 5+ IMUs, raw axes, gyroscope, pressure, or engineered features | Practical and aligned with the lower-back RQ, but discards orientation and gyroscope information |
| Sample size | 314 development participants; RevalExo 17 frozen external participants | Several deep-learning papers use fewer than 20 participants; stronger recent work uses 50–180+ | Good for a research prototype; external cohort remains small |
| Split | Participant-disjoint internal evaluation; participant-level aggregation | Leakage from windows or repeated trials remains common | Stronger than typical practice |
| External validation | RevalExo excluded from fitting and used once as a frozen stress test | Often absent or same-cohort validation | Major strength, but uncertainty is wide with n=17 |
| Model | Inception-style 1D CNN; MiniROCKET comparison available | 1D CNN, CNN-LSTM, DNN, SVM/RF; no universal winner | Defensible baseline; architecture superiority is not established |
| Augmentation | Tested diffusion and conventional augmentation with utility gates | Often reported only by internal score | Our rejection gates are more rigorous |
| Clinical utility | AUROC, Brier, balanced accuracy, healthy false positives | Accuracy is frequently the headline metric | Better evaluation contract, still needs prospective/independent cohorts |

Recent work reinforces this interpretation. A 2024 systematic review found methodological errors and limited clinical utility across post-stroke gait classifiers. A 2025 wearable-IMU study used 85 stroke patients and 97 controls with repeated split-level stability checks, while a 2026 deep-learning clinical gait study used participant-level 5-fold validation and training-only augmentation. These are useful comparators, but their tasks and sensors are not identical to ours, so headline accuracy is not directly comparable.

## Processing audit: what is sound

- Development and external participants are separated.
- Windows are aggregated to participants before headline metrics.
- MAREA and DUO-GAIT were resampled to 100 Hz and converted to the canonical 200-point cycle representation for synthesis.
- DUO-GAIT units were explicitly harmonized from g to m/s².
- Source/class-balanced sampling and fold-fitted normalization were used in the main robust-pooling work.
- Earlier bugs in cadence, turn handling, harmonic ratio, OxWalk bouts, and Felius loading were found and corrected rather than silently retained.

## Processing risks still requiring a fair audit

1. **Contract mismatch between experiments.** The synthesis pipeline uses complete 200-phase cycles, then the classifier ablation interpolates them to 500 samples. The real classifier windows are 5-second windows, not necessarily event-bounded cycles. This may create a distribution mismatch unrelated to generator quality.
2. **Magnitude conversion removes directional information.** Taking acceleration magnitude can make sensor orientation robust, but it also removes signed trunk/foot directional cues that may carry stroke asymmetry. A raw-axis or gravity-aware ablation is needed before attributing all limitations to the architecture.
3. **Cycle boundary convention differs by source.** MAREA uses left-foot heel strikes from GroundTruth; DUO-GAIT uses official processed left-foot IC events. The event definitions and stride durations need a side-by-side audit before treating them as the same “cycle” distribution.
4. **Synthetic parent grouping is artificial.** Assigning 25 synthetic cycles to one parent ID prevents window inflation, but those are not genuine participants. Utility experiments should report synthetic fraction by cycles and should not claim increased cohort size.
5. **The full-data prototype uses pool normalization.** This is acceptable for a final refit after model selection, but all comparisons must use fold-fitted statistics. The official robust-validation artifacts, not the convenience full-data checkpoint, remain the evidence source.
6. **The latest pretraining probe is architecture-mismatched.** The masked-reconstruction encoder is not the same feature extractor as the official Inception model, so its negative result does not rule out synthetic pretraining generally. It rules out this particular recipe.

7. **Raw-axis ablation is currently blocked by the available artifacts.** The processed development pool contains `validated_acceleration_magnitude_windows_float32.npy` with shape `(18511, 500, 3)` and Sint `(3995, 500, 3)`. No processed development raw 18-channel tensor is present. RevalExo does contain `(2228, 500, 18)`, but it is frozen external data and cannot be used to train a raw-axis comparison. Therefore, the magnitude representation cannot yet be blamed or cleared by experiment.

The source inventory has now narrowed this blocker: raw files are available for Voisard (1,356 text files) and Felius (1,148 CSV files), while no directly usable Sint CSV raw files were found in its extracted release. The raw-axis audit should therefore begin with Voisard+Felius under the primary contract; Sint can be retained in a separate magnitude-only sensitivity branch until an adapter is verified. Inventory: `data/processed/development_raw_axis_inventory.csv`.

The first linkage check found that `validated_window_metadata.csv` currently contains 16,366 Felius windows, but its stored `trial_id` values do not directly resolve to the raw Felius filenames. This is a metadata-key reconstruction problem: raw files exist, but a verified trial/subject mapping must be recovered before creating raw-axis windows. No raw-axis tensor has been created yet.

## Online-release resolution

The official Felius paper states that all data and processing software are released through Zenodo DOI `10.5281/zenodo.11044903`; the authors' processing repository is [Reliability-of-Gait](https://github.com/RichardFel/Reliability-of-Gait). Its README confirms the intended input contract: three IMU files (two feet and one low back), seven columns consisting of timestamp, three accelerometer axes, and three gyroscope axes. The local release's `Data_Healthy`, `Data_Stroke`, and `Data_long` folders follow that contract, but the processed window table stores a shortened/normalized trial key that is not the raw filename key.

The safe solution is to use the official folder-aware `list_trials()` logic as the source of truth, create a mapping table from `(subject, trial_key, folder)` to processed `trial_id`, and require exact subject plus sensor-triplet agreement before slicing. We should not infer mappings from row order or nearest filename similarity.

## Signed-axis reconstruction completed

The mapping was resolved using exact trial and sensor-triplet filenames. All 18,511 development windows were reconstructed: 16,366 Felius and 2,145 Voisard, across 284 participants, as `primary_signed_acceleration_windows_float32.npy` with shape `(18511, 500, 9)`. Voisard raw m/s² values were converted to g; Felius values were already in g. Recomputing the three magnitudes from the signed tensor reproduced `validated_acceleration_magnitude_windows_float32.npy` exactly within floating-point tolerance (mean absolute error 0.0; maximum approximately 1e-6). The new artifact is therefore a verified representation sibling, not a new or mismatched dataset.

## Corrected signed-axis versus magnitude ablation

Using identical five participant-disjoint folds, source/class-balanced sampling, fold-fitted normalization, and participant-level epoch selection, the 9-channel signed-axis and 3-channel magnitude representations gave:

| Representation | Mean AUROC | Mean Brier | Mean balanced accuracy |
|---|---:|---:|---:|
| Magnitude (3 channels) | 0.9794 | 0.0660 | 0.9080 |
| Signed axes (9 channels) | 0.9741 | 0.0563 | 0.9274 |

Signed axes slightly reduced ranking discrimination but improved calibration and balanced accuracy. This is exploratory internal evidence, not a replacement decision: the signed-axis branch still needs frozen RevalExo evaluation and repeated seeds. The first run selected epochs using window-level AUROC; that result was discarded and replaced by this participant-level selection run.

## Frozen external signed-axis test

The signed-axis branch was trained with the same five participant-disjoint folds and evaluated on RevalExo after applying the verified `LB, LF, RF` axis-block mapping and each fold's training normalization. It failed external transfer:

| Representation | AUROC | Brier | Balanced accuracy | Healthy FPs |
|---|---:|---:|---:|---:|
| Signed axes, RevalExo | 0.457 | 0.412 | 0.500 | 7/7 |
| Official magnitude baseline, RevalExo | 0.914 | 0.161 | 0.714 | 4/7 |

This resolves the internal/external disagreement: signed axes contain useful within-dataset information but are not orientation/domain invariant across the current source systems. The magnitude representation remains the official deployment-facing contract. Signed axes should only be revisited with validated sensor-frame alignment, gravity/dynamic-acceleration separation, or an explicitly domain-invariant representation.

## What should be done before changing architecture again

1. Create one locked preprocessing contract for raw axes, magnitude, sampling rate, window/cycle definition, and channel order.
2. Recover/reconstruct development raw tri-axial accelerometer channels from the immutable source releases, then run a paired ablation: magnitude vs signed axes, fixed 5-second windows vs event-normalized cycles, with identical participant folds.
3. Re-run the current Inception and MiniROCKET baselines under that contract.
4. Add a simple feature baseline using trunk RMS, cadence, mean stride time, and bilateral asymmetry; these are the most defensible cross-source features in the wiki.
5. Only then test a CNN-LSTM/TCN or transformer; model complexity should be justified by repeated participant-level improvement, not training loss.

## Decision

The approach is methodologically credible as a research prototype, but not “done enough” to claim the current limitations are purely architectural. The most responsible next step is a preprocessing-contract audit and raw-axis/magnitude ablation. The generator should remain quarantined until that audit is complete.

## References

- Jiao et al., systematic review of automatic post-stroke gait classification (2024): https://www.sciencedirect.com/science/article/pii/S0966636224000559
- Wearable MIMU feature stability study (2025): https://pmc.ncbi.nlm.nih.gov/articles/PMC12987975/
- Participant-level deep-learning clinical gait validation (2026): https://rehab.jmir.org/2026/1/e94031
- IMU validity/reliability in post-stroke gait (2024): https://pubmed.ncbi.nlm.nih.gov/37545107/
