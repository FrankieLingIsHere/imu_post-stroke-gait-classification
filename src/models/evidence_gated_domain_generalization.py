"""Evidence-gated source-only domain-generalization benchmark.

This module is intentionally narrow: it compares the established ERM training
recipe with the released HAROOD CORAL objective and an explicitly labelled
ERM++-style optimization recipe. It never loads RevalExo or NONAN.
"""

from __future__ import annotations

import argparse
import copy
import gc
import hashlib
import json
import math
import random
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import balanced_accuracy_score, brier_score_loss, roc_auc_score
from torch import nn

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from models.stroke_gait_inception import InceptionBlock


METHODS = ("erm", "coral", "ermpp_style")
FIXED_ENSEMBLES = {
    "ensemble_erm_coral": ("erm", "coral"),
    "ensemble_erm_ermpp": ("erm", "ermpp_style"),
    "ensemble_all": ("erm", "coral", "ermpp_style"),
}


@dataclass(frozen=True)
class BenchmarkConfig:
    seeds: tuple[int, ...] = (42, 137, 202, 314, 515)
    tuning_seed: int = 20260903
    checkpoints: tuple[int, ...] = (4, 8, 12, 16)
    per_source_batch: int = 64
    learning_rate: float = 1e-3
    erm_weight_decay: float = 1e-4
    ermpp_weight_decay: float = 5e-4
    coral_weight: float = 1.0
    linear_steps: int = 500
    sma_start_step: int = 600
    validation_fraction: float = 0.20
    representation: str = "lower_back_acceleration"


class DomainNet(nn.Module):
    """The established Inception feature extractor with a channel-flexible input."""

    def __init__(self, channels: int) -> None:
        super().__init__()
        self.features = nn.Sequential(
            InceptionBlock(channels),
            nn.MaxPool1d(2),
            InceptionBlock(64),
            nn.AdaptiveAvgPool1d(1),
        )
        self.classifier = nn.Sequential(nn.Flatten(), nn.Dropout(0.30), nn.Linear(64, 1))

    def encode(self, x: torch.Tensor) -> torch.Tensor:
        return self.features(x).flatten(1)

    def classify_features(self, features: torch.Tensor) -> torch.Tensor:
        return self.classifier(features).squeeze(1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.classify_features(self.encode(x))


class SimpleMovingAverage:
    """Parameter/buffer average matching HAROOD's released ERM++ behavior."""

    def __init__(self, network: nn.Module, start_step: int) -> None:
        self.network = copy.deepcopy(network).eval()
        self.start_step = int(start_step)
        self.global_step = 0
        self.count = 0

    @torch.no_grad()
    def update(self, source: nn.Module) -> None:
        self.global_step += 1
        source_state = source.state_dict()
        average_state = self.network.state_dict()
        new_state = {}
        if self.global_step >= self.start_step:
            self.count += 1
            for name, old_value in average_state.items():
                current = source_state[name].detach()
                if "num_batches_tracked" in name:
                    new_state[name] = current.clone()
                else:
                    new_state[name] = (
                        old_value.detach().clone() * self.count + current.clone()
                    ) / (1.0 + self.count)
        else:
            new_state = {name: value.detach().clone() for name, value in source_state.items()}
        self.network.load_state_dict(new_state)

    def evaluation_model(self, source: nn.Module) -> nn.Module:
        return self.network if self.global_step >= self.start_step else source


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def load_development_data(processed: Path) -> tuple[np.ndarray, pd.DataFrame]:
    main_x = np.load(processed / "validated_acceleration_magnitude_windows_float32.npy")
    main_m = pd.read_csv(processed / "validated_window_metadata.csv")
    sint_x = np.load(processed / "sint_maartenskliniek_external_windows_float32.npy")
    sint_m = pd.read_csv(processed / "sint_maartenskliniek_external_window_metadata.csv")
    if main_x.shape[0] != len(main_m) or sint_x.shape[0] != len(sint_m):
        raise AssertionError("Tensor and metadata lengths do not match")
    x = np.concatenate([main_x, sint_x]).astype("float32", copy=False)
    meta = pd.concat([main_m, sint_m], ignore_index=True)
    keep = meta["label"].isin(["healthy", "stroke"]).to_numpy()
    x = x[keep]
    meta = meta.loc[keep].reset_index(drop=True)
    meta["y"] = meta["label"].eq("stroke").astype(int)
    meta["source"] = meta["dataset_id"].astype(str)
    meta["group"] = meta["source"] + "::" + meta["participant_key"].astype(str)
    if x.shape[1:] != (500, 3) or not np.isfinite(x).all():
        raise AssertionError(f"Unexpected development tensor contract: {x.shape}")
    if meta["source"].nunique() != 3:
        raise AssertionError("Expected exactly three development sources")
    return x, meta


def representation_channels(name: str) -> list[int]:
    mapping = {
        "lower_back_acceleration": [0],
        "three_channel_acceleration": [0, 1, 2],
    }
    if name not in mapping:
        raise ValueError(f"Unknown representation: {name}")
    return mapping[name]


def participant_inner_split(
    meta: pd.DataFrame, outer_train: np.ndarray, seed: int, fraction: float
) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    eligible = meta.loc[outer_train, ["source", "y", "group"]].drop_duplicates()
    validation_groups: set[str] = set()
    for (_, _), cell in eligible.groupby(["source", "y"], sort=True):
        groups = np.array(sorted(cell["group"].unique()))
        rng.shuffle(groups)
        count = max(1, int(round(len(groups) * fraction)))
        if count >= len(groups):
            count = len(groups) - 1
        validation_groups.update(groups[:count].tolist())
    validation = outer_train & meta["group"].isin(validation_groups).to_numpy()
    fit = outer_train & ~validation
    for frame_mask, name in ((fit, "fit"), (validation, "validation")):
        cells = meta.loc[frame_mask].groupby(["source", "y"]).size()
        if len(cells) != 4 or (cells <= 0).any():
            raise AssertionError(f"Incomplete source/class cells in {name}: {cells.to_dict()}")
    if set(meta.loc[fit, "group"]).intersection(set(meta.loc[validation, "group"])):
        raise AssertionError("Participant leakage in inner split")
    return fit, validation


class BalancedSourceBatcher:
    """Draw equal healthy/stroke counts from each source at every optimizer step."""

    def __init__(self, meta: pd.DataFrame, mask: np.ndarray, per_source_batch: int, seed: int) -> None:
        if per_source_batch % 2:
            raise ValueError("per_source_batch must be even")
        self.rng = np.random.default_rng(seed)
        self.sources = sorted(meta.loc[mask, "source"].unique())
        self.per_class = per_source_batch // 2
        self.cells = {}
        for source in self.sources:
            for label in (0, 1):
                idx = np.flatnonzero(mask & meta["source"].eq(source).to_numpy() & meta["y"].eq(label).to_numpy())
                if len(idx) == 0:
                    raise AssertionError(f"Empty training cell: {source}, {label}")
                self.cells[(source, label)] = idx

    def draw(self) -> tuple[np.ndarray, np.ndarray]:
        indices = []
        domains = []
        for domain_id, source in enumerate(self.sources):
            for label in (0, 1):
                chosen = self.rng.choice(self.cells[(source, label)], self.per_class, replace=True)
                indices.append(chosen)
                domains.extend([domain_id] * len(chosen))
        index = np.concatenate(indices)
        domain = np.asarray(domains, dtype=np.int64)
        order = self.rng.permutation(len(index))
        return index[order], domain[order]


def coral_loss(first: torch.Tensor, second: torch.Tensor) -> torch.Tensor:
    """HAROOD's released mean-plus-covariance CORAL objective."""
    mean_first = first.mean(0, keepdim=True)
    mean_second = second.mean(0, keepdim=True)
    centered_first = first - mean_first
    centered_second = second - mean_second
    covariance_first = centered_first.T @ centered_first / (len(first) - 1)
    covariance_second = centered_second.T @ centered_second / (len(second) - 1)
    return (mean_first - mean_second).pow(2).mean() + (
        covariance_first - covariance_second
    ).pow(2).mean()


def probabilities(
    model: nn.Module,
    x: np.ndarray,
    indices: np.ndarray,
    channels: list[int],
    mean: np.ndarray,
    std: np.ndarray,
    device: torch.device,
    batch_size: int = 512,
) -> np.ndarray:
    model.eval()
    outputs = []
    with torch.inference_mode():
        for start in range(0, len(indices), batch_size):
            part = indices[start : start + batch_size]
            z = ((x[part][:, :, channels] - mean) / std).transpose(0, 2, 1).astype("float32")
            outputs.append(torch.sigmoid(model(torch.from_numpy(z).to(device))).cpu().numpy())
    return np.concatenate(outputs)


def participant_predictions(
    meta: pd.DataFrame, indices: np.ndarray, window_probabilities: np.ndarray
) -> pd.DataFrame:
    frame = meta.iloc[indices][["source", "group", "y"]].copy()
    frame["probability"] = window_probabilities
    return frame.groupby(["source", "group", "y"], as_index=False)["probability"].mean()


def metric_row(frame: pd.DataFrame) -> dict[str, float | int]:
    y = frame["y"].to_numpy()
    probability = frame["probability"].to_numpy()
    prediction = probability >= 0.5
    healthy = y == 0
    stroke = y == 1
    return {
        "participants": int(len(frame)),
        "healthy": int(healthy.sum()),
        "stroke": int(stroke.sum()),
        "auroc": float(roc_auc_score(y, probability)),
        "brier": float(brier_score_loss(y, probability)),
        "balanced_accuracy": float(balanced_accuracy_score(y, prediction)),
        "specificity": float((~prediction[healthy]).mean()),
        "sensitivity": float(prediction[stroke].mean()),
        "false_positives": int(prediction[healthy].sum()),
        "false_negatives": int((~prediction[stroke]).sum()),
    }


def evaluate_by_source(
    model: nn.Module,
    x: np.ndarray,
    meta: pd.DataFrame,
    indices: np.ndarray,
    channels: list[int],
    mean: np.ndarray,
    std: np.ndarray,
    device: torch.device,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    window_probability = probabilities(model, x, indices, channels, mean, std, device)
    people = participant_predictions(meta, indices, window_probability)
    rows = []
    for source, frame in people.groupby("source", sort=True):
        rows.append({"evaluation_source": source, **metric_row(frame)})
    rows.append({"evaluation_source": "pooled", **metric_row(people)})
    return pd.DataFrame(rows), people


def train_model(
    method: str,
    x: np.ndarray,
    meta: pd.DataFrame,
    train_mask: np.ndarray,
    channels: list[int],
    epochs: int,
    config: BenchmarkConfig,
    seed: int,
    device: torch.device,
    evaluation_masks: dict[int, np.ndarray] | None = None,
) -> tuple[nn.Module, np.ndarray, np.ndarray, list[dict]]:
    if method not in METHODS:
        raise ValueError(method)
    set_seed(seed)
    train_values = x[train_mask][:, :, channels]
    mean = train_values.reshape(-1, len(channels)).mean(axis=0)
    std = train_values.reshape(-1, len(channels)).std(axis=0).clip(1e-4)
    model = DomainNet(len(channels)).to(device)
    if method == "ermpp_style":
        full_optimizer = torch.optim.Adam(
            model.parameters(), lr=config.learning_rate, weight_decay=config.ermpp_weight_decay, foreach=False
        )
        head_optimizer = torch.optim.Adam(
            model.classifier.parameters(), lr=config.learning_rate,
            weight_decay=config.ermpp_weight_decay, foreach=False
        )
        moving_average = SimpleMovingAverage(model, config.sma_start_step)
    else:
        full_optimizer = torch.optim.AdamW(
            model.parameters(), lr=config.learning_rate, weight_decay=config.erm_weight_decay
        )
        head_optimizer = None
        moving_average = None

    batcher = BalancedSourceBatcher(meta, train_mask, config.per_source_batch, seed + 1000)
    steps_per_epoch = max(1, math.ceil(int(train_mask.sum()) / (config.per_source_batch * len(batcher.sources))))
    history = []
    global_step = 0
    checkpoints = set(evaluation_masks or {})
    for epoch in range(1, epochs + 1):
        model.train()
        epoch_class = []
        epoch_coral = []
        for _ in range(steps_per_epoch):
            index, domain = batcher.draw()
            z = ((x[index][:, :, channels] - mean) / std).transpose(0, 2, 1).astype("float32")
            batch_x = torch.from_numpy(z).to(device)
            batch_y = torch.from_numpy(meta.iloc[index]["y"].to_numpy("float32")).to(device)
            batch_domain = torch.from_numpy(domain).to(device)
            features = model.encode(batch_x)
            logits = model.classify_features(features)
            class_loss = nn.functional.binary_cross_entropy_with_logits(logits, batch_y)
            alignment = torch.zeros((), device=device)
            if method == "coral":
                domain_values = sorted(batch_domain.unique().tolist())
                pair_count = 0
                for left_pos, left in enumerate(domain_values):
                    for right in domain_values[left_pos + 1 :]:
                        alignment = alignment + coral_loss(features[batch_domain == left], features[batch_domain == right])
                        pair_count += 1
                alignment = alignment / max(pair_count, 1)
            loss = class_loss + (config.coral_weight * alignment if method == "coral" else 0.0)
            if method == "ermpp_style" and global_step <= config.linear_steps:
                optimizer = head_optimizer
            else:
                optimizer = full_optimizer
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            optimizer.step()
            global_step += 1
            if moving_average is not None:
                moving_average.update(model)
            epoch_class.append(float(class_loss.detach().cpu()))
            epoch_coral.append(float(alignment.detach().cpu()))
        history.append(
            {
                "epoch": epoch,
                "class_loss": float(np.mean(epoch_class)),
                "coral_loss": float(np.mean(epoch_coral)),
                "global_step": global_step,
            }
        )
        if epoch in checkpoints:
            evaluation_model = moving_average.evaluation_model(model) if moving_average else model
            metrics, _ = evaluate_by_source(
                evaluation_model, x, meta, evaluation_masks[epoch], channels, mean, std, device
            )
            for row in metrics.to_dict("records"):
                history.append({"epoch": epoch, "validation": True, **row})
    evaluation_model = moving_average.evaluation_model(model) if moving_average else model
    evaluation_model = copy.deepcopy(evaluation_model).to(device).eval()
    del model, full_optimizer, head_optimizer, moving_average, batcher
    gc.collect()
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return evaluation_model, mean, std, history


def tune_epochs(
    method: str,
    held_out_source: str,
    x: np.ndarray,
    meta: pd.DataFrame,
    channels: list[int],
    config: BenchmarkConfig,
    device: torch.device,
) -> tuple[int, pd.DataFrame]:
    outer_train = meta["source"].ne(held_out_source).to_numpy()
    fit, validation = participant_inner_split(
        meta, outer_train, config.tuning_seed, config.validation_fraction
    )
    evaluation_masks = {epoch: np.flatnonzero(validation) for epoch in config.checkpoints}
    model, _, _, history = train_model(
        method, x, meta, fit, channels, max(config.checkpoints), config,
        config.tuning_seed, device, evaluation_masks
    )
    del model
    records = []
    history_frame = pd.DataFrame(history)
    validation_history = history_frame.loc[history_frame.get("validation", False).fillna(False)].copy()
    for epoch, frame in validation_history.loc[
        validation_history["evaluation_source"].ne("pooled")
    ].groupby("epoch"):
        records.append(
            {
                "held_out_source": held_out_source,
                "method": method,
                "epoch": int(epoch),
                "worst_balanced_accuracy": float(frame["balanced_accuracy"].min()),
                "worst_specificity": float(frame["specificity"].min()),
                "worst_sensitivity": float(frame["sensitivity"].min()),
                "worst_auroc": float(frame["auroc"].min()),
                "mean_brier": float(frame["brier"].mean()),
            }
        )
    tuning = pd.DataFrame(records)
    best = tuning.sort_values(
        ["worst_balanced_accuracy", "worst_specificity", "mean_brier", "epoch"],
        ascending=[False, False, True, True],
    ).iloc[0]
    return int(best["epoch"]), tuning


def bootstrap_paired_delta(
    merged: pd.DataFrame, metric: str, seed: int = 20260903, draws: int = 10000
) -> tuple[float, float, float]:
    delta = merged[f"{metric}_candidate"].to_numpy() - merged[f"{metric}_erm"].to_numpy()
    rng = np.random.default_rng(seed)
    samples = rng.choice(delta, size=(draws, len(delta)), replace=True).mean(axis=1)
    return float(delta.mean()), float(np.quantile(samples, 0.025)), float(np.quantile(samples, 0.975))


def add_fixed_ensembles(
    metrics: pd.DataFrame, predictions: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Add deterministic equal-weight ensembles from matched participant predictions."""
    keys = ["representation", "held_out_source", "seed", "source", "group", "y"]
    wide = predictions.pivot(index=keys, columns="method", values="probability").reset_index()
    if any(method not in wide for method in METHODS):
        raise AssertionError("A base method is missing from the ensemble prediction matrix")
    ensemble_metrics = []
    ensemble_predictions = []
    for name, members in FIXED_ENSEMBLES.items():
        frame = wide[keys].copy()
        frame["probability"] = wide[list(members)].mean(axis=1)
        frame["method"] = name
        frame["selected_epochs"] = -1
        ensemble_predictions.append(frame)
        for (representation, held_out, seed), outer in frame.groupby(
            ["representation", "held_out_source", "seed"], sort=True
        ):
            for source, source_frame in outer.groupby("source", sort=True):
                ensemble_metrics.append(
                    {
                        "representation": representation,
                        "held_out_source": held_out,
                        "seed": seed,
                        "method": name,
                        "selected_epochs": -1,
                        "evaluation_source": source,
                        **metric_row(source_frame),
                    }
                )
            ensemble_metrics.append(
                {
                    "representation": representation,
                    "held_out_source": held_out,
                    "seed": seed,
                    "method": name,
                    "selected_epochs": -1,
                    "evaluation_source": "pooled",
                    **metric_row(outer),
                }
            )
    return (
        pd.concat([metrics, pd.DataFrame(ensemble_metrics)], ignore_index=True),
        pd.concat([predictions, *ensemble_predictions], ignore_index=True),
    )


def decide(metrics: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    source_only = metrics.loc[metrics["evaluation_source"].ne("pooled")].copy()
    summary = source_only.groupby(["method", "held_out_source"], as_index=False).agg(
        auroc=("auroc", "mean"),
        brier=("brier", "mean"),
        balanced_accuracy=("balanced_accuracy", "mean"),
        specificity=("specificity", "mean"),
        sensitivity=("sensitivity", "mean"),
        false_positives=("false_positives", "mean"),
    )
    erm = source_only.loc[source_only["method"].eq("erm")]
    decisions = {}
    candidate_methods = sorted(set(source_only["method"]) - {"erm"})
    for method in candidate_methods:
        candidate = source_only.loc[source_only["method"].eq(method)]
        merged = erm.merge(
            candidate, on=["held_out_source", "seed", "evaluation_source"],
            suffixes=("_erm", "_candidate"), validate="one_to_one"
        )
        intervals = {}
        for metric in ("balanced_accuracy", "specificity", "sensitivity", "auroc", "brier"):
            mean, low, high = bootstrap_paired_delta(merged, metric)
            intervals[metric] = {"mean_delta": mean, "ci_low": low, "ci_high": high}
        erm_source = summary.loc[summary["method"].eq("erm")]
        candidate_source = summary.loc[summary["method"].eq(method)]
        worst = {
            "balanced_accuracy_delta": float(candidate_source["balanced_accuracy"].min() - erm_source["balanced_accuracy"].min()),
            "specificity_delta": float(candidate_source["specificity"].min() - erm_source["specificity"].min()),
            "sensitivity_delta": float(candidate_source["sensitivity"].min() - erm_source["sensitivity"].min()),
            "auroc_delta": float(candidate_source["auroc"].min() - erm_source["auroc"].min()),
            "mean_brier_delta": float(candidate_source["brier"].mean() - erm_source["brier"].mean()),
        }
        noninferior = (
            worst["balanced_accuracy_delta"] >= -0.005
            and worst["specificity_delta"] >= -0.02
            and worst["auroc_delta"] >= -0.01
            and worst["mean_brier_delta"] <= 0.01
            and intervals["balanced_accuracy"]["ci_low"] >= -0.02
            and intervals["specificity"]["ci_low"] >= -0.05
            and intervals["brier"]["ci_high"] <= 0.02
        )
        material_gain = (
            intervals["balanced_accuracy"]["mean_delta"] >= 0.005
            or intervals["specificity"]["mean_delta"] >= 0.02
            or intervals["brier"]["mean_delta"] <= -0.005
        )
        decisions[method] = {
            "accepted": bool(noninferior and material_gain),
            "noninferior": bool(noninferior),
            "material_gain": bool(material_gain),
            "worst_source_deltas": worst,
            "paired_bootstrap": intervals,
        }
    accepted = [method for method, result in decisions.items() if result["accepted"]]
    if accepted:
        accepted.sort(
            key=lambda method: (
                decisions[method]["paired_bootstrap"]["balanced_accuracy"]["mean_delta"]
                - decisions[method]["paired_bootstrap"]["brier"]["mean_delta"]
            ), reverse=True
        )
        selected = accepted[0]
    else:
        selected = "erm"
    decision = {
        "selected_method": selected,
        "candidate_decisions": decisions,
        "selection_scope": "development-only repeated leave-one-source-out",
        "frozen_cohorts_loaded": False,
    }
    return summary, decision


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run(project_root: Path, config: BenchmarkConfig) -> dict:
    processed = project_root / "data" / "processed"
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if device.type != "cuda":
        raise RuntimeError("This benchmark is intentionally GPU-only")
    x, meta = load_development_data(processed)
    channels = representation_channels(config.representation)
    print(f"Device: {device} | {torch.cuda.get_device_name(0)}")
    print(f"Representation: {config.representation} | channels={channels}")
    print(meta.groupby(["source", "label"])["group"].nunique().rename("participants"))

    tuning_rows = []
    selected_epochs = {}
    for held_out_source in sorted(meta["source"].unique()):
        for method in METHODS:
            epoch, tuning = tune_epochs(method, held_out_source, x, meta, channels, config, device)
            tuning_rows.append(tuning)
            selected_epochs[(held_out_source, method)] = epoch
            print(f"Tuned {held_out_source} {method}: {epoch} epochs")
    tuning_frame = pd.concat(tuning_rows, ignore_index=True)
    tuning_frame["representation"] = config.representation

    metric_rows = []
    prediction_rows = []
    for held_out_source in sorted(meta["source"].unique()):
        train_mask = meta["source"].ne(held_out_source).to_numpy()
        test_index = np.flatnonzero(~train_mask)
        if set(meta.loc[train_mask, "group"]).intersection(set(meta.iloc[test_index]["group"])):
            raise AssertionError("Outer participant leakage")
        for seed in config.seeds:
            for method in METHODS:
                epochs = selected_epochs[(held_out_source, method)]
                model, mean, std, _ = train_model(
                    method, x, meta, train_mask, channels, epochs, config, seed, device
                )
                source_metrics, people = evaluate_by_source(
                    model, x, meta, test_index, channels, mean, std, device
                )
                for row in source_metrics.to_dict("records"):
                    metric_rows.append(
                        {
                            "representation": config.representation,
                            "held_out_source": held_out_source,
                            "seed": seed,
                            "method": method,
                            "selected_epochs": epochs,
                            **row,
                        }
                    )
                people = people.assign(
                    representation=config.representation,
                    held_out_source=held_out_source,
                    seed=seed,
                    method=method,
                    selected_epochs=epochs,
                )
                prediction_rows.append(people)
                print(f"Complete {held_out_source} seed={seed} method={method}")
                del model
                gc.collect()
                torch.cuda.empty_cache()

    metrics = pd.DataFrame(metric_rows)
    predictions = pd.concat(prediction_rows, ignore_index=True)
    metrics, predictions = add_fixed_ensembles(metrics, predictions)
    summary, decision = decide(metrics)
    prefix = {
        "lower_back_acceleration": "evidence_gated_lower_back_dg",
        "three_channel_acceleration": "evidence_gated_three_channel_dg",
    }[config.representation]
    tuning_path = processed / f"{prefix}_tuning.csv"
    metrics_path = processed / f"{prefix}_metrics.csv"
    prediction_path = processed / f"{prefix}_participant_predictions.csv"
    summary_path = processed / f"{prefix}_summary.csv"
    decision_path = processed / f"{prefix}_decision.json"
    tuning_frame.to_csv(tuning_path, index=False)
    metrics.to_csv(metrics_path, index=False)
    predictions.to_csv(prediction_path, index=False)
    summary.to_csv(summary_path, index=False)
    decision.update(
        {
            "config": asdict(config),
            "development_participants": int(meta["group"].nunique()),
            "development_windows": int(len(meta)),
            "sources": sorted(meta["source"].unique().tolist()),
            "input_sha256": {
                "primary": sha256(processed / "validated_acceleration_magnitude_windows_float32.npy"),
                "sint": sha256(processed / "sint_maartenskliniek_external_windows_float32.npy"),
            },
        }
    )
    decision_path.write_text(json.dumps(decision, indent=2), encoding="utf-8")
    print(summary.round(4).to_string(index=False))
    print(json.dumps(decision, indent=2))
    return {
        "tuning": tuning_frame,
        "metrics": metrics,
        "predictions": predictions,
        "summary": summary,
        "decision": decision,
    }


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--representation",
        choices=("lower_back_acceleration", "three_channel_acceleration"),
        default="lower_back_acceleration",
    )
    parser.add_argument("--seeds", type=int, nargs="*", default=list(BenchmarkConfig().seeds))
    return parser.parse_args(argv)


if __name__ == "__main__":
    args = parse_args()
    configuration = BenchmarkConfig(seeds=tuple(args.seeds), representation=args.representation)
    run(args.project_root.resolve(), configuration)
