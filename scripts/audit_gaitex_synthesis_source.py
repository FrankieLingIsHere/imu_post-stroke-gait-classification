"""Audit GAITEX as a physics-grounded virtual-IMU synthesis source.

This script intentionally does not generate accelerations or map pelvis to lower
back.  It establishes whether normal-gait motion and the required foot/pelvis
assets exist before a documented virtual-sensor placement model is selected.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "archive" / "raw" / "gaitex_2026" / "data"
OUT = ROOT / "data" / "interim" / "gaitex_2026"


def marker_columns(columns: list[str]) -> list[str]:
    required_prefixes = ("PELV", "L_FOOT", "R_FOOT")
    return ["time_[s]"] + [c for c in columns if c.startswith(required_prefixes)]


def main() -> None:
    rows: list[dict[str, object]] = []
    for person_dir in sorted(p for p in DATA.iterdir() if p.is_dir()):
        ng = person_dir / "ng"
        stem = f"{person_dir.name}_ng"
        timestamp_path = ng / f"timestamps_{stem}.csv"
        metadata_path = ng / f"metadata_{stem}.json"
        marker_path = ng / f"qualisys_marker_data_{stem}.csv"
        imu_path = ng / f"xsens_imu_data_{stem}.csv"
        required = [timestamp_path, metadata_path, marker_path, imu_path]
        exists = all(p.exists() for p in required)
        row: dict[str, object] = {
            "participant_key": f"gaitex_2026_{person_dir.name}",
            "participant": person_dir.name,
            "normal_gait_assets_complete": exists,
            "sampling_hz": np.nan,
            "normal_gait_segments": 0,
            "speed_min_km_h": np.nan,
            "speed_max_km_h": np.nan,
            "pelvis_sensor": False,
            "left_foot_sensor": False,
            "right_foot_sensor": False,
            "marker_interval_completeness": np.nan,
            "needs_segment_level_marker_qc": False,
            "direct_three_channel_inference_eligible": False,
            "virtual_synthesis_candidate": False,
            "reason": "",
        }
        if not exists:
            row["reason"] = "missing normal-gait timestamp, metadata, marker, or IMU orientation file"
            rows.append(row)
            continue

        timestamps = pd.read_csv(timestamp_path)
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        imu_header = pd.read_csv(imu_path, nrows=0).columns.tolist()
        mapping = metadata.get("inverse_kinematics", {})
        sensors = {value.get("imu_name") for value in mapping.values()}
        row["normal_gait_segments"] = len(timestamps)
        row["speed_min_km_h"] = float(timestamps["velocities_[km_h]"].min())
        row["speed_max_km_h"] = float(timestamps["velocities_[km_h]"].max())
        row["pelvis_sensor"] = "XSens_Pelvis" in sensors
        row["left_foot_sensor"] = "XSens_Foot_Left" in sensors
        row["right_foot_sensor"] = "XSens_Foot_Right" in sensors
        row["sampling_hz"] = 100.0  # GAITEX release acquisition rate; confirm from its 0.01-s time base.
        marker_header = pd.read_csv(marker_path, nrows=0).columns.tolist()
        columns = marker_columns(marker_header)
        marker = pd.read_csv(marker_path, usecols=columns)
        in_gait = np.zeros(len(marker), dtype=bool)
        for interval in timestamps.itertuples(index=False):
            in_gait |= (marker["time_[s]"] >= interval[1]) & (marker["time_[s]"] <= interval[2])
        values = marker.loc[in_gait, [c for c in columns if c != "time_[s]"]].to_numpy(float)
        # A missing Qualisys marker is an all-zero XYZ triplet.  A single zero
        # coordinate is a valid physical position and must not reject a frame.
        marker_xyz = values.reshape(-1, len(values[0]) // 3, 3)
        marker_valid = np.isfinite(marker_xyz).all(axis=2) & ~np.isclose(marker_xyz, 0.0).all(axis=2)
        # Each documented rigid sensor cluster has four markers.  Three valid
        # non-collinear markers are sufficient to reconstruct a cluster pose;
        # demanding all four would discard otherwise usable motion.
        cluster_usable = marker_valid.reshape(-1, 3, 4).sum(axis=2) >= 3
        row["marker_interval_completeness"] = float(cluster_usable.all(axis=1).mean())
        has_orientation = all(any(c.startswith(f"{sensor}_Q") for c in imu_header) for sensor in ("XSens_Pelvis", "XSens_Foot_Left", "XSens_Foot_Right"))
        if bool(row["pelvis_sensor"] and row["left_foot_sensor"] and row["right_foot_sensor"] and has_orientation):
            row["virtual_synthesis_candidate"] = True
            row["needs_segment_level_marker_qc"] = bool(row["marker_interval_completeness"] < 0.99)
            if row["needs_segment_level_marker_qc"]:
                row["reason"] = "normal-gait assets complete with local marker loss; retain only marker-complete windows; pelvis-to-L5 virtual placement remains mandatory"
            else:
                row["reason"] = "normal-gait motion assets complete; raw release supplies orientation/markers, not acceleration; pelvis-to-L5 virtual placement remains mandatory"
        else:
            row["reason"] = "required orientation, marker, or normal-gait asset is incomplete"
        rows.append(row)

    audit = pd.DataFrame(rows)
    OUT.mkdir(parents=True, exist_ok=True)
    audit.to_csv(OUT / "audit.csv", index=False)
    manifest = {
        "dataset_id": "gaitex_2026",
        "participants": int(len(audit)),
        "normal_gait_participants": int(audit.normal_gait_assets_complete.sum()),
        "virtual_synthesis_candidates": int(audit.virtual_synthesis_candidate.sum()),
        "participants_needing_segment_level_marker_qc": int(audit.needs_segment_level_marker_qc.sum()),
        "contract": {
            "normal_gait": "three annotated treadmill-speed intervals per participant",
            "motion": "100-Hz marker trajectories and Xsens orientation quaternions",
            "feet": "documented left/right foot IMUs",
            "trunk": "documented pelvis IMU; not accepted as lower back for direct inference",
        },
        "decision": "candidate for physics-grounded virtual acceleration synthesis only; excluded from direct binary pooling and frozen external testing",
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(audit.to_string(index=False))
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
