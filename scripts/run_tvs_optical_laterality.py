"""Independent-modality reference intake and conditional laterality comparator."""
from pathlib import Path
import sys,json
import numpy as np
import pandas as pd
from scipy.io import loadmat
from scipy.signal import butter,sosfiltfilt
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import SVC
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from run_conditional_gait_comparison import sha
OUT=ROOT/'data/processed/tvs_optical_laterality_v1'


def contacts(standard):
    periods=standard.get('ContinuousWalkingPeriod',[])
    if isinstance(periods,dict):periods=[periods]
    records={}
    for b in periods:
        times=np.atleast_1d(b.get('InitialContact_Event',[]))
        sides=np.atleast_1d(b.get('InitialContact_LeftRight',[]))
        if len(times)!=len(sides):raise ValueError('Unpaired reference times/sides')
        for t,s in zip(times,sides):
            if str(s) not in ['Left','Right'] or not np.isfinite(t):raise ValueError('Invalid reference label/time')
            label=int(str(s)=='Right');t=float(t)
            if t in records and records[t]!=label:raise ValueError('Conflicting reference side')
            records[t]=label
    return sorted(records.items())


def main():
    OUT.mkdir(exist_ok=True)
    base=ROOT/'data/interim/public_imu_screen_2026-09-08'
    files={(p.parent.parent.name,p.parent.name):p for p in (base/'cohort_hallway_v1/raw').glob('*/*/data.mat')}
    files.setdefault(('HA','4109'),base/'HA_sample/data.mat');files.setdefault(('PD','4020'),base/'PD_sample/data.mat')
    manifest={f'{c}/{i}':dict(path=str(p),sha256=sha(p)) for (c,i),p in files.items()}
    manifest['protocol_sha256']=sha(ROOT/'docs/TVS_OPTICAL_LATERALITY_PROTOCOL_2026-09-09.md');manifest['code_sha256']=sha(Path(__file__))
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
    rows=[];ledger=[]
    for (cohort,identity),p in files.items():
        person=cohort+'/'+identity;data=loadmat(p,simplify_cells=True)['data']
        for tm,tests in data.items():
            for task,trials in tests.items():
                if task not in ['Test5','Test6','Test7','Test10']:continue
                for trial,r in trials.items():
                    name='/'.join([tm,task,trial]);expected=usable=matched=same=0;timing=[];error=''
                    try:
                        standards=r.get('Standards',{})
                        periods=standards.get('Stereophoto',{}).get('ContinuousWalkingPeriod',[])
                        if isinstance(periods,dict):periods=[periods]
                        # Count declared contacts before validating labels/times so
                        # rejected partial-reference trials remain in the denominator.
                        expected=sum(len(np.atleast_1d(b.get('InitialContact_Event',[]))) for b in periods)
                        opt=contacts(standards.get('Stereophoto',{}));indip=contacts(standards.get('INDIP',{}));expected=len(opt)
                        if not opt:raise ValueError('No optical side contacts')
                        if not standards.get('Stereophoto_raw',{}).get('Mrks'):raise ValueError('No raw optical marker fields')
                        i=j=0
                        while i<len(opt) and j<len(indip):
                            a,s=opt[i];b,t=indip[j]
                            if b<a-.15:j+=1
                            elif b>a+.15:i+=1
                            else:matched+=1;same+=int(s==t);timing.append(abs(a-b));i+=1;j+=1
                        sensor=r['SU']['LowerBack'];x=np.asarray(sensor['Gyr']);assert sensor['Fs']['Gyr']==100
                        if x.ndim!=2 or x.shape[1]!=3 or not np.isfinite(x).all():raise ValueError('Invalid gyro')
                        ic=np.rint(np.array([t for t,s in opt])*100).astype(int)-1
                        if (ic<0).any() or (ic>=len(x)).any() or len(set(ic))!=len(ic):raise ValueError('Invalid sample indices')
                        filtered=sosfiltfilt(butter(4,[.5,2],btype='bandpass',fs=100,output='sos'),x,axis=0)
                        first=np.gradient(filtered,axis=0);second=np.gradient(first,axis=0)
                        features=np.c_[filtered,first,second][ic]
                        for index,((time,side),feature) in enumerate(zip(opt,features)):
                            rows.append(dict(participant=person,cohort=cohort,trial=name,ic=int(ic[index]),side=side,**{f'f{k}':v for k,v in enumerate(feature)}))
                        usable=expected
                    except (ValueError,KeyError,AssertionError) as exc:error=str(exc)
                    ledger.append(dict(participant=person,cohort=cohort,trial=name,expected=expected,usable=usable,reference_matches=matched,reference_side_agreements=same,timing_mae=float(np.mean(timing)) if timing else np.nan,error=error))
    events=pd.DataFrame(rows);coverage=pd.DataFrame(ledger);events.to_csv(OUT/'features.csv',index=False);coverage.to_csv(OUT/'trial_coverage.csv',index=False)
    people=pd.DataFrame([dict(participant=c+'/'+i,cohort=c) for c,i in files])
    eligible=events.groupby('participant').side.nunique();people['eligible']=people.participant.map(eligible).eq(2)
    print(coverage.groupby('cohort')[['expected','usable','reference_matches','reference_side_agreements']].sum().to_string())
    sums=coverage.groupby('cohort')[['expected','usable']].sum()
    if not people.eligible.all() or ((sums.usable/sums.expected)<.95).any() or people.groupby('cohort').size().min()<3:
        people.to_csv(OUT/'participants.csv',index=False);(OUT/'decision.json').write_text(json.dumps({'passed':False,'reason':'eligibility gate failed; no fit'}));print('Eligibility gate failed');return
    predictions=[]
    for fold,(tr,te) in enumerate(StratifiedKFold(3,shuffle=True,random_state=20260909).split(people,people.cohort)):
        train=events[events.participant.isin(people.iloc[tr].participant)];test=events[events.participant.isin(people.iloc[te].participant)]
        people.loc[te,'fold']=fold;assert not set(train.participant)&set(test.participant)
        counts=train.groupby(['participant','side']).size();w=np.array([.5/counts.loc[(r.participant,r.side)] for r in train.itertuples()]);w*=len(train)/w.sum()
        model=make_pipeline(MinMaxScaler(),SVC(C=1,kernel='linear'));cols=[f'f{k}' for k in range(9)]
        model.fit(train[cols],train.side,svc__sample_weight=w)
        result=test.drop(columns=cols).copy();result['prediction']=model.predict(test[cols]);result['correct']=result.side.eq(result.prediction);result['fold']=fold;predictions.append(result)
    pred=pd.concat(predictions);pred.to_csv(OUT/'predictions.csv',index=False)
    people=people.merge(pred.groupby('participant').correct.mean().rename('accuracy'),on='participant',how='left');people['accuracy']=people.accuracy.fillna(0)
    people.to_csv(OUT/'participants.csv',index=False);metrics=people.groupby('cohort').accuracy.agg(['count','mean','min']);metrics.to_csv(OUT/'metrics.csv')
    (OUT/'decision.json').write_text(json.dumps(dict(passed=bool(metrics['mean'].ge(.9).all()),fits=3,participants=len(people),task='conditional laterality, not stroke classification'),indent=2));print(metrics.to_string())


if __name__=='__main__':main()
