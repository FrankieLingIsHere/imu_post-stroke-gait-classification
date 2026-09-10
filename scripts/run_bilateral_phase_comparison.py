"""Execute the locked reference-assisted phase feasibility comparison."""
from pathlib import Path
import sys
import json
import hashlib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'scripts'))
import run_conditional_gait_comparison as baseline
from src.features.bilateral_phase import extract_phase, FEATURES

OUT = ROOT / 'data/processed/bilateral_phase_v1'


def main():
    OUT.mkdir(exist_ok=True)
    protocol = ROOT / 'docs/BILATERAL_PHASE_PROTOCOL_2026-09-09.md'
    manifest = {'protocol_sha256': baseline.sha(protocol), 'inputs': {}}
    for name in ['packet_alignment_v1/participant_contract.csv',
                 'conditional_gait_v1/trial_features.csv',
                 'lower_back_events_v1/trial_metrics.csv']:
        manifest['inputs'][name] = baseline.sha(ROOT / 'data/processed' / name)
    (OUT / 'manifest.json').write_text(json.dumps(manifest, indent=2))
    people = pd.read_csv(ROOT / 'data/processed/packet_alignment_v1/participant_contract.csv')
    selected = pd.read_csv(ROOT / 'data/processed/conditional_gait_v1/trial_features.csv')
    validity = pd.read_csv(ROOT / 'data/processed/lower_back_events_v1/trial_metrics.csv')
    valid = validity.groupby('trial').reference_valid.all().to_dict()
    paths = {p.stem.removesuffix('_meta'): p for p in
             (ROOT / 'data/raw/voisard_2025/data').glob('*/*/*/*/*_meta.json')}
    rows = []
    for row in selected.itertuples():
        path = paths[row.trial]
        m = json.loads(path.read_text(encoding='utf-8'))
        features = extract_phase(m.get('leftGaitEvents') or [], m.get('rightGaitEvents') or [],
                                 m['uturnBoundaries'], float(m['freq']))
        reference_valid = valid[row.trial]
        if not reference_valid:
            features.update({k: np.nan for k in FEATURES})
        rows.append(dict(participant=row.participant, trial=row.trial,
                         reference_valid=reference_valid, metadata_sha256=baseline.sha(path), **features))
    trials = pd.DataFrame(rows)
    trials['complete_phase'] = trials[FEATURES].notna().all(axis=1)
    trials.to_csv(OUT / 'trial_features.csv', index=False)
    people = people.merge(trials.groupby('participant')[FEATURES].mean(), on='participant', validate='one_to_one')
    assert len(people) == 259 and people.participant.nunique() == 259
    people.to_csv(OUT / 'participant_features.csv', index=False)
    joined = trials.merge(people[['participant', 'target', 'pathology']], on='participant', validate='many_to_one')
    joined.groupby(['target', 'pathology']).agg(trials=('trial','size'),
        complete_trials=('complete_phase','sum'), invalid_reference=('reference_valid',lambda x: (~x).sum()),
        malformed_pairs=('malformed_pairs','sum'), invalid_cycles=('invalid_cycles','sum'),
        valid_cycles=('valid_cycles','sum')).to_csv(OUT / 'coverage.csv')
    baseline.ARMS = {'nuisance_cadence': baseline.NUISANCE + ['cadence'],
                     'nuisance_cadence_phase': baseline.NUISANCE + ['cadence'] + FEATURES,
                     'combined': baseline.NUISANCE + baseline.GAIT,
                     'combined_phase': baseline.NUISANCE + baseline.GAIT + FEATURES}
    predictions = pd.concat([baseline.run_cv(people, 'all_selected'),
                             baseline.run_cv(people[people.matched], 'device_protocol_matched')])
    predictions.to_csv(OUT / 'predictions.csv', index=False)
    old = pd.read_csv(ROOT / 'data/processed/packet_alignment_v1/feature_predictions.csv')
    merged = predictions.merge(old, on=['participant','target','pathology','fold','arm','scope'], suffixes=('_new','_old'))
    assert len(merged) == 2 * (259 + 144)
    delta = float(abs(merged.score_new-merged.score_old).max())
    assert delta < 1e-10, delta
    metrics = []
    for (scope, arm), group in predictions.groupby(['scope', 'arm']):
        metrics.append(dict(scope=scope, arm=arm, **baseline.score_metrics(group),
            stroke_tp=int(((group.target==1)&(group.score>=.5)).sum()),
            healthy_fp=int(((group.target==0)&(group.score>=.5)).sum()),
            other_fp=int(((group.target==2)&(group.score>=.5)).sum())))
    metrics = pd.DataFrame(metrics)
    metrics.to_csv(OUT / 'metrics.csv', index=False)
    predictions.assign(positive=predictions.score.ge(.5)).groupby(['scope','arm','target','pathology']).agg(
        participants=('participant','size'), positives=('positive','sum')).to_csv(OUT / 'pathology_counts.csv')
    gates = []
    for scope, frame in metrics.groupby('scope'):
        a = frame.set_index('arm').loc['nuisance_cadence']
        b = frame.set_index('arm').loc['nuisance_cadence_phase']
        gates.append(dict(scope=scope, other_fpr_reduction=float(a.other_fpr-b.other_fpr),
                          stroke_tp_change=int(b.stroke_tp-a.stroke_tp),
                          healthy_fp_change=int(b.healthy_fp-a.healthy_fp),
                          passed=bool(a.other_fpr-b.other_fpr>=.05 and b.stroke_tp>=a.stroke_tp and b.healthy_fp<=a.healthy_fp)))
    result = dict(gates=gates, passed=all(g['passed'] for g in gates), baseline_max_score_delta=delta,
                  participants_missing_any_phase=int(people[FEATURES].isna().any(axis=1).sum()),
                  trials=len(trials), complete_trials=int(trials.complete_phase.sum()))
    (OUT / 'decision.json').write_text(json.dumps(result, indent=2))
    print(metrics.to_string(index=False))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
