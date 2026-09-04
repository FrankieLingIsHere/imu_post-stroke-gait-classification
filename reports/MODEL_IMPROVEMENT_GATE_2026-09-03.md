# Evidence-gated model improvement result

Date: 2026-09-03

## Decision

Admit a fixed equal-probability ensemble of ERM, Deep CORAL, and ERM++-style
models as the new **development-selected lower-back acceleration candidate**.
Keep lower-back acceleration magnitude as the primary research input. Do not
claim external or clinical validation from this experiment.

The ensemble decision is based only on out-of-source predictions from Felius,
Voisard, and Sint Maartenskliniek. RevalExo and NONAN were not loaded for
training, tuning, threshold selection, or acceptance.

## Development protocol

- Input: one 500-sample lower-back acceleration-magnitude channel.
- Data: 22,506 real windows from 314 participants across three sources.
- Outer evaluation: leave one complete source out.
- Inner tuning: participant-disjoint 20% split within the two training sources.
- Repetitions: seeds 42, 137, 202, 314, and 515.
- Batch construction: equal source and class contribution.
- Metrics: participant-level AUROC, Brier score, balanced accuracy,
  specificity, sensitivity, FP, FN, and paired 10,000-draw bootstrap intervals.
- Base candidates: matched ERM control, released mean-plus-covariance CORAL,
  and ERM++-style head warm-up plus simple moving average.
- Rescue audit: deterministic equal-probability ensembles formed only from
  matched out-of-source participant predictions.

## Primary lower-back result

| Configuration | Mean AUROC | Mean Brier | Mean balanced accuracy | Mean specificity | Mean sensitivity | Worst-source AUROC | Worst-source balanced accuracy |
|---|---:|---:|---:|---:|---:|---:|---:|
| ERM control | 0.8737 | 0.1664 | 0.7834 | 0.7145 | 0.8523 | 0.8552 | 0.7594 |
| ERM + CORAL + ERM++-style ensemble | **0.8882** | **0.1425** | **0.8140** | **0.7743** | **0.8537** | **0.8588** | **0.7637** |

Paired ensemble-minus-ERM effects across the 15 source-seed units were:

| Metric | Mean delta | 95% paired bootstrap interval |
|---|---:|---:|
| Balanced accuracy | +0.0306 | +0.0038 to +0.0636 |
| Specificity | +0.0599 | -0.0014 to +0.1324 |
| Sensitivity | +0.0014 | -0.0225 to +0.0274 |
| AUROC | +0.0146 | +0.0011 to +0.0318 |
| Brier score | -0.0239 | -0.0493 to -0.0018 |

The fixed ensemble passed every predefined non-inferiority condition and the
material-gain condition. Standalone CORAL and ERM++-style replacements did not
pass. The admitted gain comes from complementary errors, not a claim that one
domain-generalization method is universally better than ERM.

## Three-channel confirmation

The same protocol was repeated using lower-back, left-foot, and right-foot
acceleration magnitudes. Its accepted ERM plus ERM++-style ensemble achieved
mean AUROC 0.9025, Brier 0.1474, balanced accuracy 0.8055, specificity 0.8379,
and sensitivity 0.7732. It improves its own three-channel ERM control but does
not displace the lower-back direction. The lower-back ensemble has higher mean
balanced accuracy (0.8140 versus 0.8055) and sensitivity (0.8537 versus
0.7732) with a simpler one-sensor contract. Three channels remain a secondary
performance/specificity ablation.

## Error and test-set consequence

Notebook 30 shows that the seed-consensus out-of-source confusion counts are:

| Held-out source | TN | FP | FN | TP |
|---|---:|---:|---:|---:|
| Felius | 26 | 8 | 28 | 101 |
| Sint Maartenskliniek | 16 | 4 | 1 | 9 |
| Voisard | 57 | 15 | 4 | 45 |
| Pooled diagnostic view | 99 | 27 | 33 | 155 |

The pooled diagnostic specificity is 78.6% (95% Wilson CI 70.6% to 84.8%) and
sensitivity is 82.4% (76.4% to 87.2%). These are diagnostic summaries, not an
independent test result, because every development source influenced model
selection. Felius contributes the largest FN burden, while Voisard contributes
the largest FP count.

## Interpretation and next lock

This experiment improves the research baseline while preserving the original
lower-back research question. It does not solve cohort size or differential
diagnosis. The next irreversible step is to package the exact ensemble recipe,
fit it on all development data using only development-selected durations, and
evaluate it once under a newly documented frozen external protocol without
retuning. Full test-set requirements are in
`TEST_SET_CREDIBILITY_AUDIT_2026-09-03.md`.

## Evidence artefacts

- `notebooks/29_evidence_gated_source_only_domain_generalization.ipynb`
- `notebooks/30_fp_fn_and_test_set_credibility_audit.ipynb`
- `src/models/evidence_gated_domain_generalization.py`
- `data/processed/evidence_gated_lower_back_dg_decision.json`
- `data/processed/evidence_gated_lower_back_dg_metrics.csv`
- `data/processed/evidence_gated_lower_back_dg_participant_predictions.csv`
- `reports/lower_back_ensemble_fp_fn_confusion.png`

