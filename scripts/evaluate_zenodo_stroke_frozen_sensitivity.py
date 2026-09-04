"""Frozen, stroke-only external sensitivity audit for the two saved baselines.

Zenodo rehabilitation data contains no healthy controls. Consequently this
script reports only participant-level true-positive / false-negative rates at
the pre-existing 0.50 reference; it deliberately does not compute AUROC,
calibrate either model, or pool these people with the Carpinella healthy cohort.
"""

from pathlib import Path
import sys

import numpy as np
import pandas as pd
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from evaluate_carpinella_lower_back_external import LowerBackNet, wilson_interval
from train_sint_sensitivity_inception import Net as ThreeChannelNet


OUT = ROOT / "data" / "processed"
WINDOWS = OUT / "zenodo_benchmark_acceleration_magnitude_windows_float32.npy"
METADATA = OUT / "zenodo_benchmark_magnitude_metadata.csv"
THREE_CHANNEL_CHECKPOINT = OUT / "full_expanded_inception_prototype_seed_42.pt"
LOWER_BACK_CHECKPOINT = OUT / "full_expanded_lower_back_only_seed_42.pt"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def predict(model: torch.nn.Module, values: np.ndarray, mean: np.ndarray, std: np.ndarray) -> np.ndarray:
    normalized = torch.from_numpy(((values - mean) / np.maximum(std, 1e-6)).transpose(0, 2, 1).astype("float32"))
    model.eval()
    outputs: list[np.ndarray] = []
    with torch.no_grad():
        for batch in normalized.split(512):
            outputs.append(torch.sigmoid(model(batch.to(DEVICE))).cpu().numpy())
    return np.concatenate(outputs)


def summarise(name: str, metadata: pd.DataFrame, probabilities: np.ndarray) -> tuple[pd.DataFrame, dict[str, object]]:
    participant_predictions = metadata[["participant", "visit"]].copy()
    participant_predictions["stroke_probability"] = probabilities
    participant_predictions = (
        participant_predictions.groupby("participant", as_index=False)
        .stroke_probability.agg(["mean", "median", "count"])
        .reset_index()
        .rename(columns={"mean": "mean_stroke_probability", "median": "median_stroke_probability", "count": "windows"})
    )
    participant_predictions["prediction_at_0_50"] = (participant_predictions.mean_stroke_probability >= 0.50).astype(int)
    true_positives = int(participant_predictions.prediction_at_0_50.sum())
    sensitivity = true_positives / len(participant_predictions)
    low, high = wilson_interval(true_positives, len(participant_predictions))
    return participant_predictions, {
        "model": name,
        "evaluation": "frozen_external_stroke_only",
        "dataset_id": "zenodo_stroke_rehab",
        "participants": len(participant_predictions),
        "windows": len(metadata),
        "decision_reference": 0.50,
        "stroke_true_positives": true_positives,
        "stroke_false_negatives": len(participant_predictions) - true_positives,
        "stroke_sensitivity": sensitivity,
        "stroke_sensitivity_wilson_95_low": low,
        "stroke_sensitivity_wilson_95_high": high,
        "mean_participant_stroke_probability": participant_predictions.mean_stroke_probability.mean(),
        "median_participant_stroke_probability": participant_predictions.mean_stroke_probability.median(),
        "device": str(DEVICE),
        "notes": "Stroke-only external audit; no AUROC, specificity, retraining, calibration, or threshold tuning performed.",
    }


def main() -> None:
    windows = np.load(WINDOWS)
    metadata = pd.read_csv(METADATA)
    assert windows.shape == (len(metadata), 500, 3) and np.isfinite(windows).all()
    assert metadata.participant.nunique() == 10 and set(metadata.label) == {1}

    three_checkpoint = torch.load(THREE_CHANNEL_CHECKPOINT, map_location="cpu", weights_only=False)
    three_model = ThreeChannelNet().to(DEVICE)
    three_model.load_state_dict(three_checkpoint["model_state_dict"])
    three_probabilities = predict(
        three_model,
        windows,
        np.asarray(three_checkpoint["mean"], dtype="float32"),
        np.asarray(three_checkpoint["std"], dtype="float32"),
    )
    three_people, three_summary = summarise(three_checkpoint["strategy"], metadata, three_probabilities)
    three_people.to_csv(OUT / "zenodo_stroke_three_channel_participant_predictions.csv", index=False)

    lower_checkpoint = torch.load(LOWER_BACK_CHECKPOINT, map_location="cpu", weights_only=False)
    lower_model = LowerBackNet().to(DEVICE)
    lower_model.load_state_dict(lower_checkpoint["model_state_dict"])
    lower_probabilities = predict(
        lower_model,
        windows[:, :, :1],
        np.asarray(lower_checkpoint["mean"], dtype="float32"),
        np.asarray(lower_checkpoint["std"], dtype="float32"),
    )
    lower_people, lower_summary = summarise(lower_checkpoint["strategy"], metadata, lower_probabilities)
    lower_people.to_csv(OUT / "zenodo_stroke_lower_back_participant_predictions.csv", index=False)

    summary = pd.DataFrame([three_summary, lower_summary])
    summary.to_csv(OUT / "zenodo_stroke_frozen_sensitivity_audit.csv", index=False)
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
