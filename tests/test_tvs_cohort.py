import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
from scripts import run_tvs_cohort as cohort


class CohortTests(unittest.TestCase):
    def person(self):
        return {'tasks':[dict(task='Test10',sensor='MM+',walking_aid=0,
                             has_lower_back=True,has_stereophoto=True,annotations={})]}

    def test_eligible_and_explicit_exclusion_reasons(self):
        p=self.person()
        self.assertIsNone(cohort.metadata_decision(p)[1])
        p['tasks'][0].update(walking_aid=1,has_stereophoto=False)
        self.assertEqual(cohort.metadata_decision(p)[1],
                         'has_stereophoto_absent,walking_aid_or_unknown')
        self.assertEqual(cohort.metadata_decision({'tasks':[]})[1],
                         'missing_or_ambiguous_hallway_task')

    def test_existing_cohort_result_stops_before_lock_or_acquisition(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp);(out/'results.json').write_text('preserved')
            with patch.object(cohort,'OUT',out),patch.object(cohort,'locked_protocol') as lock:
                with self.assertRaises(FileExistsError):cohort.main()
                lock.assert_not_called()
            self.assertEqual((out/'results.json').read_text(),'preserved')

    def test_failed_transfer_stops_before_any_cohort_scoring(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)
            p=dict(hashes={},people=[dict(cohort='HA',participant='1234',metadata_exclusion=None)])
            with patch.object(cohort,'OUT',out),patch.object(cohort,'locked_protocol',return_value=p),patch.object(cohort,'local_raw',side_effect=ValueError('bad CRC')):
                with self.assertRaisesRegex(RuntimeError,'No cohort scoring'):cohort.main()
            self.assertFalse((out/'results.json').exists())
            self.assertIn('transfer_failure',(out/'intake.json').read_text())


if __name__=='__main__':unittest.main()
