# Scripts

Reusable scripts support the executed notebook record. They are grouped by purpose through their names:

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
