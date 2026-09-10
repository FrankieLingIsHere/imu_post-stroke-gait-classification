"""Pinned mobgap lower-back measurement adapter; no diagnosis/reference input."""
from importlib.metadata import version

import numpy as np
import pandas as pd
from mobgap.gait_sequences import GsdAdaptiveIonescu
from mobgap.initial_contacts import IcdShinImproved

COLS = ['acc_x', 'acc_y', 'acc_z', 'gyr_x', 'gyr_y', 'gyr_z']


def detect_lower_back_events(data, sampling_rate_hz, *, known_gait=False):
    """Return bouts and absolute sample ICs from m/s² acceleration.

    Gyroscope columns satisfy mobgap's frame schema but neither selected
    algorithm uses them. known_gait bypasses GSD for an explicitly provided
    gait sequence; callers must disclose where that sequence came from.
    No turn detector or laterality assignment is implemented.
    """
    if version('mobgap') != '1.2.0':
        raise RuntimeError('This adapter was locked to mobgap 1.2.0')
    if not np.isfinite(sampling_rate_hz) or sampling_rate_hz <= 0:
        raise ValueError('Positive finite sampling rate required')
    if not set(COLS).issubset(data.columns):
        raise ValueError('Missing sensor-frame columns')
    data = data[COLS].reset_index(drop=True).copy()
    acc = data[COLS[:3]].to_numpy(dtype=float)
    if len(acc) < 2 or not np.isfinite(acc).all():
        return {'status': 'invalid_acceleration', 'bouts': [], 'events': []}
    if np.ptp(np.linalg.norm(acc, axis=1)) == 0:
        return {'status': 'constant_magnitude', 'bouts': [], 'events': []}
    bouts = [(0, len(data))] if known_gait else [
        (int(r.start), int(r.end)) for r in
        GsdAdaptiveIonescu().detect(data, sampling_rate_hz=sampling_rate_hz).gs_list_.itertuples()
    ]
    records, events = [], []
    for start, end in bouts:
        if not 0 <= start < end <= len(data):
            raise ValueError('Detector produced invalid bout bounds')
        ic = IcdShinImproved(axis='norm').detect(
            data.iloc[start:end].reset_index(drop=True), sampling_rate_hz=sampling_rate_hz
        ).ic_list_.ic.to_numpy(dtype=int)
        ic = np.unique(ic[(ic >= 0) & (ic < end-start)]) + start
        cadence = float(60*(len(ic)-1)*sampling_rate_hz/(ic[-1]-ic[0])) if len(ic) >= 2 else None
        records.append(dict(start=start, end=end, contacts=len(ic), cadence=cadence))
        events.extend(ic.tolist())
    return {'status': 'ok' if events else 'no_contacts', 'bouts': records,
            'events': sorted(set(events))}


def match_events(reference, predicted, tolerance_samples):
    """Maximum-cardinality ordered 1:1 matching within a fixed tolerance.

    Earliest feasible pairs; no duplicate reference credit. Timing residuals
    describe these pairs, not a post-hoc optimized temporal alignment.
    """
    ref = np.sort(np.asarray(reference, dtype=int))
    pred = np.sort(np.asarray(predicted, dtype=int))
    i = j = 0
    residuals = []
    while i < len(ref) and j < len(pred):
        if pred[j] < ref[i] - tolerance_samples:
            j += 1
        elif pred[j] > ref[i] + tolerance_samples:
            i += 1
        else:
            residuals.append(int(pred[j]-ref[i])); i += 1; j += 1
    tp = len(residuals)
    return dict(tp=tp, fp=len(pred)-tp, fn=len(ref)-tp, residuals=residuals)
