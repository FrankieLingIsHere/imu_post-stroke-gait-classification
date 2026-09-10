"""Raw-to-processed gyro mapping audit, without contact labels or model fitting."""
from pathlib import Path
import sys,json,itertools
import numpy as np
import pandas as pd
from scipy.signal import butter,filtfilt

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from src.data.voisard_aligned import align_packets
from run_conditional_gait_comparison import sha
OUT=ROOT/'data/processed/gyro_axis_v1'


def best_mapping(raw,processed):
    candidates=[]
    for perm in itertools.permutations(range(3)):
        q=raw[:,perm]
        signs=np.where(((q-q.mean(axis=0))*(processed-processed.mean(axis=0))).sum(axis=0)>=0,1,-1)
        mapped=q*signs
        centered=mapped-mapped.mean(axis=0);target=processed-processed.mean(axis=0)
        scale=float((centered*target).sum()/(centered*centered).sum()) if np.any(centered) else np.nan
        offset=(processed-scale*mapped).mean(axis=0)
        candidates.append(dict(mapping=' '.join(('+' if s>0 else '-')+'XYZ'[i] for i,s in zip(perm,signs)),
            rmse=float(np.sqrt(np.mean((mapped-processed)**2))),scale=scale,
            offset_x=float(offset[0]),offset_y=float(offset[1]),offset_z=float(offset[2]),
            scaled_rmse=float(np.sqrt(np.mean((scale*mapped+offset-processed)**2)))))
    return min(candidates,key=lambda x:x['scaled_rmse'])


def main():
    OUT.mkdir(exist_ok=True)
    selected_path=ROOT/'data/processed/bilateral_phase_v1/trial_features.csv'
    axis_path=ROOT/'data/processed/directional_axis_v1/axis_audit.csv'
    selected=pd.read_csv(selected_path);axes=pd.read_csv(axis_path).set_index('trial')
    paths={p.stem.removesuffix('_meta'):p for p in (ROOT/'data/raw/voisard_2025/data').glob('*/*/*/*/*_meta.json')}
    (OUT/'manifest.json').write_text(json.dumps({str(p.relative_to(ROOT)):sha(p) for p in [Path(__file__),selected_path,axis_path,ROOT/'src/data/voisard_aligned.py']},indent=2))
    b,a=butter(8,14,fs=100);rows=[]
    for r in selected.itertuples():
        p=paths[r.trial];m=json.loads(p.read_text(encoding='utf-8'));assert m['freq']==100
        files=[p.parent/f'{r.trial}_raw_data_{s}.txt' for s in ['HE','LB','LF','RF']]
        origin=int(round(min(pd.read_csv(f,sep='\t',usecols=['PacketCounter'],nrows=1).PacketCounter.iloc[0] for f in files)))
        raw=pd.read_csv(files[1],sep='\t',usecols=['PacketCounter','Gyr_X','Gyr_Y','Gyr_Z'])
        # Reuse the already tested clock/interpolation logic for three gyro columns.
        x=align_packets(raw.rename(columns={f'Gyr_{k}':f'Acc_{k}' for k in 'XYZ'}),origin)
        processed_path=p.parent/f'{r.trial}_processed_data.txt'
        y=pd.read_csv(processed_path,sep='\t',usecols=['LB_Gyr_'+k for k in 'XYZ']).to_numpy()
        row=dict(participant=r.participant,trial=r.trial,sensor=m['sensor'],raw_sha256=sha(files[1]),processed_sha256=sha(processed_path),
                 accel_mapping=axes.loc[r.trial,'best_mapping'],raw_samples=len(x),processed_samples=len(y))
        if len(x)==len(y) and np.isfinite(x).all() and np.isfinite(y).all():
            q=filtfilt(b,a,x,axis=0);match=best_mapping(q,y)
            row.update(status='compared',**match,identity_rmse=float(np.sqrt(np.mean((q-y)**2))))
            row['same_as_accel_mapping']=match['mapping']==row['accel_mapping']
        else:row['status']='unsupported_length_or_nonfinite'
        rows.append(row)
    frame=pd.DataFrame(rows);frame.to_csv(OUT/'gyro_axis_audit.csv',index=False)
    print(frame.groupby(['sensor','status','mapping'],dropna=False).size().to_string())
    print(frame.groupby('sensor')[['scale','rmse','scaled_rmse']].agg(['median','max']).to_string())
    print('Mapping disagreements:',frame.loc[frame.status.eq('compared'),'same_as_accel_mapping'].eq(False).sum())


if __name__=='__main__':main()
