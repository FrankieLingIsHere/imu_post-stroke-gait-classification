"""Download only laboratory metadata for HA/PD and inventory matched tasks.

No signals or model scores are loaded. Includes all 40 laboratory participants;
the two opened schema-development subjects are marked and excluded from selection.
"""
import io
import json
import struct
import sys
import zlib
import hashlib
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from scipy.io import loadmat

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.acquire_tvs_schema_samples import read_range, record

BASE = ROOT/'data/interim/public_imu_screen_2026-09-08'
OUT = BASE/'lab_metadata'


def member_bytes(cohort, entry):
    url = next(f['links']['self'] for f in record['files'] if f['key']==cohort+'.zip')
    # Metadata only: cap before making a request. Extra bytes cover ZIP headers.
    if entry['compressed'] > 100000 or entry['size'] > 1000000:
        raise ValueError('Not a small metadata member')
    block = read_range(url, entry['offset'], entry['offset']+entry['compressed']+1023)
    if block[:4] != b'PK\x03\x04': raise ValueError('Invalid ZIP header')
    method = struct.unpack_from('<H', block, 8)[0]
    name_len, extra_len = struct.unpack_from('<HH', block, 26)
    start = 30+name_len+extra_len
    if block[30:30+name_len].decode() != entry['name']: raise ValueError('Wrong ZIP member')
    compressed = block[start:start+entry['compressed']]
    raw = zlib.decompress(compressed, -15) if method == 8 else compressed
    if method not in (0,8) or len(raw)!=entry['size'] or zlib.crc32(raw)!=entry['crc32']:
        raise ValueError('Metadata CRC/length mismatch')
    return raw


def screen(pair):
    cohort, entries = pair
    participant = entries[0]['name'].split('/')[1]
    folder = OUT/cohort/participant
    folder.mkdir(parents=True, exist_ok=True)
    hashes = {}
    for entry in entries:
        target = folder/Path(entry['name']).name
        sample = BASE/f'{cohort}_sample'/target.name
        if not target.exists() and (cohort,participant) in {('HA','4109'),('PD','4020')} and sample.exists():
            # Reuse already acquired schema files; CRC below checks their identity.
            target.write_bytes(sample.read_bytes())
        raw = target.read_bytes() if target.exists() else member_bytes(cohort, entry)
        if len(raw)!=entry['size'] or zlib.crc32(raw)!=entry['crc32']:
            raise ValueError('Cached metadata CRC mismatch')
        target.write_bytes(raw)
        hashes[target.name] = hashlib.sha256(raw).hexdigest()
    tests = json.loads((folder/'test_list.json').read_text())['data']
    info = loadmat(io.BytesIO((folder/'infoForAlgo.mat').read_bytes()), simplify_cells=True)['infoForAlgo']
    rows=[]
    for tm, details in info.items():
        for task in ('Test5','Test6','Test7','Test10'):
            candidates=[t for t in tests if t['key'][:2]==[tm,task]]
            last=max(candidates,key=lambda t:int(t['key'][2].removeprefix('Trial'))) if candidates else None
            value=last['value'] if last else {}
            rows.append(dict(time_measure=tm,task=task,trial=last['key'][2] if last else None,
                has_lower_back=['SU','LowerBack'] in value.get('available_sensors',[]),
                has_stereophoto='Stereophoto' in value.get('available_reference_systems',[]),
                sensor=details.get('SensorType_SU'),walking_aid=details.get('WalkingAid_01'),
                annotations=details.get('Annotations',{}).get(task,{})))
    result=dict(cohort=cohort,participant=participant,
                schema_development=(cohort,participant) in {('HA','4109'),('PD','4020')},
                tasks=rows,metadata_sha256=hashes)
    (folder/'screen.json').write_text(json.dumps(result,indent=2,default=str))
    print(cohort,participant,'metadata verified',flush=True)
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--offline',action='store_true',help='Use cached metadata only; never fetch')
    args=parser.parse_args()
    jobs=[]
    for cohort in ('HA','PD'):
        entries=json.loads((BASE/f'{cohort}_inventory.json').read_text())
        subjects=sorted({e['name'].split('/')[1] for e in entries if e['name'].endswith('/Laboratory/data.mat')})
        for subject in subjects:
            selected=[e for e in entries if e['name'] in
                {f'{cohort}/{subject}/Laboratory/infoForAlgo.mat',f'{cohort}/{subject}/Laboratory/test_list.json'}]
            if len(selected)!=2:raise ValueError('Missing participant metadata member')
            jobs.append((cohort,selected))
    OUT.mkdir(parents=True,exist_ok=True)
    results=[]
    failures=[]
    pending=[]
    for job in jobs:
        cohort,entries=job
        participant=entries[0]['name'].split('/')[1]
        folder=OUT/cohort/participant
        cached=all((folder/Path(e['name']).name).exists() for e in entries)
        if cached or (cohort,participant) in {('HA','4109'),('PD','4020')}:
            results.append(screen(job))
        else:pending.append(job)
    def attempt(job):
        try:return screen(job),None
        except Exception as error:
            return None,dict(cohort=job[0],participant=job[1][0]['name'].split('/')[1],
                             status='pending_transfer',error=f'{type(error).__name__}: {error}')
    if not args.offline:
        for start in range(0,len(pending),4):
            with ThreadPoolExecutor(max_workers=4) as pool:batch=list(pool.map(attempt,pending[start:start+4]))
            results.extend(r for r,e in batch if r is not None)
            failures.extend(e for r,e in batch if e is not None)
            (OUT/'screening.json').write_text(json.dumps(results,indent=2,default=str))
            if not any(r is not None for r,e in batch):
                print('No transfers completed in this batch; stopping network retries.',flush=True)
                break
    (OUT/'screening.json').write_text(json.dumps(results,indent=2,default=str))
    completed={(r['cohort'],r['participant']) for r in results}
    unresolved=[dict(cohort=c,participant=e[0]['name'].split('/')[1],status='pending_transfer')
                for c,e in jobs if (c,e[0]['name'].split('/')[1]) not in completed]
    state=dict(total_candidates=len(jobs),metadata_verified=len(results),pending=unresolved,
               transfer_errors=failures,selection_ready=not unresolved,
               rule='Transfer failures are pending, never clinical exclusions. Complete metadata before selecting.')
    (OUT/'intake_status.json').write_text(json.dumps(state,indent=2))
    for c in ('HA','PD'):
        for task in ('Test5','Test6','Test7','Test10'):
            eligible=[r['participant'] for r in results if r['cohort']==c and not r['schema_development']
                      and any(t['task']==task and t['has_lower_back'] and t['has_stereophoto']
                              and t['sensor']=='MM+' and not t['annotations'] for t in r['tasks'])]
            print(c,task,len(eligible),eligible)
    print('Verified',len(results),'pending',len(unresolved),'selection ready',not unresolved)
    return 2 if unresolved else 0


if __name__=='__main__':raise SystemExit(main())
