from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1] / "data/raw/zenodo_stroke_rehab/extracted"
OUT = Path(__file__).resolve().parents[1] / "data/processed/zenodo_stroke_rehab_file_audit.csv"

participants = pd.read_csv(ROOT / "raw/participant_info.csv")
rows = []
for path in sorted((ROOT / "interim").glob("imu*/visit*/imu/*.csv")):
    frame = pd.read_csv(path)
    sensor = path.stem
    sample_hz = 1.0 / frame["timestamp"].diff().median() if "timestamp" in frame else None
    rows.append({
        "participant": path.parents[2].name,
        "visit": path.parents[1].name,
        "sensor": sensor,
        "rows": len(frame),
        "sample_hz": sample_hz,
        "columns": ";".join(frame.columns),
    })

audit = pd.DataFrame(rows).merge(participants[["sub", "age", "sex"]], left_on="participant", right_on="sub", how="left")
OUT.parent.mkdir(parents=True, exist_ok=True)
audit.to_csv(OUT, index=False)
print("Participants:", len(participants))
print("Age range:", int(participants.age.min()), "to", int(participants.age.max()))
print("Sensor counts:")
print(audit.groupby("sensor").agg(participants=("participant", "nunique"), files=("sensor", "size"), median_hz=("sample_hz", "median")))
print("Wrote:", OUT)
