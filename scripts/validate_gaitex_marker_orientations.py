"""Validate GAITEX target marker-plate orientations against Xsens orientation.

The calculation follows the public GAITEX reference implementation's essential
steps: reconstruct a plate frame from the first three listed markers, rotate
the raw Xsens frame into OpenSim coordinates, and apply a heading correction at
the static alignment instant.  This validates the documented pelvis/foot plate
motion only.  It does not define the pelvis plate as L5 or generate IMU data.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.spatial.transform import Rotation


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "archive" / "raw" / "gaitex_2026" / "data"
OUT = ROOT / "data" / "interim" / "gaitex_2026"
TARGETS = {
    "recorded_pelvis_plate_not_l5": "pelvis",
    "left_foot_plate": "calcn_l",
    "right_foot_plate": "calcn_r",
}
IMU_TO_OPENSIM = Rotation.from_euler("x", -90.0, degrees=True)


def read_trc(path: Path) -> pd.DataFrame:
    """Read GAITEX's publisher-prepared OpenSim-coordinate TRC file.

    This follows the public `processing.helper_fcts.read_trc_file` convention.
    The source's raw Qualisys CSV uses a different global coordinate convention
    and must not be compared directly to segment-registered Xsens orientation.
    """
    lines = path.read_text(encoding="utf-8").splitlines()
    markers = [item for item in lines[3].split("\t") if item not in {"Frame#", "Time", ""}]
    columns = ["Time"] + [f"{marker}_{axis}" for marker in markers for axis in ("x", "y", "z")]
    records = [line.split("\t")[1:] for line in lines[5:] if line.strip()]
    return pd.DataFrame(records, columns=columns).astype(float)


def marker_xyz(frame: pd.DataFrame, marker: str) -> np.ndarray:
    return frame[[f"{marker}_{axis}" for axis in ("x", "y", "z")]].to_numpy(float) / 1000.0


def valid_marker_rows(points: list[np.ndarray]) -> np.ndarray:
    stacked = np.stack(points, axis=1)
    return np.isfinite(stacked).all(axis=(1, 2)) & ~np.isclose(stacked, 0.0).all(axis=2).any(axis=1)


def plate_rotation(first: np.ndarray, second: np.ndarray, third: np.ndarray) -> Rotation:
    """Reconstruct the marker-plate orientation as in GAITEX's public script."""
    x_axis = first - second
    y_axis = third - second
    z_axis = np.cross(x_axis, y_axis)
    x_axis /= np.linalg.norm(x_axis, axis=1, keepdims=True)
    y_axis /= np.linalg.norm(y_axis, axis=1, keepdims=True)
    z_axis /= np.linalg.norm(z_axis, axis=1, keepdims=True)
    frames = np.stack([x_axis, y_axis, z_axis], axis=2)
    return Rotation.from_matrix(frames)


def nearest_indices(reference_time: np.ndarray, query_time: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    right = np.searchsorted(reference_time, query_time).clip(1, len(reference_time) - 1)
    left = right - 1
    choose_right = np.abs(reference_time[right] - query_time) < np.abs(reference_time[left] - query_time)
    indices = np.where(choose_right, right, left)
    return indices, np.abs(reference_time[indices] - query_time)


def main() -> None:
    rows: list[dict[str, object]] = []
    for person_dir in sorted(path for path in DATA.iterdir() if path.is_dir()):
        person = person_dir.name
        ng = person_dir / "ng"
        stem = f"{person}_ng"
        paths = {
            "metadata": ng / f"metadata_{stem}.json",
            "markers": ng / "ik_imus" / f"marker_data_osim_format_{stem}.trc",
            "imu": ng / f"xsens_imu_data_{stem}.csv",
            "segments": ng / f"timestamps_{stem}.csv",
        }
        if not all(path.exists() for path in paths.values()):
            continue
        metadata = json.loads(paths["metadata"].read_text(encoding="utf-8"))
        start_ts = float(metadata.get("start_ts", 0.0))
        target_info = {label: metadata["inverse_kinematics"][segment] for label, segment in TARGETS.items()}
        markers = read_trc(paths["markers"])
        markers = markers.loc[markers["Time"] >= start_ts].reset_index(drop=True)
        imu = pd.read_csv(paths["imu"])
        imu = imu.loc[imu["time [s]"] >= start_ts].reset_index(drop=True)
        marker_time = markers["Time"].to_numpy(float)
        imu_time = imu["time [s]"].to_numpy(float)
        matched_imu, mismatch = nearest_indices(imu_time, marker_time)
        segments = pd.read_csv(paths["segments"])

        for plate, info in target_info.items():
            names = info["marker_names"][:3]
            points = [marker_xyz(markers, name) for name in names]
            valid = valid_marker_rows(points) & (mismatch <= 0.002)
            if not valid.any():
                continue
            first_valid = int(np.flatnonzero(valid)[0])
            marker_orientation = plate_rotation(*(point[valid] for point in points))
            quaternion_columns = [f'{info["imu_name"]}_{component}' for component in ("QX", "QY", "QZ", "QW")]
            xsens_orientation = Rotation.from_quat(imu.loc[matched_imu[valid], quaternion_columns].to_numpy(float))
            xsens_opensim = IMU_TO_OPENSIM * xsens_orientation

            # Use GAITEX's heading-only registration at the first valid static-alignment frame.
            initial_marker_orientation = plate_rotation(*(point[first_valid:first_valid + 1] for point in points))
            initial_xsens = IMU_TO_OPENSIM * Rotation.from_quat(
                imu.loc[[matched_imu[first_valid]], quaternion_columns].to_numpy(float)
            )
            heading_delta = (initial_marker_orientation * initial_xsens.inv()).as_euler("yxz", degrees=True)[0, 0]
            registered_xsens = Rotation.from_euler("y", heading_delta, degrees=True) * xsens_opensim
            deviation_deg = np.linalg.norm((marker_orientation * registered_xsens.inv()).as_rotvec(degrees=True), axis=1)
            valid_times = marker_time[valid]

            for segment in segments.itertuples(index=False):
                label, start_s, end_s, speed_km_h = segment
                in_segment = (valid_times >= start_s) & (valid_times <= end_s)
                if not in_segment.any():
                    continue
                values = deviation_deg[in_segment]
                rows.append(
                    {
                        "participant": person,
                        "segment": label,
                        "speed_km_h": float(speed_km_h),
                        "plate": plate,
                        "valid_frames": int(len(values)),
                        "marker_imu_time_mismatch_p99_ms": float(np.quantile(mismatch[valid][in_segment], 0.99) * 1000.0),
                        "orientation_deviation_median_deg": float(np.median(values)),
                        "orientation_deviation_p95_deg": float(np.quantile(values, 0.95)),
                        "orientation_deviation_p99_deg": float(np.quantile(values, 0.99)),
                        "orientation_deviation_max_deg": float(np.max(values)),
                    }
                )

    result = pd.DataFrame(rows)
    OUT.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUT / "marker_orientation_validation.csv", index=False)
    manifest = {
        "purpose": "validate recorded GAITEX plate orientation only; no virtual L5, acceleration, synthesis, or classifier data produced",
        "participants": int(result.participant.nunique()),
        "segment_plate_rows": int(len(result)),
        "reference_method": "GAITEX public orientation_deviation_plot.py: marker-plate frame, Xsens-to-OpenSim rotation, heading correction",
        "l5_status": "unresolved: the validated pelvis plate remains pelvis, not a documented L5 attachment",
    }
    (OUT / "marker_orientation_validation_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(result.groupby("plate")[["orientation_deviation_median_deg", "orientation_deviation_p95_deg", "marker_imu_time_mismatch_p99_ms"]].median())
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
