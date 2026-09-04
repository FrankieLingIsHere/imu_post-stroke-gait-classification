"""Compare GAITEX virtual signals with the real Felius/Voisard healthy contract.

This is a descriptive source-compatibility audit.  It uses only the primary
development datasets and never reads RevalExo.  A low divergence is not enough
to admit GAITEX into supervised binary training because its trunk channel is a
pelvis proxy and its acceleration is virtual.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupKFold


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
VIRTUAL = ROOT / "data" / "interim" / "gaitex_2026" / "virtual_acceleration_sensitivity"
OUT = ROOT / "data" / "interim" / "gaitex_2026"
GRAVITY_M_S2 = 9.80665
RNG = np.random.default_rng(42)


def features(windows: np.ndarray) -> np.ndarray:
    """Compact per-window magnitude dynamics; no labels or external data."""
    mean = windows.mean(axis=1)
    std = windows.std(axis=1)
    p95 = np.quantile(windows, 0.95, axis=1)
    centered = windows - mean[:, None, :]
    spectrum = np.abs(np.fft.rfft(centered, axis=1)) ** 2
    frequency = np.fft.rfftfreq(windows.shape[1], d=1.0 / 100.0)
    centroid = (spectrum * frequency[None, :, None]).sum(axis=1) / spectrum.sum(axis=1).clip(1e-8)
    return np.concatenate([mean, std, p95, centroid], axis=1)


def bounded_per_participant(indices: np.ndarray, groups: np.ndarray, maximum: int = 24) -> np.ndarray:
    chosen = []
    for group in np.unique(groups[indices]):
        local = indices[groups[indices] == group]
        chosen.extend(RNG.choice(local, size=min(maximum, len(local)), replace=False))
    return np.asarray(chosen, dtype=int)


def energy_distance(x: np.ndarray, y: np.ndarray) -> float:
    return float(2 * cdist(x, y).mean() - cdist(x, x).mean() - cdist(y, y).mean())


def group_source_auc(x: np.ndarray, y: np.ndarray, x_groups: np.ndarray, y_groups: np.ndarray) -> float:
    values = np.concatenate([x, y])
    labels = np.r_[np.zeros(len(x), dtype=int), np.ones(len(y), dtype=int)]
    groups = np.r_[x_groups, y_groups]
    scores = np.full(len(labels), np.nan)
    # GroupKFold remains participant-disjoint. If a fold happens to contain one
    # source only, it is skipped rather than producing an invalid AUC.
    for train, test in GroupKFold(n_splits=3).split(values, labels, groups):
        if len(np.unique(labels[train])) < 2 or len(np.unique(labels[test])) < 2:
            continue
        model = LogisticRegression(max_iter=2000, class_weight="balanced", random_state=42)
        model.fit(values[train], labels[train])
        scores[test] = model.predict_proba(values[test])[:, 1]
    valid = np.isfinite(scores)
    return float(roc_auc_score(labels[valid], scores[valid])) if valid.any() and len(np.unique(labels[valid])) == 2 else float("nan")


def main() -> None:
    train = np.load(PROCESSED / "validated_acceleration_magnitude_windows_float32.npy")
    metadata = pd.read_csv(PROCESSED / "validated_window_metadata.csv")
    healthy = metadata.dataset_id.isin(["felius_2024", "voisard_2025"]) & metadata.label.eq("healthy")
    train = train[healthy.to_numpy()]
    metadata = metadata.loc[healthy].reset_index(drop=True)
    train_features = features(train)
    train_groups = metadata.participant_key.to_numpy()
    train_indices = bounded_per_participant(np.arange(len(train)), train_groups)
    reference = train_features[train_indices]
    reference_mean = reference.mean(axis=0)
    reference_std = reference.std(axis=0).clip(1e-6)

    rows = []
    for smoothing in (11, 21, 31):
        virtual = np.load(VIRTUAL / f"gaitex_virtual_proper_acceleration_magnitude_savgol_{smoothing}.npy") / GRAVITY_M_S2
        virtual_metadata = pd.read_csv(VIRTUAL / f"gaitex_virtual_proper_acceleration_magnitude_savgol_{smoothing}_metadata.csv")
        virtual_features = features(virtual)
        virtual_groups = virtual_metadata.participant.to_numpy()
        virtual_indices = bounded_per_participant(np.arange(len(virtual)), virtual_groups)
        candidate = virtual_features[virtual_indices]
        reference_z = (reference - reference_mean) / reference_std
        candidate_z = (candidate - reference_mean) / reference_std
        rows.append(
            {
                "smoothing_samples": smoothing,
                "virtual_windows": int(len(virtual)),
                "virtual_participants": int(virtual_metadata.participant.nunique()),
                "healthy_reference_windows": int(len(train)),
                "healthy_reference_participants": int(metadata.participant_key.nunique()),
                "feature_energy_distance": energy_distance(reference_z, candidate_z),
                "participant_disjoint_source_auc": group_source_auc(reference_z, candidate_z, train_groups[train_indices], virtual_groups[virtual_indices]),
                "median_abs_standardized_feature_shift": float(np.median(np.abs(candidate_z.mean(axis=0)))),
                "pelvis_proxy_median_g": float(np.median(virtual[:, :, 0])),
                "left_foot_p99_g": float(np.quantile(virtual[:, :, 1], 0.99)),
                "right_foot_p99_g": float(np.quantile(virtual[:, :, 2], 0.99)),
            }
        )
    audit = pd.DataFrame(rows).sort_values("feature_energy_distance")
    audit.to_csv(OUT / "virtual_training_contract_audit.csv", index=False)
    manifest = {
        "purpose": "unadapted virtual-to-real healthy contract audit; not a binary-training admission gate",
        "reference_data": "healthy windows from Felius and Voisard only",
        "explicit_exclusions": ["RevalExo", "Sint", "stroke windows", "classifier fitting"],
        "unit_conversion": "virtual proper acceleration magnitude converted from m/s² to g only",
        "interpretation": "source separability or distribution divergence indicates an adapter/pretraining requirement, not invalid motion",
        "next_gate": "only a fold-fitted source-aware adapter or self-supervised pretraining comparison may test downstream utility",
    }
    (OUT / "virtual_training_contract_audit_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(audit.to_string(index=False))
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
