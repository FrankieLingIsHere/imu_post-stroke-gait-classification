# Differential-gait implementation and decision

**Implemented and executed:** 27 GPU training fits comparing three objectives,
plus a separate input-validity wrapper. The three-class candidate failed its
locked gate and is not promoted. Constant/nonfinite windows can now be rejected
without returning a score through the new optional wrapper. The frozen v0.2.0
weights, original inference API and all prior TVS results remain unchanged.

## Specific unanswered question

Earlier three-channel binary negative-exposure experiments failed their gates.
They did not test an explicit three-class objective against a matched binary
exposure control on the current one-channel backbone. This experiment asks
whether separating healthy/stroke/other-pathology supervision provides an
advantage beyond simply adding the same non-stroke examples as binary negatives.
It is a test of a hypothesis, not a presumed correction of a proven root cause.

## Controlled implementation

[Training runner](../scripts/train_differential_gait_candidate.py): all arms use
the existing lower-back Inception-style feature backbone, trained from scratch.
The three-class arm changes only the final linear output size and loss. This
is a controlled single-member ERM benchmark, not a comparison against the
full-data 15-member frozen ensemble on people it already saw during training.

- **Data:** Voisard only, with the existing annotated straight-walking extraction:
  72 healthy, 49 stroke and 138 other-pathology participants; 7,485 windows.
  No TVS, RevalExo, Felius or Sint inputs were loaded for this experiment.
- **Arms:** healthy/stroke binary; binary with other-pathology negatives; explicit
  healthy/stroke/other-pathology classes. Original clinical labels are preserved.
- **Splits:** three participant-disjoint folds. Each holds out two entire
  pathology groups: ACL/CIPN, HOA/KOA or PD/RIL. Healthy/stroke people receive
  fixed stratified folds. Every person has one held-out prediction per seed/arm.
- **Sampling:** uniformly sample people within each target, then a window from
  that person. Exposure and three-class arms share the same batches: 32 healthy,
  32 stroke and 32 other windows. The primary binary arm drops the other windows.
  Thus the binary-exposure control accounts for changed training class proportions.
- **Training:** seeds 42/137/202; eight epochs of 40 steps; AdamW learning rate
  0.001, weight decay 0.0001. Normalization uses only primary training windows
  and is shared across arms. No held-out statistics or checkpoint selection.
- **Scoring:** mean window stroke score per person, fixed threshold 0.50.
  Binary uses sigmoid; three-class uses the stroke softmax component (index 1).

The protocol, dependency/input hashes and fixed assignments were saved before
training. For every seed, the candidate had to lose at most two percentage
points of stroke sensitivity and healthy specificity relative to each control,
reduce other-pathology false positives by at least ten points versus primary
binary, and by at least five points versus binary exposure. There was no tuning
after observing results. All three seeds failed.

## Executed result

Mean participant-level metrics across the three seeds:

| Objective | Healthy specificity | Stroke sensitivity | Other-pathology false-positive rate |
|---|---:|---:|---:|
| Primary binary | 91.20% | 87.76% | 53.38% |
| Binary exposure | 92.59% | 68.71% | 35.99% |
| Three-class candidate | 93.06% | 68.71% | 40.58% |

Relative to primary binary, the three-class candidate reduced other-pathology
false positives by 12.80 percentage points but lost 19.05 points of stroke
sensitivity. Relative to binary exposure, its mean sensitivity was identical
and its other-pathology false-positive rate was 4.59 points worse. The proposed
label separation does not pass this experiment's effectiveness requirement.
Do not select its best seed or adjust the threshold to reinterpret the failure.

This is development evidence from one acquisition source, not independent-site
validation. Pathology pairs have unequal counts, the fixed training recipe was
not optimized for each arm, and three seeds provide limited precision. Repeated
inspection of these development data remains a limitation. The result rejects
this specific candidate, not every possible multiclass formulation and not the
possibility of improving stroke specificity.

## Input-validity implementation delivered

[Validity module and CLI](../models/input_validity.py) provide
`predict_windows_with_validity`. It rejects nonfinite or exactly constant
magnitude windows before model inference and returns `stroke_score: null` with
an explicit reason. Rejection is never a healthy/negative prediction. Other
finite windows are forwarded unchanged to the frozen predictor.

This deliberately conservative check fits no TVS threshold. It is not a gait
detector: small variations, non-walking noise and unsupported movement can still
pass. It fixes the demonstrated constant-input scoring behaviour when this
wrapper is used; it does not fix the TVS healthy walking errors. It is opt-in,
and the original frozen API remains unchanged for reproducibility. Any downstream
participant aggregation must disclose rejected windows and eligibility rules.

```powershell
& C:/Users/frank/.venv-cu130/Scripts/python.exe -m models.input_validity `
  --checkpoint models/checkpoints/stroke-gait-lower-back-ensemble-v0.2.0.pt `
  --manifest models/checkpoints/stroke-gait-lower-back-ensemble-v0.2.0.manifest.json `
  --windows path/to/windows.npy --output path/to/window_scores.json
```

The CLI writes explicit scored/rejected counts and refuses to overwrite an
existing output. No new model weights are distributed as an improved release.

## Verification and continuation

Six focused tests passed: identical starting backbone/stroke-class mapping,
participant/pathology isolation, balanced training-only sampling, invalid-window
exclusion, no fake negative on rejection and shape/small-variation handling.
The API and CLI integration check agreed: one nonconstant release-smoke window
retained its expected score, while the release's constant smoke input plus two
synthetic invalid inputs were rejected. The initial integration assertion assumed
both release smoke windows were nonconstant; inspecting the fixture identified
the constant case and the corrected assertion verifies its intentional rejection.

Verified 2,331 participant prediction rows, complete participant accounting in
all nine arm/seed combinations, locked source/input hashes and unchanged frozen
checkpoint. Artifacts under `data/processed/differential_gait_v1/` include:
protocol/hash, participant folds, 27 fold checkpoints/results, aggregated and
pathology metrics, decision, verification and CLI smoke output.

The classifier improvement remains unresolved. Do not rerun this three-class
candidate as pending work. A further training proposal must identify a different
mechanism and a defensible sensitivity-preserving validation design; no such
replacement is admitted by this run. The validity wrapper is the implemented
input-handling improvement, with its limited scope stated above.
