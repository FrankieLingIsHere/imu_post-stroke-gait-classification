"""Test a leakage-safe, waveform-preserving GAITEX source adapter.

The adapter matches only each channel's healthy-development median and IQR.
It is fitted independently inside repeated participant-held-out splits.  An
affine transform cannot manufacture gait dynamics: it preserves within-window
ordering, temporal correlation, and non-DC spectral shape exactly.  The audit
asks whether scale/offset alone explains the virtual-vs-real mismatch; it does
not fit or evaluate the stroke classifier.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupShuffleSplit


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
VIRTUAL = ROOT / "data" / "interim" / "gaitex_2026" / "virtual_acceleration_sensitivity"
OUT = ROOT / "data" / "interim" / "gaitex_2026"
RNG = np.random.default_rng(42)


def feature_matrix(windows: np.ndarray) -> np.ndarray:
    mean = windows.mean(axis=1)
    std = windows.std(axis=1)
    p95 = np.quantile(windows, 0.95, axis=1)
    centred = windows - mean[:, None, :]
    spectrum = np.abs(np.fft.rfft(centred, axis=1)) ** 2
    frequency = np.fft.rfftfreq(windows.shape[1], d=1.0 / 100.0)
    centroid = (spectrum * frequency[None, :, None]).sum(axis=1) / spectrum.sum(axis=1).clip(1e-8)
    return np.concatenate([mean, std, p95, centroid], axis=1)


def cap_per_person(indices: np.ndarray, groups: np.ndarray, maximum: int = 24) -> np.ndarray:
    selected = []
    for group in np.unique(groups[indices]):
        local = indices[groups[indices] == group]
        selected.extend(RNG.choice(local, size=min(maximum, len(local)), replace=False))
    return np.asarray(selected, dtype=int)


def energy_distance(left: np.ndarray, right: np.ndarray) -> float:
    return float(2 * cdist(left, right).mean() - cdist(left, left).mean() - cdist(right, right).mean())


def robust_affine(reference: np.ndarray, candidate: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    reference_median = np.median(reference, axis=(0, 1))
    candidate_median = np.median(candidate, axis=(0, 1))
    reference_iqr = np.quantile(reference, 0.75, axis=(0, 1)) - np.quantile(reference, 0.25, axis=(0, 1))
    candidate_iqr = np.quantile(candidate, 0.75, axis=(0, 1)) - np.quantile(candidate, 0.25, axis=(0, 1))
    scale = reference_iqr / candidate_iqr.clip(1e-5)
    offset = reference_median - scale * candidate_median
    return scale, offset


def main() -> None:
    real = np.load(PROCESSED / "validated_acceleration_magnitude_windows_float32.npy")
    real_meta = pd.read_csv(PROCESSED / "validated_window_metadata.csv")
    mask = real_meta.dataset_id.isin(["felius_2024", "voisard_2025"]) & real_meta.label.eq("healthy")
    real = real[mask.to_numpy()]
    real_groups = real_meta.loc[mask, "participant_key"].to_numpy()
    virtual = np.load(VIRTUAL / "gaitex_virtual_proper_acceleration_magnitude_savgol_11.npy") / 9.80665
    virtual_meta = pd.read_csv(VIRTUAL / "gaitex_virtual_proper_acceleration_magnitude_savgol_11_metadata.csv")
    virtual_groups = virtual_meta.participant.to_numpy()
    real_indices = cap_per_person(np.arange(len(real)), real_groups)
    virtual_indices = cap_per_person(np.arange(len(virtual)), virtual_groups)
    real = real[real_indices]
    real_groups = real_groups[real_indices]
    virtual = virtual[virtual_indices]
    virtual_groups = virtual_groups[virtual_indices]
    all_windows = np.concatenate([real, virtual])
    labels = np.r_[np.zeros(len(real), dtype=int), np.ones(len(virtual), dtype=int)]
    groups = np.r_[real_groups, virtual_groups]
    rows = []
    splitter = GroupShuffleSplit(n_splits=20, test_size=0.25, random_state=42)
    for split, (train, test) in enumerate(splitter.split(all_windows, labels, groups), start=1):
        real_train = train[labels[train] == 0]
        virtual_train = train[labels[train] == 1] - len(real)
        real_test = test[labels[test] == 0]
        virtual_test = test[labels[test] == 1] - len(real)
        if not len(real_train) or not len(virtual_train) or not len(real_test) or not len(virtual_test):
            continue
        scale, offset = robust_affine(real[real_train], virtual[virtual_train])
        virtual_adapted = virtual * scale[None, None, :] + offset[None, None, :]
        real_features = feature_matrix(real)
        virtual_before = feature_matrix(virtual)
        virtual_after = feature_matrix(virtual_adapted)
        standard_mean = real_features[real_train].mean(axis=0)
        standard_std = real_features[real_train].std(axis=0).clip(1e-6)
        train_x = np.concatenate([real_features[real_train], virtual_after[virtual_train]])
        train_y = np.r_[np.zeros(len(real_train), dtype=int), np.ones(len(virtual_train), dtype=int)]
        test_x = np.concatenate([real_features[real_test], virtual_after[virtual_test]])
        test_y = np.r_[np.zeros(len(real_test), dtype=int), np.ones(len(virtual_test), dtype=int)]
        classifier = LogisticRegression(max_iter=2000, class_weight="balanced", random_state=42)
        classifier.fit((train_x - standard_mean) / standard_std, train_y)
        source_auc = roc_auc_score(test_y, classifier.predict_proba((test_x - standard_mean) / standard_std)[:, 1])
        before_energy = energy_distance(
            (real_features[real_test] - standard_mean) / standard_std,
            (virtual_before[virtual_test] - standard_mean) / standard_std,
        )
        after_energy = energy_distance(
            (real_features[real_test] - standard_mean) / standard_std,
            (virtual_after[virtual_test] - standard_mean) / standard_std,
        )
        rows.append(
            {
                "split": split,
                "real_test_participants": int(np.unique(real_groups[real_test]).size),
                "virtual_test_participants": int(np.unique(virtual_groups[virtual_test]).size),
                "source_auc_after_adapter": float(source_auc),
                "energy_distance_before": before_energy,
                "energy_distance_after": after_energy,
                "energy_distance_change": after_energy - before_energy,
                "pelvis_scale": float(scale[0]),
                "left_foot_scale": float(scale[1]),
                "right_foot_scale": float(scale[2]),
            }
        )
    splits = pd.DataFrame(rows)
    splits.to_csv(OUT / "virtual_affine_adapter_split_audit.csv", index=False)
    summary = {
        "splits": int(len(splits)),
        "source_auc_median": float(splits.source_auc_after_adapter.median()),
        "source_auc_empirical_95pct_interval": [float(splits.source_auc_after_adapter.quantile(0.025)), float(splits.source_auc_after_adapter.quantile(0.975))],
        "energy_distance_before_median": float(splits.energy_distance_before.median()),
        "energy_distance_after_median": float(splits.energy_distance_after.median()),
        "energy_distance_change_median": float(splits.energy_distance_change.median()),
        "adapter": "per-channel robust affine scale/offset fitted on healthy training participants inside each split",
        "waveform_preservation": "affine channel mapping preserves temporal ordering, correlation, and non-DC spectral shape; it cannot add physiological detail",
        "exclusions": ["RevalExo", "Sint", "stroke windows", "classifier fitting"],
        "decision_scope": "source-contract evidence only; downstream pretraining utility would still require a separately designed participant-level comparison",
    }
    (OUT / "virtual_affine_adapter_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(splits.describe().to_string())
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
