"""Algebraic checks for a steady alternating gait specification, not clinical validation."""
from math import isfinite


def derive_cycle(*, speed_m_s, cadence_steps_min, paretic_step_length_ratio,
                 opposite_contact_phase, paretic_stance_fraction,
                 nonparetic_stance_fraction):
    """P contact is phase 0, NP contact is phase phi, next P contact phase 1.

    Assumes steady forward progression, two positive steps per cycle and no
    flight. Treadmill speed means progression relative to the belt, not lab-frame
    pelvis speed. No diagnosis, severity or physiological feasibility is inferred.
    """
    values = [speed_m_s, cadence_steps_min, paretic_step_length_ratio,
              opposite_contact_phase, paretic_stance_fraction,
              nonparetic_stance_fraction]
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not isfinite(v)
           for v in values):
        raise ValueError('All parameters must be finite real scalars, not booleans.')
    if min(values[:3]) <= 0:
        raise ValueError('Speed, cadence and step-length ratio must be positive.')
    phi, dp, dn = values[3:]
    if not all(0 < v < 1 for v in [phi, dp, dn]):
        raise ValueError('Contact phase and stance fractions must lie strictly inside (0, 1).')
    if dp < phi or dn < 1 - phi:
        raise ValueError('Stance intervals leave flight gaps; outside this walking contract.')
    duration = 120 / cadence_steps_min
    stride = speed_m_s * duration
    np_step = stride / (1 + paretic_step_length_ratio)
    return dict(
        cycle_duration_s=duration,
        paretic_step_length_m=stride - np_step,
        nonparetic_step_length_m=np_step,
        paretic_step_time_s=(1 - phi) * duration,
        nonparetic_step_time_s=phi * duration,
        paretic_stance_s=dp * duration,
        nonparetic_stance_s=dn * duration,
        paretic_swing_s=(1 - dp) * duration,
        nonparetic_swing_s=(1 - dn) * duration,
        initial_double_support_fraction=phi + dn - 1,
        terminal_double_support_fraction=dp - phi,
        total_double_support_fraction=dp + dn - 1,
        status='algebraically_consistent_not_clinically_validated',
    )
