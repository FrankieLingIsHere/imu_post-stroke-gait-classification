import io,json,tempfile,time,unittest,zipfile,threading,urllib.request,urllib.error
import subprocess
from pathlib import Path
from unittest.mock import patch
from http.server import ThreadingHTTPServer
from calibration_companion import Companion,handler
from calibration_companion import run_reference,IMAGE,GPU_IMAGE
from calibration_companion import recover_reference_job

def capture(status='completed'):
    data=io.BytesIO()
    with zipfile.ZipFile(data,'w') as z:z.writestr('manifest.json',json.dumps({'kind':'phone-camera-imu-alignment-capture-v1','status':status,'error':None}))
    return data.getvalue()
class CompanionChecks(unittest.TestCase):
    def test_thread_budget_is_forwarded_and_invalid_values_fail_before_job_creation(self):
        import os
        from calibration_companion import reference_threads
        with patch.dict(os.environ,{},clear=True):self.assertEqual(reference_threads(),2)
        with patch.dict(os.environ,{'GAITTRACE_REFERENCE_THREADS':'2'}):self.assertEqual(reference_threads(),2)
        with tempfile.TemporaryDirectory() as temp, patch.dict(os.environ,{'GAITTRACE_REFERENCE_THREADS':'2'}), \
                patch('calibration_companion.subprocess.run',return_value=subprocess.CompletedProcess([],0,stdout='{}')) as run:
            folder=Path(temp)
            (folder/'result.json').write_text(json.dumps({'method':'ikalibr-tro-2025','distanceReady':False}))
            run_reference(folder)
            commands=[call.args[0] for call in run.call_args_list if 'run' in call.args[0]]
            self.assertTrue(commands)
            self.assertTrue(all('GAITTRACE_REFERENCE_THREADS=2' in command for command in commands))
        for value in ('0','9','all'):
            with patch.dict(os.environ,{'GAITTRACE_REFERENCE_THREADS':value}), patch('calibration_companion.subprocess.run') as run:
                with self.assertRaises(ValueError):run_reference(Path('not-created'))
                run.assert_not_called()

    def test_tablet_link_is_board_only_and_feedback_never_exposes_camera_or_jobs(self):
        with tempfile.TemporaryDirectory() as folder:
            c=Companion(folder,lambda _:{});server=ThreadingHTTPServer(('127.0.0.1',0),handler(c,'http://192.168.1.42:8765'))
            threading.Thread(target=server.serve_forever,daemon=True).start();url=f'http://127.0.0.1:{server.server_port}'
            try:
                def post(path,value):
                    return urllib.request.urlopen(urllib.request.Request(url+path,data=json.dumps(value).encode(),headers={'Authorization':'Bearer '+c.token,'Content-Type':'application/json'}))
                page=urllib.request.urlopen(url+'/').read().decode()
                self.assertIn('/board/'+c.board_token,page);self.assertNotIn('__PAIR_QR__',page)
                tablet=urllib.request.urlopen(url+'/board/'+c.board_token).read().decode()
                self.assertNotIn(c.token,tablet);self.assertNotIn('/api/jobs',tablet)
                c.board='native-generated-png'
                state=json.load(urllib.request.urlopen(url+'/board/'+c.board_token+'/state'))
                self.assertEqual(state,{'png':'native-generated-png'})
                with self.assertRaises(urllib.error.HTTPError):urllib.request.urlopen(url+'/board/'+'0'*64+'/state')
                # Board capability cannot authenticate any service API.
                with self.assertRaises(urllib.error.HTTPError):urllib.request.urlopen(urllib.request.Request(url+'/api/health',headers={'Authorization':'Bearer '+c.board_token}))
                value={'acceptedViews':12,'hint':'Turn the tablet.','status':'checking','image':'private-frame','distanceReady':True}
                self.assertEqual(post('/api/lens-progress',value).status,200)
                feedback=json.load(urllib.request.urlopen(urllib.request.Request(url+'/api/page-state',headers={'Authorization':'Bearer '+c.token})))
                self.assertEqual(feedback['progress'],{k:value[k] for k in ['acceptedViews','hint','status']})
                self.assertGreaterEqual(feedback['progressAgeSeconds'],0)
                for invalid in [True,-1,49,'12']:
                    with self.assertRaises(urllib.error.HTTPError) as failure:post('/api/lens-progress',{**value,'acceptedViews':invalid})
                    self.assertEqual(failure.exception.code,400)
                from test_lens_framing import image_frame
                image=image_frame()
                self.assertEqual(post('/api/lens-progress',{**value,'jpeg':image}).status,200)
                feedback=json.load(urllib.request.urlopen(urllib.request.Request(url+'/api/page-state',headers={'Authorization':'Bearer '+c.token})))
                self.assertEqual(len(feedback['framing']['corners']),48)
                self.assertFalse(feedback['framing']['calibrationAuthority'])
                self.assertNotIn('jpeg',feedback);self.assertNotIn(image,json.dumps(feedback))
                self.assertEqual(list(Path(folder).iterdir()),[],'No preview or feedback files persisted')
                checklist={'leftRightAngle':False,'upDownAngle':False,'horizontal':True,'vertical':True}
                post('/api/lens-progress',{**value,'acceptedViews':48,'coverageChecklist':checklist})
                self.assertEqual(c.lens_progress['coverageChecklist'],checklist)
                post('/api/lens-progress',{**value,'coverageChecklist':checklist,'activeRound':'high-low-angles'})
                self.assertEqual(c.lens_progress['activeRound'],'high-low-angles')
                with self.assertRaises(urllib.error.HTTPError):post('/api/lens-progress',{**value,'activeRound':'invented-round'})
                for invalid in [{**checklist,'leftRightAngle':1},{'leftRightAngle':True},[True]*4]:
                    with self.assertRaises(urllib.error.HTTPError):post('/api/lens-progress',{**value,'coverageChecklist':invalid})
                for phase in ['fitting','saving']:
                    self.assertEqual(post('/api/lens-progress',{**value,'status':phase}).status,200)
                    self.assertEqual(c.lens_progress['status'],phase)
                post('/api/lens-progress',{**value,'jpeg':'invalid'})
                self.assertEqual(c.framing['error'],'unavailable');self.assertEqual(c.lens_progress['acceptedViews'],12)
            finally:server.shutdown();server.server_close()
    def test_gpu_failure_keeps_capture_and_discloses_cpu_fallback(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory);original=b'unchanged-upload';(folder/'input.zip').write_bytes(original);commands=[]
            def process(command,**kwargs):
                commands.append(command)
                if 'info' in command:return subprocess.CompletedProcess(command,0,stdout='{"nvidia":{}}')
                if '--gpus' in command:raise subprocess.CalledProcessError(1,command)
                if command[-1:] == [IMAGE] and not any('GAITTRACE_REFERENCE_STAGE=' in v for v in command):
                    (folder/'result.json').write_text(json.dumps({'method':'ikalibr-tro-2025','distanceReady':False}))
                return subprocess.CompletedProcess(command,0)
            with patch('calibration_companion.subprocess.run',side_effect=process):result=run_reference(folder)
            self.assertFalse(result['distanceReady']);self.assertEqual((folder/'input.zip').read_bytes(),original)
            self.assertEqual(json.loads((folder/'gpu-fallback.json').read_text())['backend'],'cpu')
            self.assertEqual(sum('--gpus' in c for c in commands),1)
            self.assertEqual(sum(c[-1:] == [IMAGE] and not any('GAITTRACE_REFERENCE_STAGE=' in v for v in c) for c in commands),1)
            imported=next(c for c in commands if c[-2:]==['/bridge/workspace.py','import'])
            exported=next(c for c in commands if c[-2:]==['/bridge/workspace.py','export'])
            self.assertIn('dst=/data', ' '.join(imported));self.assertIn('type=volume', ' '.join(imported))
            self.assertNotIn('type=bind,src='+str(folder)+',dst=/data', ' '.join(imported))
            self.assertEqual(exported[-1],'export')
            self.assertTrue(any('volume' in c and 'rm' in c for c in commands))
    def test_timeout_stops_only_this_named_calibration_container(self):
        with tempfile.TemporaryDirectory() as directory:
            commands=[]
            def process(command,**kwargs):
                commands.append(command)
                if 'info' in command:return subprocess.CompletedProcess(command,0,stdout='{}')
                if 'run' in command:raise subprocess.TimeoutExpired(command,kwargs['timeout'])
                return subprocess.CompletedProcess(command,0)
            with patch('calibration_companion.subprocess.run',side_effect=process):
                with self.assertRaises(subprocess.TimeoutExpired):run_reference(Path(directory))
            run=next(c for c in commands if 'run' in c);stop=next(c for c in commands if 'stop' in c)
            name=run[run.index('--name')+1];self.assertTrue(name.startswith('gaittrace-calibration-'))
            self.assertEqual(stop[-1],name);self.assertNotIn('kill',stop)
    def test_completed_job_is_local_durable_and_deduplicated(self):
        with tempfile.TemporaryDirectory() as folder:
            calls=[]
            def run(path):calls.append(path);return {'method':'ikalibr-tro-2025','distanceReady':False}
            body=capture();c=Companion(folder,run);key=c.submit(body)
            for _ in range(100):
                if c.jobs[key]['status']!='processing':break
                time.sleep(.01)
            self.assertEqual(c.jobs[key]['status'],'completed');self.assertEqual(c.submit(body),key);self.assertEqual(len(calls),1)
            self.assertIn(key,Companion(folder,run).jobs)
            with self.assertRaises(ValueError):c.submit(capture('user-stopped'))
    def test_engine_failure_is_never_a_success(self):
        with tempfile.TemporaryDirectory() as folder:
            def fail(path):raise RuntimeError('missing upstream output')
            c=Companion(folder,fail);key=c.submit(capture())
            for _ in range(100):
                if c.jobs[key]['status']!='processing':break
                time.sleep(.01)
            self.assertEqual(c.jobs[key]['status'],'failed');self.assertNotIn('result',c.jobs[key])
            details=json.loads((Path(folder)/key/'failure.json').read_text())
            self.assertEqual(details['errorType'],'RuntimeError');self.assertTrue(details['captureRetained'])
    def test_retained_terminal_result_can_be_recovered_without_reuploading_capture(self):
        with tempfile.TemporaryDirectory() as folder:
            c=Companion(folder,lambda _:{});key='a'*24;record=Path(folder)/key;record.mkdir()
            c.jobs[key]={'id':key,'status':'failed'}
            server=ThreadingHTTPServer(('127.0.0.1',0),handler(c,'http://192.168.1.42:8765'))
            threading.Thread(target=server.serve_forever,daemon=True).start()
            try:
                complete={'id':key,'status':'completed','result':{'method':'ikalibr-tro-2025','distanceReady':False}}
                (record/'job.json').write_text(json.dumps(complete))
                request=urllib.request.Request(f'http://127.0.0.1:{server.server_port}/api/jobs/{key}',headers={'Authorization':'Bearer '+c.token})
                self.assertEqual(json.load(urllib.request.urlopen(request)),complete)
                c.jobs[key]={'id':key,'status':'processing'}
                self.assertEqual(json.load(urllib.request.urlopen(request))['status'],'processing','An active worker cannot be replaced by an old disk result')
            finally:server.shutdown();server.server_close()
    def test_recovery_binds_to_original_capture_and_cannot_admit_distance(self):
        import hashlib
        with tempfile.TemporaryDirectory() as temp:
            source=capture();digest=hashlib.sha256(source).hexdigest();folder=Path(temp)/digest[:24];folder.mkdir();(folder/'input.zip').write_bytes(source)
            result={'method':'ikalibr-tro-2025','kind':'phone-reference-camera-imu-calibration-v1',
                    'status':'reference-solved-review-required','sourceSha256':digest,'binding':{},'lensProfile':None,
                    'upstreamParameters':{'CalibParam':{'fixture':True}},'cameraImuCandidateReady':False,
                    'fullCalibrationReady':False,'distanceReady':False,'independentDistanceValidation':False}
            with self.assertRaisesRegex(ValueError,'review contract'):recover_reference_job(folder,{**result,'distanceReady':True})
            with self.assertRaisesRegex(ValueError,'review contract'):recover_reference_job(folder,{**result,'sourceSha256':'0'*64})
            job=recover_reference_job(folder,result)
            self.assertEqual(job['status'],'completed');self.assertFalse(job['result']['distanceReady'])
            self.assertEqual((folder/'input.zip').read_bytes(),source)
            self.assertIn(folder.name,Companion(Path(temp)).jobs)
    def test_native_workspace_preserves_raw_capture_and_exports_failure_evidence(self):
        import importlib.util
        spec=importlib.util.spec_from_file_location('reference_workspace',Path(__file__).parent/'calibration-companion/workspace.py')
        workspace=importlib.util.module_from_spec(spec);spec.loader.exec_module(workspace)
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp);host=folder/'host';linux=folder/'linux';host.mkdir()
            original=capture();(host/'input.zip').write_bytes(original);(host/'job.json').write_text('retained-host-job')
            workspace.import_capture(host,linux)
            self.assertFalse((linux/'job.json').exists())
            (linux/'reference-initial.log').write_text('upstream failure evidence')
            (linux/'output').mkdir();(linux/'output/partial.json').write_text('{}')
            workspace.export_outputs(linux,host)
            self.assertEqual((host/'input.zip').read_bytes(),original)
            self.assertEqual((host/'job.json').read_text(),'retained-host-job')
            self.assertEqual((host/'reference-initial.log').read_text(),'upstream failure evidence')
            self.assertTrue((host/'output/partial.json').exists())
            (linux/'input.zip').write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'Working capture changed'):workspace.export_outputs(linux,host)
    def test_solver_failure_still_exports_diagnostics_before_removing_workspace(self):
        with tempfile.TemporaryDirectory() as temp:
            commands=[]
            def process(command,**kwargs):
                commands.append(command)
                if 'info' in command:return subprocess.CompletedProcess(command,0,stdout='{}')
                if command[-1:] == [IMAGE]:raise subprocess.CalledProcessError(1,command)
                return subprocess.CompletedProcess(command,0)
            with patch('calibration_companion.subprocess.run',side_effect=process):
                with self.assertRaises(subprocess.CalledProcessError):run_reference(Path(temp))
            export_index=next(i for i,c in enumerate(commands) if c[-2:]==['/bridge/workspace.py','export'])
            remove_index=next(i for i,c in enumerate(commands) if 'volume' in c and 'rm' in c)
            self.assertLess(export_index,remove_index)
    def test_real_http_requires_pairing_token_and_rejects_partial_uploads(self):
        with tempfile.TemporaryDirectory() as folder:
            c=Companion(folder,lambda _:{});server=ThreadingHTTPServer(('127.0.0.1',0),handler(c,'http://192.168.1.42:8765'))
            threading.Thread(target=server.serve_forever,daemon=True).start();url=f'http://127.0.0.1:{server.server_port}'
            try:
                with self.assertRaises(urllib.error.HTTPError) as failure:urllib.request.urlopen(url+'/api/health')
                self.assertEqual(failure.exception.code,401)
                req=urllib.request.Request(url+'/api/health',headers={'Authorization':'Bearer '+c.token})
                self.assertEqual(json.load(urllib.request.urlopen(req))['method'],'ikalibr-tro-2025')
                req=urllib.request.Request(url+'/api/captures',data=capture('interrupted'),headers={'Authorization':'Bearer '+c.token})
                with self.assertRaises(urllib.error.HTTPError) as failure:urllib.request.urlopen(req)
                self.assertEqual(failure.exception.code,400)
            finally:server.shutdown();server.server_close()
if __name__=='__main__':unittest.main()
