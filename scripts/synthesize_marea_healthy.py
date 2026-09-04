"""Generate a small, provenance-preserving MAREA-only healthy augmentation."""
from pathlib import Path
import numpy as np, pandas as pd
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/'data'/'processed'; rng=np.random.default_rng(42)
X=np.load(P/'tier1_healthy_marea_duogait_windows_float32.npy'); m=pd.read_csv(P/'tier1_healthy_marea_duogait_window_metadata.csv'); keep=m.dataset_id.eq('marea_2017').to_numpy(); X=X[keep]; m=m.loc[keep].reset_index(drop=True)
out=[]; rows=[]
for pid in m.participant_key.unique():
 idx=np.flatnonzero(m.participant_key.eq(pid).to_numpy()); n=max(1,int(round(len(idx)*.20)))
 for j in range(n):
  a,b=rng.choice(idx,2,replace=False); lam=float(rng.uniform(.35,.65)); out.append((lam*X[a]+(1-lam)*X[b]).astype('float32')); rows.append({'dataset_id':'marea_2017_synthetic','label':'healthy','participant_key':f'synthetic_marea_{pid}_{j:04d}','parent_a':str(m.iloc[a].participant_key),'parent_b':str(m.iloc[b].participant_key),'mix_weight':lam,'synthetic':True})
Y=np.stack(out); meta=pd.DataFrame(rows); np.save(P/'marea_synthetic_healthy_windows_float32.npy',Y); meta.to_csv(P/'marea_synthetic_healthy_metadata.csv',index=False)
summary=pd.DataFrame({'channel':['lower_back','left_foot','right_foot'],'real_mean':X.mean((0,1)),'synthetic_mean':Y.mean((0,1)),'mean_difference':Y.mean((0,1))-X.mean((0,1)),'real_std':X.std((0,1)),'synthetic_std':Y.std((0,1))}); summary.to_csv(P/'marea_synthetic_healthy_quality_summary.csv',index=False)
print('real',X.shape,'synthetic',Y.shape); print(summary.to_string(index=False))
