"""Audit older healthy triaxial data for age/speed/domain robustness."""
from pathlib import Path
import numpy as np, pandas as pd

R=Path(__file__).resolve().parents[1]; D=R/'data/raw/triaxial_accelerometer/extracted'; OUT=R/'data/processed/triaxial_healthy_domain_audit.csv'; meta=pd.read_csv(D/'_data_old.csv'); meta['ID']=meta.ID.astype(int)
rows=[]
for f in D.glob('*.csv'):
 if f.name=='_data_old.csv': continue
 parts=f.stem.split('_'); pid=int(parts[0]); sensor=parts[1]; condition='_'.join(parts[2:]); x=pd.read_csv(f,header=None).apply(pd.to_numeric,errors='coerce').to_numpy(); finite=np.isfinite(x).all(1); z=x[finite]; mag=np.linalg.norm(z,axis=1) if len(z) else np.array([]); r=meta.loc[meta.ID.eq(pid)].iloc[0]
 rows.append({'dataset_id':'triaxial_healthy','participant':f'{pid:03d}','age':r.age,'sex':r.sex,'sensor':sensor,'condition':condition,'samples':len(x),'finite_fraction':float(finite.mean()),'magnitude_median':float(np.median(mag)) if len(mag) else np.nan,'magnitude_p95':float(np.percentile(mag,95)) if len(mag) else np.nan,'speed_metadata':r.get('speed_'+condition.replace('_','_'),np.nan)})
a=pd.DataFrame(rows); OUT.parent.mkdir(parents=True,exist_ok=True); a.to_csv(OUT,index=False); print(a.groupby('sensor').agg(participants=('participant','nunique'),files=('participant','size'),age_min=('age','min'),age_max=('age','max'),median_samples=('samples','median'),median_mag=('magnitude_median','median'))); print('Wrote',OUT)
