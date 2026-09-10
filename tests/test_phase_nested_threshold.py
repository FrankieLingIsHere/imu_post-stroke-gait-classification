import unittest
import numpy as np
from scripts.run_phase_nested_threshold import sensitivity_threshold


class ThresholdTest(unittest.TestCase):
    def test_largest_feasible_threshold(self):
        scores=np.linspace(.1,1,10)
        threshold=sensitivity_threshold(scores)
        self.assertAlmostEqual(threshold,.2)
        self.assertGreaterEqual(np.mean(scores>=threshold),.9)
        self.assertLess(np.mean(scores>=np.nextafter(threshold,np.inf)),.9)

    def test_small_sample_and_ties(self):
        self.assertEqual(sensitivity_threshold([.2,.2,.8]),.2)

    def test_invalid(self):
        for scores in [[],[np.nan]]:
            with self.assertRaises(ValueError):
                sensitivity_threshold(scores)


if __name__=='__main__':
    unittest.main()
