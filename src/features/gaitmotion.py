"""Load GaitMotion (Zhang et al., 2024) as a separate simulated-pathology set.

GaitMotion's "Stroke" and "Shuffle" folders are healthy volunteers
instructed to simulate stroke and Parkinsonian gait, not clinically
diagnosed patients (confirmed against the published paper, arXiv:2405.09569).
Per the manuscript's revised Section 3.8, this data must never be pooled
with the genuine Voisard/Felius stroke evidence -- functions here only
build a separately-reported descriptive table, not classifier training data.

Each ``.pkl`` file is a 3-element list: [0] raw IMU array, [1] a per-stride
gait-parameter DataFrame (already includes Step_time/Stride_time), [2] a
small index array. Only the per-stride parameter table is used here.
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

from .signal_utils import poincare_sd, sample_entropy


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = PROJECT_ROOT / "data" / "raw" / "gaitmotion_2025" / "data"

CONDITION_LABELS = {
    "Normal": "Normal (real gait)",
    "Shuffle": "Simulated Parkinsonian gait",
    "Stroke": "Simulated stroke gait",
}

_FILENAME_RE = re.compile(r"^(?P<subject>P\d+)_(?P<trial>\d+)_(?P<side>[LR])\.pkl$")


def list_files() -> pd.DataFrame:
    rows = []
    for condition in CONDITION_LABELS:
        folder = DATA_ROOT / condition
        if not folder.exists():
            continue
        for path in sorted(folder.glob("*.pkl")):
            match = _FILENAME_RE.match(path.name)
            if not match:
                continue
            rows.append(
                {
                    "condition": condition,
                    "subject": match.group("subject"),
                    "trial": match.group("trial"),
                    "side": match.group("side"),
                    "path": path,
                }
            )
    return pd.DataFrame(rows)


def summarize_file(path: Path) -> dict:
    """Mean/CV of step time and stride length from the per-stride parameter table."""
    _, stride_params, _ = pd.read_pickle(path)
    step_time = stride_params["Step_time"].to_numpy(dtype=float)
    step_time = step_time[step_time > 0]
    stride_length = stride_params["Stride_length"].to_numpy(dtype=float)
    stride_length = stride_length[stride_length > 0]
    return {
        "n_strides": len(stride_params),
        "step_time_mean_s": float(np.mean(step_time)) if len(step_time) else np.nan,
        "step_time_cv": (
            float(np.std(step_time) / np.mean(step_time)) if len(step_time) > 1 else np.nan
        ),
        "stride_length_mean_cm": float(np.mean(stride_length)) if len(stride_length) else np.nan,
    }


def build_pathology_classification_table() -> pd.DataFrame:
    """Literature-informed features from the raw IMU array (element [0] of
    each .pkl, columns 0-2 accelerometer, 3-5 gyroscope, orientation not
    confirmed so magnitude is used, matching this review's own convention
    for Voisard/Felius), labeled Normal / Shuffle (simulated Parkinsonian) /
    Stroke (simulated stroke), for the RQ3 pipeline-generalization check
    added 2026-07-22.

    Deliberately excludes cadence and harmonic ratio: both need a sampling
    rate, and this dataset's IMU sampling rate could not be confirmed
    against the published paper (arXiv:2405.09569) or the UBC data
    repository page within this review's access. RMS is genuinely
    sampling-rate-independent and used directly. Sample entropy and Poincare
    SD1 are NOT rate-independent -- both are computed from consecutive-sample
    relationships and would need resampling to a common rate to be
    comparable across datasets, exactly like cadence and harmonic ratio (see
    ``signal_utils.sample_entropy`` and ``signal_utils.poincare_sd``'s own
    docstrings; caught as a direct self-contradiction with this docstring's
    former "sampling-rate-independent" claim by a round-18 journal-critic
    adversarial review). Since this dataset's rate is unconfirmed, both are
    passed ``fs=None`` and return NaN here rather than a silently
    incomparable value, consistent with the same choice already made for
    cadence and harmonic ratio. This is a simulated-pathology sensitivity
    check on this review's own pipeline, never real stroke evidence -- see
    this dataset's role note in Section 3.8.
    """
    rows = []
    for _, row in list_files().iterrows():
        raw, _stride_params, _idx = pd.read_pickle(row.path)
        accel_mag = np.linalg.norm(raw[:, 0:3], axis=1)
        gyro_mag = np.linalg.norm(raw[:, 3:6], axis=1)
        sd1, _ = poincare_sd(gyro_mag, fs=None)
        rows.append(
            {
                "subject": row.subject,
                "trial": row.trial,
                "side": row.side,
                "label": row.condition,
                "accel_rms": float(np.sqrt(np.nanmean(accel_mag**2))),
                "gyro_rms": float(np.sqrt(np.nanmean(gyro_mag**2))),
                # fs=None: GaitMotion's own IMU sampling rate is unconfirmed (see this
                # project's other disclosed limitations on this dataset), so this now
                # returns NaN rather than silently comparing an unresampled signal
                # against every other dataset's common-rate sample entropy.
                "sampen_accel": sample_entropy(accel_mag, fs=None),
                "poincare_sd1_gyro": sd1,
            }
        )
    return pd.DataFrame(rows)


PATHOLOGY_FEATURE_COLUMNS = ["accel_rms", "gyro_rms", "sampen_accel", "poincare_sd1_gyro"]


def build_summary_table() -> pd.DataFrame:
    files = list_files()
    records = [
        {
            "condition": CONDITION_LABELS[row.condition],
            "subject": row.subject,
            "trial": row.trial,
            "side": row.side,
            **summarize_file(row.path),
        }
        for row in files.itertuples()
    ]
    return pd.DataFrame(records)
