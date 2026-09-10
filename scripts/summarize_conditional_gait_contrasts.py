"""Separate healthy and pathological diagnostic contrasts without refitting."""
from pathlib import Path
import hashlib
import json
import sys

import pandas as pd
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.run_conditional_gait_comparison import score_metrics


def main():
    out = ROOT / 'data/processed/conditional_gait_v1'
    predictions = pd.read_csv(out / 'predictions.csv')
    people = pd.read_csv(out / 'participant_contract.csv')
    rows = []
    for (scope, arm), frame in predictions.groupby(['scope', 'arm']):
        for negative, label in [(0, 'stroke_vs_healthy'), (2, 'stroke_vs_other')]:
            subset = frame[frame.target.isin([1, negative])]
            rows.append(dict(scope=scope, arm=arm, comparison=label, n=len(subset),
                             auroc=roc_auc_score(subset.target.eq(1), subset.score)))
    pd.DataFrame(rows).to_csv(out / 'diagnostic_contrasts.csv', index=False)
    rows = []
    for scope, frame in [('all_selected', people), ('device_protocol_matched', people[people.matched])]:
        rows.append(dict(scope=scope, model='prior binary_exposure three-seed mean; trained on all-device folds',
                         **score_metrics(frame.assign(score=frame.cnn_binary_exposure_oof_score))))
    pd.DataFrame(rows).to_csv(out / 'prior_cnn_descriptive_metrics.csv', index=False)
    verification = json.loads((out / 'verification.json').read_text())
    verification['hashes'].update({p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in out.glob('*.csv')})
    verification['contrast_script_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    (out / 'verification.json').write_text(json.dumps(verification, indent=2))
    print('Diagnostic contrasts and existing CNN context saved; no fitting.')


if __name__ == '__main__':
    main()
