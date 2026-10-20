"""Few-view device tasks and first-order MAML camera focal residual model.

Solver-derived labels are research candidates, not physical ground truth. This
model does not infer extrinsics, clock offset or metric distance. Training and
saved results are orchestrated in phone_camera_imu_calibration.ipynb.
"""
import hashlib
import json
import math
import zipfile
from pathlib import Path

VERSION='camera-focal-fomaml-v1'


def load_examples(paths):
    """Ingest app bundles/helper examples, deduplicate immutable raw captures."""
    rows=[];seen=set();sources=set()
    for path in map(Path,paths):
        if path.suffix.lower()=='.zip':
            with zipfile.ZipFile(path) as archive:
                if len(archive.namelist())!=len(set(archive.namelist())):raise ValueError('ambiguous-enrollment-bundle')
                example=json.loads(archive.read('training-example.json'))
                capture=archive.read('input.zip')
                if hashlib.sha256(capture).hexdigest()!=example.get('sourceSha256'):raise ValueError('bundle-source-mismatch')
        else:
            example=json.loads(path.read_text())
            source=path.parent/'input.zip'
            if not source.is_file():raise ValueError('original-capture-required')
            capture=source.read_bytes()
            if hashlib.sha256(capture).hexdigest()!=example.get('sourceSha256'):raise ValueError('example-source-mismatch')
        if (example.get('kind')!='few-shot-camera-calibration-example-v1' or example.get('schemaVersion')!=1
                or example.get('labelSource')!='ikalibr-candidate-not-independent-truth' or example.get('independentValidation') is not False):
            raise ValueError('invalid-training-label-contract')
        b=example['binding'];device=example['device'];digest=example['sourceSha256']
        import io
        from rapid_calibration import BINDING,inspect_capture
        meta=inspect_capture(io.BytesIO(capture))
        if meta.get('artifactReplay') or any(meta.get(k)!=b.get(k) for k in BINDING) or meta.get('device')!=device:raise ValueError('source-binding-or-replay-mismatch')
        if 'synthetic' in json.dumps({'device':device,'binding':b}).lower():raise ValueError('synthetic-control-is-not-training-data')
        if len(digest)!=64 or any(c not in '0123456789abcdef' for c in digest):raise ValueError('invalid-source-hash')
        if example.get('artifactReplay'):raise ValueError('replay-is-not-new-training-data')
        model=(device.get('manufacturer'),device.get('model'))
        if not all(isinstance(v,str) and v for v in model) or not b.get('installationId'):raise ValueError('device-identity-missing')
        identity=(b['installationId'],b['captureId'])
        if identity in seen or digest in sources:continue
        seen.add(identity);sources.add(digest)
        p=example['referenceParameters']['CalibParam']['INTRI']['Camera']
        camera=[r['value']['ptr_wrapper']['data'] for r in p if r['key']=='/gaittrace/camera']
        if len(camera)!=1:raise ValueError('ambiguous-camera-label')
        focal=camera[0]['focal_length'];width,height=b['width'],b['height']
        if len(focal)!=2 or not all(math.isfinite(v) and 150<=v<=1600 for v in focal) or (width,height)!=(640,480):raise ValueError('unsupported-focal-label')
        features=[];frames=set()
        for view in example['features']:
            if view['frame'] in frames:raise ValueError('duplicated-few-shot-view')
            frames.add(view['frame']);f=view['focalPixels'][0]
            uncertainty=view['focalUncertaintyPixels'];uncertainty=float(uncertainty[0] if isinstance(uncertainty,list) else uncertainty)
            feature=[math.log(f[0]/width),math.log(f[1]/height),float(view['radialK1']),uncertainty/width]
            if not all(math.isfinite(v) for v in feature):raise ValueError('nonfinite-model-feature')
            features.append(feature)
        if len(features)!=10:raise ValueError('ten-disjoint-views-needed')
        rows.append({'sourceSha256':digest,'captureId':b['captureId'],'deviceGroup':'/'.join(model),
                     'taskGroup':json.dumps([b[k] for k in ['installationId','cameraId','opticalSetup','width','height','imageAxes']],separators=(',',':')),
                     'installationId':b['installationId'],'features':features,
                     'label':[math.log(focal[0]/width),math.log(focal[1]/height)],
                     'labelSource':example['labelSource']})
    return rows


def task_partition(rows,validation_device,test_device):
    """Hold out whole hardware models, never frames from the same phone."""
    groups={r['deviceGroup'] for r in rows}
    if len(groups)<5:raise ValueError('Need at least five phone models: three training, one validation, one held-out test. Current data cannot train this model honestly.')
    if validation_device==test_device or validation_device not in groups or test_device not in groups:raise ValueError('invalid-device-holdout')
    tasks={r.get('taskGroup',r['deviceGroup']) for r in rows}
    counts={g:len({r['captureId'] for r in rows if r.get('taskGroup',r['deviceGroup'])==g}) for g in tasks}
    if min(counts.values())<2:raise ValueError('Each device needs two separate physical enrollments for support/query tasks.')
    result={'train':[],'validation':[],'test':[]}
    for row in rows:
        split='validation' if row['deviceGroup']==validation_device else 'test' if row['deviceGroup']==test_device else 'train'
        result[split].append(row)
    # Five devices is a software minimum, not evidence of population validity.
    return result


def make_model():
    import torch
    # Predict a correction to GeoCalib log focal length, initialized to no change.
    model=torch.nn.Sequential(torch.nn.Linear(4,24),torch.nn.Tanh(),torch.nn.Linear(24,2))
    torch.nn.init.zeros_(model[-1].weight);torch.nn.init.zeros_(model[-1].bias)
    return model


def adapted_prediction(model,support,query,device,*,inner_steps=3,inner_lr=.05):
    """Support is five labelled views; query is a different physical capture.

    First-order MAML preserves the meta-gradient without second-order graphs.
    Adaptation requires a solver label; unlabelled views cannot magically supply
    metric/calibration truth. The app's current unlabeled setup uses GeoCalib.
    """
    import torch
    from torch.func import functional_call
    sx=torch.tensor(support['features'][:5],dtype=torch.float32,device=device)
    sy=torch.tensor(support['label'],dtype=torch.float32,device=device).expand(5,2)
    qx=torch.tensor(query['features'][5:],dtype=torch.float32,device=device)
    params=dict(model.named_parameters())
    for _ in range(inner_steps):
        loss=torch.nn.functional.mse_loss(sx[:,:2]+functional_call(model,params,(sx,)),sy)
        grads=torch.autograd.grad(loss,tuple(params.values()))
        params={k:v-inner_lr*g.detach() for (k,v),g in zip(params.items(),grads)}
    prediction=qx[:,:2]+functional_call(model,params,(qx,))
    return prediction

def episode_loss(model,support,query,device,*,inner_steps=3,inner_lr=.05):
    import torch
    prediction=adapted_prediction(model,support,query,device,inner_steps=inner_steps,inner_lr=inner_lr)
    qy=torch.tensor(query['label'],dtype=torch.float32,device=device).expand(5,2)
    return torch.nn.functional.mse_loss(prediction,qy),prediction,qy


def train(partition,output,*,epochs=100,seed=42,software_control=False):
    """GPU when available. Validation selects weights; test is evaluated once."""
    import torch
    groups={key:{r['deviceGroup'] for r in rows} for key,rows in partition.items()}
    if any(groups[a]&groups[b] for a,b in [('train','validation'),('train','test'),('validation','test')]) or len(groups['train'])<3 or not groups['validation'] or not groups['test']:
        raise ValueError('invalid-device-partition')
    if epochs<1:raise ValueError('invalid-training-epochs')
    if not software_control and any(r.get('labelSource')!='ikalibr-candidate-not-independent-truth' or 'synthetic' in r['deviceGroup'].lower() for rows in partition.values() for r in rows):
        raise ValueError('physical-candidate-labels-required')
    torch.manual_seed(seed);device='cuda' if torch.cuda.is_available() else 'cpu';model=make_model().to(device)
    optimizer=torch.optim.Adam(model.parameters(),lr=.001);out=Path(output);out.mkdir(parents=True,exist_ok=True)
    def pairs(rows):
        for group in sorted({r.get('taskGroup',r['deviceGroup']) for r in rows}):
            captures=sorted([r for r in rows if r.get('taskGroup',r['deviceGroup'])==group],key=lambda r:r['captureId'])
            if len(captures)<2:raise ValueError('separate-support-query-captures-needed')
            for i in range(len(captures)):yield captures[i],captures[(i+1)%len(captures)]
    best=math.inf;history=[];checkpoint=out/'focal-meta-model.pt'
    for epoch in range(epochs):
        losses=[]
        for s,q in pairs(partition['train']):
            optimizer.zero_grad();loss,_,_=episode_loss(model,s,q,device);loss.backward();optimizer.step();losses.append(float(loss.detach().cpu()))
        values=[float(episode_loss(model,s,q,device)[0].detach().cpu()) for s,q in pairs(partition['validation'])]
        value=sum(values)/len(values);history.append({'epoch':epoch,'trainMseLogFocal':sum(losses)/len(losses),'validationMseLogFocal':value})
        if value<best:
            best=value;torch.save({'version':VERSION,'weights':model.state_dict(),'inputDimension':4,'outputDimension':2,'seed':seed,'researchOnly':True,'independentValidation':False,'syntheticControl':software_control},checkpoint)
    model.load_state_dict(torch.load(checkpoint,weights_only=True,map_location=device)['weights'])
    errors=[]
    for s,q in pairs(partition['test']):
        _,prediction,label=episode_loss(model,s,q,device);errors.extend((torch.exp(prediction-label)-1).abs().detach().cpu().flatten().tolist())
    report={'kind':'few-shot-focal-training-report-v1','modelVersion':VERSION,'backend':device,'epochs':epochs,'seed':seed,
            'splitHardwareModels':{k:sorted(v) for k,v in groups.items()},'sourceSha256':{k:[r['sourceSha256'] for r in rows] for k,rows in partition.items()},
            'history':history,'heldOutMeanAbsFocalFraction':sum(errors)/len(errors),'checkpointSha256':hashlib.sha256(checkpoint.read_bytes()).hexdigest(),
            'labelSource':'synthetic-software-control' if software_control else 'ikalibr-candidate-not-independent-truth','syntheticControl':software_control,'independentValidation':False,'distanceModel':False,'deploymentApproved':False,
            'limitations':['focal-residual-only','support-requires-solver-label','held-out-errors-are-against-solver-candidates-not-physical-truth']}
    (out/'training-report.json').write_text(json.dumps(report,indent=2));return report


def adapt_focal(checkpoint,support,query):
    """Research inference after labelled support; cannot activate a phone profile."""
    import torch
    state=torch.load(checkpoint,weights_only=True,map_location='cpu')
    if state.get('version')!=VERSION or state.get('syntheticControl') is not False or state.get('researchOnly') is not True:raise ValueError('unusable-research-checkpoint')
    if support.get('labelSource')!='ikalibr-candidate-not-independent-truth':raise ValueError('support-needs-solver-label')
    device='cuda' if torch.cuda.is_available() else 'cpu';model=make_model().to(device);model.load_state_dict(state['weights'])
    if support.get('deviceGroup')!=query.get('deviceGroup') or support.get('installationId')!=query.get('installationId'):raise ValueError('support-needs-matching-phone')
    if support.get('taskGroup')!=query.get('taskGroup'):raise ValueError('support-needs-matching-camera-and-optics')
    prediction=adapted_prediction(model,support,query,device)
    focal=torch.exp(prediction)*torch.tensor([640,480],device=device)
    baseline=torch.exp(torch.tensor(query['features'][5:],dtype=torch.float32,device=device)[:,:2])*torch.tensor([640,480],device=device)
    if not torch.isfinite(focal).all() or torch.max(torch.abs(focal/baseline-1))>.08:raise ValueError('learned-residual-outside-research-bounds')
    return {'kind':'few-shot-focal-research-prediction-v1','version':VERSION,'focalPixels':focal.detach().cpu().tolist(),
            'supportSourceSha256':support['sourceSha256'],'querySourceSha256':query['sourceSha256'],
            'checkpointSha256':hashlib.sha256(Path(checkpoint).read_bytes()).hexdigest(),
            'distanceReady':False,'fullCalibrationReady':False,'deploymentApproved':False,'independentValidation':False}
