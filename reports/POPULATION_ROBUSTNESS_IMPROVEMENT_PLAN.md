# Improving population robustness after synthetic-enrichment rejection

## Evidence-led conclusion

Direct MAREA/DUO-GAIT synthetic healthy enrichment is rejected: it does not produce a material, repeatable gain in participant-disjoint validation. The remaining problem is population/domain shift, arising from participant characteristics, protocol, sensor hardware/attachment, placement/orientation, and walking context. These factors are also identified as major cross-domain sources of variation in recent IMU-HAR benchmarking.

## Ordered next experiments

1. **Worst-domain evaluation before a new model.** Extend the existing participant-disjoint benchmark with leave-one-source-out and leave-one-protocol-out splits. Report mean *and worst-group* AUROC, Brier, balanced accuracy, sensitivity, specificity, and healthy false positives. A model that improves average performance but harms one source is not accepted.
2. **Group-robust real-data training.** Train the existing magnitude Inception model with group distributionally robust optimization or a worst-source validation objective over Voisard, Felius, and Sint. Use source only during training; do not require a source ID at deployment. Compare against source/class-balanced sampling under identical folds.
3. **Real-signal, physically constrained augmentation.** Test one factor at a time inside training folds: small amplitude calibration changes, sensor-noise/drift profiles, and cadence-preserving time warps. Retain acceleration magnitude, which is externally robust to orientation; do not resurrect signed-axis augmentation until frame alignment is validated. Reject every transformation that harms a held-out source.
4. **Specificity-first calibration and abstention.** Use nested out-of-fold probabilities to set a high-specificity operating threshold and an indeterminate zone. The indeterminate outcome prompts repeat walking or clinical review. It is more defensible than forcing a binary label in a population unlike the training cohort.
5. **Hard-negative evaluation data.** Prioritize real older healthy controls and non-stroke mobility disorders for evaluation, not as blindly relabelled training data. The key question becomes whether the model says “stroke” for Parkinsonism, osteoarthritis, COPD, fracture, or slow healthy gait. This prevents a stroke-vs-young-healthy shortcut.
6. **Age and severity reporting.** Where subject-level metadata exists, report age-overlap and severity strata with confidence intervals. Do not add age as a classifier input until healthy/stroke age overlap is adequate; current evidence shows that age can become a shortcut.
7. **Second independent external cohort.** RevalExo is a useful stress test but contains seven healthy people. A second wearable-IMU cohort with both healthy and stroke participants is required before any clinical-ready claim.

## Acceptance rule

Select an improvement only when repeated participant-disjoint validation improves or is non-inferior on the worst source and does not worsen frozen external calibration, balanced accuracy, or healthy false positives. Do not select by AUROC alone.

## Leave-one-source-out group-robust experiment (2026-09-01)

The first real-data robustness experiment held out one complete source at a time and compared source/class-balanced empirical-risk minimization (ERM) with a group-distributionally robust objective over the source-by-class groups seen in training. Normalization was fitted only on the two retained sources; RevalExo was untouched.

| Held-out source | Training | AUROC | Brier | Balanced accuracy | Healthy false positives |
|---|---|---:|---:|---:|---:|
| Felius | source-balanced ERM | 0.899 | 0.221 | 0.762 | 3/34 |
| Felius | group-DRO | 0.895 | 0.243 | 0.761 | 2/34 |
| Sint | source-balanced ERM | 0.905 | 0.129 | 0.800 | 0/20 |
| Sint | group-DRO | 0.955 | 0.113 | 0.850 | 4/20 |
| Voisard | source-balanced ERM | 0.927 | 0.123 | 0.807 | 19/72 |
| Voisard | group-DRO | 0.920 | 0.165 | 0.816 | 25/72 |

Group-DRO helps Sint discrimination but worsens healthy specificity, and it does not improve the Felius or Voisard holdouts. It therefore fails the project acceptance rule as a global replacement. The result exposes Voisard healthy specificity as the highest-priority internal hard-negative problem. Next: targeted real-signal augmentation and threshold/abstention analysis evaluated specifically against the held-out Voisard healthy group, not further synthetic enrichment.

## Targeted physical augmentation on held-out Voisard (2026-09-01)

The next predeclared test trained only on Felius and Sint, then held out **every Voisard participant**. The augmentation was intentionally modest and physically plausible for acceleration magnitude: independent per-sensor gain (0.95--1.05), Gaussian noise (SD 0.01 g), and a shared 0.92--1.08 cadence-preserving time warp. Fitting normalization, sampling, and training all used only the retained sources. RevalExo was not read or used.

| Training mode | Held-out participants | AUROC | Brier | Balanced accuracy | Healthy false positives |
|---|---:|---:|---:|---:|---:|
| Source/class-balanced ERM | 121 | 0.897 | 0.131 | 0.807 | 16 |
| + physical augmentation | 121 | 0.883 | 0.178 | 0.779 | 26 |

The augmentation increases Voisard healthy false positives by ten and degrades discrimination and calibration. It is rejected, rather than tuned against this holdout. This is useful negative evidence: simple signal noise, gain, and time-warp simulation does not recreate the source/population shift. The next experiment is threshold and abstention selection from participant-level out-of-fold development predictions, followed by an untouched external RevalExo check only after the operating rule is locked.

## Strict specificity operating-rule audit (2026-09-01)

The participant-level OOF audit did not support a clinically safe two-sided healthy/stroke triage rule. At the first threshold satisfying both pooled 95% Wilson lower-bound healthy specificity >=90% and observed healthy specificity >=90% in each source (0.78), pooled specificity is 96.8% but pooled sensitivity is 63.8%; worst-source sensitivity is 60.0%. No uniform automatic healthy-clearance threshold meets the corresponding pooled and per-source sensitivity criteria. Use this only as a descriptive high-specificity referral candidate, not as a replacement for the baseline 0.5 classifier. One locked, descriptive RevalExo evaluation follows; it cannot be used to change the rule.

The locked RevalExo check of 0.78 is complete: 6/7 healthy participants are negative (one FP), while 7/10 stroke participants are positive (three FN), for 85.7% specificity, 70.0% sensitivity, and 77.9% balanced accuracy. This is a one-time descriptive evaluation of the saved full-expanded prototype, not a further decision gate. It confirms that thresholding can reduce false positives but cannot make this cohort clinically adequate or eliminate the need for real hard-negative data.

## Existing Voisard non-stroke hard-negative evaluation (2026-09-01)

The full local Voisard release already contains 138 participant-disjoint non-CVA clinical hard negatives collected with the same 100 Hz LB/LF/RF protocol. The saved full-expanded model was evaluated without retraining or tuning. It classifies 72/138 (52.2%) as stroke at 0.50 and 43/138 (31.2%) at the locked 0.78 threshold. The greatest false-positive burdens are RIL (62.7% / 49.0%) and PD (62.5% / 33.3%). This demonstrates an unresolved differential-diagnosis failure, not merely a healthy-cohort size issue. Keep these cohorts out of the binary training set; their immediate role is a hard-negative stress test and, later, a separately designed open-set/differential-gait study. See `VOISARD_NONSTROKE_HARD_NEGATIVE_EVALUATION_2026-09-01.md`.

## Binary hard-negative exposure (2026-09-01)

The final-product constraint was retained: the tested model emits only a binary stroke score. Non-CVA data were treated as temporary negative exposure, with one entire pathology cohort held out per run and a separate five-fold participant-disjoint primary-task safety gate. A 25% exposure dose reduces unseen-pathology FPs (52.2% to 31.2%) but fails the primary gate (Brier 0.0904 to 0.1404; BA 0.8941 to 0.8236). A 7.7% dose preserves the primary task (AUROC/Brier/BA 0.9585/0.0838/0.8901) but only reduces unseen-pathology FPs to 46.4%; PD and RIL remain high. Neither variant is admitted. The next evidence need is independent, age-overlapping real healthy/stroke data and a pre-specified confidence/abstention study, not further blind pooling.

## Why this is preferable to further direct synthesis

Synthetic data can improve one distribution while increasing false positives in another. Our own results demonstrate that risk. Recent work similarly treats user, device, placement, environment, and demographic variation as separate domain shifts, and studies cross-population gains with nested evaluation rather than assuming pooled data always helps.

## References

- Smartphone/IMU domain-adaptation benchmark (2024): https://pmc.ncbi.nlm.nih.gov/articles/PMC11531562/
- Cross-population single-IMU gait study (2025): https://pubmed.ncbi.nlm.nih.gov/41516612/
- Stroke wearable MIMU feature-stability study (2025): https://pmc.ncbi.nlm.nih.gov/articles/PMC12987975/
- Motion-Drift Augmentation for IMU analysis (CVPR 2025): https://mlanthology.org/cvpr/2025/wu2025cvpr-moda/
