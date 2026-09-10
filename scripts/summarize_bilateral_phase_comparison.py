"""Report fixed out-of-fold results and conditional paired uncertainty."""
from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/processed/bilateral_phase_v1'


def main():
    predictions = pd.read_csv(OUT / 'predictions.csv')
    metrics = pd.read_csv(OUT / 'metrics.csv')
    decision = json.loads((OUT / 'decision.json').read_text())
    rng = np.random.default_rng(20260909)
    uncertainty = []
    for scope, group in predictions.groupby('scope'):
        pair = group[group.arm.eq('nuisance_cadence')].merge(
            group[group.arm.eq('nuisance_cadence_phase')], on=['participant','target','fold','pathology','scope'])
        for target, label in [(0, 'healthy_fpr_change'), (1, 'stroke_sensitivity_change'), (2, 'other_fpr_change')]:
            g = pair[pair.target.eq(target)]
            differences = (g.score_y.ge(.5).astype(int)-g.score_x.ge(.5).astype(int)).to_numpy()
            values = [rng.choice(differences, len(differences), replace=True).mean() for _ in range(2000)]
            lo, hi = np.quantile(values, [.025,.975])
            uncertainty.append(dict(scope=scope, measure=label, change=differences.mean(), lower=lo, upper=hi))
    pd.DataFrame(uncertainty).to_csv(OUT / 'paired_uncertainty.csv', index=False)
    lines = ['# Bilateral phase-feature experiment, 2026-09-09', '',
             '**Executed: primary gate failed in both scopes. False positives remain.**', '',
             'The five annotation-derived phase features improve out-of-fold AUROC and reduce',
             'false positives, but the primary comparison loses stroke detections. This is',
             'evidence of incremental predictive information in this development sample,',
             'not proof of a causal mechanism or an independently validated model.', '',
             '[Pre-fit protocol](../docs/BILATERAL_PHASE_PROTOCOL_2026-09-09.md).',
             'Four fixed arms, three existing participant/pathology folds, fixed threshold 0.5.',
             'All 259 selected participants retained, including the 144-person device/protocol',
             'subset (49 stroke, 19 healthy, 76 other). This subset is not age matched.', '',
             '| Scope | Arm | Stroke detected / 49 | Healthy FP | Other FP | AUROC |',
             '|---|---|---:|---:|---:|---:|']
    for r in metrics.itertuples():
        healthy, other = (72, 138) if r.scope == 'all_selected' else (19, 76)
        lines.append(f'| {r.scope} | {r.arm} | {r.stroke_tp}/49 | {r.healthy_fp}/{healthy} | {r.other_fp}/{other} | {r.auroc:.3f} |')
    lines += ['', 'The primary nuisance+cadence+phase arm reduces other FP by 9/138 in the',
              'full sample and 9/76 in the matched subset, but loses two and four stroke',
              'detections respectively. Both fail the locked sensitivity-preserving gate.',
              'The secondary combined+phase arm reduces matched other FP from 43 to 31',
              'without changing 31/49 stroke detections. Its full-sample comparison loses',
              'one stroke detection (43 to 42), so this does not rescue the primary decision.', '',
              '## Measurement and verification', '',
              f'- {decision["trials"]} selected trials processed, {decision["complete_trials"]} with complete phase features.',
              '- Three previously invalid reference-bound trials remain in the ledger with missing phase features.',
              '- All 259 participants have complete aggregated phase features. No participant was dropped.',
              '- Invalid cycles are counted by pathology. No diagnosis or deficit-side field enters predictors.',
              '- Features use TO/HS annotations, not newly estimated single-sensor events.',
              '- Double support uses fully covered left HS-to-HS cycles and stance intersections.',
              '  Finite-bout coverage can depend on the reference side. No paretic-side inference is used.',
              '- Four synthetic unit tests passed: symmetric gait/support, equal-stride unequal-step',
              '  timing with side swap, turns/missing contacts, malformed/empty events.',
              f'- Reproduced all 806 baseline participant predictions, maximum score difference {decision["baseline_max_score_delta"]:.3g}.',
              '- Protocol and input hashes, per-trial metadata hashes, features, predictions,',
              '  pathology counts and coverage are saved in `data/processed/bilateral_phase_v1/`.', '',
              '## Conditional uncertainty', '',
              'Paired 2,000-resample participant bootstrap of fixed OOF calls, new minus baseline.',
              'These intervals do not include model retraining or uncertainty across new cohorts.', '',
              '| Scope | Measure | Change, percentage points | 95% interval |',
              '|---|---|---:|---:|']
    for r in uncertainty:
        lines.append(f'| {r["scope"]} | {r["measure"]} | {100*r["change"]:.1f} | {100*r["lower"]:.1f} to {100*r["upper"]:.1f} |')
    lines += ['', '## Decision and next unresolved question', '',
              'Do not promote this candidate or repeat the same fixed-threshold comparison.',
              'The next bounded question is whether the added information improves specificity',
              'at a sensitivity target selected entirely within training folds. That requires',
              'a separately locked nested validation design and the same baseline control.',
              'Selecting a threshold on these outer-fold labels would invalidate that test.',
              'Even a successful development result would still need independent cohort and',
              'sensor-only measurement validation. Missing phase information is not established',
              'as the unique cause of the frozen CNN errors.', '',
              'Metadata and raw acquisition: unchanged, no downloads. Phase preprocessing and',
              'the 24 logistic fits: completed. Frozen model: unchanged, historical 89/138',
              'other-pathology positives still apply, not rerun here. No clinical release.', '',
              'Reproduce with the existing Python environment:', '',
              '```powershell',
              '& C:/Users/frank/.venv-cu130/Scripts/python.exe -m unittest discover -s tests -p test_bilateral_phase.py',
              '& C:/Users/frank/.venv-cu130/Scripts/python.exe scripts/run_bilateral_phase_comparison.py',
              '& C:/Users/frank/.venv-cu130/Scripts/python.exe scripts/summarize_bilateral_phase_comparison.py',
              '```', '']
    (ROOT / 'reports/BILATERAL_PHASE_COMPARISON_2026-09-09.md').write_text('\n'.join(lines), encoding='utf-8')


if __name__ == '__main__':
    main()
