import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import run_tvs_hallway_probe as probe


class HallwayProbeTests(unittest.TestCase):
    def test_empty_and_present_turn_fields_remain_distinct(self):
        rows = probe.annotation_audit({'Stereophoto': {'ContinuousWalkingPeriod': [
            {'Turning_SharpTurn_Flag': []}, {'Turning_SharpTurn_Flag': [1]}]}})
        self.assertEqual([r['empty'] for r in rows], [True, False])
        self.assertEqual([r['size'] for r in rows], [0, 1])
        self.assertNotEqual(rows[0]['path'], rows[1]['path'])

    def test_changed_protocol_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'protocol.json'
            path.write_text(json.dumps({'threshold': .5}))
            digest = probe.sha(path)
            path.write_text(json.dumps({'threshold': .9}))
            with self.assertRaisesRegex(ValueError, 'Changed locked artifact'):
                probe.checked_json(path, digest)

    def test_existing_results_prevent_new_lock_or_scoring(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp)
            (out / 'results.json').write_text('saved results')
            with patch.object(probe, 'OUT', out), patch.object(probe, 'protocol') as lock:
                with self.assertRaises(FileExistsError):
                    probe.main()
                lock.assert_not_called()
            self.assertEqual((out / 'results.json').read_text(), 'saved results')


if __name__ == '__main__':
    unittest.main()
