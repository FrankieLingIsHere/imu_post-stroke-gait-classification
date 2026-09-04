from pathlib import Path
import numpy as np, pandas as pd
from scipy.spatial.distance import cdist
from scipy.signal import welch
import os
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/'data'/'processed'
real=np.load(P/'tier1_healthy_marea_duogait_windows_float32.npy'); rm=pd.read_csv(P/'tier1_healthy_marea_duogait_window_metadata.csv'); real=real[rm.dataset_id.eq('marea_2017').to_numpy()]
syn_name=os.getenv('MAREA_SYNTHETIC_FILE','marea_synthetic_healthy_windows_float32.npy'); syn=np.load(P/syn_name); rng=np.random.default_rng(42); ri=rng.choice(len(real),min(1200,len(real)),replace=False)
def ac(x,lag=25):
 x=x-x.mean(); return float(np.mean(x[:-lag]*x[lag:])/(np.mean(x*x)+1e-8))
def psd(x): return welch(x,fs=100,nperseg=128,axis=0)[1].mean(1)
rows=[]
for name,x in [('real',real[ri]),('synthetic',syn)]:
 rows.append({'set':name,'windows':len(x),'mean_all':float(x.mean()),'std_all':float(x.std()),'mean_window_std':float(x.std((1,2)).mean()),'autocorr_lag25':float(np.mean([ac(v[:,c]) for v in x[:300] for c in range(3)])),'psd_mean':float(psd(x[:300]).mean())})
flat_s=syn.reshape(len(syn),-1)[::max(1,len(syn)//300)]; flat_r=real[ri[:300]].reshape(min(300,len(ri)),-1); flat_r2=real[ri[300:600]].reshape(min(300,len(ri)-300),-1)
sr=cdist(flat_s,flat_r).min(1); rr=cdist(flat_r,flat_r2).min(1)
stem=Path(syn_name).stem; pd.DataFrame(rows).to_csv(P/(stem+'_quality_summary.csv'),index=False)
pd.DataFrame({'comparison':['synthetic_to_real','real_to_real'],'nearest_distance_mean':[sr.mean(),rr.mean()],'nearest_distance_p05':[np.percentile(sr,5),np.percentile(rr,5)],'nearest_distance_p50':[np.median(sr),np.median(rr)]}).to_csv(P/(stem+'_nearest_neighbour_audit.csv'),index=False)
print(pd.DataFrame(rows).to_string(index=False)); print('nearest mean synthetic/real',sr.mean(),rr.mean())
