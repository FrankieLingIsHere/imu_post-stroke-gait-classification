"""Quantify candidate normalization strategies without touching model labels or test data.

This is a pre-training audit. Statistics are fitted separately per source on the
development pool and then used only to describe how much source shift remains.
It does not select a final transform or use RevalExo for fitting.
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "data" / "processed"
OUT = P / "normalization_strategy_audit.csv"

arrays = [
    ("validated", "validated_acceleration_magnitude_windows_float32.npy", "validated_window_metadata.csv"),
    ("sint", "sint_maartenskliniek_external_windows_float32.npy", "sint_maartenskliniek_external_window_metadata.csv"),
    ("tier1_healthy", "tier1_healthy_marea_duogait_windows_float32.npy", "tier1_healthy_marea_duogait_window_metadata.csv"),
]
parts = []
for source, arr_name, meta_name in arrays:
    x = np.load(P / arr_name).astype("float32")
    m = pd.read_csv(P / meta_name)
    if "label" in m:
        keep = m.label.isin(["healthy", "stroke"]).to_numpy()
        x, m = x[keep], m.loc[keep].reset_index(drop=True)
    m["source"] = source
    parts.append((source, x, m))

# The existing representation is magnitude per channel: N x time x 3.
all_x = np.concatenate([x for _, x, _ in parts], axis=0)
global_med = np.median(all_x, axis=(0, 1))
global_iqr = np.subtract(*np.percentile(all_x, [75, 25], axis=(0, 1))).clip(1e-5)
global_mean = all_x.mean(axis=(0, 1))
global_std = all_x.std(axis=(0, 1)).clip(1e-5)

rows = []
for source, x, m in parts:
    source_med = np.median(x, axis=(0, 1))
    source_iqr = np.subtract(*np.percentile(x, [75, 25], axis=(0, 1))).clip(1e-5)
    source_mean = x.mean(axis=(0, 1))
    source_std = x.std(axis=(0, 1)).clip(1e-5)
    for channel, (gm, gs, gi, sm, ss, si) in enumerate(zip(global_mean, global_std, global_iqr, source_mean, source_std, source_iqr)):
        rows.append({
            "source": source, "channel": ["lower_back", "left_foot", "right_foot"][channel],
            "raw_mean": float(sm), "raw_std": float(ss),
            "global_z_mean": float((sm-gm)/gs), "global_z_std": float(ss/gs),
            "global_robust_mean": float((sm-gm)/gi), "global_robust_scale": float(si/gi),
            "raw_iqr": float(si),
            "participants": int(m.participant_key.nunique()) if "participant_key" in m else int(m.subject.nunique()),
            "windows": int(len(m)),
        })

pd.DataFrame(rows).to_csv(OUT, index=False)
print(pd.DataFrame(rows).to_string(index=False))
print(f"Wrote {OUT}")
