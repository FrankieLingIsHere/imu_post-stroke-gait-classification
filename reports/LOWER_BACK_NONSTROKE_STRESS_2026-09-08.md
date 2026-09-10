# Frozen lower-back ensemble: non-stroke stress test

Completed 2026-09-08 under the [predeclared protocol](../docs/LOWER_BACK_NONSTROKE_STRESS_PROTOCOL_2026-09-08.md).
This closes the exact-weight measurement gap identified in the evidence map.

The v0.2.0 ensemble assigned a positive stroke score at the descriptive 0.50
threshold to **89/138 non-stroke participants (64.5%, 95% Wilson CI 56.2–72.0%)**.
Thus, non-stroke specificity on this inspected cohort was 49/138 (35.5%).
The frozen research model does not demonstrate adequate differential stroke
specificity at this reference operating point. No threshold or model was changed.

| Pathology group | Positive / total | Positive-call rate | 95% Wilson interval | Historical three-channel positive count |
|---|---:|---:|---:|---:|
| ACL | 6/11 | 54.5% | 28.0–78.7% | 4/11 |
| CIPN | 11/19 | 57.9% | 36.3–76.9% | 10/19 |
| HOA | 9/15 | 60.0% | 35.7–80.2% | 4/15 |
| KOA | 12/18 | 66.7% | 43.7–83.7% | 7/18 |
| PD | 15/24 | 62.5% | 42.7–78.8% | 15/24 |
| RIL | 36/51 | 70.6% | 57.0–81.3% | 32/51 |
| Pooled | **89/138** | **64.5%** | **56.2–72.0%** | **72/138** |

ACL: anterior cruciate ligament injury; CIPN: chemotherapy-induced peripheral
neuropathy; HOA/KOA: hip/knee osteoarthritis; PD: Parkinson disease;
RIL: radiation-induced leukoencephalopathy. These participants are not healthy
controls. Positive calls are false positives relative to their non-stroke labels.

The current model made 17 more positive calls than the historical three-channel
prototype on matched participants at 0.50. This is a descriptive comparison of
different fitted models and input contracts. It cannot isolate the effect of
sensor count, establish overall superiority, or justify switching the incumbent.
This cohort has no stroke cases, so sensitivity, stroke AUROC and the complete
FP/FN trade-off cannot be estimated here.

## Accounting and integrity

- Same 138 participant identities, pathology assignments and 5,340 windows as
  the historical evaluation, checked before inference.
- 868 trial records: 866 included, two lacked qualifying five-second walking
  spans. All historical trial identities, window counts and statuses matched.
- All 138 participants scored; no participant inference failures or abstentions.
  One participant has missing age. No outcome-based exclusions.
- No participant-key overlap with the saved full-development freeze manifest;
  its hash matched the release manifest. This cannot detect undisclosed aliases.
- Existing raw-signal adapter reused with channel zero only. Member normalization
  remains checkpoint-fixed; participant score is mean window probability.
- Saved aggregation independently recomputed. All Wilson intervals matched
  SciPy's independent implementation. No training, calibration or threshold search.

## Limits and decision

This is same-protocol Voisard evidence, not an independent-site test. The cohort
was previously inspected and used in historical exposure experiments. The
intervals quantify participant-level binomial uncertainty, not uncertainty from
site selection, prior experimentation or incomplete clinical labels.

The false-positive limitation is now measured for the exact frozen artifact.
Do not repeat this audit or reopen threshold/architecture searches on these
results. Retain the artifact as the development-selected research incumbent,
but do not describe it as a stroke-specific clinical classifier. The immediate
next engineering task is the provider-schema acceptance gate; the scientific
need remains new paired, clinically characterized cohort evidence with non-stroke
comparison groups and a separately locked final-test protocol.

## Reproduction

Evaluator: `scripts/evaluate_lower_back_nonstroke_stress.py`. It refuses existing
outputs. Local private artifacts use `data/processed/lower_back_v020_nonstroke_stress_`
with `windows.csv`, `participants.csv`, `trials.csv`, `summary.csv`, and
`provenance.json` suffixes. The provenance includes raw-file, adapter, protocol,
checkpoint and training-split hashes plus software versions and inference time.

Checkpoint SHA-256:
`34df2abadf862d7838dcfca7917a13c872254bde8a9a6ff9f8554e7b8a3d3ea6`.
Python 3.11.9, PyTorch 2.14.0.dev20260707+cu130, NumPy 2.4.6, pandas 3.0.5.
