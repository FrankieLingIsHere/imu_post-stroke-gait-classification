"""Matched lower-back objective experiment; never replaces frozen v0.2.0.

Three arms: healthy/stroke binary, binary with other-pathology exposure, and
explicit healthy/stroke/other-pathology classes. Same-site development evidence.
"""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,sys
import numpy as np
import pandas as pd
import torch
from sklearn.model_selection import StratifiedKFold

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from models.lower_back_ensemble import LowerBackDomainNet
from scripts.benchmark_binary_hard_negative_exposure_loco import load_hard_negatives

OUT=ROOT/'data/processed/differential_gait_v1'
ARMS=('binary_primary','binary_exposure','three_class')
SEEDS=(42,137,202)


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def make_model(arm,seed):
    torch.manual_seed(seed)
    model=LowerBackDomainNet()
    if arm=='three_class':model.classifier[2]=torch.nn.Linear(64,3)
    elif arm not in ARMS:raise ValueError(arm)
    return model


def stroke_scores(logits,arm):
    return logits.softmax(1)[:,1] if arm=='three_class' else logits.sigmoid()


def make_folds(meta):
    people=meta[['participant','target','pathology']].drop_duplicates()
    if people.participant.duplicated().any():raise ValueError('Conflicting participant labels')
    primary=people[people.target<2].reset_index(drop=True)
    assignment={}
    for fold,(_,test) in enumerate(StratifiedKFold(3,shuffle=True,random_state=20260909).split(primary,primary.target)):
        assignment.update({p:fold for p in primary.iloc[test].participant})
    for fold,pathologies in enumerate(np.array_split(sorted(people[people.target==2].pathology.unique()),3)):
        assignment.update({p:fold for p in people[people.pathology.isin(pathologies)].participant})
    result=people.copy();result['fold']=result.participant.map(assignment)
    if result.fold.isna().any():raise ValueError('Unassigned person')
    return result


def participant_batch(meta,train,rng):
    """Equal target counts, uniform people within target, then a random window."""
    indices=[]
    for target in (0,1,2):
        frame=meta.loc[train & meta.target.eq(target)]
        pools={p:g.index.to_numpy() for p,g in frame.groupby('participant')}
        if not pools:raise ValueError('Empty training class')
        for person in rng.choice(sorted(pools),32,replace=True):indices.append(rng.choice(pools[person]))
    return np.asarray(indices)


def metrics(frame):
    out={}
    for target,name in ((0,'healthy_specificity'),(1,'stroke_sensitivity'),(2,'other_fpr')):
        g=frame[frame.target==target];pos=g.score.ge(.5)
        out[name]=float((~pos).mean() if target==0 else pos.mean())
    return out


def main():
    OUT.mkdir(exist_ok=True)
    if (OUT/'decision.json').exists():raise FileExistsError('Experiment complete; inspect saved results')
    if not torch.cuda.is_available():raise RuntimeError('Expected existing CUDA environment')
    torch.set_num_threads(4);torch.backends.cudnn.benchmark=False
    torch.backends.cudnn.allow_tf32=False;torch.backends.cuda.matmul.allow_tf32=False
    p=ROOT/'data/processed'
    x=np.load(p/'validated_acceleration_magnitude_windows_float32.npy')
    meta=pd.read_csv(p/'validated_window_metadata.csv')
    keep=meta.dataset_id.eq('voisard_2025')&meta.label.isin(['healthy','stroke'])
    x=x[keep.to_numpy(),:,:1];primary=meta.loc[keep].reset_index(drop=True)
    primary=pd.DataFrame(dict(participant=primary.participant_key,target=primary.label.eq('stroke').astype(int),
                              pathology=primary.label,trial=primary.trial_id))
    hard_path=OUT/'other_windows.npy';hard_meta=OUT/'other_metadata.csv'
    if hard_path.exists() and hard_meta.exists():hx=np.load(hard_path);hm=pd.read_csv(hard_meta)
    else:
        hx,hm=load_hard_negatives();hx=hx[:,:,:1]
        np.save(hard_path,hx,allow_pickle=False);hm.to_csv(hard_meta,index=False)
    other=pd.DataFrame(dict(participant=hm.participant_key,target=2,pathology=hm.cohort,trial=hm.trial_id))
    if set(primary.participant)&set(other.participant):raise ValueError('Primary/other overlap')
    x=np.concatenate([x,hx]).astype('float32');meta=pd.concat([primary,other],ignore_index=True)
    if x.shape[1:]!=(500,1) or not np.isfinite(x).all():raise ValueError('Invalid input')
    folds=make_folds(meta);meta['fold']=meta.participant.map(folds.set_index('participant').fold)
    lock=dict(created_utc=datetime.now(timezone.utc).isoformat(),scope='single-protocol Voisard objective feasibility; not independent-site validation or v0.2.0 replacement',
              classes={'healthy':0,'stroke':1,'other_pathology':2},arms=ARMS,seeds=SEEDS,epochs=8,steps_per_epoch=40,
              optimizer='AdamW lr=0.001 weight_decay=0.0001',sampler='32 uniform participants per target then uniform window; primary arm omits target2 after identical sampling',
              normalization='primary training windows only, shared across arms; no held-out statistics',
              splits='3 participant-disjoint folds; two entire nonstroke pathology groups withheld per fold; fixed across seeds and arms',
              aggregation='mean stroke score across windows per participant; fixed 0.50',
              gate='every seed: three-class vs primary sensitivity and specificity drops <=0.02, other FPR reduction >=0.10; vs binary exposure sensitivity/specificity drops <=0.02 and other FPR reduction >=0.05',
              exclusion='TVS, RevalExo, Felius and Sint not loaded',
              hashes={str(path.relative_to(ROOT)):digest(path) for path in [Path(__file__),ROOT/'models/lower_back_ensemble.py',
                      ROOT/'models/stroke_gait_inception.py',ROOT/'scripts/benchmark_binary_hard_negative_exposure_loco.py',
                      p/'validated_acceleration_magnitude_windows_float32.npy',p/'validated_window_metadata.csv',hard_path,hard_meta]},
              input_tensor_sha256=hashlib.sha256(x.tobytes()).hexdigest(),participants=len(folds),windows=len(x))
    protocol=OUT/'protocol.json'
    if protocol.exists():
        saved=json.loads(protocol.read_text());lock['created_utc']=saved['created_utc']
        if json.loads(json.dumps(lock))!=saved:raise ValueError('Protocol changed; no adaptive resume')
    else:
        with protocol.open('x') as f:json.dump(lock,f,indent=2)
        (OUT/'protocol.sha256').write_text(digest(protocol))
        folds.to_csv(OUT/'participant_folds.csv',index=False)
    if digest(protocol)!=(OUT/'protocol.sha256').read_text():raise ValueError('Protocol hash changed')
    print('LOCKED',len(folds),'people',len(x),'windows',folds.groupby(['target','fold']).size().to_dict(),flush=True)
    results=[]
    for seed in SEEDS:
        for fold in range(3):
            train=meta.fold.ne(fold);test=~train
            assert not set(meta.loc[train,'participant'])&set(meta.loc[test,'participant'])
            assert not set(meta.loc[train & meta.target.eq(2),'pathology'])&set(meta.loc[test & meta.target.eq(2),'pathology'])
            norm=x[(train & meta.target.lt(2)).to_numpy()];mu=float(norm.mean());sd=max(float(norm.std()),1e-4)
            values=torch.from_numpy(np.ascontiguousarray(((x-mu)/sd).transpose(0,2,1))).cuda()
            targets=torch.from_numpy(meta.target.to_numpy()).long().cuda()
            test_idx=np.flatnonzero(test);labels=meta.loc[test,['participant','target','pathology']].reset_index(drop=True)
            for arm in ARMS:
                dest=OUT/f'{arm}_seed{seed}_fold{fold}.csv'
                if dest.exists():
                    if not dest.with_suffix('.pt').exists():raise ValueError('Incomplete saved fit')
                    results.append(pd.read_csv(dest));continue
                model=make_model(arm,seed+fold*1000).cuda()
                optimizer=torch.optim.AdamW(model.parameters(),lr=.001,weight_decay=.0001)
                rng=np.random.default_rng(seed+fold*1000+77);torch.manual_seed(seed+fold*1000+99)
                batches=[participant_batch(meta,train,rng) for _ in range(8*40)]
                for index in batches:
                    if arm=='binary_primary':index=index[meta.target.iloc[index].to_numpy()<2]
                    model.train();optimizer.zero_grad(set_to_none=True);logits=model(values[index])
                    loss=torch.nn.functional.cross_entropy(logits,targets[index]) if arm=='three_class' else torch.nn.functional.binary_cross_entropy_with_logits(logits,targets[index].eq(1).float())
                    loss.backward();optimizer.step()
                model.eval();scores=[]
                with torch.inference_mode():
                    for start in range(0,len(test_idx),256):scores.extend(stroke_scores(model(values[test_idx[start:start+256]]),arm).cpu().numpy().tolist())
                frame=labels.copy();frame['score']=scores
                person=frame.groupby(['participant','target','pathology'],as_index=False).score.mean()
                person['arm']=arm;person['seed']=seed;person['fold']=fold
                torch.save(dict(model_state_dict={k:v.cpu() for k,v in model.state_dict().items()},arm=arm,mean=mu,std=sd,
                                seed=seed,fold=fold,protocol_sha256=digest(protocol),classes=lock['classes']),dest.with_suffix('.pt'))
                person.to_csv(dest,index=False);results.append(person)
                print(seed,fold,arm,metrics(person),flush=True)
                del model,optimizer
            del values,targets
    predictions=pd.concat(results,ignore_index=True);predictions.to_csv(OUT/'participant_predictions.csv',index=False)
    rows=[]
    for (seed,arm),frame in predictions.groupby(['seed','arm']):
        if frame.participant.duplicated().any() or len(frame)!=len(folds):raise ValueError('OOF accounting failed')
        rows.append(dict(seed=int(seed),arm=arm,**metrics(frame)))
    table=pd.DataFrame(rows);table.to_csv(OUT/'metrics.csv',index=False)
    gates=[]
    for seed in SEEDS:
        t=table[table.seed==seed].set_index('arm');candidate=t.loc['three_class'];passed=True;checks={}
        for control,reduction in [('binary_primary',.10),('binary_exposure',.05)]:
            b=t.loc[control];ok=bool(candidate.stroke_sensitivity>=b.stroke_sensitivity-.02-1e-12 and candidate.healthy_specificity>=b.healthy_specificity-.02-1e-12 and candidate.other_fpr<=b.other_fpr-reduction+1e-12)
            checks[control]=ok;passed &=ok
        gates.append(dict(seed=seed,passed=bool(passed),checks=checks))
    decision=dict(passed=all(g['passed'] for g in gates),gates=gates,
                  outcome='eligible for further validation only' if all(g['passed'] for g in gates) else 'reject candidate promotion',
                  frozen_model_changed=False,protocol_sha256=digest(protocol))
    with (OUT/'decision.json').open('x') as f:json.dump(decision,f,indent=2)
    print(table.to_string(index=False),flush=True);print(json.dumps(decision),flush=True)


if __name__=='__main__':main()
