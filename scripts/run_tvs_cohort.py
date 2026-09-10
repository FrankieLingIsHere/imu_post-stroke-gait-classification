"""One resumable cohort-wide TVS hallway acquisition and frozen evaluation.

Account for all 40 HA/PD people. No per-person selection or scoring decisions.
Newly opened and previously inspected participants are reported separately.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import sys

import numpy as np
from scipy.io import loadmat

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts import run_tvs_locked_pilot as acquisition
from src.data.tvs import trial_windows

BASE=ROOT/'data/interim/public_imu_screen_2026-09-08'
OUT=BASE/'cohort_hallway_v1'
CHECKPOINT=ROOT/'models/checkpoints/stroke-gait-lower-back-ensemble-v0.2.0.pt'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def metadata_decision(person):
    tasks=[t for t in person['tasks'] if t['task']=='Test10']
    if len(tasks)!=1:return None,'missing_or_ambiguous_hallway_task'
    t=tasks[0]
    reasons=[]
    for key in ('has_lower_back','has_stereophoto'):
        if not t[key]:reasons.append(key+'_absent')
    if t['sensor']!='MM+':reasons.append('sensor_mismatch')
    if t['walking_aid']!=0:reasons.append('walking_aid_or_unknown')
    if t['annotations']:reasons.append('task_annotation')
    return t,','.join(reasons) if reasons else None


def locked_protocol():
    OUT.mkdir(exist_ok=True)
    path=OUT/'protocol.json'
    if path.exists():
        if sha(path)!=(OUT/'protocol.sha256').read_text():raise ValueError('Protocol changed')
        return json.loads(path.read_text())
    metadata=json.loads((BASE/'lab_metadata/screening.json').read_text())
    inspected={(p['cohort'],p['participant']) for p in json.loads((BASE/'locked_pilot_v1/protocol.json').read_text())['selected']}
    rows=[]
    for person in sorted(metadata,key=lambda p:(p['cohort'],p['participant'])):
        task,reason=metadata_decision(person)
        rows.append(dict(cohort=person['cohort'],participant=person['participant'],task=task,
                         metadata_exclusion=reason,previously_inspected=bool(person['schema_development'] or
                         (person['cohort'],person['participant']) in inspected)))
    if len(rows)!=40 or len({(r['cohort'],r['participant']) for r in rows})!=40:
        raise ValueError('Expected 40 unique registered people')
    p=dict(created_utc=datetime.now(timezone.utc).isoformat(),people=rows,
           scope='all 40 registered HA/PD participants accounted for; exploratory hallway specificity; no stroke group',
           task='Test10 final metadata trial, same task all included people',
           primary_reporting='newly opened people separately by HA/PD; inspected stratum and combined descriptive counts also shown',
           rules='MM+, lower-back, Stereophoto, no walking aid or task annotation; finite native 100Hz; complete within-bout 500-sample windows; no padding/replacement',
           turns='reference truth unavailable; possible turns retained; not straight-only validation',
           threshold=.5,aggregation='mean window score per person',window=500,hop=250,
           no_tuning=True,abstention='disabled',
           transfers='two simultaneous resumable 1MiB ranges; reuse verified local raw and caches; acquisition failure stops batch without scoring',
           hashes={str(path.relative_to(ROOT)):sha(path) for path in [Path(__file__),ROOT/'src/data/tvs.py',
                   ROOT/'models/predict_lower_back.py',ROOT/'scripts/run_tvs_locked_pilot.py',
                   BASE/'lab_metadata/screening.json',BASE/'HA_inventory.json',BASE/'PD_inventory.json',
                   BASE/'input_transfer_check.json',CHECKPOINT]})
    with path.open('x') as f:json.dump(p,f,indent=2)
    (OUT/'protocol.sha256').write_text(sha(path))
    return p


def local_raw(row):
    folder=BASE/'locked_pilot_v1'/row['cohort']/row['participant']
    if (folder/'manifest.json').exists():
        manifest=json.loads((folder/'manifest.json').read_text());path=folder/'data.mat'
    else:
        manifest=next((m for m in json.loads((BASE/'sample_manifest.json').read_text())
                       if m['member']==f"{row['cohort']}/{row['participant']}/Laboratory/data.mat"),None)
        path=BASE/(row['cohort']+'_sample')/'data.mat'
    if manifest:
        if sha(path)!=manifest['sha256']:raise ValueError('Existing raw checksum mismatch')
        return path
    acquisition.OUT=OUT/'raw'
    return acquisition.acquire(row)


def main():
    if (OUT/'results.json').exists():raise FileExistsError('Cohort already scored; read saved result')
    p=locked_protocol()
    for path,digest in p['hashes'].items():
        if sha(ROOT/path)!=digest:raise ValueError('Locked dependency changed: '+path)
    rows=[];arrays=[]
    for person in p['people']:
        row=dict(person)
        if row['metadata_exclusion']:
            row.update(status='excluded_metadata',windows=0)
        else:
            try:
                path=local_raw(row)
            except Exception as error:
                row.update(status='transfer_failure',reason=f'{type(error).__name__}: {error}',windows=0)
                rows.append(row)
                (OUT/'intake.json').write_text(json.dumps(rows,indent=2))
                raise RuntimeError('Acquisition incomplete; resume same cohort. No cohort scoring.') from error
            try:
                t=row['task']
                trial=loadmat(path,simplify_cells=True)['data'][t['time_measure']]['Test10'][t['trial']]
                x,windows,audit=trial_windows(trial)
                row.update(status='included' if len(x) else 'excluded_duration_or_reference',
                           windows=len(x),audit=audit,raw_path=str(path.relative_to(ROOT)),raw_sha256=sha(path))
                folder=OUT/'prepared'/row['cohort']/row['participant'];folder.mkdir(parents=True,exist_ok=True)
                np.save(folder/'windows.npy',x,allow_pickle=False)
                (folder/'window_metadata.json').write_text(json.dumps(windows,indent=2))
                row['windows_sha256']=sha(folder/'windows.npy')
                if len(x):arrays.append((len(rows),x))
            except (ValueError,KeyError,TypeError) as error:
                row.update(status='excluded_quality',reason=f'{type(error).__name__}: {error}',windows=0)
        rows.append(row)
        (OUT/'intake.json').write_text(json.dumps(rows,indent=2))
        print('INTAKE',len(rows),'/40',row['cohort'],row['participant'],row['status'],flush=True)
    import torch
    from models.predict_lower_back import load_bundle,predict_windows
    torch.set_num_threads(4)
    bundle=load_bundle(CHECKPOINT,CHECKPOINT.with_suffix('.manifest.json'));smoke=bundle['smoke_test']
    np.testing.assert_allclose(predict_windows(bundle,smoke['windows'].numpy()),smoke['expected_probabilities'].numpy(),atol=1e-6,rtol=0)
    for index,x in arrays:
        y=predict_windows(bundle,x)
        if not (np.isfinite(y).all() and ((y>=0)&(y<=1)).all()):raise ValueError('Invalid predictions')
        rows[index].update(window_scores=y.tolist(),mean_score=float(y.mean()),positive=bool(y.mean()>=p['threshold']))
    groups=[]
    for c in ('HA','PD'):
        for history in ('new','inspected','all'):
            group=[r for r in rows if r['cohort']==c and (history=='all' or r['previously_inspected']==(history=='inspected'))]
            included=[r for r in group if r['status']=='included'];n=len(included);k=sum(r['positive'] for r in included)
            groups.append(dict(cohort=c,stratum=history,registered=len(group),evaluated=n,excluded=len(group)-n,
                               positive=k,negative=n-k,positive_rate=k/n if n else None,wilson_95=acquisition.wilson(k,n)))
    result=dict(scope=p['scope'],protocol_sha256=sha(OUT/'protocol.json'),participants=rows,groups=groups)
    with (OUT/'results.json').open('x') as f:json.dump(result,f,indent=2)
    print('RESULT',json.dumps(groups),flush=True)


if __name__=='__main__':main()
