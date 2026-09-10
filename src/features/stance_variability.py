"""Within-side, within-straight-bout stance-duration CV, annotation assisted."""
import numpy as np


def stance_cv(segments, min_cycles=5):
    side_values = [[], []]
    counts = [0, 0]
    eligible = 0
    for segment in segments:
        for side in (0, 1):
            values = np.asarray(segment[side], dtype=float)
            if not np.isfinite(values).all() or (values <= 0).any():
                raise ValueError('Invalid stance durations')
            counts[side] += len(values)
            if len(values) >= min_cycles:
                side_values[side].append(float(np.std(values, ddof=1)/np.mean(values)))
                eligible += 1
    # Equal weight per side and per eligible bout, not pooled left/right durations.
    value = float(np.mean([np.mean(x) for x in side_values])) if all(side_values) else np.nan
    return dict(stance_duration_cv=value, left_cycles=counts[0], right_cycles=counts[1],
                eligible_side_bouts=eligible)
