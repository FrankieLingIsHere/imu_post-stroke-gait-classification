"""Lock, acquire and evaluate a four-person exploratory TVS specificity pilot.

Selection never depends on predictions or download success. Failures are recorded
without replacement. This is not clinical validation and contains no stroke group.
"""
from pathlib import Path
import hashlib
import json
import sys
import struct
import zlib
from datetime import datetime, timezone
import argparse

import numpy as np
from scipy.io import loadmat

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.acquire_tvs_schema_samples import read_range, record
from src.data.tvs import trial_windows

BASE = ROOT/'data/interim/public_imu_screen_2026-09-08'
OUT = BASE/'locked_pilot_v1'


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def lock():
    OUT.mkdir(exist_ok=True)
    path = OUT/'protocol.json'
    if path.exists(): return json.loads(path.read_text())
    metadata = json.loads((BASE/'lab_metadata/screening.json').read_text())
    selected=[]
    for cohort in ('HA','PD'):
        eligible=[]
        for person in metadata:
            if person['cohort']!=cohort or person['schema_development']: continue
            tasks=[t for t in person['tasks'] if t['task']=='Test6' and t['has_lower_back']
                   and t['has_stereophoto'] and t['sensor']=='MM+' and t['walking_aid']==0
                   and not t['annotations']]
            if len(tasks)==1: eligible.append((person,tasks[0]))
        for person,task in sorted(eligible,key=lambda item:item[0]['participant'])[:2]:
            selected.append(dict(cohort=cohort,participant=person['participant'],
                                 time_measure=task['time_measure'],task='Test6',trial=task['trial']))
    if len(selected)!=4: raise ValueError('Need two metadata candidates per group')
    protocol=dict(version=1,created_utc=datetime.now(timezone.utc).isoformat(),
        scope='exploratory four-person non-stroke specificity pilot, not clinical validation',
        selection='first two lexicographic IDs per cohort with eligible final slow-walk trial; no replacement',
        task='Test6 slow straight walk',reference='Stereophoto.ContinuousWalkingPeriod',
        no_walking_aids=True,window_samples=500,hop_samples=250,aggregation='mean window probability per participant',
        threshold=.5,abstention='disabled',no_tuning=True,selected=selected,
        exclusions='missing/invalid reference; no full 5s window; invalid native rate/timebase/finite signals; nonempty break or turn annotations',
        reporting='per-group positive count and Wilson interval; no stroke sensitivity/AUROC; disclose all failures',
        adapter_sha256=sha(ROOT/'src/data/tvs.py'),
        metadata_sha256=sha(BASE/'lab_metadata/screening.json'),
        checkpoint_sha256=sha(ROOT/'models/checkpoints/stroke-gait-lower-back-ensemble-v0.2.0.pt'))
    with path.open('x') as f:json.dump(protocol,f,indent=2)
    (OUT/'protocol.sha256').write_text(sha(path))
    print('LOCKED',selected,flush=True)
    return protocol


def acquire(person):
    cohort,pid=person['cohort'],person['participant']
    inventory=json.loads((BASE/f'{cohort}_inventory.json').read_text())
    entry=next(e for e in inventory if e['name']==f'{cohort}/{pid}/Laboratory/data.mat')
    if entry['compressed']>65000000 or entry['size']>100000000:raise ValueError('Pilot member size cap')
    folder=OUT/cohort/pid;folder.mkdir(parents=True,exist_ok=True)
    target=folder/'data.mat'
    if target.exists():
        raw=target.read_bytes()
    else:
        url=next(f['links']['self'] for f in record['files'] if f['key']==cohort+'.zip')
        offset=entry['offset'];header=read_range(url,offset,offset+29)
        if header[:4]!=b'PK\x03\x04' or struct.unpack_from('<H',header,8)[0]!=8:raise ValueError('Invalid ZIP header')
        n,e=struct.unpack_from('<HH',header,26);start=offset+30+n+e
        compressed=read_range(url,start,start+entry['compressed']-1)
        raw=zlib.decompress(compressed,-15)
    if len(raw)!=entry['size'] or zlib.crc32(raw)!=entry['crc32']:raise ValueError('Member CRC/size mismatch')
    if not target.exists():
        temp=target.with_suffix('.part');temp.write_bytes(raw);temp.replace(target)
    (folder/'manifest.json').write_text(json.dumps(dict(member=entry['name'],sha256=sha(target),crc_verified=True,bytes=len(raw)),indent=2))
    print('ACQUIRED',cohort,pid,len(raw),flush=True)
    return target


def wilson(k,n):
    if not n:return None
    z=1.959963984540054;p=k/n;den=1+z*z/n
    center=(p+z*z/(2*n))/den;half=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [max(0.,center-half),min(1.,center+half)]


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--acquire-only',action='store_true');args=parser.parse_args()
    protocol=lock()
    if sha(OUT/'protocol.json')!=(OUT/'protocol.sha256').read_text():raise ValueError('Protocol changed')
    if sha(ROOT/'src/data/tvs.py')!=protocol['adapter_sha256']:raise ValueError('Adapter changed after lock')
    if (OUT/'results.json').exists():raise FileExistsError('Pilot already evaluated; inspect saved results')
    rows=[];arrays=[]
    for person in protocol['selected']:
        row=dict(person)
        phase='acquisition'
        try:
            path=acquire(person)
            if args.acquire_only:continue
            phase='quality'
            trial=loadmat(path,simplify_cells=True)['data'][person['time_measure']][person['task']][person['trial']]
            ref=trial.get('Standards',{}).get('Stereophoto',{}).get('ContinuousWalkingPeriod',[])
            bouts=[ref] if isinstance(ref,dict) else list(ref)
            for bout in bouts:
                for key,value in bout.items():
                    if ('Break_' in key or 'Turn' in key) and np.asarray(value).size:
                        raise ValueError('Nonempty break/turn annotation')
            x,meta,audit=trial_windows(trial)
            row.update(windows=len(x),status='included' if len(x) else 'excluded_no_complete_window',audit=audit)
            folder=path.parent
            np.save(folder/'windows.npy',x,allow_pickle=False)
            (folder/'window_metadata.json').write_text(json.dumps(meta,indent=2))
            if len(x):arrays.append((len(rows),x))
        except (ValueError,KeyError) as error:
            row.update(status='transfer_or_execution_failure' if phase=='acquisition' else 'excluded_schema_or_quality',
                       reason=str(error),windows=0)
        except Exception as error:row.update(status='transfer_or_execution_failure',reason=f'{type(error).__name__}: {error}',windows=0)
        rows.append(row)
        (OUT/'intake.json').write_text(json.dumps(rows,indent=2))
    if args.acquire_only:return
    if any(r['status']=='transfer_or_execution_failure' for r in rows):
        raise RuntimeError('Incomplete acquisition; no scoring. Resume same locked participants.')
    import torch
    from models.predict_lower_back import load_bundle,predict_windows
    torch.set_num_threads(4)
    checkpoint=ROOT/'models/checkpoints/stroke-gait-lower-back-ensemble-v0.2.0.pt'
    if sha(checkpoint)!=protocol['checkpoint_sha256']:raise ValueError('Checkpoint changed')
    bundle=load_bundle(checkpoint,checkpoint.with_suffix('.manifest.json'))
    smoke=bundle['smoke_test'];np.testing.assert_allclose(predict_windows(bundle,smoke['windows'].numpy()),smoke['expected_probabilities'].numpy(),atol=1e-6,rtol=0)
    for index,x in arrays:
        y=predict_windows(bundle,x)
        if not np.isfinite(y).all():raise ValueError('Nonfinite predictions')
        rows[index].update(probability=float(y.mean()),positive=bool(y.mean()>=protocol['threshold']),window_probabilities=y.tolist())
    groups=[]
    for c in ('HA','PD'):
        included=[r for r in rows if r['cohort']==c and r['status']=='included'];k=sum(r['positive'] for r in included);n=len(included)
        groups.append(dict(cohort=c,selected=2,evaluated=n,positive=k,negative=n-k,
                           positive_rate=k/n if n else None,wilson_95=wilson(k,n)))
    results=dict(protocol_sha256=sha(OUT/'protocol.json'),checkpoint_sha256=sha(checkpoint),scope=protocol['scope'],participants=rows,groups=groups)
    with (OUT/'results.json').open('x') as f:json.dump(results,f,indent=2)
    print('RESULT',json.dumps(groups),flush=True)


if __name__=='__main__':main()
