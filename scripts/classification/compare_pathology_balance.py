"""Single locked phase+HR weighting comparison; no diagnosis input at inference."""
from pathlib import Path
import sys
import json
import hashlib
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'scripts'))
from models.prototype_stroke_features import FEATURES
from run_phase_nested_threshold import sensitivity_threshold

OUT = ROOT / 'data/processed/pathology_balance_v1'
NEURO = ['CIPN', 'PD', 'RIL']


def weights_for(train):
    weights = pd.Series(0., index=train.index)
    for target, mass in [(0, .25), (1, .5)]:
        mask = train.target.eq(target)
        assert mask.any()
        weights.loc[mask] = mass / mask.sum()
    other = train.target.eq(2)
    counts = train.loc[other, 'pathology'].value_counts()
    assert len(counts)
    weights.loc[other] = train.loc[other, 'pathology'].map(.25 / len(counts) / counts)
    assert np.isclose(weights.sum(), 1.) and weights.gt(0).all()
    return weights * len(train)


def fit(train):
    model = make_pipeline(SimpleImputer(strategy='median', add_indicator=True),
                          StandardScaler(), LogisticRegression(C=1., max_iter=3000,
                          random_state=20260909))
    return model.fit(train[FEATURES], train.target.eq(1),
                     logisticregression__sample_weight=weights_for(train))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    sources = [ROOT / 'data/processed/directional_hr_v1/participants_main.csv',
               ROOT / 'data/processed/directional_hr_v1/predictions.csv',
               ROOT / 'docs/classification/PATHOLOGY_BALANCE.md', Path(__file__),
               ROOT / 'models/prototype_stroke_features.py',
               ROOT / 'scripts/run_phase_nested_threshold.py']
    manifest = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    (OUT / 'manifest.json').write_text(json.dumps(manifest, indent=2))
    people = pd.read_csv(sources[0])
    old = pd.read_csv(sources[1])
    baseline = old[old.variant.eq('main') & old.arm.eq('nuisance_cadence_phase_hr')].copy()
    baseline['arm'] = 'baseline'
    results, inners, thresholds, ledger = [baseline], [], [], []
    for scope, data in [('all_selected', people), ('device_protocol_matched', people[people.matched])]:
        assert data.participant.is_unique
        for outer in sorted(data.fold.unique()):
            train, test = data[data.fold.ne(outer)], data[data.fold.eq(outer)]
            assert not set(train.participant) & set(test.participant)
            assert not set(train.loc[train.target.eq(2), 'pathology']) & set(test.loc[test.target.eq(2), 'pathology'])
            parts = []
            for inner, (a, b) in enumerate(StratifiedKFold(3, shuffle=True, random_state=20260909).split(train, train.target)):
                fitted, val = train.iloc[a], train.iloc[b]
                assert not set(fitted.participant) & set(val.participant)
                model = fit(fitted)
                row = val[['participant', 'target', 'pathology']].copy()
                row['score'] = model.predict_proba(val[FEATURES])[:, 1]
                row['scope'], row['outer_fold'], row['inner_fold'] = scope, int(outer), inner
                parts.append(row)
            scores = pd.concat(parts)
            assert scores.participant.is_unique and set(scores.participant) == set(train.participant)
            inners.append(scores)
            threshold = sensitivity_threshold(scores.loc[scores.target.eq(1), 'score'])
            thresholds.append(dict(scope=scope, fold=int(outer), threshold=threshold))
            weight = weights_for(train) / len(train)
            for pathology, mass in weight.groupby(train.pathology).sum().items():
                ledger.append(dict(scope=scope, fold=int(outer), pathology=pathology, mass=mass))
            model = fit(train)
            row = test[['participant', 'target', 'pathology', 'fold']].copy()
            row['score'] = model.predict_proba(test[FEATURES])[:, 1]
            row['threshold'], row['scope'], row['arm'] = threshold, scope, 'pathology_balanced'
            row['positive'] = row.score.ge(threshold)
            results.append(row)
    predictions = pd.concat(results, ignore_index=True)
    metrics = []
    for (scope, arm), g in predictions.groupby(['scope', 'arm']):
        assert g.participant.is_unique
        base = baseline[baseline.scope.eq(scope)].set_index('participant')
        assert set(g.participant) == set(base.index)
        for col in ['target', 'pathology', 'fold']:
            assert (g.set_index('participant')[col].sort_index() == base[col].sort_index()).all()
        metrics.append(dict(scope=scope, arm=arm, n=len(g),
            stroke_tp=int(g.loc[g.target.eq(1), 'positive'].sum()),
            healthy_fp=int(g.loc[g.target.eq(0), 'positive'].sum()),
            other_fp=int(g.loc[g.target.eq(2), 'positive'].sum()),
            neuro_fp=int(g.loc[g.pathology.isin(NEURO), 'positive'].sum()),
            neuro_n=int(g.pathology.isin(NEURO).sum())))
    metrics = pd.DataFrame(metrics)
    gates = []
    for scope, g in metrics.groupby('scope'):
        g = g.set_index('arm'); a, b = g.loc['baseline'], g.loc['pathology_balanced']
        checks = dict(neuro_reduction=bool((a.neuro_fp-b.neuro_fp)/a.neuro_n >= .05),
                      stroke_preserved=bool(b.stroke_tp >= a.stroke_tp),
                      healthy_preserved=bool(b.healthy_fp <= a.healthy_fp),
                      other_preserved=bool(b.other_fp <= a.other_fp))
        gates.append(dict(scope=scope, checks=checks, passed=all(checks.values())))
    for name, frame in [('predictions', predictions), ('inner_predictions', pd.concat(inners)),
                        ('thresholds', pd.DataFrame(thresholds)), ('training_weights', pd.DataFrame(ledger)), ('metrics', metrics)]:
        frame.to_csv(OUT / f'{name}.csv', index=False)
    predictions.groupby(['scope', 'arm', 'pathology']).agg(n=('participant', 'size'), positive=('positive', 'sum')).to_csv(OUT / 'pathology_counts.csv')
    decision = dict(passed=all(g['passed'] for g in gates), gates=gates, fits=24,
                    independent_validation=False)
    (OUT / 'decision.json').write_text(json.dumps(decision, indent=2))
    print(metrics.to_string(index=False))
    print(json.dumps(decision, indent=2))


if __name__ == '__main__':
    main()
