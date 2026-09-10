# Scripts

This folder contains utilities, shared helpers and historical experiment orchestration. They are grouped by purpose through their names:

- `download_*`, `check_*`, and `audit_*` — source acquisition, structure checks, and compatibility audits.
- `materialize_*`, `extract_*`, and `harmonize_*` — local data preparation under the `data/` contract.
- `train_*`, `pretrain_*`, `finetune_*`, and `benchmark_*` — model development under participant-level split controls.
- `evaluate_*`, `analyze_*`, and `bootstrap_*` — locked evaluation and error analysis.
- `render_*` and `build_*` — report and catalogue generation.

Scripts assume the locally acquired datasets described in `data/README.md`; they will not run from a data-free clone. Material research conclusions must be captured in the relevant active notebook and linked from a report/wiki note.



## Classification script responsibilities

Read results in [the notebook guide](../notebooks/README.md), not by rerunning
one-off report scripts. Five phase/measurement summarizers were replaced by
notebook 36 and the VGA regularization report writer by notebook 37. Those six
`.py` files were removed after import-dependency and source-preservation checks.

Retained utilities handle acquisition, packaging, release verification and page
building. Training/analysis runners that expose functions imported by tests or
other experiments are retained until those functions move into reusable modules.
Examples include `run_conditional_gait_comparison`, `run_phase_nested_threshold`,
`benchmark_gait_cnn` and the ElderNet adaptation helpers. Their retention is a
migration dependency, not a recommendation to add more experiment scripts.
Historical source hashes and saved decision files must not be rewritten to make
a reorganized path look like the original experiment. Check out the recorded
revision when reproducing an old source-hashed execution.


## Complete script inventory (2026-09-10)

[Notebook 38: every script and dependency](../notebooks/38_script_dependency_inventory.ipynb) stores the full
139-script inventory. Structural triage: 27 have Python consumers, 20 are utility
candidates, and 92 require notebook-migration evidence review. All 216 tracked
Python files parsed; 54 existing notebooks (including archives) were scanned.
Only 11 scripts have exact path mentions in notebooks; this is not output coverage.
Eight scripts have missing literal paths: six have existing archive counterparts;
two Mobilise-D scripts lack the checked paths. No byte-identical scripts found.
Dynamic imports/calls and filename-based utility labels require manual review.
This is a complete structural inventory, not a full semantic review or deletion
approval. No experiments were run or scripts deleted by this check.
