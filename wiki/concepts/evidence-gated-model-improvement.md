---
type: concept
status: active
updated: 2026-09-09
---

# Evidence-gated model improvement

Latest: [native alignment correction](../../reports/PACKET_ALIGNMENT_CORRECTION_2026-09-09.md)
completed; frozen non-stroke positives remain 89/138, zero changed calls. This
preprocessing correction is retained but not a specificity fix. No next diagnostic
candidate is admitted. See [[classification-project-status]].

Previous: [conditional gait comparison](../../reports/CONDITIONAL_GAIT_COMPARISON_2026-09-09.md)
completed 36 feature/covariate fits; no replacement admitted. Device/protocol-matched
RMS separates stroke from healthy better than stroke from other disorders. The measurement adapter is now evaluated and rejected; the packet-timeline
correction is now completed as recorded in [[classification-methodology]].

Previous implementation decision: [differential experiment](../../reports/DIFFERENTIAL_GAIT_IMPLEMENTATION_2026-09-09.md)
completed 27 GPU fits and failed all three seed gates. Other-pathology FPR fell
but stroke sensitivity dropped by 19.05 percentage points versus the matched
primary control. No model promotion. The separate input-validity wrapper rejects
constant/nonfinite windows with no score; it is not a moving-gait specificity fix.
Use [[classification-project-status]] as the current continuation, with the
older sections below retaining completed evidence rather than pending tasks.


Current completion update (2026-09-09): [full cohort results](../../reports/TVS_COHORT_RESULT_2026-09-09.md).
All 30 additional files acquired; 36 raw participants local in total. All 40
registered people accounted for: 34 evaluated on 117 windows, five metadata
exclusions and one short-bout exclusion. Positive calls: 17/18 healthy and 16/16
PD overall; 14/15 healthy and 14/14 PD among newly opened people. Verification
passed; no process remains running. Cohort acquisition/scoring is complete,
not pending. Earlier launch descriptions below are historical. No model
improvement or validated correction is claimed.


Current implementation and acquisition handoff: [[classification-project-status]]. TVS progress and exact download counts: [[mobilise-d-tvs]]. The development results below remain historical evidence, not new TVS performance estimates.

The 2026-09-03 development experiment improves the primary lower-back
acceleration classifier through complementary model errors rather than a blind
replacement of the established ERM baseline. The evidence sources are executed
notebooks `29_evidence_gated_source_only_domain_generalization.ipynb` and
`30_fp_fn_and_test_set_credibility_audit.ipynb`. The complete decisions are in
`../../reports/MODEL_IMPROVEMENT_GATE_2026-09-03.md` and
`../../reports/TEST_SET_CREDIBILITY_AUDIT_2026-09-03.md`.

## Locked development protocol

The experiment used 22,506 real windows from 314 Felius, Voisard, and
[[sint-maartenskliniek]] participants. Every outer fold excluded one complete
source. Epoch selection used participant-disjoint validation inside the two
remaining sources. Five seeds were evaluated at participant level. RevalExo
and NONAN were not loaded.

The matched candidates were ERM, Deep CORAL, and an explicitly labelled
ERM++-style optimization recipe. Neither standalone replacement passed the
predefined gate. A transparent secondary audit then tested fixed equal-weight
probability ensembles from matched out-of-source predictions.

## Result

The ERM + CORAL + ERM++-style lower-back ensemble improved mean AUROC from
0.8737 to 0.8882, Brier score from 0.1664 to 0.1425, balanced accuracy from
0.7834 to 0.8140, and specificity from 0.7145 to 0.7743. Mean sensitivity was
preserved at 0.8537 versus 0.8523. Its paired balanced-accuracy gain was 0.0306
with a 95% bootstrap interval of 0.0038 to 0.0636. The ensemble passed the
predefined non-inferiority and material-gain conditions.

A secondary three-channel confirmation selected ERM + ERM++-style and reached
mean AUROC 0.9025 and balanced accuracy 0.8055. It did not overturn the
lower-back-first decision because the lower-back ensemble retained higher
balanced accuracy and sensitivity with a simpler sensor contract. This updates
the stale historical interpretation that three channels must remain primary.

## Error burden and test-set credibility

Cross-seed consensus on the out-of-source development predictions produced 99
TN, 27 FP, 33 FN, and 155 TP. Felius accounts for 28 of the 33 FN, while
Voisard accounts for 15 of the 27 FP. Pooled diagnostic specificity is 78.6%
(95% Wilson CI 70.6% to 84.8%) and sensitivity is 82.4% (76.4% to 87.2%).
These are not independent final-test estimates because all three sources
influenced model selection.

The existing 7-healthy/10-stroke paired external cohort is too small for a
precise clinical claim. Using the development rates only as planning values, a
95% Wilson interval no wider than ten percentage points requires approximately
257 independent healthy/non-stroke and 222 independent stroke participants.
This is a planning calculation, not a universal regulatory requirement.

## Completed development decisions

Notebook 31 established that threshold tuning cannot jointly remove FP and FN:
the minimum development-consensus error is 58 participants, zero FP requires
157 FN, and zero FN requires 87 FP. A matched MiniROCKET plus deep-ensemble
fusion was also rejected after increasing mean total errors by 19.0%, including
both FP and FN increases. See
`../../reports/SCORE_OVERLAP_AND_HETEROGENEOUS_RESCUE_2026-09-03.md`.

Participant-level multiple-instance learning was tested in executed notebook
32. Mean pooling reduced mean source/seed errors only from 21.73 to 21.33
(1.8%), with FP unchanged at 9.80 and FN down from 11.93 to 11.53, but balanced
accuracy fell from 0.8140 to 0.7691 and AUROC from 0.8882 to 0.8442. The paired
balanced-accuracy delta was -0.0449 (95% bootstrap interval -0.0649 to
-0.0247). Gated attention increased errors to 23.33 and was less stable. Both
candidates were rejected. This shows that copying participant labels onto
windows is not the sole cause of the score overlap. See
`../../reports/PARTICIPANT_MIL_GATE_2026-09-03.md`.

The lower-back deep ensemble is now frozen as the selected development model.
Further architecture or threshold selection on the same 314 people risks
adaptive overfitting. New untouched, paired lower-back IMU participants with
healthy, stroke, and clinically relevant non-stroke gait variation are the
limiting requirement for a credible reduction in both FP and FN.

The one narrowly defined correction from [[prior-method-code-alignment]] is now
complete in notebook 34. InceptionTime canonical mechanics increased mean
source/seed errors to 32.13 and canonical 10k MiniROCKET increased them to
23.27, versus 21.73 for the incumbent. The closest fixed
incumbent/MiniROCKET fusion reached 22.13: it reduced mean FP by 0.47 but added
0.87 FN and regressed Felius and Sint despite helping Voisard. No candidate
passed the locked gate. Architecture rotation on these 314 participants is
closed; see `../../reports/CANONICAL_CORRECTIVE_BENCHMARK_2026-09-03.md`.

The exact members, equal averaging and training duration are now frozen in
v0.2.0. Before final external evaluation, lock cohort-specific preprocessing,
threshold, calibration and abstention decisions. The final test must use
previously unseen participants from independent sites, include demographic and
stroke-severity breadth plus non-stroke gait confounders, and report TP/FP/FN/TN
with confidence intervals by site and predefined subgroup. No external
retuning is allowed.

## Local weight freeze completed 2026-09-08

The earlier frozen selection decision now has a concrete local artifact:
`stroke-gait-lower-back-ensemble-v0.2.0`, 15 members trained for eight epochs
each on the established 314 development participants. Nine contract tests and
CPU/GPU/CLI equivalence checks on 96 development windows passed. No external
cohort was loaded. This does not update held-out performance estimates or lock
the final-test threshold/calibration/abstention protocol. See
`../../reports/LOWER_BACK_RELEASE_FREEZE_2026-09-08.md` for duplicate-work checks,
checksum, precision correction and verification details.

## Related decisions

The subsequent [locked TVS pilot](../../reports/TVS_LOCKED_PILOT_2026-09-08.md)
is new execution, not a repeat of the exact-weight Voisard audit. It adds four
selected raw-file acquisitions with frozen decisions and explicit exclusions.
Both new healthy slow-walking bouts are too short for the five-second contract,
so this pilot cannot establish healthy specificity. PD/1001 was also too short;
PD/1000 alone was evaluated and scored positive at 0.887380. All four acquisitions
completed. The separate offline task-duration screen is feasibility
work only. Neither activity changes the selected model or demonstrates fewer
false positives. Current continuation is maintained in [[classification-project-status]].

This decision implements [[evidence-gate-cross-dataset-imu]], preserves the
minimal-sensor direction in [[sensor-placement]], and should govern subsequent
work in [[classification-methods]] and [[future-directions]].


## Exact-weight specificity stress result (2026-09-08)

Frozen v0.2.0 produced 89/138 non-stroke positive calls at 0.50 (64.5%, 95% Wilson CI 56.2 to 72.0%) on the previously inspected Voisard cohort. Historical three-channel positive count was 72/138. No threshold or model change followed. This closes the exact-weight audit gap but confirms substantial differential-specificity limitations. No independent-validation or sensitivity claim is supported. See `../../reports/LOWER_BACK_NONSTROKE_STRESS_2026-09-08.md`. The role-specific provider gate is implemented. The subsequent pooling diagnosis still leaves 87/138 positive calls and does not resolve specificity. TVS acquisition/evaluation and the differential-objective experiment are complete; use [[classification-project-status]] for the current decision.


## Hallway transfer probe completed (2026-09-08)

The [hallway probe](../../reports/TVS_HALLWAY_PROBE_2026-09-08.md) reused four
inspected pilot people with a separate fixed protocol, excluding schema samples.
All four had valid windows; 2/2 healthy and 2/2 PD were positive at 0.50. Neither
reference system supplies turning information; possible turns were retained.
The failure is not confined to pathological gait, but its cause is unproven.
The input-transfer check is complete without a tested mismatch, and the later
three-class candidate was rejected. Domain generalization remains unresolved. These people cannot become an untouched
test for a subsequent correction. No additional download or clinical claim.


## Input-transfer check and cohort-wide continuation

The [new check and batch](../../reports/TVS_INPUT_TRANSFER_AND_COHORT_2026-09-08.md)
verified raw magnitude reconstruction, 100 Hz timebase, g units and exact frozen
training normalization constants. No tested mismatch or corrective transformation
was identified. The user authorized a full HA/PD registered-cohort queue: 40
accounted for, 35 metadata-eligible, five explicit exclusions, 30 new raw members
plus five reused eligible files. Results separate new and previously inspected
participants. This expands evaluation; it does not establish model improvement.


## Positive-call mechanism diagnosis completed

The [controlled diagnosis](../../reports/TVS_POSITIVE_CALL_MECHANISM_2026-09-08.md)
used only four inspected TVS people and 24 development controls. No new cohort
participant was used. All 15 members called both healthy TVS people positive;
actual training batches had 32 healthy and 32 stroke windows per source. Final
head bias alone was small relative to healthy feature-logit contributions.
Offset/amplitude/filter probes did not remove either healthy false positive.
Temporal shuffling drove scores near zero, while constant signals produced high
positive scores. These demonstrate temporal-pattern dependence and a non-walking
failure mode, not a proven clinical cause of the real hallway errors. No model,
threshold, filter or normalization change was promoted. The cohort and subsequent differential-objective experiment are complete;
use [[classification-project-status]] for the current decision. Do not repeat
this diagnosis or tune on the four inspected people.
