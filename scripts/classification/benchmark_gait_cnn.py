"""Train upstream Linn39 gait_cnn faithfully with explicit stroke-task repairs.

Upstream MIT Copyright (c) 2023 Lin Zhou, license retained in pinned repository.
"""
from pathlib import Path
import os,sys,json,ast,hashlib,contextlib,io
os.environ['KERAS_BACKEND']='torch'
os.environ['MPLBACKEND']='Agg'
import numpy as np
import pandas as pd
import torch
from scipy.signal import butter,filtfilt,resample
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler
from keras import models,layers,utils
from keras.optimizers import Adam
from keras.callbacks import EarlyStopping,ReduceLROnPlateau

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from src.data.voisard_aligned import align_packets
UP=ROOT/'models/research/gait_cnn-689cc9b'
OUT=ROOT/'data/processed/gait_cnn_v1'
ARMS={'lb_magnitude':[18],'lb6':list(range(6)),'feet12':list(range(6,18)),'all18':list(range(18))}


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def upstream_builder():
    path=UP/'src/models/train_model.py'
    tree=ast.parse(path.read_text())
    node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='get_CNN_model')
    namespace=dict(models=models,layers=layers,Adam=Adam)
    exec(compile(ast.Module(body=[node],type_ignores=[]),str(path),'exec'),namespace)
    return namespace['get_CNN_model']


def cycle_bounds(m):
    turn=m['uturnBoundaries'];cycles=[];bad=0
    events=m.get('leftGaitEvents') or []
    for a,b in zip(events,events[1:]):
        if len(a)!=2 or len(b)!=2 or not np.isfinite(a+b).all():bad+=1;continue
        if not a[0]<a[1]<b[0]<b[1]:bad+=1;continue
        if not (b[1]<turn[0] or a[1]>turn[1]):continue
        if b[1]-a[1]<16:bad+=1;continue
        cycles.append((int(a[1]),int(b[1])))
    return cycles,bad


def prepare():
    if (OUT/'windows.npy').exists():
        return np.load(OUT/'windows.npy'),pd.read_csv(OUT/'cycles.csv'),pd.read_csv(OUT/'people.csv')
    people=pd.read_csv(ROOT/'data/processed/directional_hr_v1/participants_main.csv')
    trials=pd.read_csv(ROOT/'data/processed/bilateral_phase_v1/trial_features.csv')
    paths={p.stem.removesuffix('_meta'):p for p in (ROOT/'data/raw/voisard_2025/data').glob('*/*/*/*/*_meta.json')}
    allx=[];rows=[];ledger=[];source=[]
    ba=butter(3,10,fs=100)
    for n,r in enumerate(trials.itertuples()):
        p=paths[r.trial];assert sha(p)==r.metadata_sha256
        m=json.loads(p.read_text());assert m['freq']==100
        cycles,bad=cycle_bounds(m);kept=0;invalid=0
        if cycles and r.reference_valid:
            sensorfiles={s:p.parent/f'{r.trial}_raw_data_{s}.txt' for s in ['HE','LB','LF','RF']}
            frames={s:pd.read_csv(f,sep='\t') for s,f in sensorfiles.items()}
            origin=int(round(min(f.PacketCounter.iloc[0] for f in frames.values())))
            signals=[]
            for s in ['LB','LF','RF']:
                f=frames[s];acc=align_packets(f,origin)/9.80665
                gyro=f[['PacketCounter','Gyr_X','Gyr_Y','Gyr_Z']].rename(columns={f'Gyr_{a}':f'Acc_{a}' for a in 'XYZ'})
                signals.append(np.concatenate([acc,align_packets(gyro,origin)],axis=1))
            length=min(map(len,signals));raw=np.concatenate([s[:length] for s in signals],axis=1)
            # Filter contiguous straight-walking regions only; never bridge a turn/gap.
            filtered=np.full((length,19),np.nan)
            for side in [0,1]:
                chosen=[(a,b) for a,b in cycles if (b<m['uturnBoundaries'][0])== (side==0)]
                if not chosen:continue
                lo=min(a for a,b in chosen);hi=min(length,max(b for a,b in chosen))
                finite=np.isfinite(raw[lo:hi]).all(axis=1)
                edges=np.diff(np.r_[False,finite,False].astype(int));starts=np.where(edges==1)[0]+lo;ends=np.where(edges==-1)[0]+lo
                for a,b in zip(starts,ends):
                    if b-a<=12:continue
                    filtered[a:b,:18]=filtfilt(*ba,raw[a:b],axis=0)
                    filtered[a:b,18]=filtfilt(*ba,np.linalg.norm(raw[a:b,:3],axis=1))
            for a,b in cycles:
                if b>length or not np.isfinite(filtered[a:b]).all():invalid+=1;continue
                allx.append(resample(filtered[a:b],200,axis=0).astype('float32'))
                rows.append(dict(participant=r.participant,trial=r.trial,start=a,end=b));kept+=1
            source.extend(dict(trial=r.trial,sensor=s,sha256=sha(f)) for s,f in sensorfiles.items())
        ledger.append(dict(participant=r.participant,trial=r.trial,cycles=kept,malformed=bad,invalid_signal=invalid,reference_valid=bool(r.reference_valid)))
        if n%250==0:print('Extracted',n,'trials',flush=True)
    meta=pd.DataFrame(rows);x=np.stack(allx);np.save(OUT/'windows.npy',x,allow_pickle=False)
    meta.to_csv(OUT/'cycles.csv',index=False);pd.DataFrame(ledger).to_csv(OUT/'trial_coverage.csv',index=False)
    pd.DataFrame(source).to_csv(OUT/'raw_hashes.csv',index=False)
    counts=meta.groupby('participant').size().rename('cycles')
    people=people.merge(counts,on='participant',how='left',validate='one_to_one');people['cycles']=people.cycles.fillna(0).astype(int)
    people.to_csv(OUT/'people.csv',index=False)
    people.assign(available=people.cycles.gt(0)).groupby('pathology').agg(n=('participant','size'),available=('available','sum')).to_csv(OUT/'coverage.csv')
    return x,meta,people


def splits(train,fold):
    rng=np.random.default_rng(20260909+int(fold));val=[];cal=[]
    for _,g in train.groupby('target'):
        ids=rng.permutation(sorted(g.participant));n=max(1,int(np.ceil(.2*len(ids))));assert len(ids)>2*n
        val.extend(ids[:n]);cal.extend(ids[n:2*n])
    return train[~train.participant.isin(val+cal)],train[train.participant.isin(val)],train[train.participant.isin(cal)]


def weights(meta,people):
    info=meta.merge(people[['participant','target']],on='participant',validate='many_to_one')
    npeople=people.groupby('target').size();ntrials=info.groupby('participant').trial.nunique();ncycles=info.groupby(['participant','trial']).size()
    w=np.array([{0:.25,1:.5,2:.25}[r.target]/npeople[r.target]/ntrials[r.participant]/ncycles[r.participant,r.trial] for r in info.itertuples()])
    return w/w.mean()


def predict(model,x,meta,people):
    ix=np.flatnonzero(meta.participant.isin(people.participant))
    pred=model.predict(x[ix],batch_size=256,verbose=0)[:,1]
    g=meta.iloc[ix][['participant','trial']].copy();g['score']=pred
    score=g.groupby(['participant','trial']).score.mean().groupby('participant').mean()
    return people[['participant','target','pathology','fold','matched']].merge(score,on='participant',validate='one_to_one')


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    torch.set_num_threads(4)
    if (OUT/'decision.json').exists():raise FileExistsError('Completed experiment')
    manifest={str(p.relative_to(ROOT)):sha(p) for p in [Path(__file__),ROOT/'docs/classification/GAIT_CNN_PROTOCOL.md',UP/'src/models/train_model.py',UP/'src/features/FeatureBuilder.py',ROOT/'src/data/voisard_aligned.py',ROOT/'data/processed/bilateral_phase_v1/trial_features.csv',ROOT/'data/processed/directional_hr_v1/participants_main.csv']}
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
    x,meta,people=prepare();people=people[people.cycles.gt(0)]
    print('Coverage',len(people),'people;',len(x),'cycles',flush=True)
    make=upstream_builder();outs=[];cals=[];splitrows=[];histories=[]
    for fold in sorted(people.fold.unique()):
        train,test=people[people.fold.ne(fold)],people[people.fold.eq(fold)]
        fit,val,cal=splits(train,fold)
        assert not set(train.participant)&set(test.participant)
        assert not set(train.loc[train.target.eq(2),'pathology'])&set(test.loc[test.target.eq(2),'pathology'])
        for role,g in [('fit',fit),('validation',val),('calibration',cal),('test',test)]:
            q=g[['participant','target','pathology']].copy();q['role'],q['outer_fold']=role,int(fold);splitrows.append(q)
        fi=np.flatnonzero(meta.participant.isin(fit.participant));vi=np.flatnonzero(meta.participant.isin(val.participant))
        targets=people.set_index('participant').target
        y=utils.to_categorical(meta.participant.map(targets).eq(1).astype(int),2)
        fw=weights(meta.iloc[fi],fit);vw=weights(meta.iloc[vi],val)
        for arm,channels in ARMS.items():
            scaler=StandardScaler().fit(x[fi][:,:,channels].reshape(-1,len(channels)))
            z=scaler.transform(x[:,:,channels].reshape(-1,len(channels))).reshape(len(x),200,len(channels)).astype('float32')
            for seed in [42,137,202]:
                run=f'{arm}_fold{fold}_seed{seed}';cp=OUT/'checkpoints';cp.mkdir(exist_ok=True)
                utils.set_random_seed(seed)
                with contextlib.redirect_stdout(io.StringIO()):
                    model=make(dict(use_wandb=False,n_filters=32,n_layers=1,initial_lr=.02,evaluation_metric='AUC'),200,len(channels))
                callbacks=[EarlyStopping(monitor='val_loss',patience=3,restore_best_weights=True),ReduceLROnPlateau(monitor='val_loss',factor=.5,patience=2,min_lr=.001)]
                history=model.fit(z[fi],y[fi],sample_weight=fw,validation_data=(z[vi],y[vi],vw),epochs=25,batch_size=32,callbacks=callbacks,verbose=0)
                model.save_weights(cp/f'{run}.weights.h5')
                np.savez(cp/f'{run}.normalization.npz',mean=scaler.mean_,scale=scaler.scale_,channels=channels)
                for epoch in range(len(history.history['loss'])):
                    histories.append(dict(run=run,epoch=epoch+1,**{k:float(v[epoch]) for k,v in history.history.items()}))
                c=predict(model,z,meta,cal);scores=np.sort(c.loc[c.target.eq(1),'score'])[::-1];threshold=float(scores[int(np.ceil(.9*len(scores)))-1])
                for dest,g in [(cals,c),(outs,predict(model,z,meta,test))]:
                    g['arm'],g['seed'],g['outer_fold'],g['threshold']=arm,seed,int(fold),threshold
                    g['positive']=g.score.ge(threshold);dest.append(g)
                print(run,'epochs',len(history.history['loss']),'done',flush=True)
                pd.DataFrame(histories).to_csv(OUT/'histories.csv',index=False)
                pd.concat(outs).to_csv(OUT/'predictions.csv',index=False)
    pred=pd.concat(outs);pd.concat(cals).to_csv(OUT/'calibration_predictions.csv',index=False);pd.concat(splitrows).to_csv(OUT/'splits.csv',index=False)
    metrics=[]
    for scope,data in [('all_available',pred),('matched_subset',pred[pred.matched])]:
        for (arm,seed),g in data.groupby(['arm','seed']):
            assert g.participant.is_unique
            for rule,pos in [('calibrated',g.positive),('fixed_0.5',g.score.ge(.5))]:
                d=dict(scope=scope,arm=arm,seed=int(seed),rule=rule,n=len(g),auroc=float(roc_auc_score(g.target.eq(1),g.score)))
                for t,name in [(0,'healthy'),(1,'stroke'),(2,'other')]:
                    mask=g.target.eq(t);d[name+'_n']=int(mask.sum());d[name+'_positive']=int(pos[mask].sum())
                mask=g.pathology.isin(['CIPN','PD','RIL']);d['neuro_n']=int(mask.sum());d['neuro_fp']=int(pos[mask].sum());metrics.append(d)
    metrics=pd.DataFrame(metrics);metrics.to_csv(OUT/'metrics.csv',index=False)
    pred.groupby(['arm','seed','pathology']).agg(n=('participant','size'),positive=('positive','sum')).to_csv(OUT/'pathology_counts.csv')
    gates=[]
    for (scope,seed),g in metrics[metrics.rule.eq('calibrated')].groupby(['scope','seed']):
        g=g.set_index('arm');a=g.loc['lb_magnitude']
        for arm in ['lb6','feet12','all18']:
            b=g.loc[arm];gates.append(dict(scope=scope,seed=int(seed),arm=arm,passed=bool((a.neuro_fp-b.neuro_fp)/a.neuro_n>=.05 and b.stroke_positive>=a.stroke_positive and b.healthy_positive<=a.healthy_positive)))
    result=dict(gates=gates,promising_arms=[arm for arm in ['lb6','feet12','all18'] if all(g['passed'] for g in gates if g['arm']==arm)],fits=36,people=len(people),cycles=len(x),independent_validation=False)
    (OUT/'decision.json').write_text(json.dumps(result,indent=2))
    print(metrics[metrics.rule.eq('calibrated')].to_string(index=False),flush=True)


if __name__=='__main__':main()
