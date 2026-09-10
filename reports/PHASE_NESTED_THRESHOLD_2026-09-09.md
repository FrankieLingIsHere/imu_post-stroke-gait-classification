# Phase features with training-selected sensitivity thresholds

Executed 2026-09-09. **Both primary gates failed. No replacement model admitted.**
The improved fixed-threshold results do not translate into adequate specificity
at high sensitivity in this development comparison.

## Locked method

[Pre-fit protocol](../docs/PHASE_NESTED_THRESHOLD_PROTOCOL_2026-09-09.md).
Reused the unchanged phase features, 259 participants, four arms and three outer
participant/pathology folds. Repeated on the existing 144-person device/protocol
subset. Three stratified participant folds inside each outer training set produced
inner OOF scores, with imputation/scaling fitted inside each inner training fold.
Inner folds allow pathology overlap, because some matched outer training sets have
only one other pathology. Outer pathology holdout remains intact.

For each arm and outer fold, the threshold is the largest inner stroke score
cutoff attaining at least 90% empirical inner sensitivity. Negative scores and
outer labels do not select it. Ties count positive. Applied these thresholds to
the existing unchanged outer-model scores. This required 72 new inner fits, with
no redundant outer refitting. A 90% inner target does not guarantee 90% outer sensitivity.

## Results

| Scope | Arm | Stroke detected /49 | Healthy FP | Other-pathology FP |
|---|---|---:|---:|---:|
| Full | Nuisance+cadence | 44 | 12/72 | 61/138 |
| Full | Nuisance+cadence+phase | 41 | 11/72 | 59/138 |
| Full | Combined | 44 | 14/72 | 67/138 |
| Full | Combined+phase | 43 | 12/72 | 62/138 |
| Matched | Nuisance+cadence | 44 | 15/19 | 69/76 |
| Matched | Nuisance+cadence+phase | 42 | 13/19 | 61/76 |
| Matched | Combined | 44 | 13/19 | 67/76 |
| Matched | Combined+phase | 45 | 13/19 | 62/76 |

Primary phase addition loses three stroke detections in the full sample and two
in the matched subset. Neither reaches 90% outer sensitivity. Full-sample other
FPR reduction is only 1.45 percentage points, below the locked five-point minimum.
Both gates fail. The secondary matched combined+phase arm reaches 91.8% sensitivity
but other FPR is 81.6% and healthy FPR 68.4%. It does not rescue the primary test.
Matched participants overlap the full sample, so these are not independent replications.

## Interpretation and stopping decision

Stop threshold sweeps on this phase feature set. Within this tested model family,
the representation still cannot separate many non-stroke walkers while retaining
high stroke sensitivity. This does not establish a unique biological root cause,
prove every possible representation impossible, or validate single-sensor phase
recovery. These are algorithm-derived annotations and reused development cohorts.

Before another model experiment, the remaining design decision is whether the
intended output is stroke diagnosis or a gait-abnormality research measure. A
diagnostic claim requires independent matched stroke/healthy/other-pathology
evidence and reproducible sensor-only measurements. A gait-abnormality output
also needs its own reference labels and validation: do not simply rename the
current stroke score as a validated abnormality score. No further threshold or
architecture sweep is supported by this result alone.

## Artifacts and checks

`data/processed/phase_nested_threshold_v1/` contains input/protocol/code hashes,
inner predictions with split membership, per-fold thresholds and achieved inner
sensitivity, all 1,612 outer prediction rows, metrics, pathology counts and decision.
Each inner validation participant is excluded from its model fit. Each outer
participant and held-out other pathology is excluded from outer training. All 259
participants remain included. Three threshold unit tests passed, covering maximal
feasible cutoff, small samples/ties and invalid inputs.

Metadata/raw acquisition unchanged, no downloads. Phase preprocessing reused.
Nested evaluation complete, no running job. Frozen release unchanged and not rerun:
its historical 89/138 other-pathology positives remain the last verified result.

Reproduce:

```powershell
& C:/Users/frank/.venv-cu130/Scripts/python.exe -m unittest discover -s tests -p test_phase_nested_threshold.py
& C:/Users/frank/.venv-cu130/Scripts/python.exe scripts/run_phase_nested_threshold.py
```
