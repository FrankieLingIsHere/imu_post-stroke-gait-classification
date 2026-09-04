# Scripts

Reusable scripts support the executed notebook record. They are grouped by purpose through their names:

- `download_*`, `check_*`, and `audit_*` — source acquisition, structure checks, and compatibility audits.
- `materialize_*`, `extract_*`, and `harmonize_*` — local data preparation under the `data/` contract.
- `train_*`, `pretrain_*`, `finetune_*`, and `benchmark_*` — model development under participant-level split controls.
- `evaluate_*`, `analyze_*`, and `bootstrap_*` — locked evaluation and error analysis.
- `render_*` and `build_*` — report and catalogue generation.

Scripts assume the locally acquired datasets described in `data/README.md`; they will not run from a data-free clone. Material research conclusions must be captured in the relevant active notebook and linked from a report/wiki note.

