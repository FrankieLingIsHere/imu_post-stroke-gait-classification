"""Frozen older-healthy lower-back external specificity audit.

This script evaluates the existing lower-back checkpoint only.  It uses the
Terrier/Piergiovanni triaxial-accelerometer release's normal corridor-walking
lumbar recordings, resampled from the documented 256 Hz source rate to the
checkpoint's 100 Hz input contract.  It never trains, recalibrates, chooses a
threshold, or changes the three-channel primary model.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import torch
from scipy.signal import resample_poly

from evaluate_carpinella_lower_back_external import LowerBackNet, wilson_interval


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "triaxial_accelerometer" / "extracted"
OUT = ROOT / "data" / "processed"
CHECKPOINT = OUT / "full_expanded_lower_back_only_seed_42.pt"
SOURCE_FS_HZ = 256
TARGET_FS_HZ = 100
WINDOW = 5 * TARGET_FS_HZ
HOP = WINDOW // 2
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def materialize_windows() -> tuple[np.ndarray, pd.DataFrame]:
    """Use normal (not metronome/outdoor) lumbar walking files only."""
    demographics = pd.read_csv(RAW / "_data_old.csv").set_index("ID")
    files = sorted(RAW.glob("*_LB_N_*.csv"))
    assert files, "No normal lower-back files found"
    windows: list[np.ndarray] = []
    records: list[dict[str, object]] = []

    for csv_file in files:
        participant, sensor, condition, direction = csv_file.stem.split("_")
        assert sensor == "LB" and condition == "N"
        raw_g = pd.read_csv(csv_file, header=None).to_numpy(dtype=np.float32)
        assert raw_g.ndim == 2 and raw_g.shape[1] == 3
        assert np.isfinite(raw_g).all(), csv_file.name
        # 100 / 256 reduces exactly to 25 / 64; polyphase filtering avoids
        # aliasing while preserving the recorded continuous walking segment.
        at_target_rate = resample_poly(raw_g, up=25, down=64, axis=0).astype(np.float32)
        magnitude_g = np.linalg.norm(at_target_rate, axis=1)
        for start in range(0, len(magnitude_g) - WINDOW + 1, HOP):
            windows.append(magnitude_g[start : start + WINDOW, None])
            records.append(
                {
                    "window_id": len(records),
                    "dataset_id": "triaxial_accelerometer_older_healthy",
                    "participant_key": f"triaxial_accelerometer::{participant}",
                    "participant_id": participant,
                    "age_years": int(demographics.loc[int(participant), "age"]),
                    "sex_code": int(demographics.loc[int(participant), "sex"]),
                    "label": "healthy",
                    "source_file": csv_file.name,
                    "direction": direction,
                    "start_sample_100hz": start,
                    "window_seconds": WINDOW / TARGET_FS_HZ,
                    "hop_seconds": HOP / TARGET_FS_HZ,
                    "source_sampling_hz": SOURCE_FS_HZ,
                    "model_sampling_hz": TARGET_FS_HZ,
                    "input_unit": "g",
                    "selection_rule": "author-segmented normal corridor walking; lower back only",
                    "resampling": "scipy.signal.resample_poly(up=25, down=64)",
                }
            )

    values = np.asarray(windows, dtype=np.float32)
    metadata = pd.DataFrame(records)
    assert values.shape[0] == len(metadata) and values.shape[1:] == (WINDOW, 1)
    assert np.isfinite(values).all() and metadata.participant_key.nunique() == 59
    return values, metadata


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    windows, metadata = materialize_windows()
    np.save(OUT / "triaxial_older_healthy_lower_back_external_windows_float32.npy", windows)
    metadata.to_csv(OUT / "triaxial_older_healthy_lower_back_external_window_metadata.csv", index=False)

    checkpoint = torch.load(CHECKPOINT, map_location="cpu", weights_only=False)
    model = LowerBackNet().to(DEVICE)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    mean = np.asarray(checkpoint["mean"], dtype=np.float32)
    std = np.maximum(np.asarray(checkpoint["std"], dtype=np.float32), 1e-6)
    normalized = torch.from_numpy(((windows - mean) / std).transpose(0, 2, 1))
    probabilities: list[np.ndarray] = []
    with torch.no_grad():
        for batch in normalized.split(512):
            probabilities.append(torch.sigmoid(model(batch.to(DEVICE))).cpu().numpy())
    metadata["stroke_probability"] = np.concatenate(probabilities)
    metadata.to_csv(OUT / "triaxial_older_healthy_lower_back_external_window_predictions.csv", index=False)

    participants = (
        metadata.groupby(["participant_key", "participant_id", "age_years", "sex_code"], as_index=False)
        .stroke_probability.agg(["mean", "median", "count"])
        .reset_index()
        .rename(columns={"mean": "mean_stroke_probability", "median": "median_stroke_probability", "count": "windows"})
    )
    participants["prediction_at_0_50"] = (participants.mean_stroke_probability >= 0.50).astype(int)
    participants.to_csv(OUT / "triaxial_older_healthy_lower_back_external_participant_predictions.csv", index=False)
    false_positives = int(participants.prediction_at_0_50.sum())
    fpr_low, fpr_high = wilson_interval(false_positives, len(participants))
    summary = pd.DataFrame([{
        "model": checkpoint["strategy"],
        "evaluation": "frozen_external_healthy_only",
        "dataset_id": "triaxial_accelerometer_older_healthy",
        "participants": len(participants),
        "age_min": int(participants.age_years.min()),
        "age_max": int(participants.age_years.max()),
        "windows": len(metadata),
        "window_seconds": WINDOW / TARGET_FS_HZ,
        "hop_seconds": HOP / TARGET_FS_HZ,
        "decision_reference": 0.50,
        "healthy_false_positives": false_positives,
        "healthy_false_positive_rate": false_positives / len(participants),
        "healthy_false_positive_rate_wilson_95_low": fpr_low,
        "healthy_false_positive_rate_wilson_95_high": fpr_high,
        "mean_participant_stroke_probability": participants.mean_stroke_probability.mean(),
        "median_participant_stroke_probability": participants.mean_stroke_probability.median(),
        "device": str(DEVICE),
        "notes": "Frozen healthy-only audit; normal corridor walking only; no fitting, calibration, or threshold tuning.",
    }])
    summary.to_csv(OUT / "triaxial_older_healthy_lower_back_external_audit.csv", index=False)
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
