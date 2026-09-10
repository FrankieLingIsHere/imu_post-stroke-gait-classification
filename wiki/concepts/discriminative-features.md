---
type: concept
---

Implementation update (2026-09-09):
[packet correction executed](../../reports/PACKET_ALIGNMENT_CORRECTION_2026-09-09.md).
Native clock reconstruction and versioned 259-person RMS comparison are complete;
combined other FPR remains 50.7%. Frozen non-stroke positives remain 89/138 with
zero participant flips. Strict matched predictions remain unchanged. This resolves
the implementation comparison's provisional mixed-cohort RMS status; manuscript
statistics are preserved pending a separate manuscript-wide impact assessment.
Use the new aligned native loader for future extraction. Event truth remains
algorithm-derived, and no clinical specificity improvement is established.


Implementation interpretation (2026-09-09): see [[classification-methodology]].
The group effects and device-matched sensitivity checks below do not establish
cross-pathology classifier specificity or absence of hardware shortcuts. This
clarification does not change manuscript feature statistics.
The [executed conditional comparison](../../reports/CONDITIONAL_GAIT_COMPARISON_2026-09-09.md)
now directly separates these endpoints: matched RMS-model AUROC .801 against
healthy versus .449 against other pathology. This is OOF classifier evidence
on 144 selected participants, not a replacement of manuscript effect sizes.

Which signal features actually separate healthy from post-stroke gait — [[research-questions|RQ1]], answered from two angles: what the literature reports, and what this review's own re-mining of [[voisard-2025]] and [[felius-dataset]] found directly.

## From the literature

Time-domain and frequency-domain features derived from raw accelerometer/gyroscope signals dominate. [[mannini-2016]] combines HMM-derived and time-frequency parameters (90 features total). [[hsu-2018]] compares 17 vs. 192 features across five placements. [[hsu-2021]] reduces 42 time-frequency parameters to 4. [[lee-2018]] reduces 165 parameters to 2–4 via sequential forward search. [[brasiliano-2026]] retains 9 of a larger candidate set via sequential backward selection. Three studies bypass hand-engineered features entirely: [[wang-2021]], [[shin-2022]], and [[lee-2025]] all feed raw six-axis signal directly into a deep neural network.

## From this review's own re-mining

## Current age-by-stroke interaction audit (project development layer, 2026-08-21)

The age question was tested directly rather than inferred from the healthy-versus-CVA age gap. A participant-level model of each feature against age, stroke label and the age-by-stroke interaction found nominally different age slopes for head RMS (p = 0.039) and lower-back RMS (p = 0.049). After Benjamini--Hochberg correction across the six tested features, both interaction q-values were 0.148. Foot RMS, cadence, mean stride time and stride-time variability did not show reliable interactions. The result supports age-stratified auditing and age-complete recruitment, but does not establish a stable age-dependent stroke signature or justify adding age to the classifier. See [[age-and-stroke-gait]] and [legacy_20_age_group_interaction_analysis](../../notebooks/archive/legacy_20_age_group_interaction_analysis.ipynb).

**Current, manuscript-verified numbers (corrected 2026-08-05) — supersedes every effect size below through the "Fifth journal-critic pass" and "Thirteenth/Fourteenth journal-critic pass" entries**, none of which was re-synced to this page after the manuscript's own rounds 16-19 (2026-07-31 to 2026-08-01) or today's round-20 critique-response fixes. This page's history below is kept as the development record, but treat only this box and the three round-20 bullets immediately following it as current truth:

- **Voisard age-adjusted (Section 4.2.2, participant level, 49 CVA/73 HS)**: lower back RMS r = 0.57 [0.41, 0.72] (page below still says 0.54), foot RMS r = 0.72 [0.57, 0.84] (unchanged), head RMS r = 0.31 [0.11, 0.50] (page below still says 0.32), cadence r = 0.42 [0.21, 0.61] (page below still says 0.44), mean stride time r = -0.42 [-0.61, -0.21] (page below still says -0.44), stride-time variability r = -0.18 [-0.38, 0.04], p = .097 — NOT significant under the primary bootstrap test, though a joint OLS robustness check does find it significant (p = .0022), a genuine method-dependent discordance disclosed rather than resolved (page below still states a single r = -0.26 with no discordance noted).
- **Pooled cross-dataset comparison (Section 4.2.6, 181 stroke/107 healthy, not 182/107 — see [[felius-dataset]]'s S001P exclusion)**: trunk RMS r = 0.90 [0.86, 0.95] full pool, or r = 0.95 [0.92, 0.98] n=58 restricted to genuine trunk-channel datasets (page below still says r = 0.88 with no trunk-only figure). Cadence r = 0.57 [0.45, 0.69], mean stride time r = -0.56 [-0.68, -0.44]. Harmonic ratio r = 0.18 [0.03, 0.34], p = .014 — **significant** (page below still says r = 0.09 or 0.11, not significant — this is the single largest remaining error on this page, since it states the opposite significance verdict from the current manuscript). Sample entropy r = -0.04 [-0.17, 0.10], not significant pooled, but Voisard-alone vs. pooled healthy IS significant (r = -0.88) while Felius-alone is significant in the opposite direction (r = 0.27) — a real sign-cancellation, not a uniform null (page below states sample entropy as "cleanly non-significant everywhere," missing this per-dataset split). Stride-time variability: five-dataset pool null (r = -0.01, p = .91) is an OxWalk-estimator artifact; four-dataset OxWalk-excluded estimate r = -0.65 [-0.78, -0.50], p = 1.2e-13, treated as the more valid figure (page below's r = -0.03/"resolved as a null" is now itself superseded — round 18 found that reading was the OxWalk artifact, not a genuine null).
- Full current-numbers narrative and provenance in [[classification-methods]]'s own matching correction box.

- **The "age confound" was itself a bug, corrected 2026-07-31 (thirteenth `journal-critic` pass).** Every earlier version of this page reported that [[voisard-2025]]'s raw cadence comparison implied stroke participants walk *faster* than healthy controls, traced that to a ~21-year unmatched age gap, and reported cadence as not significant after age-adjustment (p = .315). Direct re-derivation against the extraction code found the real cause: this review's own cadence denominator divided event counts by the recording's full length minus only the u-turn, silently counting idle recording time before and after the labeled walk as walking time, and doing so more severely for faster walkers. That artifact both manufactured the apparent raw reversal and suppressed the age-adjusted effect. Fixed at the source (`src/features/voisard.py`) and re-derived from the actual span of labeled gait events: cadence is not an age artifact. It survives age-adjustment robustly (r = 0.44) and is no longer treated as a narrower, confound-limited finding than trunk RMS or mean stride time.
- **A second, independent bug was found and fixed the same round**: stride-time mean and CV were computed by diffing all surviving gait-event timestamps sorted together, which spliced one artificial, multi-second "stride" spanning the entire u-turn into the mean and CV of every trial with a turn. This inflated stride-time-CV to implausible values (0.30-0.69 on a 10 m walk) and inflated mean stride time more for stroke trials (slower turns) than healthy ones. Fixed by computing diffs within the pre-turn and post-turn segments separately.
- **What survives age-adjustment, corrected values, refreshed 2026-07-31 (14th pass)**: lower back RMS (r = 0.54), foot RMS (r = 0.72), head RMS (r = 0.32), cadence (r = 0.44), mean stride time (r = -0.44), and stride-time variability (r = -0.26) all remain significant after age-adjustment, each with a bootstrap 95% CI, and each in the clinically expected direction — see [[classification-methods]] for the full table. The RMS figures moved slightly this pass: a 14th `journal-critic` review found that round 13's cadence-denominator fix was never extended to RMS/sample entropy/harmonic ratio/Poincare SD1, which were still reading the whole raw file, idle padding included — fixed by restricting all of them to the same straight-walking span cadence already uses. A stricter joint age-and-group OLS model, checked as a robustness test, gives the same qualitative pattern for every feature. **Sign convention**: positive rank-biserial r means the stroke group's value is *lower* than the healthy group's, negative means it's *higher*.
- **A real hardware confound, checked directly, 2026-07-31**: Voisard's CVA cohort is recorded 100% on one accelerometer platform (TechnoConcept), while its HS cohort mixes that platform with a second (XSens) at roughly 27/73. Within HS alone, device is a real age-adjusted predictor of lower-back RMS (r = -0.39, p < .0001). A device-matched sensitivity check (TechnoConcept-only both arms) found every affected effect size held or strengthened relative to the mixed comparison — the confound is real but does not appear to be producing the reported findings. This check was computed in an earlier pass but never actually written into the manuscript until this one — a gap a 14th `journal-critic` review caught by grepping the manuscript text directly.
- **A hardware confound was also checked directly, not just theorized, 2026-07-31**: [[voisard-2025]]'s CVA cohort is recorded 100% on one accelerometer platform (TechnoConcept), while its HS cohort is a 73%/27% mix of two platforms (XSens/TechnoConcept). A device-matched sensitivity check (TechnoConcept-only CVA vs. TechnoConcept-only HS) found every effect size held or strengthened relative to the full mixed-device comparison, evidence the confound is real but not what's driving the reported group differences.
- **A second confound**, gender, discovered independently within [[voisard-2025]]'s HS group: real on cadence and both stride-time measures even after age-adjustment, but the two accelerometer-RMS gender effects turn out to be age artifacts. This gender effect was never incorporated into the primary CVA-vs-HS age adjustment above, a disclosed limitation on how completely age was isolated as the only confound.
- **Cadence and mean stride time's correlation is now much tighter than previously reported, corrected 2026-07-31**: with the denominator bug above fixed, [[voisard-2025]]'s own cadence and stride time now correlate at Pearson r ≈ -0.96 (participant level), not the r ≈ -0.60 an earlier round reported (itself downstream of the same bug), and are close enough to [[felius-dataset]]'s exact algebraic identity (product = 120 for every trial) that this review no longer treats Voisard as offering meaningfully independent-measurement evidence beyond what Felius already provides. The pooled Voisard+Felius correlation is likewise r ≈ -0.96, not the r ≈ -0.80 previously reported.
- **Trunk-channel-only recomputation, added 2026-08-05**: the pooled trunk RMS figure (manuscript's current r = 0.90, n = 181 stroke/107 healthy, superseding this page's stale r = 0.88 entry below) pools two substitute channels (OxWalk's hip sensor, GaitMotion's foot sensor) alongside three genuine trunk-region sensors (DUO-GAIT sacral, MAREA waist, Camargo trunk). Restricted to only the three genuine-trunk-channel healthy-reference datasets, the same participant-level test gives r = 0.95, 95% CI [0.92, 0.98], n = 58 healthy — reproduced directly against the codebase (`cross_dataset.build_healthy_reference_table()` filtered to `dataset.isin(["DUO-GAIT","MAREA","Camargo"])`) and now a live notebook cell, not only an assertion. Manuscript now reports both figures side by side rather than disclosing the trunk-only estimate as uncomputed.
- **Pooled cross-dataset comparison could not be age-adjusted, explicit disclosure added 2026-08-05**: none of the five healthy-reference datasets ships participant-level demographics, so every pooled effect size (trunk RMS, cadence, mean stride time, etc.) should be read as a combined pathology-and-age separation bound, not a pathology-isolated effect, unlike [[voisard-2025]]'s own age-residualized within-study test.
- **Scoped deployment caution added 2026-08-05**: the manuscript's Conclusion now states directly that Poincare SD1 and sample entropy specifically should not be relied on for cross-platform clinical deployment until sensor-axis orientation and sampling rate are calibrated across target hardware — a caution that explicitly does not extend to harmonic ratio or trunk RMS/cadence/mean stride time, which generalize consistently.
- **A genuine, unresolved disagreement**: sample entropy and Poincare SD1 disagree in *direction* between [[voisard-2025]] and [[felius-dataset]] — not smoothed over, reported as open. Three explanations are plausible (hardware/mounting/protocol, orientation-invariant magnitude computation, or a real clinical difference between the two stroke cohorts) and none can be confirmed or ruled out, since [[felius-dataset]]'s public release has no participant-level clinical data to check the third against.
- Foot RMS ranks highest of nine literature-informed candidate features by SNR, ahead of lower-back RMS, sample entropy, and every other spatiotemporal feature, corrected 2026-07-30 to include the foot channel in this ranking.
- **Cross-dataset validation against a pooled independent healthy reference, substantially strengthened 2026-07-31 (14th `journal-critic` pass, two more code bugs found and fixed)**: on top of round 13's fixes, this pass found (a) RMS/sample entropy/harmonic ratio/Poincare SD1 for Voisard were still reading the whole raw file rather than the walking-only span cadence already used, and (b) OxWalk's own lower-back RMS was computed over its entire free-living day-long recording rather than the "active walking bouts" its own module already restricts cadence and step-time CV to — confirmed directly: only ~13% of a sample OxWalk file falls inside an active bout. Both fixed. The result: **trunk RMS jumps from r = 0.59 to r = 0.88** [0.82, 0.92] and now separates the pooled stroke group from every one of the five individual healthy-reference datasets significantly, OxWalk included — OxWalk was previously the one dataset trunk RMS failed against, and that failure was the bug, not a real hip-vs-trunk placement effect as an earlier round had theorized. **Sample entropy flips from spuriously significant to cleanly non-significant everywhere** (pooled r = -0.04, CI crosses zero, both Voisard-alone and Felius-alone against the pool also null), finally resolving a direct self-contradiction an earlier pass had left standing between two adjacent manuscript paragraphs. Cadence (r = 0.47) and mean stride time (r = -0.45) generalize as before, each with a bootstrap 95% CI, each holding direction against Voisard and Felius checked separately. Harmonic ratio remains **not significant** (r = 0.09, CI crosses zero) with a genuine cross-dataset direction disagreement (positive against Camargo/DUO-GAIT/MAREA, negative against OxWalk). Stride-time variability remains nominally significant (r = 0.48) but is reported as **unresolved rather than confirmed**, and is now explicitly flagged as **sign-reversed** relative to both real within-study effects (Voisard -0.26, Felius -0.77) — not just "unreliable," but pointing the wrong way. The pooled healthy reference mixes three incompatible stride-time-CV estimators (corrected from an earlier pass's miscount of "two... four of five"): Voisard's own event-based calculation, a windowed-autocorrelation estimator for Felius and three of five healthy datasets (DUO-GAIT, MAREA, Camargo), and a step-time CV for a fourth (OxWalk), with the fifth (GaitMotion) computing nothing. Even restricted to the estimator-matched subset the effect weakens sharply (r = 0.18, p = .046) while DUO-GAIT returns a median 6-10x any of the others using the identical method — an inconsistency not resolved this round. Per-dataset trunk-RMS medians are now disclosed directly in the manuscript (DUO-GAIT 1.03g, MAREA 1.12g, Camargo 1.25g, OxWalk 1.06g, GaitMotion 1.30g foot-substitute, vs. pooled stroke 1.02g), honestly flagging the residual ~0.22g spread between the three genuine trunk-channel datasets as real and larger than ideal for one pooled estimate, rather than smoothed away. Full breakdown in [[classification-methods]].
- **Per-dataset sensitivity check**: trunk RMS shows no significant difference against OxWalk alone (the largest single healthy-reference dataset, consistent with OxWalk's hip-substitute channel), and cadence/mean stride time show no significant difference against DUO-GAIT alone, though both remain significant against the other four datasets individually. Harmonic ratio's post-fix direction disagreement against OxWalk specifically is new this round. Excluding GaitMotion's Normal-gait condition entirely from the pool leaves every effect size and significance level materially unchanged.
- **Per-stroke-dataset decisive check, refreshed 2026-07-31**: trunk RMS, cadence, and mean stride time each hold the same direction in both the Voisard-alone and Felius-alone comparisons as in that dataset's own within-study result — cadence included now that its extraction bug is fixed, no longer the "partial exception" earlier rounds reported. Sample entropy does not hold up here either now (both Voisard-alone and Felius-alone against the pool are non-significant, consistent with its within-Felius null). Harmonic ratio does not: it holds a real effect for Voisard alone but shows essentially no effect for Felius alone (133 of the pool's 182 stroke participants), so its pooled significance more likely reflects Voisard's own contribution plus the imperfectly-matched healthy-reference computation than a corroborated pathology signal. **Trunk RMS, cadence, and mean stride time are the three features this review treats as credibly generalizing evidence from this pooled check** — sample entropy no longer among them after the windowing fix above.
- **DUO-GAIT's own harmonic-ambiguity bug found and fixed, same day**: self-investigation of round 14's own "DUO-GAIT stride-time-CV anomaly, disclosed but not diagnosed" open item found a real fourth code bug — DUO-GAIT's sacral placement on symmetric healthy gait produces two comparably strong autocorrelation peaks (step period and stride period, exactly double), and the frequency detector locked onto whichever was marginally stronger per trial, confirmed directly against several subjects' own autocorrelation arrays. Fixed with an opt-in disambiguation step (default off, every other dataset unaffected). Cadence and mean stride time strengthen further (r = 0.57, r = -0.55) and now hold against every individual healthy dataset with **no exception at all**. **Stride-time variability is now resolved, not merely disclosed as unresolved**: restricted to only the datasets sharing Voisard's/Felius's own windowed-autocorrelation estimator, the effect vanishes entirely (r = -0.03, p = .76) — the full pool's nominal significance traces cleanly to OxWalk's own differently-defined step-time CV (4-5x every other dataset's value), not a real stroke-versus-healthy signal. Full detail in [[classification-methods]].

## Links

Feeds directly into [[sensor-placement]] (lower back carries the discriminative signal) and [[classification-methods]] (which features feed which classifiers).


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
