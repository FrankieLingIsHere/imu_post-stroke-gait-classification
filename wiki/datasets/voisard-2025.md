---
type: dataset
population: "260 participants: 73 HS, 143 neuro (49 CVA/stroke, 19 CIPN, 24 Parkinson's, 51 RIL), 44 ortho (ACL/HOA/KOA)"
sensors: "head, lower back, bilateral foot, 100 Hz"
role: primary
---
Latest experiment (2026-09-09): [Controlled regularization and warm-up](../../docs/classification/VGA_REGULARIZATION_RESULT.md) completed and verified: 27 fits, all 40 epochs, same 248-person VGA impairment-screening target. Control normal false alerts16-17/84 and impairment detections91-101/164; decay16-18 and87-102; warm-up15-19 and89-103. Warm-up slightly improves paired full AUROC but increases false alerts in two seeds. All settings fail the prototype gate. Only2/27 runs improve after simulated patience8 stopping, best epochs1-24, none at40. No consistent specificity fix, no model promotion. Schedule/optimizer tests and source/label/split/threshold/metric/checkpoint verification passed. Metadata and raw acquisition unchanged, preprocessing reused, evaluation complete. DUO-GAIT remains a reused alert stress test without VGA labels. Do not rerun this completed comparison.

This week: [progress, benchmark tables and model structures](../../docs/classification/WEEKLY_PROGRESS_2026-09-07.md) (2026-09-07 through 2026-09-09). Separates the packaged stroke logistic model, stroke CNN comparisons and six-channel VGA screening reference. No new training or promotion. [Week 3 GitHub Pages report](https://frankielingishere.github.io/imu_post-stroke-gait-classification/reports/WEEK_03_PROGRESS.html) published and live-verified on 2026-09-09.



Implementation update (2026-09-09):
[packet correction executed](../../reports/PACKET_ALIGNMENT_CORRECTION_2026-09-09.md).
Native clock reconstruction and versioned 259-person RMS comparison are complete;
combined other FPR remains 50.7%. Frozen non-stroke positives remain 89/138 with
zero participant flips. Strict matched predictions remain unchanged. This resolves
the implementation comparison's provisional mixed-cohort RMS status; manuscript
statistics are preserved pending a separate manuscript-wide impact assessment.
Use the new aligned native loader for future extraction. Event truth remains
algorithm-derived, and no clinical specificity improvement is established.


Voisard, C. et al. (2025), *A dataset of clinical gait signals with wearable sensors from healthy, neurological, and orthopedic cohorts*, *Scientific Data* 12:1674. The review's **primary** hands-on-mining dataset — the largest, richest-metadata real stroke-vs-healthy source, and the only one of the two real stroke datasets with any participant-level demographic data at all.

## Key findings (this review's own re-mining)

- HS/CVA comparison uses 73 healthy + 49 CVA participants (488 trials). **Not age-matched**: HS averages 37.7y (SD 19.5) vs. CVA 59.0y (SD 8.8), a ~21-year gap.
- Raw cadence looked discriminative (p < .001) but reversed to non-significant (p = .315) after age-adjustment via linear residualization — the review's central demographic-confound finding. **Collinearity check added 2026-07-29** (after a `journal-critic` review questioned whether age and group were too correlated for the regression to separate them): point-biserial r = 0.48 between age and group, VIF approximately 1.3 — moderate, not severe by conventional thresholds — and every CVA participant's age falls within the HS group's own broader range, confirming enough within-group age variation exists for the adjustment to be meaningful rather than an artifact of near-perfect collinearity.
- Lower back RMS, head RMS, mean stride time, and stride-time CV all remain significant after age-adjustment (rank-biserial r = 0.58, 0.30, -0.43, -0.32) and anchor [[sensor-placement]]'s trunk-placement finding.
- The age-by-stroke interaction audit used one participant-level row per Voisard participant. Head RMS and lower-back RMS had nominal interaction p-values of 0.039 and 0.049, but both became q = 0.148 after Benjamini--Hochberg correction across six features. The result supports age-stratified auditing, not an age-gated stroke classifier. See [[age-and-stroke-gait]].
- The provisional age bands contain 43 healthy and 0 CVA participants at 18--39, 15 healthy and 27 CVA participants at 40--59, and 15 healthy and 22 CVA participants at 60+. Only the latter two bands support within-band binary performance checks.
- The complete release has 259 participants with valid ages from 18 to 90 years across healthy, neurological and orthopedic cohorts. One participant has an invalid or missing age value. The primary healthy/CVA subset has 72 healthy participants with usable validated windows and ages 18--87, while CVA participants begin at age 41. This is broad overall coverage but not broad age overlap for the binary stroke task.
- Continuous age regression on healthy Voisard participants was exploratory. A Ridge model using engineered gait features reached mean MAE 12.86 years and R² 0.310 across repeated participant-level folds. The GPU Inception-style regression reached MAE 13.42 years and R² 0.243. See [[age-and-stroke-gait]].
- In the age-adjusted stroke baseline, raw gait features reached AUROC 0.973, gait plus age reached 0.968 and age alone reached 0.803 across repeated participant-level folds. Age-residualized gait fell to AUROC 0.882. This is a shortcut audit on the current age-imbalanced subset, not evidence for clinical deployment. See [[age-and-stroke-gait]].
- A **second**, independently discovered confound: HS gender effect is real on cadence and both stride-time measures even after age-adjustment, but the two accelerometer-RMS gender effects are age artifacts. See the manuscript's Section 4.2.2 for the full age-adjusted gender breakdown.
- Voisard's per-trial Fugl-Meyer LE and Timed-Up-and-Go scores remain under-exploited — not yet used beyond the binary healthy-vs-stroke comparison. Flagged as a specific gap in [[future-directions]].
- Nested SBS+CV: 0.89 accuracy (SD 0.06). Single-level CV: 0.92 (SVM) / 0.95 (RF). Cluster purity 0.76, adjusted Rand index 0.27.

## Links

Paired directly against [[felius-dataset]] throughout [[discriminative-features]] and [[sensor-placement]] as the review's two real stroke-vs-healthy sources. The age and gender confounds discovered here are the review's most-cited original findings — see `synthesis.md`.


## Phase-feature development result, 2026-09-09

[Executed comparison](../../reports/BILATERAL_PHASE_COMPARISON_2026-09-09.md)
adds alternating step, swing/stance asymmetry and support fractions from existing
annotations. All 259 selected participants retained. Primary other FP falls
73 to 64/138 but stroke detections fall 43 to 41/49. Matched subset also loses
sensitivity, so neither passes the locked gate. This improves development ranking
but does not establish diagnostic specificity or recovery from one lower-back IMU.
Metadata/raw acquisition unchanged, phase preprocessing and evaluation complete.
See [[classification-project-status]] for the current next question.


Follow-up [nested threshold evaluation](../../reports/PHASE_NESTED_THRESHOLD_2026-09-09.md)
also failed both primary gates. At training-selected sensitivity thresholds,
matched combined+phase detects 45/49 stroke but calls 62/76 other and 13/19 healthy
positive. Phase information has not delivered adequate specificity at high
sensitivity. Stop threshold sweeps. Acquisition unchanged, preprocessing reused,
nested evaluation complete. See [[classification-project-status]].


## Stance variability feasibility completed, 2026-09-09

[Executed CV coverage check](../../reports/STANCE_VARIABILITY_FEASIBILITY_2026-09-09.md):
1,259/1,348 usable trial CVs. Healthy 68/72, ACL 9/11 and HOA 13/15 fail the locked
95% group coverage gate; stroke 49/49. No participants dropped, no model fitted,
no new accuracy result. Eight CV/phase tests passed. Metadata/raw acquisition
unchanged, CV preprocessing complete and classifier evaluation not run.
All selected raw headers contain Acc/Gyr/Mag XYZ; the subsequent audit below
resolves nominal axes, without per-trial calibration. Next is provider device-axis convention verification for directional
harmonic ratio, followed conditionally by gyro measurement validation. Existing
magnitude HR is not ML HR. OOD stays lower priority. No release changes or running job.


## Directional-axis audit completed

[Provider/file verification](../../reports/DIRECTIONAL_AXIS_AUDIT_2026-09-09.md)
establishes nominal LB X vertical, Y ML, Z AP. It supersedes the earlier metadata-only
uncertainty. Raw/processed mappings: 750 TechnoConcept flip X/Y, 37 identity,
507 XSens identity, 54 unsupported comparisons. All comparable filtered mappings
match to numerical precision. CVA_18_2 has Z-dominant initial gravity; retain as a
quality flag, not a diagnosis-based exclusion. Per-trial anatomy remains unvalidated.
Nominal-Y harmonic ratio with coverage/orientation sensitivity is completed below. Sign inversion is irrelevant to Fourier amplitudes but
relevant to gyro laterality. Acquisition unchanged, axis audit complete, HR
extraction/evaluation completed below. No new diagnostic score or release change.


## Directional HR experiment complete

[Executed results](../../reports/ML_HARMONIC_RATIO_2026-09-09.md): primary matched
phase+HR detects 44/49 stroke with 5/19 healthy and 47/76 other FP, versus 42/49,
13/19 and 61/76 without HR. Full HR: 45/49, 6/72 and 56/138. Both primary gates
fail (matched sensitivity below 90%, full FPR improvement below 5pp). All 259
participants retained; main HR coverage complete, quality-screened HR available
245/259 with train-only imputation. Three tests and 96 fits complete. Improvements
not uniformly robust to quality screening. No model promotion. Metadata/raw
acquisition unchanged, HR preprocessing/evaluation complete. Conditional gyro laterality is completed below. OOD remains separate.


## Conditional gyro laterality completed

[Executed result](../../reports/GYRO_LATERALITY_2026-09-09.md): reference-time side
assignment gate failed. Matched healthy 97.8%, stroke 89.6%, CIPN 95.9%, PD 96.6%,
RIL 88.1% participant-macro accuracy. Full stroke 71.4%, healthy 54.0%. Six fresh
fits and two tests complete, 48,131/48,257 contacts usable. No pretrained pickle
or environment downgrade used. No automatic label flipping or adapter promotion.
The signed gyro audit is completed below; scope dependence is not proof of device causality. Acquisition unchanged, conditional
preprocessing/evaluation complete. Autonomous and independent measurement validation
remain unfulfilled. Stroke-classifier results unchanged. No running job.


## Gyro mapping audit complete

[Executed mapping audit](../../reports/GYRO_AXIS_TRANSFER_AUDIT_2026-09-09.md):
1,294 comparable trials, all gyro/acceleration sign permutations agree. Scale 1,
constant offset correction reconstructs processed gyro to max RMSE 2.1e-14.
54 comparisons unsupported. No input bug found that justifies retraining.
Ten participants with both devices have saved side accuracy 25.9% XSens vs 78.9%
TechnoConcept; sessions/mounting/protocol remain possible contributors. No label
flips or independent anatomical validation. Two tests passed. Acquisition unchanged,
audit complete, model results unchanged. Close this audit. New calibration needs
independent frame evidence; OOD must consult prior abstention decisions first.


## Physical calibration hypotheses checked

[Executed checks](../../reports/GYRO_CALIBRATION_EVIDENCE_2026-09-09.md): U-turn
integrals 3.075 XSens/3.068 TechnoConcept support common radians/s scale. Processed
initial bias near zero, head/back turn signs agree 1,343/1,343 usable trials.
These do not prove absolute handedness. All ten paired-device participants use
different sessions; prior device accuracy gap is confounded by visit/mounting,
with one distance-protocol difference. No guessed correction or new model fit.
Acquisition unchanged, physical checks complete, independent calibration unresolved.
Next prerequisite: independent known-direction/event references, not repeat unit,
bias or raw/processed mapping checks. Model results unchanged.
