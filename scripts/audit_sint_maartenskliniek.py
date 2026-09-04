"""Audit Sint Maartenskliniek raw Xsens exports before model use.

This script does not fit a model and does not create training labels beyond
the public folder-level CVA/healthy-control labels.
"""
from pathlib import Path
import re
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/raw/sint_maartenskliniek/extracted/IMU_GaitAnalysis-1.1.0/data"
OUT = ROOT / "data/processed/sint_maartenskliniek_export_audit.csv"
SENSORS = {
    "leftfoot": "00B40AC5.txt",
    "rightfoot": "00B40A23.txt",
    "lumbar": "00B40A8D.txt",
}


def read_sensor(path: Path) -> tuple[pd.DataFrame, dict]:
    lines = path.read_text(errors="replace").splitlines()
    header_idx = next(i for i, line in enumerate(lines) if line.startswith("PacketCounter\t"))
    meta = {}
    for line in lines[:header_idx]:
        if line.startswith("//") and ":" in line:
            key, value = line[2:].split(":", 1)
            meta[key.strip()] = value.strip()
    frame = pd.read_csv(path, sep="\t", skiprows=header_idx)
    return frame, meta


def main() -> None:
    rows = []
    for label, parent in [("stroke", DATA / "CVA"), ("healthy", DATA / "Healthy_controls")]:
        for participant_dir in sorted(parent.glob("900_*")):
            xsens = participant_dir / "Xsens"
            for trial_dir in sorted(xsens.glob("exported*")):
                sensor_paths = {
                    name: next(iter(trial_dir.glob(f"*_{filename}")), trial_dir / filename)
                    for name, filename in SENSORS.items()
                }
                present = {name: path.exists() for name, path in sensor_paths.items()}
                if not any(present.values()):
                    continue
                row = {
                    "dataset": "sint_maartenskliniek",
                    "participant": participant_dir.name,
                    "label": label,
                    "trial": trial_dir.name,
                    "complete_lb_lf_rf": all(present.values()),
                    **{f"has_{name}": value for name, value in present.items()},
                }
                for name, path in sensor_paths.items():
                    if not path.exists():
                        continue
                    try:
                        frame, meta = read_sensor(path)
                        acc = frame[["Acc_X", "Acc_Y", "Acc_Z"]].apply(pd.to_numeric, errors="coerce").to_numpy()
                        finite = np.isfinite(acc).all(axis=1)
                        row[f"{name}_rows"] = len(frame)
                        row[f"{name}_finite_fraction"] = float(finite.mean()) if len(finite) else 0.0
                        row[f"{name}_acc_abs_max"] = float(np.nanmax(np.abs(acc))) if finite.any() else np.nan
                        row[f"{name}_acc_mag_median"] = float(np.nanmedian(np.linalg.norm(acc, axis=1))) if finite.any() else np.nan
                        row[f"{name}_device"] = meta.get("DeviceId", "")
                    except Exception as exc:  # preserve the failing file in the audit
                        row[f"{name}_error"] = type(exc).__name__
                rows.append(row)
    audit = pd.DataFrame(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    audit.to_csv(OUT, index=False)
    print(f"Wrote {OUT}")
    print("Participants:", audit.participant.nunique())
    print(audit.groupby(["label", "complete_lb_lf_rf"]).participant.nunique())
    print("Complete trials:", int(audit.complete_lb_lf_rf.sum()))
    print("Rows per complete trial:")
    print(audit.loc[audit.complete_lb_lf_rf, ["label", "lumbar_rows", "leftfoot_rows", "rightfoot_rows"]].describe())


if __name__ == "__main__":
    main()
