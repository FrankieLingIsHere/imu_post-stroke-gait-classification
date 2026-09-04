"""Audit finite values and extreme-signal rates in Zenodo stroke windows."""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
X = np.load(ROOT / "data/processed/zenodo_stroke_windows_float32.npy", mmap_mode="r")
M = pd.read_csv(ROOT / "data/processed/zenodo_stroke_window_metadata.csv")
names = [f"{s}_{k}" for s in ("LB", "LF", "RF") for k in ("ax", "ay", "az", "gx", "gy", "gz")]
rows = []
for participant, idx in M.groupby("participant").groups.items():
    a = np.asarray(X[idx])
    for j, name in enumerate(names):
        v = a[:, :, j]
        rows.append({
            "participant": participant, "channel": name,
            "windows": len(v), "finite": bool(np.isfinite(v).all()),
            "p01": np.quantile(v, .01), "median": np.quantile(v, .5),
            "p99": np.quantile(v, .99), "max_abs": np.abs(v).max(),
            "rate_abs_gt_100": np.mean(np.abs(v) > 100),
            "rate_abs_gt_500": np.mean(np.abs(v) > 500),
        })
out = ROOT / "data/processed/zenodo_stroke_window_quality.csv"
pd.DataFrame(rows).to_csv(out, index=False)
summary = pd.DataFrame(rows).groupby("channel").agg(
    participants=("participant", "nunique"), max_abs=("max_abs", "max"),
    median_p99=("p99", "median"), median_rate_gt100=("rate_abs_gt_100", "median"),
    max_rate_gt100=("rate_abs_gt_100", "max"), max_rate_gt500=("rate_abs_gt_500", "max"))
print(summary.to_string(float_format=lambda z: f"{z:.4f}"))
print(f"Wrote: {out}")
