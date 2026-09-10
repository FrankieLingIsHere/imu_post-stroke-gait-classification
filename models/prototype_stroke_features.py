"""Participant-feature stroke research prototype; trusted local artifacts only."""
from pathlib import Path
import argparse,hashlib,json
import joblib
import numpy as np
import pandas as pd

FEATURES=['age','xsens_fraction','protocol_length_m','cadence','step_asymmetry',
          'swing_asymmetry','stance_asymmetry','swing_fraction','double_support_fraction','ml_log_hr']


def validate(frame):
    required=['participant']+FEATURES
    missing=set(required)-set(frame.columns)
    if missing:raise ValueError('Missing columns: '+', '.join(sorted(missing)))
    ids=frame.participant
    if ids.isna().any() or ids.astype(str).str.strip().eq('').any() or ids.duplicated().any():
        raise ValueError('Participant IDs must be present and unique')
    x=frame[FEATURES].apply(pd.to_numeric,errors='coerce')
    reasons=[]
    for index,row in x.iterrows():
        bad=[]
        for name in FEATURES:
            value=row[name]
            if name=='age' and pd.isna(frame.loc[index,name]):continue
            if not np.isfinite(value):bad.append(name);continue
            if name in ['xsens_fraction','swing_fraction','double_support_fraction'] and not 0<=value<=1:bad.append(name)
            elif name in ['step_asymmetry','swing_asymmetry','stance_asymmetry'] and not 0<=value<=2:bad.append(name)
            elif name in ['cadence','protocol_length_m'] and value<=0:bad.append(name)
            elif name in ['age','ml_log_hr'] and value<0:bad.append(name)
        reasons.append('invalid:'+','.join(bad) if bad else 'ok')
    return x,pd.Series(reasons,index=frame.index)


def predict_frame(frame,model,threshold):
    frame=frame.reset_index(drop=True)
    x,status=validate(frame)
    result=pd.DataFrame({'participant':frame.participant,'score':np.nan,'decision':'unknown','status':status,
                         'age_imputed':x.age.isna(),'threshold':threshold})
    valid=status.eq('ok')
    if valid.any():
        score=model.predict_proba(x.loc[valid])[:,1]
        result.loc[valid,'score']=score
        result.loc[valid,'decision']=np.where(score>=threshold,'research_positive','research_negative')
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--package',required=True,type=Path)
    p.add_argument('--input',required=True,type=Path)
    p.add_argument('--output',required=True,type=Path)
    args=p.parse_args();manifest=json.loads((args.package/'manifest.json').read_text())
    checkpoint=args.package/'model.joblib'
    if hashlib.sha256(checkpoint.read_bytes()).hexdigest()!=manifest['checkpoint_sha256']:raise ValueError('Checkpoint checksum mismatch')
    if manifest['features']!=FEATURES or manifest['task']!='stroke_feature_research':raise ValueError('Unsupported contract')
    threshold=float(manifest['threshold'])
    if not 0<=threshold<=1:raise ValueError('Invalid threshold')
    model=joblib.load(checkpoint)
    frame=pd.read_csv(args.input)
    result=predict_frame(frame,model,threshold);result.to_csv(args.output,index=False)
    print(json.dumps({'rows':len(result),'scored':int(result.status.eq('ok').sum()),'unknown':int(result.status.ne('ok').sum()),'mode':'annotation_assisted_research'}))


if __name__=='__main__':main()
