"""Load DUO-GAIT (Zhou et al., 2023) healthy-reference spatiotemporal parameters.

Unlike Felius/MAREA, DUO-GAIT's own processing pipeline already publishes
per-subject aggregate gait parameters (cadence, stride time, stride length,
symmetry index, etc.) under ``repository_processed`` -- these are used
directly rather than re-derived from raw signals, since they are the
dataset authors' own validated numbers.

Used here as a healthy-population reference (16 healthy adults, single-task
vs dual-task, unfatigued vs fatigued), not for stroke classification: this
dataset has no stroke cohort.
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_ROOT = PROJECT_ROOT / "data" / "raw" / "duogait_2023" / "data" / "repository_raw"
DATA_ROOT = RAW_ROOT.parent / "repository_processed"
# repository_raw/OG_st_raw|OG_dt_raw hold ONE continuous ~49-minute recording per
# subject per visit -- confirmed directly against Zhou et al. (2023, Scientific
# Data, PMC10442385): "Raw IMU data ... were continuously recorded from the start
# of the first walking session to the end of the second walking session" and
# "the 'OG_st_raw' folder contains the data from the entire single task visits
# (i.e., ST-Control and ST-Fatigue)". That single file spans the 6-minute control
# walk, the non-walking fatigue protocol in between, and the 6-minute fatigue
# walk, with no usable per-sample walking annotation (the raw export's own
# "Event" column is an empty placeholder, confirmed against the header row).
# The dataset authors already did the correct walking-only segmentation
# themselves via "visual examination of the IMU signals" and published it here:
INTERIM_ROOT = RAW_ROOT.parent / "repository_interim"

CONDITIONS = ["OG_st_control", "OG_st_fatigue", "OG_dt_control", "OG_dt_fatigue"]
SAMPLING_RATE_HZ = 128.0  # Gait Up Physilog, confirmed directly from the raw CSV header row
SENSORS = ["HE", "ST", "SA", "LW", "RW", "LF", "RF"]  # head, sternum, sacrum, wrists, feet
SENSOR_LABELS = {
    "HE": "Head", "ST": "Chest (sternum)", "SA": "Lower back (sacrum)",
    "LW": "Left wrist", "RW": "Right wrist", "LF": "Left foot", "RF": "Right foot",
}

_SUBJECT_RE = re.compile(r"sub_(\d+)")


def load_demographics() -> pd.DataFrame:
    """Per-subject sex/age/height/weight/activity_level from the dataset's own file."""
    df = pd.read_csv(RAW_ROOT / "subject_info.csv")
    df = df.rename(columns={"sub": "subject"})
    return df[["subject", "sex", "age", "activity_level"]]


def build_feature_table(conditions: list[str] = CONDITIONS) -> pd.DataFrame:
    """One row per subject/condition, using the dataset's own aggregate_params.csv."""
    rows = []
    for condition in conditions:
        condition_dir = DATA_ROOT / condition
        if not condition_dir.exists():
            continue
        for subject_dir in sorted(condition_dir.iterdir()):
            params_path = subject_dir / "aggregate_params.csv"
            if not params_path.exists():
                continue
            match = _SUBJECT_RE.search(subject_dir.name)
            params = pd.read_csv(params_path).iloc[0]
            rows.append(
                {
                    "subject": match.group(0) if match else subject_dir.name,
                    "condition": condition,
                    "cadence_steps_per_min": params.get("cadence_avg"),
                    "cadence_cv": params.get("cadence_CV"),
                    "stride_time_mean_s": params.get("stride_times_avg"),
                    "stride_time_cv": params.get("stride_times_CV"),
                    "stride_length_m": params.get("stride_lengths_avg"),
                    "speed_m_s": params.get("speed_avg"),
                    "stride_time_symmetry_index": params.get("stride_times_SI"),
                }
            )
    table = pd.DataFrame(rows)
    return table.merge(load_demographics(), on="subject", how="left")


def _load_sensor_raw(path: Path) -> pd.DataFrame:
    """Parse a Gait Up Physilog export: 4 description lines, a grouped-unit header,
    the real column-name row (starts with 'Time,'), then a units row before data.
    Returns the full numeric frame (Accel X/Y/Z and Gyro X/Y/Z), not just accel.

    Kept only for reference/debugging against the untrimmed whole-visit export --
    no feature-computation path in this project should call this anymore, since
    it returns ~49 minutes of mostly non-walking signal. Use _load_sensor_segment
    instead, which reads the dataset's own walking-only interim segmentation."""
    with path.open(encoding="utf-8", errors="replace") as f:
        lines = f.readlines()
    header_idx = next(i for i, line in enumerate(lines) if line.startswith("Time,"))
    df = pd.read_csv(path, skiprows=header_idx, header=0, low_memory=False)
    df = df.iloc[1:].reset_index(drop=True)  # drop the units row
    cols = ["Accel X", "Accel Y", "Accel Z", "Gyro X", "Gyro Y", "Gyro Z"]
    return df[cols].apply(pd.to_numeric, errors="coerce")


def _load_sensor_segment(path: Path) -> pd.DataFrame:
    """Parse one of the dataset's own manually-segmented, walking-only interim
    CSVs (repository_interim/OG_{st,dt}_{control,fatigue}/sub_XX/{sensor}.csv):
    an unnamed row-index column, timestamp, then GyrX/Y/Z, AccX/Y/Z -- still the
    original absolute sample index/timestamp from the raw recording (confirmed:
    sub_01's OG_st_control SA.csv starts at row index 49000, timestamp 382.8s,
    not re-based to 0), just trimmed to the ~6-minute walking bout, matching
    Zhou et al. (2023)'s stated protocol duration. Renamed to this module's
    existing Accel X/Gyro X column convention so callers are format-agnostic."""
    df = pd.read_csv(path, index_col=0)
    df = df.rename(columns={
        "AccX": "Accel X", "AccY": "Accel Y", "AccZ": "Accel Z",
        "GyrX": "Gyro X", "GyrY": "Gyro Y", "GyrZ": "Gyro Z",
    })
    cols = ["Accel X", "Accel Y", "Accel Z", "Gyro X", "Gyro Y", "Gyro Z"]
    return df[cols].apply(pd.to_numeric, errors="coerce")


def _load_sensor_accel(path: Path) -> np.ndarray:
    raw = _load_sensor_segment(path)
    return np.linalg.norm(raw[["Accel X", "Accel Y", "Accel Z"]].to_numpy(), axis=1)


def build_placement_comparison(condition: str = "OG_st_control", sensors: list[str] = SENSORS) -> pd.DataFrame:
    """Per-subject, per-sensor accel-magnitude RMS -- for comparing placements directly.

    Uses the dataset's own walking-only interim segmentation (control/unfatigued
    state by default, matching this review's other healthy-reference datasets,
    none of which apply a fatigue manipulation) -- not the raw export, which is
    the entire ~49-minute visit including the non-walking fatigue protocol.
    """
    condition_dir = INTERIM_ROOT / condition
    rows = []
    for subject_dir in sorted(condition_dir.iterdir()):
        if not subject_dir.is_dir():
            continue
        match = _SUBJECT_RE.search(subject_dir.name)
        subject = match.group(0) if match else subject_dir.name
        for sensor in sensors:
            sensor_path = subject_dir / f"{sensor}.csv"
            if not sensor_path.exists():
                continue
            magnitude = _load_sensor_accel(sensor_path)
            rows.append(
                {
                    "subject": subject,
                    "sensor": sensor,
                    "placement": SENSOR_LABELS.get(sensor, sensor),
                    "accel_rms_g": float(np.sqrt(np.nanmean(magnitude**2))),
                }
            )
    table = pd.DataFrame(rows)
    return table.merge(load_demographics(), on="subject", how="left")


FEATURE_COLUMNS = [
    "cadence_steps_per_min",
    "stride_time_mean_s",
    "stride_time_cv",
    "stride_length_m",
    "speed_m_s",
]
