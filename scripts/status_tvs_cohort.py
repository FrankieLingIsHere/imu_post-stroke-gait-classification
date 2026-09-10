"""Read-only cohort status; pending work is not inferred to be a running job."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'data/interim/public_imu_screen_2026-09-08'
OUT=BASE/'cohort_hallway_v1'


def main():
    p=json.loads((OUT/'protocol.json').read_text())
    path=OUT/'results.json'
    complete=path.exists()
    if complete:
        result=json.loads(path.read_text());intake=result['participants']
    else:
        intake=json.loads((OUT/'intake.json').read_text()) if (OUT/'intake.json').exists() else []
    by_id={(r['cohort'],r['participant']):r for r in intake}
    counts={}
    for person in p['people']:
        row=by_id.get((person['cohort'],person['participant']))
        status='excluded_metadata' if person['metadata_exclusion'] else row['status'] if row else 'pending'
        counts[status]=counts.get(status,0)+1
    new_manifests=list((OUT/'raw').glob('*/*/manifest.json'))
    raw_bytes=sum(json.loads(m.read_text())['bytes'] for m in new_manifests)
    report=dict(evaluation_complete=complete,registered=len(p['people']),accounting=counts,
                newly_acquired_raw_files=len(new_manifests),new_raw_bytes=raw_bytes,
                note='Pending does not establish whether a process is running. Read job output for transfer state.')
    if complete:report['groups']=result['groups']
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
