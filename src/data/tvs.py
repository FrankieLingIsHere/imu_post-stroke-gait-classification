"""TVS laboratory lower-back adapter for schema-development smoke tests.

Native Acc is in g. Reference intervals follow mobgap's MATLAB convention:
round(Start*Fs)-1 through round(End*Fs), end-exclusive in Python.
No padding, reference fallback, gravity subtraction or normalization is applied.
Turns are not reliably annotated by these references; this is not a straight-
walking eligibility gate for a final clinical evaluation.
"""
import numpy as np

WINDOW, HOP = 500, 250
TASKS = ('Test5', 'Test6', 'Test7', 'Test10')


def interval(start, end, length):
    if not np.isfinite([start, end]).all() or end <= start:
        raise ValueError('Invalid reference interval')
    begin, stop = int(np.rint(start * 100)) - 1, int(np.rint(end * 100))
    if begin < 0 or stop > length or stop <= begin:
        raise ValueError('Reference interval outside sensor recording')
    return begin, stop


def trial_windows(recording):
    sensor = recording['SU']['LowerBack']
    if sensor['Fs']['Acc'] != 100:
        raise ValueError('Only native 100 Hz acceleration is supported')
    acc = np.asarray(sensor['Acc'], dtype=np.float32)
    if acc.ndim != 2 or acc.shape[1] != 3 or not np.isfinite(acc).all():
        raise ValueError('Expected finite N-by-3 raw acceleration in g')
    stamps = np.asarray(sensor['Timestamp']).reshape(-1)
    if len(stamps) != len(acc) or not np.isfinite(stamps).all() or np.any(np.diff(stamps) <= 0):
        raise ValueError('Invalid timestamps')
    if not np.allclose(np.diff(stamps), .01, atol=.0001, rtol=0):
        raise ValueError('Timestamp gaps or irregular native sampling')
    reference = recording.get('Standards', {}).get('Stereophoto', {})
    bouts = reference.get('ContinuousWalkingPeriod', [])
    bouts = [bouts] if isinstance(bouts, dict) else list(bouts)
    windows, metadata, audit = [], [], []
    magnitude = np.linalg.norm(acc, axis=1)
    previous_end = -1
    for bout_id, bout in enumerate(bouts):
        begin, stop = interval(bout['Start'], bout['End'], len(acc))
        if begin < previous_end:
            raise ValueError('Overlapping or unsorted reference bouts')
        previous_end = stop
        breaks_start = np.asarray(bout.get('Break_Start', [])).reshape(-1)
        breaks_end = np.asarray(bout.get('Break_End', [])).reshape(-1)
        if len(breaks_start) != len(breaks_end):
            raise ValueError('Unpaired reference breaks')
        breaks = [interval(a, b, len(acc)) for a, b in zip(breaks_start, breaks_end)]
        count = 0
        for start in range(begin, stop-WINDOW+1, HOP):
            end = start+WINDOW
            if any(start < b and end > a for a, b in breaks):
                continue
            windows.append(magnitude[start:end, None])
            metadata.append(dict(bout_id=bout_id, start=start, end=end,
                                 reference_start=begin, reference_end=stop))
            count += 1
        audit.append(dict(bout_id=bout_id, start=begin, end=stop, windows=count,
                          status='included' if count else 'no_complete_5s_window'))
    if not bouts:
        audit.append(dict(status='missing_reference_bouts', windows=0))
    return (np.stack(windows) if windows else np.empty((0, WINDOW, 1), dtype=np.float32),
            metadata, audit)
