"""Standard COLMAP SfM, with explicit CUDA or CPU execution and provenance.
This stage supplies measured image poses to the published calibration solver.
It is not a distance estimator or a substitute camera/IMU calibration fit.
"""
import argparse,hashlib,json,os,re,shutil,subprocess,time
from pathlib import Path

ROOT=Path('/data')
def run_sfm(gpu=False):
    plan=json.loads((ROOT/'sfm-stage.json').read_text())
    sfm=ROOT/plan['workspace'];images=ROOT/plan['images'];image_list=ROOT/'sfm-images.txt'
    backend='cuda' if gpu else 'cpu'
    db=sfm/(backend+'-keyframes.db');models=sfm/(backend+'-models');models.mkdir(exist_ok=True)
    environment={**os.environ,'QT_QPA_PLATFORM':'offscreen'}
    version=subprocess.run(['colmap','-h'],capture_output=True,text=True,check=True).stdout.splitlines()[:3]
    if gpu and 'without CUDA' in '\n'.join(version):raise ValueError('COLMAP was compiled without CUDA.')
    def options(command):
        help_result=subprocess.run(['colmap',command,'-h'],capture_output=True,text=True,check=True)
        return help_result.stdout+help_result.stderr
    # COLMAP renamed these namespaces; query the actual pinned executable.
    extraction='FeatureExtraction' if '--FeatureExtraction.use_gpu' in options('feature_extractor') else 'SiftExtraction'
    matching='FeatureMatching' if '--FeatureMatching.use_gpu' in options('sequential_matcher') else 'SiftMatching'
    timings={}
    def command(args,label):
        began=time.monotonic()
        with (ROOT/('sfm-'+backend+'-'+label+'.log')).open('w') as log:
            subprocess.run(['colmap',*args],check=True,stdout=log,stderr=subprocess.STDOUT,env=environment,timeout=2400)
        timings[label]=time.monotonic()-began
    command(['feature_extractor','--database_path',str(db),'--image_path',str(images),'--image_list_path',str(image_list),'--ImageReader.camera_model','PINHOLE','--ImageReader.single_camera','1','--ImageReader.camera_params',plan['cameraParameters'],f'--{extraction}.use_gpu',str(int(gpu)),f'--{extraction}.num_threads','2','--SiftExtraction.max_num_features','2000'],'features')
    command(['sequential_matcher','--database_path',str(db),'--SequentialMatching.overlap','30','--SequentialMatching.loop_detection','0',f'--{matching}.use_gpu',str(int(gpu)),f'--{matching}.num_threads','2'],'matches')
    command(['mapper','--database_path',str(db),'--image_path',str(images),'--output_path',str(models),'--Mapper.num_threads','2','--Mapper.init_min_tri_angle','25','--Mapper.init_max_error','2','--Mapper.tri_min_angle','3','--Mapper.ba_refine_focal_length','0','--Mapper.ba_refine_principal_point','0'],'map')
    coherent=sorted(p.parent for p in models.glob('*/images.bin'))
    if len(coherent)!=1:raise ValueError('Scene reconstruction was empty or fragmented. The capture is kept.')
    command(['model_converter','--input_path',str(coherent[0]),'--output_path',str(sfm),'--output_type','TXT'],'convert')
    registered=re.search(r'Number of images:\s*(\d+)',(sfm/'images.txt').read_text())
    if not registered or int(registered[1])<2:raise ValueError('The reconstruction had too few registered images.')
    # A completed executable is necessary; merely seeing nvidia-smi is not proof
    # that this capture was processed with GPU feature extraction and matching.
    evidence={'backend':backend,'image':os.environ.get('GAITTRACE_SFM_IMAGE'),'colmapVersion':version,'executableSha256':hashlib.sha256(Path(shutil.which('colmap')).read_bytes()).hexdigest(),'measuredKeyframes':plan['measuredKeyframes'],'registeredImages':int(registered[1]),'matcher':'standard sequential; 30 neighbouring images; loop detection disabled','stageSeconds':timings,'gpuRequestedFor':['features','matches'] if gpu else [],'mapperGpuRequested':False,'calibrationSolverGpuRequested':False}
    (ROOT/'sfm-complete.json').write_text(json.dumps(evidence,indent=2))
    return evidence
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--gpu',action='store_true');args=parser.parse_args()
    print(json.dumps(run_sfm(args.gpu),indent=2))
