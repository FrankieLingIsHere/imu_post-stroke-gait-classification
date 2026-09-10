"""Label-independent features from annotated [toe-off, heel-strike] pairs.

Reference-assisted feasibility only; does not estimate events from IMU signals.
"""
import numpy as np

FEATURES = ['step_asymmetry', 'swing_asymmetry', 'stance_asymmetry',
            'swing_fraction', 'double_support_fraction']


def extract_phase(left, right, turn, frequency, return_stances=False):
    if frequency <= 0 or len(turn) != 2 or turn[0] > turn[1]:
        raise ValueError('Invalid clock or turn')
    counts = dict(malformed_pairs=0, turn_pairs=0, invalid_cycles=0,
                  valid_cycles=0, valid_step_pairs=0, valid_support_cycles=0)
    swings, stances, steps = [[], []], [[], []], [[], []]
    fractions, supports = [], []
    segments = [[[], []], [[], []]]
    for side, events in enumerate((left, right)):
        previous = -np.inf
        for pair in events:
            if len(pair) != 2 or not np.isfinite(pair).all() or not previous < pair[0] < pair[1]:
                counts['malformed_pairs'] += 1
                # Barrier prevents constructing a cycle across a malformed row.
                for segment in segments:
                    segment[side].append(None)
                continue
            previous = pair[1]
            if pair[1] < turn[0]:
                segments[0][side].append(pair)
            elif pair[0] > turn[1]:
                segments[1][side].append(pair)
            else:
                counts['turn_pairs'] += 1
    stance_segments = []
    for segment in segments:
        cycles = [[], []]
        segment_stances = [[], []]
        for side in (0, 1):
            opposite = [p[1] for p in segment[1-side] if p is not None]
            for a, b in zip(segment[side], segment[side][1:]):
                if a is None or b is None:
                    counts['invalid_cycles'] += 1
                    continue
                to, hs = a
                next_to, next_hs = b
                contacts = [x for x in opposite if hs < x < next_hs]
                if not to < hs < next_to < next_hs or len(contacts) != 1:
                    counts['invalid_cycles'] += 1
                    continue
                counts['valid_cycles'] += 1
                cycles[side].append((hs, next_to, next_hs))
                swings[side].append((next_hs-next_to)/frequency)
                stances[side].append((next_to-hs)/frequency)
                segment_stances[side].append((next_to-hs)/frequency)
                fractions.append((next_hs-next_to)/(next_hs-hs))
                # Each cycle supplies one step landing on each side.
                steps[1-side].append((contacts[0]-hs)/frequency)
                steps[side].append((next_hs-contacts[0])/frequency)
                counts['valid_step_pairs'] += 1
        for start, toe, end in cycles[0]:
            covering = [(max(start, a), min(end, c)) for a, b, c in cycles[1]
                        if a < end and c > start]
            covered = sum(max(0, b-a) for a, b in covering)
            if not np.isclose(covered, end-start):
                continue
            overlap = sum(max(0, min(toe, b)-max(start, a)) for a, b, c in cycles[1])
            supports.append(overlap/(end-start))
            counts['valid_support_cycles'] += 1
        stance_segments.append(segment_stances)
    def asym(values):
        if min(map(len, values)) < 2:
            return np.nan
        a, b = map(np.mean, values)
        return abs(a-b)/((a+b)/2)
    result = dict(step_asymmetry=asym(steps), swing_asymmetry=asym(swings),
                stance_asymmetry=asym(stances),
                swing_fraction=np.mean(fractions) if len(fractions) >= 4 else np.nan,
                double_support_fraction=np.mean(supports) if len(supports) >= 2 else np.nan,
                **counts)
    if return_stances:
        result['stance_segments'] = stance_segments
    return result
