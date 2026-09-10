"""Frozen-model mechanism probes, not candidate preprocessing or validation.

Only four already inspected TVS people and deterministic development controls
are opened. The new cohort extension is deliberately not consulted.
"""
from pathlib import Path
import hashlib
import json
import sys
import numpy as np
import pandas as pd
import torch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from models.predict_lower_back import load_bundle
from models.lower_back_ensemble import LowerBackDomainNet
from src.models.evidence_gated_domain_generalization import load_development_data,BalancedSourceBatcher

BASE=ROOT/'data/interim/public_imu_screen_2026-09-08'
OUT=BASE/'positive_call_diagnosis_v1'
VARIANTS=('identity','mean_to_one','half_dynamic_amplitude','double_dynamic_amplitude',
          'keep_below_5hz','keep_below_10hz','time_reverse','time_shuffle','constant_mean')


def transform(x,name):
    x=np.asarray(x,dtype=np.float32);mean=x.mean(axis=1,keepdims=True)
    if name=='identity':return x.copy()
    if name=='mean_to_one':return x-mean+1
    if name=='half_dynamic_amplitude':return mean+.5*(x-mean)
    if name=='double_dynamic_amplitude':return mean+2*(x-mean)
    if name.startswith('keep_below_'):
        cutoff=5 if name=='keep_below_5hz' else 10
        z=np.fft.rfft(x,axis=1);z[:,np.fft.rfftfreq(500,.01)>cutoff,:]=0
        return np.fft.irfft(z,n=500,axis=1).astype(np.float32)
    if name=='time_reverse':return x[:,::-1,:].copy()
    if name=='time_shuffle':
        return x[:,np.random.default_rng(20260908).permutation(500),:].copy()
    if name=='constant_mean':return np.broadcast_to(mean,x.shape).copy()
    raise ValueError(name)


def main():
    OUT.mkdir(exist_ok=True)
    if (OUT/'summary.json').exists():raise FileExistsError('Diagnosis complete; read saved results')
    checkpoint=ROOT/'models/checkpoints/stroke-gait-lower-back-ensemble-v0.2.0.pt'
    bundle=load_bundle(checkpoint,checkpoint.with_suffix('.manifest.json'))
    dev,meta=load_development_data(ROOT/'data/processed')
    arrays=[];identities=[];selection=[]
    for (source,label),frame in meta.groupby(['source','label']):
        for person in sorted(frame['group'].unique())[:4]:
            indices=frame.index[frame['group']==person].to_numpy()
            indices=indices[np.linspace(0,len(indices)-1,min(3,len(indices)),dtype=int)]
            arrays.append(dev[indices,:,[0]].reshape(len(indices),500,1))
            identities.extend([dict(scope='development_resubstitution',source=source,label=label,participant=person)]*len(indices))
            selection.append(dict(participant=person,indices=indices.tolist()))
    old=json.loads((BASE/'hallway_probe_v1/results.json').read_text())
    for person in old['participants']:
        path=BASE/'hallway_probe_v1'/person['cohort']/person['participant']/'windows.npy'
        if hashlib.sha256(path.read_bytes()).hexdigest()!=person['windows_sha256']:raise ValueError('TVS input changed')
        x=np.load(path);arrays.append(x)
        identities.extend([dict(scope='inspected_TVS',source='TVS',label=person['cohort'],participant=person['cohort']+'/'+person['participant'])]*len(x))
    x=np.concatenate(arrays)
    lock=dict(scope='mechanism probes only; never used to select a correction',variants=VARIANTS,
              selection=selection,tvs='four previously inspected hallway people only',
              controls='24 development people, up to three equally spaced windows each; resubstitution not held-out accuracy',
              limitations='FFT cutoffs imply periodic boundaries; shuffled/constant/doubled signals can be outside physiological distribution',
              script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              input_sha256=hashlib.sha256(x.tobytes()).hexdigest(),
              checkpoint_sha256=hashlib.sha256(checkpoint.read_bytes()).hexdigest())
    lock_path=OUT/'protocol.json'
    if lock_path.exists():
        if json.loads(lock_path.read_text())!=json.loads(json.dumps(lock)):raise ValueError('Changed diagnostic protocol')
    else:
        with lock_path.open('x') as f:json.dump(lock,f,indent=2)
    torch.set_num_threads(4)
    samples=np.concatenate([transform(x,v) for v in VARIANTS])
    sums=np.zeros(len(samples),dtype=np.float64);method_scores={m:np.zeros(len(samples)) for m in ('erm','coral','ermpp_style')}
    member_rows=[];biases=[]
    with torch.inference_mode():
        for member in bundle['members']:
            model=LowerBackDomainNet().eval();model.load_state_dict(member['model_state_dict'])
            mu=float(member['mean'].item());sd=float(member['std'].item())
            scores=[];identity_logits=[]
            for start in range(0,len(samples),256):
                t=torch.from_numpy(np.ascontiguousarray(((samples[start:start+256]-mu)/sd).transpose(0,2,1)))
                z=model(t);scores.extend(torch.sigmoid(z).numpy().tolist())
                if start==0:identity_logits=z[:len(x)].numpy()
            scores=np.asarray(scores);sums+=scores/15;method_scores[member['method']]+=scores/5
            bias=float(model.classifier[2].bias.item());biases.append(dict(method=member['method'],seed=member['seed'],head_bias=bias))
            frame=pd.DataFrame(identities);frame['score']=scores[:len(x)];frame['logit']=identity_logits
            for keys,g in frame.groupby(['scope','source','label','participant']):
                member_rows.append(dict(zip(('scope','source','label','participant'),keys),method=member['method'],seed=member['seed'],
                                        mean_score=float(g.score.mean()),mean_logit=float(g.logit.mean()),head_bias=bias,
                                        mean_feature_contribution=float(g.logit.mean()-bias)))
    rows=[]
    for v,variant in enumerate(VARIANTS):
        frame=pd.DataFrame(identities);frame['score']=sums[v*len(x):(v+1)*len(x)]
        for method,values in method_scores.items():frame[method]=values[v*len(x):(v+1)*len(x)]
        for keys,g in frame.groupby(['scope','source','label','participant']):
            rows.append(dict(zip(('scope','source','label','participant'),keys),variant=variant,
                             mean_score=float(g.score.mean()),positive=bool(g.score.mean()>=.5),
                             **{method:float(g[method].mean()) for method in method_scores}))
    frame=pd.DataFrame(rows)
    for person in old['participants']:
        actual=frame[(frame.participant==person['cohort']+'/'+person['participant'])&(frame.variant=='identity')].iloc[0].mean_score
        np.testing.assert_allclose(actual,person['mean_score'],atol=1e-6,rtol=0)
    batcher=BalancedSourceBatcher(meta,np.ones(len(meta),dtype=bool),64,42);idx,_=batcher.draw()
    balance=meta.iloc[idx].groupby(['source','label']).size().to_dict()
    frame.to_csv(OUT/'participant_probes.csv',index=False)
    pd.DataFrame(member_rows).to_csv(OUT/'member_identity.csv',index=False)
    summary=dict(identity_reproduced=True,head_biases=biases,
                 actual_batch_counts={str(k):int(v) for k,v in balance.items()},
                 groups=frame.groupby(['scope','label','variant']).agg(people=('participant','size'),positive=('positive','sum'),mean_score=('mean_score','mean')).reset_index().to_dict('records'))
    with (OUT/'summary.json').open('x') as f:json.dump(summary,f,indent=2)
    print(frame[frame.scope=='inspected_TVS'][['participant','variant','mean_score','erm','coral','ermpp_style']].to_string(index=False))
    print('BATCH',summary['actual_batch_counts'])
    print('HEAD BIAS RANGE',min(b['head_bias'] for b in biases),max(b['head_bias'] for b in biases))


if __name__=='__main__':main()
