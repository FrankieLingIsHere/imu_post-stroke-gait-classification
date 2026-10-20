"""Pinned learned prior + disjoint-view consistency; never certifies distance."""
import hashlib
import json
import math
import sys
import zipfile
from pathlib import Path

from rapid_calibration import BINDING, CHECKOUT_REVISION, CHECKPOINT_SHA256, inspect_capture

def validate_seed(seed,binding):
    import numpy as np
    l=seed.get('learned',{});K=np.asarray(seed.get('lens',{}).get('cameraMatrix'),dtype=float);D=np.asarray(seed.get('lens',{}).get('distortion'),dtype=float)
    if (seed.get('kind')!='phone-learned-lens-seed-v1' or seed.get('method')!='geocalib-eccv2024-seed'
        or seed.get('lensReady') is not False or seed.get('calibrationSeedReady') is not True
        or any(seed.get(k) is not False for k in ['distanceReady','fullCalibrationReady','independentDistanceValidation'])
        or any(seed.get('binding',{}).get(k)!=binding.get(k) for k in BINDING)
        or l.get('sourceCommit')!=CHECKOUT_REVISION or l.get('checkpointSha256')!=CHECKPOINT_SHA256
        or l.get('supportViews')!=5 or l.get('queryViews')!=5 or l.get('disjointViews') is not True or l.get('qualityAccepted') is not True
        or l.get('neuralWeightsUpdated') is not False or l.get('fullLensValidated') is not False or l.get('internalUncertaintyValidated') is not False
        or not math.isfinite(l.get('viewConsistencyFraction',math.inf)) or not 0<=l['viewConsistencyFraction']<=.08
        or K.shape!=(3,3) or not np.isfinite(K).all() or not 150<=K[0,0]<=1600 or not 150<=K[1,1]<=1600
        or K[0,2]!=320 or K[1,2]!=240 or K[0,1]!=0 or K[1,0]!=0 or not np.array_equal(K[2],[0,0,1])
        or D.shape!=(5,) or not np.isfinite(D).all() or abs(D[0])>.3 or np.any(D[1:]!=0)):
        raise ValueError('learned-seed-failed-integrity')
    return seed

def refined_lens(reference):
    """Use solver-refined Brown parameters, not the initial learned seed, in VIO."""
    import numpy as np
    rows=reference['upstreamParameters']['CalibParam']['INTRI']['Camera']
    cameras=[r['value']['ptr_wrapper']['data'] for r in rows if r['key']=='/gaittrace/camera']
    if len(cameras)!=1:raise ValueError('ambiguous-refined-camera')
    camera=cameras[0];f=np.asarray(camera['focal_length']);c=np.asarray(camera['principal_point']);d=np.asarray(camera['disto_param'])
    if (f.shape!=(2,) or c.shape!=(2,) or d.shape!=(5,) or not np.isfinite(np.r_[f,c,d]).all()
        or np.any(f<150) or np.any(f>1600) or not 160<=c[0]<=480 or not 120<=c[1]<=360
        or np.max(np.abs(d))>5 or camera['img_width']!=640 or camera['img_height']!=480):raise ValueError('refined-lens-outside-research-bounds')
    return {'model':'opencv-pinhole-radtan5','cameraMatrix':[[float(f[0]),0,float(c[0])],[0,float(f[1]),float(c[1])],[0,0,1]],
            'distortion':[float(d[0]),float(d[1]),float(d[3]),float(d[4]),float(d[2])],
            'origin':'ikalibr-refined-candidate','independentLensValidation':False}


def seed_from_predictions(meta, support, query, provenance):
    """All thresholds are experimental engineering checks, not clinical limits."""
    import numpy as np
    focal = np.array(support['focalPixels'][0], dtype=float)
    other = np.array(query['focalPixels'][0], dtype=float)
    dist = float(support['radialK1'])
    if (focal.shape != (2,) or not np.isfinite(focal).all()
            or not np.isfinite(other).all() or not math.isfinite(dist)
            or np.any(focal < 150) or np.any(focal > 1600) or abs(dist) > .3
            or np.max(np.abs(other/focal-1)) > .08):
        raise ValueError('view-estimates-disagree')
    binding = {k:meta[k] for k in BINDING}
    return {'schemaVersion':1,'kind':'phone-learned-lens-seed-v1',
            'method':'geocalib-eccv2024-seed','status':'experimental-lens-seed',
            'binding':binding,'lensReady':False,'calibrationSeedReady':True,
            'distanceReady':False,'fullCalibrationReady':False,
            'independentDistanceValidation':False,
            'lens':{'model':'opencv-pinhole-radtan5',
                    'cameraMatrix':[[float(focal[0]),0,meta['width']/2],
                                    [0,float(focal[1]),meta['height']/2],[0,0,1]],
                    'distortion':[dist,0.,0.,0.,0.]},
            'learned':{**provenance,'supportViews':5,'queryViews':5,
                       'disjointViews':True,'viewConsistencyFraction':float(np.max(np.abs(other/focal-1))),
                       'qualityAccepted':True,'neuralWeightsUpdated':False,
                       'assumedZeroCoefficients':['k2','p1','p2','k3'],
                       'principalPointAssumed':'image-center',
                       'fullLensValidated':False,'internalUncertaintyValidated':False}}


def process(config):
    import subprocess
    import numpy as np
    source, out = Path(config['source']), Path(config['output'])
    meta = inspect_capture(source)
    checkout = Path(config['checkout'])
    revision = subprocess.run(['git','-C',str(checkout),'rev-parse','HEAD'],
                              check=True,capture_output=True,text=True).stdout.strip()
    if revision != CHECKOUT_REVISION:raise ValueError('model-source-mismatch')
    sys.path[:0] = [config['dependencies'], str(checkout)]
    import cv2
    import torch
    from geocalib import GeoCalib
    torch.hub.set_dir(config['cache']);torch.manual_seed(42)
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = GeoCalib(weights='distorted').to(device)
    with zipfile.ZipFile(source) as archive:
        imu=[json.loads(s) for s in archive.read('imu.ndjson').decode().splitlines() if s.strip()]
        origin=meta['alignmentMovementStartedBootNs']
        for sensor, minimum in [('gyroscope',1e-4),('accelerometer',.001)]:
            rows=[r for r in imu if r['sensor']==sensor and r['timestampNs']>=origin]
            values=np.array([[r[k] for k in ['x','y','z']] for r in rows],dtype=float)
            times=np.array([r['timestampNs'] for r in rows],dtype=np.int64)
            if (len(rows)<100 or not np.isfinite(values).all() or np.any(np.diff(times)<=0)
                    or np.max(np.diff(times))>25000000
                    or np.min(np.linalg.eigvalsh(np.cov(values.T)))<minimum):
                raise ValueError('more-varied-motion-needed')
        index=[json.loads(s) for s in archive.read('frames.ndjson').decode().splitlines() if s.strip()]
        index=[r for r in index if r['timestampNs']>=origin]
        if len(index)<300 or index[-1]['timestampNs']-origin<40000000000:
            raise ValueError('continuous-scan-needed')
        selected=[]
        # Each time stratum supplies one distinct clear view. Interleaving assigns
        # five support and five query images; no frame is used in both sets.
        for block in np.array_split(np.arange(len(index)),10):
            candidates=[]
            for i in block[::max(1,len(block)//8)]:
                row=index[int(i)];name=row['file']
                if not name.startswith('frames/') or '..' in name:raise ValueError('invalid-frame-path')
                data=archive.read(name);image=cv2.imdecode(np.frombuffer(data,np.uint8),cv2.IMREAD_GRAYSCALE)
                if image is None or image.shape!=(480,640):continue
                sharp=float(cv2.Laplacian(image,cv2.CV_64F).var())
                corners=cv2.goodFeaturesToTrack(image,100,.01,15)
                if sharp>=20 and corners is not None and len(corners)>=40:
                    candidates.append((sharp,row,data))
            if not candidates:raise ValueError('clear-scene-views-needed')
            _,row,data=max(candidates,key=lambda item:item[0])
            path=out/f'enrollment-view-{len(selected)}.jpg';path.write_bytes(data)
            selected.append((path,row['file'],hashlib.sha256(data).hexdigest()))
    tensors=[model.load_image(path).to(device) for path,_,_ in selected]
    def predict(items):
        result=model.calibrate(torch.stack(items),camera_model='simple_radial',shared_intrinsics=True)
        return {'focalPixels':result['camera'].f.detach().cpu().tolist(),
                'radialK1':float(result['camera'].dist.detach().cpu()[0,0]),
                'focalUncertaintyPixels':result['focal_uncertainty'].detach().cpu().tolist()}
    support=predict(tensors[::2]);query=predict(tensors[1::2])
    checkpoint=Path(config['cache'])/'geocalib/distorted.tar'
    if hashlib.sha256(checkpoint.read_bytes()).hexdigest()!=CHECKPOINT_SHA256:raise ValueError('model-checkpoint-mismatch')
    provenance={'sourceCommit':revision,'checkpointSha256':hashlib.sha256(checkpoint.read_bytes()).hexdigest(),
                'workerSourceSha256':config.get('workerSourceSha256'),'orchestratorSourceSha256':config.get('orchestratorSourceSha256'),
                'backend':device,'torchVersion':torch.__version__,'enrollmentRevision':config['revision'],
                'frameSha256':{name:digest for _,name,digest in selected},
                'support':support,'query':query,
                'viewPredictions':[{**predict([tensor]),'frame':name} for tensor,(_,name,_) in zip(tensors,selected)]}
    seed=seed_from_predictions(meta,support,query,provenance)
    (out/'lens-seed.json').write_text(json.dumps(seed,indent=2),encoding='utf-8')
    print(json.dumps({'status':'experimental-lens-seed','backend':device,'consistency':seed['learned']['viewConsistencyFraction']}))
    return seed


def warmup(config):
    import subprocess
    revision=subprocess.run(['git','-C',config['checkout'],'rev-parse','HEAD'],check=True,capture_output=True,text=True).stdout.strip()
    if revision!=CHECKOUT_REVISION:raise ValueError('model-source-mismatch')
    sys.path[:0]=[config['dependencies'],config['checkout']]
    import torch
    from geocalib import GeoCalib
    torch.hub.set_dir(config['cache']);device='cuda' if torch.cuda.is_available() else 'cpu'
    model=GeoCalib(weights='distorted').to(device)
    # Execute kernels before advertising runtime readiness; initialization alone
    # does not establish that the requested GPU can run this model.
    with torch.inference_mode():model.calibrate(torch.zeros(1,3,480,640,device=device),camera_model='simple_radial',shared_intrinsics=True)
    if device=='cuda':torch.cuda.synchronize()
    checkpoint=Path(config['cache'])/'geocalib/distorted.tar'
    if hashlib.sha256(checkpoint.read_bytes()).hexdigest()!=CHECKPOINT_SHA256:raise ValueError('model-checkpoint-mismatch')
    result={'kind':'learned-enrollment-runtime-check-v1','backend':device,'sourceCommit':revision,'checkpointSha256':CHECKPOINT_SHA256,'kernelsExecuted':True}
    Path(config['checkout']).parent.joinpath('enrollment-runtime.json').write_text(json.dumps(result))
    print(json.dumps(result));return result

if __name__ == '__main__':
    if sys.argv[1]=='--warmup':warmup(json.loads(Path(sys.argv[2]).read_text()));raise SystemExit(0)
    config=json.loads(Path(sys.argv[1]).read_text())
    try:process(config)
    except Exception as error:
        Path(config['output'],'learned-failure.json').write_text(json.dumps({'reason':str(error),'type':type(error).__name__}))
        raise
