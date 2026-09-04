"""Canonical corrective benchmark for the primary lower-back gait model.

This module is deliberately bounded. It compares the unchanged notebook-29
incumbent with canonical-mechanics InceptionTime, canonical 10k MiniROCKET, and
three fixed equal-probability fusions. Only the Felius, Voisard, and Sint
development sources are loaded. RevalExo and NONAN are never loaded.
"""

from __future__ import annotations

import copy
import gc
import hashlib
import json
import math
import os
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.linear_model import LogisticRegression, RidgeClassifier, RidgeClassifierCV
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.preprocessing import StandardScaler
from sktime.transformations.panel.rocket import MiniRocket
from torch import nn

from src.models.evidence_gated_domain_generalization import (
    BalancedSourceBatcher,
    load_development_data,
    metric_row,
    participant_inner_split,
    participant_predictions,
    set_seed,
)
from src.models.lower_back_minirocket_rescue import (
    balanced_bias_indices,
    participant_source_class_weights,
)


MODULE_VERSION = "2026-09-03-v1"
INCEPTIONTIME_COMMIT = "952d115e83fb3a66d75c5858c702f8dd5eeb18b7"
MINIROCKET_COMMIT = "0b1c245d9c9dbc50886f28bc7b32d5d45b5663d6"
INCUMBENT_METHOD = "incumbent_notebook29"
BASE_CANDIDATES = ("canonical_inceptiontime", "canonical_minirocket")
FUSIONS = {
    "fusion_incumbent_inceptiontime": (INCUMBENT_METHOD, "canonical_inceptiontime"),
    "fusion_incumbent_minirocket": (INCUMBENT_METHOD, "canonical_minirocket"),
    "fusion_all_three": (INCUMBENT_METHOD, "canonical_inceptiontime", "canonical_minirocket"),
}


@dataclass(frozen=True)
class CorrectiveConfig:
    seeds: tuple[int, ...] = (42, 137, 202, 314, 515)
    tuning_seed: int = 20260903
    inception_checkpoints: tuple[int, ...] = (8, 16, 24, 32)
    per_source_batch: int = 64
    learning_rate: float = 1e-3
    weight_decay: float = 0.0
    validation_fraction: float = 0.20
    minirocket_kernels: int = 10_000
    minirocket_max_dilations: int = 32
    minirocket_bias_windows_per_source_class: int = 2_000
    minirocket_jobs: int = min(16, os.cpu_count() or 1)
    calibration_folds: int = 3
    ridge_alphas: tuple[float, ...] = tuple(np.logspace(-3, 3, 10).tolist())
    bootstrap_draws: int = 20_000


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _same_pad(x: torch.Tensor, kernel_size: int) -> torch.Tensor:
    total = kernel_size - 1
    left = total // 2
    return nn.functional.pad(x, (left, total - left))


class SameConv1d(nn.Module):
    """Stride-one Keras-style SAME convolution, including even kernels."""

    def __init__(self, in_channels: int, out_channels: int, kernel_size: int) -> None:
        super().__init__()
        self.kernel_size = int(kernel_size)
        self.conv = nn.Conv1d(in_channels, out_channels, self.kernel_size, bias=False)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.conv(_same_pad(x, self.kernel_size))


class CanonicalInceptionModule(nn.Module):
    """PyTorch translation of the audited official InceptionTime module."""

    def __init__(self, in_channels: int, filters: int = 32, bottleneck: int = 32) -> None:
        super().__init__()
        self.use_bottleneck = in_channels > 1
        branch_input = bottleneck if self.use_bottleneck else in_channels
        self.bottleneck = (
            nn.Conv1d(in_channels, bottleneck, 1, bias=False)
            if self.use_bottleneck
            else nn.Identity()
        )
        self.branches = nn.ModuleList(
            [SameConv1d(branch_input, filters, kernel) for kernel in (40, 20, 10)]
        )
        self.pool_projection = nn.Conv1d(in_channels, filters, 1, bias=False)
        self.batch_norm = nn.BatchNorm1d(filters * 4)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        bottleneck = self.bottleneck(x)
        outputs = [branch(bottleneck) for branch in self.branches]
        outputs.append(self.pool_projection(nn.functional.max_pool1d(x, 3, stride=1, padding=1)))
        return torch.relu(self.batch_norm(torch.cat(outputs, dim=1)))


class CanonicalInceptionTime(nn.Module):
    """Six modules, residual shortcut every third module, GAP, binary head."""

    def __init__(self, in_channels: int = 1) -> None:
        super().__init__()
        modules = []
        channels = in_channels
        for _ in range(6):
            modules.append(CanonicalInceptionModule(channels))
            channels = 128
        self.modules_list = nn.ModuleList(modules)
        self.shortcuts = nn.ModuleList(
            [
                nn.Sequential(nn.Conv1d(in_channels, 128, 1, bias=False), nn.BatchNorm1d(128)),
                nn.Sequential(nn.Conv1d(128, 128, 1, bias=False), nn.BatchNorm1d(128)),
            ]
        )
        self.classifier = nn.Linear(128, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        residual = x
        shortcut_index = 0
        for depth, module in enumerate(self.modules_list):
            x = module(x)
            if depth % 3 == 2:
                x = torch.relu(x + self.shortcuts[shortcut_index](residual))
                residual = x
                shortcut_index += 1
        return self.classifier(x.mean(dim=-1)).squeeze(1)


def _normalized_batch(
    x: np.ndarray, indices: np.ndarray, mean: float, std: float
) -> torch.Tensor:
    values = ((x[indices, :, 0] - mean) / std).astype("float32", copy=False)
    return torch.from_numpy(np.ascontiguousarray(values[:, None, :]))


@torch.inference_mode()
def _inception_probabilities(
    model: nn.Module,
    x: np.ndarray,
    indices: np.ndarray,
    mean: float,
    std: float,
    device: torch.device,
    batch_size: int = 512,
) -> np.ndarray:
    model.eval()
    values = []
    for start in range(0, len(indices), batch_size):
        batch = _normalized_batch(x, indices[start : start + batch_size], mean, std).to(device)
        with torch.autocast(device_type="cuda", dtype=torch.float16):
            values.append(torch.sigmoid(model(batch)).float().cpu().numpy())
    return np.concatenate(values)


def train_inceptiontime(
    x: np.ndarray,
    meta: pd.DataFrame,
    train_mask: np.ndarray,
    epochs: int,
    config: CorrectiveConfig,
    seed: int,
    device: torch.device,
    evaluation_masks: dict[int, np.ndarray] | None = None,
) -> tuple[nn.Module, float, float, list[dict]]:
    set_seed(seed)
    train_values = x[train_mask, :, 0]
    mean = float(train_values.mean())
    std = float(max(train_values.std(), 1e-4))
    model = CanonicalInceptionTime().to(device)
    optimizer = torch.optim.Adam(
        model.parameters(), lr=config.learning_rate, weight_decay=config.weight_decay
    )
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="min", factor=0.5, patience=6, min_lr=1e-4
    )
    scaler = torch.amp.GradScaler("cuda")
    batcher = BalancedSourceBatcher(meta, train_mask, config.per_source_batch, seed + 1000)
    steps_per_epoch = max(
        1, math.ceil(int(train_mask.sum()) / (config.per_source_batch * len(batcher.sources)))
    )
    history: list[dict] = []
    checkpoints = set(evaluation_masks or {})
    for epoch in range(1, epochs + 1):
        model.train()
        losses = []
        for _ in range(steps_per_epoch):
            index, _ = batcher.draw()
            batch_x = _normalized_batch(x, index, mean, std).to(device)
            batch_y = torch.from_numpy(meta.iloc[index]["y"].to_numpy("float32")).to(device)
            optimizer.zero_grad(set_to_none=True)
            with torch.autocast(device_type="cuda", dtype=torch.float16):
                loss = nn.functional.binary_cross_entropy_with_logits(model(batch_x), batch_y)
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            losses.append(float(loss.detach().cpu()))
        mean_loss = float(np.mean(losses))
        scheduler.step(mean_loss)
        history.append(
            {"epoch": epoch, "training_loss": mean_loss, "learning_rate": optimizer.param_groups[0]["lr"]}
        )
        if epoch in checkpoints:
            validation_index = evaluation_masks[epoch]
            probability = _inception_probabilities(
                model, x, validation_index, mean, std, device
            )
            people = participant_predictions(meta, validation_index, probability)
            for source, frame in people.groupby("source", sort=True):
                history.append(
                    {"epoch": epoch, "validation": True, "evaluation_source": source, **metric_row(frame)}
                )
    result = copy.deepcopy(model).eval()
    del model, optimizer, scheduler, scaler, batcher
    gc.collect()
    torch.cuda.empty_cache()
    return result, mean, std, history


def tune_inceptiontime(
    held_out_source: str,
    x: np.ndarray,
    meta: pd.DataFrame,
    config: CorrectiveConfig,
    device: torch.device,
) -> tuple[int, pd.DataFrame]:
    outer_train = meta["source"].ne(held_out_source).to_numpy()
    fit, validation = participant_inner_split(
        meta, outer_train, config.tuning_seed, config.validation_fraction
    )
    evaluation_masks = {
        epoch: np.flatnonzero(validation) for epoch in config.inception_checkpoints
    }
    model, _, _, history = train_inceptiontime(
        x,
        meta,
        fit,
        max(config.inception_checkpoints),
        config,
        config.tuning_seed,
        device,
        evaluation_masks,
    )
    del model
    frame = pd.DataFrame(history)
    frame = frame.loc[frame.get("validation", False).fillna(False)].copy()
    rows = []
    for epoch, epoch_frame in frame.groupby("epoch", sort=True):
        rows.append(
            {
                "held_out_source": held_out_source,
                "method": "canonical_inceptiontime",
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
        ["worst_balanced_accuracy", "worst_specificity", "mean_brier", "epoch"],
        ascending=[False, False, True, True],
    ).iloc[0]
    return int(best["epoch"]), tuning


def run_inceptiontime(
    project_root: Path,
    x: np.ndarray,
    meta: pd.DataFrame,
    config: CorrectiveConfig,
    device: torch.device,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    processed = project_root / "data" / "processed"
    prediction_path = processed / "canonical_inceptiontime_participant_predictions.csv"
    tuning_path = processed / "canonical_inceptiontime_tuning.csv"
    if prediction_path.exists():
        cached = pd.read_csv(prediction_path)
        complete = len(cached) == len(config.seeds) * meta["group"].nunique()
        if complete and set(cached["seed"].unique()) == set(config.seeds):
            print("Using complete cached canonical InceptionTime predictions")
            return cached, pd.read_csv(tuning_path)

    tuning_rows = []
    selected_epochs = {}
    for source in sorted(meta["source"].unique()):
        epoch, tuning = tune_inceptiontime(source, x, meta, config, device)
        selected_epochs[source] = epoch
        tuning_rows.append(tuning)
        print(f"InceptionTime tuned: held_out={source} epochs={epoch}")
    tuning_frame = pd.concat(tuning_rows, ignore_index=True)
    tuning_frame.to_csv(tuning_path, index=False)

    predictions = []
    for source in sorted(meta["source"].unique()):
        train_mask = meta["source"].ne(source).to_numpy()
        test_index = np.flatnonzero(~train_mask)
        for seed in config.seeds:
            model, mean, std, _ = train_inceptiontime(
                x, meta, train_mask, selected_epochs[source], config, seed, device
            )
            probability = _inception_probabilities(model, x, test_index, mean, std, device)
            people = participant_predictions(meta, test_index, probability).assign(
                method="canonical_inceptiontime",
                held_out_source=source,
                seed=seed,
                selected_epochs=selected_epochs[source],
                module_version=MODULE_VERSION,
            )
            predictions.append(people)
            partial = pd.concat(predictions, ignore_index=True)
            partial.to_csv(prediction_path, index=False)
            result = metric_row(people)
            print(
                f"InceptionTime complete: held_out={source} seed={seed} "
                f"BA={result['balanced_accuracy']:.3f} FP={result['false_positives']} "
                f"FN={result['false_negatives']}"
            )
            del model
            gc.collect()
            torch.cuda.empty_cache()
    return pd.concat(predictions, ignore_index=True), tuning_frame


def _panel(x: np.ndarray, indices: np.ndarray, mean: float, std: float) -> np.ndarray:
    values = ((x[indices, :, 0] - mean) / std).astype("float32", copy=False)
    return np.ascontiguousarray(values[:, None, :])


def _participant_calibration_frame(
    meta: pd.DataFrame, indices: np.ndarray, scores: np.ndarray
) -> pd.DataFrame:
    frame = meta.iloc[indices][["source", "group", "y"]].copy()
    frame["score"] = scores
    return frame.groupby(["source", "group", "y"], as_index=False)["score"].mean()


def _participant_source_class_weights(frame: pd.DataFrame) -> np.ndarray:
    counts = frame.groupby(["source", "y"])["group"].transform("count").to_numpy()
    weights = 1.0 / counts
    return weights / weights.mean()


def run_minirocket(
    project_root: Path,
    x: np.ndarray,
    meta: pd.DataFrame,
    config: CorrectiveConfig,
) -> pd.DataFrame:
    processed = project_root / "data" / "processed"
    prediction_path = processed / "canonical_minirocket_participant_predictions.csv"
    if prediction_path.exists():
        cached = pd.read_csv(prediction_path)
        complete = len(cached) == len(config.seeds) * meta["group"].nunique()
        if complete and set(cached["seed"].unique()) == set(config.seeds):
            print("Using complete cached canonical MiniROCKET predictions")
            return cached

    predictions = []
    diagnostics = []
    for source in sorted(meta["source"].unique()):
        train_mask = meta["source"].ne(source).to_numpy()
        train_index = np.flatnonzero(train_mask)
        test_index = np.flatnonzero(~train_mask)
        train_groups = set(meta.iloc[train_index]["group"])
        if train_groups.intersection(meta.iloc[test_index]["group"]):
            raise AssertionError("Participant leakage in MiniROCKET outer split")
        mean = float(x[train_index, :, 0].mean())
        std = float(max(x[train_index, :, 0].std(), 1e-4))
        weights = participant_source_class_weights(meta, train_index)
        for seed in config.seeds:
            bias_index = balanced_bias_indices(
                meta,
                train_mask,
                seed,
                per_cell=config.minirocket_bias_windows_per_source_class,
            )
            rocket = MiniRocket(
                num_kernels=config.minirocket_kernels,
                max_dilations_per_kernel=config.minirocket_max_dilations,
                n_jobs=config.minirocket_jobs,
                random_state=seed,
            )
            rocket.fit(_panel(x, bias_index, mean, std))
            train_features = np.asarray(
                rocket.transform(_panel(x, train_index, mean, std)), dtype="float32"
            )
            scaler = StandardScaler(with_mean=False, copy=False)
            train_features = scaler.fit_transform(train_features).astype("float32", copy=False)
            y_train = meta.iloc[train_index]["y"].to_numpy()
            ridge_cv = RidgeClassifierCV(alphas=np.asarray(config.ridge_alphas))
            ridge_cv.fit(train_features, y_train, sample_weight=weights)
            alpha = float(ridge_cv.alpha_)

            splitter = StratifiedGroupKFold(
                n_splits=config.calibration_folds, shuffle=True, random_state=seed
            )
            oof_score = np.full(len(train_index), np.nan, dtype="float64")
            groups = meta.iloc[train_index]["group"].to_numpy()
            for inner_fit, inner_calibration in splitter.split(train_features, y_train, groups):
                ridge = RidgeClassifier(alpha=alpha, solver="lsqr")
                ridge.fit(
                    train_features[inner_fit],
                    y_train[inner_fit],
                    sample_weight=weights[inner_fit],
                )
                oof_score[inner_calibration] = ridge.decision_function(
                    train_features[inner_calibration]
                )
            if not np.isfinite(oof_score).all():
                raise AssertionError("Incomplete participant-safe calibration predictions")
            calibration = _participant_calibration_frame(meta, train_index, oof_score)
            platt = LogisticRegression(C=1e6, solver="lbfgs", max_iter=2000)
            platt.fit(
                calibration[["score"]],
                calibration["y"],
                sample_weight=_participant_source_class_weights(calibration),
            )

            final_ridge = RidgeClassifier(alpha=alpha, solver="lsqr")
            final_ridge.fit(train_features, y_train, sample_weight=weights)
            del train_features, ridge_cv
            test_features = np.asarray(
                rocket.transform(_panel(x, test_index, mean, std)), dtype="float32"
            )
            test_features = scaler.transform(test_features).astype("float32", copy=False)
            test_window_score = final_ridge.decision_function(test_features)
            people = _participant_calibration_frame(meta, test_index, test_window_score)
            people["probability"] = platt.predict_proba(people[["score"]])[:, 1]
            people = people.drop(columns="score").assign(
                method="canonical_minirocket",
                held_out_source=source,
                seed=seed,
                selected_alpha=alpha,
                module_version=MODULE_VERSION,
            )
            predictions.append(people)
            pd.concat(predictions, ignore_index=True).to_csv(prediction_path, index=False)
            result = metric_row(people)
            diagnostics.append(
                {
                    "held_out_source": source,
                    "seed": seed,
                    "selected_alpha": alpha,
                    "features": int(config.minirocket_kernels // 84 * 84),
                    **result,
                }
            )
            pd.DataFrame(diagnostics).to_csv(
                processed / "canonical_minirocket_diagnostics.csv", index=False
            )
            print(
                f"MiniROCKET complete: held_out={source} seed={seed} alpha={alpha:g} "
                f"BA={result['balanced_accuracy']:.3f} FP={result['false_positives']} "
                f"FN={result['false_negatives']}"
            )
            del rocket, scaler, final_ridge, platt, test_features, test_window_score
            gc.collect()
    return pd.concat(predictions, ignore_index=True)


def load_incumbent(processed: Path, meta: pd.DataFrame, config: CorrectiveConfig) -> pd.DataFrame:
    path = processed / "evidence_gated_lower_back_dg_participant_predictions.csv"
    incumbent = pd.read_csv(path)
    incumbent = incumbent.loc[incumbent["method"].eq("ensemble_all")].copy()
    incumbent = incumbent[["held_out_source", "seed", "source", "group", "y", "probability"]]
    incumbent["method"] = INCUMBENT_METHOD
    expected = len(config.seeds) * meta["group"].nunique()
    if len(incumbent) != expected or set(incumbent["seed"].unique()) != set(config.seeds):
        raise AssertionError("Notebook-29 incumbent predictions do not match the locked protocol")
    return incumbent


def add_fixed_fusions(predictions: pd.DataFrame) -> pd.DataFrame:
    keys = ["held_out_source", "seed", "source", "group", "y"]
    wide = predictions.pivot(index=keys, columns="method", values="probability").reset_index()
    required = {INCUMBENT_METHOD, *BASE_CANDIDATES}
    if not required.issubset(wide.columns):
        raise AssertionError(f"Missing prediction columns: {required - set(wide.columns)}")
    frames = [predictions]
    for method, members in FUSIONS.items():
        frame = wide[keys].copy()
        frame["probability"] = wide[list(members)].mean(axis=1)
        frame["method"] = method
        frames.append(frame)
    return pd.concat(frames, ignore_index=True)


def metrics_from_predictions(predictions: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (method, source, seed), frame in predictions.groupby(
        ["method", "held_out_source", "seed"], sort=True
    ):
        if source != frame["source"].iloc[0] or frame["source"].nunique() != 1:
            raise AssertionError("Outer source and evaluation source are not identical")
        rows.append(
            {
                "method": method,
                "held_out_source": source,
                "evaluation_source": source,
                "seed": int(seed),
                **metric_row(frame),
            }
        )
    return pd.DataFrame(rows)


def _paired_interval(delta: np.ndarray, draws: int, seed: int) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    bootstrap = rng.choice(delta, size=(draws, len(delta)), replace=True).mean(axis=1)
    return {
        "mean_delta": float(delta.mean()),
        "ci_low": float(np.quantile(bootstrap, 0.025)),
        "ci_high": float(np.quantile(bootstrap, 0.975)),
    }


def decide(metrics: pd.DataFrame, config: CorrectiveConfig) -> tuple[pd.DataFrame, dict]:
    baseline = metrics.loc[metrics["method"].eq(INCUMBENT_METHOD)].copy()
    candidates = sorted(set(metrics["method"]) - {INCUMBENT_METHOD})
    decisions = {}
    source_rows = []
    for method in candidates:
        candidate = metrics.loc[metrics["method"].eq(method)].copy()
        merged = baseline.merge(
            candidate,
            on=["held_out_source", "evaluation_source", "seed"],
            suffixes=("_baseline", "_candidate"),
            validate="one_to_one",
        )
        intervals = {}
        for metric in (
            "balanced_accuracy",
            "specificity",
            "sensitivity",
            "auroc",
            "brier",
            "false_positives",
            "false_negatives",
        ):
            delta = merged[f"{metric}_candidate"].to_numpy() - merged[f"{metric}_baseline"].to_numpy()
            intervals[metric] = _paired_interval(
                delta, config.bootstrap_draws, config.tuning_seed
            )
        baseline_errors = merged["false_positives_baseline"] + merged["false_negatives_baseline"]
        candidate_errors = merged["false_positives_candidate"] + merged["false_negatives_candidate"]
        total_interval = _paired_interval(
            (candidate_errors - baseline_errors).to_numpy(),
            config.bootstrap_draws,
            config.tuning_seed,
        )
        source_delta = merged.assign(
            total_error_delta=candidate_errors - baseline_errors,
            ba_delta=merged["balanced_accuracy_candidate"] - merged["balanced_accuracy_baseline"],
            specificity_delta=merged["specificity_candidate"] - merged["specificity_baseline"],
            sensitivity_delta=merged["sensitivity_candidate"] - merged["sensitivity_baseline"],
            auroc_delta=merged["auroc_candidate"] - merged["auroc_baseline"],
        ).groupby("held_out_source", as_index=False).agg(
            total_error_delta=("total_error_delta", "mean"),
            balanced_accuracy_delta=("ba_delta", "mean"),
            specificity_delta=("specificity_delta", "mean"),
            sensitivity_delta=("sensitivity_delta", "mean"),
            auroc_delta=("auroc_delta", "mean"),
        )
        source_delta.insert(0, "method", method)
        source_rows.append(source_delta)
        relative_reduction = float(
            (baseline_errors.mean() - candidate_errors.mean()) / baseline_errors.mean()
        )
        both_error_types_improved = (
            intervals["false_positives"]["mean_delta"] < 0
            and intervals["false_negatives"]["mean_delta"] < 0
        )
        source_safe = bool(
            (source_delta["total_error_delta"] <= 0).all()
            and (source_delta["balanced_accuracy_delta"] >= -0.02).all()
            and (source_delta["specificity_delta"] >= -0.05).all()
            and (source_delta["sensitivity_delta"] >= -0.05).all()
            and (source_delta["auroc_delta"] >= -0.02).all()
        )
        discrimination_safe = bool(
            intervals["balanced_accuracy"]["mean_delta"] >= 0.005
            and intervals["balanced_accuracy"]["ci_low"] >= -0.02
            and intervals["auroc"]["mean_delta"] >= 0
            and intervals["auroc"]["ci_low"] >= -0.02
            and intervals["brier"]["mean_delta"] <= 0
            and intervals["brier"]["ci_high"] <= 0.02
        )
        material = relative_reduction >= 0.10
        total_error_supported = total_interval["ci_high"] <= 0
        accepted = bool(
            both_error_types_improved
            and source_safe
            and discrimination_safe
            and material
            and total_error_supported
        )
        decisions[method] = {
            "accepted": accepted,
            "both_fp_and_fn_improved": bool(both_error_types_improved),
            "every_source_nonregressing": source_safe,
            "discrimination_and_calibration_safe": discrimination_safe,
            "material_total_error_reduction": bool(material),
            "total_error_ci_supports_nonincrease": bool(total_error_supported),
            "mean_total_errors_baseline": float(baseline_errors.mean()),
            "mean_total_errors_candidate": float(candidate_errors.mean()),
            "relative_total_error_reduction": relative_reduction,
            "paired_bootstrap": {**intervals, "total_errors": total_interval},
        }
    accepted = [method for method, result in decisions.items() if result["accepted"]]
    selected = (
        max(accepted, key=lambda method: decisions[method]["relative_total_error_reduction"])
        if accepted
        else INCUMBENT_METHOD
    )
    decision = {
        "selected_method": selected,
        "improvement_found": selected != INCUMBENT_METHOD,
        "candidate_decisions": decisions,
        "gate": {
            "both_mean_fp_and_mean_fn_must_decrease": True,
            "minimum_relative_total_error_reduction": 0.10,
            "paired_total_error_bootstrap_ci_high_max": 0.0,
            "every_source_mean_total_error_delta_max": 0.0,
            "mean_balanced_accuracy_delta_min": 0.005,
            "mean_auroc_delta_min": 0.0,
            "mean_brier_delta_max": 0.0,
        },
        "selection_scope": "development-only five-seed leave-one-source-out",
        "frozen_cohorts_loaded": False,
        "if_no_candidate_passes": "Stop model rotation and retain notebook-29 incumbent.",
    }
    return pd.concat(source_rows, ignore_index=True), decision


def run(project_root: Path, config: CorrectiveConfig | None = None) -> dict:
    config = config or CorrectiveConfig()
    project_root = project_root.resolve()
    processed = project_root / "data" / "processed"
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if device.type != "cuda":
        raise RuntimeError("Canonical InceptionTime benchmark requires CUDA")
    module_text = Path(__file__).read_text(encoding="utf-8").lower()
    forbidden_loader_tokens = (
        "revalexo" + "_external_windows",
        "nonan" + "_external_windows",
    )
    for forbidden in forbidden_loader_tokens:
        if forbidden in module_text:
            raise AssertionError(f"Frozen-cohort loader reference found: {forbidden}")

    x, meta = load_development_data(processed)
    print(f"GPU candidate: {torch.cuda.get_device_name(0)}")
    print(f"MiniROCKET CPU workers: {config.minirocket_jobs}")
    print(meta.groupby(["source", "y"])["group"].nunique().rename("participants"))
    incumbent = load_incumbent(processed, meta, config)
    inception, tuning = run_inceptiontime(project_root, x, meta, config, device)
    minirocket = run_minirocket(project_root, x, meta, config)
    predictions = add_fixed_fusions(pd.concat([incumbent, inception, minirocket], ignore_index=True))
    metrics = metrics_from_predictions(predictions)
    source_deltas, decision = decide(metrics, config)
    summary = metrics.groupby(["method", "held_out_source"], as_index=False).agg(
        auroc=("auroc", "mean"),
        brier=("brier", "mean"),
        balanced_accuracy=("balanced_accuracy", "mean"),
        specificity=("specificity", "mean"),
        sensitivity=("sensitivity", "mean"),
        false_positives=("false_positives", "mean"),
        false_negatives=("false_negatives", "mean"),
    )
    overall = metrics.groupby("method", as_index=False).agg(
        auroc=("auroc", "mean"),
        brier=("brier", "mean"),
        balanced_accuracy=("balanced_accuracy", "mean"),
        specificity=("specificity", "mean"),
        sensitivity=("sensitivity", "mean"),
        false_positives=("false_positives", "mean"),
        false_negatives=("false_negatives", "mean"),
    )
    overall["total_errors"] = overall["false_positives"] + overall["false_negatives"]
    predictions.to_csv(processed / "canonical_corrective_participant_predictions.csv", index=False)
    metrics.to_csv(processed / "canonical_corrective_metrics.csv", index=False)
    summary.to_csv(processed / "canonical_corrective_source_summary.csv", index=False)
    overall.to_csv(processed / "canonical_corrective_overall_summary.csv", index=False)
    source_deltas.to_csv(processed / "canonical_corrective_source_deltas.csv", index=False)
    decision.update(
        {
            "module_version": MODULE_VERSION,
            "config": asdict(config),
            "development_participants": int(meta["group"].nunique()),
            "development_windows": int(len(meta)),
            "sources": sorted(meta["source"].unique().tolist()),
            "implementation_sources": {
                "inceptiontime_commit": INCEPTIONTIME_COMMIT,
                "minirocket_commit": MINIROCKET_COMMIT,
                "sktime_version": __import__("sktime").__version__,
                "torch_version": torch.__version__,
            },
            "input_sha256": {
                "primary": sha256(processed / "validated_acceleration_magnitude_windows_float32.npy"),
                "sint": sha256(processed / "sint_maartenskliniek_external_windows_float32.npy"),
                "incumbent_predictions": sha256(
                    processed / "evidence_gated_lower_back_dg_participant_predictions.csv"
                ),
            },
        }
    )
    (processed / "canonical_corrective_decision.json").write_text(
        json.dumps(decision, indent=2), encoding="utf-8"
    )
    print("\nOVERALL PARTICIPANT-LEVEL RESULTS")
    print(overall.round(4).to_string(index=False))
    print("\nDECISION")
    print(json.dumps(decision, indent=2))
    return {
        "tuning": tuning,
        "metrics": metrics,
        "summary": summary,
        "overall": overall,
        "source_deltas": source_deltas,
        "predictions": predictions,
        "decision": decision,
    }


if __name__ == "__main__":
    run(Path.cwd())
