import csv,io,json,tempfile,unittest,zipfile
from pathlib import Path
import numpy as np
from distance_validation import parameters,prepare_reference,inspect_capture,assess_states,horizontal_distance,noise_settings
import test_vio_reference as capture_fixture

def reference(binding):
    def row(value,topic='/gaittrace/camera'):return [{'key':topic,'value':value}]
    return {'kind':'phone-reference-camera-imu-calibration-v1','method':'ikalibr-tro-2025','status':'reference-solved-review-required','sourceSha256':'a'*64,'cameraImuCandidateReady':False,'distanceReady':False,'fullCalibrationReady':False,'independentDistanceValidation':False,'binding':binding,
      'lensProfile':{'lensReady':True,'binding':binding,'lens':{'cameraMatrix':[[500,0,320],[0,500,240],[0,0,1]],'distortion':[.1,-.2,0,0,.3],'heldOutP90Pixels':.2}},
      'upstreamParameters':{'CalibParam':{'EXTRI':{'SO3_CmToBr':row({'qx':0,'qy':0,'qz':np.sqrt(.5),'qw':np.sqrt(.5)}),'POS_CmInBr':row({'r0c0':.02,'r1c0':-.01,'r2c0':.003}),'SO3_BiToBr':row({'qx':0,'qy':0,'qz':0,'qw':1},'/gaittrace/imu'),'POS_BiInBr':row({'r0c0':0,'r1c0':0,'r2c0':0},'/gaittrace/imu')},'TEMPORAL':{'TO_CmToBr':row(-.002),'RS_READOUT':row(.03),'TO_BiToBr':row(0,'/gaittrace/imu')}}}}

def capture(folder):
    old=capture_fixture.ReferenceContractTests().fixture(Path(folder));out=Path(folder)/'reference-trial.zip'
    with zipfile.ZipFile(old) as src,zipfile.ZipFile(out,'w') as z:
        meta=json.loads(src.read('manifest.json'));meta.update(kind='front-camera-distance-research-v1',status='quiet-stop',error=None,stabilizationRequested='off',capturePipeline='native-camera-imu-v2',opticalSetup='waist-bag-window');meta['diagnostics']['placementCompleted']=True
        r=reference(meta)
        for name in src.namelist():
            if name not in ['manifest.json','research-profile.json']:z.writestr(name,src.read(name))
        z.writestr('manifest.json',json.dumps(meta));z.writestr('reference-calibration.json',json.dumps(r))
    return out,r

class DistanceValidationTests(unittest.TestCase):
    def test_reference_geometry_direction_and_measured_translation_not_zero_guess(self):
        with tempfile.TemporaryDirectory() as folder:
            p,r=capture(folder);out=Path(folder)/'out';prepare_reference(p,out)
            import cv2
            f=cv2.FileStorage(str(out/'reference.yaml'),cv2.FILE_STORAGE_READ)
            np.testing.assert_allclose(f.getNode('extrinsicRotation').mat(),[[0,-1,0],[1,0,0],[0,0,1]],atol=1e-10)
            np.testing.assert_allclose(f.getNode('extrinsicTranslation').mat().ravel(),[.02,-.01,.003]);self.assertEqual(f.getNode('td').real(),-.002);self.assertEqual(f.getNode('readout').real(),.03);f.release()
            assumptions=json.loads((out/'reference-assumptions.json').read_text());self.assertFalse(assumptions['groundTruthUsedToSetScale']);self.assertIn('provisional',assumptions['noiseSource'])
    def test_wrong_camera_optics_or_reference_frame_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            _,r=capture(folder);r['upstreamParameters']['CalibParam']['TEMPORAL']['TO_BiToBr'][0]['value']=.01
            with self.assertRaisesRegex(ValueError,'Nonidentity'):parameters(r)
            r['upstreamParameters']['CalibParam']['TEMPORAL']['TO_BiToBr'][0]['value']=0;r['upstreamParameters']['CalibParam']['EXTRI']['SO3_CmToBr'][0]['value']['qw']=5
            with self.assertRaisesRegex(ValueError,'rotation'):parameters(r)
    def test_only_continuous_complete_route_can_be_compared(self):
        def row(t,x,ready='1'):return dict(imu_time_s=str(t),initialized=ready,px=str(x),py='0',pz='5',vx='.5',vy='0',vz='0',ba_norm='.05',bg_norm='.001',reboot='0')
        rows=[row(.9,0),row(1,.05),row(1.1,.1),row(1.2,.15)]
        good=assess_states(rows,'',1,1.2);self.assertTrue(good['fullRouteCovered']);self.assertAlmostEqual(good['completeRouteEstimateMetres'],.1)
        late=assess_states(rows[2:],'',1,1.2);self.assertFalse(late['fullRouteCovered']);self.assertEqual(late['reason'],'partial-route');self.assertIsNone(late['completeRouteEstimateMetres'])
        rows[2]['reboot']='1';reset=assess_states(rows,'system reboot!',1,1.2);self.assertIsNone(reset['experimentalSegmentMetres']);rows[2]['reboot']='0'
        gap=assess_states([row(1,0),row(1.5,1)],'',1,1.5);self.assertEqual(gap['reason'],'tracking-integrity-failed')
    def test_straight_distance_does_not_integrate_lateral_sway_or_finishing_pause(self):
        t=np.arange(0,6,.05);p=np.column_stack([.5*t,.08*np.sin(2*np.pi*2*t)])
        self.assertAlmostEqual(horizontal_distance(p,t,'straight'),np.linalg.norm(p[-1]-p[0]))
        def row(t,x):return dict(imu_time_s=str(t),initialized='1',px=str(x),py='0',pz='0',vx='.5',vy='0',vz='0',ba_norm='.05',bg_norm='.001',reboot='0')
        rows=[row(t,.5*min(t,6)) for t in np.arange(.9,10,.05)]
        result=assess_states(rows,'system reboot! during practice only',1,6,'straight',9)
        self.assertTrue(result['fullRouteCovered']);self.assertLess(result['completeRouteEstimateMetres'],3)
        for r in rows:
            if float(r['imu_time_s'])>6:r['px']=str(3+.1*(float(r['imu_time_s'])-6))
        drift=assess_states(rows,'',1,6,'straight',9);self.assertEqual(drift['reason'],'standing-drift');self.assertIsNone(drift['completeRouteEstimateMetres'])
    def test_pose_jump_is_rejected_even_with_normal_velocity_and_no_reboot(self):
        def row(t,x):return dict(imu_time_s=str(t),initialized='1',px=str(x),py='0',pz='0',vx='.5',vy='0',vz='0',ba_norm='.05',bg_norm='.001',reboot='0')
        rows=[row(.95,0),row(1,.025),row(1.05,.05),row(1.1,.075)]
        self.assertTrue(assess_states(rows,'',1,1.1)['fullRouteCovered'])
        rows[2]['px']='1'
        result=assess_states(rows,'',1,1.1)
        self.assertEqual(result['trackingIssue'],'pose-discontinuity')
        self.assertEqual(result['reason'],'tracking-integrity-failed')
        self.assertIsNone(result['completeRouteEstimateMetres'])
    def test_finishing_tail_jump_below_drift_limit_is_not_silently_accepted(self):
        def row(t,x):return dict(imu_time_s=str(t),initialized='1',px=str(x),py='0',pz='0',vx='0',vy='0',vz='0',ba_norm='.05',bg_norm='.001',reboot='0')
        rows=[row(.95,0),row(1,0),row(1.05,.025),row(1.10,.05),row(1.11,.15),row(1.15,.05)]
        result=assess_states(rows,'',1,1.10,standing_end=1.15)
        self.assertEqual(result['trackingIssue'],'pose-discontinuity')
        self.assertFalse(result['fullRouteCovered'])
    def test_jump_in_near_trigger_bracket_is_checked(self):
        def row(t,x):return dict(imu_time_s=str(t),initialized='1',px=str(x),py='0',pz='0',vx='.5',vy='0',vz='0',ba_norm='.05',bg_norm='.001',reboot='0')
        rows=[row(.99,0),row(1,1),row(1.05,1.025),row(1.1,1.05)]
        self.assertEqual(assess_states(rows,'',1,1.1)['trackingIssue'],'pose-discontinuity')
    def test_turns_require_route_selection_and_do_not_collapse_to_endpoint(self):
        t=np.arange(0,8,.05);x=np.where(t<=4,.5*t,4-.5*t);p=np.column_stack([x,np.zeros_like(x)])
        self.assertIsNone(horizontal_distance(p,t,'straight'))
        self.assertGreater(horizontal_distance(p,t,'with-turns'),3.7)
        with self.assertRaises(ValueError):horizontal_distance(p,t,'unknown')
    def test_known_lengths_are_recovered_without_reference_length_being_input(self):
        for length in [2,3,5]:
            t=np.linspace(0,2*length,int(length*40)+1);p=np.column_stack([t/2,np.zeros_like(t)])
            self.assertAlmostEqual(horizontal_distance(p,t,'straight'),length)
            self.assertAlmostEqual(horizontal_distance(p,t,'with-turns'),length)
    def test_phone_noise_uses_sample_sigma_not_density_and_never_invents_random_walk(self):
        meta={'installationId':'p','device':{'model':'test'},'capturePipeline':'native-camera-imu-v2'}
        report={'binding':meta,'whiteNoiseCandidateReady':True,'biasRandomWalkReady':False,'distanceReady':False,'sensors':{s:{'stdAxes':v,'sampleRateHz':200,'whiteNoiseDensityCandidate':[1e-8]*3} for s,v in [('accelerometer',[.01,.02,.03]),('gyroscope',[.001,.002,.003])]}}
        values,source=noise_settings(meta,report);self.assertEqual(values['acc_n'],.03);self.assertEqual(values['gyr_n'],.003);self.assertEqual(values['acc_w'],.00004);self.assertIn('provisional',source)
        report['binding']={**meta,'installationId':'other'};self.assertEqual(noise_settings(meta,report)[0]['acc_n'],.08)
    def test_service_dispatches_distance_separately_and_idempotently(self):
        from calibration_companion import Companion
        import time
        with tempfile.TemporaryDirectory() as folder:
            source,_=capture(folder);calls=[]
            c=Companion(Path(folder)/'jobs',runner=lambda _:self.fail('Calibration runner used for walk'),distance_runner=lambda p:calls.append(p) or {'distanceReady':False})
            key=c.submit(source.read_bytes(),3)
            for _ in range(100):
                if not c.processing:break
                time.sleep(.01)
            self.assertEqual(c.jobs[key]['status'],'completed');self.assertEqual(len(calls),1);self.assertEqual(c.submit(source.read_bytes(),3),key);self.assertEqual(len(calls),1)
            self.assertEqual(json.loads((calls[0]/'request.json').read_text())['referenceDistanceMetres'],3)
            with self.assertRaises(ValueError):c.submit(source.read_bytes(),10)
    def test_failed_processing_can_retry_saved_capture_without_new_walk(self):
        from calibration_companion import Companion
        import time
        with tempfile.TemporaryDirectory() as folder:
            source,_=capture(folder);calls=[]
            def runner(path):
                calls.append(path)
                if len(calls)==1:raise RuntimeError('temporary engine failure')
                return {'distanceReady':False}
            c=Companion(Path(folder)/'jobs',distance_runner=runner)
            def wait():
                for _ in range(100):
                    if not c.processing:return
                    time.sleep(.01)
                self.fail('Worker did not finish')
            key=c.submit(source.read_bytes(),3);wait();self.assertEqual(c.jobs[key]['status'],'failed')
            self.assertEqual(c.submit(source.read_bytes(),3),key);wait();self.assertEqual(c.jobs[key]['status'],'completed');self.assertEqual(len(calls),2)
            self.assertEqual((calls[0]/'input.zip').read_bytes(),source.read_bytes());self.assertTrue(list(calls[0].glob('job-before-retry-*.json')))
    def test_upload_storage_failure_releases_worker_and_preserves_saved_input(self):
        from calibration_companion import Companion
        import hashlib
        with tempfile.TemporaryDirectory() as folder:
            source,_=capture(folder);body=source.read_bytes();c=Companion(Path(folder)/'jobs',distance_runner=lambda p:{})
            from distance_pipeline import processing_spec
            key=hashlib.sha256(body+b'3:processing:'+processing_spec()['revision'].encode()+b':noise:provisional-defaults').hexdigest()[:24];target=c.folder/key;target.mkdir();(target/'input.zip').write_bytes(b'preserve this unrelated input')
            with self.assertRaisesRegex(ValueError,'does not match'):c.submit(body,3)
            self.assertFalse(c.processing);self.assertNotIn(key,c.jobs);self.assertEqual((target/'input.zip').read_bytes(),b'preserve this unrelated input')
    def test_no_feature_exit_is_data_rejection_but_other_engine_failures_are_not_success(self):
        import subprocess,types
        from unittest.mock import patch
        from distance_validation import run_distance,VINS_COMMIT
        with tempfile.TemporaryDirectory() as folder:
            folder=Path(folder);source,_=capture(folder);(folder/'input.zip').write_bytes(source.read_bytes());(folder/'request.json').write_text(json.dumps({'referenceDistanceMetres':3}))
            replay=folder/'replay';replay.mkdir();(replay/'reference-states.csv').write_text('initialized,imu_time_s\n');(replay/'reference-stdout.txt').write_text('frames=0 initialized_frames=0 distanceReady=false');(replay/'reference-stderr.txt').write_text('');(replay/'features-summary.json').write_text(json.dumps({'medianFeatures':0,'frontend':'test-only'}));(replay/'compute-summary.json').write_text('{}')
            for exit_code in [6,1]:
                # This tiny legacy adapter fixture has no two-second baseline.
                # The corrected-mode negative control runs through the actual service.
                with patch.dict('os.environ',{'GAITTRACE_DISTANCE_PIPELINE':'fixed-time-v2'}),patch('distance_validation.os',types.SimpleNamespace(name='nt')),patch('distance_validation.subprocess.check_output',side_effect=[VINS_COMMIT,'a'*64]),patch('distance_validation.subprocess.run'),patch('vio_compute.run_replay',side_effect=subprocess.CalledProcessError(exit_code,['test-estimator'])):
                    if exit_code==6:
                        result=run_distance(folder);self.assertIsNone(result['completeRouteEstimateMetres']);self.assertFalse(result['distanceReady']);self.assertEqual(result['compute']['dataRejection'],'no-usable-feature-frames')
                    else:
                        with self.assertRaises(subprocess.CalledProcessError):run_distance(folder)

if __name__=='__main__':unittest.main()
