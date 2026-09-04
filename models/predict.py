"""Run research-only inference for the released three-channel gait checkpoint."""

from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path

import numpy as np
import torch

from stroke_gait_inception import StrokeGaitInception

EXPECTED_SHA256 = "5ea8c249814dc80cb478f4a26ac45e6d01248b7df127f1db1caa537a6bd0d02d"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--windows", type=Path, required=True, help=".npy array with shape (n, 500, 3) in LB/LF/RF order")
    parser.add_argument("--output", type=Path, required=True, help="CSV path for window-level research probabilities")
    parser.add_argument("--device", default="cpu", choices=("cpu", "cuda"))
    args = parser.parse_args()

    if args.device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA was requested but is not available.")
    if sha256(args.checkpoint) != EXPECTED_SHA256:
        raise RuntimeError("Checkpoint SHA-256 does not match stroke-gait-inception-v0.1.0.")

    windows = np.load(args.windows)
    if windows.ndim != 3 or windows.shape[1:] != (500, 3):
        raise ValueError(f"Expected windows with shape (n, 500, 3), got {windows.shape}.")
    if not np.isfinite(windows).all():
        raise ValueError("Input contains NaN or infinite values.")

    # The release checkpoint contains NumPy normalisation arrays; load only a
    # checksum-verified checkpoint obtained from the official release location.
    checkpoint = torch.load(args.checkpoint, map_location="cpu", weights_only=False)
    mean = np.asarray(checkpoint["mean"], dtype=np.float32)
    std = np.maximum(np.asarray(checkpoint["std"], dtype=np.float32), 1e-6)
    inputs = torch.from_numpy(((windows.astype(np.float32) - mean) / std).transpose(0, 2, 1))

    model = StrokeGaitInception()
    model.load_state_dict(checkpoint["model_state_dict"], strict=True)
    model.to(args.device).eval()
    with torch.inference_mode():
        probabilities = torch.sigmoid(model(inputs.to(args.device))).cpu().numpy()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("window_index", "stroke_probability"))
        writer.writeheader()
        writer.writerows(
            {"window_index": index, "stroke_probability": float(probability)}
            for index, probability in enumerate(probabilities)
        )
    print(f"Wrote {len(probabilities)} research probabilities to {args.output}")


if __name__ == "__main__":
    main()

