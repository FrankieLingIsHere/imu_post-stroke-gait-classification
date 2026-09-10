# Final channel ablation and false-positive localization

2026-09-09. Complete:36 new fits,18 validation-selected models and27-model
trial/cycle replay. Neither ablation passes any of its six paired admission
comparisons against the combined model. Protocol:
[GAIT_CHANNEL_ABLATION_PROTOCOL.md](../../GAIT_CHANNEL_ABLATION_PROTOCOL.md).

## Final results

Full259 cohort, ranges across three seeds, calibrated operating point. These
ranges are not confidence intervals.

| Input | AUROC | Stroke TP/49 | Healthy FP/72 | Neurological FP/94 |
|---|---:|---:|---:|---:|
| Combined frame6, previous run | .756–.768 | 45–47 | 16–23 | 80–82 |
| Acceleration values only | .735–.783 | 46–48 | 19–30 | 79–82 |
| Gyro values only | .749–.780 | 41–48 | 45–53 | 82–86 |

Gyro-value-only classification is particularly poor on healthy controls. Removing
gyro does not resolve neurological false positives. It is therefore unsupported
to identify gyro alone as the cause of combined-model failures. Both inputs carry
some ranking information but neither provides adequate specificity in this recipe.
Matched-device results and fixed.5 tradeoffs are retained in metrics.csv, not
substituted for the failed full/matched paired gate.

DUO-GAIT false positives/16, range across nine fold/seed models:

| Condition | Acceleration values | Gyro values | Combined, previous run |
|---|---:|---:|---:|
| Single-task control | 1–15 | 11–16 | 3–16 |
| Single-task fatigue | 0–16 | 13–16 | 7–16 |
| Dual-task control | 1–14 | 11–15 | 4–14 |
| Dual-task fatigue | 1–16 | 12–16 | 10–15 |

The wide model ranges remain a serious stability limitation. These16 young
healthy participants cannot estimate stroke sensitivity or independently establish
neurological specificity. No best external run is selected or promoted.

## Where the errors occur

Participants consistently positive across every seed:

| Pathology | Combined | Acceleration values | Gyro values |
|---|---:|---:|---:|
| Parkinson's | 22/24 | 21/24 | 21/24 |
| Radiation-induced leukoencephalopathy | 44/51 | 45/51 | 49/51 |
| Chemotherapy-induced peripheral neuropathy | 14/19 | 12/19 | 11/19 |

For70 of the combined model's80 consistently positive neurological controls,
every evaluated walking trial is positive in all three seeds. The median fraction
of positive trials among those80 is1.0. Thus isolated high-scoring strides are
not a sufficient explanation of most persistent participant errors. This does
not mean every individual cycle is positive. Trial means and participant
aggregation are explicitly distinguished in the saved trace.

The same calibration stroke ID sets the combined threshold in all three seeds
within each fold: CVA_31 in fold0, CVA_16 in fold1 and CVA_8 in fold2. These are
dataset participant identifiers, not clinical diagnoses of outlier status. Do
not remove these people because their scores lower the threshold. Their full
threshold-setting records are saved for review.

## Question and scope

Train acceleration-value-only and gyro-value-only classifiers using the same
waveform frame and validation-selected training recipes as the completed combined
model. The frame/adapter functions were checked for identical ASTs against the
previous runner. Previously completed magnitude/combined arms are reused, not
retrained. This is36 new fits, not a new architecture sweep. No deployment changes.
The gyro-value arm still uses acceleration to define coordinates. Removing
acceleration values is therefore not removing every dependence on acceleration.

All259 Voisard participants and16 DUO-GAIT participants/four conditions are the
same development/stress cohorts as before. These are not untouched external
positive data. Strides remain reference-assisted. Paired comparisons preserve
participant, seed and split identities; they are not causal channel attribution
inside a fixed trained network, since each channel subset has its own fitted model.

## Verified localization from the existing combined model

The same22/24 Parkinson's participants,44/51 radiation-induced leukoencephalopathy
participants and14/19 chemotherapy-induced peripheral neuropathy participants
are positive in all three seeds. That is80/94 neurological controls consistently
positive. Errors are not explained by random seed variability alone. This is
evidence of failed discrimination of these held-out pathologies, not proof of a
unique shared biomechanical feature or biological cause. Diagnosis groups and
outer folds are coupled by the deliberate leave-pathology-out design, so their
effects cannot be separated causally using this table.

There are only seven stroke participants in each calibration split. The stated
at-least90% sensitivity rule selects7/7, because6/7 is85.7%. Thus the threshold
equals the lowest calibration stroke score and the realized calibration target
is100%. This is a concrete resolution limitation of the chosen calibration
design, not a new training-label leakage finding. Combined-model thresholds
range .05987–.31211 across folds/seeds.

At fixed.5, combined neurological positives fall from80–82/94 to56–62/94, but
stroke detections fall from45–47/49 to32–36/49. Threshold choice contributes to
the operating point, while substantial score overlap remains. Raising a cutoff
does not solve that discrimination problem. Fixed.5 is descriptive here, not a
newly selected operating threshold or clinical calibration recommendation.

## Traceable artifacts

`data/processed/gait_channel_ablation_v1/` contains the new experiment artifacts.
Localization adds participant consistency/IDs and score margins, pathology counts,
per-fold thresholds and calibration resolution, score quantiles, paired condition
changes in DUO-GAIT, trial contributions and the strongest three non-stroke cycles
per trial. Cycle sample/time positions refer to the shared100Hz packet clock.
These intervals identify strong model responses, not independently annotated
cycle-level clinical false positives or explanatory physiological biomarkers.

No new raw acquisition. Frame/adapter preprocessing, training, evaluation and
localization are complete. Source/split checks and validation-only recipe
selection/threshold provenance verification passed. Two selected checkpoints
reloaded with maximum score errors7.11e-7 and5.00e-6 and no changed calls. The
27-model trial replay reconstructed participant scores with maximum error5.96e-6.
Frame unit-test evidence is inherited from the identical previously tested frame
implementation, not a new clinical measurement validation.

## Decision and supported explanation

Stop the planned tuning/channel sequence here. Keep the existing prototype and
all these models as research baselines; none earns replacement through this gate.
The strongest supported explanation is functional: the learned scores overlap
substantially between stroke and other neurological gait, while a seven-person
calibration set requires retaining its lowest-scoring stroke case to meet the
nominal sensitivity rule. This produces repeatable, often whole-trial false
positives. Seed noise or a few extreme cycles do not account for most of them.

This is not a demonstrated unique biological or sensor-level root cause. The
experiments do not isolate age, pace, device, mounting, waveform-frame instability
or learned biomechanical markers. Gyro-value ablation fails to provide a clean
fix, and changing thresholds trades away stroke detections. No additional rescue
sweep was launched. Independent positive-cohort evidence and a more defensible
calibration sample remain requirements for a stronger diagnostic claim, rather
than another untested claim that a different network will solve the problem.
