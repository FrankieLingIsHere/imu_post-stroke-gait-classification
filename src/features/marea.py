"""Load MAREA (Khandelwal & Wickstrom, 2017) for a real-world robustness check.

MAREA's own value (per the manuscript's Section 3.8 positioning) is that the
*same* healthy subjects walked on a treadmill, indoors, and outdoors --
subjects 1-11 have both treadmill and indoor overground walking segments,
letting cadence be compared within the same person across environments.
Subjects 12-20 only have an outdoor segment. There is no stroke cohort here;
this is a signal-robustness reference, not classification evidence.

Feature extraction reuses the same autocorrelation-based fundamental-period
approach as ``features.felius`` (see ``features/signal_utils.py``), since
MAREA ships raw accelerometer data with no pre-labeled gait events.
Confirmed sampling rate: 128 Hz (Khandelwal & Wickstrom, 2017; not stated
directly in the local repository files).

MAREA also has waist/wrist/ankle (LF/RF) placements recorded concurrently,
letting cadence be compared across placements on the exact same walking
bout -- used here for the sensor-placement comparison (RQ2), alongside the
indoor/outdoor/treadmill robustness angle above.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import scipy.io as sio

from .signal_utils import dominant_stride_frequency, windowed_stride_time_cv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = PROJECT_ROOT / "data" / "raw" / "marea_2017" / "data"
TXT_ROOT = DATA_ROOT / "Subject Data_txt format"
TIMINGS_ROOT = DATA_ROOT / "Activity Timings"

SAMPLING_RATE_HZ = 128.0

# 0-indexed column pairs into indoorTime/outdoorTime, per the dataset's own mainScript.m
INDOOR_SEGMENTS = {"treadWalk": (0, 1), "indoorWalk": (5, 6)}
OUTDOOR_SEGMENTS = {"outdoorWalk": (0, 1)}

# A single limb (foot/ankle/wrist) completes one full swing per STRIDE, so its
# dominant autocorrelation period is a stride period (needs x2 for steps/min).
# A trunk/pelvis sensor (waist) instead bounces once per STEP -- either foot's
# contact produces a bounce -- so its dominant period is already a step period.
# Confirmed directly: raw Waist detection here came out at ~2x the concurrent
# LF/RF cadence on the same walking bout, consistent with this known
# biomechanical difference rather than a detection error.
STEP_PERIODIC_PLACEMENTS = {"Waist"}


def _load_timings() -> tuple[np.ndarray, np.ndarray]:
    indoor = sio.loadmat(TIMINGS_ROOT / "Indoor Experiment Timings.mat", simplify_cells=True)[
        "indoorTime"
    ]
    outdoor = sio.loadmat(TIMINGS_ROOT / "Outdoor Experiment Timings.mat", simplify_cells=True)[
        "outdoorTime"
    ]
    return indoor, outdoor


def _load_signal(subject_num: int, sensor: str) -> np.ndarray | None:
    path = TXT_ROOT / f"Sub{subject_num}_{sensor}.txt"
    if not path.exists():  # e.g. Sub4_Wrist.txt does not exist in the local copy
        return None
    df = pd.read_csv(path)
    return np.linalg.norm(df[["accX", "accY", "accZ"]].to_numpy(), axis=1)


def build_feature_table(sensor: str = "LF") -> pd.DataFrame:
    indoor, outdoor = _load_timings()
    rows = []

    for row_idx, subject_num in enumerate(range(1, 12)):  # subjects 1-11: indoor experiments
        signal = _load_signal(subject_num, sensor)
        for segment_name, (start_col, end_col) in INDOOR_SEGMENTS.items():
            start, end = int(indoor[row_idx, start_col]), int(indoor[row_idx, end_col])
            rows.append(_segment_features(subject_num, segment_name, signal[start:end], sensor))

    for row_idx, subject_num in enumerate(range(12, 21)):  # subjects 12-20: outdoor experiments
        signal = _load_signal(subject_num, sensor)
        for segment_name, (start_col, end_col) in OUTDOOR_SEGMENTS.items():
            start, end = int(outdoor[row_idx, start_col]), int(outdoor[row_idx, end_col])
            rows.append(_segment_features(subject_num, segment_name, signal[start:end], sensor))

    return pd.DataFrame(rows)


def build_placement_comparison(sensors: list[str] = ("Waist", "Wrist", "LF", "RF")) -> pd.DataFrame:
    """Cadence per sensor placement on the *same* walking bout for each subject.

    Uses treadWalk for subjects 1-11 and outdoorWalk for subjects 12-20 (the
    segment every subject in each group has), so placements are compared on
    a matched activity, not mixed across different walking conditions.
    """
    indoor, outdoor = _load_timings()
    rows = []
    for row_idx, subject_num in enumerate(range(1, 12)):
        start, end = int(indoor[row_idx, 0]), int(indoor[row_idx, 1])
        for sensor in sensors:
            full_signal = _load_signal(subject_num, sensor)
            if full_signal is None:
                continue
            rows.append({**_segment_features(subject_num, "treadWalk", full_signal[start:end], sensor), "placement": sensor})
    for row_idx, subject_num in enumerate(range(12, 21)):
        start, end = int(outdoor[row_idx, 0]), int(outdoor[row_idx, 1])
        for sensor in sensors:
            full_signal = _load_signal(subject_num, sensor)
            if full_signal is None:
                continue
            rows.append({**_segment_features(subject_num, "outdoorWalk", full_signal[start:end], sensor), "placement": sensor})
    return pd.DataFrame(rows)


def _segment_features(subject_num: int, segment: str, signal: np.ndarray, sensor: str = "LF") -> dict:
    # disambiguate_harmonic only for step-periodic (Waist) placements, matching
    # cross_dataset.py's own treatment of this same sensor -- an earlier round
    # enabled this in cross_dataset._marea_rows() but left this sibling
    # function, used elsewhere in this notebook for MAREA's own within-dataset
    # comparisons, on the unfixed default, so the two computed two different
    # stride-time-CV values for the identical underlying signal. Foot/wrist
    # placements never showed the step/stride ambiguity this flag corrects for
    # (confirmed when the flag was first added), so restricting it to Waist
    # here avoids any risk of it changing an already-correct foot/wrist result.
    is_step_periodic = sensor in STEP_PERIODIC_PLACEMENTS
    freq = dominant_stride_frequency(signal, SAMPLING_RATE_HZ, disambiguate_harmonic=is_step_periodic)
    steps_per_cycle = 1.0 if is_step_periodic else 2.0
    return {
        "subject": f"Sub{subject_num}",
        "segment": segment,
        "cadence_steps_per_min": freq * 60.0 * steps_per_cycle if freq and not np.isnan(freq) else np.nan,
        "stride_time_cv": windowed_stride_time_cv(signal, SAMPLING_RATE_HZ, disambiguate_harmonic=is_step_periodic),
    }


FEATURE_COLUMNS = ["cadence_steps_per_min", "stride_time_cv"]
