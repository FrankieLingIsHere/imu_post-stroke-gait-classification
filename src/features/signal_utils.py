"""Shared signal-processing helpers for datasets with no labeled gait events.

Used by Felius and MAREA: both ship raw accelerometer data with no
heel-strike annotations, so stride timing is estimated from the signal
itself rather than discrete events.

Fundamental stride period is estimated via unbiased autocorrelation (the
first strong peak at a physiologically plausible lag), not via picking the
single highest-power bin in an FFT/Welch spectrum. Foot/ankle-mounted
accelerometers commonly show a stronger spectral peak at the *second*
harmonic (roughly double the true stride frequency) than at the
fundamental -- confirmed directly against MAREA data, where naive FFT
peak-picking returned 225-270 steps/min (physiologically impossible) versus
~110-135 steps/min from autocorrelation. Autocorrelation avoids this because
it searches outward from the shortest plausible lag for the first strong
periodicity rather than the single global power maximum.

Even with autocorrelation, highly irregular gait (seen especially in some
Felius Stroke trials) can fail to show any real periodicity in the search
window, and the best-available peak sits right at the window edge -- a
sign of failure, not a real 300 steps/min stride rate. Two quality gates
below reject such cases as NaN rather than silently returning them:
peak-at-boundary, and peak autocorrelation below ``MIN_PEAK_STRENGTH``.
"""

from __future__ import annotations

import numpy as np
from scipy.signal import correlate

MIN_STRIDE_S = 0.4  # 150 strides/min upper bound
MAX_STRIDE_S = 2.0  # 30 strides/min lower bound
MIN_PEAK_STRENGTH = 0.25  # autocorrelation value below this = no real periodicity found


def dominant_stride_frequency(
    signal_1d: np.ndarray,
    fs: float,
    min_stride_s: float = MIN_STRIDE_S,
    max_stride_s: float = MAX_STRIDE_S,
    disambiguate_harmonic: bool = False,
    half_ratio_threshold: float = 0.85,
) -> float:
    """Fundamental stride frequency (Hz, one cycle per stride) via autocorrelation.

    ``disambiguate_harmonic`` is opt-in and defaults to False, so every
    existing caller (Felius, MAREA, Camargo, Voisard's own cadence
    reconciliation) is completely unaffected. Confirmed necessary for
    DUO-GAIT specifically: its sacral placement on highly symmetric healthy
    gait produces two comparably strong autocorrelation peaks, one at the
    true step period and one at the stride period (exactly double), since
    consecutive left and right steps look nearly identical at that site.
    Plain peak-picking then locks onto whichever peak is marginally
    stronger, unpredictably by trial, producing a spuriously bimodal
    cadence distribution -- caught by a journal-critic adversarial review
    that traced several DUO-GAIT subjects' implausibly slow cadence
    (roughly half of physiologically typical adult walking) and the
    dataset's own stride-time-CV outlier value to this ambiguity. When
    enabled, checks the autocorrelation value at exactly half the detected
    peak's lag (double the frequency) and prefers it whenever that
    candidate is positive and at least ``half_ratio_threshold`` of the
    detected peak's own strength, rather than the detected peak itself.
    """
    n = len(signal_1d)
    if n < fs * max_stride_s * 2:
        return np.nan

    detrended = signal_1d - np.mean(signal_1d)
    # FFT-based correlation (method="fft"): direct np.correlate is O(n^2) and far too
    # slow for multi-minute, 100+ Hz segments (tens of thousands of samples).
    autocorr = correlate(detrended, detrended, mode="full", method="fft")[n - 1 :]
    if autocorr[0] <= 0:
        return np.nan
    autocorr = autocorr / autocorr[0]

    min_lag = max(int(min_stride_s * fs), 1)
    max_lag = min(int(max_stride_s * fs), n - 1)
    if min_lag >= max_lag:
        return np.nan

    window = autocorr[min_lag:max_lag]
    peak_offset = int(np.argmax(window))
    peak_lag = min_lag + peak_offset
    peak_value = window[peak_offset]

    at_boundary = peak_offset <= 1 or peak_offset >= len(window) - 2
    if at_boundary or peak_value < MIN_PEAK_STRENGTH:
        return np.nan

    if disambiguate_harmonic:
        half_lag = peak_lag // 2
        # half_lag must still respect min_lag -- otherwise this can accept a
        # candidate faster than the function's own physiological ceiling
        # (fs / min_lag), which happened for several Camargo trials during
        # verification: a peak_lag just above min_lag produced a half_lag
        # below it, selected because it passed the strength-ratio check,
        # yielding a cadence (~260-286 steps/min) faster than any real human
        # gait rather than a corrected, plausible one.
        if half_lag >= min_lag:
            half_value = autocorr[half_lag]
            if half_value > 0 and half_value >= half_ratio_threshold * peak_value:
                peak_lag = half_lag

    return float(fs / peak_lag)


def windowed_stride_time_cv(
    signal_1d: np.ndarray,
    fs: float,
    window_s: float = 5.0,
    hop_s: float = 2.5,
    disambiguate_harmonic: bool = False,
) -> float:
    """Coefficient of variation of stride time across sliding sub-windows.

    ``disambiguate_harmonic`` forwards to ``dominant_stride_frequency`` per
    window (see its own docstring) and defaults to False, so every existing
    caller is unaffected. Needed for DUO-GAIT specifically, where the same
    step/stride harmonic ambiguity affecting single-estimate cadence is even
    more disruptive per 5 s window (only ~4-6 gait cycles per window), since
    a short window can lock onto a third or fourth sub-harmonic that the
    exact-half check above does not catch, not only the exact double. When
    ``disambiguate_harmonic`` is True, a second pass removes any per-window
    estimate whose stride time deviates by more than 40% from the window
    set's own median before computing the CV -- confirmed necessary by
    direct inspection of DUO-GAIT's own per-window estimates, which cluster
    tightly (roughly 105-113 steps/min) with a handful of clear outliers
    (30-80 steps/min, corresponding to a 3x-4x sub-harmonic lock) rather
    than following the smooth, single-cluster distribution real stride-rate
    drift would produce.
    """
    window = int(window_s * fs)
    hop = int(hop_s * fs)
    stride_times = []
    for start in range(0, max(len(signal_1d) - window, 1), hop):
        freq = dominant_stride_frequency(
            signal_1d[start : start + window], fs, disambiguate_harmonic=disambiguate_harmonic
        )
        if freq and not np.isnan(freq):
            stride_times.append(1.0 / freq)
    if len(stride_times) < 2:
        return np.nan
    stride_times = np.array(stride_times)
    if disambiguate_harmonic and len(stride_times) >= 4:
        median_st = np.median(stride_times)
        keep = np.abs(stride_times - median_st) <= 0.4 * median_st
        if keep.sum() >= 2:
            stride_times = stride_times[keep]
    return float(np.std(stride_times) / np.mean(stride_times))


# ---------------------------------------------------------------------------
# Nonlinear-dynamics / smoothness features, added after the literature review
# (Section 4.4-4.5 of the manuscript) surfaced them as techniques used by
# included studies but not yet tried on this project's own mined datasets:
# sample entropy (Inui et al., 2026), harmonic ratio (Inui et al., 2026), and
# a Poincare-plot perpendicular-axis SD on gyroscope data (Lee et al., 2018).
# ---------------------------------------------------------------------------

MAX_SAMPEN_SAMPLES = 5000  # secondary safety cap only (see TARGET_SAMPEN_HZ below);
# sample entropy is O(n^2), so this still guards against a pathologically long
# input, but resampling to a common rate keeps it from being the thing that
# actually determines n for any dataset in normal use.

TARGET_SAMPEN_HZ = 10.0  # common effective rate every signal is resampled to
# before entropy is computed, regardless of native sampling rate or trial
# duration. A journal-critic adversarial review caught a real, undisclosed
# confound in an earlier version of this function: it capped every signal to
# a fixed *sample count* (1500) via uniform index selection regardless of
# duration, so a short, near-native-rate trial (e.g. an 11-second, 200 Hz
# Camargo trial, barely downsampled) and a long trial (e.g. a 6-minute,
# 128 Hz DUO-GAIT/MAREA walk) ended up compared at effective rates roughly
# 90 Hz apart (confirmed directly: ~93 Hz vs ~4 Hz), which alone plausibly
# explains most of Camargo's much lower raw sample-entropy values relative to
# DUO-GAIT/MAREA rather than a genuine gait-regularity difference. Resampling
# every signal to the same target rate first removes that duration-dependent
# confound at its source instead of only disclosing it. 10 Hz is chosen to
# keep several samples per gait cycle (stride frequency is roughly 1-2 Hz)
# while staying computationally cheap and leaving even the shortest Camargo
# trials (~11 s) with a comfortable sample count.


def sample_entropy(signal_1d: np.ndarray, fs: float | None, m: int = 2, r: float | None = None) -> float:
    """Sample entropy (Richman & Moorman, 2000): -ln(A/B), the log-ratio of
    template matches of length m+1 to length m, at tolerance r. Lower values
    mean a more regular (self-similar) signal; higher values mean a more
    irregular one. Used here as a regularity feature on acceleration signal,
    following Inui et al. (2026)'s SampEn_AP.

    ``fs`` (the signal's native sampling rate) is required so every signal
    can be resampled to the same effective rate (``TARGET_SAMPEN_HZ``) before
    entropy is computed -- see that constant's own comment for why this
    matters for cross-dataset comparability. Pass ``fs=None`` only when the
    native rate genuinely cannot be confirmed (e.g. GaitMotion, per this
    project's own disclosed limitation); this returns NaN rather than
    silently comparing an unresampled signal against everything else.
    """
    x = np.asarray(signal_1d, dtype=float)
    x = x[~np.isnan(x)]
    if fs is None:
        return np.nan
    if fs > TARGET_SAMPEN_HZ:
        from scipy.signal import resample_poly
        from fractions import Fraction
        ratio = Fraction(TARGET_SAMPEN_HZ / fs).limit_denominator(1000)
        x = resample_poly(x, ratio.numerator, ratio.denominator)
    n = len(x)
    if n > MAX_SAMPEN_SAMPLES:
        idx = np.linspace(0, n - 1, MAX_SAMPEN_SAMPLES).astype(int)
        x = x[idx]
        n = MAX_SAMPEN_SAMPLES
    if n < (m + 1) * 4:
        return np.nan
    if r is None:
        r = 0.2 * np.std(x)
    if r <= 0:
        return np.nan

    # Resampling to TARGET_SAMPEN_HZ above removes the RATE confound but not
    # a DURATION confound: sample entropy's own estimate accuracy at a fixed
    # template length m improves with more samples, and per-dataset segment
    # duration is not itself harmonized here (e.g. Camargo trials run ~11 s
    # while DUO-GAIT/MAREA walks run several minutes). Confirmed directly by
    # a round-18 journal-critic adversarial review: even after the common-
    # rate fix, per-dataset healthy sample-entropy means still span roughly a
    # 2.6x range (Camargo ~0.51, DUO-GAIT ~0.98, MAREA ~1.11, OxWalk ~1.30)
    # despite all four reflecting similar healthy overground gait. Disclosed
    # here and in the manuscript (Table 6) rather than corrected -- a proper
    # fix would mean harmonizing segment duration itself across datasets
    # built from fundamentally different recording protocols (single short
    # trials vs. continuous multi-minute walks), a larger redesign than a
    # rate-resampling fix.

    def _match_count(order: int) -> int:
        templates = np.array([x[i : i + order] for i in range(n - order + 1)])
        count = 0
        for i in range(len(templates) - 1):
            dist = np.max(np.abs(templates[i + 1 :] - templates[i]), axis=1)
            count += int(np.sum(dist <= r))
        return count

    b = _match_count(m)
    a = _match_count(m + 1)
    if b == 0 or a == 0:
        return np.nan
    return float(-np.log(a / b))


def harmonic_ratio(
    signal_1d: np.ndarray, fs: float, stride_freq: float, n_harmonics: int = 10, axis_type: str = "vertical"
) -> float:
    """Ratio of even-to-odd (vertical/anterior-posterior axes) or odd-to-even
    (mediolateral axis) harmonic amplitudes at multiples of the stride
    frequency, a standard smoothness/rhythmicity measure -- used here
    following Inui et al. (2026)'s HR_AP. Higher values indicate smoother,
    more rhythmic gait.
    """
    x = np.asarray(signal_1d, dtype=float)
    x = x[~np.isnan(x)]
    n = len(x)
    if n < fs * 2 or not stride_freq or np.isnan(stride_freq) or stride_freq <= 0:
        return np.nan

    spectrum = np.abs(np.fft.rfft(x - np.mean(x)))
    freqs = np.fft.rfftfreq(n, d=1.0 / fs)

    harmonic_amps = []
    for k in range(1, n_harmonics + 1):
        target = k * stride_freq
        if target >= freqs[-1]:
            break
        idx = int(np.argmin(np.abs(freqs - target)))
        harmonic_amps.append(spectrum[idx])
    if len(harmonic_amps) < 4:
        return np.nan
    harmonic_amps = np.array(harmonic_amps)

    odd = harmonic_amps[0::2].sum()  # 1st, 3rd, 5th, ...
    even = harmonic_amps[1::2].sum()  # 2nd, 4th, 6th, ...
    if axis_type == "mediolateral":
        return float(odd / even) if even > 0 else np.nan
    return float(even / odd) if odd > 0 else np.nan


def poincare_sd(signal_1d: np.ndarray, fs: float | None) -> tuple[float, float]:
    """SD1 (short-term/perpendicular-axis variability) and SD2 (long-term
    variability) of the lag-1 Poincare plot of a signal against itself.
    Following Lee et al. (2018)'s best single feature (SD of the Poincare
    plot's perpendicular axis on angular velocity).

    ``fs`` (the signal's native sampling rate) is required for the same
    reason ``sample_entropy`` requires it (see that function's own
    docstring and ``TARGET_SAMPEN_HZ``'s comment): SD1 is computed from
    consecutive-sample (lag-1) differences, so for a band-limited signal
    it scales roughly as 1/fs -- a higher native rate means adjacent
    samples are closer together in time and hence closer in value,
    shrinking SD1 for no gait-related reason. A journal-critic adversarial
    review (round 18) caught this as the identical confound already fixed
    for sample entropy but left unfixed here, with GaitMotion's
    ~3x-elevated SD1 mean relative to Voisard/Felius as the symptom. Every
    signal is resampled to the same ``TARGET_SAMPEN_HZ`` before SD1/SD2 are
    computed, exactly as sample entropy already does. Pass ``fs=None`` only
    when the native rate genuinely cannot be confirmed (e.g. GaitMotion,
    per this project's own disclosed limitation); this returns NaN rather
    than silently comparing an unresampled signal against everything else.
    """
    x = np.asarray(signal_1d, dtype=float)
    x = x[~np.isnan(x)]
    if fs is None:
        return np.nan, np.nan
    if fs > TARGET_SAMPEN_HZ:
        from scipy.signal import resample_poly
        from fractions import Fraction
        ratio = Fraction(TARGET_SAMPEN_HZ / fs).limit_denominator(1000)
        x = resample_poly(x, ratio.numerator, ratio.denominator)
    if len(x) < 3:
        return np.nan, np.nan
    x1, x2 = x[:-1], x[1:]
    diff = x1 - x2
    total = x1 + x2
    sd1 = float(np.std(diff) / np.sqrt(2))
    sd2 = float(np.std(total) / np.sqrt(2))
    return sd1, sd2


def feature_snr(values: np.ndarray, labels: np.ndarray) -> float:
    """Between-group to within-group variance ratio (an ANOVA F-statistic),
    used as a signal-to-noise-ratio-style feature-relevance score following
    Hsu et al. (2021)'s SNR-based feature selection.
    """
    values = np.asarray(values, dtype=float)
    labels = np.asarray(labels)
    mask = ~np.isnan(values)
    values, labels = values[mask], labels[mask]
    groups = [values[labels == g] for g in np.unique(labels)]
    groups = [g for g in groups if len(g) > 0]
    if len(groups) < 2:
        return np.nan
    grand_mean = np.mean(values)
    k = len(groups)
    n = len(values)
    between = sum(len(g) * (np.mean(g) - grand_mean) ** 2 for g in groups) / (k - 1)
    within_df = n - k
    if within_df <= 0:
        return np.nan
    within = sum(np.sum((g - np.mean(g)) ** 2) for g in groups) / within_df
    return float(between / within) if within > 0 else np.nan


def kmedoids_cosine(
    x: np.ndarray, k: int = 2, n_init: int = 10, max_iter: int = 100, random_state: int = 0
):
    """Minimal k-medoids (PAM-style) clustering with cosine distance,
    following Brasiliano et al. (2026)'s unsupervised validation step: check
    whether supervised-selected features also separate groups without using
    the labels to fit the clustering itself.
    """
    from sklearn.metrics.pairwise import cosine_distances

    rng = np.random.RandomState(random_state)
    dist = cosine_distances(x)
    n = x.shape[0]

    best_cost = np.inf
    best_labels = None
    best_medoids = None
    for _ in range(n_init):
        medoids = rng.choice(n, size=k, replace=False)
        for _ in range(max_iter):
            labels = np.argmin(dist[:, medoids], axis=1)
            new_medoids = medoids.copy()
            for ki in range(k):
                members = np.where(labels == ki)[0]
                if len(members) == 0:
                    continue
                sub_dist = dist[np.ix_(members, members)]
                new_medoids[ki] = members[np.argmin(sub_dist.sum(axis=1))]
            if np.array_equal(new_medoids, medoids):
                break
            medoids = new_medoids
        labels = np.argmin(dist[:, medoids], axis=1)
        cost = float(dist[np.arange(n), medoids[labels]].sum())
        if cost < best_cost:
            best_cost, best_labels, best_medoids = cost, labels, medoids

    return best_labels, best_medoids
