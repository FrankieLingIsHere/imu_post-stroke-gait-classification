---
type: concept
status: active
updated: 2026-09-03
---

# Evidence-gated model improvement

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

## Next action

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

Before final external evaluation, freeze the exact members, equal averaging,
preprocessing, training durations, and threshold. The final test must use
previously unseen participants from independent sites, include demographic and
stroke-severity breadth plus non-stroke gait confounders, and report TP/FP/FN/TN
with confidence intervals by site and predefined subgroup. No external
retuning is allowed.

## Links

This decision implements [[evidence-gate-cross-dataset-imu]], preserves the
minimal-sensor direction in [[sensor-placement]], and should govern subsequent
work in [[classification-methods]] and [[future-directions]].
