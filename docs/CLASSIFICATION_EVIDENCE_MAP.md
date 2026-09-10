# Classification evidence map

Current implementation: [workspace guide](classification/README.md) and [weekly progress](classification/WEEKLY_PROGRESS_2026-09-07.md). Completed public results are in Week 3 commit `b462795`; remaining local files include both completed work and active research.

> Current user-authorized direction: working research prototypes may use lower
> gates, with historical validation failures preserved. See
> [prototype policy and dataset roles](RESEARCH_PROTOTYPE_POLICY_2026-09-09.md).
> TVS contact-laterality prototype is packaged and CLI verified; it is not a stroke model.
> Stroke phase+HR prototype is now [packaged and CLI verified](classification/README.md).
> [Feature audit and held-out benchmark](classification/BENCHMARK.md) completed.
> Full-development threshold remains exploratory; no new independent validation.

Current handoff: [wiki project status](../wiki/concepts/classification-project-status.md).
Historical: [differential implementation](../reports/DIFFERENTIAL_GAIT_IMPLEMENTATION_2026-09-09.md). The three-class
candidate was implemented and rejected after sensitivity loss. An optional
constant/nonfinite validity wrapper is implemented; it does not fix moving-gait
false positives. Frozen v0.2.0 and prior predictions are unchanged.

TVS metadata/raw/preprocessing/evaluation are complete for the locked scope:
40 metadata, 36 raw participants, 34 evaluated on 117 windows; 17/18 healthy and
16/16 PD positive. See [cohort result](../reports/TVS_COHORT_RESULT_2026-09-09.md).
No process or acquisition remains pending. All TVS evidence is now inspected.

| Question | Existing evidence | Model and status |
|---|---|---|
| Does explicit three-class supervision fix specificity? | [Executed differential experiment](../reports/DIFFERENTIAL_GAIT_IMPLEMENTATION_2026-09-09.md) | New one-channel, same-protocol matched controls; 27 fits, failed all seed gates. Completed, not promoted. |
| Where does the selected ensemble make FP/FN errors? | Notebook 30; `data/processed/lower_back_ensemble_seed_consensus_confusion.csv`; `lower_back_ensemble_persistent_errors.csv` | Notebook-29 lower-back ensemble, source-held-out predictions. Completed. |
| Can a threshold remove both error types? | [Score overlap report](../reports/SCORE_OVERLAP_AND_HETEROGENEOUS_RESCUE_2026-09-03.md), notebook 31 | Selected lower-back ensemble consensus. Completed: minimum 58 errors; zero FP requires 157 FN; zero FN requires 87 FP. Do not repeat threshold search. |
| Has specificity-first threshold/deferral been attempted? | [Specificity strategy](../reports/SPECIFICITY_FIRST_FALSE_POSITIVE_STRATEGY.md); `development_specificity_abstention_summary.csv` | Historical three-channel model with participant OOF splits, not source-held-out lower-back ensemble. Threshold 0.78 is not transferable to v0.2.0. Completed historical experiment. |
| Does other pathological gait produce positive calls? | [Voisard hard-negative report](../reports/VOISARD_NONSTROKE_HARD_NEGATIVE_EVALUATION_2026-09-01.md); `voisard_nonstroke_hard_negative_participant_predictions.csv` | Historical three-channel full-expanded seed-42 prototype. 138 non-stroke participants; 72 positive at 0.50, 43 at 0.78. Same-protocol stress test, not independent-site evidence. |
| Has negative exposure already been tried? | Same Voisard report; `binary_hard_negative_exposure_*` tables and scripts | Historical three-channel experiment. Large dose damaged calibration/BA; small dose missed the required hard-negative gain. Both rejected. |
| Does participant-level pooling fix the overlap? | [MIL report](../reports/PARTICIPANT_MIL_GATE_2026-09-03.md), notebook 32 | Lower-back source-held-out experiments. Both tested candidates rejected. Notebook 31's proposed MIL step is completed, not pending. |
| Are corrected architectures/fusions still pending? | [Corrective benchmark](../reports/CANONICAL_CORRECTIVE_BENCHMARK_2026-09-03.md), notebook 34 | Completed. No replacement admitted; architecture rotation closed. |
| Are demographic limitations known? | `data/processed/demographic_clinical_population_coverage.csv`, `baseline_subgroup_coverage_audit.csv`; demographic reports | Completed coverage work, not proof of age-adjusted stroke specificity. Baseline subgroup script uses historical `repeated_pooled_outer_predictions.csv`; its age join/grouping can drop missing ages, so it is not complete participant accounting. |
| Is final-test credibility already assessed? | [Credibility audit](../reports/TEST_SET_CREDIBILITY_AUDIT_2026-09-03.md), notebook 30 | Completed. Three-source development is not final validation; repeatedly inspected RevalExo is small. |
| Are actual selected weights frozen? | [Freeze report](../reports/LOWER_BACK_RELEASE_FREEZE_2026-09-08.md) | v0.2.0, 15 members, locally trained and CPU/GPU/CLI verified. Completed. These full-development weights are distinct from OOF fold fits. |

## Existing selected-ensemble counts verified

Read the saved notebook-29 participant predictions, selected `ensemble_all`,
checked unique source/participant/seed rows and five seeds per participant,
averaged probabilities across seeds, then applied the existing 0.50 threshold.
Counts matched the saved notebook-30 consensus table exactly:

| Development source | TN | FP | FN | TP |
|---|---:|---:|---:|---:|
| Felius | 26 | 8 | 28 | 101 |
| Sint | 16 | 4 | 1 | 9 |
| Voisard | 57 | 15 | 4 | 45 |
| Total | 99 | 27 | 33 | 155 |

The 27/126 healthy false-positive fraction is 21.4%; the 33/188 stroke
false-negative fraction is 17.6%. These are cross-seed consensus development
counts, not average source/seed errors and not external performance. Do not
mix them with the historical 72/138 non-stroke result.

## Conditional discrimination: completed, not pending

[Executed conditional comparison](../reports/CONDITIONAL_GAIT_COMPARISON_2026-09-09.md):
259-person metadata/features/prediction contract, 36 fits on existing folds and
144-person device/protocol-matched subset. Matched RMS AUROC .801 against healthy
versus .449 against other pathology. Combined features underperform nuisance plus
cadence. This remains reference-assisted within-source evidence.

## Event/cadence adapter: completed, not pending

[Executed measurement validation](../reports/LOWER_BACK_EVENT_VALIDATION_2026-09-09.md):
260 people/1,356 trials, full-prepared-signal and reference-bout modes. Default
mobgap components fail admission; stroke F1 .811 autonomous, .855 in known bouts.
Count-cadence MAE exceeds 5 steps/min in all groups. Three invalid-reference trials
are retained in accounting. Reference events are algorithm-derived, not independent
laboratory truth. Four tests passed. No replacement promoted.

## Native packet correction: completed, specificity failure persists

[Executed correction](../reports/PACKET_ALIGNMENT_CORRECTION_2026-09-09.md):
common acquisition origin, bounded interpolation and counter rollover support.
Provider-processing check passed on 1,348 trials. Regenerated 259-person feature
contract and 36 fixed fits; combined other FPR unchanged at 50.7%. Frozen v0.2.0
89/138 positive before and after on the same 5,340 non-stroke windows, no participant
call changes. Four tests passed. Use aligned native loader for new extraction.
This resolves the pending mixed-cohort implementation RMS question with versioned
results; manuscript-wide impact assessment is separate. Do not rerun this completed
correction. It is not a demonstrated fix for stroke specificity.

## Actual remaining gap

No intervention has demonstrated adequate sensitivity-preserving transfer and
stroke specificity. The new three-class objective is completed and rejected,
not an outstanding proposal. The next candidate needs a different justified
mechanism and disjoint validation; do not reopen completed experiments under new
names. The validity wrapper only removes non-informative/invalid window scores,
with rejected coverage explicit. No independent paired final cohort is accepted.

## Bilateral phase experiment completed

[Executed phase comparison](../reports/BILATERAL_PHASE_COMPARISON_2026-09-09.md):
all 259 selected participants retained across the existing folds, 1,348 trials,
1,345 complete trial feature sets and no missing participant feature sets.
Adding phase features to nuisance+cadence reduces other false positives 73 to 64/138,
but stroke detections fall 43 to 41/49. Matched comparison: other FP 35 to 26/76,
stroke detections 34 to 30/49. Both fail the pre-fit sensitivity-preserving gate.
Secondary combined+phase matched result: other FP 43 to 31/76 with detections
unchanged at 31/49. No promotion. Baseline reproduction and four unit tests passed.
This is completed annotation-assisted development evidence, not sensor-only or
independent validation. No downloads or release changes. Do not rerun this test.
The follow-up [nested threshold experiment](../reports/PHASE_NESTED_THRESHOLD_2026-09-09.md)
is now completed: 72 inner fits, training-only 90% sensitivity thresholds, both
primary gates failed. Primary full: 41/49 stroke detected, 59/138 other FP, versus
baseline 44/49 and 61/138. Matched: 42/49 and 61/76 versus 44/49 and 69/76.
Secondary matched combined+phase detects 45/49 but calls 62/76 other and 13/19
healthy positive. Stop threshold sweeps on this representation. No model admitted.
The completed phase/threshold experiments remain closed. The subsequent
stance-variability feasibility result and current measurement priority are below. Neither stroke diagnosis nor a renamed abnormality score
is validated by these results. Independent cohort and measurement evidence remain
required. Acquisition unchanged, phase preprocessing reused, evaluation complete.

## Roadmap priority 1 completed: stance variability coverage

[Executed feasibility](../reports/STANCE_VARIABILITY_FEASIBILITY_2026-09-09.md):
1,259/1,348 trials have within-side/bout CV, but participant coverage fails the
locked 95% per-group gate: healthy 68/72, ACL 9/11, HOA 13/15. All 49 stroke have
coverage. All participants retained in the ledger, no model fitted. Eight tests
passed across the new CV and existing phase extractor. Do not relax the gate or
rerun this estimator as an untested proposal. Acquisition unchanged, preprocessing
complete, classifier evaluation not run. Latest model results unchanged.
The subsequent directional-axis audit below resolves the nominal mapping.
All 1,348 raw headers have accelerometer/gyro/magnetometer XYZ.
Then consider gyro-assisted measurement validation; OOD remains lower priority.

## Nominal directional axes resolved

[Executed axis audit](../reports/DIRECTIONAL_AXIS_AUDIT_2026-09-09.md): provider
Figure 2 supports lower-back X vertical, Y ML and Z AP. Of 1,294 comparable
raw/processed trials, 750 TechnoConcept flip X/Y signs, 37 retain identity, and
507 XSens retain identity. Filtered signed mappings match to numerical precision.
54 XSens comparisons remain unsupported. Initial-second gravity is X-dominant in
1,347/1,348 trials; CVA_18_2 is Z-dominant. This is a screening flag, not a clinical
exclusion or validated stationary interval. Per-trial anatomical calibration is
not established. The nominal-Y harmonic-ratio experiment is now completed below. Sign inversion does not change HR
amplitudes. No new classifier result. Acquisition unchanged, axis audit complete,
directional HR preprocessing/evaluation completed below. Gyro laterality remains separate.

## Directional harmonic ratio completed

[Executed HR comparison](../reports/ML_HARMONIC_RATIO_2026-09-09.md): all 259
participants have main features, 1,345 usable trials. 72 inner and 24 outer fits,
three tests passed. Primary matched phase+HR: 44/49 stroke, 5/19 healthy FP,
47/76 other FP versus phase baseline 42/49, 13/19, 61/76. Full: 45/49, 6/72,
56/138 versus 41/49, 11/72, 59/138. Useful gains, both locked gates fail: matched
sensitivity below 90%, full other-FPR reduction below 5pp. Quality-screened primary
matched result 42/49, 6/19, 48/76. No promotion or threshold sweep. Acquisition
unchanged, HR preprocessing/evaluation complete. The following conditional gyro experiment is now completed; no specificity fix
is established.

## Conditional gyro laterality completed

[Executed result](../reports/GYRO_LATERALITY_2026-09-09.md): six fresh linear SVC
fits on six gyro feature types, participant/pathology held out, known contact times.
48,131/48,257 contacts usable. Matched participant-macro accuracy: healthy 97.8%,
stroke 89.6%, CIPN 95.9%, PD 96.6%, RIL 88.1%. Full stroke 71.4%, healthy 54.0%.
Gate failed. No event-adapter integration, no post-hoc label flips. Two tests passed.
This is annotation-conditioned agreement, not independent or autonomous measurement
validation. The signed gyro raw/processed check is now complete below; it does not
justify corrective fitting. Device and cohort effects remain entangled. Acquisition unchanged,
gyro preprocessing/conditional evaluation complete, release unchanged.

## Gyro transformation audit complete

[Executed audit](../reports/GYRO_AXIS_TRANSFER_AUDIT_2026-09-09.md): 1,294/1,348
trials comparable. All gyro mappings agree with acceleration mappings. Scale 1,
constant offsets fully explain residuals (max corrected RMSE 2.1e-14), consistent
with documented provider offset subtraction. 54 comparisons unresolved. No new
input correction or retraining justified. Two tests passed, all trial rows retained.
Ten participants with both devices show saved OOF side accuracy 25.9% XSens vs
78.9% TechnoConcept; exploratory transfer evidence, not isolated device causality.
Close this mapping audit. Any new sign/calibration intervention needs independent
frame evidence. OOD remains separately scoped against prior abstention work.
Acquisition unchanged, audit complete, model results unchanged, no running job.

## Physical calibration evidence checks completed

[Executed physical checks](../reports/GYRO_CALIBRATION_EVIDENCE_2026-09-09.md):
all 1,348 trials. Median gravity-projected U-turn integral XSens 3.075,
TechnoConcept 3.068 supports common radians/s scale, not degrees/radians mismatch.
Processed static bias is near zero; 450/507 comparable XSens and all 787
TechnoConcept offsets agree with native first-200-row subtraction. Head/back turn
signs agree in all 1,343 jointly usable trials. These are consistency checks, not
independent absolute heading calibration. All ten paired-device participants use
different sessions; their accuracy gap does not isolate hardware. No rescaling,
label flipping or retraining. Existing physical checks closed. Next prerequisite
is independent known-direction or event-reference availability; do not claim
absolute handedness or reference correctness from these signals alone. Acquisition
unchanged, physical checks complete, independent calibration unresolved.

## Local optical reference intake and exploratory classifier

[Executed TVS intake](../reports/TVS_OPTICAL_REFERENCE_AND_CLASSIFIER_2026-09-09.md):
32 existing participants (17 healthy/15 PD), 225 trial records. Optical event-side
fields and raw markers verified. 163 trials usable, 45 absent optical contacts,
17 partial/invalid. Optical/INDIP agree on side in all 1,584 matched contacts.
Corrected coverage 823/952 healthy, 822/962 PD fails 95% gate. Initial denominator
bug permitted three exploratory laterality fits (87.46% HA, 87.34% PD); preserved
and explicitly not admitted. Fixed accounting, reran intake, no additional fits.
No stroke cohort or new stroke classifier. Acquisition unchanged. Next measurement
task is a separately specified per-contact optical quality policy, retaining
unknown intervals and participant coverage. Voisard calibration remains unresolved.

Historical DUO-GAIT inventory is superseded by the completed magnitude test linked above; directional transfer remains pending.
