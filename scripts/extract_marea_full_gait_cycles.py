from pathlib import Path
import numpy as np, pandas as pd
from scipy.io import loadmat
ROOT=Path(__file__).resolve().parents[1]; R=ROOT/'data/raw/marea_2017/data'; S=R/'Subject Data_mat format'; gt=loadmat(R/'GroundTruth.mat',squeeze_me=True,struct_as_record=False)['GroundTruth']; cycles=[]; rows=[]
def sig(sub,loc):
 d=loadmat(S/f'{sub}_{loc}.mat'); return np.sqrt(np.asarray(d['accX']).ravel()**2+np.asarray(d['accY']).ravel()**2+np.asarray(d['accZ']).ravel()**2)
for item in np.atleast_1d(gt):
 ev=item.treadWalk; sub=str(ev.SubIdx)
 try: W,L,F=sig(sub,'Waist'),sig(sub,'LF'),sig(sub,'RF')
 except (FileNotFoundError,KeyError): continue
 hs=np.asarray(ev.LF_HS).ravel().astype(int); hs=hs[(hs>0)&(hs<len(L))]
 for i in range(len(hs)-1):
  a,b=hs[i],hs[i+1]
  if b-a<80 or b-a>300: continue
  grid=np.linspace(a,b,200); cycles.append(np.stack([np.interp(grid,np.arange(len(W)),W),np.interp(grid,np.arange(len(L)),L),np.interp(grid,np.arange(len(F)),F)],1).astype('float32')); rows.append({'dataset_id':'marea_2017','participant_key':f'marea_2017_{sub}','trial_id':'treadWalk','cycle_index':i,'source_hz':128,'phase_points':200,'cycle_duration_sec':float((b-a)/128)})
Y=np.stack(cycles); pd.DataFrame(rows).to_csv(ROOT/'data/processed/marea_full_gait_cycle_metadata.csv',index=False); np.save(ROOT/'data/processed/marea_full_gait_cycles_float32.npy',Y); print('cycles',Y.shape,'participants',pd.DataFrame(rows).participant_key.nunique())
