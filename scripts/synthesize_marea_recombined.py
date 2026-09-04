from pathlib import Path
import numpy as np, pandas as pd
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/'data'/'processed'; rng=np.random.default_rng(43)
X=np.load(P/'tier1_healthy_marea_duogait_windows_float32.npy'); m=pd.read_csv(P/'tier1_healthy_marea_duogait_window_metadata.csv'); keep=m.dataset_id.eq('marea_2017').to_numpy(); X=X[keep]; m=m.loc[keep].reset_index(drop=True)
out=[]; rows=[]
for pid in m.participant_key.unique():
 idx=np.flatnonzero(m.participant_key.eq(pid).to_numpy()); n=max(1,int(round(len(idx)*.20)))
 for j in range(n):
  a,b=rng.choice(idx,2,replace=False); cut=int(rng.integers(190,310)); fade=20; left=X[a,:cut-fade]; blend=X[a,cut-fade:cut]*(np.arange(fade,0,-1)[:,None]/fade)+X[b,cut:cut+fade]*(np.arange(1,fade+1)[:,None]/fade); out.append(np.concatenate([left,blend,X[b,cut:]],axis=0).astype('float32')); rows.append({'dataset_id':'marea_2017_recombined','label':'healthy','participant_key':f'synthetic_marea_recombined_{pid}_{j:04d}','parent_a':str(m.iloc[a].participant_key),'parent_b':str(m.iloc[b].participant_key),'cut_index':cut,'synthetic':True})
Y=np.stack(out); pd.DataFrame(rows).to_csv(P/'marea_recombined_healthy_metadata.csv',index=False); np.save(P/'marea_recombined_healthy_windows_float32.npy',Y); print('real',X.shape,'synthetic',Y.shape)
