"""Audit the public healthy subset of the Kiel Validation Dataset.

No tensor is materialised and no classifier is run: the release has bilateral
feet but a pelvis sensor, not a documented lower-back sensor.  This script
records that contract boundary explicitly so later work cannot silently map
pelvis to the LB channel.
"""

from pathlib import Path
import json

import numpy as np
import pandas as pd
from scipy.io import loadmat


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "kiel_validation_dataset" / "preferred_walking"
OUT = ROOT / "data" / "interim" / "kiel_validation_dataset"


def main() -> None:
    rows: list[dict[str, object]] = []
    for file in sorted(RAW.glob("pp*_imu_walk_preferred.mat")):
        payload = loadmat(file, squeeze_me=True, struct_as_record=False)["data"]
        locations = [str(item) for item in payload.imu_location]
        acceleration = np.asarray(payload.acc, dtype=np.float32)
        rows.append(
            {
                "dataset_id": "kiel_validation_dataset",
                "participant_id": file.name.split("_")[0],
                "file": file.name,
                "task": "walk_preferred",
                "label": "healthy",
                "sampling_hz": int(payload.fs),
                "acceleration_shape": "x".join(map(str, acceleration.shape)),
                "acceleration_unit": "g",
                "sensor_locations": ";".join(locations),
                "has_left_foot": "left_foot" in locations,
                "has_right_foot": "right_foot" in locations,
                "has_pelvis": "pelvis" in locations,
                "has_documented_lower_back": False,
                "three_channel_contract_status": "ineligible: pelvis is not a documented lower-back placement",
                "direct_model_role": "none; do not pool or infer",
            }
        )
    audit = pd.DataFrame(rows)
    assert len(audit) == 10 and audit.has_left_foot.all() and audit.has_right_foot.all()
    assert audit.has_pelvis.all() and not audit.has_documented_lower_back.any()
    OUT.mkdir(parents=True, exist_ok=True)
    audit.to_csv(OUT / "audit.csv", index=False)
    manifest = {
        "dataset_id": "kiel_validation_dataset",
        "public_subset": "ten healthy participants, preferred walking only",
        "raw_path": str(RAW.relative_to(ROOT)),
        "participants": int(len(audit)),
        "sampling_hz": sorted(audit.sampling_hz.unique().tolist()),
        "sensor_contract": "bilateral feet plus pelvis; no documented lower-back channel",
        "decision": "ineligible for direct LB/LF/RF inference or pooling",
        "source": "https://github.com/neurogeriatricskiel/Validation-dataset",
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(audit[["participant_id", "sampling_hz", "acceleration_shape", "three_channel_contract_status"]].to_string(index=False))
    print("Wrote", OUT)


if __name__ == "__main__":
    main()

