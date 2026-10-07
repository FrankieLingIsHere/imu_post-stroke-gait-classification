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
def run_reference(folder):
    shared=['run','--rm','--network','none','--shm-size','512m','--mount',f'type=bind,src={linux_path(folder)},dst=/data','--mount',f'type=bind,src={linux_path(BASE/"calibration-companion")},dst=/bridge,readonly']
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
    result=json.loads((folder/'result.json').read_text())
    if result.get('method')!='ikalibr-tro-2025' or result.get('distanceReady') is not False:raise ValueError('Invalid reference-engine result.')
    return result
def private_host():
    with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as sock:
        try:sock.connect(('8.8.8.8',80));return sock.getsockname()[0]
        except OSError:return '127.0.0.1'
class Companion:
    def __init__(self,folder,runner=run_reference):
        self.folder=Path(folder);self.folder.mkdir(parents=True,exist_ok=True);self.runner=runner
        self.token=secrets.token_hex(32);self.board_token=secrets.token_hex(32);self.jobs={};self.lock=threading.Lock();self.processing=False;self.board=None;self.board_mode='computer';self.lens_progress=None;self.progress_updated=0;self.framing=None
        for record in self.folder.glob('*/job.json'):
            try:
                job=json.loads(record.read_text());key=record.parent.name
                if re.fullmatch('[0-9a-f]{24}',key) and job.get('status') in ['completed','failed']:self.jobs[key]=job
            except (ValueError,OSError):pass
    def authenticated(self,header):return hmac.compare_digest(header or '',f'Bearer {self.token}')
    def submit(self,body):
        if not body or len(body)>250*1024**2:raise ValueError('Capture size is invalid.')
        with zipfile.ZipFile(io.BytesIO(body)) as z:
            if sum(v.file_size for v in z.infolist())>350*1024**2 or z.getinfo('manifest.json').file_size>1024**2:raise ValueError('Capture size is invalid.')
            if len(set(z.namelist()))!=len(z.namelist()):raise ValueError('Capture contains ambiguous files.')
            meta=json.loads(z.read('manifest.json'))
            if meta.get('kind')!='phone-camera-imu-alignment-capture-v1' or meta.get('status')!='completed' or meta.get('error'):raise ValueError('A completed sensor-alignment capture is needed.')
        key=hashlib.sha256(body).hexdigest()[:24]
        with self.lock:
            if key in self.jobs:return key
            if self.processing:raise ValueError('The computer is already processing a capture.')
            self.processing=True;self.jobs[key]={'id':key,'status':'processing'}
        folder=self.folder/key;folder.mkdir(exist_ok=True);(folder/'input.zip').write_bytes(body)
        def work():
            try:
                result=self.runner(folder)
                job={'id':key,'status':'completed','result':result}
            except Exception:
                # Details stay in the local processor log. Never return a successful
                # calibration from an empty output, timeout or upstream exit 0.
                job={'id':key,'status':'failed','message':'Reference processing could not complete. The capture is kept for review.'}
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
            if self.path=='/api/health':self.reply(200,{'kind':'gaittrace-local-calibration-service-v1','method':'ikalibr-tro-2025','distanceReady':False});return
            if self.path=='/api/page-state':
                self.reply(200,{'png':companion.board,'mode':companion.board_mode,'progress':companion.lens_progress,'progressAgeSeconds':time.monotonic()-companion.progress_updated if companion.lens_progress else None,'framing':companion.framing});return
            match=re.fullmatch(r'/api/jobs/([0-9a-f]{24})',self.path)
            if match:self.reply(200 if match[1] in companion.jobs else 404,companion.jobs.get(match[1],{'status':'missing'}));return
            self.reply(404,{'error':'not-found'})
        def do_POST(self):
            if not companion.authenticated(self.headers.get('Authorization')):self.reply(401,{'error':'unauthorized'});return
            if self.path=='/api/lens-progress':
                try:
                    length=int(self.headers.get('Content-Length','0'))
                    if not 0<length<1500000:raise ValueError()
                    progress=json.loads(self.rfile.read(length))
                    if type(progress.get('acceptedViews')) is not int or not 0<=progress['acceptedViews']<=48:raise ValueError()
                    if progress.get('status') not in ['checking','completed','stopped','failed']:raise ValueError()
                    if not isinstance(progress.get('hint'),str) or not 0<len(progress['hint'])<=300:raise ValueError()
                    framing=None
                    if progress.get('jpeg') and progress['status']=='checking':
                        try:
                            from lens_framing import frame_outline
                            framing=frame_outline(progress['jpeg'])
                        except Exception:
                            # Display failure is never calibration failure. Never return raw JPEGs.
                            framing={'kind':'display-only-charuco-framing','error':'unavailable','calibrationAuthority':False}
                    # Transient text/corner coordinates only. Original JPEG is never stored/returned.
                    companion.lens_progress={key:progress[key] for key in ['acceptedViews','hint','status']};companion.progress_updated=time.monotonic()
                    companion.framing=framing
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
                    companion.board=png;companion.board_mode=mode;companion.framing=None;companion.lens_progress=None;self.reply(200,{'status':'board-ready'})
                except (ValueError,KeyError):self.reply(400,{'error':'invalid-board'})
                return
            if self.path!='/api/captures':self.reply(404,{'error':'not-found'});return
            try:
                size=int(self.headers.get('Content-Length','0'))
                if size<=0 or size>250*1024**2:raise ValueError('Capture size is invalid.')
                self.connection.settimeout(120);body=self.rfile.read(size)
                if len(body)!=size:raise ValueError('Capture upload was interrupted.')
                key=companion.submit(body);self.reply(202,{'id':key,'status':'processing'})
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
    import qrcode # Check before starting the server.
    url=f'http://{private_host()}:{args.port}';companion=Companion(BASE.parent/'dist/calibration-processor')
    server=ThreadingHTTPServer(('0.0.0.0',args.port),handler(companion,url));print('Calibration page:',url,flush=True)
    if not args.no_browser:webbrowser.open(url)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
if __name__=='__main__':main()
