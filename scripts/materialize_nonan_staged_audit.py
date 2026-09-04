"""Materialize predeclared NONAN structural-audit windows; never training data."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from zipfile import ZipFile

import numpy as np
import pandas as pd
from scipy.signal import resample_poly


ROOT = Path(__file__).resolve().parents[1]
RAW_ROOT = ROOT / "data" / "raw" / "nonan_gaitprint"
OUT = ROOT / "data" / "interim" / "nonan_gaitprint"
CHANNELS = {
    "lower_spine_l1_t12_proxy": ["Lower spine Accel Sensor X (mG)", "Lower spine Accel Sensor Y (mG)", "Lower spine Accel Sensor Z (mG)"],
    "left_foot": ["Foot Accel Sensor X LT (mG)", "Foot Accel Sensor Y LT (mG)", "Foot Accel Sensor Z LT (mG)"],
    "right_foot": ["Foot Accel Sensor X RT (mG)", "Foot Accel Sensor Y RT (mG)", "Foot Accel Sensor Z RT (mG)"],
}
WINDOW = 500  # 5 s at the established 100-Hz model rate


def repair_isolated_vector_spikes(signal: np.ndarray, threshold_g: float = 16.0) -> tuple[np.ndarray, int]:
    """Interpolate only interior runs of <=2 vector-magnitude exceedances."""
    repaired = signal.copy()
    bad = np.linalg.norm(repaired, axis=1) > threshold_g
    patched = 0
    i = 0
    while i < len(bad):
        if not bad[i]:
            i += 1
            continue
        j = i + 1
        while j < len(bad) and bad[j]:
            j += 1
        if i > 0 and j < len(bad) and j - i <= 2:
            repaired[i:j] = np.linspace(repaired[i - 1], repaired[j], j - i + 2)[1:-1]
            patched += j - i
        i = j
    return repaired, patched


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--partition", default="structural_audit_only")
    args = parser.parse_args()
    packages = (
        RAW_ROOT / "staged_audit" / "source_packages"
        if args.partition == "structural_audit_only"
        else RAW_ROOT / "source_packages" / args.partition
    )
    if not packages.exists():
        raise FileNotFoundError(packages)
    raw_windows: list[np.ndarray] = []
    repaired_windows: list[np.ndarray] = []
    metadata: list[dict] = []
    patched_total = 0
    for archive in sorted(packages.glob("S*.zip")):
        participant = archive.stem
        with ZipFile(archive) as z:
            for member in sorted(name for name in z.namelist() if name.endswith(".csv")):
                with z.open(member) as handle:
                    reader = csv.reader((line.decode("utf-8-sig") for line in handle))
                    header = next(reader)
                    indices = [[header.index(name) for name in names] for names in CHANNELS.values()]
                    rows = [[float(row[i]) / 1000.0 for group in indices for i in group] for row in reader]
                axes = np.asarray(rows, dtype=np.float32).reshape(-1, 3, 3)
                repaired_axes = axes.copy()
                patched = 0
                for channel in range(3):
                    repaired_axes[:, channel], n = repair_isolated_vector_spikes(axes[:, channel])
                    patched += n
                patched_total += patched
                raw_resampled = resample_poly(axes, 1, 2, axis=0)
                repaired_resampled = resample_poly(repaired_axes, 1, 2, axis=0)
                raw_mag = np.linalg.norm(raw_resampled, axis=2)
                repaired_mag = np.linalg.norm(repaired_resampled, axis=2)
                for start in range(0, len(raw_mag) - WINDOW + 1, WINDOW):
                    raw_windows.append(raw_mag[start : start + WINDOW])
                    repaired_windows.append(repaired_mag[start : start + WINDOW])
                    metadata.append({
                        "dataset_id": "nonan_gaitprint",
                        "participant": participant,
                        "participant_key": f"nonan_gaitprint:{participant}",
                        "label": "healthy",
                        "partition": args.partition,
                        "lower_back_contract": "lower_spine_l1_t12_proxy",
                        "trial": Path(member).stem,
                        "start_100hz": start,
                        "window_seconds": 5.0,
                        "source_hz": 200.0,
                        "target_hz": 100.0,
                        "isolated_spike_samples_repaired_trial": patched,
                    })
    OUT.mkdir(parents=True, exist_ok=True)
    raw = np.asarray(raw_windows, dtype=np.float32)
    repaired = np.asarray(repaired_windows, dtype=np.float32)
    assert raw.shape == repaired.shape and raw.shape[1:] == (WINDOW, 3) and np.isfinite(raw).all() and np.isfinite(repaired).all()
    prefix = "staged_audit" if args.partition == "structural_audit_only" else args.partition
    np.save(OUT / f"{prefix}_magnitude_raw.npy", raw)
    np.save(OUT / f"{prefix}_magnitude_isolated_spike_repaired.npy", repaired)
    pd.DataFrame(metadata).to_csv(OUT / f"{prefix}_window_metadata.csv", index=False)
    (OUT / f"{prefix}_materialization.json").write_text(json.dumps({"windows": int(len(raw)), "shape": list(raw.shape), "patched_samples": patched_total, "status": args.partition}, indent=2), encoding="utf-8")
    print(json.dumps({"partition": args.partition, "windows": raw.shape, "patched_samples": patched_total, "raw_max_g": float(raw.max()), "repaired_max_g": float(repaired.max())}))


if __name__ == "__main__":
    main()
