# Stroke feature prototype: verified development benchmark

Executed 2026-09-09. This verifies feature reconstruction, the prediction interface
and participant/pathology-held-out performance. It is not independent external
validation of the full-data package or its single development-selected threshold.

## Required inputs verified

Reconstructed all ten predictors from 1,348 original metadata/processed-signal
files and aggregated to the same 259 participants. Verified source hashes before
extraction. Every reconstructed column matches the packaged training table to
floating-point precision (largest difference 1.42e-14).

| Feature | Available participants | Handling |
|---|---:|---|
| Age | 258/259 | One missing value, training-fold median imputation |
| XSens fraction | 259/259 | Metadata-derived, 0-1 |
| One-way protocol length | 259/259 | Metadata-derived metres |
| Cadence | 259/259 | Existing event-count/straight-duration implementation |
| Step asymmetry | 259/259 | Annotation-assisted |
| Swing asymmetry | 259/259 | Annotation-assisted |
| Stance asymmetry | 259/259 | Annotation-assisted |
| Swing fraction | 259/259 | Annotation-assisted |
| Double-support fraction | 259/259 | Valid stance-overlap implementation |
| Nominal-Y log harmonic ratio | 259/259 | Provider processed signal plus annotated stride boundaries |

Three invalid-reference trials contribute missing phase/HR values to aggregation,
but their participants have other usable trials. No participant was dropped.
This is numerical reconstruction with the existing extractors, not independent
proof of physiological measurement accuracy. Supporting sensor-only extraction,
cross-source feature equivalence and reliable independent references remain open.

## Benchmark design

Refitted baseline and candidate in the existing three outer folds, separately for
259 full-scope and 144 device/protocol-matched participants: 12 verification fits.
Participants are disjoint; other-pathology groups are held out as whole groups.
All scores reproduce the saved experiment. Candidate predictions through the
packaged API match direct estimator predictions, with no rejected held-out rows.

Candidate thresholds are reconstructed from saved inner OOF stroke predictions
and verified against recorded thresholds. Inner calibration participants exactly
equal outer training participants, each appearing once. The old inner folds were
participant-stratified, not pathology-disjoint. No outer test labels choose these
thresholds. Baseline uses its recorded training-selected thresholds.

The full-data package threshold 0.3953767333929809 is deliberately **not** used in
these headline metrics: it was chosen with access to all development labels.
All cohorts have been repeatedly inspected, so even correctly separated folds
are development evidence subject to selection effects. No architecture/threshold
search or new final test occurred.

## Results

Baseline is age/device/protocol plus cadence. Candidate adds the five phase
features and nominal-Y HR. AUROC treats stroke versus all non-stroke participants.

| Scope/model | AUROC | Balanced accuracy | Stroke TP/FN | Healthy FP | Other FP |
|---|---:|---:|---:|---:|---:|
| Full baseline | 0.798 | 0.775 | 44/5 | 12/72 | 61/138 |
| Full candidate | **0.897** | **0.812** | **45/4** | **6/72** | **56/138** |
| Matched baseline | 0.671 | 0.507 | 44/5 | 15/19 | 69/76 |
| Matched candidate | **0.835** | **0.675** | **44/5** | **5/19** | **47/76** |

Full candidate sensitivity 91.8%, healthy specificity 91.7%, other FPR 40.6%.
Matched sensitivity 89.8%, healthy specificity 73.7%, other FPR 61.8%.
Full candidate descriptive Wilson 95% intervals: sensitivity 80.8-96.8%, healthy
specificity 83.0-96.1%, other FPR 32.7-48.9%. All intervals and fold counts are saved.
They do not capture model-selection/retraining uncertainty or new-cohort transfer.
Brier scores are saved (0.154 full, 0.162 matched), but class-weighted model scores
are not established clinical probabilities.

## Remaining false positives by pathology

| Pathology | Full candidate | Matched candidate |
|---|---:|---:|
| ACL | 0/11 | Not present |
| HOA | 0/15 | Not present |
| KOA | 0/18 | Not present |
| CIPN | 13/19 | 11/18 |
| PD | 13/24 | 11/19 |
| RIL | 30/51 | 25/39 |

The full candidate improves PD/RIL versus baseline but increases CIPN positives
from 9/19 to 13/19. Thus the aggregate improvement is not uniform. Better full-scope
specificity is partly associated with correctly rejected orthopedic controls;
those controls are absent from the matched subset. Different training subsets and
covariates also change performance, so the difference is not a causal device test.
Neither benchmark has established stroke specificity against neurological controls.

## Reproduce and artifacts

```powershell
& C:/Users/frank/.venv-cu130/Scripts/python.exe scripts/classification/benchmark_stroke_features.py
```

`data/processed/stroke_feature_benchmark_v1/` contains reconstructed trials, feature
audit, fold verification, held-out predictions, metrics, Wilson intervals,
pathology/fold counts and verification manifest. Ten existing tests passed across
input contract, phase extraction and HR extraction. Package hashes verified.
The model package and historical experiments remain unchanged.

Acquisition unchanged. Source-feature reconstruction and held-out development
benchmark complete. Independent validation and end-to-end raw-signal feature
recovery are not complete. Use the prototype for research workflows with these
limits explicit; do not describe the training batch smoke check as a benchmark.
