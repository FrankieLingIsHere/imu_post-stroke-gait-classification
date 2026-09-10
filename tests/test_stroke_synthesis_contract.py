import unittest
from src.data.stroke_synthesis_contract import derive_cycle


class CycleContractTests(unittest.TestCase):
    def spec(self, **changes):
        # Engineering fixtures, not clinical stroke parameter recommendations.
        p = dict(speed_m_s=1., cadence_steps_min=100., paretic_step_length_ratio=1.,
                 opposite_contact_phase=.5, paretic_stance_fraction=.6,
                 nonparetic_stance_fraction=.6)
        p.update(changes)
        return derive_cycle(**p)

    def test_symmetric_closure(self):
        x = self.spec()
        self.assertAlmostEqual(x['cycle_duration_s'], 1.2)
        self.assertAlmostEqual(x['paretic_step_length_m'], .6)
        self.assertAlmostEqual(x['total_double_support_fraction'], .2)

    def test_asymmetry_directions_and_speed_closure(self):
        for ratio in [.7, 1.5]:
            x = self.spec(paretic_step_length_ratio=ratio)
            self.assertAlmostEqual(x['paretic_step_length_m']/x['nonparetic_step_length_m'], ratio)
            self.assertAlmostEqual((x['paretic_step_length_m']+x['nonparetic_step_length_m'])/x['cycle_duration_s'], 1.)

    def test_periodic_contact_overlap(self):
        x = self.spec(opposite_contact_phase=.4, paretic_stance_fraction=.55,
                      nonparetic_stance_fraction=.7)
        self.assertAlmostEqual(x['initial_double_support_fraction'], .1)
        self.assertAlmostEqual(x['terminal_double_support_fraction'], .15)
        self.assertAlmostEqual(x['paretic_stance_s']+x['paretic_swing_s'], x['cycle_duration_s'])
        self.assertAlmostEqual(x['paretic_step_time_s']+x['nonparetic_step_time_s'], x['cycle_duration_s'])

    def test_rejects_flight_on_either_transition(self):
        for changes in [dict(paretic_stance_fraction=.4), dict(nonparetic_stance_fraction=.4)]:
            with self.assertRaises(ValueError): self.spec(**changes)

    def test_invalid_values(self):
        for key in ['speed_m_s', 'cadence_steps_min', 'paretic_step_length_ratio',
                    'opposite_contact_phase', 'paretic_stance_fraction', 'nonparetic_stance_fraction']:
            for value in [0, -1, float('nan'), float('inf'), True, None]:
                with self.assertRaises(ValueError): self.spec(**{key: value})


if __name__ == '__main__':
    unittest.main()
