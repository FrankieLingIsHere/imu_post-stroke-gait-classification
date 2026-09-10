"""Execute the predeclared v0.2.0 stress test without training or tuning."""
from pathlib import Path
import hashlib
import json
import sys
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from models.predict_lower_back import load_bundle, predict_windows, RELEASE_ID
from scripts.evaluate_voisard_nonstroke_hard_negatives import magnitude_windows


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def wilson(k, n):
    z = 1.959963984540054
    p = k / n
    center = (p + z*z/(2*n)) / (1+z*z/n)
    half = z*np.sqrt(p*(1-p)/n + z*z/(4*n*n)) / (1+z*z/n)
    return max(0., center-half), min(1., center+half)


def main():
    torch.set_num_threads(4)
    processed = ROOT/'data/processed'
    prefix = 'lower_back_v020_nonstroke_stress'
    if list(processed.glob(prefix+'*')):
        raise FileExistsError('Prior stress-test outputs exist; inspect instead of overwriting')
    protocol = ROOT/'docs/LOWER_BACK_NONSTROKE_STRESS_PROTOCOL_2026-09-08.md'
    checkpoint = ROOT/'models/checkpoints'/f'{RELEASE_ID}.pt'
    manifest = checkpoint.with_suffix('.manifest.json')
    assert sha(checkpoint) == '34df2abadf862d7838dcfca7917a13c872254bde8a9a6ff9f8554e7b8a3d3ea6'
    bundle = load_bundle(checkpoint, manifest)
    expected = pd.read_csv(processed/'voisard_nonstroke_hard_negative_participant_predictions.csv')
    train = pd.read_csv(processed/'lower_back_release_freeze_participants.csv')
    train_keys = set(train.group.str.split('::', n=1).str[1])
    arrays, rows, audit = [], [], []
    hashes = {}
    raw = ROOT/'data/raw/voisard_2025/data'
    paths = sorted(list((raw/'neuro').glob('*/*/*/*_meta.json')) + list((raw/'ortho').glob('*/*/*/*_meta.json')))
    for path in paths:
        metadata = json.loads(path.read_text(encoding='utf-8'))
        cohort = metadata.get('pathologyKey')
        if cohort == 'CVA':
            continue
        if cohort not in {'ACL','CIPN','HOA','KOA','PD','RIL'}:
            raise ValueError(f'Unexpected pathology: {cohort}')
        key = f"voisard_2025:{metadata['subject']}"
        if key in train_keys:
            raise ValueError('Training participant overlap')
        windows, metadata, trial = magnitude_windows(path)
        for source in [path] + [path.parent/f'{trial}_raw_data_{sensor}.txt' for sensor in ('LB','LF','RF')]:
            hashes[str(source.relative_to(ROOT))] = sha(source)
        audit.append(dict(cohort=cohort, participant_key=key, trial_id=trial,
                          windows=len(windows), status='included' if len(windows) else 'no_5s_straight_walk_window'))
        if len(windows):
            arrays.append(windows[:, :, :1])
            rows.extend(dict(cohort=cohort, participant_key=key, trial_id=trial,
                             age=metadata.get('age'), pathology=metadata.get('pathology')) for _ in windows)
    frame = pd.DataFrame(rows)
    counts = frame.groupby(['cohort','participant_key']).size().sort_index()
    historical = expected.set_index(['cohort','participant_key']).windows.sort_index()
    pd.testing.assert_series_equal(counts, historical, check_names=False)
    assert len(counts) == 138 and len(frame) == 5340
    x = np.concatenate(arrays)
    if not np.isfinite(x).all():
        raise ValueError('Nonfinite input')
    print('Pre-inference gates passed: 138 participants, 5340 windows, no training-key overlap', flush=True)
    started = datetime.now(timezone.utc).isoformat()
    frame['probability'] = predict_windows(bundle, x, device='cuda')
    people = frame.groupby(['cohort','participant_key'], as_index=False).agg(
        age=('age','first'), pathology=('pathology','first'), windows=('probability','size'),
        probability=('probability','mean'))
    people['positive'] = people.probability.ge(.5)
    summaries = []
    for name, group in list(people.groupby('cohort')) + [('pooled', people)]:
        n, k = len(group), int(group.positive.sum())
        low, high = wilson(k, n)
        summaries.append(dict(cohort=name, participants=n, positive=k, negative=n-k,
                              positive_rate=k/n, ci_low=low, ci_high=high,
                              missing_age=int(group.age.isna().sum())))
    summary = pd.DataFrame(summaries)
    frame.to_csv(processed/f'{prefix}_windows.csv', index=False)
    people.to_csv(processed/f'{prefix}_participants.csv', index=False)
    pd.DataFrame(audit).to_csv(processed/f'{prefix}_trials.csv', index=False)
    summary.to_csv(processed/f'{prefix}_summary.csv', index=False)
    record = dict(release_id=RELEASE_ID, checkpoint_sha256=sha(checkpoint),
        protocol_sha256=sha(protocol), inference_started_utc=started,
        participant_overlap=0, participants=len(people), windows=len(frame),
        trial_status_counts=pd.Series([a['status'] for a in audit]).value_counts().to_dict(),
        threshold=.5, calibration='none', abstention='disabled', independent_validation=False,
        input_hashes=hashes,
        provenance_hashes={str(p.relative_to(ROOT)):sha(p) for p in [
            Path(__file__), ROOT/'scripts/evaluate_voisard_nonstroke_hard_negatives.py',
            ROOT/'models/predict_lower_back.py', processed/'lower_back_release_freeze_participants.csv',
            processed/'voisard_nonstroke_hard_negative_participant_predictions.csv', manifest]},
        software=dict(python=sys.version.split()[0],torch=torch.__version__,numpy=np.__version__,pandas=pd.__version__))
    (processed/f'{prefix}_provenance.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
    print(summary.to_string(index=False))
    print(record['trial_status_counts'])


if __name__ == '__main__':
    main()
