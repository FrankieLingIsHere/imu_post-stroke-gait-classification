"""Participant-level multiple-instance learning for lower-back gait windows.

Only the three development sources are loaded. A participant is a bag of real
five-second windows and receives one binary loss. The module never loads frozen
external tensors.
"""

from __future__ import annotations

import copy
import gc
import hashlib
import json
import math
import random
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch import nn

from models.stroke_gait_inception import InceptionBlock
from src.models.evidence_gated_domain_generalization import (
    bootstrap_paired_delta,
    load_development_data,
    metric_row,
    participant_inner_split,
)


METHODS = ("mil_mean", "mil_attention")


@dataclass(frozen=True)
class MILConfig:
    seeds: tuple[int, ...] = (42, 137, 202, 314, 515)
    tuning_seed: int = 20260903
    checkpoints: tuple[int, ...] = (10, 20, 30, 40)
    validation_fraction: float = 0.20
    windows_per_bag: int = 16
    participants_per_source_class: int = 2
    learning_rate: float = 1e-3
    weight_decay: float = 1e-4
    attention_hidden: int = 32
    dropout: float = 0.25


class WindowEncoder(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.network = nn.Sequential(
            InceptionBlock(1),
            nn.MaxPool1d(2),
            InceptionBlock(64),
            nn.AdaptiveAvgPool1d(1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.network(x).flatten(1)


class ParticipantMIL(nn.Module):
    def __init__(self, pooling: str, config: MILConfig) -> None:
        super().__init__()
        if pooling not in {"mean", "attention"}:
            raise ValueError(pooling)
        self.pooling = pooling
        self.encoder = WindowEncoder()
        self.attention_v = nn.Linear(64, config.attention_hidden)
        self.attention_u = nn.Linear(64, config.attention_hidden)
        self.attention_w = nn.Linear(config.attention_hidden, 1)
        self.classifier = nn.Sequential(
            nn.Dropout(config.dropout),
            nn.Linear(64, 1),
        )

    def forward(self, bags: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        batch, instances, channels, samples = bags.shape
        encoded = self.encoder(bags.reshape(batch * instances, channels, samples))
        encoded = encoded.reshape(batch, instances, -1)
        if self.pooling == "mean":
            weights = torch.full(
                (batch, instances), 1.0 / instances, device=bags.device, dtype=encoded.dtype
            )
        else:
            attention = torch.tanh(self.attention_v(encoded)) * torch.sigmoid(
                self.attention_u(encoded)
            )
            weights = torch.softmax(self.attention_w(attention).squeeze(-1), dim=1)
        participant = torch.sum(encoded * weights.unsqueeze(-1), dim=1)
        return self.classifier(participant).squeeze(1), weights


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


class ParticipantBagBatcher:
    """Draw equal participant counts from every training source/class cell."""

    def __init__(
        self,
        meta: pd.DataFrame,
        mask: np.ndarray,
        config: MILConfig,
        seed: int,
    ) -> None:
        self.rng = np.random.default_rng(seed)
        self.config = config
        self.cells: dict[tuple[str, int], np.ndarray] = {}
        self.group_indices: dict[str, np.ndarray] = {}
        selected = meta.loc[mask]
        for group, frame in selected.groupby("group", sort=True):
            self.group_indices[group] = frame.index.to_numpy()
        for (source, label), frame in selected.groupby(["source", "y"], sort=True):
            groups = np.asarray(sorted(frame["group"].unique()))
            if len(groups) < config.participants_per_source_class:
                raise AssertionError(f"Insufficient participants in {source}/{label}")
            self.cells[(source, int(label))] = groups

    @property
    def batch_participants(self) -> int:
        return len(self.cells) * self.config.participants_per_source_class

    def draw(self) -> tuple[np.ndarray, np.ndarray]:
        bags: list[np.ndarray] = []
        labels: list[int] = []
        for (_, label), groups in sorted(self.cells.items()):
            selected_groups = self.rng.choice(
                groups, self.config.participants_per_source_class, replace=False
            )
            for group in selected_groups:
                candidates = self.group_indices[str(group)]
                bag = self.rng.choice(
                    candidates,
                    self.config.windows_per_bag,
                    replace=len(candidates) < self.config.windows_per_bag,
                )
                bags.append(bag)
                labels.append(label)
        order = self.rng.permutation(len(bags))
        return np.stack(bags)[order], np.asarray(labels, dtype="float32")[order]


def normalized_bags(
    x: np.ndarray,
    bag_indices: np.ndarray,
    mean: float,
    std: float,
) -> np.ndarray:
    values = (x[bag_indices, :, 0] - mean) / std
    return values[:, :, None, :].astype("float32", copy=False)


def evaluate_participants(
    model: ParticipantMIL,
    x: np.ndarray,
    meta: pd.DataFrame,
    indices: np.ndarray,
    mean: float,
    std: float,
    device: torch.device,
) -> pd.DataFrame:
    groups = meta.iloc[indices][["source", "group", "y"]].drop_duplicates()
    rows: list[dict] = []
    model.eval()
    with torch.inference_mode():
        for row in groups.itertuples(index=False):
            window_indices = np.flatnonzero(meta["group"].eq(row.group).to_numpy())
            window_indices = np.intersect1d(window_indices, indices, assume_unique=False)
            bag = normalized_bags(x, window_indices[None, :], mean, std)
            logits, weights = model(torch.from_numpy(bag).to(device))
            probability = float(torch.sigmoid(logits)[0].cpu())
            attention = weights[0].float().cpu().numpy()
            entropy = float(-(attention * np.log(attention + 1e-12)).sum())
            effective = float(np.exp(entropy))
            rows.append(
                {
                    "source": row.source,
                    "group": row.group,
                    "y": int(row.y),
                    "probability": probability,
                    "windows": int(len(window_indices)),
                    "max_attention": float(attention.max()),
                    "effective_windows": effective,
                }
            )
    return pd.DataFrame(rows)


def train_model(
    method: str,
    x: np.ndarray,
    meta: pd.DataFrame,
    train_mask: np.ndarray,
    epochs: int,
    config: MILConfig,
    seed: int,
    device: torch.device,
    validation_indices: np.ndarray | None = None,
) -> tuple[ParticipantMIL, float, float, list[dict]]:
    if method not in METHODS:
        raise ValueError(method)
    set_seed(seed)
    train_index = np.flatnonzero(train_mask)
    train_values = x[train_index, :, 0]
    mean = float(train_values.mean())
    std = float(max(train_values.std(), 1e-4))
    pooling = "attention" if method == "mil_attention" else "mean"
    model = ParticipantMIL(pooling, config).to(device)
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=config.learning_rate, weight_decay=config.weight_decay
    )
    scaler = torch.amp.GradScaler("cuda")
    batcher = ParticipantBagBatcher(meta, train_mask, config, seed + 1000)
    participants = meta.loc[train_mask, "group"].nunique()
    steps_per_epoch = max(1, math.ceil(participants / batcher.batch_participants))
    history: list[dict] = []
    for epoch in range(1, epochs + 1):
        model.train()
        losses = []
        for _ in range(steps_per_epoch):
            bag_indices, labels = batcher.draw()
            bags = torch.from_numpy(normalized_bags(x, bag_indices, mean, std)).to(device)
            target = torch.from_numpy(labels).to(device)
            optimizer.zero_grad(set_to_none=True)
            with torch.amp.autocast("cuda"):
                logits, _ = model(bags)
                loss = nn.functional.binary_cross_entropy_with_logits(logits, target)
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            scaler.step(optimizer)
            scaler.update()
            losses.append(float(loss.detach().cpu()))
        history.append({"epoch": epoch, "loss": float(np.mean(losses))})
        if validation_indices is not None and epoch in config.checkpoints:
            people = evaluate_participants(
                model, x, meta, validation_indices, mean, std, device
            )
            for source, frame in people.groupby("source", sort=True):
                history.append(
                    {
                        "epoch": epoch,
                        "validation": True,
                        "evaluation_source": source,
                        **metric_row(frame),
                    }
                )
    trained = copy.deepcopy(model).eval()
    del model, optimizer, scaler, batcher
    gc.collect()
    torch.cuda.empty_cache()
    return trained, mean, std, history


def tune_epochs(
    method: str,
    held_out_source: str,
    x: np.ndarray,
    meta: pd.DataFrame,
    config: MILConfig,
    device: torch.device,
) -> tuple[int, pd.DataFrame]:
    outer_train = meta["source"].ne(held_out_source).to_numpy()
    fit, validation = participant_inner_split(
        meta, outer_train, config.tuning_seed, config.validation_fraction
    )
    model, _, _, history = train_model(
        method,
        x,
        meta,
        fit,
        max(config.checkpoints),
        config,
        config.tuning_seed,
        device,
        np.flatnonzero(validation),
    )
    del model
    frame = pd.DataFrame(history)
    frame = frame.loc[frame.get("validation", False).fillna(False)]
    rows = []
    for epoch, epoch_frame in frame.groupby("epoch"):
        rows.append(
            {
                "held_out_source": held_out_source,
                "method": method,
                "epoch": int(epoch),
                "worst_balanced_accuracy": float(epoch_frame["balanced_accuracy"].min()),
                "worst_specificity": float(epoch_frame["specificity"].min()),
                "worst_sensitivity": float(epoch_frame["sensitivity"].min()),
                "worst_auroc": float(epoch_frame["auroc"].min()),
                "mean_brier": float(epoch_frame["brier"].mean()),
            }
        )
    tuning = pd.DataFrame(rows)
    best = tuning.sort_values(
        ["worst_balanced_accuracy", "worst_specificity", "worst_sensitivity", "mean_brier", "epoch"],
        ascending=[False, False, False, True, True],
    ).iloc[0]
    return int(best["epoch"]), tuning


def compare_candidates(metrics: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    summary = metrics.groupby(["method", "held_out_source"], as_index=False).agg(
        auroc=("auroc", "mean"),
        brier=("brier", "mean"),
        balanced_accuracy=("balanced_accuracy", "mean"),
        specificity=("specificity", "mean"),
        sensitivity=("sensitivity", "mean"),
        false_positives=("false_positives", "mean"),
        false_negatives=("false_negatives", "mean"),
    )
    baseline = metrics.loc[metrics["method"].eq("deep_ensemble")]
    decisions = {}
    for method in METHODS:
        candidate = metrics.loc[metrics["method"].eq(method)]
        merged = baseline.merge(
            candidate,
            on=["held_out_source", "evaluation_source", "seed"],
            suffixes=("_erm", "_candidate"),
            validate="one_to_one",
        )
        intervals = {}
        for metric in (
            "balanced_accuracy", "specificity", "sensitivity", "auroc", "brier",
            "false_positives", "false_negatives",
        ):
            mean, low, high = bootstrap_paired_delta(merged, metric)
            intervals[metric] = {"mean_delta": mean, "ci_low": low, "ci_high": high}
        b = summary.loc[summary["method"].eq("deep_ensemble")]
        c = summary.loc[summary["method"].eq(method)]
        worst = {
            "balanced_accuracy_delta": float(c["balanced_accuracy"].min() - b["balanced_accuracy"].min()),
            "specificity_delta": float(c["specificity"].min() - b["specificity"].min()),
            "sensitivity_delta": float(c["sensitivity"].min() - b["sensitivity"].min()),
            "auroc_delta": float(c["auroc"].min() - b["auroc"].min()),
            "mean_brier_delta": float(c["brier"].mean() - b["brier"].mean()),
        }
        noninferior = (
            worst["balanced_accuracy_delta"] >= -0.005
            and worst["specificity_delta"] >= -0.02
            and worst["sensitivity_delta"] >= -0.02
            and worst["auroc_delta"] >= -0.01
            and worst["mean_brier_delta"] <= 0.01
            and intervals["balanced_accuracy"]["ci_low"] >= -0.02
            and intervals["specificity"]["ci_low"] >= -0.05
            and intervals["sensitivity"]["ci_low"] >= -0.05
            and intervals["brier"]["ci_high"] <= 0.02
        )
        fp_fn_safe = (
            intervals["false_positives"]["mean_delta"] <= 0
            and intervals["false_negatives"]["mean_delta"] <= 0
        )
        baseline_error = float(
            (baseline["false_positives"] + baseline["false_negatives"]).mean()
        )
        candidate_error = float(
            (candidate["false_positives"] + candidate["false_negatives"]).mean()
        )
        reduction = (baseline_error - candidate_error) / baseline_error
        decisions[method] = {
            "accepted": bool(noninferior and fp_fn_safe and reduction >= 0.10),
            "noninferior": bool(noninferior),
            "fp_and_fn_nonincreasing": bool(fp_fn_safe),
            "mean_total_errors": candidate_error,
            "relative_total_error_reduction": float(reduction),
            "worst_source_deltas": worst,
            "paired_bootstrap": intervals,
        }
    accepted = [name for name, value in decisions.items() if value["accepted"]]
    selected = min(accepted, key=lambda name: decisions[name]["mean_total_errors"]) if accepted else "deep_ensemble"
    return summary, {
        "selected_method": selected,
        "candidate_decisions": decisions,
        "selection_scope": "development-only repeated leave-one-source-out",
        "frozen_cohorts_loaded": False,
    }


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run(project_root: Path, config: MILConfig = MILConfig()) -> dict:
    processed = project_root / "data" / "processed"
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if device.type != "cuda":
        raise RuntimeError("Participant MIL benchmark requires CUDA")
    x, meta = load_development_data(processed)
    print("GPU:", torch.cuda.get_device_name(0))
    print(meta.groupby(["source", "label"])["group"].nunique())

    tuning_rows = []
    selected_epochs: dict[tuple[str, str], int] = {}
    for held_out_source in sorted(meta["source"].unique()):
        for method in METHODS:
            epochs, tuning = tune_epochs(
                method, held_out_source, x, meta, config, device
            )
            selected_epochs[(held_out_source, method)] = epochs
            tuning_rows.append(tuning)
            print(f"Tuned {held_out_source} {method}: {epochs} epochs")
    tuning_frame = pd.concat(tuning_rows, ignore_index=True)

    metric_rows: list[dict] = []
    prediction_rows: list[pd.DataFrame] = []
    for held_out_source in sorted(meta["source"].unique()):
        train_mask = meta["source"].ne(held_out_source).to_numpy()
        test_index = np.flatnonzero(~train_mask)
        for seed in config.seeds:
            for method in METHODS:
                epochs = selected_epochs[(held_out_source, method)]
                model, mean, std, _ = train_model(
                    method, x, meta, train_mask, epochs, config, seed, device
                )
                people = evaluate_participants(
                    model, x, meta, test_index, mean, std, device
                )
                result = metric_row(people)
                metric_rows.append(
                    {
                        "method": method,
                        "held_out_source": held_out_source,
                        "evaluation_source": held_out_source,
                        "seed": seed,
                        "selected_epochs": epochs,
                        **result,
                    }
                )
                prediction_rows.append(
                    people.assign(
                        method=method,
                        held_out_source=held_out_source,
                        seed=seed,
                        selected_epochs=epochs,
                    )
                )
                print(
                    f"Complete {held_out_source} seed={seed} {method}: "
                    f"BA={result['balanced_accuracy']:.3f} "
                    f"FP={result['false_positives']} FN={result['false_negatives']}"
                )
                del model
                gc.collect()
                torch.cuda.empty_cache()

    metrics = pd.DataFrame(metric_rows)
    predictions = pd.concat(prediction_rows, ignore_index=True)
    deep_predictions = pd.read_csv(
        processed / "evidence_gated_lower_back_dg_participant_predictions.csv"
    )
    deep_predictions = deep_predictions.loc[
        deep_predictions["method"].eq("ensemble_all")
    ].copy()
    for (held_out_source, seed), frame in deep_predictions.groupby(
        ["held_out_source", "seed"], sort=True
    ):
        metric_rows.append(
            {
                "method": "deep_ensemble",
                "held_out_source": held_out_source,
                "evaluation_source": held_out_source,
                "seed": seed,
                "selected_epochs": -1,
                **metric_row(frame),
            }
        )
    metrics = pd.DataFrame(metric_rows)
    summary, decision = compare_candidates(metrics)
    decision["config"] = asdict(config)
    decision["input_sha256"] = {
        "primary": sha256(processed / "validated_acceleration_magnitude_windows_float32.npy"),
        "sint": sha256(processed / "sint_maartenskliniek_external_windows_float32.npy"),
        "deep_predictions": sha256(processed / "evidence_gated_lower_back_dg_participant_predictions.csv"),
    }
    tuning_frame.to_csv(processed / "participant_mil_tuning.csv", index=False)
    metrics.to_csv(processed / "participant_mil_metrics.csv", index=False)
    predictions.to_csv(processed / "participant_mil_predictions.csv", index=False)
    summary.to_csv(processed / "participant_mil_summary.csv", index=False)
    (processed / "participant_mil_decision.json").write_text(
        json.dumps(decision, indent=2), encoding="utf-8"
    )
    print(summary.round(4).to_string(index=False))
    print(json.dumps(decision, indent=2))
    return {
        "tuning": tuning_frame,
        "metrics": metrics,
        "predictions": predictions,
        "summary": summary,
        "decision": decision,
    }


if __name__ == "__main__":
    run(Path.cwd().resolve())
