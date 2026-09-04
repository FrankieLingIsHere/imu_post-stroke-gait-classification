"""Load Camargo et al. (2021) for a locomotion-mode pipeline-generalization
check and a four-placement comparison (RQ2/RQ3), added 2026-07-22.

Camargo was previously excluded from all quantitative use: both ``scipy.io``
and ``pymatreader`` can only return the raw, undocumented MCOS byte layout
for this dataset's ``.mat`` files, since the dataset authors serialized every
signal-bearing file as a MATLAB ``table`` object rather than a plain struct
or array. The ``mat-io`` package (``matio``, https://github.com/foreverallama/matio)
correctly reconstructs these tables as pandas DataFrames -- confirmed
directly against this dataset's own IMU files: decoded sampling interval is
exactly 200 Hz and decoded trunk accelerometer magnitude averages ~1.03 g
with plausible walking-scale variance, both matching the dataset's own
documentation and physically sane values, not corrupted output. All 22
subjects' data is present locally.

22 healthy adults, no stroke cohort -- like DUO-GAIT, MAREA, and OxWalk, this
cannot answer "does this discriminate post-stroke gait" (RQ1) without a
label this dataset does not have. What it *can* do, honestly: it is the only
dataset with all four of trunk, thigh, shank, and foot recorded
simultaneously (RQ2), and its locomotion-mode folder structure
(levelground/ramp/stair/treadmill) is a real, non-trivial, already-labeled
four-class target for testing whether this review's own literature-informed
feature-and-classifier pipeline generalizes to a different real
classification problem (RQ3) -- not stroke evidence, a pipeline check.
"""

from __future__ import annotations

import glob
import os
from pathlib import Path

import matio
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = PROJECT_ROOT / "data" / "raw" / "camargo_2021" / "data"

SAMPLING_RATE_HZ = 200.0
PLACEMENTS = ["trunk", "thigh", "shank", "foot"]


def _imu_files(mode: str) -> list[Path]:
    pattern = str(DATA_ROOT / "*" / "*" / mode / "imu" / "*.mat")
    return [Path(p) for p in sorted(glob.glob(pattern))]


def _trial_window(imu_path: Path) -> pd.DataFrame | None:
    """Load one trial's IMU table, trimmed to the condition file's own
    trialStarts/trialEnds (excludes idle/stand padding some modes include)."""
    cond_path = Path(str(imu_path).replace(os.sep + "imu" + os.sep, os.sep + "conditions" + os.sep))
    try:
        imu = matio.load_from_mat(str(imu_path))["data"]
        cond = matio.load_from_mat(str(cond_path))
    except Exception:
        return None
    start = float(np.ravel(cond.get("trialStarts", [[imu["Header"].iloc[0]]]))[0])
    end = float(np.ravel(cond.get("trialEnds", [[imu["Header"].iloc[-1]]]))[0])
    return imu[(imu["Header"] >= start) & (imu["Header"] <= end)].reset_index(drop=True)


def _subject_from_path(path: Path) -> str:
    return Path(path).relative_to(DATA_ROOT).parts[0]


def build_placement_comparison(mode: str = "levelground", max_trials_per_subject: int = 5) -> pd.DataFrame:
    """RMS acceleration magnitude at all four simultaneous placements, per trial."""
    rows = []
    counts: dict[str, int] = {}
    for imu_path in _imu_files(mode):
        subject = _subject_from_path(imu_path)
        if counts.get(subject, 0) >= max_trials_per_subject:
            continue
        trial = _trial_window(imu_path)
        if trial is None or len(trial) < SAMPLING_RATE_HZ * 2:
            continue
        counts[subject] = counts.get(subject, 0) + 1
        for placement in PLACEMENTS:
            cols = [f"{placement}_Accel_X", f"{placement}_Accel_Y", f"{placement}_Accel_Z"]
            if not all(c in trial.columns for c in cols):
                continue
            magnitude = np.linalg.norm(trial[cols].to_numpy(dtype=float), axis=1)
            rows.append(
                {
                    "subject": subject,
                    "trial": imu_path.stem,
                    "placement": placement,
                    "accel_rms_g": float(np.sqrt(np.nanmean(magnitude**2))),
                }
            )
    return pd.DataFrame(rows)


