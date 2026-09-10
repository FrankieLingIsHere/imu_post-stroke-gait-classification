"""Checksum-verified research inference for the selected lower-back ensemble."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
import torch

try:
    from .lower_back_ensemble import LowerBackDomainNet
except ImportError:
    from lower_back_ensemble import LowerBackDomainNet

RELEASE_ID = "stroke-gait-lower-back-ensemble-v0.2.0"
EXPECTED_MEMBERS = {(method, seed) for method in ("erm", "coral", "ermpp_style")
                    for seed in (42, 137, 202, 314, 515)}


def load_bundle(checkpoint: Path, manifest_path: Path) -> dict:
    """The manifest must come from a trusted release, independently of the weight."""
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    digest = hashlib.sha256()
    with checkpoint.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    if manifest.get("release_id") != RELEASE_ID:
        raise ValueError("Manifest is not for the selected lower-back release")
    if digest.hexdigest() != manifest.get("checkpoint_sha256"):
        raise ValueError("Checkpoint checksum mismatch")
    bundle = torch.load(checkpoint, map_location="cpu", weights_only=True)
    validate_bundle(bundle)
    return bundle


def validate_bundle(bundle: dict) -> None:
    if (bundle.get("release_id") != RELEASE_ID or bundle.get("format_version") != 1
            or bundle.get("architecture") != "LowerBackDomainNet"):
        raise ValueError("Unsupported ensemble release or architecture")
    contract = bundle.get("input_contract", {})
    if contract != {"shape": ["windows", 500, 1], "sampling_hz": 100,
                    "duration_seconds": 5, "channel": "lower_back_acceleration_magnitude_g"}:
        raise ValueError("Incompatible lower-back input contract")
    members = bundle.get("members", [])
    if len(members) != 15 or {(m["method"], m["seed"]) for m in members} != EXPECTED_MEMBERS:
        raise ValueError("Expected exactly three methods times five distinct seeds")
    for member in members:
        for name in ("mean", "std"):
            value = torch.as_tensor(member[name])
            if value.numel() != 1 or not torch.isfinite(value).all():
                raise ValueError("Normalization must contain finite scalar values")
        if float(member["std"].item()) <= 0:
            raise ValueError("Normalization standard deviation must be positive")


@torch.inference_mode()
@torch.backends.cudnn.flags(allow_tf32=False)
def predict_windows(bundle: dict, windows: np.ndarray, batch_size: int = 256,
                    device: str = "cpu") -> np.ndarray:
    validate_bundle(bundle)
    values = np.asarray(windows, dtype=np.float32)
    if values.ndim != 3 or values.shape[1:] != (500, 1) or len(values) == 0:
        raise ValueError("Expected nonempty (n_windows, 500, 1) input")
    if not np.isfinite(values).all() or batch_size <= 0:
        raise ValueError("Input must be finite and batch size positive")
    result = np.zeros(len(values), dtype=np.float64)
    for member in bundle["members"]:
        model = LowerBackDomainNet().to(device).eval()
        model.load_state_dict(member["model_state_dict"], strict=True)
        mean = float(member["mean"].item())
        std = max(float(member["std"].item()), 1e-6)
        for start in range(0, len(values), batch_size):
            batch = (values[start:start + batch_size] - mean) / std
            inputs = torch.from_numpy(np.ascontiguousarray(batch.transpose(0, 2, 1)))
            probability = torch.sigmoid(model(inputs.to(device))).cpu().numpy()
            if not np.isfinite(probability).all():
                raise ValueError("Model produced nonfinite probabilities")
            result[start:start + len(probability)] += probability / len(bundle["members"])
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--windows", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--batch-size", type=int, default=256)
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cpu")
    args = parser.parse_args()
    bundle = load_bundle(args.checkpoint, args.manifest)
    smoke = bundle["smoke_test"]
    observed = predict_windows(bundle, smoke["windows"].numpy(), args.batch_size, args.device)
    np.testing.assert_allclose(observed, smoke["expected_probabilities"].numpy(),
                               atol=1e-6, rtol=0)
    probabilities = predict_windows(bundle, np.load(args.windows, allow_pickle=False),
                                    args.batch_size, args.device)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["window_index", "stroke_probability"])
        writer.writerows(enumerate(probabilities))


if __name__ == "__main__":
    main()
