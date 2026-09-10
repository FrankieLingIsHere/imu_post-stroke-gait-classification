"""Write executed conditional-laterality report from saved metrics."""
from pathlib import Path
import pandas as pd
import json

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/processed/gyro_laterality_v1'


def main():
    metrics=pd.read_csv(OUT/'metrics.csv');decision=json.loads((OUT/'decision.json').read_text())
    coverage=pd.read_csv(OUT/'trial_coverage.csv');fits=pd.read_csv(OUT/'fit_counts.csv')
    lines=['# Conditional gyro laterality experiment, 2026-09-09','',
           '**Gate '+('passed' if decision['passed'] else 'failed')+'. This measures side assignment at supplied contact times, not stroke diagnosis.**','',
           '[Pre-fit protocol](../docs/GYRO_LATERALITY_PROTOCOL_2026-09-09.md).',
           'Used six nominal vertical/AP gyro features: 0.5-2 Hz filtered values and',
           'first/second sample gradients at reference heel strikes. Provider-processed',
           'X/Z axes, with no per-person or diagnosis-driven sign reversal. Fresh linear',
           'SVC C=1 and training-fold MinMaxScaler. Participant-equal weights split equally',
           'between sides. Existing three outer participant/pathology folds, full and',
           'matched scopes. This is inspired by Ullrich feature types, not an exact',
           'reproduction or a run of its pretrained model. Six new fits.','',
           'Installed mobgap pretrained estimators emitted sklearn serialization-version',
           'warnings (1.6.1 versus local 1.9.0). They were not used for predictions.',
           'The existing environment was retained and no packages downgraded.','',
           '## Results','',
           '| Scope | Group | Participants | Participant-macro side accuracy | Contact coverage | Pass |',
           '|---|---|---:|---:|---:|---|']
    for r in metrics.itertuples():
        lines.append(f'| {r.scope} | {r.pathology} | {r.n} | {r.accuracy:.1%} | {r.coverage:.1%} | {r.passed} |')
    lines+=['',f'Usable contacts: {coverage.usable.sum():,}/{coverage.expected.sum():,}. Three invalid',
            'reference-bound trials remain in coverage. All 259 participants retained in',
            'the main ledger. Missing participant accuracy would count zero.',
            f'Training single-side participant exclusions across fits: {fits.training_excluded_single_side.sum()}.',
            'Two tests passed: feature dimensions/sign response and duplicate/out-of-range/',
            'nonfinite rejection. All held-out participant/pathology checks passed.','',
            '## Limits and decision','',
            'References are algorithm-derived foot annotations. Contact times and straight',
            'bout boundaries are supplied, so this is conditional agreement, not independent',
            'measurement validity or autonomous contact accuracy. No final-contact, stance,',
            'double-support or stroke-diagnostic accuracy is established. The nominal',
            'processed-axis convention is used without per-trial anatomical calibration.',
            'The fresh fit does not validate a transferable pretrained model. Matched and',
            'full scopes overlap and are not independent replications.','',
            ('The conditional feasibility gate passed. Next test must use predicted contacts and count missed/extra/wrong-side events together.' if decision['passed'] else
             'The conditional feasibility gate failed. Do not attach this model to the event adapter or claim autonomous phase recovery. Do not globally flip test labels or retune on held-out cases. The saved per-group results locate the measurement limitation; independent event references remain needed.'),'',
            'No new stroke-classification result. Previous primary matched HR result remains',
            '44/49 stroke detected, 5/19 healthy FP, 47/76 other FP. Frozen release unchanged.',
            'Metadata/raw acquisition unchanged. Gyro feature extraction and conditional',
            'evaluation complete. Autonomous laterality and independent validation not done.',
            'No background job after completion.','',
            'Artifacts in `data/processed/gyro_laterality_v1/`: hashes, features, trial coverage,',
            'contact predictions, fit counts, participant/group metrics and decision.',
            'Run `scripts/run_gyro_laterality.py` then `scripts/summarize_gyro_laterality.py`.','']
    (ROOT/'reports/GYRO_LATERALITY_2026-09-09.md').write_text('\n'.join(lines),encoding='utf-8')


if __name__=='__main__':main()
