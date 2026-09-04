"""Participant-level preprocessing ablation for the Zenodo stroke adapter."""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
X = np.load(ROOT / "data/processed/zenodo_stroke_windows_float32.npy", mmap_mode="r")
M = pd.read_csv(ROOT / "data/processed/zenodo_stroke_window_metadata.csv")
rng = np.random.default_rng(20260824)
participants = np.array(sorted(M.participant.unique()))
rng.shuffle(participants)
folds = np.array_split(participants, 5)
rows = []
for fold, test_people in enumerate(folds):
    fit_people = np.array([p for p in participants if p not in set(test_people)])
    fit = X[M.participant.isin(fit_people)]
    test = X[M.participant.isin(test_people)]
    flat = np.asarray(fit).reshape(-1, X.shape[-1])
    med = np.median(flat, axis=0)
    q25, q75 = np.quantile(flat, [.25, .75], axis=0)
    iqr = np.maximum(q75 - q25, 1e-3)
    for policy in ("standard", "robust", "cap_99.5_robust", "cap_99.9_robust"):
        if policy == "standard":
            center, scale = flat.mean(0), np.maximum(flat.std(0), 1e-3)
            z = (np.asarray(test).reshape(-1, X.shape[-1]) - center) / scale
        else:
            cap_q = None if policy == "robust" else (0.995 if policy == "cap_99.5_robust" else 0.999)
            t = np.asarray(test)
            if cap_q:
                lo, hi = np.quantile(flat, [1-cap_q, cap_q], axis=0)
                t = np.clip(t, lo, hi)
            z = ((t - med) / iqr).reshape(-1, X.shape[-1])
        rows.append({"fold": fold, "policy": policy, "fit_participants": len(fit_people),
                     "test_participants": len(test_people), "test_abs_z_p99": np.quantile(np.abs(z), .99),
                     "test_abs_z_max": np.max(np.abs(z)), "test_abs_z_gt10": np.mean(np.abs(z)>10)})
out = ROOT / "data/processed/zenodo_preprocessing_ablation.csv"
result = pd.DataFrame(rows)
result.to_csv(out, index=False)
print(result.groupby("policy")[["test_abs_z_p99", "test_abs_z_max", "test_abs_z_gt10"]].mean().to_string())
print(f"Wrote: {out}")
