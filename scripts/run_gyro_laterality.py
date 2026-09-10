"""Conditional event-side feasibility, using reference times, never diagnosis."""
from pathlib import Path
import sys,json
import numpy as np
import pandas as pd
from scipy.signal import butter,sosfiltfilt
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import SVC

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from src.features.voisard import _events_outside_uturn,_walking_bounds
from run_conditional_gait_comparison import sha
OUT=ROOT/'data/processed/gyro_laterality_v1'
COLS=[f'f{i}' for i in range(6)]


def gyro_features(gyro,contacts):
    x=np.asarray(gyro,dtype=float);ic=np.asarray(contacts,dtype=int)
    if x.ndim!=2 or x.shape[1]!=2 or not np.isfinite(x).all():
        raise ValueError('Invalid gyro bout')
    if len(set(ic))!=len(ic) or (ic<0).any() or (ic>=len(x)).any():
        raise ValueError('Invalid contact indices')
    filtered=sosfiltfilt(butter(4,[.5,2],fs=100,btype='bandpass',output='sos'),x,axis=0)
    first=np.gradient(filtered,axis=0);second=np.gradient(first,axis=0)
    return np.c_[filtered,first,second][ic]


def main():
    OUT.mkdir(exist_ok=True)
    phase=ROOT/'data/processed/bilateral_phase_v1'
    people=pd.read_csv(phase/'participant_features.csv');trials=pd.read_csv(phase/'trial_features.csv')
    inputs=[Path(__file__),ROOT/'docs/GYRO_LATERALITY_PROTOCOL_2026-09-09.md',phase/'participant_features.csv',phase/'trial_features.csv']
    (OUT/'manifest.json').write_text(json.dumps({str(p.relative_to(ROOT)):sha(p) for p in inputs},indent=2))
    paths={p.stem.removesuffix('_meta'):p for p in (ROOT/'data/raw/voisard_2025/data').glob('*/*/*/*/*_meta.json')}
    events=[];ledger=[]
    for r in trials.itertuples():
        p=paths[r.trial];m=json.loads(p.read_text(encoding='utf-8'));assert m['freq']==100
        signal=p.parent/(r.trial+'_processed_data.txt')
        gyro=pd.read_csv(signal,sep='\t',usecols=['LB_Gyr_X','LB_Gyr_Z']).to_numpy()
        lp,la=_events_outside_uturn(m['leftGaitEvents'],m['uturnBoundaries']);rp,ra=_events_outside_uturn(m['rightGaitEvents'],m['uturnBoundaries'])
        expected=sum(map(len,[lp,la,rp,ra]));usable=0;errors=[]
        if r.reference_valid:
            for bout,(left,right) in enumerate([(lp,rp),(la,ra)]):
                combined=left+right
                if not combined:continue
                start=min(e[0] for e in combined);end=max(e[1] for e in combined)+1
                refs=sorted([(int(e[1]),side) for side,side_events in [(0,left),(1,right)] for e in side_events])
                try:
                    if not 0<=start<end<=len(gyro):raise ValueError('Invalid bounds')
                    features=gyro_features(gyro[int(start):int(end)],[i-int(start) for i,s in refs])
                    for (ic,side),feature in zip(refs,features):
                        events.append(dict(participant=r.participant,trial=r.trial,bout=bout,ic=ic,side=side,**dict(zip(COLS,feature))))
                    usable+=len(refs)
                except ValueError as exc:errors.append(str(exc))
        else:errors.append('Invalid reference bounds')
        ledger.append(dict(participant=r.participant,trial=r.trial,expected=expected,usable=usable,errors='|'.join(errors),signal_sha256=sha(signal),metadata_sha256=sha(p)))
    event=pd.DataFrame(events);event.to_csv(OUT/'features.csv',index=False)
    ledger=pd.DataFrame(ledger);ledger.to_csv(OUT/'trial_coverage.csv',index=False)
    event=event.merge(people[['participant','target','pathology','fold','matched']],on='participant',validate='many_to_one')
    predictions=[];fit_counts=[]
    for scope,subset in [('all_selected',people),('device_protocol_matched',people[people.matched])]:
        selected=event[event.participant.isin(subset.participant)]
        for fold in sorted(subset.fold.unique()):
            train,test=selected[selected.fold.ne(fold)],selected[selected.fold.eq(fold)]
            assert not set(train.participant)&set(test.participant)
            assert not set(train.loc[train.target.eq(2),'pathology'])&set(test.loc[test.target.eq(2),'pathology'])
            side_counts=train.groupby(['participant','side']).size()
            eligible=side_counts.groupby(level=0).size().loc[lambda x:x==2].index
            excluded=train.participant.nunique()-len(eligible);train=train[train.participant.isin(eligible)]
            weights=np.array([.5/side_counts.loc[(r.participant,r.side)] for r in train.itertuples()]);weights*=len(train)/weights.sum()
            model=make_pipeline(MinMaxScaler(),SVC(C=1,kernel='linear'))
            model.fit(train[COLS],train.side,svc__sample_weight=weights)
            row=test.drop(columns=COLS).copy();row['predicted_side']=model.predict(test[COLS]);row['correct']=row.side.eq(row.predicted_side);row['scope']=scope
            predictions.append(row);fit_counts.append(dict(scope=scope,fold=int(fold),training_participants=len(eligible),training_excluded_single_side=excluded,training_events=len(train),test_events=len(test)))
    pred=pd.concat(predictions);pred.to_csv(OUT/'predictions.csv',index=False);pd.DataFrame(fit_counts).to_csv(OUT/'fit_counts.csv',index=False)
    metrics=[];participant_rows=[]
    counts=ledger.groupby('participant')[['expected','usable']].sum()
    for scope,subset in [('all_selected',people),('device_protocol_matched',people[people.matched])]:
        accuracy=pred[pred.scope.eq(scope)].groupby('participant').correct.mean()
        p=subset[['participant','target','pathology']].merge(counts,on='participant').merge(accuracy.rename('accuracy'),on='participant',how='left')
        p['accuracy']=p.accuracy.fillna(0);p['scope']=scope;participant_rows.append(p)
        for (target,pathology),g in p.groupby(['target','pathology']):
            coverage=g.usable.sum()/g.expected.sum()
            metrics.append(dict(scope=scope,target=target,pathology=pathology,n=len(g),accuracy=g.accuracy.mean(),coverage=coverage,passed=bool(g.accuracy.mean()>=.9 and coverage>=.95)))
    pd.concat(participant_rows).to_csv(OUT/'participant_metrics.csv',index=False)
    metrics=pd.DataFrame(metrics);metrics.to_csv(OUT/'metrics.csv',index=False)
    (OUT/'decision.json').write_text(json.dumps(dict(passed=bool(metrics.passed.all()),fits=6,reference='algorithm-derived contact times; conditional laterality only'),indent=2))
    print(metrics.to_string(index=False))


if __name__=='__main__':main()
