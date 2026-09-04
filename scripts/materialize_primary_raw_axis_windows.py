"""Rebuild signed tri-axial LB/LF/RF windows, loading each trial once."""
from pathlib import Path
import numpy as np,pandas as pd
R=Path(__file__).resolve().parents[1]; P=R/'data/processed'; meta=pd.read_csv(P/'validated_window_metadata.csv'); arrays=[]; kept=[]
V={p.name:p for p in (R/'data/raw/voisard_2025/data').rglob('*_raw_data_LB.txt')}
F={p.name:p for p in (R/'data/raw/felius_2024/data/Raw_data').rglob('*_lowback.csv')}
def load(path,sep,cols): return pd.read_csv(path,sep=sep,engine='python' if sep is None else 'c')[cols].to_numpy('float32')
for (src,trial),g in meta.groupby(['dataset_id','trial_id'],sort=False):
 if src=='voisard_2025':
  h=V.get(f'{trial}_raw_data_LB.txt'); base=h.parent if h else None; names=[f'{trial}_raw_data_{c}.txt' for c in ['LB','LF','RF']]; sep='\t'; cols=['Acc_X','Acc_Y','Acc_Z']
 elif src=='felius_2024':
  h=F.get(f'{trial}_lowback.csv'); base=h.parent if h else None; names=[f'{trial}_{c}.csv' for c in ['lowback','leftfoot','rightfoot']]; sep=None; cols=['ax','ay','az']
 else: continue
 if base is None or not all((base/n).exists() for n in names): continue
 try:
  sig=[load(base/n,sep,cols) for n in names]
  for _,r in g.iterrows():
   a,b=int(r.start_sample),int(r.end_sample)
   if min(len(x) for x in sig)>=b: arrays.append(np.concatenate([x[a:b] for x in sig],1)); kept.append(r.to_dict())
 except Exception: continue
arr=np.stack(arrays).astype('float32'); md=pd.DataFrame(kept); units=np.where(md.dataset_id.eq('voisard_2025').to_numpy(),'m/s2','g'); arr[md.dataset_id.eq('voisard_2025').to_numpy()]/=9.80665; md['acceleration_unit']='g'; md['unit_conversion']=np.where(md.dataset_id.eq('voisard_2025'),'raw m/s2 / 9.80665','raw g'); np.save(P/'primary_signed_acceleration_windows_float32.npy',arr); md.to_csv(P/'primary_signed_acceleration_window_metadata.csv',index=False); print({'shape':arr.shape,'participants':md.participant_key.nunique(),'sources':md.dataset_id.value_counts().to_dict(),'match_rate':len(md)/len(meta[meta.dataset_id.isin(['voisard_2025','felius_2024'])])})
