import hashlib
import io
import json
import os
import tempfile
import time
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

import numpy as np

from distance_pipeline import CORRECTED, LEGACY, processing_spec, quiet_initialization, validate_engine_capabilities
from test_distance_validation import capture


def quiet_capture(*, quiet_after=1, gap=False, walking_start=5):
    content = io.BytesIO()
    samples = []
    for i in range(1200):
        t = 1_000_000_000+i*5_000_000
        if gap and 1.5 < i*.005 < 1.6: continue
        moving = i*.005 < quiet_after
        for sensor, xyz in [('accelerometer', [0, 0, 9.80665]),
                            ('gyroscope', [.2 if moving else 0, 0, 0])]:
            samples.append(dict(sensor=sensor, timestampNs=t, x=xyz[0], y=xyz[1], z=xyz[2]))
    with zipfile.ZipFile(content, 'w') as z:
        z.writestr('manifest.json', json.dumps({'startedBootNs':1_000_000_000,
            'diagnostics':{'walkStartedBootNs':1_000_000_000+int(walking_start*1e9)}}))
        z.writestr('imu.ndjson', '\n'.join(json.dumps(r) for r in samples))
    return content.getvalue()


class DistancePipelineChecks(unittest.TestCase):
    def test_quiet_gate_keeps_two_seconds_and_excludes_placement_motion(self):
        source=quiet_capture()
        stream=io.BytesIO(source);value=quiet_initialization(stream, .0268)
        self.assertEqual(value['startBootNs'],2_000_000_000)
        self.assertEqual(value['quietEndBootNs'],4_000_000_000)
        self.assertEqual(value['excludedPrefixSeconds'],1)
        self.assertFalse(value['placementAnatomicallyVerified'])
        self.assertEqual(source,stream.getvalue())

    def test_gap_and_no_pre_walk_quietness_cannot_pass(self):
        with self.assertRaisesRegex(ValueError,'No continuous quiet'):
            quiet_initialization(io.BytesIO(quiet_capture(gap=True,walking_start=3.4)),.0268)
        with self.assertRaisesRegex(ValueError,'No continuous quiet'):
            quiet_initialization(io.BytesIO(quiet_capture(quiet_after=5)),.0268)

    def test_corrected_engine_requires_both_timing_and_initialization_capabilities(self):
        base={'distanceProtocolVersion':2,'fixedGeometry':True,'fixedTimeOffset':True}
        with patch.dict(os.environ,{'GAITTRACE_DISTANCE_PIPELINE':CORRECTED}):spec=processing_spec()
        self.assertFalse(validate_engine_capabilities(base,spec))
        self.assertFalse(validate_engine_capabilities({**base,'fixedTimeRowCorrection':True},spec))
        self.assertTrue(validate_engine_capabilities({**base,'fixedTimeRowCorrection':True,'replayInitializationWindow':True},spec))
        with patch.dict(os.environ,{'GAITTRACE_DISTANCE_PIPELINE':LEGACY}):old=processing_spec()
        self.assertTrue(validate_engine_capabilities(base,old))
        self.assertNotEqual(old['revision'],spec['revision'])

    def test_processing_revision_changes_job_key_without_overwriting_completed_record(self):
        from calibration_companion import Companion
        with tempfile.TemporaryDirectory() as temp:
            source,_=capture(temp);body=source.read_bytes();calls=[]
            service=Companion(Path(temp)/'jobs',distance_runner=lambda p:calls.append(p) or {'distanceReady':False})
            with patch.dict(os.environ,{'GAITTRACE_DISTANCE_PIPELINE':LEGACY}):
                old=service.submit(body,3)
                while service.processing:time.sleep(.005)
                previous=(service.folder/old/'job.json').read_bytes()
            with patch.dict(os.environ,{'GAITTRACE_DISTANCE_PIPELINE':CORRECTED}):
                new=service.submit(body,3)
                while service.processing:time.sleep(.005)
                self.assertEqual(service.submit(body,3),new)
            self.assertNotEqual(old,new);self.assertEqual(len(calls),2)
            self.assertEqual((service.folder/old/'job.json').read_bytes(),previous)
            self.assertEqual((service.folder/new/'input.zip').read_bytes(),body)
            self.assertEqual(json.loads((service.folder/new/'request.json').read_text())['processingMode'],CORRECTED)

    def test_saved_revision_cannot_silently_use_changed_method(self):
        from distance_validation import run_distance
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp);(p/'request.json').write_text(json.dumps({'referenceDistanceMetres':3,'processingRevision':'older-method'}))
            with self.assertRaisesRegex(ValueError,'Processing method changed'):run_distance(p)
            self.assertFalse((p/'replay').exists())

    def test_invalid_processing_mode_does_not_fallback(self):
        with patch.dict(os.environ,{'GAITTRACE_DISTANCE_PIPELINE':'typo'}):
            with self.assertRaisesRegex(ValueError,'Invalid'):processing_spec()

    def test_backend_choice_is_part_of_processing_identity(self):
        with patch.dict(os.environ,{'GAITTRACE_VIO_BACKEND':'cpu'}):cpu=processing_spec()
        with patch.dict(os.environ,{'GAITTRACE_VIO_BACKEND':'cuda'}):cuda=processing_spec()
        self.assertNotEqual(cpu['revision'],cuda['revision'])

    def test_updated_noise_profile_creates_a_separate_job_and_snapshots_its_bytes(self):
        from calibration_companion import Companion
        with tempfile.TemporaryDirectory() as temp:
            source,_=capture(temp);body=source.read_bytes()
            with zipfile.ZipFile(source) as z:meta=json.loads(z.read('manifest.json'))
            service=Companion(Path(temp)/'jobs',distance_runner=lambda _: {'distanceReady':False})
            first=service.submit(body,3)
            while service.processing:time.sleep(.005)
            profiles=service.folder/'noise-profiles';profiles.mkdir()
            profile=profiles/hashlib.sha256(meta['installationId'].encode()).hexdigest()
            data=b'{"candidate":"labelled fake, job identity test only"}';profile.write_bytes(data)
            second=service.submit(body,3)
            while service.processing:time.sleep(.005)
            self.assertNotEqual(first,second)
            self.assertEqual((service.folder/second/'noise-report.json').read_bytes(),data)
            self.assertEqual(json.loads((service.folder/second/'request.json').read_text())['noiseProfileSha256'],hashlib.sha256(data).hexdigest())

    def test_windows_build_keeps_linux_output_path_absolute(self):
        import subprocess
        from distance_pipeline import setup_distance_engine
        capability=json.dumps({'distanceProtocolVersion':2,'fixedGeometry':True,'fixedTimeOffset':True,
                               'fixedTimeRowCorrection':True,'replayInitializationWindow':True})
        with patch.dict(os.environ,{'GAITTRACE_DISTANCE_PIPELINE':CORRECTED}), \
                patch('subprocess.run',return_value=subprocess.CompletedProcess([],0,stdout=capability)) as run:
            setup_distance_engine()
            commands=[call.args[0] for call in run.call_args_list]
            configure=next(c for c in commands if '-B' in c)
            self.assertEqual(configure[configure.index('-B')+1],'/root/gaittrace-vio/distance-build-v3')
            self.assertNotIn('\\',configure[configure.index('-B')+1])


if __name__=='__main__':unittest.main()
