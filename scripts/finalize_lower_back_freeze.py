"""Finish the interrupted 2026-09-08 freeze without retraining any member.

Requires its preserved preprecision checkpoint, tuning/split records and source
snapshot. Refuses an existing manifest. Only smoke metadata changes in the bundle.
"""
from pathlib import Path
import json
import sys
from dataclasses import asdict

import numpy as np
import pandas as pd
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from models.predict_lower_back import predict_windows, validate_bundle, RELEASE_ID
from src.models.freeze_lower_back_ensemble import FreezeConfig, sha256, state_sha256, SELECTION_EVIDENCE
from src.models.evidence_gated_domain_generalization import load_development_data


def main():
    torch.set_num_threads(4)
    directory = ROOT / "models/checkpoints"
    checkpoint = directory / f"{RELEASE_ID}.pt"
    manifest_path = directory / f"{RELEASE_ID}.manifest.json"
    if manifest_path.exists():
        raise FileExistsError(manifest_path)
    original = directory / f"{RELEASE_ID}.preprecision.pt"
    bundle = torch.load(original, map_location="cpu", weights_only=True)
    validate_bundle(bundle)
    smoke = bundle["smoke_test"]
    windows = smoke["windows"].numpy()
    cpu = predict_windows(bundle, windows)
    gpu = predict_windows(bundle, windows, device="cuda")
    np.testing.assert_allclose(cpu, gpu, atol=1e-6, rtol=0)
    original_smoke_error = float(np.max(np.abs(cpu - smoke["expected_probabilities"].numpy())))
    smoke["expected_probabilities"] = torch.tensor(cpu, dtype=torch.float32)
    bundle["inference_precision"] = "float32; cuDNN TF32 disabled"
    torch.save(bundle, checkpoint)
    reloaded = torch.load(checkpoint, map_location="cpu", weights_only=True)
    for before, after in zip(bundle["members"], reloaded["members"]):
        for key, value in before["model_state_dict"].items():
            assert torch.equal(value, after["model_state_dict"][key])
    processed = ROOT / "data/processed"
    _, meta = load_development_data(processed)
    inputs = ["validated_acceleration_magnitude_windows_float32.npy", "validated_window_metadata.csv",
              "sint_maartenskliniek_external_windows_float32.npy",
              "sint_maartenskliniek_external_window_metadata.csv",
              "lower_back_release_freeze_participants.csv", "lower_back_release_freeze_tuning.csv"]
    code = ["data/processed/lower_back_freezer_training_snapshot.py",
            "src/models/freeze_lower_back_ensemble.py", "src/models/evidence_gated_domain_generalization.py",
            "models/lower_back_ensemble.py", "models/stroke_gait_inception.py",
            "models/predict_lower_back.py", "scripts/finalize_lower_back_freeze.py"]
    manifest = {
        "release_id": RELEASE_ID, "checkpoint_filename": checkpoint.name,
        "checkpoint_sha256": sha256(checkpoint), "checkpoint_bytes": checkpoint.stat().st_size,
        "selection_evidence": SELECTION_EVIDENCE, "config": asdict(FreezeConfig()),
        "selected_epochs": {m["method"]: m["epochs"] for m in bundle["members"]},
        "members": [{"method": m["method"], "seed": m["seed"], "epochs": m["epochs"],
                     "state_sha256": state_sha256(m["model_state_dict"])} for m in bundle["members"]],
        "development_participants": int(meta["group"].nunique()), "development_windows": len(meta),
        "development_sources": sorted(meta["source"].unique().tolist()),
        "input_sha256": {name: sha256(processed / name) for name in inputs},
        "code_sha256": {name: sha256(ROOT / name) for name in code},
        "software": {"python": sys.version.split()[0], "torch": torch.__version__,
                     "numpy": np.__version__, "pandas": pd.__version__,
                     "scikit_learn": __import__("sklearn").__version__,
                     "cuda_device": torch.cuda.get_device_name(0)},
        "smoke_test_maximum_absolute_error": float(np.max(np.abs(cpu-gpu))),
        "recovery": {"original_checkpoint_sha256": sha256(original),
                     "original_tf32_smoke_error": original_smoke_error,
                     "weights_retrained": False, "changed": "smoke expectations and inference precision metadata only"},
        "external_cohorts_loaded": False,
        "performance_claim": "None: full-development fit, not unbiased evaluation."}
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({"checkpoint_sha256": manifest["checkpoint_sha256"],
                      "smoke_error": manifest["smoke_test_maximum_absolute_error"]}, indent=2))


if __name__ == "__main__":
    main()
