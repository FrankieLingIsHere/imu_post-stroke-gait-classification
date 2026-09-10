"""Controlled feature fusion with a lower-back network and ElderNet."""
from pathlib import Path
import sys,json,copy
import numpy as np
import pandas as pd
import torch
from sklearn.metrics import roc_auc_score

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from scripts.classification.probe_eldernet_lower_back import build_encoder,to_eldernet_window,sha,UP
from src.data.voisard_aligned import load_aligned_lower_back
from models.lower_back_ensemble import LowerBackDomainNet
PRIOR=ROOT/'data/processed/eldernet_lower_back_v1'
OUT=ROOT/'data/processed/eldernet_fusion_v1'
SEED=20260909


def split_calibration(train,fold):
    rng=np.random.default_rng(SEED+fold); ids=[]
    for target,g in train.groupby('target'):
        assert len(g)>=2
        ids.extend(rng.choice(sorted(g.participant),min(len(g)-1,max(1,int(np.ceil(len(g)*.25)))),replace=False))
    return train[~train.participant.isin(ids)],train[train.participant.isin(ids)]


def digest_state(module):
    import hashlib
    h=hashlib.sha256()
    for k,v in module.state_dict().items():
        h.update(k.encode());h.update(v.detach().cpu().numpy().tobytes())
    return h.hexdigest()


def fusion_logits(model, head, main, cache, magnitude, indices, mean, std, device):
    batch=(magnitude[indices].to(device)-mean)/std
    primary=main.features(batch.reshape(-1,1,500)).flatten(1).reshape(len(indices),2,64).mean(1)
    primary=torch.nn.functional.layer_norm(primary,(64,))
    if model is not None:
        aux=model.feature_extractor.layer5(cache[indices].to(device))
        aux=model.fc(aux.flatten(1))
        aux=torch.nn.functional.layer_norm(aux,(128,))
        primary=torch.cat([primary,aux],dim=1)
    return head(primary).flatten()


def aggregate(model,head,main,cache,magnitude,mean,std,meta,people,device):
    main.eval()
    mask=meta.participant.isin(people.participant);ix=np.flatnonzero(mask)
    parts=[]
    with torch.no_grad():
        for a in range(0,len(ix),128):
            parts.extend(fusion_logits(model,head,main,cache,magnitude,ix[a:a+128],mean,std,device).sigmoid().cpu().numpy())
    frame=meta.loc[mask,['participant','trial']].copy();frame['score']=parts
    score=frame.groupby(['participant','trial']).score.mean().groupby('participant').mean()
    return people.merge(score,on='participant',validate='one_to_one')


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    if (OUT/'decision.json').exists():raise FileExistsError('Completed; inspect saved results')
    torch.set_num_threads(4)
    torch.backends.cudnn.benchmark=False
    device='cuda' if torch.cuda.is_available() else 'cpu'
    sources=[Path(__file__),ROOT/'docs/classification/ELDERNET_FUSION_PROTOCOL.md',
             PRIOR/'window_metadata.csv',PRIOR/'participant_coverage.csv',
             ROOT/'scripts/classification/probe_eldernet_lower_back.py',UP/'weights/gait_speed_weights.pt']
    (OUT/'manifest.json').write_text(json.dumps({str(p.relative_to(ROOT)):sha(p) for p in sources},indent=2))
    for item in json.loads((UP/'acquisition.json').read_text())['files']:
        assert sha(UP/item['path'])==item['sha256']
    meta=pd.read_csv(PRIOR/'window_metadata.csv');coverage=pd.read_csv(PRIOR/'participant_coverage.csv')
    coverage.to_csv(OUT/'participant_coverage.csv',index=False)
    people=coverage[coverage.available].copy()
    paths={p.stem.removesuffix('_meta'):p for p in (ROOT/'data/raw/voisard_2025/data').glob('*/*/*/*/*_meta.json')}
    x=np.empty((len(meta),3,300),dtype='float32')
    magnitude=np.empty((len(meta),2,1,500),dtype='float32')
    for trial,g in meta.groupby('trial'):
        p=paths[trial];assert sha(p.parent/f'{trial}_raw_data_LB.txt')==g.raw_sha256.iloc[0]
        raw,_=load_aligned_lower_back(p.parent,trial)
        for r in g.itertuples():
            chunk=raw[r.start:r.start+1000]
            x[r.Index]=to_eldernet_window(chunk)
            magnitude[r.Index]=np.linalg.norm(chunk/9.80665,axis=1).reshape(2,1,500)
    magnitude=torch.from_numpy(magnitude)
    caches={}; originals={}
    for kind in ['random','pretrained']:
        model=build_encoder(kind=='pretrained').to(device)
        early=torch.nn.Sequential(*list(model.feature_extractor.children())[:4]).eval()
        with torch.no_grad():
            caches[kind]=torch.cat([early(torch.from_numpy(x[i:i+64]).to(device)).cpu() for i in range(0,len(x),64)])
        originals[kind]=model.cpu()
    print('Reconstructed verified windows and cached frozen layers 1-4',flush=True)
    rows=[];calrows=[];splits=[];lossrows=[];checks=[];thresholds=[]
    for scope,data in [('all_available',people),('matched_available',people[people.matched])]:
        for fold in sorted(data.fold.unique()):
            outer,test=data[data.fold.ne(fold)],data[data.fold.eq(fold)]
            fit,cal=split_calibration(outer,int(fold))
            assert not set(outer.participant)&set(test.participant)
            assert not set(outer.loc[outer.target.eq(2),'pathology'])&set(test.loc[test.target.eq(2),'pathology'])
            assert not set(fit.participant)&set(cal.participant)
            for role,g in [('fit',fit),('calibration',cal),('test',test)]:
                s=g[['participant','target','pathology']].copy();s['scope'],s['outer_fold'],s['role']=scope,int(fold),role;splits.append(s)
            pools={p:{t:g.index.to_numpy() for t,g in meta[meta.participant.eq(p)].groupby('trial')} for p in fit.participant}
            fit_values=magnitude[meta.participant.isin(fit.participant).to_numpy()]
            mean,std=float(fit_values.mean()),float(fit_values.std(unbiased=False))
            assert std>0
            for arm,kind,adapt in [('main_only','random',False),('random_fusion','random',True),('pretrained_fusion','pretrained',True)]:
                model=copy.deepcopy(originals[kind]).to(device).eval();model.requires_grad_(False)
                frozen_before=digest_state(torch.nn.Sequential(*list(model.feature_extractor.children())[:4]))
                late_before=digest_state(torch.nn.Sequential(model.feature_extractor.layer5,model.fc))
                if adapt:
                    model.feature_extractor.layer5.requires_grad_(True);model.fc.requires_grad_(True)
                torch.manual_seed(SEED)
                main=LowerBackDomainNet().to(device)
                main_before=digest_state(main.features)
                head=torch.nn.Linear(192 if adapt else 64,1).to(device)
                torch.nn.init.zeros_(head.weight);torch.nn.init.zeros_(head.bias)
                groups=[dict(params=list(head.parameters())+list(main.features.parameters()),lr=.001)]
                if adapt:groups.append(dict(params=[p for p in model.parameters() if p.requires_grad],lr=.0001))
                optim=torch.optim.AdamW(groups,weight_decay=.0001)
                rng=np.random.default_rng(SEED+int(fold));cache=caches[kind]
                targets={t:sorted(fit.loc[fit.target.eq(t),'participant']) for t in [0,1,2]}
                for epoch in range(6):
                    losses=[]
                    main.train()
                    for step in range(30):
                        ix=[];ys=[]
                        for t in rng.choice([0,1,2],32,p=[.25,.5,.25]):
                            person=rng.choice(targets[t]);trial=rng.choice(sorted(pools[person]))
                            ix.append(rng.choice(pools[person][trial]));ys.append(float(t==1))
                        logits=fusion_logits(model if adapt else None,head,main,cache,magnitude,ix,mean,std,device)
                        loss=torch.nn.functional.binary_cross_entropy_with_logits(logits,torch.tensor(ys,device=device))
                        assert torch.isfinite(loss)
                        optim.zero_grad();loss.backward()
                        torch.nn.utils.clip_grad_norm_([p for group in optim.param_groups for p in group['params']],1.)
                        optim.step();losses.append(float(loss.detach()))
                    lossrows.append(dict(scope=scope,fold=int(fold),arm=arm,epoch=epoch+1,loss=float(np.mean(losses))))
                frozen_after=digest_state(torch.nn.Sequential(*list(model.feature_extractor.children())[:4]))
                late_after=digest_state(torch.nn.Sequential(model.feature_extractor.layer5,model.fc))
                assert frozen_before==frozen_after and ((late_before!=late_after)==adapt)
                assert main_before!=digest_state(main.features)
                checks.append(dict(scope=scope,fold=int(fold),arm=arm,early_unchanged=True,late_changed=adapt,main_changed=True,mean=mean,std=std))
                c=aggregate(model if adapt else None,head,main,cache,magnitude,mean,std,meta,cal,device)
                scores=np.sort(c.loc[c.target.eq(1),'score'].to_numpy())[::-1]
                threshold=float(scores[int(np.ceil(.9*len(scores)))-1])
                for dest,g in [(calrows,c),(rows,aggregate(model if adapt else None,head,main,cache,magnitude,mean,std,meta,test,device))]:
                    g['positive']=g.score.ge(threshold);g['threshold']=threshold
                    g['scope'],g['arm'],g['outer_fold']=scope,arm,int(fold);dest.append(g)
                thresholds.append(dict(scope=scope,fold=int(fold),arm=arm,threshold=threshold,calibration_strokes=len(scores)))
                print(scope,int(fold),arm,'done',flush=True)
    pred=pd.concat(rows);metrics=[]
    for (scope,arm),g in pred.groupby(['scope','arm']):
        assert g.participant.is_unique
        d=dict(scope=scope,arm=arm,n=len(g),auroc=float(roc_auc_score(g.target.eq(1),g.score)))
        for t,name in [(0,'healthy'),(1,'stroke'),(2,'other')]:
            h=g[g.target.eq(t)];d[name+'_n']=len(h);d[name+'_positive']=int(h.positive.sum())
        h=g[g.pathology.isin(['CIPN','PD','RIL'])];d['neuro_n']=len(h);d['neuro_fp']=int(h.positive.sum());metrics.append(d)
    metrics=pd.DataFrame(metrics);gates=[]
    for scope,g in metrics.groupby('scope'):
        g=g.set_index('arm');b=g.loc['pretrained_fusion']
        for control in ['random_fusion','main_only']:
            a=g.loc[control];gates.append(dict(scope=scope,control=control,passed=bool((a.neuro_fp-b.neuro_fp)/a.neuro_n>=.05 and b.stroke_positive>=a.stroke_positive and b.healthy_positive<=a.healthy_positive)))
    for name,frame in [('predictions',pred),('calibration_predictions',pd.concat(calrows)),('splits',pd.concat(splits)),('losses',pd.DataFrame(lossrows)),('checks',pd.DataFrame(checks)),('thresholds',pd.DataFrame(thresholds)),('metrics',metrics)]:frame.to_csv(OUT/f'{name}.csv',index=False)
    pred.groupby(['scope','arm','pathology']).agg(n=('participant','size'),positive=('positive','sum')).to_csv(OUT/'pathology_counts.csv')
    pred.pivot(index=['scope','participant','target','pathology'],columns='arm',values='positive').to_csv(OUT/'paired_calls.csv')
    result=dict(passed=all(g['passed'] for g in gates),gates=gates,fits=18,device=device,independent_validation=False)
    (OUT/'decision.json').write_text(json.dumps(result,indent=2));print(metrics.to_string(index=False),flush=True)


if __name__=='__main__':main()
