# Clinician-observed gait impairment screening: first executed baseline

> Follow-up complete: [controlled regularization and warm-up](VGA_REGULARIZATION_RESULT.md) ran 27 fits of 40 epochs. Neither tested change consistently reduced false alerts. This report preserves the earlier VGA baseline.

2026-09-09. New target, separate from stroke diagnosis.18 fits,9 validation-selected
models,248 participants evaluated; prototype gate failed. No existing model replaced.

## Ground truth and coverage

The [provider paper](https://www.nature.com/articles/s41597-025-05959-w) describes
clinician visual assessment and missing assessments. Its
[full-text XML, Table1](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12546693/fullTextXML)
defines0 none,1 mild,2 moderate,3 severe and4 very severe gait deterioration.
This is an observational rating, not proof of etiology or longitudinal decline.
The table's dictionary name differs from the actual JSON key: local files use
`visualGaitAssessment`. No diagnosis was substituted for the rating.

For each of the existing259 participants, select the earliest session with usable
cached cycles before examining its label. Do not move to later visits to obtain
a preferred/available score.84 have score0,164 have scores1–4, and11 have missing
ratings. Missing cases remain unknown in the coverage ledger. Every included
first session has internally consistent scores. The healthy group contributes
65 score0 and one score1 participant. Nineteen diagnosed participants have score0:
six stroke, six RIL, four CIPN and three ACL. Disease does not automatically imply
a positive screening label. Scores are targets only, never network inputs.

## Training and calibration

The [locked protocol](VGA_SCREEN_PROTOCOL.md) uses the existing six-channel
waveform frame and upstream CNN. Equal class/person/trial weighting; original
participant-disjoint fit/validation/calibration/test roles, intersected with the
new first-session eligible cohort. Two existing recipes and three seeds. Validation
loss selects weights/recipe; calibration sets an empirical<=10% normal-score
alert cutoff. There is no stroke-sensitivity requirement in this target.
The prototype gate requires<=10% held-out normal-score alerts and>=70% detection
of score1–4, in every seed. This is an experimental policy, not a clinical standard.

Calibration contains12,12 and10 normal-rated participants in the three folds.
Each corrected model flags one normal calibration participant, corresponding
to8.3%,8.3% and10%. Those small-sample rates do not guarantee population specificity.

## Held-out results

Ranges span three seeds, not confidence intervals. Each participant appears once
per seed in the outer held-out predictions.

| Measure | Result |
|---|---:|
| AUROC, full248 | .790–.797 |
| Alerts among all normal-rated people | 14–18/84 (16.7–21.4%) |
| Observed impairment detected | 88–105/164 (53.7–64.0%) |
| False alerts: healthy group, score0 | 6–9/65 (9.2–13.8%) |
| False alerts: diagnosed group, score0 | 8–9/19 |
| Mild impairment detected | 27–31/62 |
| Moderate impairment detected | 31–43/63 |
| Severe impairment detected | 28–29/37 |
| Very severe impairment detected | 2/2 |

The last severity group is far too small for a general performance claim.
Matched subset138: AUROC .665–.701, normal alerts12–14/28, impairment detected
67–81/110. Neither the full nor matched results establish adequate screening.
The primary gate fails: the model both exceeds the false-alert target and misses
too much impairment. It is especially insensitive to mild observed impairment.

This does not convert prior stroke false positives into successes retroactively.
Labels, objective, calibration and first-session population differ from the old
stroke benchmark; subtracting their counts would not measure a controlled upgrade.
The new deliverable is a label-grounded screening baseline with measured tradeoffs.

DUO-GAIT,16 healthy people in each condition, nine fold/seed models:
single-task control1–5 alerts, fatigue0–6, dual-task control0–5, dual-task fatigue
0–7. These are alert counts, not verified VGA false positives: DUO-GAIT has no
matching visual-assessment labels. The data are a reused healthy stress test.

## Verification and numerical correction

Initial float64-nextafter threshold logic was insufficient when compared with
float32 scores: the cutoff observation could still be included. The required
finalizer advances by one representable float32 value instead. It recomputes
thresholds from calibration scores only and preserves the original outputs in
`initial_threshold_outputs/`. Nine calibration decisions changed; zero held-out
or external decisions changed. No model was refitted or selected from those outcomes.
Initial calibration outputs are superseded and must not be used as final evidence.

Two regression tests verify strict boundary exclusion, ties, invalid inputs and
the empirical alert budget at several small sample sizes. Label coverage,
validation-selected recipes, source hashes, thresholds and held-out participant
identities passed verification. This is not independent measurement validation.

## Reproduction and status

Run in this order using `C:/Users/frank/.venv-cu130/Scripts/python.exe`:

```text
scripts/classification/benchmark_vga_screen.py
scripts/classification/finalize_vga_screen.py
scripts/classification/verify_vga_screen.py
-m unittest discover -s tests -p test_vga_threshold.py
```

The training runner produces preliminary threshold outputs; finalization is
required before interpretation. It refuses to overwrite a completed experiment.
The finalizer is idempotent against its saved initial outputs. Final artifacts
live under `data/processed/vga_screen_v1/`: label coverage, first-session labels,
metadata hashes, people, selection, histories,18 checkpoints, calibration and
predictions, severity/subgroup metrics, external alerts and verification.
`screening_splits.csv` explicitly separates the legacy diagnosis target from the
new VGA target; `eligible_splits.csv` preserves the original split-source fields.

Metadata interpretation/label construction complete; raw acquisition unchanged;
first-session preprocessing, training and evaluation complete. Stroke-specific
classification remains a separate unresolved task. Screening requires better
normal-score specificity and mild-impairment detection before promotion. Clinical
ratings are subjective,11 cases lack labels, sensor-only stride extraction and
independent positive-cohort validation remain open. No automated outreach,
downloads, deployment or additional tuning sweep occurred.
