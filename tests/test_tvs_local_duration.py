"""Offline duration-screen checks using small MATLAB fixtures."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from scipy.io import savemat

from scripts import screen_tvs_local_duration as screen


class LocalDurationTests(unittest.TestCase):
    def fixture(self, root):
        base = root / 'data/interim/public_imu_screen_2026-09-08'
        folder = base / 'HA_sample'
        folder.mkdir(parents=True)
        trial = {'SU': {'LowerBack': {'Acc': np.ones((1000, 3)),
                 'Fs': {'Acc': 100}, 'Timestamp': np.arange(1000) / 100}},
                 'Standards': {'Stereophoto': {'ContinuousWalkingPeriod':
                              {'Start': .01, 'End': 5.}}}}
        short = {'SU': trial['SU'], 'Standards': {'Stereophoto': {
                 'ContinuousWalkingPeriod': {'Start': .01, 'End': 4.99}}}}
        path = folder / 'data.mat'
        savemat(path, {'data': {'TimeMeasure1': {
            'Test5': {'Trial1': trial, 'Trial2': short},
            'Test10': {'Trial1': trial}}}})
        (base / 'sample_manifest.json').write_text(json.dumps([
            dict(member='HA/1234/Laboratory/data.mat',
                 sha256=hashlib.sha256(path.read_bytes()).hexdigest())]))
        return base, path

    def test_final_trial_shortage_is_not_replaced_by_longer_earlier_trial(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            base, _ = self.fixture(root)
            with patch.object(screen, 'ROOT', root), patch('builtins.print'):
                screen.main()
            result = json.loads((base / 'local_duration_screen.json').read_text())
            rows = {row['task']: row for row in result['rows']}
            self.assertEqual(rows['Test5']['trial'], 'Trial2')
            self.assertEqual(rows['Test5']['windows'], 0)
            self.assertEqual(rows['Test10']['windows'], 1)
            self.assertEqual(rows['Test6']['status'], 'missing_task')
            self.assertEqual(result['source_count'], 1)

    def test_corrupt_raw_member_stops_screen_without_result(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            base, path = self.fixture(root)
            path.write_bytes(path.read_bytes() + b'corruption')
            with patch.object(screen, 'ROOT', root):
                with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
                    screen.main()
            self.assertFalse((base / 'local_duration_screen.json').exists())


if __name__ == '__main__':
    unittest.main()
