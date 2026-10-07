import csv
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

import cv2
import numpy as np

from vio_reference import export_capture, write_reference_config, summarize_reference


class ReferenceContractTests(unittest.TestCase):
    def fixture(self, directory, *, bad_units=False, bad_profile=False, duplicate=False, bad_optics=False):
        binding = {'installationId': 'fixture', 'cameraId': '1', 'width': 640, 'height': 480,
                   'imageAxes': 'native-sensor-unrotated-unmirrored', 'sensorOrientationDegrees': 270}
        manifest = dict(binding, captureId='fixture', timestampSource='realtime',
                        diagnostics={'walkStartedBootNs':1_010_000_000},
                        units={'accelerometer': 'g' if bad_units else 'm/s2', 'gyroscope': 'rad/s'})
        profile = {'binding': dict(binding), 'lens': {'cameraMatrix': [[500,0,320],[0,500,240],[0,0,1]],
                      'distortion': [.1,-.2,0,0,.3]},
                   'rotationTiming': {'rotationImuToCamera': [[0,-1,0],[1,0,0],[0,0,1]],
                                      'residualTimeOffsetSeconds': -.025}}
        if bad_profile:
            profile['binding']['cameraId'] = '0'
        if bad_optics:
            manifest.update(capturePipeline='native-camera-imu-v2',opticalSetup='waist-bag-window')
            profile['binding'].update(capturePipeline='native-camera-imu-v2',opticalSetup='clear-lens')
        imu = []
        for i in range(6):
            t = 1_000_000_000+i*5_000_000
            imu.append(dict(sensor='accelerometer', timestampNs=t, x=i, y=0, z=9.8))
            imu.append(dict(sensor='gyroscope', timestampNs=t+1_000_000, x=.1, y=.2, z=.3))
        if duplicate:
            imu.append(imu[0])
        frames = [dict(file=f'frames/{i}.jpg', timestampNs=1_005_000_000+i*10_000_000) for i in range(2)]
        capture = [dict(timestampNs=r['timestampNs'], exposureNs=2_000_000, rollingShutterSkewNs=4_000_000) for r in frames]
        _, image = cv2.imencode('.jpg', np.zeros((480,640), np.uint8))
        path = directory/'fixture.zip'
        with zipfile.ZipFile(path, 'w') as bundle:
            for name, data in [('manifest.json',manifest), ('research-profile.json',profile)]:
                bundle.writestr(name,json.dumps(data))
            for name,data in [('imu.ndjson',imu), ('frames.ndjson',frames), ('capture-results.ndjson',capture)]:
                bundle.writestr(name,'\n'.join(json.dumps(r) for r in data))
            for r in frames:
                bundle.writestr(r['file'],image.tobytes())
        return path

    def test_clock_interpolation_no_camera_upsampling_and_rotation_direction(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp)
            summary = export_capture(self.fixture(p),p/'out')
            self.assertEqual(summary['frameCount'],2)
            self.assertEqual(summary['pairedImuCount'],5)
            self.assertEqual(summary['discardedUnbracketedGyro'],1)
            self.assertFalse(summary['distanceReady'])
            with (p/'out/imu.csv').open() as f:
                rows=list(csv.DictReader(f))
            self.assertAlmostEqual(float(rows[0]['ax']),.2)
            self.assertEqual(int(rows[0]['timestamp_ns']),1_001_000_000)
            with (p/'out/frames.csv').open() as f:
                rows=list(csv.DictReader(f))
            self.assertEqual(int(rows[0]['timestamp_ns']),1_008_000_000)
            assumptions=write_reference_config(p/'out')
            fs=cv2.FileStorage(str(p/'out/reference.yaml'),cv2.FILE_STORAGE_READ)
            np.testing.assert_allclose(fs.getNode('extrinsicRotation').mat(),[[0,1,0],[-1,0,0],[0,0,1]])
            fs.release()
            self.assertEqual(assumptions['translationSource'],'zero initial guess; online refinement enabled')

    def test_rejects_wrong_units(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)
            with self.assertRaisesRegex(ValueError,'SI units'):
                export_capture(self.fixture(p,bad_units=True),p/'out')

    def test_rejects_wrong_camera_profile(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)
            with self.assertRaisesRegex(ValueError,'Profile mismatch: opticalSetup'):
                export_capture(self.fixture(p,bad_optics=True),p/'optics')
            with self.assertRaisesRegex(ValueError,'Profile mismatch'):
                export_capture(self.fixture(p,bad_profile=True),p/'out')

    def test_rejects_nonmonotonic_imu(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)
            with self.assertRaisesRegex(ValueError,'increasing'):
                export_capture(self.fixture(p,duplicate=True),p/'out')

    def test_reset_never_becomes_a_stitched_route_distance(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp);source=self.fixture(p);out=p/'out'
            export_capture(source,out)
            fields=['imu_time_s','initialized','px','py','pz','vx','vy','vz','ba_norm','bg_norm','td']
            with (out/'reference-states.csv').open('w',newline='') as f:
                w=csv.DictWriter(f,fields);w.writeheader()
                for t,ready,x in [(1.008,1,0),(1.012,1,1),(1.018,0,100)]:
                    row=dict.fromkeys(fields,0)
                    row.update(imu_time_s=t,initialized=ready,px=x)
                    w.writerow(row)
            (out/'reference-stderr.txt').write_text('system reboot!\n')
            result=summarize_reference(out,source)
            self.assertEqual(result['initializedFramesAfterAppTrigger'],1)
            self.assertEqual(result['reboots'],1)
            self.assertIsNone(result['provisionalImuPositionPathAfterAppTriggerMetres'])
            self.assertFalse(result['distanceReady'])


if __name__ == '__main__':
    unittest.main()
