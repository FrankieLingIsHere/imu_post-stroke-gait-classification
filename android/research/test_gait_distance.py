"""Main recording contracts; controlled inputs are not clinical distance validation."""
import io,json,tempfile,time,unittest,zipfile
import os
from unittest.mock import patch
from pathlib import Path
import numpy as np
from test_distance_validation import capture
from distance_validation import inspect_capture,central_10m_estimate,assess_states
from calibration_companion import Companion

def main_capture(folder,protocol='research-walk'):
    source,_=capture(folder);out=Path(folder)/'main.zip'
    with zipfile.ZipFile(source) as old,zipfile.ZipFile(out,'w') as new:
        meta=json.loads(old.read('manifest.json'));meta.update(kind='gait-camera-imu-distance-capture-v1',status='completed',sessionId='recording-123',captureId='gait-camera-recording-123',protocol=protocol)
        for name in old.namelist():new.writestr(name,json.dumps(meta) if name=='manifest.json' else old.read(name))
    return out

class GaitDistanceTests(unittest.TestCase):
    def test_main_capture_has_no_reference_scale_or_crossed_trial_endpoint(self):
        with tempfile.TemporaryDirectory() as folder,patch.dict(os.environ,{'GAITTRACE_DISTANCE_PIPELINE':'fixed-time-rows-quiet-v1'}):
            source=main_capture(folder);meta,_=inspect_capture(source);self.assertEqual(meta['sessionId'],'recording-123')
            requests=[]
            def run(job):requests.append(json.loads((job/'request.json').read_text()));return {'mockTransportTest':True}
            c=Companion(Path(folder)/'jobs',distance_runner=run)
            key=c.submit(source.read_bytes(),gait=True,route_geometry='straight')
            for _ in range(100):
                if c.jobs[key]['status']=='completed':break
                time.sleep(.01)
            self.assertEqual(c.jobs[key]['status'],'completed');self.assertIsNone(requests[0]['referenceDistanceMetres']);self.assertFalse(requests[0]['groundTruthUsedToSetScale']);self.assertEqual(requests[0]['sessionId'],'recording-123')
            self.assertEqual(c.submit(source.read_bytes(),gait=True,route_geometry='straight'),key)
            with self.assertRaises(ValueError):c.submit(source.read_bytes(),3)
            with self.assertRaises(ValueError):c.submit(source.read_bytes(),gait=True,route_geometry='with-turns')
    def test_10mwt_uses_1_10_1_zones_and_excludes_approach_and_finishing_stillness(self):
        def row(t):return dict(imu_time_s=str(t),initialized='1',px=str(max(0,min(12.2,t))),py='0',pz='0',vx='1',vy='0',vz='0',ba_norm='.05',bg_norm='.001',reboot='0')
        rows=[row(t) for t in np.arange(-.1,17,.05)]
        integrity=assess_states(rows,'',0,16,'straight',16.9)
        self.assertTrue(integrity['fullRouteCovered'])
        z=central_10m_estimate(rows,0,16,integrity)
        self.assertEqual(z['status'],'experimental');self.assertAlmostEqual(z['timedZoneSeconds'],10);self.assertAlmostEqual(z['speedMps'],1)
        self.assertAlmostEqual(z['startOffsetSeconds'],1);self.assertAlmostEqual(z['endOffsetSeconds'],11);self.assertFalse(z['clinicalOutcomeVerified'])
        for bad in [dict(fullRouteCovered=False,completeRouteEstimateMetres=None),dict(fullRouteCovered=True,completeRouteEstimateMetres=11.9)]:
            z=central_10m_estimate(rows,0,16,bad);self.assertIsNone(z['speedMps']);self.assertEqual(z['status'],'unavailable')
    def test_malformed_main_binding_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            source=main_capture(folder)
            with zipfile.ZipFile(source) as old:parts={n:old.read(n) for n in old.namelist()}
            for change in [{'sessionId':'../escape'},{'captureId':'distance-trial-123'},{'status':'quiet-stop'},{'protocol':'invented'}]:
                m=json.loads(parts['manifest.json']);m.update(change);data=io.BytesIO()
                with zipfile.ZipFile(data,'w') as new:
                    for name,value in parts.items():new.writestr(name,json.dumps(m) if name=='manifest.json' else value)
                with self.assertRaises(ValueError):inspect_capture(io.BytesIO(data.getvalue()))

if __name__=='__main__':unittest.main()
