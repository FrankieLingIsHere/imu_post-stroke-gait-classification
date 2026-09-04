"""Convert Zenodo SA/LF/RF 18-channel windows to notebook-17's 3 magnitudes."""
from pathlib import Path
import numpy as np,pandas as pd
R=Path(__file__).resolve().parents[1]; x=np.load(R/'data/processed/zenodo_stroke_windows_float32.npy'); m=pd.read_csv(R/'data/processed/zenodo_stroke_window_metadata.csv')
# Materialization order is SA, LF, RF; each sensor is accel xyz then gyro xyz.
mag=np.stack([np.linalg.norm(x[:, :, 0:3],axis=2),np.linalg.norm(x[:, :, 6:9],axis=2),np.linalg.norm(x[:, :, 12:15],axis=2)],axis=2).astype('float32')
np.save(R/'data/processed/zenodo_benchmark_acceleration_magnitude_windows_float32.npy',mag); m.to_csv(R/'data/processed/zenodo_benchmark_magnitude_metadata.csv',index=False); print(mag.shape,'participants',m.participant.nunique())
