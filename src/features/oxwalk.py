"""Load OxWalk (Small et al., 2022) healthy free-living step-annotated data.

OxWalk ships its own ground-truth step annotations (a ``1`` marks a step),
so -- like Voisard -- cadence and step timing come from the provided labels
rather than a signal-processing proxy. Recordings are free-living (not a
supervised walking protocol), so features are restricted to "active walking
bouts": consecutive annotated steps less than ``BOUT_GAP_S`` apart, to avoid
diluting cadence with long idle/non-walking stretches.

Used here as a healthy hip/wrist placement reference; OxWalk has no stroke
cohort.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = PROJECT_ROOT / "data" / "raw" / "oxwalk_2022" / "data"

BOUT_GAP_S = 2.0
PLACEMENTS = ["Hip_100Hz", "Wrist_100Hz"]


def list_files(placements: list[str] = PLACEMENTS) -> pd.DataFrame:
    rows = []
    for placement in placements:
        folder = DATA_ROOT / placement
        if not folder.exists():
            continue
        for path in sorted(folder.glob("*.csv")):
            participant = path.stem.split("_")[0]
            rows.append({"placement": placement, "participant": participant, "path": path})
    return pd.DataFrame(rows)


def extract_features(path: Path) -> dict:
    df = pd.read_csv(path, usecols=["timestamp", "annotation"])
    timestamps = pd.to_datetime(df["timestamp"])
    step_times = timestamps[df["annotation"] == 1].to_numpy()
    if len(step_times) < 3:
        return {"n_steps": len(step_times), "cadence_steps_per_min": np.nan, "step_time_cv": np.nan}

    intervals_s = np.diff(step_times).astype("timedelta64[ms]").astype(float) / 1000.0
    bout_intervals = intervals_s[intervals_s < BOUT_GAP_S]
    if len(bout_intervals) < 2:
        return {"n_steps": len(step_times), "cadence_steps_per_min": np.nan, "step_time_cv": np.nan}

    return {
        "n_steps": len(step_times),
        "cadence_steps_per_min": float(60.0 / np.mean(bout_intervals)),
        "step_time_cv": float(np.std(bout_intervals) / np.mean(bout_intervals)),
    }


def bout_mask(path: Path) -> np.ndarray:
    """Boolean mask, one entry per row of the raw CSV at ``path``, True for
    samples that fall within an active walking bout (between two consecutive
    annotated steps less than ``BOUT_GAP_S`` apart), False for free-living
    idle/non-walking time.

    Added so any feature computed on this dataset's raw signal, not only
    cadence and step-time CV, can be restricted to the same walking-only
    definition this module's own docstring specifies -- a signal-magnitude
    RMS computed over the whole day-long recording, as this module's
    downstream callers previously did, is dominated by free-living idle
    time rather than walking, since OxWalk is not a supervised walking
    protocol like Voisard's. Caught by a journal-critic adversarial review.

    Safe for a simple point-wise statistic like RMS (order-independent), but
    NOT safe to use as `signal[mask]` for any feature that assumes temporal
    continuity (sample entropy, harmonic ratio) -- see `bout_bounds` below,
    added specifically because a single OxWalk file typically contains 20-50
    separate bouts (confirmed directly: a 5-file sample ranged 22-54 bouts,
    mean bout length 450-6600 samples), so concatenating them via boolean
    indexing introduces that many artificial sample-to-sample discontinuities
    into the signal, which a windowed-autocorrelation or FFT-based feature
    would read as a real signal, not the stitching artifact it actually is.
    """
    df = pd.read_csv(path, usecols=["timestamp", "annotation"])
    timestamps = pd.to_datetime(df["timestamp"])
    step_idx = np.flatnonzero(df["annotation"].to_numpy() == 1)
    mask = np.zeros(len(df), dtype=bool)
    if len(step_idx) < 2:
        return mask
    step_times = timestamps.iloc[step_idx].to_numpy()
    gaps_s = np.diff(step_times).astype("timedelta64[ms]").astype(float) / 1000.0
    for i, gap in enumerate(gaps_s):
        if gap < BOUT_GAP_S:
            mask[step_idx[i] : step_idx[i + 1] + 1] = True
    return mask


def bout_bounds(path: Path) -> list[tuple[int, int]]:
    """Same walking-bout definition as `bout_mask`, but returned as a list of
    (start, end) sample-index ranges (end exclusive) rather than a flat
    boolean mask, so a caller can compute a continuity-sensitive feature
    (sample entropy, harmonic ratio) separately per bout and aggregate
    afterward, instead of concatenating non-contiguous bouts into one array
    first -- see `bout_mask`'s own docstring for why that matters."""
    df = pd.read_csv(path, usecols=["timestamp", "annotation"])
    timestamps = pd.to_datetime(df["timestamp"])
    step_idx = np.flatnonzero(df["annotation"].to_numpy() == 1)
    if len(step_idx) < 2:
        return []
    step_times = timestamps.iloc[step_idx].to_numpy()
    gaps_s = np.diff(step_times).astype("timedelta64[ms]").astype(float) / 1000.0
    bounds = []
    bout_start = None
    for i, gap in enumerate(gaps_s):
        if gap < BOUT_GAP_S:
            if bout_start is None:
                bout_start = step_idx[i]
            bout_end = step_idx[i + 1] + 1
        else:
            if bout_start is not None:
                bounds.append((bout_start, bout_end))
                bout_start = None
    if bout_start is not None:
        bounds.append((bout_start, bout_end))
    return bounds


def load_demographics() -> pd.DataFrame:
    """Per-participant sex and age *range* (OxWalk ships age as a bracket, not a value)."""
    return pd.read_csv(DATA_ROOT / "metadata.csv")


def build_feature_table(placements: list[str] = PLACEMENTS) -> pd.DataFrame:
    files = list_files(placements)
    records = [
        {"placement": row.placement, "participant": row.participant, **extract_features(row.path)}
        for row in files.itertuples()
    ]
    table = pd.DataFrame(records)
    return table.merge(load_demographics(), on="participant", how="left")


FEATURE_COLUMNS = ["cadence_steps_per_min", "step_time_cv"]
