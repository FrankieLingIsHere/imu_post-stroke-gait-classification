"""Unified cross-dataset healthy-reference check, added 2026-07-22.

Direct response to the user's objection to the first version of this
session's dataset expansion: testing DUO-GAIT/OxWalk/MAREA/Camargo against
their *own* unrelated labeled tasks (environment, dual-task, locomotion
mode) produced real results, but none of them actually served RQ1/RQ3's
real question, which is specifically about discriminating and classifying
*post-stroke* gait. This module replaces that framing with one that keeps
every dataset pointed at the same goal: every healthy-only dataset
(DUO-GAIT, OxWalk, MAREA, Camargo, plus GaitMotion's "Normal" condition)
becomes an independent, out-of-sample test of whether the stroke-vs-healthy
classifier and discriminative features built on Voisard/Felius (Section
4.2.4) actually generalize to genuinely different, independently-collected
healthy people -- not just the same-study controls they were built and
validated on.

Two honest limits, stated once here rather than repeated per dataset below:
1. Not every dataset has every literature-informed feature available (a
   head sensor, a gyroscope, a confirmed sampling rate). Missing features
   are left as NaN and handled by the classifier's own median imputer,
   fit on the *training* data only -- standard practice, not fabrication.
2. GaitMotion's only available placement is the foot, not trunk/lower back
   like every other dataset here. Its result is reported with that caveat
   attached, not silently pooled as if it were placement-matched.

**A real units bug caught during development, not before it reached the
manuscript**: a first version of this module applied a Voisard-trained and
a Felius-trained classifier directly to this module's harmonized feature
table and got a 100.0% false-positive rate against every single one of 335
independent healthy people, with zero variation across datasets -- too
uniform to be a real finding. Direct inspection of each dataset's raw
signal confirmed a genuine unit mismatch: Voisard, MAREA, and GaitMotion
report accelerometer data in m/s^2 (confirmed: resting-magnitude ~9.8-11,
matching gravity in that unit), while Camargo, DUO-GAIT, OxWalk, and Felius
report accelerometer data in g (confirmed: resting-magnitude ~1.0). Gyro
units similarly split: Voisard and Camargo in rad/s (confirmed: walking
magnitude ~0.5-0.9), DUO-GAIT, GaitMotion, and Felius in deg/s (confirmed
directly from DUO-GAIT's own CSV header, and from magnitude: ~30-180).
Every raw signal below is converted to a single canonical unit (g for
accelerometer, deg/s for gyroscope) immediately after loading, before any
feature is derived from it. Sample entropy and harmonic ratio are
scale-invariant by construction (both are computed relative to the
signal's own distribution) and were never affected by this bug -- only RMS
and Poincare SD1, which scale linearly with the raw signal, were.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

MS2_PER_G = 9.80665
DEG_PER_RAD = 57.29577951308232

from . import camargo as camargo_mod
from . import duogait as duogait_mod
from . import gaitmotion as gaitmotion_mod
from . import marea as marea_mod
from . import oxwalk as oxwalk_mod
from .signal_utils import (
    dominant_stride_frequency,
    harmonic_ratio,
    poincare_sd,
    sample_entropy,
    windowed_stride_time_cv,
)

LITERATURE_FEATURE_COLUMNS = [
    "cadence_steps_per_min",
    "stride_time_mean_s",
    "stride_time_cv_mean",
    "lb_accel_rms",
    "he_accel_rms",
    "lb_sampen",
    "lb_harmonic_ratio",
    "lb_poincare_sd1_gyro",
]


_SAMPEN_FS_DEFAULT = object()  # sentinel: "use fs itself", distinct from an explicit None


def _row(
    dataset,
    subject,
    accel_mag,
    fs,
    gyro_mag=None,
    cadence_override=None,
    stride_cv_override=None,
    placement_note="trunk-equivalent",
    disambiguate_harmonic=False,
    sampen_fs=_SAMPEN_FS_DEFAULT,
):
    # sampen_fs defaults to fs itself (most callers), but OxWalk passes fs=None
    # here (its cadence/stride-CV come from annotation overrides, not
    # autocorrelation) while still having a perfectly confirmed native rate
    # for sample entropy specifically -- sampen_fs lets it supply that
    # separately instead of losing entropy to the same None that correctly
    # disables the autocorrelation-based features.
    if sampen_fs is _SAMPEN_FS_DEFAULT:
        sampen_fs = fs
    # Trunk/waist/sacrum sensors sit near the body's center of mass and bounce
    # ONCE PER STEP (either foot), not once per stride like an ankle/foot
    # sensor -- confirmed directly in this project's own MAREA analysis
    # (manuscript Section 4.2.3). Every placement used by this module's
    # per-dataset extractors is trunk-equivalent (SA/Waist/trunk/foot-only-
    # for-GaitMotion), so the correct conversion is x60x1, not x60x2. Using
    # the stride-periodic factor here would silently double every non-
    # override cadence, the exact bug already caught and fixed for MAREA's
    # Waist sensor elsewhere in this project -- re-derived and fixed here
    # before it reached the manuscript.
    #
    # disambiguate_harmonic defaults to False, so every dataset except
    # DUO-GAIT (the only caller that opts in) is completely unaffected --
    # see dominant_stride_frequency's own docstring for why DUO-GAIT needs
    # it: a step/stride autocorrelation-peak ambiguity specific to its
    # sacral placement on highly symmetric healthy gait.
    freq = (
        dominant_stride_frequency(accel_mag, fs, disambiguate_harmonic=disambiguate_harmonic)
        if fs
        else None
    )
    cadence = cadence_override if cadence_override is not None else (
        freq * 60.0 * 1.0 if freq and not np.isnan(freq) else np.nan
    )
    stride_cv = stride_cv_override if stride_cv_override is not None else (
        windowed_stride_time_cv(accel_mag, fs, disambiguate_harmonic=disambiguate_harmonic) if fs else np.nan
    )
    sd1 = np.nan
    if gyro_mag is not None:
        sd1, _ = poincare_sd(gyro_mag, fs=fs)
    return {
        "dataset": dataset,
        "subject": subject,
        "placement_note": placement_note,
        "cadence_steps_per_min": cadence,
        # Stride time = one full gait cycle = 2 steps, so 120/cadence, not 60/cadence
        # (which would be step time). Confirmed against Voisard's own convention:
        # its stride_time_mean_s is the interval between successive same-foot
        # events, not successive steps of either foot -- see voisard.py's
        # _stride_time_stats.
        "stride_time_mean_s": 120.0 / cadence if cadence and not np.isnan(cadence) and cadence > 0 else np.nan,
        "stride_time_cv_mean": stride_cv,
        "lb_accel_rms": float(np.sqrt(np.nanmean(accel_mag**2))),
        "he_accel_rms": np.nan,
        "lb_sampen": sample_entropy(accel_mag, fs=sampen_fs),
        # harmonic_ratio's own harmonic index is defined relative to the true
        # stride fundamental, not the step rate -- freq here is a step rate
        # (per the comment above), so it must be halved first. Passing freq
        # directly, as an earlier version of this line did, silently indexed
        # harmonic_ratio's even/odd split one octave off for every
        # trunk-equivalent dataset that reaches this default path (DUO-GAIT,
        # MAREA, Camargo), a journal-critic adversarial review caught this
        # directly against the code.
        "lb_harmonic_ratio": (
            harmonic_ratio(accel_mag, fs, freq / 2.0) if fs and freq and not np.isnan(freq) else np.nan
        ),
        "lb_poincare_sd1_gyro": sd1,
    }


def _duogait_rows(disambiguate_harmonic: bool = True) -> list[dict]:
    # Uses the dataset's own walking-only interim segmentation (control /
    # unfatigued state), not repository_raw's OG_st_raw -- that raw export is
    # confirmed (Zhou et al. 2023, PMC10442385) to be one continuous ~49-minute
    # recording per subject spanning the 6-minute control walk, the non-walking
    # fatigue protocol, and the 6-minute fatigue walk concatenated, with no
    # usable per-sample walking annotation. An earlier version of this function
    # read that raw export directly, diluting every raw-signal feature (RMS,
    # cadence, sample entropy, harmonic ratio, Poincare SD1) with ~43 minutes of
    # non-walking signal -- caught via direct inspection of the raw file's own
    # header and cross-checked against the dataset's published protocol.
    rows = []
    condition_dir = duogait_mod.INTERIM_ROOT / "OG_st_control"
    for subject_dir in sorted(condition_dir.iterdir()):
        if not subject_dir.is_dir():
            continue
        subject = duogait_mod._SUBJECT_RE.search(subject_dir.name)
        subject = subject.group(0) if subject else subject_dir.name
        sa_path = subject_dir / "SA.csv"
        he_path = subject_dir / "HE.csv"
        if not sa_path.exists():
            continue
        sa = duogait_mod._load_sensor_segment(sa_path)
        accel_mag = np.linalg.norm(sa[["Accel X", "Accel Y", "Accel Z"]].to_numpy(), axis=1)
        gyro_mag = np.linalg.norm(sa[["Gyro X", "Gyro Y", "Gyro Z"]].to_numpy(), axis=1)
        row = _row(
            "DUO-GAIT", subject, accel_mag, duogait_mod.SAMPLING_RATE_HZ,
            gyro_mag=gyro_mag, disambiguate_harmonic=disambiguate_harmonic,
        )
        if he_path.exists():
            he_accel = duogait_mod._load_sensor_accel(he_path)
            row["he_accel_rms"] = float(np.sqrt(np.nanmean(he_accel**2)))
        rows.append(row)
    return rows


OXWALK_HIP_FS_HZ = 100.0  # confirmed directly: folder name "Hip_100Hz", per this dataset's own convention


MIN_BOUT_SAMPLES_FOR_SAMPEN = 120  # 1.2 s at 100 Hz -- resamples to >= (m+1)*4 = 12
# points at TARGET_SAMPEN_HZ (10 Hz), signal_utils.sample_entropy's own minimum

MIN_BOUT_SAMPLES_FOR_HR = 1000  # 10 s at 100 Hz. harmonic_ratio's own frequency
# resolution is 1/duration, and it reads a single FFT bin per harmonic -- a
# short bout gives a coarse resolution that can misassign energy between
# adjacent harmonics. 10 s gives 0.1 Hz resolution, well under a typical
# 0.8-1.5 Hz stride frequency, so consecutive harmonics stay separated.
# Deliberately a separate, larger floor from MIN_BOUT_SAMPLES_FOR_SAMPEN
# above -- an earlier version of this function used the sample-entropy floor
# for both features, even though the two have different minimum-duration
# requirements for a reliable estimate.


def _oxwalk_rows() -> list[dict]:
    rows = []
    files = oxwalk_mod.list_files(placements=["Hip_100Hz"])
    for f in files.itertuples():
        df = pd.read_csv(f.path, usecols=["timestamp", "x", "y", "z", "annotation"])
        # Restricted to active walking bouts, matching oxwalk.py's own
        # cadence/step-time-CV convention -- an earlier version left this
        # unrestricted, so lb_accel_rms was the RMS of a mostly free-living,
        # non-walking day rather than a walking RMS comparable to the other
        # datasets in this pool.
        mask = oxwalk_mod.bout_mask(f.path)
        accel_mag = np.linalg.norm(df.loc[mask, ["x", "y", "z"]].to_numpy(), axis=1)
        feats = oxwalk_mod.extract_features(f.path)  # annotation-based cadence, more accurate than autocorrelation here
        if np.isnan(feats["cadence_steps_per_min"]) or len(accel_mag) == 0:
            continue
        cadence = feats["cadence_steps_per_min"]
        stride_freq_hz = cadence / 120.0  # cadence = stride_freq_hz * 60 * 2 steps/stride
        row = _row(
            "OxWalk", f.participant, accel_mag, fs=None,
            cadence_override=cadence,
            stride_cv_override=feats["step_time_cv"],
            sampen_fs=None,  # overridden below with a per-bout estimate instead
        )
        # Sample entropy and harmonic ratio both assume temporal continuity
        # (windowed autocorrelation, FFT), unlike RMS above. A typical OxWalk
        # file splits into 20-50 separate walking bouts (confirmed directly:
        # a 5-file sample ranged 22-54 bouts), so concatenating them via the
        # boolean mask above, as an earlier version of this function did for
        # every feature, introduces that many artificial discontinuities
        # into the signal -- fine for RMS (order-independent), but read as
        # real high-frequency content by these two features specifically.
        # Computed per bout instead, weighted by each bout's own sample
        # count, and only over bouts long enough to support a valid estimate.
        all_bounds = oxwalk_mod.bout_bounds(f.path)
        full = df[["x", "y", "z"]].to_numpy()
        sampen_vals, sampen_weights = [], []
        hr_vals, hr_weights = [], []
        for s, e in all_bounds:
            n = e - s
            if n >= MIN_BOUT_SAMPLES_FOR_SAMPEN:
                bout_mag = np.linalg.norm(full[s:e], axis=1)
                se = sample_entropy(bout_mag, fs=OXWALK_HIP_FS_HZ)
                if not np.isnan(se):
                    sampen_vals.append(se)
                    sampen_weights.append(n)
            if n >= MIN_BOUT_SAMPLES_FOR_HR:
                bout_mag = np.linalg.norm(full[s:e], axis=1)
                hr = harmonic_ratio(bout_mag, OXWALK_HIP_FS_HZ, stride_freq_hz)
                if not np.isnan(hr):
                    hr_vals.append(hr)
                    hr_weights.append(n)
        row["lb_sampen"] = (
            float(np.average(sampen_vals, weights=sampen_weights)) if sampen_vals else np.nan
        )
        row["lb_harmonic_ratio"] = (
            float(np.average(hr_vals, weights=hr_weights)) if hr_vals else np.nan
        )
        rows.append(row)
    return rows


def _marea_rows(disambiguate_harmonic: bool = True) -> list[dict]:
    # MAREA's accelerometer is in m/s^2 (confirmed: resting magnitude ~10.6),
    # not g like Camargo/DUO-GAIT/OxWalk/Felius -- converted here so RMS is
    # in the same canonical unit as everything else this module produces.
    #
    # disambiguate_harmonic defaults to True here too, not just for DUO-GAIT:
    # a journal-critic adversarial review flagged MAREA's stride-time-CV mean
    # (0.12, roughly double DUO-GAIT/Camargo's ~0.02-0.03) as an unexplained
    # discrepancy given all three use the same waist/trunk-equivalent,
    # windowed-autocorrelation estimator. Direct verification confirmed the
    # same short-window sub-harmonic lock: enabling disambiguation drops
    # MAREA's mean stride-time-CV to 0.047, in line with the other two, while
    # leaving its single-estimate cadence and harmonic ratio completely
    # unchanged (confirmed: max abs diff 0.0 across all 20 subjects) --
    # this only stabilizes the per-5s-window estimate, not the whole-signal one.
    rows = []
    indoor, outdoor = marea_mod._load_timings()
    for row_idx, subject_num in enumerate(range(1, 12)):
        signal = marea_mod._load_signal(subject_num, "Waist")
        if signal is None:
            continue
        start, end = int(indoor[row_idx, 0]), int(indoor[row_idx, 1])  # treadWalk segment
        rows.append(_row("MAREA", f"Sub{subject_num}", signal[start:end] / MS2_PER_G, marea_mod.SAMPLING_RATE_HZ,
                          disambiguate_harmonic=disambiguate_harmonic))
    for row_idx, subject_num in enumerate(range(12, 21)):
        signal = marea_mod._load_signal(subject_num, "Waist")
        if signal is None:
            continue
        start, end = int(outdoor[row_idx, 0]), int(outdoor[row_idx, 1])
        rows.append(_row("MAREA", f"Sub{subject_num}", signal[start:end] / MS2_PER_G, marea_mod.SAMPLING_RATE_HZ,
                          disambiguate_harmonic=disambiguate_harmonic))
    return rows


def _camargo_rows(max_trials_per_subject: int = 5, disambiguate_harmonic: bool = True) -> list[dict]:
    # disambiguate_harmonic=True here too, for the same reason as MAREA above:
    # Camargo's mean stride-time-CV before this fix was 0.067, roughly double
    # DUO-GAIT's estimator-matched value, and enabling disambiguation drops it
    # to 0.026, matching the same short-window sub-harmonic lock pattern. This
    # surfaced a second, independent bug in dominant_stride_frequency's own
    # half-lag check (fixed in signal_utils.py): the half-lag candidate could
    # fall below min_lag, producing a small number of implausible cadences
    # (~260-286 steps/min) instead of a corrected one -- confirmed and fixed
    # with a min_lag floor on the accepted half-lag before this default changed.
    rows = []
    counts: dict[str, int] = {}
    for imu_path in camargo_mod._imu_files("levelground"):
        subject = camargo_mod._subject_from_path(imu_path)
        if counts.get(subject, 0) >= max_trials_per_subject:
            continue
        trial = camargo_mod._trial_window(imu_path)
        if trial is None or len(trial) < camargo_mod.SAMPLING_RATE_HZ * 2:
            continue
        accel_cols = ["trunk_Accel_X", "trunk_Accel_Y", "trunk_Accel_Z"]
        gyro_cols = ["trunk_Gyro_X", "trunk_Gyro_Y", "trunk_Gyro_Z"]
        if not all(c in trial.columns for c in accel_cols + gyro_cols):
            continue
        counts[subject] = counts.get(subject, 0) + 1
        accel_mag = np.linalg.norm(trial[accel_cols].to_numpy(dtype=float), axis=1)
        # Camargo's accelerometer is already g (confirmed: resting magnitude ~1.03,
        # see camargo.py's own docstring), but its gyroscope is rad/s (confirmed:
        # walking magnitude ~0.85, same order as Voisard's own rad/s gyro) -- converted
        # to deg/s here to match DUO-GAIT/GaitMotion/Felius's canonical unit.
        gyro_mag = np.linalg.norm(trial[gyro_cols].to_numpy(dtype=float), axis=1) * DEG_PER_RAD
        rows.append(_row("Camargo", subject, accel_mag, camargo_mod.SAMPLING_RATE_HZ, gyro_mag=gyro_mag,
                          disambiguate_harmonic=disambiguate_harmonic))
    return rows


def _gaitmotion_rows() -> list[dict]:
    # GaitMotion's accelerometer is in m/s^2 (confirmed: resting magnitude ~11.0),
    # converted to g here. Its gyroscope (~179 magnitude while walking) is already
    # deg/s, consistent with DUO-GAIT/Felius, so left unconverted.
    rows = []
    files = gaitmotion_mod.list_files()
    for f in files[files["condition"] == "Normal"].itertuples():
        raw, _stride_params, _idx = pd.read_pickle(f.path)
        accel_mag = np.linalg.norm(raw[:, 0:3], axis=1) / MS2_PER_G
        gyro_mag = np.linalg.norm(raw[:, 3:6], axis=1)
        # fs not confirmed for this dataset -- no cadence/harmonic ratio, same
        # constraint already applied in build_pathology_classification_table.
        row = _row(
            "GaitMotion", f.subject, accel_mag, fs=None, gyro_mag=gyro_mag,
            placement_note="foot (not trunk -- only placement this dataset has)",
        )
        rows.append(row)
    return rows


def build_healthy_reference_table() -> pd.DataFrame:
    """One row per subject/trial across all five non-stroke sources, in the
    same feature space as Voisard/Felius's own LITERATURE_FEATURE_COLUMNS,
    for testing whether the stroke-vs-healthy classifier and discriminative
    features generalize to genuinely independent healthy people."""
    rows = _duogait_rows() + _oxwalk_rows() + _marea_rows() + _camargo_rows() + _gaitmotion_rows()
    cols = ["dataset", "subject", "placement_note"] + LITERATURE_FEATURE_COLUMNS
    return pd.DataFrame(rows)[cols]


# Added 2026-08-11: foot/ankle-channel RMS for the healthy-reference datasets,
# mirroring build_healthy_reference_table()'s trunk RMS exactly (same unit
# conversion, same walking-span restriction per dataset, same bilateral
# left+right averaging convention already used for Voisard/Felius's own
# foot_accel_rms_mean) but never previously computed here -- foot RMS was
# more discriminative than trunk RMS within both real stroke datasets but
# had never been entered into this pooled cross-dataset check. OxWalk (hip
# and wrist only) has no foot or ankle channel and is excluded outright, not
# substituted. MAREA's LF/RF placement is ankle, not foot -- included as a
# substitute channel, flagged via placement_note, exactly as the trunk
# comparison already treats OxWalk's hip and GaitMotion's foot as trunk
# substitutes.

def _duogait_foot_rows() -> list[dict]:
    # Same OG_st_control walking-only interim segmentation as _duogait_rows,
    # just reading LF.csv/RF.csv instead of SA.csv -- already in the
    # canonical g unit, confirmed in _duogait_rows's own unit-mismatch note.
    rows = []
    condition_dir = duogait_mod.INTERIM_ROOT / "OG_st_control"
    for subject_dir in sorted(condition_dir.iterdir()):
        if not subject_dir.is_dir():
            continue
        subject = duogait_mod._SUBJECT_RE.search(subject_dir.name)
        subject = subject.group(0) if subject else subject_dir.name
        lf_path = subject_dir / "LF.csv"
        rf_path = subject_dir / "RF.csv"
        if not lf_path.exists() or not rf_path.exists():
            continue
        lf_rms = float(np.sqrt(np.nanmean(duogait_mod._load_sensor_accel(lf_path) ** 2)))
        rf_rms = float(np.sqrt(np.nanmean(duogait_mod._load_sensor_accel(rf_path) ** 2)))
        rows.append({
            "dataset": "DUO-GAIT",
            "subject": subject,
            "placement_note": "foot (genuine, bilateral)",
            "foot_accel_rms_mean": float(np.nanmean([lf_rms, rf_rms])),
        })
    return rows


def _camargo_foot_rows(max_trials_per_subject: int = 5) -> list[dict]:
    # Same levelground trial windowing and per-subject trial cap as
    # _camargo_rows, reading the foot_Accel_* columns instead of trunk_Accel_*.
    # Camargo's foot channel is single-sided (only "foot", no left/right
    # split), matching the dataset's own column naming -- no averaging needed.
    rows = []
    counts: dict[str, int] = {}
    for imu_path in camargo_mod._imu_files("levelground"):
        subject = camargo_mod._subject_from_path(imu_path)
        if counts.get(subject, 0) >= max_trials_per_subject:
            continue
        trial = camargo_mod._trial_window(imu_path)
        if trial is None or len(trial) < camargo_mod.SAMPLING_RATE_HZ * 2:
            continue
        accel_cols = ["foot_Accel_X", "foot_Accel_Y", "foot_Accel_Z"]
        if not all(c in trial.columns for c in accel_cols):
            continue
        counts[subject] = counts.get(subject, 0) + 1
        accel_mag = np.linalg.norm(trial[accel_cols].to_numpy(dtype=float), axis=1)
        rows.append({
            "dataset": "Camargo",
            "subject": subject,
            "placement_note": "foot (genuine, single-sided)",
            "foot_accel_rms_mean": float(np.sqrt(np.nanmean(accel_mag ** 2))),
        })
    return rows


def _gaitmotion_foot_rows() -> list[dict]:
    # GaitMotion's only placement IS the foot (see _gaitmotion_rows's own
    # docstring) -- the accel_mag it already computes there and stores under
    # the generic "lb_accel_rms" column is itself a foot RMS, just carrying
    # the trunk-equivalent column name every other dataset's _row() call
    # uses. Recomputed here under its own name rather than renamed in place,
    # so build_healthy_reference_table()'s existing output/column is untouched.
    #
    # Added 2026-08-11: unlike _gaitmotion_rows() above, this restricts each
    # trial's RMS to the gait-active portion of the raw signal, rather than
    # computing over the whole file -- the same class of walking-span
    # restriction every other dataset in this module already applies (Voisard's
    # corrected bounds, OxWalk's bout mask, Camargo's trial window, DUO-GAIT's
    # interim segmentation, MAREA's timing segments), which GaitMotion alone
    # had never been given. Confirmed directly: the raw array carries two
    # previously-unused columns beyond the six IMU channels (index 6 and 7),
    # binary-valued and matching the source paper's own description of the
    # released data ("step segmentation results synchronized with
    # accelerometer and gyroscope data") -- almost certainly per-sample
    # stance/swing gait-phase flags. The same paper confirms each raw trial
    # also includes deliberate non-gait content: "Participants were asked to
    # stay stationary for a couple of seconds before and after the trials for
    # calibration." Restricting to samples where either flag is active (a
    # standard stand-in for "gait phase" when neither the raw file nor the
    # stride table gives an explicit non-walking-supplemental-nulls flag)
    # excludes that calibration padding, exactly as every sibling dataset
    # here already excludes its own idle time before computing RMS.
    rows = []
    files = gaitmotion_mod.list_files()
    for f in files[files["condition"] == "Normal"].itertuples():
        raw, _stride_params, _idx = pd.read_pickle(f.path)
        gait_active = (raw[:, 6] > 0) | (raw[:, 7] > 0)
        if not gait_active.any():
            continue
        accel_mag = np.linalg.norm(raw[gait_active, 0:3], axis=1) / MS2_PER_G
        rows.append({
            "dataset": "GaitMotion",
            "subject": f.subject,
            "placement_note": "foot (genuine, only placement this dataset has; gait-active samples only)",
            "foot_accel_rms_mean": float(np.sqrt(np.nanmean(accel_mag ** 2))),
        })
    return rows


def _marea_foot_rows(sensors: tuple[str, str] = ("LF", "RF")) -> list[dict]:
    # Same indoor treadWalk (subjects 1-11) / outdoor (subjects 12-20)
    # segment windowing and m/s^2-to-g conversion as _marea_rows, reading
    # the ankle-worn LF/RF sensors instead of Waist. Bilateral averaging
    # matches Voisard/Felius/DUO-GAIT's own convention.
    rows = []
    indoor, outdoor = marea_mod._load_timings()
    for row_idx, subject_num in enumerate(range(1, 12)):
        start, end = int(indoor[row_idx, 0]), int(indoor[row_idx, 1])
        rms_vals = []
        for sensor in sensors:
            signal = marea_mod._load_signal(subject_num, sensor)
            if signal is None:
                continue
            rms_vals.append(float(np.sqrt(np.nanmean((signal[start:end] / MS2_PER_G) ** 2))))
        if rms_vals:
            rows.append({
                "dataset": "MAREA",
                "subject": f"Sub{subject_num}",
                "placement_note": "ankle (substitute -- LF/RF, not foot)",
                "foot_accel_rms_mean": float(np.nanmean(rms_vals)),
            })
    for row_idx, subject_num in enumerate(range(12, 21)):
        start, end = int(outdoor[row_idx, 0]), int(outdoor[row_idx, 1])
        rms_vals = []
        for sensor in sensors:
            signal = marea_mod._load_signal(subject_num, sensor)
            if signal is None:
                continue
            rms_vals.append(float(np.sqrt(np.nanmean((signal[start:end] / MS2_PER_G) ** 2))))
        if rms_vals:
            rows.append({
                "dataset": "MAREA",
                "subject": f"Sub{subject_num}",
                "placement_note": "ankle (substitute -- LF/RF, not foot)",
                "foot_accel_rms_mean": float(np.nanmean(rms_vals)),
            })
    return rows


FOOT_RMS_GENUINE_DATASETS = ["DUO-GAIT", "Camargo", "GaitMotion"]
FOOT_RMS_SUBSTITUTE_DATASETS = ["MAREA"]  # ankle, not foot -- OxWalk excluded entirely (no distal channel)


def build_foot_rms_reference() -> pd.DataFrame:
    """One row per subject/trial across the four healthy-reference datasets
    that provide a usable foot or ankle channel (DUO-GAIT, Camargo,
    GaitMotion genuine foot; MAREA ankle substitute), for the same pooled
    cross-dataset generalization check build_healthy_reference_table()
    already runs for trunk RMS. OxWalk (hip and wrist only) is excluded
    outright -- no distal channel to substitute, unlike its hip-for-trunk
    role in the trunk comparison."""
    rows = _duogait_foot_rows() + _camargo_foot_rows() + _gaitmotion_foot_rows() + _marea_foot_rows()
    return pd.DataFrame(rows)[["dataset", "subject", "placement_note", "foot_accel_rms_mean"]]


def discriminative_feature_comparison(stroke_features: pd.DataFrame, healthy_reference: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Mann-Whitney U comparison of each shared feature: pooled stroke
    (Voisard + Felius) vs. the pooled independent healthy reference (five
    non-stroke datasets), rather than each stroke dataset against only its
    own same-study controls. Answers RQ1's real question directly: do the
    discriminative features already identified in Section 4.2.2 still
    separate stroke from healthy against a much larger, more independent,
    cross-hardware healthy population, not just the study that found them."""
    import scipy.stats as st

    rows = []
    for col in columns:
        a = stroke_features[col].dropna()
        b = healthy_reference[col].dropna()
        if len(a) < 3 or len(b) < 3:
            continue
        u, p = st.mannwhitneyu(a, b)
        r = 1 - (2 * u) / (len(a) * len(b))
        rows.append(
            {
                "feature": col,
                "stroke_median": a.median(),
                "healthy_median": b.median(),
                "n_stroke": len(a),
                "n_healthy": len(b),
                "p_value": p,
                "effect_size_r": r,
            }
        )
    return pd.DataFrame(rows)


def harmonize_voisard_features(voisard_features: "pd.DataFrame") -> "pd.DataFrame":
    """Voisard's own accelerometer (m/s^2) and gyroscope (rad/s) are in
    different units from this module's canonical g / deg-per-s -- convert a
    copy of Voisard's feature table so a classifier trained on it can be
    fairly applied to build_healthy_reference_table()'s output. Felius needs
    no equivalent correction: its accelerometer is already g and its
    gyroscope already deg/s (confirmed directly against its raw CSV)."""
    out = voisard_features.copy()
    for col in ("lb_accel_rms", "he_accel_rms", "foot_accel_rms_mean"):
        if col in out.columns:
            out[col] = out[col] / MS2_PER_G
    if "lb_poincare_sd1_gyro" in out.columns:
        out["lb_poincare_sd1_gyro"] = out["lb_poincare_sd1_gyro"] * DEG_PER_RAD
    return out
