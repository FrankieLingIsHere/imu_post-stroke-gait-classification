"""Differential-specificity evaluation on untouched non-CVA Voisard cohorts.

These participants are never added to the binary stroke training pool.  They
share the published Voisard device/protocol but are participant-disjoint from
the HS/CVA subset, so the result measures same-protocol clinical differential
specificity rather than independent-site generalization.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import torch

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'raw' / 'voisard_2025' / 'data'
P = ROOT / 'data' / 'processed'
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
WINDOW, HOP = 500, 250


class Block(torch.nn.Module):
    def __init__(self, input_channels, output_channels=16):
        super().__init__()
        bottleneck = min(32, input_channels)
        # Attribute names deliberately mirror the saved full-expanded checkpoint.
        self.b = torch.nn.Conv1d(input_channels, bottleneck, 1, bias=False)
        self.br = torch.nn.ModuleList([
            torch.nn.Conv1d(bottleneck, output_channels, kernel, padding=kernel // 2, bias=False)
            for kernel in (7, 15, 25)
        ])
        self.pool = torch.nn.Conv1d(input_channels, output_channels, 1, bias=False)
        self.bn = torch.nn.BatchNorm1d(output_channels * 4)
        self.res = (torch.nn.Conv1d(input_channels, output_channels * 4, 1, bias=False)
                    if input_channels != output_channels * 4 else torch.nn.Identity())

    def forward(self, x):
        z = self.b(x)
        pooled = self.pool(torch.nn.functional.max_pool1d(x, 3, 1, 1))
        return torch.nn.functional.gelu(self.bn(torch.cat([b(z) for b in self.br] + [pooled], 1)) + self.res(x))


class Net(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.f = torch.nn.Sequential(Block(3), torch.nn.MaxPool1d(2), Block(64), torch.nn.AdaptiveAvgPool1d(1))
        self.c = torch.nn.Sequential(torch.nn.Flatten(), torch.nn.Dropout(0.3), torch.nn.Linear(64, 1))

    def forward(self, x):
        return self.c(self.f(x)).squeeze(1)


def walking_bounds(meta):
    turn_start, turn_end = meta['uturnBoundaries']
    events = [event for side in ('leftGaitEvents', 'rightGaitEvents') for event in (meta.get(side) or [])]
    before = [event for event in events if event[1] < turn_start]
    after = [event for event in events if event[0] > turn_end]
    return ([(min(e[0] for e in before), max(e[1] for e in before))] if before else []) + \
           ([(min(e[0] for e in after), max(e[1] for e in after))] if after else [])


def magnitude_windows(meta_path):
    meta = json.loads(meta_path.read_text(encoding='utf-8'))
    if float(meta.get('freq', 0)) != 100.0:
        raise ValueError(f"Unexpected sampling rate: {meta_path}")
    trial_id, base = meta_path.stem.removesuffix('_meta'), meta_path.parent
    sensors = []
    for sensor in ('LB', 'LF', 'RF'):
        frame = pd.read_csv(base / f'{trial_id}_raw_data_{sensor}.txt', sep='\t')
        sensors.append(frame[['Acc_X', 'Acc_Y', 'Acc_Z']].to_numpy('float32') / 9.80665)
    length = min(map(len, sensors))
    signal = np.column_stack([np.linalg.norm(values[:length], axis=1) for values in sensors]).astype('float32')
    starts = [start for begin, end in walking_bounds(meta)
              for start in range(int(begin), int(end) - WINDOW + 1, HOP)
              if start + WINDOW <= length]
    windows = np.stack([signal[start:start + WINDOW] for start in starts]) if starts else np.empty((0, WINDOW, 3), dtype='float32')
    return windows, meta, trial_id


def main():
    checkpoint = torch.load(P / 'full_expanded_inception_prototype_seed_42.pt', map_location='cpu', weights_only=False)
    model = Net().to(DEVICE)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    mean = np.asarray(checkpoint['mean'], dtype='float32')
    std = np.asarray(checkpoint['std'], dtype='float32').clip(1e-4)
    rows, audit = [], []
    # Explicitly exclude HS and CVA: all inputs below are non-stroke hard negatives.
    meta_paths = sorted(list((RAW / 'neuro').glob('*/*/*/*_meta.json')) + list((RAW / 'ortho').glob('*/*/*/*_meta.json')))
    for meta_path in meta_paths:
        try:
            windows, meta, trial_id = magnitude_windows(meta_path)
            pathology = str(meta.get('pathologyKey', ''))
            if pathology == 'CVA':
                continue
            audit.append({'cohort': pathology, 'participant_key': f"voisard_2025:{meta['subject']}", 'trial_id': trial_id,
                          'windows': len(windows), 'status': 'included' if len(windows) else 'no_5s_straight_walk_window'})
            if not len(windows):
                continue
            with torch.no_grad():
                xb = torch.from_numpy(((windows - mean) / std).transpose(0, 2, 1)).to(DEVICE)
                probability = torch.sigmoid(model(xb)).cpu().numpy()
            rows.extend({'cohort': pathology, 'participant_key': f"voisard_2025:{meta['subject']}", 'trial_id': trial_id,
                         'age': meta.get('age'), 'pathology': meta.get('pathology'), 'window_probability': float(p)} for p in probability)
        except Exception as error:
            audit.append({'cohort': meta_path.parts[-4], 'participant_key': 'unknown', 'trial_id': meta_path.stem,
                          'windows': 0, 'status': f'error: {type(error).__name__}'})
    window = pd.DataFrame(rows)
    if window.empty:
        raise RuntimeError('No valid non-CVA windows were materialized; do not write an empty evaluation.')
    participant = window.groupby(['cohort', 'participant_key'], as_index=False).agg(
        age=('age', 'first'), pathology=('pathology', 'first'), windows=('window_probability', 'size'),
        mean_stroke_probability=('window_probability', 'mean'))
    for threshold in (0.50, 0.78):
        participant[f'predicted_stroke_at_{threshold:.2f}'] = participant.mean_stroke_probability >= threshold
    summary = participant.groupby('cohort', as_index=False).agg(
        participants=('participant_key', 'size'), mean_probability=('mean_stroke_probability', 'mean'),
        median_probability=('mean_stroke_probability', 'median'), q90_probability=('mean_stroke_probability', lambda x: x.quantile(.9)),
        false_positive_rate_at_0_50=('predicted_stroke_at_0.50', 'mean'),
        false_positive_rate_at_0_78=('predicted_stroke_at_0.78', 'mean'))
    window.to_csv(P / 'voisard_nonstroke_hard_negative_window_predictions.csv', index=False)
    participant.to_csv(P / 'voisard_nonstroke_hard_negative_participant_predictions.csv', index=False)
    pd.DataFrame(audit).to_csv(P / 'voisard_nonstroke_hard_negative_trial_audit.csv', index=False)
    summary.to_csv(P / 'voisard_nonstroke_hard_negative_summary.csv', index=False)
    print(summary.round(3).to_string(index=False))
    print({'participants': len(participant), 'windows': len(window), 'device': str(DEVICE)})


if __name__ == '__main__':
    main()
