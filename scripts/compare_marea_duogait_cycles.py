from pathlib import Path
import numpy as np, pandas as pd
from scipy.signal import welch
P=Path(__file__).resolve().parents[1]/'data'/'processed'; rows=[]
for src,xfile,mfile in [('marea','marea_full_gait_cycles_float32.npy','marea_full_gait_cycle_metadata.csv'),('duogait','duogait_full_gait_cycles_ms2_float32.npy','duogait_full_gait_cycle_metadata_ms2.csv')]:
 x=np.load(P/xfile); m=pd.read_csv(P/mfile); rows.append({'source':src,'cycles':len(x),'participants':m.participant_key.nunique(),'mean':x.mean(),'std':x.std(),'cycle_std':x.std((1,2)).mean(),'smoothness':np.abs(np.diff(x,axis=1)).mean(),'lowfreq_power':welch(x[:min(1000,len(x))],fs=1,nperseg=64,axis=1)[1][:,:8].mean(),'duration_mean_sec':m.cycle_duration_sec.mean(),'duration_std_sec':m.cycle_duration_sec.std()})
pd.DataFrame(rows).to_csv(P/'marea_duogait_cycle_comparison.csv',index=False); print(pd.DataFrame(rows).to_string(index=False))
