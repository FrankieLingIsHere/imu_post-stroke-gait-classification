from pathlib import Path
import numpy as np, pandas as pd, scipy.io as sio
from scipy.signal import resample
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'data/processed'; win=500; hop=250; arrays=[]; rows=[]
def add(sig,src,pid,trial):
 sig=resample(sig,round(len(sig)*100/128),axis=0)
 for st in range(0,max(0,len(sig)-win+1),hop): arrays.append(sig[st:st+win].astype('float32')); rows.append({'dataset_id':src,'participant_key':f'{src}_{pid}','trial_id':trial,'label':'healthy','start_sample':st,'window_seconds':5.0})
mroot=ROOT/'data/raw/marea_2017/data'; txt=mroot/'Subject Data_txt format'; indoor=sio.loadmat(mroot/'Activity Timings/Indoor Experiment Timings.mat',simplify_cells=True)['indoorTime']; outdoor=sio.loadmat(mroot/'Activity Timings/Outdoor Experiment Timings.mat',simplify_cells=True)['outdoorTime']
for i,s in enumerate(range(1,21)):
 paths=[txt/f'Sub{s}_{x}.txt' for x in ('Waist','LF','RF')]
 if not all(p.exists() for p in paths): continue
 sig=[]
 for p in paths:
  d=pd.read_csv(p); sig.append(np.linalg.norm(d[['accX','accY','accZ']].to_numpy(),axis=1)/9.80665)
 segs=[('treadWalk',indoor[i,0],indoor[i,1]),('indoorWalk',indoor[i,5],indoor[i,6])] if s<=11 else [('outdoorWalk',outdoor[s-12,0],outdoor[s-12,1])]
 for trial,a,b in segs:
  n=min(map(len,sig)); add(np.stack([x[int(a):min(int(b),n)] for x in sig],axis=1),'marea_2017',f'Sub{s}',trial)
droot=ROOT/'data/raw/duogait_2023/data/repository_interim/OG_st_control'
for sd in sorted(droot.glob('sub_*')):
 paths=[sd/f'{x}.csv' for x in ('SA','LF','RF')]
 if not all(p.exists() for p in paths): continue
 sig=[]
 for p in paths:
  d=pd.read_csv(p); sig.append(np.linalg.norm(d[['AccX','AccY','AccZ']].to_numpy(),axis=1))
 n=min(map(len,sig)); add(np.stack([x[:n] for x in sig],axis=1),'duogait_2023',sd.name,'OG_st_control')
X=np.stack(arrays) if arrays else np.empty((0,win,3),dtype='float32'); np.save(OUT/'tier1_healthy_marea_duogait_windows_float32.npy',X); pd.DataFrame(rows).to_csv(OUT/'tier1_healthy_marea_duogait_window_metadata.csv',index=False); print({'windows':len(rows),'participants':pd.DataFrame(rows).participant_key.nunique(),'datasets':pd.DataFrame(rows).dataset_id.value_counts().to_dict(),'shape':X.shape})
