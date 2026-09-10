"""A failed download must never silently reduce an evaluated cohort."""
from contextlib import ExitStack
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import run_tvs_locked_pilot as pilot


class LockedPilotTests(unittest.TestCase):
    def setup_lock(self, out):
        protocol = dict(adapter_sha256=pilot.sha(pilot.ROOT / 'src/data/tvs.py'),
                        selected=[dict(cohort='HA', participant='1234')])
        path = out / 'protocol.json'
        path.write_text(json.dumps(protocol))
        (out / 'protocol.sha256').write_text(pilot.sha(path))
        return protocol

    def test_crc_failure_stops_before_scoring_and_is_not_quality_exclusion(self):
        with tempfile.TemporaryDirectory() as temp, ExitStack() as stack:
            out = Path(temp)
            protocol = self.setup_lock(out)
            stack.enter_context(patch.object(pilot, 'OUT', out))
            stack.enter_context(patch.object(pilot, 'lock', return_value=protocol))
            stack.enter_context(patch.object(pilot, 'acquire', side_effect=ValueError('Member CRC/size mismatch')))
            stack.enter_context(patch('sys.argv', ['pilot']))
            with self.assertRaisesRegex(RuntimeError, 'Incomplete acquisition; no scoring'):
                pilot.main()
            rows = json.loads((out / 'intake.json').read_text())
            self.assertEqual(rows[0]['status'], 'transfer_or_execution_failure')
            self.assertFalse((out / 'results.json').exists())

    def test_existing_result_is_preserved_without_acquiring_again(self):
        with tempfile.TemporaryDirectory() as temp, ExitStack() as stack:
            out = Path(temp)
            protocol = self.setup_lock(out)
            result = out / 'results.json'
            result.write_text('immutable result')
            stack.enter_context(patch.object(pilot, 'OUT', out))
            stack.enter_context(patch.object(pilot, 'lock', return_value=protocol))
            acquire = stack.enter_context(patch.object(pilot, 'acquire'))
            stack.enter_context(patch('sys.argv', ['pilot']))
            with self.assertRaises(FileExistsError):
                pilot.main()
            acquire.assert_not_called()
            self.assertEqual(result.read_text(), 'immutable result')

    def test_changed_protocol_stops_before_acquisition(self):
        with tempfile.TemporaryDirectory() as temp, ExitStack() as stack:
            out = Path(temp)
            protocol = self.setup_lock(out)
            (out / 'protocol.json').write_text('{}')
            stack.enter_context(patch.object(pilot, 'OUT', out))
            stack.enter_context(patch.object(pilot, 'lock', return_value=protocol))
            acquire = stack.enter_context(patch.object(pilot, 'acquire'))
            stack.enter_context(patch('sys.argv', ['pilot']))
            with self.assertRaisesRegex(ValueError, 'Protocol changed'):
                pilot.main()
            acquire.assert_not_called()


if __name__ == '__main__':
    unittest.main()
