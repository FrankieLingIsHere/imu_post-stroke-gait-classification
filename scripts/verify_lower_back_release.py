"""Verify saved lower-back weights against training inference on development data only."""
from pathlib import Path
import json
import subprocess
import sys

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from models.predict_lower_back import RELEASE_ID, load_bundle, predict_windows
from src.models.evidence_gated_domain_generalization import DomainNet, load_development_data, probabilities


def main():
    torch.set_num_threads(4)
    directory = ROOT / "models/checkpoints"
    checkpoint = directory / f"{RELEASE_ID}.pt"
    manifest = directory / f"{RELEASE_ID}.manifest.json"
    bundle = load_bundle(checkpoint, manifest)
    x, meta = load_development_data(ROOT / "data/processed")
    indices = np.unique(np.concatenate([
        np.asarray(rows)[np.linspace(0, len(rows) - 1, min(16, len(rows)), dtype=int)]
        for rows in meta.groupby(["source", "y"]).indices.values()
    ]))
    windows = x[indices, :, :1]
    reference = []
    for member in bundle["members"]:
        model = DomainNet(1).eval()
        model.load_state_dict(member["model_state_dict"], strict=True)
        reference.append(probabilities(model, x, indices, [0], member["mean"].numpy(),
                                       member["std"].numpy(), torch.device("cpu")))
    expected = np.mean(reference, axis=0)
    errors = {}
    for device in ("cpu", "cuda"):
        observed = predict_windows(bundle, windows, batch_size=17, device=device)
        np.testing.assert_allclose(observed, expected, atol=1e-6, rtol=0)
        errors[device] = float(np.max(np.abs(observed - expected)))
    smoke = bundle["smoke_test"]
    np.testing.assert_allclose(predict_windows(bundle, smoke["windows"].numpy()),
                               smoke["expected_probabilities"].numpy(), atol=1e-6, rtol=0)
    processed = ROOT / "data/processed"
    input_path = processed / "lower_back_release_verification_windows.npy"
    output_path = processed / "lower_back_release_verification_cli.csv"
    np.save(input_path, windows)
    subprocess.run([sys.executable, "-m", "models.predict_lower_back", "--checkpoint",
                    str(checkpoint), "--manifest", str(manifest), "--windows", str(input_path),
                    "--output", str(output_path), "--batch-size", "17"], cwd=ROOT, check=True)
    cli = np.genfromtxt(output_path, delimiter=",", names=True)["stroke_probability"]
    np.testing.assert_allclose(cli, expected, atol=1e-6, rtol=0)
    report = {"release_id": RELEASE_ID, "verified_development_windows": len(indices),
              "member_count": len(bundle["members"]), "maximum_absolute_errors": errors,
              "cli_maximum_absolute_error": float(np.max(np.abs(cli - expected))),
              "smoke_test_passed": True, "external_cohorts_loaded": False,
              "performance_evaluation": False}
    (processed / "lower_back_release_verification.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
