"""Validation-selected upstream CNN on a rotation-equivariant waveform frame."""
from benchmark_gait_cnn import *
from scipy.signal import butter,filtfilt,resample
OLD=OUT
OUT=ROOT/'data/processed/vga_screen_v1'

def canonical(x):
    a=x[:,:,:3].astype('float64');g=x[:,:,3:6].astype('float64')
    mean=a.mean(axis=1);strength=np.linalg.norm(mean,axis=1);v=mean/np.maximum(strength[:,None],1e-12)
    h=a-np.einsum('btc,bc->bt',a,v)[:,:,None]*v[:,None,:]
    covariance=np.einsum('btc,btd->bcd',h,h)
    eig,vec=np.linalg.eigh(covariance);u=vec[:,:,-1]
    proj=np.einsum('btc,bc->bt',h,u);peak=np.argmax(np.abs(proj),axis=1)
    u*=np.where(proj[np.arange(len(x)),peak]<0,-1,1)[:,None]
    w=np.cross(v,u);basis=np.stack([v,u,w],axis=2)
    gap=(eig[:,-1]-eig[:,-2])/np.maximum(eig[:,-1],1e-12)
    valid=(strength>1e-6)&(eig[:,-1]>1e-12)&(gap>1e-8)
    z=np.concatenate([np.einsum('btc,bcd->btd',a,basis),np.einsum('btc,bcd->btd',g,basis)],axis=2).astype('float32')
    return z,valid,gap,strength

def external():
    ledger=pd.read_csv(ROOT/'data/processed/gait_cnn_duogait_v2/cycles.csv');allx=[];rows=[];hashes={}
    base=ROOT/'data/archive/raw/duogait_2023/data/repository_interim';ba=butter(3,10,fs=128)
    for (person,condition),tab in ledger.groupby(['participant','condition'],sort=False):
        p=base/condition/person/'SA.csv';hashes[str(p.relative_to(ROOT))]=sha(p);f=pd.read_csv(p)
        a=f[['AccX','AccY','AccZ']].to_numpy();g=np.deg2rad(f[['GyrX','GyrY','GyrZ']].to_numpy())
        raw=np.c_[a,g,np.linalg.norm(a,axis=1)];filtered=np.full_like(raw,np.nan);mask=np.zeros(len(f),bool)
        for r in tab.itertuples():mask[r.start:r.end]=True
        mask &= np.isfinite(raw).all(axis=1)
        edges=np.diff(np.r_[False,mask,False].astype(int))
        for start,end in zip(np.where(edges==1)[0],np.where(edges==-1)[0]):
            if end-start>12:filtered[start:end]=filtfilt(*ba,raw[start:end],axis=0)
        for r in tab.itertuples():
            if not np.isfinite(filtered[r.start:r.end]).all():continue
            allx.append(resample(filtered[r.start:r.end],200,axis=0).astype('float32'));rows.append(dict(participant=person,condition=condition))
    (OUT/'external_hashes.json').write_text(json.dumps(hashes,indent=2))
    return np.stack(allx),pd.DataFrame(rows)

def screening_labels(meta,people):
    paths={p.stem.removesuffix('_meta'):p for p in (ROOT/'data/raw/voisard_2025/data').glob('*/*/*/*/*_meta.json')}
    rows=[];hashes={}
    for trial in meta.trial.unique():
        p=paths[trial];m=json.loads(p.read_text());hashes[str(p.relative_to(ROOT))]=sha(p)
        rows.append(dict(trial=trial,participant='voisard_2025:'+m['subject'],session=m['session'],vga=pd.to_numeric(m.get('visualGaitAssessment'),errors='coerce')))
    labels=pd.DataFrame(rows);labels=labels[labels.session.eq(labels.groupby('participant').session.transform('min'))]
    ledger=labels.groupby('participant').agg(n=('vga','size'),known=('vga','count'),lo=('vga','min'),hi=('vga','max')).reset_index()
    ledger['eligible']=ledger.known.eq(ledger.n)&ledger.lo.between(0,4)&ledger.hi.between(0,4)&((ledger.lo.gt(0)==ledger.hi.gt(0)))
    ledger.to_csv(OUT/'label_coverage.csv',index=False);labels.to_csv(OUT/'first_session_labels.csv',index=False)
    (OUT/'metadata_hashes.json').write_text(json.dumps(hashes,indent=2))
    eligible=ledger[ledger.eligible].set_index('participant');people=people[people.participant.isin(eligible.index)].copy()
    people['target']=people.participant.map(eligible.lo).gt(0).astype(int);people['vga']=people.participant.map(eligible.lo)
    people.to_csv(OUT/'people.csv',index=False)
    keep=meta.trial.isin(labels[labels.participant.isin(people.participant)].trial)
    return keep.to_numpy(),people

def weights(meta,people):
    info=meta.merge(people[['participant','target']],on='participant',validate='many_to_one')
    npeople=people.groupby('target').size();ntrials=info.groupby('participant').trial.nunique();ncycles=info.groupby(['participant','trial']).size()
    w=np.array([.5/npeople[r.target]/ntrials[r.participant]/ncycles[r.participant,r.trial] for r in info.itertuples()])
    return w/w.mean()

def main():
    OUT.mkdir(exist_ok=True,parents=True);torch.set_num_threads(4)
    if (OUT/'decision.json').exists():raise FileExistsError('Complete')
    manifest={str(p.relative_to(ROOT)):sha(p) for p in [Path(__file__),ROOT/'docs/classification/VGA_SCREEN_PROTOCOL.md',OLD/'windows.npy',OLD/'splits.csv',ROOT/'data/processed/gait_cnn_duogait_v2/cycles.csv']}
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
    raw=np.load(OLD/'windows.npy');meta=pd.read_csv(OLD/'cycles.csv');people=pd.read_csv(OLD/'people.csv')
    frame,valid,gap,strength=canonical(raw[:,:,:6]);assert valid.all(),'Unidentifiable frames require explicit coverage decision'
    quality=meta.copy();quality['gap']=gap;quality['gravity_g']=strength;quality.to_csv(OUT/'frame_quality.csv',index=False)
    ext,emeta=external();eframe,ev,eg,es=canonical(ext[:,:,:6]);assert ev.all()
    eq=emeta.copy();eq['gap']=eg;eq['gravity_g']=es;eq.to_csv(OUT/'external_quality.csv',index=False)
    keep,people=screening_labels(meta,people);meta=meta.loc[keep].reset_index(drop=True);frame=frame[keep]
    datasets={'vga_frame6':(frame,eframe)}
    split=pd.read_csv(OLD/'splits.csv');recipes=[('upstream',.02,25,3,2,.001),('conservative',.001,40,8,3,.00001)]
    selected=[];preds=[];cals=[];extpred=[];histories=[];cp=OUT/'checkpoints';cp.mkdir(exist_ok=True)
    for fold in [0,1,2]:
        roles={role:people[people.participant.isin(g.participant)] for role,g in split[split.outer_fold.eq(fold)].groupby('role')}
        fit,val,cal,test=[roles[r] for r in ['fit','validation','calibration','test']]
        fi=np.flatnonzero(meta.participant.isin(fit.participant));vi=np.flatnonzero(meta.participant.isin(val.participant))
        y=utils.to_categorical(meta.participant.map(people.set_index('participant').target).eq(1).astype(int),2)
        fw=weights(meta.iloc[fi],fit);vw=weights(meta.iloc[vi],val)
        for arm,(x,ex) in datasets.items():
            channels=x.shape[-1];scaler=StandardScaler().fit(x[fi].reshape(-1,channels))
            z=scaler.transform(x.reshape(-1,channels)).reshape(x.shape).astype('float32');ez=scaler.transform(ex.reshape(-1,channels)).reshape(ex.shape).astype('float32')
            np.savez(cp/f'{arm}_fold{fold}_scaler.npz',mean=scaler.mean_,scale=scaler.scale_)
            for seed in [42,137,202]:
                best=None
                for recipe,lr,epochs,patience,lrpat,floor in recipes:
                    utils.set_random_seed(seed);run=f'{arm}_fold{fold}_seed{seed}_{recipe}'
                    with contextlib.redirect_stdout(io.StringIO()):model=upstream_builder()(dict(use_wandb=False,n_filters=32,n_layers=1,initial_lr=lr,evaluation_metric='AUC'),200,channels)
                    h=model.fit(z[fi],y[fi],sample_weight=fw,validation_data=(z[vi],y[vi],vw),epochs=epochs,batch_size=32,verbose=0,callbacks=[EarlyStopping(monitor='val_loss',patience=patience,restore_best_weights=True),ReduceLROnPlateau(monitor='val_loss',factor=.5,patience=lrpat,min_lr=floor)])
                    model.save_weights(cp/f'{run}.weights.h5');loss=float(min(h.history['val_loss']))
                    for epoch in range(len(h.history['loss'])):histories.append(dict(run=run,epoch=epoch+1,**{k:float(v[epoch]) for k,v in h.history.items()}))
                    if best is None or loss<best[0]:best=(loss,recipe,run)
                    pd.DataFrame(histories).to_csv(OUT/'histories.csv',index=False);print(run,len(h.history['loss']),loss,flush=True)
                loss,recipe,run=best;model.load_weights(cp/f'{run}.weights.h5')
                selected.append(dict(arm=arm,fold=fold,seed=seed,recipe=recipe,val_loss=loss,run=run))
                c=predict(model,z,meta,cal);s=np.sort(c.loc[c.target.eq(0),'score']);assert len(s)>=5
                threshold=float(np.nextafter(np.float64(s[int(np.ceil(.9*len(s)))-1]),np.inf))
                for dest,q in [(cals,c),(preds,predict(model,z,meta,test))]:
                    q['arm'],q['seed'],q['outer_fold'],q['threshold']=arm,seed,fold,threshold;q['positive']=q.score.ge(threshold);dest.append(q)
                q=emeta.copy();q['score']=model.predict(ez,batch_size=256,verbose=0)[:,1];q=q.groupby(['participant','condition'],as_index=False).score.mean()
                q['arm'],q['seed'],q['outer_fold'],q['threshold']=arm,seed,fold,threshold;q['positive']=q.score.ge(threshold);extpred.append(q)
                pd.DataFrame(selected).to_csv(OUT/'selection.csv',index=False);pd.concat(preds).to_csv(OUT/'predictions.csv',index=False)
    pred=pd.concat(preds);pd.concat(cals).to_csv(OUT/'calibration.csv',index=False);pd.concat(extpred).to_csv(OUT/'external_predictions.csv',index=False)
    pred=pred.merge(people[['participant','vga']],on='participant',validate='many_to_one');pred.to_csv(OUT/'predictions.csv',index=False)
    pd.concat([g.assign(role=role,outer_fold=fold) for fold in [0,1,2] for role,g in split[split.outer_fold.eq(fold)&split.participant.isin(people.participant)].groupby('role')]).to_csv(OUT/'eligible_splits.csv',index=False)
    metrics=[]
    for scope,g0 in [('full',pred),('matched',pred[pred.matched])]:
        for seed,g in g0.groupby('seed'):
            d=dict(scope=scope,seed=int(seed),auroc=float(roc_auc_score(g.target,g.score)))
            for name,mask in [('normal',g.target.eq(0)),('impaired',g.target.eq(1)),('healthy_group',g.pathology.eq('healthy')),('diagnosed_normal',g.target.eq(0)&g.pathology.ne('healthy'))]:
                d[name+'_n']=int(mask.sum());d[name+'_alerts']=int(g.positive[mask].sum())
            metrics.append(d)
    m=pd.DataFrame(metrics);m.to_csv(OUT/'metrics.csv',index=False)
    pred.groupby(['seed','vga']).agg(n=('participant','size'),alerts=('positive','sum')).to_csv(OUT/'severity.csv')
    pd.concat(extpred).groupby(['seed','outer_fold','condition']).agg(n=('participant','size'),alerts=('positive','sum')).to_csv(OUT/'external_metrics.csv')
    g=m[m.scope.eq('full')];passed=bool(((g.normal_alerts/g.normal_n<=.1)&(g.impaired_alerts/g.impaired_n>=.7)).all())
    (OUT/'decision.json').write_text(json.dumps(dict(fits=18,passed=passed,new_target='clinician VGA>0',clinical_validation=False),indent=2));print(m.to_string(index=False))

if __name__=='__main__':main()
