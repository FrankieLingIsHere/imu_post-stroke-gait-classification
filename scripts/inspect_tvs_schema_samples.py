"""Inspect downloaded TVS laboratory samples without running the classifier.

Run after acquire_tvs_schema_samples.py. Samples are format-development data,
not an untouched evaluation cohort. Raw Acc units follow the archived official
mobgap loader evidence; no sensor values are converted or normalized here.
"""
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.io import loadmat

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'data/interim/public_imu_screen_2026-09-08'


def inspect(cohort, manifest):
    path = EVIDENCE / f'{cohort}_sample/data.mat'
    provenance = next(m for m in manifest if m['member'].startswith(cohort + '/')
                      and m['member'].endswith('/data.mat'))
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != provenance['sha256']:
        raise ValueError(f'{cohort}: sample checksum mismatch')
    data = loadmat(path, simplify_cells=True)['data']
    rows = []
    for time_measure, tests in data.items():
        for test, trials in tests.items():
            last = max(trials, key=lambda name: int(name.removeprefix('Trial')))
            for trial, recording in trials.items():
                sensor = recording.get('SU', {}).get('LowerBack')
                row = dict(time_measure=time_measure, test=test, trial=trial,
                           preferred_trial=trial == last,
                           walking_task=test in {'Test5', 'Test6', 'Test7', 'Test10'})
                if not sensor:
                    rows.append(dict(row, status='missing_lower_back'))
                    continue
                acc = np.asarray(sensor.get('Acc', []))
                gyr = np.asarray(sensor.get('Gyr', []))
                fs = sensor.get('Fs', {})
                if acc.ndim != 2 or acc.shape[1] != 3 or gyr.shape != acc.shape:
                    raise ValueError(f'{cohort}/{test}/{trial}: invalid Acc/Gyr shapes')
                if fs.get('Acc') != 100 or fs.get('Gyr') != 100:
                    raise ValueError(f'{cohort}/{test}/{trial}: unexpected native rate')
                finite = bool(np.isfinite(acc).all() and np.isfinite(gyr).all())
                timestamps = np.asarray(sensor.get('Timestamp', [])).reshape(-1)
                valid_time = bool(len(timestamps) == len(acc)
                                  and np.isfinite(timestamps).all()
                                  and np.all(np.diff(timestamps) > 0))
                rows.append(dict(row, status='schema_ok' if finite else 'nonfinite',
                                 samples=len(acc), acc_shape=list(acc.shape),
                                 gyr_shape=list(gyr.shape), sampling_hz=100,
                                 duration_seconds=len(acc)/100, finite=finite,
                                 timestamps_strictly_increasing=valid_time,
                                 median_acc_norm_g=float(np.median(np.linalg.norm(acc, axis=1))),
                                 reference_systems=list(recording.get('Standards', {}))))
    return dict(cohort=cohort, member=provenance['member'], sha256=digest,
                sensor_path='SU.LowerBack', native_acc_units='g', trials=rows)


if __name__ == '__main__':
    manifest = json.loads((EVIDENCE / 'sample_manifest.json').read_text())
    result = dict(scope='schema inspection only; no model inference',
                  participants=[inspect(c, manifest) for c in ('HA', 'PD')])
    (EVIDENCE / 'tvs_schema_results.json').write_text(json.dumps(result, indent=2))
    for participant in result['participants']:
        rows = participant['trials']
        print(participant['member'], len(rows), 'trials;',
              sum(r.get('samples', 0) for r in rows), 'samples;',
              sum(r['status'] == 'schema_ok' for r in rows), 'schema_ok;',
              sum(r.get('timestamps_strictly_increasing', False) for r in rows),
              'monotonic timestamp trials')
