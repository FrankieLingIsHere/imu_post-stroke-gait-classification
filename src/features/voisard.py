"""Load Voisard et al. (2025) trials and extract basic spatiotemporal features.

Implements the first two exploratory-analysis steps from the manuscript's
Section 3.8: isolating the CVA/HS classes and computing cadence, step time,
and step time variability from the head, lower back, and foot channels.
Gait-event timing comes directly from each trial's provided
``leftGaitEvents``/``rightGaitEvents`` annotations rather than a home-grown
detector, since the dataset already ships them.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from .signal_utils import harmonic_ratio, poincare_sd, sample_entropy


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = PROJECT_ROOT / "data" / "raw" / "voisard_2025" / "data"

# Only these two cohorts are used for the initial binary classification
# baseline (manuscript Section 3.8, step 2).
COHORTS = {
    "healthy": ["HS"],
    "neuro": ["CVA"],
}


def list_trials(cohorts: dict[str, list[str]] = COHORTS) -> pd.DataFrame:
    """Return one row per trial folder for the requested cohorts."""
    rows = []
    for domain, keys in cohorts.items():
        for key in keys:
            for meta_path in sorted((DATA_ROOT / domain / key).glob("*/*/*_meta.json")):
                trial_dir = meta_path.parent
                rows.append(
                    {
                        "domain": domain,
                        "cohort": key,
                        "subject": trial_dir.parent.name,
                        "trial_id": trial_dir.name,
                        "trial_dir": trial_dir,
                        "meta_path": meta_path,
                    }
                )
    return pd.DataFrame(rows)


def _events_outside_uturn(events: list[list[int]], uturn: list[int]) -> tuple[list[list[int]], list[list[int]]]:
    """Split gait events into the pre-turn and post-turn straight-walking segments.

    Events overlapping the u-turn itself are dropped. Kept as two separate
    segments rather than merged back into one sorted list, so that stride-time
    diffs are never taken across the u-turn gap. An earlier version merged
    them before diffing, which spliced one artificial, multi-second "stride"
    spanning the entire turn into the mean and CV of every trial that has a
    u-turn -- caught by a journal-critic adversarial review that traced the
    resulting implausible CVs (0.30+ on a 10 m walk) to this.
    """
    start, end = uturn
    pre = [e for e in events if e[1] < start]
    post = [e for e in events if e[0] > end]
    return pre, post


def _stride_time_stats(
    events_pre: list[list[int]], events_post: list[list[int]], freq: float
) -> tuple[float, float, int]:
    """Mean stride time (s), coefficient of variation, and event count for one foot.

    Diffs are computed within the pre-turn and post-turn segments separately,
    then pooled, so no diff spans the removed u-turn.
    """
    n_events = len(events_pre) + len(events_post)
    diff_segments = []
    for segment in (events_pre, events_post):
        starts = np.array(sorted(e[0] for e in segment), dtype=float)
        if len(starts) >= 2:
            diff_segments.append(np.diff(starts) / freq)
    if not diff_segments:
        return np.nan, np.nan, n_events
    stride_times = np.concatenate(diff_segments)
    mean_st = float(np.mean(stride_times))
    cv_st = float(np.std(stride_times) / mean_st) if mean_st > 0 else np.nan
    return mean_st, cv_st, n_events


def _walking_bounds(
    events_pre: list[list[int]], events_post: list[list[int]]
) -> list[tuple[int, int]]:
    """Sample-index (start, end) ranges covering only the straight-walking
    segments, one per side of the u-turn that actually has events.

    Derived the same way _straight_walk_span_samples derives cadence's
    denominator, so every raw-signal feature (RMS, sample entropy, harmonic
    ratio, Poincare SD1), not only cadence, excludes the same idle padding
    and u-turn. An earlier round fixed only the cadence denominator and left
    these four features reading the whole raw file -- caught by a
    journal-critic adversarial review that traced the same idle-padding
    problem to features beyond the one it was first found in.
    """
    bounds = []
    for segment in (events_pre, events_post):
        if segment:
            bounds.append((min(e[0] for e in segment), max(e[1] for e in segment)))
    return bounds


def _restrict_to_walking(df: pd.DataFrame, bounds: list[tuple[int, int]]) -> pd.DataFrame | None:
    if not bounds:
        return None
    parts = [df.iloc[start:end] for start, end in bounds if end > start]
    parts = [p for p in parts if len(p) > 0]
    if not parts:
        return None
    return pd.concat(parts, ignore_index=True) if len(parts) > 1 else parts[0]


def _channel_accel_rms(
    trial_dir: Path, trial_id: str, channel: str, bounds: list[tuple[int, int]]
) -> float:
    """RMS of the tri-axial acceleration magnitude for one raw sensor
    channel, restricted to the straight-walking bounds."""
    path = trial_dir / f"{trial_id}_raw_data_{channel}.txt"
    if not path.exists():
        return np.nan
    df = pd.read_csv(path, sep="\t")
    df = _restrict_to_walking(df, bounds)
    if df is None or len(df) == 0:
        return np.nan
    accel = df[["Acc_X", "Acc_Y", "Acc_Z"]].to_numpy()
    magnitude = np.linalg.norm(accel, axis=1)
    return float(np.sqrt(np.mean(magnitude**2)))


def _channel_nonlinear_features(
    trial_dir: Path,
    trial_id: str,
    channel: str,
    cadence_steps_per_min: float,
    bounds: list[tuple[int, int]],
    fs: float,
) -> dict:
    """Sample entropy, harmonic ratio, and Poincare-plot SD1 for one channel,
    restricted to the straight-walking bounds.

    Sensor-axis orientation is not confirmed for this dataset (unlike Lee et
    al. (2018)'s own calibrated sensor), so these are computed on
    acceleration/angular-velocity *magnitude* rather than a specific
    labeled axis, to avoid an unverified vertical/AP/ML axis claim.

    ``fs`` must be this trial's own recorded rate (meta["freq"]), not
    assumed -- an earlier version hardcoded 100.0 Hz for the harmonic-ratio
    call. Checked directly: every sampled trial's own meta.json reports
    100.0 regardless of whether the sensor was TechnoConcept or XSens MTw
    Awinda, so this hardcoding happened not to produce a wrong value here,
    but reading the trial's own field is the correct, non-assuming practice
    regardless, and costs nothing once the value is already being loaded
    from the same meta.json for cadence.

    Computed per bound (pre-turn and post-turn separately) and combined by a
    sample-count-weighted average, rather than on `_restrict_to_walking`'s
    single concatenated array -- checked directly: every one of a 1356-trial
    sample has both a pre-turn and a post-turn segment, so the concatenated
    array has a real discontinuity at the stitch point in every single
    trial, not an occasional edge case. RMS is order-independent and
    unaffected by this (still computed on the concatenated array elsewhere
    in this module), but sample entropy, harmonic ratio, and Poincare SD1
    all assume the signal is genuinely continuous sample-to-sample, the same
    concatenation issue this project's own OxWalk loader was found to have.
    """
    path = trial_dir / f"{trial_id}_raw_data_{channel}.txt"
    if not path.exists():
        return {"sampen": np.nan, "harmonic_ratio": np.nan, "poincare_sd1_gyro": np.nan}
    df_full = pd.read_csv(path, sep="\t")

    stride_freq = (cadence_steps_per_min / 2.0) / 60.0 if cadence_steps_per_min else np.nan
    sampen_vals, sampen_w = [], []
    hr_vals, hr_w = [], []
    sd1_vals, sd1_w = [], []
    for start, end in bounds:
        if end <= start:
            continue
        seg = df_full.iloc[start:end]
        if len(seg) == 0:
            continue
        seg_accel_mag = np.linalg.norm(seg[["Acc_X", "Acc_Y", "Acc_Z"]].to_numpy(), axis=1)
        seg_gyro_mag = np.linalg.norm(seg[["Gyr_X", "Gyr_Y", "Gyr_Z"]].to_numpy(), axis=1)
        n = len(seg)
        se = sample_entropy(seg_accel_mag, fs=fs)
        if not np.isnan(se):
            sampen_vals.append(se)
            sampen_w.append(n)
        if stride_freq and not np.isnan(stride_freq):
            hr = harmonic_ratio(seg_accel_mag, fs=fs, stride_freq=stride_freq)
            if not np.isnan(hr):
                hr_vals.append(hr)
                hr_w.append(n)
        seg_sd1, _ = poincare_sd(seg_gyro_mag, fs=fs)
        if not np.isnan(seg_sd1):
            sd1_vals.append(seg_sd1)
            sd1_w.append(n)

    sampen = float(np.average(sampen_vals, weights=sampen_w)) if sampen_vals else np.nan
    hr = float(np.average(hr_vals, weights=hr_w)) if hr_vals else np.nan
    sd1 = float(np.average(sd1_vals, weights=sd1_w)) if sd1_vals else np.nan

    return {
        "sampen": sampen,
        "harmonic_ratio": hr,
        "poincare_sd1_gyro": sd1,
    }


def _straight_walk_span_samples(
    events_pre: list[list[int]], events_post: list[list[int]], uturn: list[int]
) -> float:
    """Straight-walking duration in samples, from the first to the last labeled
    gait event, minus the u-turn.

    Replaces an earlier version that used the whole processed-file's row
    count minus only the u-turn window as the denominator. That approach
    silently counted pre-walk and post-walk idle padding (confirmed directly
    against trial metadata to run several seconds per trial) as walking
    time, and did so asymmetrically across cohorts, since a fixed amount of
    padding deflates a faster walker's cadence proportionally more than a
    slower walker's -- caught by a journal-critic adversarial review that
    traced a reported CVA-vs-HS cadence reversal partly to this artifact.
    Using the labeled-event span instead ties the denominator to the same
    ground truth the numerator (event count) already uses.
    """
    all_events = events_pre + events_post
    if not all_events:
        return np.nan
    span = max(e[1] for e in all_events) - min(e[0] for e in all_events)
    if events_pre and events_post:
        # The span crosses the u-turn only if events exist on both sides of it.
        span -= uturn[1] - uturn[0]
    return max(span, 0)


def extract_trial_features(trial_dir: Path, meta_path: Path) -> dict:
    """Extract one feature row for a single trial folder."""
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    freq = meta["freq"]
    uturn = meta["uturnBoundaries"]
    trial_id = meta_path.stem.removesuffix("_meta")

    left_pre, left_post = _events_outside_uturn(meta.get("leftGaitEvents") or [], uturn)
    right_pre, right_post = _events_outside_uturn(meta.get("rightGaitEvents") or [], uturn)

    left_stride_time, left_stride_cv, left_n = _stride_time_stats(left_pre, left_post, freq)
    right_stride_time, right_stride_cv, right_n = _stride_time_stats(right_pre, right_post, freq)

    straight_walk_samples = _straight_walk_span_samples(
        left_pre + right_pre, left_post + right_post, uturn
    )
    straight_walk_minutes = straight_walk_samples / freq / 60.0 if straight_walk_samples else np.nan
    cadence = (
        (left_n + right_n) / straight_walk_minutes
        if straight_walk_minutes and straight_walk_minutes > 0
        else np.nan
    )

    tug = meta.get("TUG")
    tug_seconds = tug if isinstance(tug, (int, float)) else np.nan

    walking_bounds = _walking_bounds(left_pre + right_pre, left_post + right_post)
    lb_nonlinear = _channel_nonlinear_features(trial_dir, trial_id, "LB", cadence, walking_bounds, fs=freq)

    return {
        "subject": meta["subject"],
        "trial_id": trial_id,
        "label": meta["pathologyKey"],
        "age": meta.get("age"),
        "gender": meta.get("gender"),
        "sensor": meta.get("sensor"),
        "cadence_steps_per_min": cadence,
        "left_stride_time_s": left_stride_time,
        "right_stride_time_s": right_stride_time,
        "stride_time_mean_s": np.nanmean([left_stride_time, right_stride_time]),
        "left_stride_time_cv": left_stride_cv,
        "right_stride_time_cv": right_stride_cv,
        "stride_time_cv_mean": np.nanmean([left_stride_cv, right_stride_cv]),
        "lb_accel_rms": _channel_accel_rms(trial_dir, trial_id, "LB", walking_bounds),
        "he_accel_rms": _channel_accel_rms(trial_dir, trial_id, "HE", walking_bounds),
        "foot_accel_rms_mean": np.nanmean([
            _channel_accel_rms(trial_dir, trial_id, "LF", walking_bounds),
            _channel_accel_rms(trial_dir, trial_id, "RF", walking_bounds),
        ]),
        "lb_sampen": lb_nonlinear["sampen"],
        "lb_harmonic_ratio": lb_nonlinear["harmonic_ratio"],
        "lb_poincare_sd1_gyro": lb_nonlinear["poincare_sd1_gyro"],
        "evaluation_score_value": meta.get("evaluationScoreValue"),
        "tug_seconds": tug_seconds,
    }


def build_feature_table(cohorts: dict[str, list[str]] = COHORTS) -> pd.DataFrame:
    """Build the full trial-level feature table for the requested cohorts."""
    trials = list_trials(cohorts)
    records = [
        extract_trial_features(row.trial_dir, row.meta_path) for row in trials.itertuples()
    ]
    return pd.DataFrame(records)


FEATURE_COLUMNS = [
    "cadence_steps_per_min",
    "stride_time_mean_s",
    "stride_time_cv_mean",
    "lb_accel_rms",
    "he_accel_rms",
]

# Nonlinear-dynamics / smoothness features, added after the literature
# review (Section 4.4-4.5) surfaced sample entropy (Inui et al., 2026),
# harmonic ratio (Inui et al., 2026), and Poincare-plot SD (Lee et al.,
# 2018) as techniques used in the included studies. Kept as a separate list
# from FEATURE_COLUMNS so existing baseline results stay reproducible;
# LITERATURE_FEATURE_COLUMNS below is the union used by the informed model.
NONLINEAR_FEATURE_COLUMNS = [
    "lb_sampen",
    "lb_harmonic_ratio",
    "lb_poincare_sd1_gyro",
]

LITERATURE_FEATURE_COLUMNS = FEATURE_COLUMNS + NONLINEAR_FEATURE_COLUMNS
