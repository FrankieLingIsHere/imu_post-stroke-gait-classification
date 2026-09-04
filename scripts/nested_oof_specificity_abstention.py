"""Lock a specificity-first operating rule from development-only participant OOF predictions.

RevalExo is deliberately absent: this script is for operating-rule development only.
Each participant appears in exactly one validation fold, and every fold's normalization
and model fit use only the other participants.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from sklearn.metrics import roc_auc_score, brier_score_loss, balanced_accuracy_score
from sklearn.model_selection import StratifiedGroupKFold

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / 'data' / 'processed'
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
SEED, FOLDS, EPOCHS, STEPS = 73, 5, 12, 50


class Block(torch.nn.Module):
    def __init__(self, input_channels, output_channels=16):
        super().__init__()
        bottleneck = min(32, input_channels)
        self.bottleneck = torch.nn.Conv1d(input_channels, bottleneck, 1, bias=False)
        self.branches = torch.nn.ModuleList([
            torch.nn.Conv1d(bottleneck, output_channels, kernel, padding=kernel // 2, bias=False)
            for kernel in (7, 15, 25)
        ])
        self.pool = torch.nn.Conv1d(input_channels, output_channels, 1, bias=False)
        self.norm = torch.nn.BatchNorm1d(output_channels * 4)
        self.residual = (torch.nn.Conv1d(input_channels, output_channels * 4, 1, bias=False)
                         if input_channels != output_channels * 4 else torch.nn.Identity())

    def forward(self, x):
        z = self.bottleneck(x)
        pooled = self.pool(torch.nn.functional.max_pool1d(x, 3, 1, 1))
        out = torch.cat([branch(z) for branch in self.branches] + [pooled], dim=1)
        return torch.nn.functional.gelu(self.norm(out) + self.residual(x))


class Net(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.features = torch.nn.Sequential(
            Block(3), torch.nn.MaxPool1d(2), Block(64), torch.nn.AdaptiveAvgPool1d(1))
        self.head = torch.nn.Sequential(torch.nn.Flatten(), torch.nn.Dropout(0.3), torch.nn.Linear(64, 1))

    def forward(self, x):
        return self.head(self.features(x)).squeeze(1)


def load_development():
    arrays = [np.load(P / 'validated_acceleration_magnitude_windows_float32.npy'),
              np.load(P / 'sint_maartenskliniek_external_windows_float32.npy')]
    metadata = [pd.read_csv(P / 'validated_window_metadata.csv'),
                pd.read_csv(P / 'sint_maartenskliniek_external_window_metadata.csv')]
    x, m = np.concatenate(arrays), pd.concat(metadata, ignore_index=True)
    keep = m.label.isin(['healthy', 'stroke']).to_numpy()
    m = m.loc[keep].reset_index(drop=True)
    m['y'] = (m.label == 'stroke').astype(int)
    return x[keep], m


def participant_frame(m):
    cols = ['participant_key', 'dataset_id', 'y']
    p = m[cols].drop_duplicates('participant_key').reset_index(drop=True)
    if p.groupby('participant_key').size().max() != 1:
        raise RuntimeError('Participant labels/source must be unique.')
    return p


def train_fold(x, m, train_people, valid_people, fold):
    torch.manual_seed(SEED + fold)
    rng = np.random.default_rng(SEED + fold)
    train_mask = m.participant_key.isin(train_people).to_numpy()
    valid_mask = m.participant_key.isin(valid_people).to_numpy()
    mu = x[train_mask].reshape(-1, 3).mean(axis=0)
    sd = x[train_mask].reshape(-1, 3).std(axis=0).clip(1e-4)
    pools = []
    for source in sorted(m.loc[train_mask, 'dataset_id'].unique()):
        for cls in (0, 1):
            ids = np.where(train_mask & m.dataset_id.eq(source).to_numpy() & m.y.eq(cls).to_numpy())[0]
            if len(ids):
                pools.append(ids)
    model = Net().to(DEVICE)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    for _ in range(EPOCHS):
        model.train()
        for _ in range(STEPS):
            ids = np.concatenate([rng.choice(ids, min(32, len(ids)), replace=len(ids) < 32) for ids in pools])
            xb = torch.from_numpy(((x[ids] - mu) / sd).transpose(0, 2, 1).astype('float32')).to(DEVICE)
            yb = torch.from_numpy(m.y.iloc[ids].to_numpy('float32')).to(DEVICE)
            optimizer.zero_grad()
            loss = torch.nn.functional.binary_cross_entropy_with_logits(model(xb), yb)
            loss.backward()
            optimizer.step()
    model.eval()
    values = x[valid_mask]
    with torch.no_grad():
        probability = torch.sigmoid(model(torch.from_numpy(((values - mu) / sd).transpose(0, 2, 1).astype('float32')).to(DEVICE))).cpu().numpy()
    out = m.loc[valid_mask, ['participant_key', 'dataset_id', 'y']].copy()
    out['window_probability'] = probability
    out = out.groupby(['participant_key', 'dataset_id', 'y'], as_index=False).window_probability.mean()
    out['fold'] = fold
    return out


def wilson_lower(successes, total):
    """Two-sided 95% Wilson lower confidence bound, without optional packages."""
    if total == 0:
        return float('nan')
    z = 1.959963984540054
    p = successes / total
    denominator = 1 + z * z / total
    centre = p + z * z / (2 * total)
    radius = z * np.sqrt((p * (1 - p) + z * z / (4 * total)) / total)
    return float((centre - radius) / denominator)


def threshold_table(pred):
    rows = []
    for threshold in np.round(np.arange(0.05, 0.951, 0.01), 2):
        healthy = pred[pred.y == 0]
        stroke = pred[pred.y == 1]
        specificity = float((healthy.probability < threshold).mean())
        sensitivity = float((stroke.probability >= threshold).mean())
        source_specificity = healthy.groupby('dataset_id')['probability'].apply(lambda z: (z < threshold).mean())
        source_sensitivity = stroke.groupby('dataset_id')['probability'].apply(lambda z: (z >= threshold).mean())
        rows.append({
            'threshold': threshold,
            'specificity': specificity,
            'specificity_wilson_lower_95': wilson_lower(int((healthy.probability < threshold).sum()), len(healthy)),
            'sensitivity': sensitivity,
            'sensitivity_wilson_lower_95': wilson_lower(int((stroke.probability >= threshold).sum()), len(stroke)),
            'balanced_accuracy': (specificity + sensitivity) / 2,
            'healthy_false_positives': int((healthy.probability >= threshold).sum()),
            'stroke_false_negatives': int((stroke.probability < threshold).sum()),
            'worst_source_specificity': float(source_specificity.min()),
            'worst_source_sensitivity': float(source_sensitivity.min()),
        })
    return pd.DataFrame(rows)


def main():
    x, m = load_development()
    people = participant_frame(m)
    split = StratifiedGroupKFold(n_splits=FOLDS, shuffle=True, random_state=SEED)
    oof = []
    for fold, (train_idx, valid_idx) in enumerate(split.split(people, people.y, people.participant_key), 1):
        out = train_fold(x, m, people.participant_key.iloc[train_idx], people.participant_key.iloc[valid_idx], fold)
        oof.append(out)
        print(f'completed fold {fold}/{FOLDS}: {len(out)} held-out participants', flush=True)
    pred = pd.concat(oof, ignore_index=True).rename(columns={'window_probability': 'probability'})
    if pred.participant_key.nunique() != len(people):
        raise RuntimeError('OOF coverage failure.')
    pred.to_csv(P / 'development_participant_oof_probabilities.csv', index=False)
    table = threshold_table(pred)
    table.to_csv(P / 'development_specificity_threshold_grid.csv', index=False)
    # A positive threshold must meet both pooled uncertainty control AND observed
    # worst-source specificity.  Pooling alone can hide a failing source.
    eligible_high = table[(table.specificity_wilson_lower_95 >= 0.90) &
                          (table.worst_source_specificity >= 0.90)]
    high = eligible_high.sort_values(['sensitivity', 'threshold'], ascending=[False, True]).iloc[0]
    # Auto-clearing a person as healthy requires a pooled AND worst-source sensitivity
    # constraint.  If the current data cannot support that claim, no auto-clear rule is
    # emitted: all sub-threshold cases are deferred for review/repeat walking.
    eligible_low = table[(table.sensitivity_wilson_lower_95 >= 0.90) &
                         (table.worst_source_sensitivity >= 0.90)]
    low = (eligible_low.sort_values('threshold', ascending=False).iloc[0]
           if len(eligible_low) else None)
    summary = pd.DataFrame([{
        'participants': len(pred), 'healthy_participants': int((pred.y == 0).sum()),
        'stroke_participants': int((pred.y == 1).sum()),
        'oof_auroc': roc_auc_score(pred.y, pred.probability),
        'oof_brier': brier_score_loss(pred.y, pred.probability),
        'threshold_0_5_balanced_accuracy': balanced_accuracy_score(pred.y, pred.probability >= .5),
        'positive_stroke_threshold': high.threshold,
        'positive_specificity': high.specificity,
        'positive_specificity_lcb95': high.specificity_wilson_lower_95,
        'positive_sensitivity': high.sensitivity,
        'healthy_auto_clear_threshold': (low.threshold if low is not None else np.nan),
        'healthy_auto_clear_stroke_sensitivity_lcb95': (low.sensitivity_wilson_lower_95 if low is not None else np.nan),
        'indeterminate_fraction': (float(((pred.probability > low.threshold) & (pred.probability < high.threshold)).mean())
                                   if low is not None else float((pred.probability < high.threshold).mean())),
        'uniform_auto_clear_supported': low is not None,
    }])
    summary.to_csv(P / 'development_specificity_abstention_summary.csv', index=False)
    print(summary.to_string(index=False)); print('device', DEVICE)


if __name__ == '__main__':
    main()
