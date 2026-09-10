# Classification workspace

Start here. **Uncommitted does not mean unfinished:** this workspace contains
completed experiments and executable prototypes as well as active research.
Only the Week 3 public page and builder were published in commit `b462795`.

## Read these first

| Need | Document |
|---|---|
| This week's completed results and internal progress | [Weekly progress](WEEKLY_PROGRESS_2026-09-07.md) |
| Current research objective and remaining evidence | [Current handoff](../../wiki/concepts/classification-project-status.md) |
| Executable stroke prototype and verified metrics | [Benchmark](BENCHMARK.md) and [prototype registry](../../models/prototypes/README.md) |
| Active synthesis implementation | [Parameter contract and executed virtual-IMU pilot](STROKE_SYNTHESIS_PARAMETER_SPEC.md) |
| Check whether an experiment was already done | [Evidence map](../CLASSIFICATION_EVIDENCE_MAP.md) |
| Latest completed training comparison | [Regularization result](VGA_REGULARIZATION_RESULT.md) |

The stroke phase+HR prototype is built and CLI verified. It uses ten
annotation-assisted features; full-development AUROC is .897 and the separate
matched comparison is .835. These are development results, not independent
clinical validation. The virtual-IMU component is implemented and tested on
healthy GAITEX motion; the clinical stroke transformation is not complete.
RevalExo is historical only and excluded from new model decisions.

## Completed experiment archive

These ten documents were moved out of the active folder. Results are retained,
including failed admission decisions. Historical proposals are not a new queue.

| Experiment | Archived evidence |
|---|---|
| ElderNet source review | [Transfer review](archive/2026-09/ELDERNET_TRANSFER.md) |
| ElderNet frozen transfer | [Result](archive/2026-09/ELDERNET_LOWER_BACK_RESULT.md) |
| ElderNet partial adaptation | [Result](archive/2026-09/ELDERNET_PARTIAL_RESULT.md) |
| ElderNet feature fusion | [Result](archive/2026-09/ELDERNET_FUSION_RESULT.md) |
| gait_cnn investigation | [Review](archive/2026-09/GAIT_CNN_REVIEW.md) |
| DUO-GAIT follow-through | [Evidence review](archive/2026-09/DUOGAIT_FOLLOWUP.md) |
| DUO-GAIT gait_cnn evaluation | [Result](archive/2026-09/DUOGAIT_GAIT_CNN_RESULT.md) |
| Sensor-channel comparison | [Result](archive/2026-09/GAIT_CHANNEL_ABLATION_RESULT.md) |
| Waveform-frame comparison | [Result](archive/2026-09/GAIT_FRAME_RESULT.md) |
| Pathology balance comparison | [Result](archive/2026-09/PATHOLOGY_BALANCE_RESULT.md) |

Locked protocol files remain at their original paths because experiment manifests
hash them. `VGA_SCREEN_RESULT.md` and `VGA_REGULARIZATION_RESULT.md` remain current result
references; the regularization reporting code now lives in notebook 37. A protocol's presence here does not mean
its experiment is pending; consult the result and evidence map.

Reusable code belongs in `src/`, executable packages in `models/prototypes/`,
runners in `scripts/`, and generated outputs in versioned `data/processed/`
folders. Historical dated reports stay in `reports/`. Avoid adding another
current-status document: update this index, the wiki handoff and weekly record.


## Experiment notebook convention

Experiment code and saved results belong in notebooks; reusable modules and tests
remain Python. [Notebook 35: virtual-IMU saved results](../../notebooks/35_virtual_imu_saved_results.ipynb)
contains full orchestration, executed artifact checks, stored cohort/exclusion
tables and an embedded six-channel plot. Reading requires no rerun. The original
pilot runner was removed after migration. Other historical runners have not yet
been migrated and must not be deleted blindly.


Local Git organization (2026-09-10): pending work is preserved on the local
`work/classification-local-2026-09-10` review branch in commits grouped by purpose.
A clean working tree does not mean all research is complete or published.
Experiment-notebook migration remains partial. Published main stays at b462795;
review each group before any future publication.


## Consolidated saved-result notebooks

Use [36 - phase and measurement](../../notebooks/36_phase_measurement_saved_results.ipynb)
and [37 - VGA training](../../notebooks/37_vga_training_saved_results.ipynb) to
inspect completed results without rerunning. Six standalone reporting scripts
were removed; their exact source and historical revision are preserved in the
notebooks. Shared training functions and utilities remain importable Python.
This is a completed reporting migration, not completion of all runner migrations.


## Complete script inventory (2026-09-10)

[Notebook 38: every script and dependency](../../notebooks/38_script_dependency_inventory.ipynb) stores the full
139-script inventory. Structural triage: 27 have Python consumers, 20 are utility
candidates, and 92 require notebook-migration evidence review. All 216 tracked
Python files parsed; 54 existing notebooks (including archives) were scanned.
Only 11 scripts have exact path mentions in notebooks; this is not output coverage.
Eight scripts have missing literal paths: six have existing archive counterparts;
two Mobilise-D scripts lack the checked paths. No byte-identical scripts found.
Dynamic imports/calls and filename-based utility labels require manual review.
This is a complete structural inventory, not a full semantic review or deletion
approval. No experiments were run or scripts deleted by this check.
