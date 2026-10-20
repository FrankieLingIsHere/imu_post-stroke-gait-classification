"""One-time local phone calibration service. Never needed during walking tests.
Transport and upstream-engine orchestration, not a replacement calibration fit.
Research experiments and saved analyses remain in the themed notebook.
"""
import argparse,base64,hashlib,hmac,io,json,os,re,secrets,socket,subprocess,threading,time,webbrowser,zipfile
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path

BASE=Path(__file__).resolve().parent
IMAGE='gaittrace-ikalibr:reference-v1'
GPU_IMAGE='gaittrace-colmap:cuda-v1'
GPU_BASE='colmap/colmap@sha256:c1de51615dff33066cd305071226b6343c1168324ef3bd622f0825e55feb5efe'
def docker_prefix():return ['wsl.exe','-d','Ubuntu','-u','root','--','docker'] if os.name=='nt' else ['docker']
def linux_path(path):
    path=Path(path).resolve()
    return '/mnt/'+path.drive[0].lower()+'/'+path.as_posix()[3:] if os.name=='nt' else str(path)

def reference_threads():
    threads=int(os.environ.get('GAITTRACE_REFERENCE_THREADS','2'))
    if not 1<=threads<=8:raise ValueError('GAITTRACE_REFERENCE_THREADS must be between 1 and 8.')
    return threads

def run_reference(folder):
    # Windows /mnt/c bind-mount writes can dominate upstream per-line pair-list
    # flushing. Use a fresh Linux volume and copy only at stage boundaries.
    threads=reference_threads()
    volume='gaittrace-reference-'+secrets.token_hex(12)
    subprocess.run(docker_prefix()+['volume','create',volume],capture_output=True,check=True,timeout=30)
    shared=['run','--rm','--network','none','--shm-size','512m','-e',f'GAITTRACE_REFERENCE_THREADS={threads}','--mount',f'type=volume,src={volume},dst=/data','--mount',f'type=bind,src={linux_path(folder)},dst=/transfer','--mount',f'type=bind,src={linux_path(BASE/"calibration-companion")},dst=/bridge,readonly']
    info=subprocess.run(docker_prefix()+['info','--format','{{json .Runtimes}}'],capture_output=True,text=True)
    image=subprocess.run(docker_prefix()+['image','inspect',GPU_IMAGE],capture_output=True)
    gpu=info.returncode==0 and 'nvidia' in info.stdout and image.returncode==0
    with (folder/'processor.log').open('w',encoding='utf-8') as log:
        deadline=time.monotonic()+3600
        def execute(args):
            remaining=deadline-time.monotonic()
            if remaining<=0:raise TimeoutError('Reference processing exceeded one hour.')
            name='gaittrace-calibration-'+secrets.token_hex(8)
            try:subprocess.run(docker_prefix()+shared+['--name',name]+args,stdout=log,stderr=subprocess.STDOUT,timeout=remaining,check=True)
            except subprocess.TimeoutExpired:
                # Killing only the Docker CLI can leave its worker running.
                # Stop this uniquely named job, never unrelated containers.
                subprocess.run(docker_prefix()+['stop','--time','10',name],capture_output=True,timeout=30)
                raise
        imported=False
        try:
            execute(['--entrypoint','python3',IMAGE,'/bridge/workspace.py','import']);imported=True
            if gpu:
                execute(['-e','GAITTRACE_REFERENCE_STAGE=prepare',IMAGE])
                try:
                    execute(['--gpus','all','-e',f'GAITTRACE_SFM_IMAGE={GPU_BASE}','--entrypoint','python3',GPU_IMAGE,'/bridge/sfm.py','--gpu'])
                except (subprocess.CalledProcessError,subprocess.TimeoutExpired) as error:
                    # Preserve GPU logs/database and disclose the fallback. No
                    # successful GPU claim is made merely from runtime detection.
                    (folder/'gpu-fallback.json').write_text(json.dumps({'reason':str(error),'backend':'cpu'}))
                    execute([IMAGE])
                else:execute(['-e','GAITTRACE_REFERENCE_STAGE=finish',IMAGE])
            else:execute([IMAGE])
        finally:
            # A failed engine still has useful evidence. Use a separate export
            # timeout so exceeding the processing budget cannot discard it.
            try:
                if imported:
                    subprocess.run(docker_prefix()+shared+['--entrypoint','python3',IMAGE,'/bridge/workspace.py','export'],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
            except Exception:
                (folder/'retained-workspace.json').write_text(json.dumps({'volume':volume,'reason':'output-transfer-failed'}))
                raise
            else:
                subprocess.run(docker_prefix()+['volume','rm',volume],capture_output=True,check=True,timeout=30)
    result=json.loads((folder/'result.json').read_text())
    if result.get('method')!='ikalibr-tro-2025' or result.get('distanceReady') is not False:raise ValueError('Invalid reference-engine result.')
    return result
def private_host():
    with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as sock:
        try:sock.connect(('8.8.8.8',80));return sock.getsockname()[0]
        except OSError:return '127.0.0.1'

def recover_reference_job(folder,result):
    """Attach a reviewed processing attempt to its retained immutable upload.

    This restores result delivery only. It cannot mark metric tracking ready.
    """
    folder=Path(folder);source=(folder/'input.zip').read_bytes();digest=hashlib.sha256(source).hexdigest()
    if folder.name!=digest[:24]:raise ValueError('Reference job does not match the retained upload.')
    with zipfile.ZipFile(io.BytesIO(source)) as archive:meta=json.loads(archive.read('manifest.json'))
    keys=['installationId','captureId','cameraId','width','height','imageAxes','sensorOrientationDegrees','stabilizationRequested','capturePipeline','opticalSetup']
    if (result.get('method')!='ikalibr-tro-2025' or result.get('kind')!='phone-reference-camera-imu-calibration-v1'
        or result.get('status')!='reference-solved-review-required' or result.get('sourceSha256')!=digest
        or any(result.get(k) is not False for k in ['cameraImuCandidateReady','fullCalibrationReady','distanceReady','independentDistanceValidation'])
        or any(result.get('binding',{}).get(k)!=meta.get(k) for k in keys)
        or result.get('lensProfile')!=meta.get('lensProfile')
        or not result.get('upstreamParameters',{}).get('CalibParam')):
        raise ValueError('Reference result does not match the saved capture or review contract.')
    job={'id':folder.name,'status':'completed','result':result}
    previous=folder/'job.json';history=folder/'job-before-recovery.json'
    if previous.is_file() and not history.exists():history.write_bytes(previous.read_bytes())
    for name,value in [('result.json',result),('job.json',job)]:
        temporary=folder/(name+'.tmp');temporary.write_text(json.dumps(value,indent=2));temporary.replace(folder/name)
    return job

class Companion:
    def __init__(self,folder,runner=run_reference,distance_runner=None,rapid_runner=None):
        self.folder=Path(folder);self.folder.mkdir(parents=True,exist_ok=True);self.runner=runner
        if distance_runner is None:
            from distance_validation import run_distance
            distance_runner=run_distance
        self.distance_runner=distance_runner
        self.rapid_runner=rapid_runner
        self.scene_enrollment=False
        from rapid_calibration import runtime_ready
        self.rapid_available=runtime_ready()
        self.token=secrets.token_hex(32);self.board_token=secrets.token_hex(32);self.jobs={};self.lock=threading.Lock();self.processing=False;self.board=None;self.board_mode='computer';self.lens_progress=None;self.progress_updated=0;self.framing=None
        for record in self.folder.glob('*/job.json'):
            try:
                job=json.loads(record.read_text());key=record.parent.name
                if re.fullmatch('[0-9a-f]{24}',key) and job.get('status') in ['completed','failed']:self.jobs[key]=job
            except (ValueError,OSError):pass
    def authenticated(self,header):return hmac.compare_digest(header or '',f'Bearer {self.token}')
    def submit(self,body,reference_metres=None,route_geometry='straight',noise=False,gait=False,rapid=False):
        distance=reference_metres is not None or gait
        if not body or len(body)>250*1024**2:raise ValueError('Capture size is invalid.')
        with zipfile.ZipFile(io.BytesIO(body)) as z:
            if sum(v.file_size for v in z.infolist())>350*1024**2 or z.getinfo('manifest.json').file_size>1024**2:raise ValueError('Capture size is invalid.')
            if len(set(z.namelist()))!=len(z.namelist()):raise ValueError('Capture contains ambiguous files.')
            meta=json.loads(z.read('manifest.json'))
            if rapid:
                if noise or distance:raise ValueError('Enrollment is separate from walking/noise tests.')
                from rapid_calibration import inspect_capture
                inspect_capture(io.BytesIO(body))
            elif noise:
                if reference_metres is not None or meta.get('kind')!='phone-imu-noise-capture-v1' or meta.get('status')!='completed' or meta.get('error') or not meta.get('installationId'):raise ValueError('A completed stationary sensor capture is needed.')
            elif not distance:
                if meta.get('kind')!='phone-camera-imu-alignment-capture-v1' or meta.get('status')!='completed' or meta.get('error'):raise ValueError('A completed sensor-alignment capture is needed.')
            else:
                if not gait and (type(reference_metres) not in [int,float] or reference_metres not in [2,3,5]):raise ValueError('Choose a 2, 3 or 5 m reference route.')
                if gait and (reference_metres is not None or meta.get('kind')!='gait-camera-imu-distance-capture-v1'):raise ValueError('A main gait distance capture is needed.')
                if not gait and meta.get('kind')!='front-camera-distance-research-v1':raise ValueError('A separate research distance trial is needed.')
                if route_geometry not in ['straight','with-turns']:raise ValueError('Invalid route geometry.')
                from distance_validation import inspect_capture
                inspect_capture(io.BytesIO(body))
                if gait and route_geometry!=('straight' if meta['protocol'] in ['10mwt','research-walk'] else 'with-turns'):raise ValueError('Route geometry does not match this protocol.')
        suffix=(str(reference_metres)+(':'+route_geometry if route_geometry!='straight' else '')).encode() if reference_metres is not None else b''
        if rapid:
            from rapid_calibration import REVISION
            sources=['rapid_calibration_worker.py','rapid_calibration.py','calibration-companion/prepare.py','calibration-companion/workspace.py','calibration-companion/solve.py']
            suffix=b':rapid:'+REVISION.encode()+hashlib.sha256(b''.join((BASE/name).read_bytes() for name in sources)).digest()
        processing=None
        noise_profile=None;noise_digest=None
        if gait:suffix=b':gait:'+meta['sessionId'].encode()+b':'+route_geometry.encode()
        if distance:
            from distance_pipeline import processing_spec
            processing=processing_spec()
            if gait and not (processing['fixedTimeRowCorrection'] and processing['quietInitializationRequired']):raise ValueError('Restart the updated computer helper for the main gait pipeline.')
            suffix+=b':processing:'+processing['revision'].encode()
            profile=self.folder/'noise-profiles'/hashlib.sha256(meta['installationId'].encode()).hexdigest()
            if profile.is_file():noise_profile=profile.read_bytes();noise_digest=hashlib.sha256(noise_profile).hexdigest()
            suffix+=b':noise:'+(noise_digest or 'provisional-defaults').encode()
        key=hashlib.sha256(body+suffix).hexdigest()[:24]
        with self.lock:
            if key in self.jobs and (not noise and not distance and not rapid or self.jobs[key].get('status')!='failed'):return key
            if self.processing:raise ValueError('The computer is already processing a capture.')
            previous_job=self.jobs.get(key)
            self.processing=True;self.jobs[key]={'id':key,'status':'processing'}
        folder=self.folder/key
        try:
            folder.mkdir(exist_ok=True)
            if (folder/'input.zip').exists():
                if (folder/'input.zip').read_bytes()!=body:raise ValueError('Retained capture does not match this request.')
            else:(folder/'input.zip').write_bytes(body)
            if (distance or noise) and (folder/'job.json').exists():
                (folder/f'job-before-retry-{time.time_ns()}.json').write_bytes((folder/'job.json').read_bytes())
            if distance:(folder/'request.json').write_text(json.dumps({'kind':'gait-distance-request-v1' if gait else 'distance-validation-request-v1','referenceDistanceMetres':reference_metres,'routeGeometry':route_geometry,'groundTruthUsedToSetScale':False,'processingRevision':processing['revision'],'processingMode':processing['mode'],'noiseProfileSha256':noise_digest,**({'sessionId':meta['sessionId'],'protocol':meta['protocol']} if gait else {})}))
            if distance:
                if noise_profile is not None:(folder/'noise-report.json').write_bytes(noise_profile)
        except Exception:
            with self.lock:
                self.processing=False
                if previous_job:self.jobs[key]=previous_job
                else:self.jobs.pop(key,None)
            raise
        def work():
            try:
                if noise:
                    from imu_noise import process_noise
                    result=process_noise(folder/'input.zip')
                    (folder/'result.json').write_text(json.dumps(result,indent=2))
                    if result['whiteNoiseCandidateReady']:
                        profiles=self.folder/'noise-profiles';profiles.mkdir(exist_ok=True)
                        profile=profiles/hashlib.sha256(meta['installationId'].encode()).hexdigest()
                        temporary=profile.with_suffix('.tmp');temporary.write_text(json.dumps(result));temporary.replace(profile)
                elif rapid:
                    if self.rapid_runner:result=self.rapid_runner(folder)
                    else:
                        from rapid_calibration import run_enrollment
                        result=run_enrollment(folder,self.runner)
                else:result=(self.distance_runner if distance else self.runner)(folder)
                job={'id':key,'status':'completed','result':result}
            except Exception as error:
                # Details stay in the local processor log. Never return a successful
                # calibration from an empty output, timeout or upstream exit 0.
                try:
                    (folder/'failure.json').write_text(json.dumps({'kind':'phone-reference-calibration-failure-v1','errorType':type(error).__name__,'detail':str(error),'captureRetained':True},indent=2))
                except OSError:pass
                job={'id':key,'status':'failed','message':('Reference processing could not complete. The capture is kept for review.' if not distance else 'Distance processing could not complete. Your walk is saved; retry processing.')}
                if rapid and str(error) in ['clear-scene-views-needed','more-varied-motion-needed','view-estimates-disagree','continuous-scan-needed']:
                    job['retryReason']=str(error)
            try:
                temporary=folder/'job.tmp';temporary.write_text(json.dumps(job,indent=2));temporary.replace(folder/'job.json')
            except OSError:
                job={'id':key,'status':'failed','message':'Reference result could not be saved. The capture is kept for review.'}
            # Publish completion only after its durable record is closed/replaced.
            with self.lock:self.jobs[key]=job;self.processing=False
        threading.Thread(target=work,daemon=True).start();return key

def handler(companion,base_url):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass # Do not log pairing secrets or home-camera data.
        def reply(self,status,value,mime='application/json'):
            data=value.encode() if isinstance(value,str) else json.dumps(value).encode()
            self.send_response(status);self.send_header('Content-Type',mime);self.send_header('Content-Length',str(len(data)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(data)
        def do_GET(self):
            if self.path=='/':
                if self.client_address[0] not in ['127.0.0.1',base_url.split('/')[2].split(':')[0]]:
                    self.reply(404,{'error':'not-found'});return
                import qrcode
                pair=json.dumps({'kind':'gaittrace-local-calibration-pair-v1','url':base_url,'token':companion.token})
                def qr(value):
                    out=io.BytesIO();qrcode.make(value).save(out,format='PNG');return base64.b64encode(out.getvalue()).decode()
                board_url=base_url+'/board/'+companion.board_token
                page=(BASE/'calibration-companion/setup.html').read_text(encoding='utf-8').replace('__PAIR_QR__',qr(pair)).replace('__BOARD_QR__',qr(board_url)).replace('__BOARD_URL__',board_url).replace('__TOKEN__',companion.token)
                self.reply(200,page,'text/html; charset=utf-8');return
            board=re.fullmatch(r'/board/([0-9a-f]{64})(/state)?',self.path)
            if board:
                if not hmac.compare_digest(board[1],companion.board_token):self.reply(404,{'error':'not-found'});return
                if board[2]:self.reply(200,{'png':companion.board})
                else:self.reply(200,(BASE/'calibration-companion/board.html').read_text(encoding='utf-8'),'text/html; charset=utf-8')
                return
            if not companion.authenticated(self.headers.get('Authorization')):self.reply(401,{'error':'unauthorized'});return
            if self.path=='/api/health':self.reply(200,{'kind':'gaittrace-local-calibration-service-v1','method':'ikalibr-tro-2025','distanceReady':False,'distanceValidationVersion':2,'gaitDistanceVersion':1,'rapidEnrollmentVersion':1,'rapidEnrollmentAvailable':companion.rapid_available});return
            if self.path=='/api/distance-health':
                from distance_pipeline import processing_spec,validate_engine_capabilities
                try:
                    processing=processing_spec()
                    probe=subprocess.run((['wsl.exe','-d','Ubuntu','-u','root','--'] if os.name=='nt' else [])+[processing['enginePath'],'--capabilities'],capture_output=True,text=True,timeout=10)
                    capabilities=json.loads(probe.stdout) if probe.returncode==0 else {}
                    available=validate_engine_capabilities(capabilities,processing)
                    from vio_compute import probe_compute
                    # Startup executes kernels; do not cold-start CUDA again
                    # inside the phone's 15-second readiness request.
                    compute=probe_compute(cached_only=True) if available else None
                    self.reply(200,{'available':available,'distanceReady':False,'compute':compute,'capabilities':capabilities,'processing':processing})
                except (OSError,subprocess.SubprocessError,ValueError):self.reply(200,{'available':False,'distanceReady':False})
                return
            if self.path=='/api/page-state':
                self.reply(200,{'png':companion.board,'mode':companion.board_mode,'sceneEnrollment':companion.scene_enrollment,'progress':companion.lens_progress,'progressAgeSeconds':time.monotonic()-companion.progress_updated if companion.lens_progress else None,'framing':companion.framing});return
            match=re.fullmatch(r'/api/jobs/([0-9a-f]{24})',self.path)
            if match:
                # A retained failed job can be reprocessed by the research
                # notebook. Refresh only durable terminal records, never expose
                # local traceback paths or replace an active job with a stale file.
                with companion.lock:
                    current=companion.jobs.get(match[1])
                    record=companion.folder/match[1]/'job.json'
                    if not current or current.get('status')!='processing':
                        try:
                            stored=json.loads(record.read_text())
                            if stored.get('id')==match[1] and stored.get('status') in ['completed','failed']:companion.jobs[match[1]]=stored
                        except (ValueError,OSError):pass
                    job=companion.jobs.get(match[1],{'status':'missing'})
                self.reply(200 if job['status']!='missing' else 404,job);return
            self.reply(404,{'error':'not-found'})
        def do_POST(self):
            if not companion.authenticated(self.headers.get('Authorization')):self.reply(401,{'error':'unauthorized'});return
            if self.path=='/api/lens-progress':
                try:
                    length=int(self.headers.get('Content-Length','0'))
                    if not 0<length<1500000:raise ValueError()
                    progress=json.loads(self.rfile.read(length))
                    if type(progress.get('acceptedViews')) is not int or not 0<=progress['acceptedViews']<=48:raise ValueError()
                    if progress.get('status') not in ['checking','fitting','saving','completed','stopped','failed']:raise ValueError()
                    if not isinstance(progress.get('hint'),str) or not 0<len(progress['hint'])<=300:raise ValueError()
                    checklist=progress.get('coverageChecklist')
                    active_round=progress.get('activeRound')
                    if active_round is not None and active_round not in ['framing','side-angles','high-low-angles','horizontal','vertical','variety','fitting','complete']:raise ValueError()
                    if checklist is not None and (not isinstance(checklist,dict) or set(checklist)!=set(['leftRightAngle','upDownAngle','horizontal','vertical']) or any(type(v) is not bool for v in checklist.values())):raise ValueError()
                    framing=None
                    scene=progress.get('sceneEnrollment',False)
                    if type(scene) is not bool:raise ValueError()
                    if progress.get('jpeg') and progress['status'] in ['checking','fitting']:
                        try:
                            from lens_framing import frame_outline,scene_outline
                            framing=(scene_outline if scene else frame_outline)(progress['jpeg'])
                        except Exception:
                            # Display failure is never calibration failure. Never return raw JPEGs.
                            framing={'kind':'display-only-charuco-framing','error':'unavailable','calibrationAuthority':False}
                    # Transient text/corner coordinates only. Original JPEG is never stored/returned.
                    companion.lens_progress={key:progress[key] for key in ['acceptedViews','hint','status']};companion.progress_updated=time.monotonic()
                    if checklist is not None:companion.lens_progress['coverageChecklist']=checklist
                    if active_round is not None:companion.lens_progress['activeRound']=active_round
                    companion.framing=framing
                    companion.scene_enrollment=scene
                    self.reply(200,{'status':'display-updated'})
                except (ValueError,KeyError,AttributeError,TypeError):self.reply(400,{'error':'invalid-progress'})
                return
            if self.path=='/api/board':
                try:
                    length=int(self.headers.get('Content-Length','0'))
                    if not 0<length<100000:raise ValueError()
                    value=json.loads(self.rfile.read(length));png=value['png'];data=base64.b64decode(png,validate=True)
                    if not data.startswith(b'\x89PNG\r\n\x1a\n'):raise ValueError()
                    mode=value.get('mode','computer')
                    if mode not in ['computer','tablet']:raise ValueError()
                    companion.board=png;companion.board_mode=mode;companion.scene_enrollment=False;companion.framing=None;companion.lens_progress=None;self.reply(200,{'status':'board-ready'})
                except (ValueError,KeyError):self.reply(400,{'error':'invalid-board'})
                return
            if self.path not in ['/api/captures','/api/distance-captures','/api/gait-distance-captures','/api/noise-captures','/api/rapid-captures']:self.reply(404,{'error':'not-found'});return
            try:
                size=int(self.headers.get('Content-Length','0'))
                if size<=0 or size>250*1024**2:raise ValueError('Capture size is invalid.')
                self.connection.settimeout(120);body=self.rfile.read(size)
                if len(body)!=size:raise ValueError('Capture upload was interrupted.')
                metres=None
                if self.path=='/api/distance-captures':
                    try:metres=int(self.headers.get('X-GaitTrace-Reference-Metres',''))
                    except ValueError:raise ValueError('Choose a 2, 3 or 5 m reference route.')
                key=companion.submit(body,metres,self.headers.get('X-GaitTrace-Route-Geometry','straight'),noise=self.path=='/api/noise-captures',gait=self.path=='/api/gait-distance-captures',rapid=self.path=='/api/rapid-captures');self.reply(202,{'id':key,'status':'processing'})
            except (ValueError,zipfile.BadZipFile,KeyError,json.JSONDecodeError) as e:self.reply(400,{'error':str(e)})
    return Handler
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8765);parser.add_argument('--no-browser',action='store_true');args=parser.parse_args()
    # Bootstrap is local and repeatable. No Docker Desktop subscription is used.
    check=subprocess.run(docker_prefix()+['image','inspect',IMAGE],capture_output=True)
    if check.returncode:
        subprocess.run(docker_prefix()+['build','-t',IMAGE,'-f',linux_path(BASE/'calibration-companion/Dockerfile'),linux_path(BASE/'calibration-companion')],check=True)
    info=subprocess.run(docker_prefix()+['info','--format','{{json .Runtimes}}'],capture_output=True,text=True)
    if info.returncode==0 and 'nvidia' in info.stdout:
        exists=subprocess.run(docker_prefix()+['image','inspect',GPU_IMAGE],capture_output=True)
        if exists.returncode:
            # Free official CUDA COLMAP image, fixed by digest rather than latest.
            pulled=subprocess.run(docker_prefix()+['build','-t',GPU_IMAGE,'-f',linux_path(BASE/'calibration-companion/Dockerfile.cuda'),linux_path(BASE/'calibration-companion')])
            if pulled.returncode:print('GPU image download failed; CPU processing remains available.',flush=True)
    from vio_compute import setup_compute
    from distance_pipeline import setup_distance_engine
    try:setup_distance_engine();setup_compute()
    except (OSError,subprocess.SubprocessError,ValueError,RuntimeError) as error:
        print('Research distance processing not ready; calibration remains available. '+str(error),flush=True)
    import qrcode # Check before starting the server.
    url=f'http://{private_host()}:{args.port}';companion=Companion(BASE.parent/'dist/calibration-processor')
    server=ThreadingHTTPServer(('0.0.0.0',args.port),handler(companion,url));print('Calibration page:',url,flush=True)
    if not args.no_browser:webbrowser.open(url)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
if __name__=='__main__':main()
