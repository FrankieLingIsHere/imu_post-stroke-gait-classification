"""Inspect already acquired TVS task duration without downloading or scoring.

This is post-pilot feasibility evidence, not a replacement pilot selection.
It never pads bouts or joins recordings to manufacture model inputs.
"""
from pathlib import Path
import hashlib
import json
import sys

from scipy.io import loadmat

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data.tvs import TASKS, trial_windows


def main():
    base = ROOT / 'data/interim/public_imu_screen_2026-09-08'
    sources = []
    for entry in json.loads((base / 'sample_manifest.json').read_text()):
        if entry['member'].endswith('/data.mat'):
            cohort, participant = entry['member'].split('/')[:2]
            sources.append((base / f'{cohort}_sample/data.mat', entry, 'schema_development'))
    for manifest in sorted((base / 'locked_pilot_v1').glob('*/*/manifest.json')):
        sources.append((manifest.parent / 'data.mat', json.loads(manifest.read_text()), 'inspected_pilot'))
    rows = []
    for path, entry, role in sources:
        if hashlib.sha256(path.read_bytes()).hexdigest() != entry['sha256']:
            raise ValueError(f'Raw checksum mismatch: {path}')
        cohort, participant = entry['member'].split('/')[:2]
        for time_measure, tests in loadmat(path, simplify_cells=True)['data'].items():
            for task in TASKS:
                row = dict(cohort=cohort, participant=participant, role=role,
                           time_measure=time_measure, task=task, windows=0)
                if task not in tests:
                    row['status'] = 'missing_task'
                else:
                    trial = max(tests[task], key=lambda name: int(name.removeprefix('Trial')))
                    row['trial'] = trial
                    try:
                        x, _, audit = trial_windows(tests[task][trial])
                        row.update(status='has_windows' if len(x) else 'no_complete_window',
                                   windows=len(x), audit=audit)
                    except (ValueError, KeyError) as error:
                        row.update(status='invalid', reason=str(error))
                rows.append(row)
    summary = [dict(cohort=cohort, task=task,
                    participants_with_windows=sum(r['windows'] > 0 for r in rows
                                                  if r['cohort'] == cohort and r['task'] == task),
                    windows=sum(r['windows'] for r in rows
                                if r['cohort'] == cohort and r['task'] == task))
               for cohort in ('HA', 'PD') for task in TASKS]
    result = dict(scope='local duration feasibility only; no predictions or clinical eligibility decision; turns not fully excluded',
                  source_count=len(sources), rows=rows, summary=summary)
    (base / 'local_duration_screen.json').write_text(json.dumps(result, indent=2))
    print(json.dumps(dict(source_count=len(sources), summary=summary), indent=2))


if __name__ == '__main__':
    main()
