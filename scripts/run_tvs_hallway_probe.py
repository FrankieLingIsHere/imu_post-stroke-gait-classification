"""Offline, frozen hallway-task probe on four already inspected TVS people.

This is not straight-walking validation: TVS reference systems do not annotate
turns. Keep possible turns; exclude recorded breaks using the frozen adapter.
No download, replacement, threshold search, or model selection is performed.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import sys

import numpy as np
from scipy.io import loadmat

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data.tvs import trial_windows

BASE = ROOT / 'data/interim/public_imu_screen_2026-09-08'
OUT = BASE / 'hallway_probe_v1'
CHECKPOINT = ROOT / 'models/checkpoints/stroke-gait-lower-back-ensemble-v0.2.0.pt'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def annotation_audit(value, prefix='Standards'):
    """Record annotation availability; an empty field never means no turns."""
    rows = []
    if isinstance(value, dict):
        for key, child in value.items():
            path = prefix + '/' + key
            if 'turn' in key.lower() or key.startswith('Break_'):
                a = np.asarray(child)
                rows.append(dict(path=path, size=int(a.size), empty=not bool(a.size)))
            rows.extend(annotation_audit(child, path))
    elif isinstance(value, (list, tuple, np.ndarray)):
        for i, child in enumerate(np.asarray(value, dtype=object).reshape(-1)):
            if isinstance(child, dict):
                rows.extend(annotation_audit(child, prefix + '/' + str(i)))
    return rows


def checked_json(path, digest):
    if sha(path) != digest:
        raise ValueError(f'Changed locked artifact: {path}')
    return json.loads(path.read_text())


def protocol():
    OUT.mkdir(exist_ok=True)
    path = OUT / 'protocol.json'
    if path.exists():
        return checked_json(path, (OUT / 'protocol.sha256').read_text())
    parent = BASE / 'locked_pilot_v1'
    old = checked_json(parent / 'protocol.json', (parent / 'protocol.sha256').read_text())
    people = []
    for person in old['selected']:
        raw = parent / person['cohort'] / person['participant'] / 'data.mat'
        manifest = json.loads((raw.parent / 'manifest.json').read_text())
        if sha(raw) != manifest['sha256']:
            raise ValueError('Raw member mismatch before lock')
        people.append(dict(cohort=person['cohort'], participant=person['participant'],
                           time_measure='TimeMeasure1', task='Test10', trial='Trial1',
                           raw_sha256=manifest['sha256']))
    p = dict(version=1, created_utc=datetime.now(timezone.utc).isoformat(),
             scope='exploratory hallway-task positive calls on inspected participants; not straight-only or clinical validation',
             selection='same four people as completed Test6 pilot; no replacement; schema pair excluded',
             prior_inspection='raw durations and one Test6 PD prediction already inspected; hallway selected for duration before hallway scoring',
             people=people, window_samples=500, hop_samples=250, units='g',
             aggregation='mean window score per person', threshold=.5,
             turns='unavailable reference truth; retain possible turns; no inferred turn filtering',
             breaks='exclude crossing windows with existing adapter',
             failure_policy='any missing/invalid/short participant stops all scoring; no replacements',
             no_tuning=True, abstention='disabled',
             adapter_sha256=sha(ROOT / 'src/data/tvs.py'),
             runner_sha256=sha(Path(__file__)), checkpoint_sha256=sha(CHECKPOINT),
             metadata_sha256=sha(BASE / 'lab_metadata/screening.json'),
             dataset_description_sha256=sha(BASE / 'tvs.json'),
             parent_results_sha256=sha(parent / 'results.json'))
    with path.open('x') as f:
        json.dump(p, f, indent=2)
    (OUT / 'protocol.sha256').write_text(sha(path))
    return p


def main():
    if (OUT / 'results.json').exists():
        raise FileExistsError('Hallway already evaluated; read saved results')
    p = protocol()
    for path, key in [(ROOT / 'src/data/tvs.py', 'adapter_sha256'),
                      (Path(__file__), 'runner_sha256'), (CHECKPOINT, 'checkpoint_sha256'),
                      (BASE / 'tvs.json', 'dataset_description_sha256'),
                      (BASE / 'lab_metadata/screening.json', 'metadata_sha256'),
                      (BASE / 'locked_pilot_v1/results.json', 'parent_results_sha256')]:
        if sha(path) != p[key]:
            raise ValueError(f'Changed after lock: {path}')
    rows, arrays = [], []
    metadata = json.loads((BASE / 'lab_metadata/screening.json').read_text())
    for person in p['people']:
        raw = BASE / 'locked_pilot_v1' / person['cohort'] / person['participant'] / 'data.mat'
        if sha(raw) != person['raw_sha256']:
            raise ValueError('Raw data changed after lock')
        info = next(v for v in metadata if v['cohort'] == person['cohort']
                    and v['participant'] == person['participant'])
        task = next(v for v in info['tasks'] if v['task'] == 'Test10')
        if not (task['sensor'] == 'MM+' and task['walking_aid'] == 0
                and task['has_lower_back'] and task['has_stereophoto']
                and not task['annotations'] and task['trial'] == person['trial']
                and task['time_measure'] == person['time_measure']):
            raise ValueError('Metadata no longer matches selected hallway protocol')
        trial = loadmat(raw, simplify_cells=True)['data'][person['time_measure']]['Test10'][person['trial']]
        x, windows, audit = trial_windows(trial)
        if not len(x):
            raise ValueError('No complete hallway window; stop without replacement')
        folder = OUT / person['cohort'] / person['participant']
        folder.mkdir(parents=True, exist_ok=True)
        np.save(folder / 'windows.npy', x, allow_pickle=False)
        (folder / 'window_metadata.json').write_text(json.dumps(windows, indent=2))
        rows.append(dict(person, windows=len(x), windows_sha256=sha(folder / 'windows.npy'),
                         straight_only_verified=False,
                         annotations=annotation_audit(trial['Standards']), bouts=audit))
        arrays.append(x)
    (OUT / 'intake.json').write_text(json.dumps(rows, indent=2))
    import torch
    from models.predict_lower_back import load_bundle, predict_windows
    torch.set_num_threads(4)
    bundle = load_bundle(CHECKPOINT, CHECKPOINT.with_suffix('.manifest.json'))
    smoke = bundle['smoke_test']
    np.testing.assert_allclose(predict_windows(bundle, smoke['windows'].numpy()),
                               smoke['expected_probabilities'].numpy(), atol=1e-6, rtol=0)
    for row, x in zip(rows, arrays):
        scores = predict_windows(bundle, x)
        if not (np.isfinite(scores).all() and ((scores >= 0) & (scores <= 1)).all()):
            raise ValueError('Invalid model output')
        row.update(window_scores=scores.tolist(), mean_score=float(scores.mean()),
                   positive=bool(scores.mean() >= p['threshold']))
    groups = []
    for cohort in ('HA', 'PD'):
        people = [row for row in rows if row['cohort'] == cohort]
        groups.append(dict(cohort=cohort, evaluated=len(people),
                           positive=sum(row['positive'] for row in people)))
    result = dict(scope=p['scope'], protocol_sha256=sha(OUT / 'protocol.json'),
                  checkpoint_sha256=p['checkpoint_sha256'], participants=rows, groups=groups,
                  release_smoke_passed=True)
    with (OUT / 'results.json').open('x') as f:
        json.dump(result, f, indent=2)
    print(json.dumps(dict(groups=groups, people=[{k:row[k] for k in
                     ('cohort', 'participant', 'windows', 'mean_score', 'positive')} for row in rows]), indent=2))


if __name__ == '__main__':
    main()
