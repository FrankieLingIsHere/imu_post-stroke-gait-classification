"""Materialize audited TVS sample windows; does not score or tune a model."""
from pathlib import Path
import hashlib
import json
import sys
import numpy as np
from scipy.io import loadmat

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data.tvs import TASKS, trial_windows


def main():
    source = ROOT/'data/interim/public_imu_screen_2026-09-08'
    output = source/'prepared'
    output.mkdir(exist_ok=True)
    manifest = json.loads((source/'sample_manifest.json').read_text())
    arrays, metadata, audit = [], [], []
    for cohort in ('HA', 'PD'):
        path = source/f'{cohort}_sample/data.mat'
        entry = next(e for e in manifest if e['member'].startswith(cohort+'/')
                     and e['member'].endswith('/data.mat'))
        if hashlib.sha256(path.read_bytes()).hexdigest() != entry['sha256']:
            raise ValueError('Sample hash mismatch')
        participant = entry['member'].split('/')[1]
        for time_measure, tests in loadmat(path, simplify_cells=True)['data'].items():
            for test in TASKS:
                identity = dict(cohort=cohort, participant=participant,
                                time_measure=time_measure, test=test)
                if test not in tests:
                    audit.append(dict(identity, status='missing_task', windows=0))
                    continue
                trials = tests[test]
                last = max(trials, key=lambda n:int(n.removeprefix('Trial')))
                identity['trial'] = last
                x, rows, decisions = trial_windows(trials[last])
                arrays.append(x)
                metadata.extend(dict(identity, **r) for r in rows)
                audit.extend(dict(identity, **r) for r in decisions)
    windows = np.concatenate(arrays)
    if not len(windows):
        raise ValueError('No complete walking windows')
    np.save(output/'windows.npy', windows, allow_pickle=False)
    (output/'window_metadata.json').write_text(json.dumps(metadata, indent=2))
    (output/'exclusions.json').write_text(json.dumps(audit, indent=2))
    summary = dict(scope='schema-development only; turns not excluded; no clinical metrics',
                   shape=list(windows.shape), dtype=str(windows.dtype), units='g',
                   hop=250, reference='Stereophoto.ContinuousWalkingPeriod',
                   by_cohort={c:sum(r['cohort']==c for r in metadata) for c in ('HA','PD')},
                   windows_sha256=hashlib.sha256((output/'windows.npy').read_bytes()).hexdigest())
    (output/'summary.json').write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
