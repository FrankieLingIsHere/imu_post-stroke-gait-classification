---
type: concept
---

# Classification methodology

Current implementation: [workspace guide](../../docs/classification/README.md) and [weekly progress](../../docs/classification/WEEKLY_PROGRESS_2026-09-07.md). Completed public results are in Week 3 commit `b462795`; remaining local files include both completed work and active research.

Current engineering decision: user authorizes lower research-prototype gates.
[Policy, dataset roles and CLI](../../docs/RESEARCH_PROTOTYPE_POLICY_2026-09-09.md).
TVS laterality prototype packaged on 32 participants/1,645 contacts under 85%
accuracy and 85% coverage gates. Earlier CV: HA 87.46%, PD 87.34%, corrected coverage
86.45%/85.45%. This is post-result prototype acceptance, not revised validation.
Original failed gates remain historical evidence. Frozen stroke model unchanged.
Acquisition unchanged, prototype fitting/packaging and real CLI smoke check complete.
Inputs require native TVS-frame gyro and supplied contact indices. No stroke output.

Methodological background: [2026-09-09 report](../../reports/CLASSIFICATION_METHODOLOGY_REVIEW_2026-09-09.md).
The lower-back magnitude classifier has not established transferable stroke
specificity. It consumes local movement patterns, without explicit side-labelled
gait events. An executed architecture check confirms a maximum 74-sample local
receptive field before global averaging; this is not proof of the clinical cause
of its errors.

## Key findings

- [[discriminative-features]] already documents group effects and device-matched
  sensitivity analyses. These do not establish that the classifier avoids device
  shortcuts or distinguishes stroke from other gait disorders.
- [[classification-project-status]] records completed TVS evaluation and rejected
  three-class training. No successful sensitivity-preserving specificity fix exists.
- Mobgap offers lower-back gait measurement; gaitmap focuses on foot IMUs.
  Commercial Mobility Lab and Physilog evidence concerns gait measurement, not
  a verified drop-in stroke diagnostic classifier. Sources and limitations are
  linked in the report.
- [Conditional comparison executed](../../reports/CONDITIONAL_GAIT_COMPARISON_2026-09-09.md):
  259 participants, 36 fits; device/protocol-matched subset 144 people. RMS AUROC
  .801 against healthy but .449 against other pathologies. Added gait features
  failed to improve on covariates plus cadence. Matching changes case mix too;
  no causal hardware attribution is established.
- [Event adapter completed](../../reports/LOWER_BACK_EVENT_VALIDATION_2026-09-09.md):
  all 260 people/1,356 trials; autonomous stroke F1 .811, count-cadence MAE 17.51.
  Default mobgap components fail admission. Reference-bout F1 .855 isolates part
  of the segmentation difficulty; no diagnosis improvement claimed.
- [Native alignment correction completed](../../reports/PACKET_ALIGNMENT_CORRECTION_2026-09-09.md):
  1,348 trials verified against provider processing; feature comparison regenerated.
  Frozen model gives 89/138 non-stroke positives before and after on identical
  windows, with zero changed participant calls. Combined feature other FPR stays
  50.7%. Correction is retained; it does not fix specificity. Do not rerun this
  closed experiment. Supplied events remain algorithm-derived references.
- Report speed-conditional and total discrimination separately. If only impairment
  is supported, narrow the endpoint rather than relabel it as stroke specificity.

No new raw data were acquired. Metadata, raw-signal, preprocessing and evaluation
completion remain as recorded in [[classification-project-status]].

## Bilateral phase experiment completed, 2026-09-09

[Executed comparison](../../reports/BILATERAL_PHASE_COMPARISON_2026-09-09.md):
259 participants, 1,348 trials, 1,345 complete trial phase sets. Every participant
retained with complete aggregated features. Existing folds and corrected baselines
reproduced. Four unit tests passed and 24 logistic fits completed.
Primary phase addition: other FP 73 to 64/138, stroke detections 43 to 41/49.
Matched subset: other FP 35 to 26/76, stroke detections 34 to 30/49. Both fail the
locked sensitivity-preserving gate. Secondary combined+phase matched other FP
43 to 31/76 with stroke detections unchanged at 31/49. Useful development signal,
not a proven root cause or admitted replacement. Frozen model remains unchanged.
Metadata/raw acquisition unchanged. Phase preprocessing and evaluation complete.
No download or running job.

## Nested sensitivity threshold experiment completed

[Executed result](../../reports/PHASE_NESTED_THRESHOLD_2026-09-09.md): 72 inner
fits with thresholds selected only from inner OOF stroke scores at a 90% target.
Both primary gates failed. Full phase arm detects 41/49 stroke with 59/138 other
FP, baseline 44/49 and 61/138. Matched phase arm detects 42/49 with 61/76 other FP,
baseline 44/49 and 69/76. Secondary matched combined+phase detects 45/49, but
62/76 other and 13/19 healthy are positive. Three threshold unit tests passed.
All participants retained, no release changes. Metadata/raw acquisition unchanged,
phase preprocessing reused and nested evaluation complete. Stop threshold sweeps.
Current roadmap priority is the directional measurement prerequisite described below.
Do not relabel stroke scores as validated gait-abnormality scores. Sensor-only phase
recovery and diagnostic specificity remain unvalidated. OOD is a separate question.

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

## Optical event-reference intake completed

[TVS intake and exploratory classifier](../../reports/TVS_OPTICAL_REFERENCE_AND_CLASSIFIER_2026-09-09.md):
32 local participants, 17 HA/15 PD. Raw optical markers and explicit event sides
verified. Optical/INDIP side agreement 1,584/1,584 matched contacts. Corrected
contact coverage 86.4% HA/85.4% PD fails gate. Initial denominator bug allowed
three exploratory fits, 87.46%/87.34% accuracy; saved as exploratory, not admitted.
Corrected intake rerun, no further fits. 163/225 trials usable; 45 missing optical,
17 partial/invalid. No stroke group, no stroke model promotion. Acquisition
unchanged, reference extraction complete, corrected model eligibility failed.
Next is explicit per-contact reference-quality handling, not dropped bad trials.
Independent calibration of Voisard is not established by TVS references.

## Stroke feature prototype packaged

[Executable package and input contract](../../models/prototypes/stroke-phase-hr-v0.1.0/README.md):
full fit on 259 Voisard participants, ten covariate/phase/HR features. Threshold
0.3953767333929809 from inspected development OOF scores, not independent validation.
Three contract tests, serialization parity, example CLI and full 259-row smoke
passed. Invalid rows produce unknown, only age may be imputed. Requires annotated
phase features, not autonomous raw input. Historical nested metrics unchanged.
Acquisition unchanged, feature preprocessing reused, packaging complete, independent
evaluation open. Files use versioned package/examples and processed batch folders.

## Stroke feature benchmark verified

[Executed benchmark](../../docs/classification/BENCHMARK.md): all ten predictors
reconstructed from 1,348 trials for 259 people, only one missing age. Twelve
held-out refits reproduce saved scores; candidate API matches fold predictions.
Ten contract/phase/HR tests passed. Full AUROC 0.897, TP 45/49, healthy FP 6/72,
other FP 56/138. Matched AUROC 0.835, TP 44/49, healthy FP 5/19, other FP 47/76.
Full orthopedic FP 0/44, neurological controls remain difficult, CIPN worsens
versus baseline. Thresholds from inner OOF training only for these metrics;
full-package threshold is not independently evaluated. Acquisition unchanged,
feature reconstruction/benchmark complete, sensor-only and independent validation open.


Notebook restructuring (2026-09-10): notebooks 36 and 37 consolidate phase/measurement
and VGA reports with saved artifact-replay outputs. Six standalone report scripts
removed after dependency checks; original source-byte hashes verified against
notebook audit cells. Shared experiment helpers and utilities remain Python.
No new model run, dataset acquisition or clinical evaluation. See the notebook
guide for the current reading path.
