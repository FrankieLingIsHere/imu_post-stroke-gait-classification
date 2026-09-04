"""Build a trial-provenance manifest from the dataset's published mapping code."""
from pathlib import Path
import re
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data/raw/sint_maartenskliniek/extracted/IMU_GaitAnalysis-1.1.0"
DATA = BASE / "data"
SOURCE = (BASE / "functions_validationstudy/functions_dataimport.py").read_text(errors="replace")
OUT = ROOT / "data/processed/sint_maartenskliniek_trial_manifest.csv"

# The release code assigns an exported### folder to each published Vicon trial.
pairs = re.findall(r"entry\.name\s*==\s*'([^']+)'(?:(?!entry\.name).){0,500}?xsensnum\[entry\.name\]\s*=\s*'([0-9]{3})'", SOURCE, re.S)
mapping = {name: num for name, num in pairs}


def local_participant(vicon_name: str) -> str:
    m = re.search(r"900_(?:CVA|V)_?(?:pp)?0*([0-9]+)", vicon_name)
    if not m:
        raise ValueError(vicon_name)
    prefix = "900_CVA_" if "CVA" in vicon_name else "900_V_"
    return f"{prefix}{int(m.group(1)):02d}"


rows = []
for vicon_name, exported in sorted(mapping.items()):
    participant = local_participant(vicon_name)
    label = "stroke" if "CVA" in vicon_name else "healthy"
    trial_type = "irregular" if "_SS" in vicon_name else "regular"
    speed = "fixed_speed" if "_FS" in vicon_name else "self_paced"
    if "2MWT" in vicon_name:
        trial_type = "2MWT"
    participant_dir = DATA / ("CVA" if label == "stroke" else "Healthy_controls") / participant
    trial_dir = participant_dir / "Xsens" / f"exported{exported}"
    rows.append({
        "dataset_id": "sint_maartenskliniek",
        "participant": participant,
        "participant_key": f"sint_{participant}",
        "label": label,
        "label_binary": int(label == "stroke"),
        "vicon_trial": vicon_name,
        "exported_trial": f"exported{exported}",
        "trial_type": trial_type,
        "speed_condition": speed,
        "export_exists": trial_dir.exists(),
    })

manifest = pd.DataFrame(rows).drop_duplicates(["participant", "exported_trial"])
manifest.to_csv(OUT, index=False)
print("Wrote", OUT)
print(manifest.groupby(["label", "trial_type", "speed_condition"]).agg(participants=("participant", "nunique"), trials=("exported_trial", "size")))
print("Missing mapped exports:", int((~manifest.export_exists).sum()))
