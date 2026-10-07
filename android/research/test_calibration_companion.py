import io,json,tempfile,time,unittest,zipfile,threading,urllib.request,urllib.error
import subprocess
from pathlib import Path
from unittest.mock import patch
from http.server import ThreadingHTTPServer
from calibration_companion import Companion,handler
from calibration_companion import run_reference,IMAGE,GPU_IMAGE

def capture(status='completed'):
    data=io.BytesIO()
    with zipfile.ZipFile(data,'w') as z:z.writestr('manifest.json',json.dumps({'kind':'phone-camera-imu-alignment-capture-v1','status':status,'error':None}))
    return data.getvalue()
class CompanionChecks(unittest.TestCase):
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
                if IMAGE in command and not any('GAITTRACE_REFERENCE_STAGE=' in v for v in command):
                    (folder/'result.json').write_text(json.dumps({'method':'ikalibr-tro-2025','distanceReady':False}))
                return subprocess.CompletedProcess(command,0)
            with patch('calibration_companion.subprocess.run',side_effect=process):result=run_reference(folder)
            self.assertFalse(result['distanceReady']);self.assertEqual((folder/'input.zip').read_bytes(),original)
            self.assertEqual(json.loads((folder/'gpu-fallback.json').read_text())['backend'],'cpu')
            self.assertEqual(sum('--gpus' in c for c in commands),1)
            self.assertEqual(sum(IMAGE in c and not any('GAITTRACE_REFERENCE_STAGE=' in v for v in c) for c in commands),1)
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
            c=Companion(folder,run);key=c.submit(capture())
            for _ in range(100):
                if c.jobs[key]['status']!='processing':break
                time.sleep(.01)
            self.assertEqual(c.jobs[key]['status'],'completed');self.assertEqual(c.submit(capture()),key);self.assertEqual(len(calls),1)
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
