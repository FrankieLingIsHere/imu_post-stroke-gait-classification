"""Train and freeze the selected lower-back development ensemble.

Only the Felius, Voisard, and Sint development tensors are loaded. The module
selects training duration on participant-disjoint, source/class-stratified
development validation groups, then retrains all selected members on the full
development pool. No external cohort is evaluated or loaded.
"""

from __future__ import annotations

import copy
import hashlib
import io
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from models.lower_back_ensemble import LowerBackDomainNet
from src.models.evidence_gated_domain_generalization import (
    BenchmarkConfig,
    METHODS,
    evaluate_by_source,
    load_development_data,
    train_model,
)


RELEASE_ID = "stroke-gait-lower-back-ensemble-v0.2.0"
SELECTION_EVIDENCE = "notebook-29 ensemble_all; notebook-34 no replacement admitted"


@dataclass(frozen=True)
class FreezeConfig:
    seeds: tuple[int, ...] = (42, 137, 202, 314, 515)
    tuning_seed: int = 20260903
    checkpoints: tuple[int, ...] = (4, 8, 12, 16)
    validation_fraction: float = 0.20
    per_source_batch: int = 64
    learning_rate: float = 1e-3
    erm_weight_decay: float = 1e-4
    ermpp_weight_decay: float = 5e-4
    coral_weight: float = 1.0
    linear_steps: int = 500
    sma_start_step: int = 600


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def state_sha256(state: dict[str, torch.Tensor]) -> str:
    buffer = io.BytesIO()
    torch.save(state, buffer)
    return hashlib.sha256(buffer.getvalue()).hexdigest()


def full_development_split(
    meta: pd.DataFrame, seed: int, fraction: float
) -> tuple[np.ndarray, np.ndarray]:
    """Hold out participants independently within every source/class cell."""
    rng = np.random.default_rng(seed)
    unique = meta[["source", "y", "group"]].drop_duplicates()
    validation_groups: set[str] = set()
    for (_, _), cell in unique.groupby(["source", "y"], sort=True):
        groups = np.asarray(sorted(cell["group"].unique()))
        rng.shuffle(groups)
        count = max(1, int(round(len(groups) * fraction)))
        count = min(count, len(groups) - 1)
        validation_groups.update(groups[:count].tolist())
    validation = meta["group"].isin(validation_groups).to_numpy()
    fit = ~validation
    if set(meta.loc[fit, "group"]).intersection(meta.loc[validation, "group"]):
        raise AssertionError("Participant leakage in full-development tuning split")
    for mask, name in ((fit, "fit"), (validation, "validation")):
        cells = meta.loc[mask].groupby(["source", "y"])["group"].nunique()
        if len(cells) != 6 or (cells <= 0).any():
            raise AssertionError(f"Incomplete source/class cells in {name}: {cells.to_dict()}")
    return fit, validation


def benchmark_config(config: FreezeConfig) -> BenchmarkConfig:
    return BenchmarkConfig(
        seeds=config.seeds,
        tuning_seed=config.tuning_seed,
        checkpoints=config.checkpoints,
        per_source_batch=config.per_source_batch,
        learning_rate=config.learning_rate,
        erm_weight_decay=config.erm_weight_decay,
        ermpp_weight_decay=config.ermpp_weight_decay,
        coral_weight=config.coral_weight,
        linear_steps=config.linear_steps,
        sma_start_step=config.sma_start_step,
        validation_fraction=config.validation_fraction,
        representation="lower_back_acceleration",
    )


def select_full_data_epochs(
    x: np.ndarray,
    meta: pd.DataFrame,
    config: FreezeConfig,
    device: torch.device,
) -> tuple[dict[str, int], pd.DataFrame]:
    fit, validation = full_development_split(
        meta, config.tuning_seed, config.validation_fraction
    )
    validation_index = np.flatnonzero(validation)
    evaluation_masks = {epoch: validation_index for epoch in config.checkpoints}
    base_config = benchmark_config(config)
    rows = []
    selected = {}
    for method in METHODS:
        model, _, _, history = train_model(
            method,
            x,
            meta,
            fit,
            [0],
            max(config.checkpoints),
            base_config,
            config.tuning_seed,
            device,
            evaluation_masks,
        )
        del model
        history_frame = pd.DataFrame(history)
        validation_history = history_frame.loc[
            history_frame.get("validation", False).fillna(False)
            & history_frame["evaluation_source"].ne("pooled")
        ].copy()
        for epoch, frame in validation_history.groupby("epoch", sort=True):
            rows.append(
                {
                    "method": method,
                    "epoch": int(epoch),
                    "worst_balanced_accuracy": float(frame["balanced_accuracy"].min()),
                    "worst_specificity": float(frame["specificity"].min()),
                    "worst_sensitivity": float(frame["sensitivity"].min()),
                    "worst_auroc": float(frame["auroc"].min()),
                    "mean_brier": float(frame["brier"].mean()),
                }
            )
    tuning = pd.DataFrame(rows)
    for method, frame in tuning.groupby("method", sort=True):
        best = frame.sort_values(
            ["worst_balanced_accuracy", "worst_specificity", "mean_brier", "epoch"],
            ascending=[False, False, True, True],
        ).iloc[0]
        selected[method] = int(best["epoch"])
    return selected, tuning


def build_smoke_windows() -> np.ndarray:
    time = np.linspace(0.0, 5.0, 500, endpoint=False, dtype="float32")
    quiet = np.ones(500, dtype="float32")
    periodic = (1.0 + 0.15 * np.sin(2 * np.pi * 1.1 * time)).astype("float32")
    return np.stack([quiet, periodic], axis=0)[:, :, None]


@torch.inference_mode()
def bundle_probabilities(
    bundle: dict,
    windows: np.ndarray,
    device: torch.device,
) -> np.ndarray:
    values = np.asarray(windows, dtype="float32")
    if values.ndim == 2:
        values = values[:, :, None]
    if values.ndim != 3 or values.shape[1:] != (500, 1):
        raise ValueError(f"Expected (n, 500) or (n, 500, 1), got {values.shape}")
    member_probabilities = []
    for member in bundle["members"]:
        mean = float(member["mean"].item())
        std = max(float(member["std"].item()), 1e-6)
        batch = torch.from_numpy(
            np.ascontiguousarray(((values[:, :, 0] - mean) / std)[:, None, :])
        ).to(device)
        model = LowerBackDomainNet().to(device)
        model.load_state_dict(member["model_state_dict"], strict=True)
        model.eval()
        member_probabilities.append(torch.sigmoid(model(batch)).cpu().numpy())
        del model
    return np.mean(np.stack(member_probabilities, axis=0), axis=0)


def run(project_root: Path, config: FreezeConfig | None = None) -> dict:
    project_root = project_root.resolve()
    config = config or FreezeConfig()
    processed = project_root / "data" / "processed"
    checkpoint_dir = project_root / "models" / "checkpoints"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_path = checkpoint_dir / f"{RELEASE_ID}.pt"
    manifest_path = checkpoint_dir / f"{RELEASE_ID}.manifest.json"
    tuning_path = processed / "lower_back_release_freeze_tuning.csv"
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if device.type != "cuda":
        raise RuntimeError("The release freeze is intentionally GPU-only")
    source_text = Path(__file__).read_text(encoding="utf-8").lower()
    forbidden_tokens = ("revalexo" + "_external_windows", "nonan" + "_external_windows")
    for token in forbidden_tokens:
        if token in source_text:
            raise AssertionError(f"Frozen-cohort loader reference found: {token}")

    x, meta = load_development_data(processed)
    selected_epochs, tuning = select_full_data_epochs(x, meta, config, device)
    tuning.to_csv(tuning_path, index=False)
    print("Selected full-development epochs:", selected_epochs)

    full_mask = np.ones(len(meta), dtype=bool)
    members = []
    member_manifest = []
    base_config = benchmark_config(config)
    for seed in config.seeds:
        for method in METHODS:
            model, mean, std, _ = train_model(
                method,
                x,
                meta,
                full_mask,
                [0],
                selected_epochs[method],
                base_config,
                seed,
                device,
            )
            state = {name: tensor.detach().cpu() for name, tensor in model.state_dict().items()}
            member = {
                "method": method,
                "seed": int(seed),
                "epochs": int(selected_epochs[method]),
                "mean": torch.tensor([float(mean[0])], dtype=torch.float32),
                "std": torch.tensor([float(std[0])], dtype=torch.float32),
                "model_state_dict": state,
            }
            members.append(member)
            member_manifest.append(
                {
                    "method": method,
                    "seed": int(seed),
                    "epochs": int(selected_epochs[method]),
                    "state_sha256": state_sha256(state),
                }
            )
            print(f"Frozen member method={method} seed={seed} epochs={selected_epochs[method]}")
            del model
            torch.cuda.empty_cache()

    bundle = {
        "release_id": RELEASE_ID,
        "format_version": 1,
        "architecture": "LowerBackDomainNet",
        "input_contract": {
            "shape": ["windows", 500, 1],
            "sampling_hz": 100,
            "duration_seconds": 5,
            "channel": "lower_back_acceleration_magnitude_g",
        },
        "aggregation": "equal mean over five seeds within each of three methods; equal mean across methods",
        "selection_evidence": SELECTION_EVIDENCE,
        "members": members,
    }
    smoke_windows = build_smoke_windows()
    smoke_probabilities = bundle_probabilities(bundle, smoke_windows, device)
    bundle["smoke_test"] = {
        "description": "constant-1g and deterministic 1.1-Hz synthetic lower-back windows",
        "windows": torch.from_numpy(smoke_windows),
        "expected_probabilities": torch.from_numpy(smoke_probabilities.astype("float32")),
        "absolute_tolerance": 1e-6,
    }
    torch.save(bundle, checkpoint_path)
    checkpoint_hash = sha256(checkpoint_path)

    reloaded = torch.load(checkpoint_path, map_location="cpu", weights_only=True)
    observed = bundle_probabilities(reloaded, smoke_windows, torch.device("cpu"))
    maximum_error = float(np.max(np.abs(observed - smoke_probabilities)))
    if maximum_error > 1e-6:
        raise AssertionError(f"Checkpoint smoke-test mismatch: {maximum_error}")

    manifest = {
        "release_id": RELEASE_ID,
        "checkpoint_filename": checkpoint_path.name,
        "checkpoint_sha256": checkpoint_hash,
        "checkpoint_bytes": checkpoint_path.stat().st_size,
        "selection_evidence": SELECTION_EVIDENCE,
        "selected_epochs": selected_epochs,
        "members": member_manifest,
        "development_participants": int(meta["group"].nunique()),
        "development_windows": int(len(meta)),
        "development_sources": sorted(meta["source"].unique().tolist()),
        "config": asdict(config),
        "input_sha256": {
            "primary": sha256(processed / "validated_acceleration_magnitude_windows_float32.npy"),
            "sint": sha256(processed / "sint_maartenskliniek_external_windows_float32.npy"),
        },
        "software": {
            "python": __import__("sys").version.split()[0],
            "torch": torch.__version__,
            "cuda_device": torch.cuda.get_device_name(0),
        },
        "smoke_test_maximum_absolute_error": maximum_error,
        "external_cohorts_loaded": False,
        "performance_claim": "None: this is a full-development fit, not an unbiased evaluation.",
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return {
        "checkpoint_path": checkpoint_path,
        "manifest_path": manifest_path,
        "manifest": manifest,
        "tuning": tuning,
        "smoke_probabilities": smoke_probabilities,
    }


if __name__ == "__main__":
    run(Path.cwd())
