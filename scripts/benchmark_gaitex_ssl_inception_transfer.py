"""Architecture-matched GAITEX SSL transfer ablation (internal CV only).

GAITEX virtual windows have no stroke/healthy classifier labels in this script.
They pretrain an Inception encoder with contrastive augmentation, then every
encoder layer is fine-tuned on real Felius/Voisard/Sint labels.  Scratch and
pretrained arms share folds, seeds, architecture, weighting, and training
schedule. RevalExo is deliberately never loaded.
"""
from __future__ import annotations

import json
import random
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import balanced_accuracy_score, brier_score_loss, roc_auc_score
from sklearn.model_selection import StratifiedGroupKFold
from torch import nn
from torch.utils.data import DataLoader, TensorDataset, WeightedRandomSampler

from train_sint_sensitivity_inception import Net


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
VIRTUAL = ROOT / "data" / "interim" / "gaitex_2026" / "virtual_acceleration_sensitivity"
OUT = ROOT / "data" / "interim" / "gaitex_2026"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
SEED = 42


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def augment(x: torch.Tensor) -> torch.Tensor:
    scale = torch.empty((len(x), 1, 1), device=x.device).uniform_(0.9, 1.1)
    noise = torch.randn_like(x) * 0.02
    return x * scale + noise


class ContrastiveEncoder(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.backbone = Net().f
        self.project = nn.Sequential(nn.Flatten(), nn.Linear(64, 64), nn.GELU(), nn.Linear(64, 32))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return nn.functional.normalize(self.project(self.backbone(x)), dim=1)


def nt_xent(left: torch.Tensor, right: torch.Tensor, temperature: float = 0.2) -> torch.Tensor:
    both = torch.cat([left, right], dim=0)
    similarity = both @ both.T / temperature
    similarity.fill_diagonal_(-torch.inf)
    target = (torch.arange(len(both), device=both.device) + len(left)) % len(both)
    return nn.functional.cross_entropy(similarity, target)


def pretrain_encoder() -> dict[str, torch.Tensor]:
    virtual = np.load(VIRTUAL / "gaitex_virtual_proper_acceleration_magnitude_savgol_11.npy") / 9.80665
    mean = virtual.reshape(-1, 3).mean(axis=0)
    std = virtual.reshape(-1, 3).std(axis=0).clip(1e-4)
    tensor = torch.from_numpy(((virtual - mean) / std).transpose(0, 2, 1).astype(np.float32))
    loader = DataLoader(TensorDataset(tensor), batch_size=64, shuffle=True, drop_last=True)
    seed_everything(SEED)
    model = ContrastiveEncoder().to(DEVICE)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    history = []
    for epoch in range(40):
        model.train()
        losses = []
        for (batch,) in loader:
            batch = batch.to(DEVICE, non_blocking=True)
            loss = nt_xent(model(augment(batch)), model(augment(batch)))
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            losses.append(loss.item())
        history.append({"epoch": epoch + 1, "contrastive_loss": float(np.mean(losses))})
    pd.DataFrame(history).to_csv(OUT / "gaitex_ssl_inception_pretraining_history.csv", index=False)
    state = {key: value.detach().cpu() for key, value in model.backbone.state_dict().items()}
    torch.save({"backbone_state_dict": state, "virtual_source": "GAITEX 110-ms virtual proper acceleration", "device": str(DEVICE)}, OUT / "gaitex_ssl_inception_encoder.pt")
    return state


def train_fold(train_x: np.ndarray, train_meta: pd.DataFrame, val_x: np.ndarray, val_y: np.ndarray, pretrained: dict[str, torch.Tensor] | None) -> np.ndarray:
    mean = train_x.reshape(-1, 3).mean(axis=0)
    std = train_x.reshape(-1, 3).std(axis=0).clip(1e-4)
    x_train = torch.from_numpy(((train_x - mean) / std).transpose(0, 2, 1).astype(np.float32))
    x_val = torch.from_numpy(((val_x - mean) / std).transpose(0, 2, 1).astype(np.float32))
    y_train = torch.from_numpy(train_meta.y.to_numpy(np.float32))
    keys = train_meta[["source", "y"]].astype(str).agg("|".join, axis=1)
    counts = keys.value_counts()
    weights = torch.tensor(keys.map(lambda item: 1.0 / counts[item]).to_numpy(), dtype=torch.double)
    loader = DataLoader(TensorDataset(x_train, y_train), batch_size=128, sampler=WeightedRandomSampler(weights, len(weights), replacement=True))
    seed_everything(SEED)
    model = Net().to(DEVICE)
    if pretrained is not None:
        model.f.load_state_dict(pretrained)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    best_auc = -np.inf
    best_state: dict[str, torch.Tensor] | None = None
    for _ in range(12):
        model.train()
        for batch, label in loader:
            optimizer.zero_grad()
            loss = nn.functional.binary_cross_entropy_with_logits(model(batch.to(DEVICE, non_blocking=True)), label.to(DEVICE, non_blocking=True))
            loss.backward()
            optimizer.step()
        model.eval()
        with torch.no_grad():
            probabilities = torch.sigmoid(model(x_val.to(DEVICE, non_blocking=True))).cpu().numpy()
        window_auc = roc_auc_score(val_y, probabilities)
        if window_auc > best_auc:
            best_auc = window_auc
            best_state = {key: value.detach().cpu().clone() for key, value in model.state_dict().items()}
    model.load_state_dict(best_state)
    model.eval()
    with torch.no_grad():
        return torch.sigmoid(model(x_val.to(DEVICE, non_blocking=True))).cpu().numpy()


def main() -> None:
    if DEVICE.type != "cuda":
        raise RuntimeError("CUDA is required for this scheduled GPU ablation.")
    OUT.mkdir(parents=True, exist_ok=True)
    pretrained = pretrain_encoder()
    x = np.concatenate([
        np.load(PROCESSED / "validated_acceleration_magnitude_windows_float32.npy"),
        np.load(PROCESSED / "sint_maartenskliniek_external_windows_float32.npy"),
    ])
    meta = pd.concat([
        pd.read_csv(PROCESSED / "validated_window_metadata.csv"),
        pd.read_csv(PROCESSED / "sint_maartenskliniek_external_window_metadata.csv"),
    ], ignore_index=True)
    keep = meta.label.isin(["healthy", "stroke"]).to_numpy()
    x = x[keep]
    meta = meta.loc[keep].reset_index(drop=True)
    meta["source"] = meta.dataset_id
    meta["group"] = meta.participant_key.astype(str)
    meta["y"] = (meta.label == "stroke").astype(int)
    people = meta[["group", "y"]].drop_duplicates("group").reset_index(drop=True)
    splitter = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=SEED)
    rows = []
    for fold, (train_people, val_people) in enumerate(splitter.split(people, people.y, people.group)):
        training_groups = set(people.iloc[train_people].group)
        train_mask = meta.group.isin(training_groups).to_numpy()
        val_mask = ~train_mask
        for strategy, state in (("scratch", None), ("gaitex_ssl", pretrained)):
            probability = train_fold(x[train_mask], meta.loc[train_mask].reset_index(drop=True), x[val_mask], meta.loc[val_mask, "y"].to_numpy(), state)
            participant = meta.loc[val_mask, ["group", "y"]].copy()
            participant["probability"] = probability
            participant = participant.groupby(["group", "y"], as_index=False).probability.mean()
            rows.append({
                "fold": fold,
                "strategy": strategy,
                "participants": int(len(participant)),
                "auroc": float(roc_auc_score(participant.y, participant.probability)),
                "brier": float(brier_score_loss(participant.y, participant.probability)),
                "balanced_accuracy": float(balanced_accuracy_score(participant.y, participant.probability >= 0.5)),
            })
            print(rows[-1], flush=True)
    result = pd.DataFrame(rows)
    result.to_csv(OUT / "gaitex_ssl_inception_internal_transfer.csv", index=False)
    paired = result.pivot(index="fold", columns="strategy", values=["auroc", "brier", "balanced_accuracy"])
    summary = {
        "device": str(DEVICE),
        "pretraining": "GAITEX virtual signals only; no classifier labels",
        "fine_tuning": "real Felius/Voisard/Sint labels only; all layers trainable",
        "evaluation": "five-fold participant-disjoint internal comparison; RevalExo never loaded",
        "mean_metrics": result.groupby("strategy")[["auroc", "brier", "balanced_accuracy"]].mean().to_dict(),
        "paired_fold_differences_gaitex_ssl_minus_scratch": {
            metric: (paired[metric]["gaitex_ssl"] - paired[metric]["scratch"]).tolist()
            for metric in ("auroc", "brier", "balanced_accuracy")
        },
    }
    (OUT / "gaitex_ssl_inception_internal_transfer_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(result.groupby("strategy")[["auroc", "brier", "balanced_accuracy"]].agg(["mean", "std"]))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
