import unittest
import tempfile
import zipfile
import json
from pathlib import Path
import numpy as np
from imu_noise import characterize,process_noise


class NoiseChecks(unittest.TestCase):
    def fixture(self,sensor='gyroscope'):
        rng=np.random.default_rng(401)
        t=np.arange(40000,dtype=np.int64)*5_000_000
        density=.0001 if sensor=='gyroscope' else .003
        values=rng.normal(0,density/np.sqrt(.005),(len(t),3))
        if sensor=='accelerometer':values[:,2]+=9.80665
        return t,values,density

    def test_known_white_noise(self):
        for sensor in ('accelerometer','gyroscope'):
            t,v,d=self.fixture(sensor);r=characterize(t,v,sensor)
            self.assertTrue(r['whiteNoiseCandidateReady'])
            np.testing.assert_allclose(r['whiteNoiseDensityCandidate'],d,rtol=.15)
            self.assertFalse(r['biasRandomWalkReady'])

    def test_clock_gaps_nonmonotonic_short_and_movement(self):
        t,v,_=self.fixture()
        bad=t.copy();bad[50:]+=50_000_000
        backwards=t.copy();backwards[50]=backwards[49]
        for clock,values in ((bad,v),(backwards,v),(t[:1000],v[:1000]),(t,v+1)):
            with self.assertRaises(ValueError):characterize(clock,values,'gyroscope')

    def test_coloured_motion_is_not_noise(self):
        t,v,_=self.fixture();v[:,0]+=.005*np.sin(t/1e9*2)
        self.assertFalse(characterize(t,v,'gyroscope')['whiteNoiseCandidateReady'])

    def test_completed_bound_archive_and_wrong_capture_kind(self):
        meta={'kind':'phone-imu-noise-capture-v1','status':'completed','error':None,
              'installationId':'synthetic-test-only','captureId':'imu-noise-123',
              'units':{'accelerometer':'m/s2','gyroscope':'rad/s','magnetometer':'uT'}}
        rows=[]
        for sensor in ('accelerometer','gyroscope'):
            t,values,_=self.fixture(sensor)
            for ts,v in zip(t,values):rows.append(json.dumps({'sensor':sensor,'timestampNs':int(ts),'x':v[0],'y':v[1],'z':v[2]}))
        for ts in t[::4]:rows.append(json.dumps({'sensor':'magnetometer','timestampNs':int(ts),'x':10,'y':20,'z':30}))
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'synthetic.zip'
            def write():
                with zipfile.ZipFile(path,'w') as z:
                    z.writestr('manifest.json',json.dumps(meta));z.writestr('imu.ndjson','\n'.join(rows))
            write();r=process_noise(path)
            self.assertEqual(r['status'],'white-noise-candidate');self.assertFalse(r['fullCalibrationReady']);self.assertFalse(r['distanceReady'])
            meta['kind']='front-camera-distance-research-v1';write()
            self.assertEqual(process_noise(path)['status'],'rejected')
            meta['kind']='phone-imu-noise-capture-v1';rows=rows[:80100];write()
            self.assertIn('Magnetometer coverage',process_noise(path)['errors'][0])


if __name__=='__main__':unittest.main()
