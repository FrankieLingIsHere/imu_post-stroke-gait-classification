"""Check saved hallway inputs against raw MAT and frozen development statistics.

No predictions, transformations, threshold selection or model fitting.
"""
from pathlib import Path
import hashlib
import json
import sys
import numpy as np
from scipy.io import loadmat

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from models.predict_lower_back import load_bundle
from src.models.evidence_gated_domain_generalization import load_development_data


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stats(x):
    a = np.asarray(x, dtype=np.float64)
    return dict(windows=len(a), mean_g=float(a.mean()), std_g=float(a.std()),
                sample_quantiles_g=np.quantile(a, [.01,.5,.99]).tolist(),
                window_std_quantiles_g=np.quantile(a.std(axis=1), [.05,.5,.95]).tolist())


def main():
    base=ROOT/'data/interim/public_imu_screen_2026-09-08'
    checkpoint=ROOT/'models/checkpoints/stroke-gait-lower-back-ensemble-v0.2.0.pt'
    manifest=json.loads(checkpoint.with_suffix('.manifest.json').read_text())
    for name,digest in manifest['input_sha256'].items():
        if sha(ROOT/'data/processed'/name)!=digest:
            raise ValueError('Development input changed: '+name)
    bundle=load_bundle(checkpoint,checkpoint.with_suffix('.manifest.json'))
    x,meta=load_development_data(ROOT/'data/processed')
    dev=[]
    for (source,label),indices in meta.groupby(['source','label']).groups.items():
        dev.append(dict(source=source,label=label,**stats(x[indices,:,0])))
    normalizers=[dict(method=m['method'],seed=m['seed'],mean=float(m['mean'].item()),
                      std=float(m['std'].item())) for m in bundle['members']]
    people=[]
    result=json.loads((base/'hallway_probe_v1/results.json').read_text())
    for person in result['participants']:
        c,p=person['cohort'],person['participant']
        raw=base/'locked_pilot_v1'/c/p/'data.mat'
        if sha(raw)!=person['raw_sha256']:raise ValueError('Raw hash mismatch')
        sensor=loadmat(raw,simplify_cells=True)['data']['TimeMeasure1']['Test10']['Trial1']['SU']['LowerBack']
        folder=base/'hallway_probe_v1'/c/p
        saved=np.load(folder/'windows.npy');windows=json.loads((folder/'window_metadata.json').read_text())
        reconstructed=np.stack([np.sqrt(np.square(np.asarray(sensor['Acc'],dtype=np.float64)[w['start']:w['end']]).sum(axis=1)) for w in windows])[:,:,None]
        np.testing.assert_allclose(saved,reconstructed,atol=5e-7,rtol=1e-6)
        assert sensor['Fs']['Acc']==100
        np.testing.assert_allclose(np.diff(sensor['Timestamp']),.01,atol=.0001,rtol=0)
        people.append(dict(cohort=c,participant=p,**stats(saved),
                           raw_reconstruction_max_error=float(np.max(np.abs(saved-reconstructed)))))
    output=dict(scope='input-transfer checks only; descriptive distribution differences do not identify causality',
                development_inputs_verified=True,checkpoint_sha256=sha(checkpoint),
                raw_reconstruction_passed=True,rate_timebase_passed=True,
                units_evidence=json.loads((base/'unit_evidence.json').read_text()),
                normalization='fixed per-member training constants applied once by predict_windows; no TVS fitting',
                normalizers=normalizers,development=dev,tvs=people)
    (base/'input_transfer_check.json').write_text(json.dumps(output,indent=2))
    print(json.dumps(output,indent=2))


if __name__=='__main__':main()
