"""Primary-task safety gate for binary hard-negative exposure.

Five participant-disjoint healthy/CVA folds compare fixed-epoch source/class
balanced binary training against the same binary model with non-CVA hard
negative exposure.  Hard-negative participants are training-only in this
gate; the held-out primary participants are never seen in any form. RevalExo
is not loaded.
"""
from pathlib import Path
import os
import numpy as np
import pandas as pd
import torch
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.metrics import roc_auc_score, brier_score_loss, balanced_accuracy_score
from benchmark_binary_hard_negative_exposure_loco import Net, load_hard_negatives, DEVICE

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / 'data' / 'processed'
SEED, EPOCHS, STEPS = 501, 12, 50
HARD_PER_COHORT = int(os.getenv('HARD_PER_COHORT', '8'))
MODES = tuple(os.getenv('MODES', 'baseline,exposure').split(','))


def train(x_primary, primary, train_mask, x_hard, mode, fold):
    torch.manual_seed(SEED + fold); rng = np.random.default_rng(SEED + fold)
    model = Net().to(DEVICE); opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    mean = x_primary[train_mask].reshape(-1, 3).mean(0); std = x_primary[train_mask].reshape(-1, 3).std(0).clip(1e-4)
    pools = [np.where(train_mask & primary.dataset_id.eq(source).to_numpy() & primary.y.eq(cls).to_numpy())[0]
             for source in sorted(primary.dataset_id.unique()) for cls in (0, 1)]
    # Sample each real pathology cohort equally, rather than allowing the large RIL
    # cohort to dominate the negative exposure signal.
    hard_metadata = HARD_METADATA
    exposure_pools = [np.where(hard_metadata.cohort.eq(c).to_numpy())[0] for c in sorted(hard_metadata.cohort.unique())]
    for _ in range(EPOCHS):
        model.train()
        for _ in range(STEPS):
            pi = np.concatenate([rng.choice(pool, 24, replace=len(pool) < 24) for pool in pools])
            if mode == 'exposure':
                hi = np.concatenate([rng.choice(pool, HARD_PER_COHORT, replace=len(pool) < HARD_PER_COHORT) for pool in exposure_pools])
                x = np.concatenate([x_primary[pi], x_hard[hi]])
                y = np.concatenate([primary.y.iloc[pi].to_numpy('float32'), np.zeros(len(hi), dtype='float32')])
            else:
                x, y = x_primary[pi], primary.y.iloc[pi].to_numpy('float32')
            xb = torch.from_numpy(((x - mean) / std).transpose(0, 2, 1).astype('float32')).to(DEVICE); yb = torch.from_numpy(y).to(DEVICE)
            opt.zero_grad(); loss = torch.nn.functional.binary_cross_entropy_with_logits(model(xb), yb); loss.backward(); opt.step()
    return model, mean, std


def predict(model, x, mean, std):
    model.eval()
    with torch.no_grad():
        return torch.sigmoid(model(torch.from_numpy(((x - mean) / std).transpose(0, 2, 1).astype('float32')).to(DEVICE))).cpu().numpy()


def main():
    global HARD_METADATA
    x_primary = np.concatenate([np.load(P / 'validated_acceleration_magnitude_windows_float32.npy'), np.load(P / 'sint_maartenskliniek_external_windows_float32.npy')])
    primary = pd.concat([pd.read_csv(P / 'validated_window_metadata.csv'), pd.read_csv(P / 'sint_maartenskliniek_external_window_metadata.csv')], ignore_index=True)
    keep = primary.label.isin(['healthy', 'stroke']).to_numpy(); x_primary, primary = x_primary[keep], primary.loc[keep].reset_index(drop=True)
    primary['y'] = (primary.label == 'stroke').astype(int)
    x_hard, HARD_METADATA = load_hard_negatives()
    people = primary[['participant_key', 'y']].drop_duplicates('participant_key').reset_index(drop=True)
    splitter = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=SEED)
    rows, oof = [], []
    for fold, (train_people, test_people) in enumerate(splitter.split(people, people.y, people.participant_key), 1):
        train_keys, test_keys = set(people.participant_key.iloc[train_people]), set(people.participant_key.iloc[test_people])
        train_mask = primary.participant_key.isin(train_keys).to_numpy(); test_mask = primary.participant_key.isin(test_keys).to_numpy()
        for mode in MODES:
            model, mean, std = train(x_primary, primary, train_mask, x_hard, mode, fold)
            probability = predict(model, x_primary[test_mask], mean, std)
            person = primary.loc[test_mask, ['participant_key', 'y']].copy(); person['probability'] = probability
            person = person.groupby(['participant_key', 'y'], as_index=False).probability.mean(); person['fold'], person['mode'] = fold, mode
            rows.append({'fold': fold, 'mode': mode, 'participants': len(person), 'auroc': roc_auc_score(person.y, person.probability),
                         'brier': brier_score_loss(person.y, person.probability), 'balanced_accuracy': balanced_accuracy_score(person.y, person.probability >= .5),
                         'healthy_false_positives': int(((person.y == 0) & (person.probability >= .5)).sum()),
                         'hard_windows_per_cohort_per_batch': HARD_PER_COHORT if mode == 'exposure' else 0})
            oof.append(person); print(rows[-1], flush=True)
    metrics = pd.DataFrame(rows); all_oof = pd.concat(oof, ignore_index=True)
    suffix = '' if HARD_PER_COHORT == 8 and MODES == ('baseline', 'exposure') else f'_h{HARD_PER_COHORT}'
    metrics.to_csv(P / f'binary_hard_negative_exposure_primary_oof_metrics{suffix}.csv', index=False)
    all_oof.to_csv(P / f'binary_hard_negative_exposure_primary_oof_predictions{suffix}.csv', index=False)
    print(metrics.groupby('mode').mean(numeric_only=True).round(4).to_string()); print('device', DEVICE)


if __name__ == '__main__': main()
