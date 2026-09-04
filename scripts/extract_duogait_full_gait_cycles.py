from pathlib import Path
import numpy as np, pandas as pd
ROOT=Path(__file__).resolve().parents[1]; base=ROOT/'data/raw/duogait_2023/data'; out=[]; meta=[]
subs=['sub_01','sub_02','sub_03','sub_05','sub_06','sub_07','sub_08','sub_09','sub_10','sub_11','sub_12','sub_13','sub_14','sub_15','sub_17','sub_18']
for sub in subs:
 proc=base/'repository_processed'/'OG_st_control'/sub; raw=base/'repository_interim'/'OG_st_control'/sub
 try:
  tab=pd.read_csv(proc/'left_foot_core_params.csv'); sig=[]
  for loc in ['SA','LF','RF']:
   d=pd.read_csv(raw/(loc+'.csv')); sig.append(np.linalg.norm(d[['AccX','AccY','AccZ']].to_numpy(float),axis=1))
  ic=pd.to_numeric(tab.ic_samples,errors='coerce').dropna().astype(int).to_numpy(); ic=ic[(ic>0)&(ic<min(map(len,sig)))]
  for j,(a,b) in enumerate(zip(ic[:-1],ic[1:])):
   if b-a<70 or b-a>260: continue
   grid=np.linspace(a,b,200); out.append(np.stack([np.interp(grid,np.arange(len(s)),s) for s in sig],1).astype('float32')); meta.append({'dataset_id':'duogait_2023','participant_key':sub,'trial_id':'OG_st_control','cycle_index':j,'source_hz':128,'phase_points':200,'cycle_duration_sec':float((b-a)/128),'event_source':'official_processed_left_foot_core_params'})
 except Exception as e: print('skip',sub,type(e).__name__,e)
Y=np.stack(out); pd.DataFrame(meta).to_csv(ROOT/'data/processed/duogait_full_gait_cycle_metadata.csv',index=False); np.save(ROOT/'data/processed/duogait_full_gait_cycles_float32.npy',Y); print('cycles',Y.shape,'participants',pd.DataFrame(meta).participant_key.nunique())
