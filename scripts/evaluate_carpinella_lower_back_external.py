"""Frozen healthy-only external audit for the lower-back baseline.

This script never trains, selects a threshold, or modifies the primary model.
It uses author-supplied straight-walking paths from Carpinella et al.'s 6MWT
release, converts acceleration from m/s² to the baseline's canonical g unit,
and reports participant-level stroke false positives at the pre-existing 0.50
model-probability decision reference.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import torch
from scipy.io import loadmat


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "carpinella_2026" / "data"
OUT = ROOT / "data" / "processed"
CHECKPOINT = OUT / "full_expanded_lower_back_only_seed_42.pt"
FS_HZ = 100
WINDOW = 5 * FS_HZ
HOP = WINDOW // 2
MS2_PER_G = 9.80665
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class Block(torch.nn.Module):
    def __init__(self, input_channels: int, output_channels: int = 16):
        super().__init__()
        bottleneck = min(32, input_channels)
        self.b = torch.nn.Conv1d(input_channels, bottleneck, 1, bias=False)
        self.br = torch.nn.ModuleList(
            [
                torch.nn.Conv1d(bottleneck, output_channels, kernel, padding=kernel // 2, bias=False)
                for kernel in (7, 15, 25)
            ]
        )
        self.pool = torch.nn.Conv1d(input_channels, output_channels, 1, bias=False)
        self.bn = torch.nn.BatchNorm1d(output_channels * 4)
        self.res = (
            torch.nn.Conv1d(input_channels, output_channels * 4, 1, bias=False)
            if input_channels != output_channels * 4
            else torch.nn.Identity()
        )

    def forward(self, values: torch.Tensor) -> torch.Tensor:
        bottleneck = self.b(values)
        branches = [branch(bottleneck) for branch in self.br]
        branches.append(self.pool(torch.nn.functional.max_pool1d(values, 3, 1, 1)))
        return torch.nn.functional.gelu(self.bn(torch.cat(branches, dim=1)) + self.res(values))


class LowerBackNet(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.f = torch.nn.Sequential(
            Block(1),
            torch.nn.MaxPool1d(2),
            Block(64),
            torch.nn.AdaptiveAvgPool1d(1),
        )
        self.c = torch.nn.Sequential(torch.nn.Flatten(), torch.nn.Dropout(0.3), torch.nn.Linear(64, 1))

    def forward(self, values: torch.Tensor) -> torch.Tensor:
        return self.c(self.f(values)).squeeze(1)


def wilson_interval(successes: int, total: int, z: float = 1.96) -> tuple[float, float]:
    if total == 0:
        return float("nan"), float("nan")
    proportion = successes / total
    denominator = 1 + z**2 / total
    centre = (proportion + z**2 / (2 * total)) / denominator
    radius = z * np.sqrt(proportion * (1 - proportion) / total + z**2 / (4 * total**2)) / denominator
    return float(max(0.0, centre - radius)), float(min(1.0, centre + radius))


def materialize_windows() -> tuple[np.ndarray, pd.DataFrame]:
    windows: list[np.ndarray] = []
    rows: list[dict[str, object]] = []
    subject_files = sorted(RAW.glob("Subject */Data.mat"), key=lambda item: int(item.parent.name.split()[-1]))
    assert len(subject_files) == 60, f"Expected 60 subjects, found {len(subject_files)}"

    for mat_file in subject_files:
        subject = mat_file.parent.name.replace(" ", "_")
        data = loadmat(mat_file, squeeze_me=True, struct_as_record=False)["Data"]
        for path_index, path in enumerate(data.SegmentedData.Path, start=1):
            acceleration = np.asarray(path.Acc, dtype=np.float32)
            timestamps = np.asarray(path.Time, dtype=np.float64)
            assert acceleration.ndim == 2 and acceleration.shape[1] == 3
            assert len(timestamps) == len(acceleration), (subject, path_index)
            assert np.isfinite(acceleration).all()
            magnitude_g = np.linalg.norm(acceleration, axis=1) / MS2_PER_G
            for start in range(0, len(magnitude_g) - WINDOW + 1, HOP):
                windows.append(magnitude_g[start : start + WINDOW, None])
                rows.append(
                    {
                        "window_id": len(rows),
                        "dataset_id": "carpinella_2026",
                        "participant_key": f"carpinella_2026::{subject}",
                        "participant_id": subject,
                        "label": "healthy",
                        "path_index": path_index,
                        "start_sample": start,
                        "window_seconds": WINDOW / FS_HZ,
                        "hop_seconds": HOP / FS_HZ,
                        "acceleration_unit": "g",
                        "unit_conversion": "SegmentedData.Path.Acc m/s2 / 9.80665",
                        "selection_rule": "author_supplied_straight_walking_path",
                    }
                )

    array = np.asarray(windows, dtype=np.float32)
    metadata = pd.DataFrame(rows)
    assert array.shape[0] == len(metadata) and array.shape[1:] == (WINDOW, 1)
    assert metadata.participant_key.nunique() == 60 and np.isfinite(array).all()
    return array, metadata


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    windows, metadata = materialize_windows()
    np.save(OUT / "carpinella_lower_back_external_windows_float32.npy", windows)
    metadata.to_csv(OUT / "carpinella_lower_back_external_window_metadata.csv", index=False)

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

    participants = (
        metadata.groupby(["participant_key", "participant_id"], as_index=False)
        .stroke_probability.agg(["mean", "median", "count"])
        .reset_index()
        .rename(columns={"mean": "mean_stroke_probability", "median": "median_stroke_probability", "count": "windows"})
    )
    participants["prediction_at_0_50"] = (participants.mean_stroke_probability >= 0.50).astype(int)
    false_positives = int(participants.prediction_at_0_50.sum())
    fpr = false_positives / len(participants)
    fpr_low, fpr_high = wilson_interval(false_positives, len(participants))
    participants.to_csv(OUT / "carpinella_lower_back_external_participant_predictions.csv", index=False)

    summary = pd.DataFrame(
        [
            {
                "model": checkpoint["strategy"],
                "evaluation": "frozen_external_healthy_only",
                "dataset_id": "carpinella_2026",
                "participants": len(participants),
                "windows": len(metadata),
                "window_seconds": WINDOW / FS_HZ,
                "hop_seconds": HOP / FS_HZ,
                "decision_reference": 0.50,
                "healthy_false_positives": false_positives,
                "healthy_false_positive_rate": fpr,
                "healthy_false_positive_rate_wilson_95_low": fpr_low,
                "healthy_false_positive_rate_wilson_95_high": fpr_high,
                "mean_participant_stroke_probability": participants.mean_stroke_probability.mean(),
                "median_participant_stroke_probability": participants.mean_stroke_probability.median(),
                "device": str(DEVICE),
                "notes": "Healthy-only external audit; no AUROC, retraining, calibration, or threshold tuning performed.",
            }
        ]
    )
    summary.to_csv(OUT / "carpinella_lower_back_external_healthy_audit.csv", index=False)
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
