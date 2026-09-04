from pathlib import Path
import numpy as np, pandas as pd
P=Path(__file__).resolve().parents[1]/'data'/'processed'; x=np.load(P/'duogait_full_gait_cycles_float32.npy'); x=(x*9.80665).astype('float32'); np.save(P/'duogait_full_gait_cycles_ms2_float32.npy',x); m=pd.read_csv(P/'duogait_full_gait_cycle_metadata.csv'); m['acceleration_unit']='m/s2'; m['unit_conversion']='raw g x 9.80665'; m.to_csv(P/'duogait_full_gait_cycle_metadata_ms2.csv',index=False); print('saved',x.shape,'mean',x.mean())
