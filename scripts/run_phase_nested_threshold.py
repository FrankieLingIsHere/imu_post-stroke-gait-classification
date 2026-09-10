"""Training-only sensitivity threshold selection for fixed phase feature arms."""
from pathlib import Path
import sys
import json
import math
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'scripts'))
from run_conditional_gait_comparison import NUISANCE, GAIT, sha
from src.features.bilateral_phase import FEATURES

OUT = ROOT / 'data/processed/phase_nested_threshold_v1'
ARMS = {'nuisance_cadence': NUISANCE + ['cadence'],
        'nuisance_cadence_phase': NUISANCE + ['cadence'] + FEATURES,
        'combined': NUISANCE + GAIT, 'combined_phase': NUISANCE + GAIT + FEATURES}


def sensitivity_threshold(stroke_scores, target=.9):
    scores = np.asarray(stroke_scores, dtype=float)
    if not len(scores) or not np.isfinite(scores).all() or not 0 < target <= 1:
        raise ValueError('Invalid threshold inputs')
    return float(np.sort(scores)[::-1][math.ceil(target*len(scores))-1])


def main():
    OUT.mkdir(exist_ok=True)
    source = ROOT / 'data/processed/bilateral_phase_v1'
    people = pd.read_csv(source / 'participant_features.csv')
    old = pd.read_csv(source / 'predictions.csv')
    manifest = {str(p.relative_to(ROOT)): sha(p) for p in [
        source / 'participant_features.csv', source / 'predictions.csv',
        ROOT / 'docs/PHASE_NESTED_THRESHOLD_PROTOCOL_2026-09-09.md', Path(__file__)]}
    (OUT / 'manifest.json').write_text(json.dumps(manifest, indent=2))
    inner_rows, thresholds, outer_rows = [], [], []
    for scope, data in [('all_selected', people), ('device_protocol_matched', people[people.matched])]:
        for outer in sorted(data.fold.unique()):
            train, test = data[data.fold.ne(outer)], data[data.fold.eq(outer)]
            assert not set(train.participant) & set(test.participant)
            assert not set(train.loc[train.target.eq(2),'pathology']) & set(test.loc[test.target.eq(2),'pathology'])
            splits = list(StratifiedKFold(3, shuffle=True, random_state=20260909).split(train, train.target))
            for arm, columns in ARMS.items():
                parts = []
                for inner, (fit_idx, val_idx) in enumerate(splits):
                    fit, val = train.iloc[fit_idx], train.iloc[val_idx]
                    assert set(fit.target)=={0,1,2}
                    assert not set(fit.participant) & set(val.participant)
                    weights = fit.target.map({t: m / fit.target.eq(t).sum() for t,m in [(0,.25),(1,.5),(2,.25)]}) * len(fit)
                    model = make_pipeline(SimpleImputer(strategy='median', add_indicator=True), StandardScaler(),
                                          LogisticRegression(C=1., max_iter=3000, random_state=20260909))
                    model.fit(fit[columns], fit.target.eq(1), logisticregression__sample_weight=weights)
                    row = val[['participant','target','pathology','fold']].copy()
                    row['score'] = model.predict_proba(val[columns])[:,1]
                    row['scope'], row['arm'], row['outer_fold'], row['inner_fold'] = scope, arm, outer, inner
                    parts.append(row)
                scores = pd.concat(parts)
                assert scores.participant.nunique()==len(train)==len(scores)
                inner_rows.append(scores)
                stroke = scores.loc[scores.target.eq(1),'score']
                threshold = sensitivity_threshold(stroke)
                thresholds.append(dict(scope=scope, arm=arm, fold=int(outer), threshold=threshold,
                    inner_stroke_n=len(stroke), inner_sensitivity=float(stroke.ge(threshold).mean())))
                result = old[old.scope.eq(scope)&old.arm.eq(arm)&old.fold.eq(outer)].copy()
                assert set(result.participant)==set(test.participant)
                result['threshold'] = threshold
                result['positive'] = result.score.ge(threshold)
                outer_rows.append(result)
    pd.concat(inner_rows).to_csv(OUT / 'inner_predictions.csv', index=False)
    pd.DataFrame(thresholds).to_csv(OUT / 'thresholds.csv', index=False)
    predictions = pd.concat(outer_rows)
    assert len(predictions)==1612
    predictions.to_csv(OUT / 'predictions.csv', index=False)
    metrics=[]
    for (scope, arm), g in predictions.groupby(['scope','arm']):
        counts = {t: int(g.loc[g.target.eq(t),'positive'].sum()) for t in [0,1,2]}
        metrics.append(dict(scope=scope, arm=arm, stroke_tp=counts[1], healthy_fp=counts[0], other_fp=counts[2],
            sensitivity=counts[1]/g.target.eq(1).sum(), other_fpr=counts[2]/g.target.eq(2).sum()))
    metrics=pd.DataFrame(metrics)
    metrics.to_csv(OUT / 'metrics.csv', index=False)
    predictions.groupby(['scope','arm','target','pathology']).agg(n=('participant','size'),positive=('positive','sum')).to_csv(OUT / 'pathology_counts.csv')
    gates=[]
    for scope, g in metrics.groupby('scope'):
        indexed = g.set_index('arm')
        a, b = indexed.loc['nuisance_cadence'], indexed.loc['nuisance_cadence_phase']
        gates.append(dict(scope=scope, passed=bool(b.sensitivity>=.9 and b.stroke_tp>=a.stroke_tp and b.healthy_fp<=a.healthy_fp and a.other_fpr-b.other_fpr>=.05)))
    decision=dict(passed=all(g['passed'] for g in gates), gates=gates, inner_fits=72, participants=259)
    (OUT / 'decision.json').write_text(json.dumps(decision,indent=2))
    print(metrics.to_string(index=False))
    print(json.dumps(decision,indent=2))


if __name__=='__main__':
    main()
