"""Create conservative synthetic healthy windows by same-source window mixing.

This is a control for generative synthesis: it cannot invent stroke pathology,
and it never uses validation or RevalExo data. Each synthetic sample is a
 convex interpolation of two different real healthy windows from the same
source, preserving the N x 500 x 3 project contract.
"""
from pathlib import Path
import numpy as np, pandas as pd

ROOT=Path(__file__).resolve().parents[1]; P=ROOT/'data'/'processed'; rng=np.random.default_rng(42)
X=np.load(P/'validated_acceleration_magnitude_windows_float32.npy'); m=pd.read_csv(P/'validated_window_metadata.csv')
keep=m.label.eq('healthy').to_numpy(); X=X[keep]; m=m.loc[keep].reset_index(drop=True)
rows=[]; out=[]
for source in m.dataset_id.astype(str).unique():
 idx=np.flatnonzero(m.dataset_id.astype(str).eq(source).to_numpy()); n=max(1,int(round(len(idx)*.25)))
 for j in range(n):
  a,b=rng.choice(idx,2,replace=False); lam=float(rng.uniform(.25,.75)); out.append((lam*X[a]+(1-lam)*X[b]).astype('float32'))
  rows.append({'dataset_id':source,'label':'healthy','participant_key':f'synthetic_{source}_{j:05d}','parent_a':str(m.iloc[a].participant_key),'parent_b':str(m.iloc[b].participant_key),'mix_weight':lam,'synthetic':True})
Y=np.stack(out); meta=pd.DataFrame(rows); np.save(P/'synthetic_healthy_phase_mixed_windows_float32.npy',Y); meta.to_csv(P/'synthetic_healthy_phase_mixed_metadata.csv',index=False)
summary=pd.DataFrame({'source':m.dataset_id.astype(str).unique()})
summary['real_windows']=summary.source.map(m.dataset_id.astype(str).value_counts()); summary['synthetic_windows']=summary.source.map(meta.dataset_id.value_counts()).fillna(0).astype(int); summary['real_participants']=summary.source.map(m.groupby(m.dataset_id.astype(str)).participant_key.nunique()); summary.to_csv(P/'synthetic_healthy_phase_mixed_summary.csv',index=False)
print(summary.to_string(index=False)); print('shape',Y.shape,'wrote',P/'synthetic_healthy_phase_mixed_windows_float32.npy')
