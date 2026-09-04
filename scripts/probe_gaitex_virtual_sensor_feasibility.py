"""Probe GAITEX marker-cluster motion before any virtual-IMU generation.

This is deliberately an audit, not a data-materialisation or model-training
script.  It derives only diagnostic centroid kinematics from the documented
pelvis and bilateral-foot marker clusters during annotated normal gait.  The
pelvis cluster is explicitly *not* renamed or treated as L5/lower back.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.signal import savgol_filter


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "archive" / "raw" / "gaitex_2026" / "data"
OUT = ROOT / "data" / "interim" / "gaitex_2026"
FS_HZ = 100.0
SMOOTHING_SAMPLES = 21  # 210 ms; diagnostic only, never a synthesis setting.
CLUSTERS = {
    "recorded_pelvis_cluster_not_l5": "PELV",
    "left_foot_cluster": "L_FOOT",
    "right_foot_cluster": "R_FOOT",
}


def cluster_columns(prefix: str) -> list[str]:
    return [f"{prefix}{index}_{axis}_[mm]" for index in range(1, 5) for axis in "XYZ"]


def consecutive_runs(mask: np.ndarray) -> list[tuple[int, int]]:
    """Return half-open runs of True frames."""
    changes = np.flatnonzero(np.diff(np.r_[False, mask, False]))
    return [(int(start), int(stop)) for start, stop in changes.reshape(-1, 2)]


def pairwise_distance_cv(points_m: np.ndarray) -> float:
    """Rigid-cluster diagnostic: median coefficient of variation of pair distances."""
    distances = []
    for left in range(4):
        for right in range(left + 1, 4):
            distances.append(np.linalg.norm(points_m[:, left] - points_m[:, right], axis=1))
    stacked = np.asarray(distances)
    medians = np.median(stacked, axis=1)
    valid = medians > 1e-6
    if not valid.any():
        return float("nan")
    return float(np.median(np.std(stacked[valid], axis=1) / medians[valid]))


def summarize_contiguous_motion(points_m: np.ndarray) -> dict[str, float]:
    """Compute ground-frame centroid acceleration diagnostics on valid samples."""
    centroid = points_m.mean(axis=1)
    acceleration = savgol_filter(
        centroid,
        window_length=SMOOTHING_SAMPLES,
        polyorder=3,
        deriv=2,
        delta=1.0 / FS_HZ,
        axis=0,
        mode="interp",
    )
    resultant = np.linalg.norm(acceleration, axis=1)
    return {
        "centroid_acceleration_rms_m_s2": float(np.sqrt(np.mean(resultant**2))),
        "centroid_acceleration_p99_m_s2": float(np.quantile(resultant, 0.99)),
        "centroid_acceleration_max_m_s2": float(np.max(resultant)),
    }


def main() -> None:
    rows: list[dict[str, object]] = []
    for person_dir in sorted(path for path in DATA.iterdir() if path.is_dir()):
        person = person_dir.name
        ng = person_dir / "ng"
        stem = f"{person}_ng"
        timestamp_path = ng / f"timestamps_{stem}.csv"
        marker_path = ng / f"qualisys_marker_data_{stem}.csv"
        imu_path = ng / f"xsens_imu_data_{stem}.csv"
        if not (timestamp_path.exists() and marker_path.exists() and imu_path.exists()):
            continue

        timestamps = pd.read_csv(timestamp_path)
        marker_usecols = ["time_[s]"] + [column for prefix in CLUSTERS.values() for column in cluster_columns(prefix)]
        marker = pd.read_csv(marker_path, usecols=marker_usecols)
        imu_time = pd.read_csv(imu_path, usecols=["time [s]"])["time [s]"].to_numpy(float)
        marker_time = marker["time_[s]"].to_numpy(float)
        time_delta = np.diff(marker_time)

        for segment in timestamps.itertuples(index=False):
            segment_label, start_s, end_s, speed_km_h = segment
            segment_mask = (marker_time >= start_s) & (marker_time <= end_s)
            segment_times = marker_time[segment_mask]
            nearest_imu = np.searchsorted(imu_time, segment_times).clip(1, len(imu_time) - 1)
            left = imu_time[nearest_imu - 1]
            right = imu_time[nearest_imu]
            aligned_imu = np.minimum(np.abs(segment_times - left), np.abs(segment_times - right)) <= 0.002

            for cluster_name, prefix in CLUSTERS.items():
                points = marker.loc[segment_mask, cluster_columns(prefix)].to_numpy(float).reshape(-1, 4, 3) / 1000.0
                per_marker_valid = np.isfinite(points).all(axis=2) & ~np.isclose(points, 0.0).all(axis=2)
                # A pose can be reconstructed from any three non-collinear
                # markers in the documented four-marker sensor cluster.
                marker_valid = per_marker_valid.sum(axis=1) >= 3
                valid = marker_valid & aligned_imu
                runs = [(start, stop) for start, stop in consecutive_runs(valid) if stop - start >= SMOOTHING_SAMPLES]
                motion_stats = []
                rigid_cvs = []
                for run_start, run_stop in runs:
                    run_points = points[run_start:run_stop]
                    motion_stats.append(summarize_contiguous_motion(run_points))
                    rigid_cvs.append(pairwise_distance_cv(run_points))
                row: dict[str, object] = {
                    "participant": person,
                    "segment": segment_label,
                    "speed_km_h": float(speed_km_h),
                    "cluster": cluster_name,
                    "frames": int(len(points)),
                    "marker_complete_fraction": float(marker_valid.mean()),
                    "minimum_visible_markers": int(per_marker_valid.sum(axis=1).min()),
                    "imu_time_aligned_fraction": float(aligned_imu.mean()),
                    "usable_contiguous_frames": int(sum(stop - start for start, stop in runs)),
                    "usable_run_count": int(len(runs)),
                    "rigid_cluster_distance_cv_median": float(np.nanmedian(rigid_cvs)) if rigid_cvs else float("nan"),
                    "centroid_acceleration_rms_m_s2": float(np.median([item["centroid_acceleration_rms_m_s2"] for item in motion_stats])) if motion_stats else float("nan"),
                    "centroid_acceleration_p99_m_s2": float(np.median([item["centroid_acceleration_p99_m_s2"] for item in motion_stats])) if motion_stats else float("nan"),
                    "centroid_acceleration_max_m_s2": float(np.max([item["centroid_acceleration_max_m_s2"] for item in motion_stats])) if motion_stats else float("nan"),
                }
                rows.append(row)

        if not np.allclose(time_delta, 1.0 / FS_HZ, atol=1e-6):
            raise ValueError(f"{person}: marker time base is not consistently 100 Hz")

    audit = pd.DataFrame(rows)
    OUT.mkdir(parents=True, exist_ok=True)
    audit.to_csv(OUT / "virtual_sensor_feasibility.csv", index=False)
    summary = {
        "purpose": "diagnostic marker-cluster feasibility; no virtual IMU or training data produced",
        "participants": int(audit.participant.nunique()),
        "normal_gait_segments": int(audit[["participant", "segment"]].drop_duplicates().shape[0]),
        "cluster_rows": int(len(audit)),
        "all_imu_alignment_at_least_99pct": bool((audit.imu_time_aligned_fraction >= 0.99).all()),
        "all_foot_segments_have_5s_contiguous_motion": bool(
            (audit.loc[audit.cluster != "recorded_pelvis_cluster_not_l5", "usable_contiguous_frames"] >= 500).all()
        ),
        "l5_status": "unresolved: recorded pelvis marker cluster is not accepted as L5/lower back",
        "next_gate": "define a reproducible L5 attachment coordinate and validate virtual proper acceleration/orientation before materialisation",
    }
    (OUT / "virtual_sensor_feasibility_manifest.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(audit.groupby("cluster")[["marker_complete_fraction", "imu_time_aligned_fraction", "usable_contiguous_frames"]].median())
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
