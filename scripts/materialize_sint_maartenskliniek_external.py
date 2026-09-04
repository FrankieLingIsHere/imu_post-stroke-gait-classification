"""Materialize Sint Maartenskliniek as an external-only candidate tensor.

No model fitting, normalization, calibration, thresholding, or training data
selection is performed here. The output is deliberately labelled external.
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/raw/sint_maartenskliniek/extracted/IMU_GaitAnalysis-1.1.0/data"
OUT = ROOT / "data/processed"
MANIFEST = OUT / "sint_maartenskliniek_trial_manifest.csv"
FS = 100
WIN = 500
HOP = 250
G = 9.80665
SENSORS = {
    "LB": "00B40A8D.txt",
    "LF": "00B40AC5.txt",
    "RF": "00B40A23.txt",
}


def read_acc(path: Path) -> np.ndarray:
    lines = path.read_text(errors="replace").splitlines()
    header = next(i for i, line in enumerate(lines) if line.startswith("PacketCounter\t"))
    frame = pd.read_csv(path, sep="\t", skiprows=header)
    acc = frame[["Acc_X", "Acc_Y", "Acc_Z"]].apply(pd.to_numeric, errors="coerce").to_numpy(dtype=np.float32)
    return acc / G


def main() -> None:
    manifest = pd.read_csv(MANIFEST)
    manifest = manifest[manifest.export_exists].copy()
    allowed = {(r.participant, r.exported_trial): r for r in manifest.itertuples()}
    windows, rows = [], []
    for label, parent in [("stroke", DATA / "CVA"), ("healthy", DATA / "Healthy_controls")]:
        for participant_dir in sorted(parent.glob("900_*")):
            for trial_dir in sorted((participant_dir / "Xsens").glob("exported*")):
                trial_info = allowed.get((participant_dir.name, trial_dir.name))
                if trial_info is None:
                    continue
                paths = {
                    name: next(iter(trial_dir.glob(f"*_{suffix}")), trial_dir / suffix)
                    for name, suffix in SENSORS.items()
                }
                if not all(path.exists() for path in paths.values()):
                    continue
                signals = {name: read_acc(path) for name, path in paths.items()}
                n = min(map(len, signals.values()))
                signal = np.stack([np.linalg.norm(signals[name][:n], axis=1) for name in ("LB", "LF", "RF")], axis=1)
                signal = signal[np.isfinite(signal).all(axis=1)]
                trial_windows = 0
                for start in range(0, max(0, len(signal) - WIN + 1), HOP):
                    windows.append(signal[start:start + WIN].astype(np.float32))
                    rows.append({
                        "window_id": len(rows),
                        "dataset_id": "sint_maartenskliniek",
                        "participant_key": f"sint_{participant_dir.name}",
                        "participant": participant_dir.name,
                        "trial": trial_dir.name,
                        "label": label,
                        "label_binary": int(label == "stroke"),
                        "source_fs_hz": FS,
                        "window_fs_hz": FS,
                        "window_seconds": WIN / FS,
                        "hop_seconds": HOP / FS,
                        "role": "external_candidate_only",
                        "vicon_trial": trial_info.vicon_trial,
                        "trial_type": trial_info.trial_type,
                        "speed_condition": trial_info.speed_condition,
                    })
                    trial_windows += 1
                if trial_windows == 0:
                    continue
    arr = np.asarray(windows, dtype=np.float32)
    meta = pd.DataFrame(rows)
    assert arr.ndim == 3 and arr.shape[1:] == (WIN, 3), arr.shape
    assert len(meta) == len(arr)
    assert np.isfinite(arr).all()
    OUT.mkdir(parents=True, exist_ok=True)
    np.save(OUT / "sint_maartenskliniek_external_windows_float32.npy", arr)
    meta.to_csv(OUT / "sint_maartenskliniek_external_window_metadata.csv", index=False)
    print("Array:", arr.shape)
    print(meta.groupby(["label", "participant_key"]).size().groupby(level=0).agg(["count", "sum"]))
    print("Wrote external-only outputs")


if __name__ == "__main__":
    main()
