"""Load Felius et al. (2024) trials and extract spatiotemporal features.

Felius, unlike Voisard, ships raw accelerometer/gyroscope CSVs with no
pre-labeled gait events, so step timing is estimated from the dominant
stepping frequency of the foot acceleration signal (Welch's method) rather
than discrete heel-strike annotations. This is a coarser proxy than
Voisard's event-based features -- documented here and in the notebook so the
two feature sets are not treated as identically derived.

Sampling rate: the repository does not state one directly, but its own
``Functions/Proces_data.py`` filter helper defaults to a 0.01 s sample
period (100 Hz), so 100 Hz is used here to match the authors' own pipeline.
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

from .signal_utils import (
    dominant_stride_frequency,
    harmonic_ratio,
    poincare_sd,
    sample_entropy,
    windowed_stride_time_cv,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = PROJECT_ROOT / "data" / "raw" / "felius_2024" / "data" / "Raw_data"

SAMPLING_RATE_HZ = 100.0
SENSOR_SUFFIXES = ("leftfoot", "rightfoot", "lowback")

FOLDER_LABELS = {
    "Data_Healthy": "Healthy",
    "Data_Stroke": "Stroke",
    # Added 2026-07-29: this project's own pipeline previously read only Data_Stroke
    # (the test-retest reliability subset), silently omitting the separate Data_long
    # folder -- the 77-participant longitudinal cohort Table 3 describes as part of
    # Felius's 107 stroke total. A journal-critic adversarial review caught the
    # resulting participant-count mismatch (34 unique subjects found vs. 107 reported).
    "Data_long": "Stroke",
}

_FILENAME_RE = re.compile(r"^(?P<trial_key>.+)_(?P<sensor>leftfoot|rightfoot|lowback)\.csv$")


def list_trials() -> pd.DataFrame:
    """Group per-sensor CSVs into one row per trial (matching sensor triplet).

    Excludes any subject whose own ID appears under more than one FOLDER_LABELS
    folder (e.g. both Data_Healthy and Data_Stroke) -- a round-19 pattern audit
    found exactly one such case, subject S001P, present in both Data_Healthy
    and Data_Stroke with the identical trial_key and byte-identical feature
    values in each copy, an apparent data-organization duplicate in Felius's
    own public release rather than two distinct people who happen to share an
    ID. The trial_key itself contains "_Stroke_" regardless of which folder it
    sits in, suggesting the Data_Healthy copy is the erroneous duplicate, but
    this project has no way to confirm that directly against Felius's own
    source, so rather than guess, every trial for any subject ID spanning more
    than one folder-derived label is excluded from both cohorts entirely.
    """
    trials: dict[tuple[str, str], dict] = {}
    subject_folders: dict[str, set[str]] = {}
    for folder, label in FOLDER_LABELS.items():
        folder_path = DATA_ROOT / folder
        if not folder_path.exists():
            continue
        for csv_path in sorted(folder_path.glob("*.csv")):
            match = _FILENAME_RE.match(csv_path.name)
            if not match:
                continue
            trial_key = match.group("trial_key")
            sensor = match.group("sensor")
            subject = trial_key.split("_", 1)[0]
            key = (folder, trial_key)
            entry = trials.setdefault(
                key,
                {"subject": subject, "trial_key": trial_key, "label": label, "paths": {}},
            )
            entry["paths"][sensor] = csv_path
            subject_folders.setdefault(subject, set()).add(folder)

    cross_folder_subjects = {s for s, folders in subject_folders.items() if len(folders) > 1}
    rows = [
        entry
        for entry in trials.values()
        if len(entry["paths"]) == len(SENSOR_SUFFIXES) and entry["subject"] not in cross_folder_subjects
    ]
    return pd.DataFrame(rows)


def _load_accel_magnitude(path: Path) -> np.ndarray:
    df = pd.read_csv(path)
    accel = df[["ax", "ay", "az"]].to_numpy()
    return np.linalg.norm(accel, axis=1)


def _load_gyro_magnitude(path: Path) -> np.ndarray:
    df = pd.read_csv(path)
    gyro = df[["gx", "gy", "gz"]].to_numpy()
    return np.linalg.norm(gyro, axis=1)


def extract_trial_features(paths: dict[str, Path]) -> dict:
    left = _load_accel_magnitude(paths["leftfoot"])
    right = _load_accel_magnitude(paths["rightfoot"])
    lowback = _load_accel_magnitude(paths["lowback"])
    lowback_gyro = _load_gyro_magnitude(paths["lowback"])

    left_freq = dominant_stride_frequency(left, SAMPLING_RATE_HZ)
    right_freq = dominant_stride_frequency(right, SAMPLING_RATE_HZ)
    mean_freq = float(np.nanmean([left_freq, right_freq]))  # single-foot rate == stride rate
    stride_freq = mean_freq if not np.isnan(mean_freq) else np.nan

    lb_sd1, _lb_sd2 = poincare_sd(lowback_gyro, fs=SAMPLING_RATE_HZ)

    return {
        # x2: each foot's dominant frequency is a stride rate (one peak per gait cycle of
        # that foot); cadence is steps/min, i.e. 2 steps per stride, to match Voisard's
        # combined left+right event count definition.
        "cadence_steps_per_min": mean_freq * 60.0 * 2.0 if not np.isnan(mean_freq) else np.nan,
        "stride_time_mean_s": 1.0 / mean_freq if mean_freq else np.nan,
        "stride_time_cv_mean": float(
            np.nanmean(
                [
                    windowed_stride_time_cv(left, SAMPLING_RATE_HZ),
                    windowed_stride_time_cv(right, SAMPLING_RATE_HZ),
                ]
            )
        ),
        "lb_accel_rms": float(np.sqrt(np.mean(lowback**2))),
        "foot_accel_rms_mean": float(np.nanmean([
            np.sqrt(np.mean(left**2)),
            np.sqrt(np.mean(right**2)),
        ])),
        "he_accel_rms": np.nan,  # Felius has no head sensor (placement differs from Voisard)
        "lb_sampen": sample_entropy(lowback, fs=SAMPLING_RATE_HZ),
        "lb_harmonic_ratio": harmonic_ratio(lowback, fs=SAMPLING_RATE_HZ, stride_freq=stride_freq)
        if stride_freq and not np.isnan(stride_freq)
        else np.nan,
        "lb_poincare_sd1_gyro": lb_sd1,
    }


def build_feature_table() -> pd.DataFrame:
    trials = list_trials()
    records = []
    for row in trials.itertuples():
        features = extract_trial_features(row.paths)
        records.append(
            {
                "subject": row.subject,
                "trial_id": row.trial_key,
                "label": row.label,
                **features,
            }
        )
    return pd.DataFrame(records)


FEATURE_COLUMNS = [
    "cadence_steps_per_min",
    "stride_time_mean_s",
    "stride_time_cv_mean",
    "lb_accel_rms",
]

NONLINEAR_FEATURE_COLUMNS = [
    "lb_sampen",
    "lb_harmonic_ratio",
    "lb_poincare_sd1_gyro",
]

LITERATURE_FEATURE_COLUMNS = FEATURE_COLUMNS + NONLINEAR_FEATURE_COLUMNS
