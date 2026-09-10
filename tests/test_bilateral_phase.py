import unittest
import numpy as np
from src.features.bilateral_phase import extract_phase, FEATURES


class PhaseTest(unittest.TestCase):
    def gait(self, offset=.5):
        return [[i-.4, i] for i in range(1, 9)], [[i+offset-.4, i+offset] for i in range(1, 9)]

    def test_symmetric_support(self):
        x = extract_phase(*self.gait(), [20, 21], 1)
        self.assertAlmostEqual(x['step_asymmetry'], 0)
        self.assertAlmostEqual(x['swing_fraction'], .4)
        self.assertAlmostEqual(x['double_support_fraction'], .2)

    def test_equal_stride_unequal_steps_and_side_swap(self):
        l, r = self.gait(.3)
        x = extract_phase(l, r, [20, 21], 1)
        self.assertAlmostEqual(x['step_asymmetry'], .8)
        y = extract_phase(r, l, [20, 21], 1)
        for key in FEATURES:
            self.assertAlmostEqual(x[key], y[key])

    def test_turn_and_missing(self):
        l, r = self.gait()
        x = extract_phase(l, r, [3, 6], 1)
        self.assertGreater(x['turn_pairs'], 0)
        self.assertLess(x['valid_cycles'], 14)
        r = r[:3] + r[4:]
        y = extract_phase(l, r, [20, 21], 1)
        self.assertGreater(y['invalid_cycles'], 0)

    def test_malformed_and_empty(self):
        x = extract_phase([[2, 1]], [], [20, 21], 1)
        self.assertEqual(x['malformed_pairs'], 1)
        self.assertTrue(all(np.isnan(x[k]) for k in FEATURES))


if __name__ == '__main__':
    unittest.main()
