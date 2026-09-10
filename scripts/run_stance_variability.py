"""One-predictor extension under the locked stance variability protocol."""
from pathlib import Path
import sys
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/'scripts'))
from src.features.bilateral_phase import extract_phase
from src.features.stance_variability import stance_cv
from run_phase_nested_threshold import ARMS, sensitivity_threshold
from run_conditional_gait_comparison import sha

OUT=ROOT/'data/processed/stance_variability_v1'


def fit_model(train, columns):
    weights=train.target.map({t:m/train.target.eq(t).sum() for t,m in [(0,.25),(1,.5),(2,.25)]})*len(train)
    model=make_pipeline(SimpleImputer(strategy='median',add_indicator=True),StandardScaler(),
                        LogisticRegression(C=1.,max_iter=3000,random_state=20260909))
    return model.fit(train[columns],train.target.eq(1),logisticregression__sample_weight=weights)


def main():
    OUT.mkdir(exist_ok=True)
    phase=ROOT/'data/processed/bilateral_phase_v1'
    prior=ROOT/'data/processed/phase_nested_threshold_v1'
    inputs=[phase/'participant_features.csv',phase/'trial_features.csv',prior/'predictions.csv',
            ROOT/'docs/STANCE_VARIABILITY_PROTOCOL_2026-09-09.md',Path(__file__),
            ROOT/'src/features/stance_variability.py',ROOT/'src/features/bilateral_phase.py']
    (OUT/'manifest.json').write_text(json.dumps({str(p.relative_to(ROOT)):sha(p) for p in inputs},indent=2))
    people=pd.read_csv(phase/'participant_features.csv')
    trials=pd.read_csv(phase/'trial_features.csv')
    paths={p.stem.removesuffix('_meta'):p for p in (ROOT/'data/raw/voisard_2025/data').glob('*/*/*/*/*_meta.json')}
    rows=[]
    for r in trials.itertuples():
        p=paths[r.trial]
        assert sha(p)==r.metadata_sha256
        m=json.loads(p.read_text(encoding='utf-8'))
        features=extract_phase(m.get('leftGaitEvents') or [],m.get('rightGaitEvents') or [],m['uturnBoundaries'],m['freq'],return_stances=True)
        cv=stance_cv(features.pop('stance_segments'))
        if not r.reference_valid:
            cv['stance_duration_cv']=np.nan
        rows.append(dict(participant=r.participant,trial=r.trial,reference_valid=r.reference_valid,**cv))
    ledger=pd.DataFrame(rows)
    ledger.to_csv(OUT/'trial_features.csv',index=False)
    people=people.merge(ledger.groupby('participant').stance_duration_cv.mean(),on='participant',validate='one_to_one')
    assert len(people)==259
    people.to_csv(OUT/'participant_features.csv',index=False)
    coverage=people.assign(available=people.stance_duration_cv.notna()).groupby(['target','pathology']).agg(n=('participant','size'),available=('available','sum'))
    coverage['fraction']=coverage.available/coverage.n
    coverage.to_csv(OUT/'coverage.csv')
    print(coverage.to_string())
    if coverage.fraction.min()<.95:
        (OUT/'decision.json').write_text(json.dumps({'passed':False,'reason':'coverage failed; no fits'}))
        return
    predictions=[]; inner_rows=[]; thresholds=[]
    for scope,data in [('all_selected',people),('device_protocol_matched',people[people.matched])]:
        for fold in sorted(data.fold.unique()):
            train,test=data[data.fold.ne(fold)],data[data.fold.eq(fold)]
            assert not set(train.participant)&set(test.participant)
            assert not set(train.loc[train.target.eq(2),'pathology'])&set(test.loc[test.target.eq(2),'pathology'])
            splits=list(StratifiedKFold(3,shuffle=True,random_state=20260909).split(train,train.target))
            for base in ['nuisance_cadence_phase','combined_phase']:
                arm=base+'_cv'; columns=ARMS[base]+['stance_duration_cv']; pieces=[]
                for inner,(fit_idx,val_idx) in enumerate(splits):
                    fit,val=train.iloc[fit_idx],train.iloc[val_idx]
                    assert not set(fit.participant)&set(val.participant)
                    model=fit_model(fit,columns)
                    row=val[['participant','target','pathology','fold']].copy()
                    row['score']=model.predict_proba(val[columns])[:,1]
                    row['scope'],row['arm'],row['outer_fold'],row['inner_fold']=scope,arm,fold,inner
                    pieces.append(row)
                inner_scores=pd.concat(pieces)
                assert inner_scores.participant.nunique()==len(train)
                inner_rows.append(inner_scores)
                stroke=inner_scores.loc[inner_scores.target.eq(1),'score']
                threshold=sensitivity_threshold(stroke)
                thresholds.append(dict(scope=scope,arm=arm,fold=int(fold),threshold=threshold,inner_sensitivity=float(stroke.ge(threshold).mean())))
                model=fit_model(train,columns)
                row=test[['participant','target','pathology','fold']].copy()
                row['score']=model.predict_proba(test[columns])[:,1]
                row['scope'],row['arm'],row['threshold']=scope,arm,threshold
                row['positive']=row.score.ge(threshold)
                predictions.append(row)
    old=pd.read_csv(prior/'predictions.csv')
    predictions=pd.concat([old,*predictions],ignore_index=True)
    predictions.to_csv(OUT/'predictions.csv',index=False)
    pd.concat(inner_rows).to_csv(OUT/'inner_predictions.csv',index=False)
    pd.DataFrame(thresholds).to_csv(OUT/'thresholds.csv',index=False)
    metrics=[]
    for (scope,arm),g in predictions.groupby(['scope','arm']):
        for rule,pos in [('nested',g.positive),('fixed_0.5',g.score.ge(.5))]:
            counts={t:int(pos[g.target.eq(t)].sum()) for t in [0,1,2]}
            metrics.append(dict(scope=scope,arm=arm,rule=rule,stroke_tp=counts[1],healthy_fp=counts[0],other_fp=counts[2],sensitivity=counts[1]/g.target.eq(1).sum(),other_fpr=counts[2]/g.target.eq(2).sum()))
    metrics=pd.DataFrame(metrics)
    metrics.to_csv(OUT/'metrics.csv',index=False)
    predictions.groupby(['scope','arm','target','pathology']).agg(n=('participant','size'),positive=('positive','sum')).to_csv(OUT/'pathology_counts.csv')
    gates=[]
    for scope,g in metrics[metrics.rule.eq('nested')].groupby('scope'):
        g=g.set_index('arm'); b=g.loc['nuisance_cadence_phase_cv']
        comparisons=[]
        for base in ['nuisance_cadence','nuisance_cadence_phase']:
            a=g.loc[base]
            comparisons.append(dict(baseline=base,stroke_tp_change=int(b.stroke_tp-a.stroke_tp),healthy_fp_change=int(b.healthy_fp-a.healthy_fp),other_fpr_reduction=float(a.other_fpr-b.other_fpr),passed=bool(b.sensitivity>=.9 and b.stroke_tp>=a.stroke_tp and b.healthy_fp<=a.healthy_fp and a.other_fpr-b.other_fpr>=.05)))
        gates.append(dict(scope=scope,comparisons=comparisons,passed=all(x['passed'] for x in comparisons)))
    decision=dict(passed=all(x['passed'] for x in gates),gates=gates,inner_fits=36,outer_fits=12,participants=259,available_trials=int(ledger.stance_duration_cv.notna().sum()))
    (OUT/'decision.json').write_text(json.dumps(decision,indent=2))
    print(metrics[metrics.rule.eq('nested')].to_string(index=False))
    print(json.dumps(decision,indent=2))


if __name__=='__main__':
    main()
