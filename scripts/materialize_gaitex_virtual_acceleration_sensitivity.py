"""Create a non-training sensitivity set of GAITEX virtual acceleration magnitudes.

Each signal is derived from the centre of a documented rigid marker plate during
annotated normal gait.  Position is smoothed and differentiated twice, then
gravity is restored to obtain global-frame specific force.  Magnitude is
rotation-invariant, matching the project's three-channel magnitude input form.

The first channel remains explicitly named ``pelvis_proxy_not_l5``.  Outputs
are for physics/adapter feasibility only, never direct binary pooling or claims
of additional recruited healthy participants.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.signal import savgol_filter


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "archive" / "raw" / "gaitex_2026" / "data"
OUT = ROOT / "data" / "interim" / "gaitex_2026" / "virtual_acceleration_sensitivity"
FS_HZ = 100.0
WINDOW_SAMPLES = 500
GRAVITY_M_S2 = np.array([0.0, -9.80665, 0.0])  # OpenSim/GAITEX TRC frame: +Y is vertical.
WINDOWS = (11, 21, 31)  # 110, 210, and 310 ms; selection is deferred to the audit.
CLUSTERS = {
    "pelvis_proxy_not_l5": "PELV",
    "left_foot": "L_FOOT",
    "right_foot": "R_FOOT",
}


def cluster_columns(prefix: str) -> list[str]:
    return [f"{prefix}{index}_{axis}_[mm]" for index in range(1, 5) for axis in "XYZ"]


def contiguous_runs(mask: np.ndarray) -> list[tuple[int, int]]:
    edges = np.flatnonzero(np.diff(np.r_[False, mask, False]))
    return [(int(start), int(stop)) for start, stop in edges.reshape(-1, 2)]


def plate_centres(marker: pd.DataFrame, prefix: str) -> tuple[np.ndarray, np.ndarray]:
    """Return plate centres (m) and frames with all four cluster markers present."""
    points = marker[cluster_columns(prefix)].to_numpy(float).reshape(-1, 4, 3) / 1000.0
    marker_valid = np.isfinite(points).all(axis=2) & ~np.isclose(points, 0.0).all(axis=2)
    frame_valid = marker_valid.all(axis=1)
    return points.mean(axis=1), frame_valid


def proper_acceleration_magnitude(position_m: np.ndarray, smoothing_samples: int) -> np.ndarray:
    linear_acceleration = savgol_filter(
        position_m,
        window_length=smoothing_samples,
        polyorder=3,
        deriv=2,
        delta=1.0 / FS_HZ,
        axis=0,
        mode="interp",
    )
    specific_force = linear_acceleration - GRAVITY_M_S2
    return np.linalg.norm(specific_force, axis=1)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    variants: dict[int, list[np.ndarray]] = {window: [] for window in WINDOWS}
    metadata_rows: dict[int, list[dict[str, object]]] = {window: [] for window in WINDOWS}
    diagnostics: list[dict[str, object]] = []
    for person_dir in sorted(path for path in DATA.iterdir() if path.is_dir()):
        person = person_dir.name
        ng = person_dir / "ng"
        stem = f"{person}_ng"
        marker_path = ng / f"qualisys_marker_data_{stem}.csv"
        timestamps_path = ng / f"timestamps_{stem}.csv"
        if not (marker_path.exists() and timestamps_path.exists()):
            continue
        usecols = ["time_[s]"] + [column for prefix in CLUSTERS.values() for column in cluster_columns(prefix)]
        marker = pd.read_csv(marker_path, usecols=usecols)
        times = marker["time_[s]"].to_numpy(float)
        segments = pd.read_csv(timestamps_path)
        centres, validity = zip(*(plate_centres(marker, prefix) for prefix in CLUSTERS.values()))
        valid_all = np.logical_and.reduce(validity)

        for segment in segments.itertuples(index=False):
            segment_label, start_s, end_s, speed_km_h = segment
            segment_mask = (times >= start_s) & (times <= end_s)
            selected = np.flatnonzero(segment_mask)
            if not len(selected):
                continue
            local_valid = valid_all[selected]
            for run_start, run_stop in contiguous_runs(local_valid):
                global_start = selected[run_start]
                global_stop = selected[run_stop - 1] + 1
                run_length = global_stop - global_start
                if run_length < WINDOW_SAMPLES:
                    continue
                positions = np.stack([centre[global_start:global_stop] for centre in centres], axis=1)
                for smoothing in WINDOWS:
                    magnitude = np.stack(
                        [proper_acceleration_magnitude(positions[:, channel], smoothing) for channel in range(3)],
                        axis=1,
                    ).astype(np.float32)
                    diagnostics.append(
                        {
                            "participant": person,
                            "segment": segment_label,
                            "speed_km_h": float(speed_km_h),
                            "smoothing_samples": smoothing,
                            "frames": run_length,
                            "pelvis_magnitude_median_g": float(np.median(magnitude[:, 0]) / 9.80665),
                            "left_foot_magnitude_p99_g": float(np.quantile(magnitude[:, 1], 0.99) / 9.80665),
                            "right_foot_magnitude_p99_g": float(np.quantile(magnitude[:, 2], 0.99) / 9.80665),
                        }
                    )
                    for offset in range(0, run_length - WINDOW_SAMPLES + 1, WINDOW_SAMPLES):
                        variants[smoothing].append(magnitude[offset:offset + WINDOW_SAMPLES])
                        metadata_rows[smoothing].append(
                            {
                                "participant": f"gaitex_2026_{person}",
                                "source_participant": person,
                                "segment": segment_label,
                                "speed_km_h": float(speed_km_h),
                                "run_start_time_s": float(times[global_start + offset]),
                                "smoothing_samples": smoothing,
                                "channel_contract": "pelvis_proxy_not_l5,left_foot,right_foot",
                                "eligible_for_binary_training": False,
                            }
                        )

    summary_rows = []
    for smoothing in WINDOWS:
        windows = np.stack(variants[smoothing]).astype(np.float32)
        metadata = pd.DataFrame(metadata_rows[smoothing])
        np.save(OUT / f"gaitex_virtual_proper_acceleration_magnitude_savgol_{smoothing}.npy", windows)
        metadata.to_csv(OUT / f"gaitex_virtual_proper_acceleration_magnitude_savgol_{smoothing}_metadata.csv", index=False)
        summary_rows.append(
            {
                "smoothing_samples": smoothing,
                "smoothing_ms": smoothing * 10,
                "windows": int(len(windows)),
                "participants": int(metadata.participant.nunique()),
                "median_pelvis_proxy_g": float(np.median(windows[:, :, 0]) / 9.80665),
                "p99_left_foot_g": float(np.quantile(windows[:, :, 1], 0.99) / 9.80665),
                "p99_right_foot_g": float(np.quantile(windows[:, :, 2], 0.99) / 9.80665),
            }
        )
    pd.DataFrame(diagnostics).to_csv(OUT / "segment_diagnostics.csv", index=False)
    summary = pd.DataFrame(summary_rows)
    summary.to_csv(OUT / "summary.csv", index=False)
    manifest = {
        "purpose": "virtual proper-acceleration sensitivity analysis only; no classifier training or direct pooling",
        "source": "GAITEX annotated normal gait, marker-plate centres",
        "channels": ["pelvis_proxy_not_l5", "left_foot", "right_foot"],
        "calculation": "Savitzky-Golay second derivative of plate-centre position, followed by gravity restoration and magnitude",
        "smoothing_variants": list(WINDOWS),
        "next_gate": "inspect smoothing sensitivity and compare only through a fold-fitted source-aware adapter/pretraining experiment",
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(summary.to_string(index=False))
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
