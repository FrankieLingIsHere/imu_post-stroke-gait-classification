"""Participant-disjoint Voisard measurement/nuisance comparison, research only.

Uses existing differential folds and corrected event-bound feature helpers.
Never changes release weights or infers missing metadata from diagnosis.
"""
from pathlib import Path
import hashlib
import json
import sys

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, brier_score_loss
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.features.voisard import (
    _events_outside_uturn, _stride_time_stats, _walking_bounds,
    _straight_walk_span_samples, _channel_accel_rms,
)

OUT = ROOT / 'data/processed/conditional_gait_v1'
P = ROOT / 'data/processed'
NUISANCE = ['age', 'xsens_fraction', 'protocol_length_m']
GAIT = ['cadence', 'stride_cv', 'stride_time_asymmetry', 'lb_rms']
ARMS = {'nuisance': NUISANCE, 'cadence_only': ['cadence'],
        'nuisance_cadence': NUISANCE + ['cadence'],
        'lb_rms_only': ['lb_rms'], 'gait': GAIT, 'combined': NUISANCE + GAIT}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def trial_features(path):
    m = json.loads(path.read_text(encoding='utf-8'))
    frequency = float(m['freq'])
    if frequency <= 0:
        raise ValueError('Invalid frequency')
    lp, la = _events_outside_uturn(m.get('leftGaitEvents') or [], m['uturnBoundaries'])
    rp, ra = _events_outside_uturn(m.get('rightGaitEvents') or [], m['uturnBoundaries'])
    lm, lc, ln = _stride_time_stats(lp, la, frequency)
    rm, rc, rn = _stride_time_stats(rp, ra, frequency)
    span = _straight_walk_span_samples(lp + rp, la + ra, m['uturnBoundaries'])
    bounds = _walking_bounds(lp + rp, la + ra)
    trial = path.stem.removesuffix('_meta')
    sensor = m.get('sensor')
    if sensor not in ('MTw Awinda XSens', 'TechnoConcept'):
        raise ValueError(f'Unmapped sensor: {sensor}')
    return dict(participant='voisard_2025:' + m['subject'], trial=trial,
                age=m.get('age'), sensor=sensor, protocol=m.get('protocol'),
                pathology_raw=m['pathologyKey'], xsens_fraction=float(sensor == 'MTw Awinda XSens'),
                protocol_length_m=float(m['protocol'].split('m')[0]),
                cadence=(ln + rn) * 60 * frequency / span if span > 0 else np.nan,
                stride_cv=np.mean([lc, rc]),
                stride_time_asymmetry=abs(lm-rm)/((lm+rm)/2) if lm+rm > 0 else np.nan,
                lb_rms=_channel_accel_rms(path.parent, trial, 'LB', bounds) if bounds else np.nan,
                event_count=ln+rn)


def score_metrics(frame):
    y = frame.target.eq(1).to_numpy()
    p = frame.score.to_numpy()
    pos = p >= .5
    return dict(n=len(frame), auroc=float(roc_auc_score(y, p)) if len(set(y)) == 2 else np.nan,
                brier=float(brier_score_loss(y, p)),
                sensitivity=float(pos[y].mean()) if y.any() else np.nan,
                healthy_specificity=float((~pos[frame.target.eq(0)]).mean()) if frame.target.eq(0).any() else np.nan,
                other_fpr=float(pos[frame.target.eq(2)].mean()) if frame.target.eq(2).any() else np.nan)


def run_cv(people, scope):
    outputs = []
    for fold in sorted(people.fold.unique()):
        train, test = people[people.fold != fold], people[people.fold == fold]
        assert not set(train.participant) & set(test.participant)
        assert not set(train.loc[train.target.eq(2), 'pathology']) & set(test.loc[test.target.eq(2), 'pathology'])
        if set(train.target) != {0, 1, 2}:
            raise ValueError(f'{scope} fold {fold}: missing training target')
        # Equal total positive/negative weight; split negatives equally across
        # healthy and other pathology. One observation per participant.
        w = train.target.map({t: mass / train.target.eq(t).sum() for t, mass in [(0,.25),(1,.5),(2,.25)]}) * len(train)
        for arm, columns in ARMS.items():
            model = make_pipeline(SimpleImputer(strategy='median', add_indicator=True),
                                  StandardScaler(), LogisticRegression(C=1., max_iter=3000, random_state=20260909))
            model.fit(train[columns], train.target.eq(1), logisticregression__sample_weight=w)
            result = test[['participant', 'target', 'pathology', 'fold']].copy()
            result['score'] = model.predict_proba(test[columns])[:, 1]
            result['arm'], result['scope'] = arm, scope
            outputs.append(result)
    return pd.concat(outputs, ignore_index=True)


def main():
    OUT.mkdir(exist_ok=True)
    if (OUT / 'metrics.csv').exists():
        raise FileExistsError('Completed comparison exists; inspect rather than rerun')
    folds_path = P / 'differential_gait_v1/participant_folds.csv'
    folds = pd.read_csv(folds_path)
    assert folds.participant.is_unique
    primary = pd.read_csv(P / 'validated_window_metadata.csv')
    primary = primary[primary.dataset_id.eq('voisard_2025')]
    other = pd.read_csv(P / 'differential_gait_v1/other_metadata.csv')
    selected = pd.concat([primary[['participant_key','trial_id']], other[['participant_key','trial_id']]]).drop_duplicates()
    selected = set(map(tuple, selected.to_numpy()))
    paths = sorted((ROOT / 'data/raw/voisard_2025/data').glob('*/*/*/*/*_meta.json'))
    lock = dict(scope='Voisard development, same prior participant/pathology folds; no external source validation',
                arms=ARMS, classifier='fixed LogisticRegression C=1; train-only median+missing indicator and scaling',
                weighting='stroke .5, healthy .25, other .25 total mass', threshold=.5,
                feature_source='reference event annotations and corrected straight-walk lower-back RMS; not autonomous lower-back extraction',
                aggregation='mean across trials represented in prior CNN inputs; retain missing features',
                matched_scope='participants with every selected trial TechnoConcept and exact 10.0m - uturn - 10.0m protocol',
                seed=20260909, hashes={str(p.relative_to(ROOT)):sha(p) for p in [Path(__file__), ROOT/'src/features/voisard.py', folds_path, P/'validated_window_metadata.csv', P/'differential_gait_v1/other_metadata.csv']})
    (OUT / 'protocol.json').write_text(json.dumps(lock, indent=2), encoding='utf-8')
    rows, census = [], []
    for path in paths:
        m = json.loads(path.read_text())
        key = ('voisard_2025:'+m['subject'], path.stem.removesuffix('_meta'))
        used = key in selected
        census.append(dict(participant=key[0], trial=key[1], selected=used, sensor=m.get('sensor'), protocol=m.get('protocol'), metadata_sha256=sha(path)))
        if used:
            row = trial_features(path)
            raw = path.parent / (key[1]+'_raw_data_LB.txt')
            row['raw_sha256'] = sha(raw) if raw.exists() else None
            rows.append(row)
    trials = pd.DataFrame(rows)
    if set(map(tuple, trials[['participant','trial']].to_numpy())) != selected:
        raise ValueError('Selected trial join incomplete')
    pd.DataFrame(census).to_csv(OUT/'trial_census.csv', index=False)
    trials.to_csv(OUT/'trial_features.csv', index=False)
    people = trials.groupby('participant')[list(dict.fromkeys(NUISANCE + GAIT))].mean().reset_index()
    detail = trials.groupby('participant').agg(trials=('trial','size'), devices=('sensor',lambda s:'|'.join(sorted(set(s)))), protocols=('protocol',lambda s:'|'.join(sorted(set(s)))))
    people = folds.merge(people, on='participant', how='left', validate='one_to_one').merge(detail,on='participant',how='left',validate='one_to_one')
    assert len(people) == len(folds) and people.trials.notna().all()
    assert set(trials.pathology_raw) == {'HS','CVA','ACL','CIPN','HOA','KOA','PD','RIL'}
    people['matched'] = people.devices.eq('TechnoConcept') & people.protocols.eq('10.0m - uturn - 10.0m')
    # Preserve CNN identity: matched single-member OOF objective benchmark,
    # averaged across its three seeds. Never confuse this with the release.
    cnn = pd.read_csv(P/'differential_gait_v1/participant_predictions.csv')
    cnn = cnn[cnn.arm.eq('binary_exposure')].groupby('participant').score.mean().rename('cnn_binary_exposure_oof_score')
    people = people.merge(cnn,on='participant',how='left',validate='one_to_one')
    assert people.cnn_binary_exposure_oof_score.notna().all()
    people.to_csv(OUT/'participant_contract.csv',index=False)
    people.groupby(['devices','protocols','target'],dropna=False).size().rename('participants').to_csv(OUT/'overlap.csv')
    missing = people.groupby('target')[NUISANCE+GAIT].agg(lambda x:int(x.isna().sum()))
    missing.to_csv(OUT/'missingness.csv')
    print('CONTRACT',len(people),'people',len(trials),'trials; matched',people.groupby('target').matched.sum().to_dict(),flush=True)
    output = [run_cv(people,'all_selected'), run_cv(people[people.matched], 'device_protocol_matched')]
    pred = pd.concat(output,ignore_index=True)
    assert not pred.duplicated(['scope','arm','participant']).any()
    pred.to_csv(OUT/'predictions.csv',index=False)
    metrics=[]
    for (scope,arm), frame in pred.groupby(['scope','arm']):
        metrics.append(dict(scope=scope,arm=arm,**score_metrics(frame)))
    result=pd.DataFrame(metrics)
    result.to_csv(OUT/'metrics.csv',index=False)
    path_rows=[]
    for (scope,arm,pathology), frame in pred.groupby(['scope','arm','pathology']):
        path_rows.append(dict(scope=scope,arm=arm,pathology=pathology,n=len(frame),positive_fraction=float(frame.score.ge(.5).mean())))
    pd.DataFrame(path_rows).to_csv(OUT/'pathology_metrics.csv',index=False)
    # Paired stratified participant bootstrap of fixed OOF predictions;
    # uncertainty conditional on these fitted folds, not model-selection error.
    intervals=[]
    for scope in pred.scope.unique():
        wide=pred[pred.scope.eq(scope)].pivot(index=['participant','target'],columns='arm',values='score').reset_index()
        rng=np.random.default_rng(20260909)
        for a,b in [('combined','nuisance'),('combined','nuisance_cadence'),('gait','cadence_only')]:
            values=[]
            for _ in range(1000):
                ix=np.concatenate([rng.choice(np.flatnonzero(wide.target.eq(t)),wide.target.eq(t).sum(),replace=True) for t in (0,1,2)])
                f=wide.iloc[ix]; ma=score_metrics(f.assign(score=f[a])); mb=score_metrics(f.assign(score=f[b]))
                values.append([ma[k]-mb[k] for k in ['auroc','sensitivity','healthy_specificity','other_fpr']])
            for i,k in enumerate(['auroc','sensitivity','healthy_specificity','other_fpr']):
                lo,hi=np.quantile(np.asarray(values)[:,i],[.025,.975])
                intervals.append(dict(scope=scope,comparison=a+' minus '+b,metric=k,low=lo,high=hi))
    pd.DataFrame(intervals).to_csv(OUT/'paired_intervals.csv',index=False)
    (OUT/'verification.json').write_text(json.dumps(dict(participants=len(people),selected_trials=len(trials),raw_census_trials=len(census),unique_predictions=True,participant_and_pathology_disjoint=True,hashes={p.name:sha(p) for p in OUT.glob('*.csv')}),indent=2))
    print(result.to_string(index=False),flush=True)


if __name__ == '__main__':
    main()
