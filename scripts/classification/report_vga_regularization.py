"""Render the completed, verified comparison without selecting an arm from test data."""
import json
from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'data/processed/vga_regularization_v1'


def table(frame):
    rows = [list(frame.columns), ['---'] * len(frame.columns), *frame.astype(str).values.tolist()]
    return '\n'.join('| ' + ' | '.join(row) + ' |' for row in rows)


def main():
    verification = json.loads((OUT / 'verification.json').read_text())
    assert verification['fits'] == 27
    decision = json.loads((OUT / 'decision.json').read_text())
    metrics = pd.read_csv(OUT / 'metrics.csv')
    dynamics = pd.read_csv(OUT / 'training_dynamics.csv')
    paired = pd.read_csv(OUT / 'paired_validation.csv')
    external = pd.read_csv(OUT / 'external_metrics.csv')
    severity = pd.read_csv(OUT / 'severity.csv')
    changes = pd.read_csv(OUT / 'paired_call_changes.csv')
    history = pd.read_csv(OUT / 'histories.csv')
    fig, axes = plt.subplots(3, 3, figsize=(14, 10), sharex=True, sharey=True)
    for fold in range(3):
        for col, seed in enumerate([42, 137, 202]):
            ax = axes[fold, col]
            for arm, color in [('fixed', '#0072B2'), ('decay', '#D55E00'), ('warmup', '#009E73')]:
                g = history[history.run.eq(f'{arm}_fold{fold}_seed{seed}')]
                ax.plot(g.epoch, g.val_loss, color=color, label=arm)
                ax.plot(g.epoch, g.loss, color=color, linestyle='--', alpha=.5)
                best = g.loc[g.val_loss.idxmin()]
                ax.scatter([best.epoch], [best.val_loss], color=color, s=25, zorder=3)
            ax.set_title(f'Fold {fold} / seed {seed}')
            ax.grid(alpha=.2)
            if col == 0: ax.set_ylabel('Weighted cross-entropy')
            if fold == 2: ax.set_xlabel('Epoch')
    axes[0, 0].legend(fontsize=9)
    fig.suptitle('VGA screen: validation (solid), training (dashed), selected epoch (dot)')
    fig.tight_layout(rect=(0, 0, 1, .96))
    fig.savefig(OUT / 'training_curves.png', dpi=160)
    plt.close(fig)
    sections = [
        '# Controlled regularization and warm-up: executed results',
        '2026-09-09. All 27 fits completed 40 epochs. This tests clinician-observed '
        'gait impairment (VGA 0 versus 1-4), separately from stroke diagnosis. '
        'No existing model was replaced.',
        '**Result: neither tested change gives a consistent reduction in false alerts.** '
        'Warm-up slightly improves full-population AUROC over the cosine control in '
        'all three seeds, but increases normal-rated alerts in two seeds. Weight decay '
        'corrects none of the control\'s normal-rated false alerts and introduces two '
        'additional alerts in seed 42. Every setting fails the fixed operating-point '
        'gate. Lower validation loss did not provide a reliable screening improvement.',
        'The previous VGA recipe had full AUROC 0.790-0.797, versus 0.769-0.784 '
        'across these new settings. That is historical context, not an isolated '
        'comparison of regularization: the schedule and recipe-selection procedure '
        'also differ. The controlled contrasts here are decay versus fixed and '
        'warmup versus fixed.',
        '## Design and actual settings',
        'The [protocol](VGA_REGULARIZATION_PROTOCOL.md) was saved and hashed before '
        'fitting. Three settings, three seeds (42, 137, 202), three participant-disjoint '
        'outer folds. The same 248 earliest-session participants, 84 normal-rated '
        'and 164 impaired-rated, were used in all settings. Eleven missing ratings '
        'remain unknown in the coverage ledger. Labels and participant metadata '
        'match the [previous VGA baseline](VGA_SCREEN_RESULT.md).',
        'The actual upstream CNN remains Conv1D(32, kernel 5, ReLU), global max pooling '
        'and a two-class softmax. Inputs are six lower-back accelerometer/gyroscope '
        'channels in the existing waveform frame, with reference-assisted stride '
        'segmentation and 200 samples per cycle. Scaling uses fitting participants '
        'only. Class, participant and trial weighting is unchanged.',
        'All settings use Adam, batch size 32 and a cosine learning-rate schedule '
        'from 0.001 to 0.00001 over 40 epochs. `fixed` has zero weight decay. '
        '`decay` changes only decoupled weight decay to 0.01, including biases. '
        '`warmup` has zero weight decay and multiplies the first five scheduled '
        'rates by (epoch+1)/5, starting at 0.0002. Schedules match from the fifth '
        'epoch onward. No early stopping, dropout, augmentation or gradient clipping '
        'was used. Warm-up changes learning rate, not a separate gradient operation.',
        'Minimum validation-loss checkpoints are evaluated. Calibration alone sets '
        'the strict float32 cutoff for at most 10% empirical normal-rated alerts. '
        'No held-out or DUO-GAIT score selects epochs, thresholds or a winning setting. '
        'The gate is normal-rated FPR <=10% and impairment sensitivity >=70% in '
        'every seed. These are project prototype criteria, not clinical standards.',
        '## Held-out participant results',
        'Each row pools the three outer folds, with every participant appearing once '
        'per seed and setting. Counts preserve the tradeoff between false alerts '
        'and missed impairment. Seeds reuse participants and are not independent cohorts.'
    ]
    for scope in ['full', 'matched']:
        g = metrics[metrics.scope.eq(scope)].copy()
        display = pd.DataFrame({'Setting': g.arm, 'Seed': g.seed, 'AUROC': g.auroc.map(lambda x: f'{x:.3f}')})
        for title, prefix in [('Normal false alerts', 'normal'), ('Impaired detected', 'impaired'), ('Healthy, VGA 0 false alerts', 'healthy_normal')]:
            display[title] = [f'{a}/{n} ({100*a/n:.1f}%)' if n else '0/0' for a, n in zip(g[prefix+'_alerts'], g[prefix+'_n'])]
        sections += [f'### {scope.capitalize()} population', table(display)]
    sections += ['Gate-passing settings: **' + (', '.join(decision['passed_arms']) or 'none') + '**. No automatic promotion follows this reused development benchmark.']
    sections += ['## Validation and training duration']
    sections += ['![Training and validation curves for every fold and seed](../../data/processed/vga_regularization_v1/training_curves.png)']
    summary = dynamics.groupby('arm').agg(best_epoch_min=('best_epoch','min'), best_epoch_max=('best_epoch','max'), best_after_patience8=('best_after_stop','sum'))
    summary['best_at_epoch40'] = dynamics.assign(at40=dynamics.best_epoch.eq(40)).groupby('arm').at40.sum()
    sections += [table(summary.reset_index())]
    late = dynamics[dynamics.best_after_stop][['run','simulated_patience8_stop','best_epoch','minimum_before_stop','minimum_full']].copy()
    for column in ['minimum_before_stop','minimum_full']:late[column] = late[column].map(lambda x: f'{x:.6f}')
    sections += ['Two of 27 runs show late recovery. None selects epoch 40. '
                 'The substantial train/validation separation, especially in fold 0, '
                 'is consistent with overfitting. These results do not support '
                 'insufficient epochs as a sufficient explanation of the remaining false alerts.', table(late)]
    for arm in ['decay', 'warmup']:
        delta = paired[arm+'_minus_fixed']
        sections += [f'`{arm}` versus `fixed`: lower best validation loss in {int(delta.lt(0).sum())}/9 paired fits. '
                     f'Mean loss difference {delta.mean():+.5f}, range {delta.min():+.5f} to {delta.max():+.5f}. '
                     'These are descriptive comparisons, not an independent significance test.']
    sections += [
        'The patience-eight stopping point is simulated on each completed run. '
        'A later best checkpoint is evidence that this stopping rule would have '
        'missed recovery on the new cosine schedule. It is not an exact counterfactual '
        'for the previous ReduceLROnPlateau recipe. Forty completed epochs do not '
        'prove convergence beyond the tested budget. Full train/validation histories '
        'and final-five-epoch changes are saved.',
        '## Paired changes in held-out calls',
        'Compared with `fixed`, positive-to-negative corrects a false alert for normal-rated '
        'people but loses a detection for impaired-rated people. Negative-to-positive '
        'has the opposite effect. This exposes changes that net counts can hide.',
        table(changes),
        '## Impairment severity',
        'Counts below span the three seeds. VGA 4 contains only two people and cannot '
        'support a general severity-performance claim.'
    ]
    sev = severity.groupby(['arm','vga']).agg(n=('n','first'), min_detected=('alerts','min'), max_detected=('alerts','max')).reset_index()
    sections += [table(sev), '## DUO-GAIT stress test',
        'Sixteen people per condition, nine fold/seed models per setting. These are '
        'alert-count ranges, not confidence intervals or verified VGA false-positive '
        'rates: DUO-GAIT has no matching VGA labels and was already used in development. '
        'It cannot establish external impaired-case sensitivity.',
        table(external.groupby(['arm','condition']).agg(n=('n','first'), min_alerts=('alerts','min'), max_alerts=('alerts','max')).reset_index()),
        '## Verification and reproducibility',
        'The verifier checks 27 complete finite 40-epoch histories, checkpoint selection, '
        'the exact learning-rate schedules, unchanged source hashes, baseline label '
        'identity, all four participant-role separations, calibration membership and '
        'alert budgets, exported calls, metrics and the gate decision. Three checkpoint '
        'spot checks (fold 0, seed 42, all settings) reproduce scores within 1e-5 '
        'with zero changed calls. Maximum spot-check error: '
        f"{max(verification['reload_errors'].values()):.3g}. "
        'Two unit tests separately check the schedule and an actual zero-gradient '
        'Keras Adam update, confirming that decoupled weight decay operates.',
        'Use `C:/Users/frank/.venv-cu130/Scripts/python.exe` with the following scripts '
        'in order. The training runner refuses to overwrite a completed experiment.',
        '```text\nscripts/classification/benchmark_vga_regularization.py\n'
        'scripts/classification/verify_vga_regularization.py\n'
        'scripts/classification/report_vga_regularization.py\n'
        '-m unittest discover -s tests -p test_vga_regularization.py\n```',
        'Artifacts: `data/processed/vga_regularization_v1/` contains checkpoints, '
        'fold scalers, manifests, label coverage, predictions, calibration, metrics, '
        'severity, external alerts, training dynamics, paired comparisons and the '
        'post-run Python/package/GPU environment record.',
        '## Limits and project status',
        'This isolates one weight-decay setting and one warm-up duration. It does not '
        'test every regularizer or establish a unique cause of false positives. '
        'Architecture, subjective labels, small calibration groups, disease/device '
        'composition and measurement transfer remain possible limitations. Repeated '
        'development on the same outer folds limits claims of independent generalization.',
        'Metadata and raw acquisition are unchanged. Previously verified labels and '
        'preprocessing are reused. This training/evaluation comparison is complete. '
        'Independent positive-cohort validation, sensor-only event extraction and '
        'stroke-specific diagnostic validity remain unresolved.'
    ]
    (ROOT / 'docs/classification/VGA_REGULARIZATION_RESULT.md').write_text('\n\n'.join(sections)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main()
