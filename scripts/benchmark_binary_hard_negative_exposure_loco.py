"""Binary stroke-score hard-negative exposure, leave-one-pathology-cohort-out.

Output stays binary (stroke probability).  Non-CVA cohorts are assigned a
temporary negative *exposure* target, never renamed healthy and never merged
into the primary baseline.  One entire pathology cohort is withheld per run.
This is a feasibility benchmark only: it cannot establish independent-site
generalization or replace the frozen primary binary model.
"""
from pathlib import Path
import os
import json
import numpy as np
import pandas as pd
import torch

ROOT = Path(__file__).resolve().parents[1]
P, RAW = ROOT / 'data' / 'processed', ROOT / 'data' / 'raw' / 'voisard_2025' / 'data'
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
WINDOW, HOP, EPOCHS, STEPS = 500, 250, 8, 50
HARD_PER_COHORT = int(os.getenv('HARD_PER_COHORT', '8'))


class Block(torch.nn.Module):
    def __init__(self, ic, oc=16):
        super().__init__(); b = min(32, ic)
        self.b = torch.nn.Conv1d(ic, b, 1, bias=False)
        self.br = torch.nn.ModuleList([torch.nn.Conv1d(b, oc, k, padding=k // 2, bias=False) for k in (7, 15, 25)])
        self.pool = torch.nn.Conv1d(ic, oc, 1, bias=False); self.bn = torch.nn.BatchNorm1d(oc * 4)
        self.res = torch.nn.Conv1d(ic, oc * 4, 1, bias=False) if ic != oc * 4 else torch.nn.Identity()
    def forward(self, x):
        z = self.b(x); q = [v(z) for v in self.br] + [self.pool(torch.nn.functional.max_pool1d(x, 3, 1, 1))]
        return torch.nn.functional.gelu(self.bn(torch.cat(q, 1)) + self.res(x))


class Net(torch.nn.Module):
    def __init__(self):
        super().__init__(); self.f = torch.nn.Sequential(Block(3), torch.nn.MaxPool1d(2), Block(64), torch.nn.AdaptiveAvgPool1d(1)); self.c = torch.nn.Sequential(torch.nn.Flatten(), torch.nn.Dropout(.3), torch.nn.Linear(64, 1))
    def forward(self, x): return self.c(self.f(x)).squeeze(1)


def bounds(meta):
    a, b = meta['uturnBoundaries']; events = [e for side in ('leftGaitEvents', 'rightGaitEvents') for e in (meta.get(side) or [])]
    pre, post = [e for e in events if e[1] < a], [e for e in events if e[0] > b]
    return ([(min(e[0] for e in pre), max(e[1] for e in pre))] if pre else []) + ([(min(e[0] for e in post), max(e[1] for e in post))] if post else [])


def load_hard_negatives():
    arrays, rows = [], []
    meta_paths = sorted(list((RAW / 'neuro').glob('*/*/*/*_meta.json')) + list((RAW / 'ortho').glob('*/*/*/*_meta.json')))
    for path in meta_paths:
        meta = json.loads(path.read_text(encoding='utf-8')); cohort = meta.get('pathologyKey')
        if cohort == 'CVA' or float(meta.get('freq', 0)) != 100.0: continue
        trial = path.stem.removesuffix('_meta'); sig = []
        for sensor in ('LB', 'LF', 'RF'):
            df = pd.read_csv(path.parent / f'{trial}_raw_data_{sensor}.txt', sep='\t')
            sig.append(df[['Acc_X', 'Acc_Y', 'Acc_Z']].to_numpy('float32') / 9.80665)
        n = min(map(len, sig)); mag = np.column_stack([np.linalg.norm(q[:n], axis=1) for q in sig]).astype('float32')
        for start, end in bounds(meta):
            for left in range(int(start), int(end) - WINDOW + 1, HOP):
                if left + WINDOW <= n:
                    arrays.append(mag[left:left + WINDOW]); rows.append({'cohort': cohort, 'participant_key': f"voisard_2025:{meta['subject']}", 'trial_id': trial})
    return np.stack(arrays).astype('float32'), pd.DataFrame(rows)


def infer(model, x, mean, std):
    model.eval(); out = []
    with torch.no_grad():
        for start in range(0, len(x), 512):
            z = torch.from_numpy(((x[start:start + 512] - mean) / std).transpose(0, 2, 1).astype('float32')).to(DEVICE)
            out.append(torch.sigmoid(model(z)).cpu().numpy())
    return np.concatenate(out)


def main():
    torch.backends.cudnn.benchmark = True
    x_primary = np.concatenate([np.load(P / 'validated_acceleration_magnitude_windows_float32.npy'), np.load(P / 'sint_maartenskliniek_external_windows_float32.npy')])
    primary = pd.concat([pd.read_csv(P / 'validated_window_metadata.csv'), pd.read_csv(P / 'sint_maartenskliniek_external_window_metadata.csv')], ignore_index=True)
    keep = primary.label.isin(['healthy', 'stroke']).to_numpy(); x_primary, primary = x_primary[keep], primary.loc[keep].reset_index(drop=True)
    primary['y'] = (primary.label == 'stroke').astype(int)
    x_hard, hard = load_hard_negatives()
    checkpoint = torch.load(P / 'full_expanded_inception_prototype_seed_42.pt', map_location='cpu', weights_only=False)
    mean, std = np.asarray(checkpoint['mean'], dtype='float32'), np.asarray(checkpoint['std'], dtype='float32').clip(1e-4)
    primary_pools = [np.where((primary.dataset_id == source).to_numpy() & (primary.y == cls).to_numpy())[0]
                     for source in sorted(primary.dataset_id.unique()) for cls in (0, 1)]
    rows, predictions = [], []
    for run, heldout in enumerate(sorted(hard.cohort.unique())):
        torch.manual_seed(300 + run); rng = np.random.default_rng(300 + run)
        train_hard = np.where(hard.cohort.ne(heldout).to_numpy())[0]; test_hard = np.where(hard.cohort.eq(heldout).to_numpy())[0]
        hard_pools = [train_hard[hard.cohort.iloc[train_hard].eq(c).to_numpy()] for c in sorted(hard.cohort[hard.cohort.ne(heldout)].unique())]
        model = Net().to(DEVICE); model.load_state_dict(checkpoint['model_state_dict'])
        opt = torch.optim.AdamW(model.parameters(), lr=1e-4, weight_decay=1e-4)
        # ~20% hard-negative exposure; six primary source/class cells retain ~80% mass.
        for _ in range(EPOCHS):
            model.train()
            for _ in range(STEPS):
                pi = np.concatenate([rng.choice(pool, 24, replace=len(pool) < 24) for pool in primary_pools])
                hi = np.concatenate([rng.choice(pool, HARD_PER_COHORT, replace=len(pool) < HARD_PER_COHORT) for pool in hard_pools])
                x = np.concatenate([x_primary[pi], x_hard[hi]])
                y = np.concatenate([primary.y.iloc[pi].to_numpy('float32'), np.zeros(len(hi), dtype='float32')])
                xb = torch.from_numpy(((x - mean) / std).transpose(0, 2, 1).astype('float32')).to(DEVICE); yb = torch.from_numpy(y).to(DEVICE)
                opt.zero_grad(); loss = torch.nn.functional.binary_cross_entropy_with_logits(model(xb), yb); loss.backward(); opt.step()
        base = Net().to(DEVICE); base.load_state_dict(checkpoint['model_state_dict'])
        before, after = infer(base, x_hard[test_hard], mean, std), infer(model, x_hard[test_hard], mean, std)
        result = hard.iloc[test_hard][['cohort', 'participant_key', 'trial_id']].copy(); result['baseline_window_probability'] = before; result['exposure_window_probability'] = after
        person = result.groupby(['cohort', 'participant_key'], as_index=False).mean(numeric_only=True)
        row = {'heldout_cohort': heldout, 'participants': len(person),
               'baseline_fpr_at_0_50': float((person.baseline_window_probability >= .5).mean()),
               'exposure_fpr_at_0_50': float((person.exposure_window_probability >= .5).mean()),
               'baseline_fpr_at_0_78': float((person.baseline_window_probability >= .78).mean()),
               'exposure_fpr_at_0_78': float((person.exposure_window_probability >= .78).mean()),
               'baseline_mean_probability': float(person.baseline_window_probability.mean()),
               'exposure_mean_probability': float(person.exposure_window_probability.mean()),
               'hard_windows_per_training_cohort_per_batch': HARD_PER_COHORT}
        rows.append(row); result['heldout_cohort'] = heldout; predictions.append(result); print(row, flush=True)
    suffix = '' if HARD_PER_COHORT == 8 else f'_h{HARD_PER_COHORT}'
    pd.DataFrame(rows).to_csv(P / f'binary_hard_negative_exposure_loco_metrics{suffix}.csv', index=False)
    pd.concat(predictions, ignore_index=True).to_csv(P / f'binary_hard_negative_exposure_loco_window_predictions{suffix}.csv', index=False)
    print(pd.DataFrame(rows).round(3).to_string(index=False)); print('device', DEVICE)


if __name__ == '__main__': main()
