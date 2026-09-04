from pathlib import Path
import numpy as np, pandas as pd
from scipy.spatial.distance import cdist
from scipy.signal import welch
import os
P=Path(__file__).resolve().parents[1]/'data'/'processed'; rng=np.random.default_rng(42)
real=np.load(P/'marea_full_gait_cycles_float32.npy'); syn=np.load(P/os.getenv('VAE_CYCLES','marea_vae_synthetic_healthy_cycles_float32.npy')); ri=rng.choice(len(real),min(1200,len(real)),replace=False)
def metrics(name,x):
 return {'set':name,'cycles':len(x),'mean':float(x.mean()),'std':float(x.std()),'cycle_std_mean':float(x.std((1,2)).mean()),'smoothness':float(np.abs(np.diff(x,axis=1)).mean()),'lowfreq_power':float(welch(x[:300],fs=1,nperseg=64,axis=1)[1][:,:8].mean())}
rows=[metrics('real',real[ri]),metrics('vae_synthetic',syn)]; a=syn.reshape(len(syn),-1)[::5]; b=real[ri[:len(a)]].reshape(len(a),-1); c=real[ri[len(a):len(a)*2]].reshape(len(a),-1); d1=cdist(a,b).min(1); d2=cdist(b,c).min(1)
pd.DataFrame(rows).to_csv(P/'marea_vae_cycle_quality_summary.csv',index=False); pd.DataFrame({'comparison':['vae_to_real','real_to_real'],'nearest_mean':[d1.mean(),d2.mean()],'nearest_p05':[np.percentile(d1,5),np.percentile(d2,5)],'nearest_p50':[np.median(d1),np.median(d2)]}).to_csv(P/'marea_vae_cycle_nearest_neighbour_audit.csv',index=False); print(pd.DataFrame(rows).to_string(index=False)); print('nearest',d1.mean(),d2.mean())
