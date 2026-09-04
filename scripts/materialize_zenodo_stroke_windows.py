"""Materialize participant-separated 3-sensor Zenodo stroke windows.

Uses the consistently available LF/RF/SA files (SA carries device tag ST-3).
This is a stroke-only representation/robustness stream, not binary training.
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/raw/zenodo_stroke_rehab/extracted/interim"
OUT = ROOT / "data/processed"
SENSORS = ("SA", "LF", "RF")
N = 500                         # 5 s at 100 Hz
STRIDE = 250                    # 50% overlap

def load(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    frame = frame.rename(columns={"AccX": "AccX", "AccY": "AccY", "AccZ": "AccZ"})
    cols = ["timestamp", "AccX", "AccY", "AccZ", "GyrX", "GyrY", "GyrZ"]
    missing = [c for c in cols if c not in frame]
    if missing:
        raise ValueError(f"{path}: missing {missing}")
    return frame[cols].dropna().drop_duplicates("timestamp").sort_values("timestamp")

def main():
    windows, meta = [], []
    for participant_dir in sorted(DATA.glob("imu*")):
        for visit_dir in sorted(participant_dir.glob("visit*")):
            paths = {s: visit_dir / "imu" / f"{s}.csv" for s in SENSORS}
            if not all(p.exists() for p in paths.values()):
                continue
            frames = {s: load(p).set_index("timestamp") for s, p in paths.items()}
            start = max(f.index.min() for f in frames.values())
            end = min(f.index.max() for f in frames.values())
            if end <= start:
                continue
            # Interpolate each sensor onto a shared 100-Hz grid.
            grid = np.arange(start, end, 0.01)
            arrays = []
            for s in SENSORS:
                source = frames[s]
                # Fill only short gaps (<=20 samples, about 0.2 s). Long gaps
                # must not be bridged because that creates artificial gyro spikes.
                f = (source.reindex(source.index.union(grid))
                     .interpolate(method="index", limit=20, limit_area="inside")
                     .reindex(grid))
                arrays.append(f.to_numpy(dtype=np.float32))
            signal = np.concatenate(arrays, axis=1)  # SA, LF, RF; accel then gyro
            valid = np.isfinite(signal).all(axis=1)
            signal = signal[valid]
            for i in range(0, len(signal) - N + 1, STRIDE):
                windows.append(signal[i:i + N])
                meta.append({"participant": participant_dir.name, "visit": visit_dir.name,
                             "start_timestamp": grid[i], "sensor_mapping": "SA=LB, LF=left_foot, RF=right_foot",
                             "label": 1})
    if not windows:
        raise RuntimeError("No complete LF/RF/SA visits found")
    OUT.mkdir(parents=True, exist_ok=True)
    np.save(OUT / "zenodo_stroke_windows_float32.npy", np.stack(windows))
    pd.DataFrame(meta).to_csv(OUT / "zenodo_stroke_window_metadata.csv", index=False)
    print(f"Wrote {len(windows)} windows from {pd.DataFrame(meta).participant.nunique()} participants")

if __name__ == "__main__":
    main()
