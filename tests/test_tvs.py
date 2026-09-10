import unittest
import numpy as np
from src.data.tvs import interval, trial_windows


def recording(start=.01, end=5, length=1000):
    return {'SU': {'LowerBack': {'Acc': np.tile([0., 0., 1.], (length, 1)),
            'Fs': {'Acc': 100}, 'Timestamp': np.arange(length)/100}},
            'Standards': {'Stereophoto': {'ContinuousWalkingPeriod':
                {'Start': start, 'End': end}}}}


class TVSAdapterTests(unittest.TestCase):
    def test_matlab_endpoints_and_exact_five_seconds(self):
        self.assertEqual(interval(.01, 5, 1000), (0, 500))
        x, rows, _ = trial_windows(recording())
        self.assertEqual(x.shape, (1, 500, 1))
        np.testing.assert_array_equal(x, 1.)
        self.assertEqual(rows[0]['end'], 500)

    def test_short_bouts_never_padded_or_concatenated(self):
        r = recording()
        r['Standards']['Stereophoto']['ContinuousWalkingPeriod'] = [
            {'Start': .01, 'End': 4.99}, {'Start': 5.01, 'End': 9.99}]
        self.assertEqual(len(trial_windows(r)[0]), 0)

    def test_reject_timestamp_gap_and_nonfinite_signal(self):
        r = recording(); r['SU']['LowerBack']['Timestamp'][501:] += .01
        with self.assertRaisesRegex(ValueError, 'Timestamp gaps'):
            trial_windows(r)
        r = recording(); r['SU']['LowerBack']['Acc'][0, 0] = np.nan
        with self.assertRaises(ValueError): trial_windows(r)

    def test_bounds_and_missing_reference(self):
        with self.assertRaises(ValueError): interval(0, 5, 1000)
        with self.assertRaises(ValueError): interval(.01, 11, 1000)
        r = recording(); r['Standards'] = {}
        self.assertEqual(len(trial_windows(r)[0]), 0)

    def test_no_window_crosses_break(self):
        r = recording(end=10)
        r['Standards']['Stereophoto']['ContinuousWalkingPeriod'].update(
            Break_Start=4., Break_End=6.)
        self.assertEqual(len(trial_windows(r)[0]), 0)


if __name__ == '__main__': unittest.main()
