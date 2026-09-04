# Participant-level MIL gate — 2026-09-03

## Question

Can participant-level learning reduce both false positives and false negatives by avoiding the weak assumption that every five-second gait window independently carries the participant's diagnosis?

## Locked protocol

- Primary input: lower-back acceleration magnitude only.
- Development data: 314 participants and 22,506 windows from Felius, Voisard, and Sint Maartenskliniek.
- Outer evaluation: one complete source held out at a time.
- Epoch selection: participant-disjoint validation inside the remaining sources.
- Repeats: seeds 42, 137, 202, 314, and 515.
- Training batches: equal participant draws from every available source/class cell; one binary loss per participant bag.
- Candidates: mean pooling and gated-attention pooling over convolutional window embeddings.
- Evaluation: every real window for a held-out participant contributes to one participant probability.
- RevalExo and NONAN signals were not loaded.

## Development result

Metrics below average the 15 matched source/seed evaluations. Error counts therefore represent mean errors per held-out-source evaluation, not one pooled clinical test.

| Method | AUROC | Brier | Balanced accuracy | Specificity | Sensitivity | Mean FP | Mean FN | Mean total errors |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Selected deep ensemble | 0.8882 | 0.1425 | 0.8140 | 0.7743 | 0.8537 | 9.80 | 11.93 | 21.73 |
| Participant mean pooling | 0.8442 | 0.1577 | 0.7691 | 0.7560 | 0.7822 | 9.80 | 11.53 | 21.33 |
| Participant gated attention | 0.8043 | 0.2030 | 0.7528 | 0.6919 | 0.8137 | 11.00 | 12.33 | 23.33 |

Mean pooling reduced total errors by only 1.8%, below the predeclared 10% requirement. Although mean FP did not increase and mean FN fell by 0.40, balanced accuracy changed by -0.0449 (95% paired bootstrap interval -0.0649 to -0.0247), AUROC by -0.0440 (-0.0653 to -0.0236), and Brier by +0.0152 (-0.0072 to +0.0379). It therefore failed non-inferiority.

Gated attention increased total errors by 7.4%, increased both mean FP and mean FN, and had a balanced-accuracy delta of -0.0612 (-0.1000 to -0.0265). It failed both the safety and performance gates.

## Why the small error-count change is not enough

The source-specific trade changed substantially. Mean pooling reduced Felius FN from 30.6 to 18.0, but increased Felius FP from 8.0 to 12.0. On Voisard it reduced FP from 17.4 to 13.6 but increased FN from 4.0 to 14.4. This is source-dependent error exchange rather than robust separation of stroke from healthy gait.

The attention model was also seed-unstable. For example, held-out Sint false positives ranged from 4 to 16 across the five seeds. Attention weights therefore do not provide a stable clinical aggregation mechanism on the present participant count.

## Decision

Reject both MIL candidates and retain the lower-back ERM + CORAL + ERM++-style equal-probability ensemble selected in notebook 29. The experiment supports the conclusion that the remaining FP/FN burden is not explained solely by window-level weak labels.

Further model selection on these same 314 participants now carries a substantial adaptive-overfitting risk. The next defensible action is to freeze the incumbent recipe and prioritize a materially larger, untouched, paired lower-back IMU cohort containing healthy controls, stroke participants, and relevant non-stroke gait confounders. Near-zero FP and FN cannot be claimed from the current overlapping development distributions or the existing 17-person paired external set.

## Evidence files

- Executed notebook: `../notebooks/32_participant_level_attention_mil.ipynb`
- Implementation: `../src/models/participant_attention_mil.py`
- Decision: `../data/processed/participant_mil_decision.json`
- Metrics: `../data/processed/participant_mil_metrics.csv`
- Predictions: `../data/processed/participant_mil_predictions.csv`
- Inner tuning: `../data/processed/participant_mil_tuning.csv`

