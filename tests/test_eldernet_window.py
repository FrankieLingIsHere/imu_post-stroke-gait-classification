import unittest
import numpy as np
from scripts.classification.probe_eldernet_lower_back import to_eldernet_window


class ElderNetWindowTest(unittest.TestCase):
    def test_physical_units_and_channel_identity(self):
        x = np.tile([9.80665, 0., -19.6133], (1000, 1))
        y = to_eldernet_window(x)
        self.assertEqual(y.shape, (3, 300))
        # Allow the polyphase filter's small phase-dependent DC ripple.
        np.testing.assert_allclose(y[0, 20:-20], 1., atol=5e-5)
        np.testing.assert_allclose(y[1], 0.)
        np.testing.assert_allclose(y[2, 20:-20], -2., atol=5e-5)

    def test_no_short_or_nonfinite_windows(self):
        for x in [np.ones((500,3)), np.full((1000,3), np.nan)]:
            with self.assertRaises(ValueError):
                to_eldernet_window(x)


if __name__ == '__main__':
    unittest.main()
