"""Check provider nominal axes against local raw/processed acceleration.

No diagnosis-dependent remapping. Initial-second gravity is a screening proxy,
not a validated stationary interval or independent anatomical calibration.
"""
from pathlib import Path
import sys
import json
import itertools
import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.data.voisard_aligned import load_aligned_lower_back


def main():
    out=ROOT/'data/processed/directional_axis_v1'
    out.mkdir(exist_ok=True)
    selected=pd.read_csv(ROOT/'data/processed/bilateral_phase_v1/trial_features.csv')
    paths={p.stem.removesuffix('_meta'):p for p in (ROOT/'data/raw/voisard_2025/data').glob('*/*/*/*/*_meta.json')}
    b,a=butter(8,14,fs=100)
    rows=[]
    for r in selected.itertuples():
        p=paths[r.trial];m=json.loads(p.read_text(encoding='utf-8'))
        x,info=load_aligned_lower_back(p.parent,r.trial)
        processed=pd.read_csv(p.parent/(r.trial+'_processed_data.txt'),sep='\t',usecols=['LB_Acc_'+k for k in 'XYZ']).to_numpy()
        row=dict(participant=r.participant,trial=r.trial,sensor=m['sensor'])
        first=x[:100]
        finite=first[np.isfinite(first).all(axis=1)]
        if len(finite):
            v=np.median(finite,axis=0); norm=np.linalg.norm(v)
            row.update(initial_samples=len(finite),initial_dominant_axis='XYZ'[np.argmax(abs(v))],
                       initial_x_gravity_fraction=float(v[0]/norm) if norm else np.nan)
        if len(x)==len(processed) and np.isfinite(x).all() and np.isfinite(processed).all():
            filtered=filtfilt(b,a,x,axis=0)
            costs=[]
            for perm in itertools.permutations(range(3)):
                q=filtered[:,perm]
                signs=np.where((q*processed).sum(axis=0)>=0,1,-1)
                costs.append((float(np.sqrt(np.mean((q*signs-processed)**2))),perm,signs))
            error,perm,signs=min(costs,key=lambda z:z[0])
            row.update(best_mapping=' '.join(('+' if s>0 else '-')+'XYZ'[i] for i,s in zip(perm,signs)),
                       best_rmse=error,identity_rmse=float(np.sqrt(np.mean((filtered-processed)**2))),
                       comparison_status='compared')
        else:
            row['comparison_status']='unsupported_length_or_nonfinite'
        rows.append(row)
    frame=pd.DataFrame(rows)
    frame.to_csv(out/'axis_audit.csv',index=False)
    print(frame.groupby(['sensor','initial_dominant_axis'],dropna=False).size().to_string())
    print(frame.groupby(['sensor','comparison_status','best_mapping'],dropna=False).size().to_string())
    print(frame.groupby('sensor')[['initial_x_gravity_fraction','identity_rmse','best_rmse']].agg(['median','max']).to_string())


if __name__=='__main__':
    main()
