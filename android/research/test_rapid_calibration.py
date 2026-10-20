import copy,hashlib,io,json,tempfile,time,unittest,zipfile
from pathlib import Path
from unittest.mock import patch
from rapid_calibration import inspect_capture,CHECKPOINT_SHA256,CHECKOUT_REVISION,run_enrollment
from rapid_calibration_worker import seed_from_predictions,validate_seed,refined_lens
from few_shot_calibration import load_examples,task_partition
from calibration_companion import Companion

def manifest():
    return {'schemaVersion':1,'kind':'phone-rapid-camera-imu-capture-v1','captureMode':'learned-scene-enrollment','status':'completed','error':None,
            'installationId':'one','captureId':'calibration-123','cameraId':'1','width':640,'height':480,
            'imageAxes':'native-sensor-unrotated-unmirrored','sensorOrientationDegrees':270,'stabilizationRequested':'off',
            'capturePipeline':'native-camera-imu-v2','opticalSetup':'waist-bag-window','timestampSource':'realtime',
            'alignmentMovementStartedBootNs':10_000_000_000,'units':{'accelerometer':'m/s2','gyroscope':'rad/s','magnetometer':'uT'},
            'device':{'manufacturer':'test','model':'one'}}

def capture(meta=None):
    data=io.BytesIO()
    with zipfile.ZipFile(data,'w') as z:
        z.writestr('manifest.json',json.dumps(meta or manifest()))
        for n in ['imu.ndjson','frames.ndjson','capture-results.ndjson']:z.writestr(n,'')
    return data.getvalue()

def seed():
    return seed_from_predictions(manifest(),{'focalPixels':[[500,500]],'radialK1':.05},{'focalPixels':[[501,501]]},
                                 {'sourceCommit':CHECKOUT_REVISION,'checkpointSha256':CHECKPOINT_SHA256,'viewPredictions':[]})

class RapidChecks(unittest.TestCase):
    def test_refinement_uses_upstream_principal_point_and_brown_coefficient_order(self):
        camera={'focal_length':[501,499],'principal_point':[321,242],'disto_param':[.1,.2,.3,.004,.005],'img_width':640,'img_height':480}
        result={'upstreamParameters':{'CalibParam':{'INTRI':{'Camera':[{'key':'/gaittrace/camera','value':{'ptr_wrapper':{'data':camera}}}]}}}}
        refined=refined_lens(result);self.assertEqual(refined['cameraMatrix'][0][2],321);self.assertEqual(refined['distortion'],[.1,.2,.004,.005,.3]);self.assertFalse(refined['independentLensValidation'])
        camera['principal_point'][0]=600
        with self.assertRaises(ValueError):refined_lens(result)
    def test_capture_contract_rejects_wrong_device_stream_or_unfinished_cue(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'input.zip';p.write_bytes(capture());self.assertEqual(inspect_capture(p)['width'],640)
            for key,value in [('kind','phone-camera-imu-alignment-capture-v1'),('status','user-stopped'),('timestampSource','unknown'),('width',1280),('alignmentMovementStartedBootNs',0),('opticalSetup','unconfirmed')]:
                m=manifest();m[key]=value;p.write_bytes(capture(m))
                with self.assertRaises(ValueError):inspect_capture(p)
            m=manifest();m['units']['gyroscope']='degrees/s';p.write_bytes(capture(m))
            with self.assertRaises(ValueError):inspect_capture(p)

    def test_seed_never_claims_full_lens_or_distance_validation(self):
        r=seed();validate_seed(r,manifest());self.assertFalse(r['lensReady']);self.assertTrue(r['calibrationSeedReady']);self.assertNotIn('heldOutP90Pixels',r['lens'])
        for mutate in [lambda s:s.update(distanceReady=True),lambda s:s['learned'].update(checkpointSha256='0'*64),lambda s:s['learned'].update(viewConsistencyFraction=.081),lambda s:s['binding'].update(cameraId='2'),lambda s:s['lens']['distortion'].__setitem__(1,.01)]:
            s=copy.deepcopy(r);mutate(s)
            with self.assertRaises(ValueError):validate_seed(s,manifest())
        for other in [600,float('nan')]:
            with self.assertRaises(ValueError):seed_from_predictions(manifest(),{'focalPixels':[[500,500]],'radialK1':0},{'focalPixels':[[other,other]]},{})

    def test_service_keeps_failed_capture_and_allows_retry_with_reason(self):
        with tempfile.TemporaryDirectory() as temp:
            called=[]
            def run(folder):
                called.append(folder)
                if len(called)==1:raise ValueError('clear-scene-views-needed')
                return {'kind':'reference-test-fixture','distanceReady':False}
            c=Companion(temp,rapid_runner=run);data=capture();key=c.submit(data,rapid=True)
            for _ in range(200):
                if c.jobs[key]['status']!='processing':break
                time.sleep(.01)
            self.assertEqual(c.jobs[key]['status'],'failed');self.assertEqual(c.jobs[key]['retryReason'],'clear-scene-views-needed')
            self.assertEqual((Path(temp)/key/'input.zip').read_bytes(),data)
            self.assertEqual(c.submit(data,rapid=True),key)
            for _ in range(200):
                if c.jobs[key]['status']!='processing':break
                time.sleep(.01)
            self.assertEqual(c.jobs[key]['status'],'completed');self.assertEqual(len(called),2)

    def test_full_enrollment_requires_reference_to_use_checked_seed(self):
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp);folder.joinpath('input.zip').write_bytes(capture());folder.joinpath('lens-seed.json').write_text(json.dumps(seed()))
            with patch('rapid_calibration.subprocess.run'),patch('distance_validation.parameters'),patch('rapid_calibration_worker.refined_lens',return_value={}):
                with self.assertRaisesRegex(ValueError,'did-not-use'):run_enrollment(folder,lambda _: {'lensProfile':{}})
                r=run_enrollment(folder,lambda _:{'lensProfile':seed(),'binding':manifest(),'sourceSha256':'1'*64,'upstreamParameters':{}})
            self.assertFalse(r['enrollment']['neuralWeightsUpdated']);self.assertEqual(r['trainingExample']['labelSource'],'ikalibr-candidate-not-independent-truth');self.assertTrue(folder.joinpath('training-example.json').is_file())

    def test_training_guard_does_not_turn_one_phone_into_many_tasks(self):
        rows=[{'deviceGroup':'Xiaomi/one','captureId':str(i)} for i in range(20)]
        with self.assertRaisesRegex(ValueError,'five phone'):task_partition(rows,'a','b')
        rows=[{'deviceGroup':str(g),'captureId':str(i)} for g in range(5) for i in range(2)]
        p=task_partition(rows,'3','4');self.assertEqual(len(p['train']),6)
        self.assertFalse({r['deviceGroup'] for r in p['train']}&{r['deviceGroup'] for r in p['test']})
        with self.assertRaises(ValueError):task_partition(rows,'3','3')
        with self.assertRaises(ValueError):task_partition(rows[:-1],'3','4')
        mismatched=[{**r,'taskGroup':r['deviceGroup']+'/'+r['captureId']} for r in rows]
        with self.assertRaises(ValueError):task_partition(mismatched,'3','4')

    def test_scene_feedback_uses_texture_not_charuco_coverage(self):
        import base64,cv2,numpy as np
        from lens_framing import scene_outline
        ok,jpeg=cv2.imencode('.jpg',np.zeros((480,640),np.uint8));self.assertTrue(ok)
        result=scene_outline(base64.b64encode(jpeg).decode())
        self.assertEqual(result['kind'],'display-only-scene-framing');self.assertFalse(result['clearSceneHint']);self.assertFalse(result['calibrationAuthority']);self.assertNotIn('jpeg',result)
        html=Path(__file__).with_name('calibration-companion').joinpath('setup.html').read_text(encoding='utf-8')
        self.assertIn('v.sceneEnrollment',html);self.assertIn('Board-free scene enrollment',html)

    def test_bundle_hash_replay_and_view_duplication_cannot_enter_training(self):
        m=manifest();r=seed();example={'kind':'few-shot-camera-calibration-example-v1','schemaVersion':1,'binding':m,'device':m['device'],'sourceSha256':hashlib.sha256(capture()).hexdigest(),'labelSource':'ikalibr-candidate-not-independent-truth','independentValidation':False,
            'referenceParameters':{'CalibParam':{'INTRI':{'Camera':[{'key':'/gaittrace/camera','value':{'ptr_wrapper':{'data':{'focal_length':[500,500]}}}}]}}},
            'features':[{'frame':f'frames/{i}.jpg','focalPixels':[[500,500]],'radialK1':0,'focalUncertaintyPixels':[1]} for i in range(10)]}
        with tempfile.TemporaryDirectory() as temp:
            Path(temp,'input.zip').write_bytes(capture())
            p=Path(temp)/'example.json';p.write_text(json.dumps(example));self.assertEqual(len(load_examples([p,p])),1)
            example['artifactReplay']={'kind':'metadata-replay'};p.write_text(json.dumps(example))
            with self.assertRaisesRegex(ValueError,'replay'):load_examples([p])
            example.pop('artifactReplay');example['features'][1]['frame']=example['features'][0]['frame'];p.write_text(json.dumps(example))
            with self.assertRaisesRegex(ValueError,'duplicated'):load_examples([p])
            p=Path(temp)/'bundle.zip'
            with zipfile.ZipFile(p,'w') as z:z.writestr('training-example.json',json.dumps(example));z.writestr('input.zip',b'changed bytes')
            with self.assertRaisesRegex(ValueError,'source-mismatch'):load_examples([p])

if __name__=='__main__':unittest.main()
