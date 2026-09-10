"""Metadata intake must work offline and reject corrupt cached evidence."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zlib

from scipy.io import savemat
from scripts import screen_tvs_lab_metadata as intake


class MetadataIntakeTests(unittest.TestCase):
    def test_offline_cache_and_integrity(self):
        with tempfile.TemporaryDirectory() as temporary:
            base=Path(temporary);folder=base/'HA'/'9999';folder.mkdir(parents=True)
            tests={'data':[
                {'key':['TimeMeasure1','Test5','Trial1'],
                 'value':{'available_sensors':[['SU','LowerBack']],
                          'available_reference_systems':['Stereophoto']}},
                # Later failed retry must not silently fall back to Trial1.
                {'key':['TimeMeasure1','Test5','Trial2'],
                 'value':{'available_sensors':[], 'available_reference_systems':[]}}]}
            (folder/'test_list.json').write_text(json.dumps(tests))
            savemat(folder/'infoForAlgo.mat',{'infoForAlgo':{'TimeMeasure1':{
                'SensorType_SU':'MM+','WalkingAid_01':0}}})
            entries=[]
            for name in ('test_list.json','infoForAlgo.mat'):
                raw=(folder/name).read_bytes()
                entries.append(dict(name=f'HA/9999/Laboratory/{name}',size=len(raw),crc32=zlib.crc32(raw)))
            with patch.object(intake,'OUT',base),patch.object(intake,'member_bytes',side_effect=AssertionError('Network used')):
                result=intake.screen(('HA',entries))
                task=next(t for t in result['tasks'] if t['task']=='Test5')
                self.assertEqual(task['trial'],'Trial2')
                self.assertFalse(task['has_lower_back'])
                self.assertFalse(task['has_stereophoto'])
                (folder/'test_list.json').write_text('{}')
                with self.assertRaisesRegex(ValueError,'CRC mismatch'):
                    intake.screen(('HA',entries))


if __name__=='__main__':unittest.main()
