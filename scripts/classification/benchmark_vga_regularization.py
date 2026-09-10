"""Isolated fixed-duration, weight-decay and warm-up contrasts."""
import benchmark_vga_screen as b
from benchmark_vga_screen import *
from keras.callbacks import LearningRateScheduler,ModelCheckpoint
from finalize_vga_screen import strict_threshold
OUT=ROOT/'data/processed/vga_regularization_v1'

def rate(epoch,warm=False):
    base=.00001+.5*(.001-.00001)*(1+np.cos(np.pi*epoch/39))
    return float(base*min(1,(epoch+1)/5) if warm else base)

def main():
    OUT.mkdir(parents=True,exist_ok=True);b.OUT=OUT;torch.set_num_threads(4)
    if (OUT/'decision.json').exists():raise FileExistsError('Completed')
    sources=[Path(__file__),ROOT/'scripts/classification/benchmark_vga_screen.py',ROOT/'scripts/classification/finalize_vga_screen.py',ROOT/'docs/classification/VGA_REGULARIZATION_PROTOCOL.md',OLD/'windows.npy',OLD/'splits.csv']
    (OUT/'manifest.json').write_text(json.dumps({str(p.relative_to(ROOT)):sha(p) for p in sources},indent=2))
    raw=np.load(OLD/'windows.npy');meta=pd.read_csv(OLD/'cycles.csv');people=pd.read_csv(OLD/'people.csv')
    frame,valid,_,_=canonical(raw[:,:,:6]);assert valid.all()
    keep,people=b.screening_labels(meta,people);frame=frame[keep];meta=meta.loc[keep].reset_index(drop=True)
    ext,emeta=b.external();eframe,valid,_,_=canonical(ext[:,:,:6]);assert valid.all()
    split=pd.read_csv(OLD/'splits.csv');preds=[];cals=[];externals=[];hist=[];selections=[];cp=OUT/'checkpoints';cp.mkdir(exist_ok=True)
    for fold in [0,1,2]:
        roles={role:people[people.participant.isin(g.participant)] for role,g in split[split.outer_fold.eq(fold)].groupby('role')}
        fit,val,cal,test=[roles[r] for r in ['fit','validation','calibration','test']]
        fi=np.flatnonzero(meta.participant.isin(fit.participant));vi=np.flatnonzero(meta.participant.isin(val.participant))
        y=utils.to_categorical(meta.participant.map(people.set_index('participant').target).astype(int),2)
        fw=b.weights(meta.iloc[fi],fit);vw=b.weights(meta.iloc[vi],val)
        scaler=StandardScaler().fit(frame[fi].reshape(-1,6));z=scaler.transform(frame.reshape(-1,6)).reshape(frame.shape).astype('float32')
        ez=scaler.transform(eframe.reshape(-1,6)).reshape(eframe.shape).astype('float32')
        np.savez(cp/f'fold{fold}_scaler.npz',mean=scaler.mean_,scale=scaler.scale_)
        for seed in [42,137,202]:
            for arm in ['fixed','decay','warmup']:
                run=f'{arm}_fold{fold}_seed{seed}';utils.set_random_seed(seed)
                with contextlib.redirect_stdout(io.StringIO()):model=upstream_builder()(dict(use_wandb=False,n_filters=32,n_layers=1,initial_lr=.001,evaluation_metric='AUC'),200,6)
                model.compile(loss='categorical_crossentropy',optimizer=Adam(learning_rate=.001,weight_decay=.01 if arm=='decay' else 0.),metrics=['AUC'])
                path=cp/f'{run}.weights.h5'
                h=model.fit(z[fi],y[fi],sample_weight=fw,validation_data=(z[vi],y[vi],vw),epochs=40,batch_size=32,verbose=0,callbacks=[LearningRateScheduler(lambda epoch,lr:rate(epoch,arm=='warmup')),ModelCheckpoint(str(path),monitor='val_loss',save_best_only=True,save_weights_only=True)])
                for epoch in range(40):hist.append(dict(run=run,epoch=epoch+1,scheduled_lr=rate(epoch,arm=='warmup'),**{k:float(v[epoch]) for k,v in h.history.items()}))
                best=int(np.argmin(h.history['val_loss']));model.load_weights(path)
                selections.append(dict(arm=arm,fold=fold,seed=seed,run=run,best_epoch=best+1,val_loss=float(h.history['val_loss'][best])))
                c=predict(model,z,meta,cal);threshold=float(strict_threshold(c.loc[c.target.eq(0),'score']))
                for dest,g in [(cals,c),(preds,predict(model,z,meta,test))]:
                    g['arm'],g['seed'],g['outer_fold'],g['threshold']=arm,seed,fold,threshold;g['positive']=g.score.ge(threshold);dest.append(g)
                e=emeta.copy();e['score']=model.predict(ez,batch_size=256,verbose=0)[:,1];e=e.groupby(['participant','condition'],as_index=False).score.mean()
                e['arm'],e['seed'],e['outer_fold'],e['threshold']=arm,seed,fold,threshold;e['positive']=e.score.ge(threshold);externals.append(e)
                pd.DataFrame(hist).to_csv(OUT/'histories.csv',index=False);pd.DataFrame(selections).to_csv(OUT/'selection.csv',index=False)
                print(run,'best epoch',best+1,'validation',h.history['val_loss'][best],flush=True)
    p=pd.concat(preds).merge(people[['participant','vga']],on='participant',validate='many_to_one');p.to_csv(OUT/'predictions.csv',index=False)
    pd.concat(cals).to_csv(OUT/'calibration.csv',index=False);e=pd.concat(externals);e.to_csv(OUT/'external_predictions.csv',index=False)
    metrics=[]
    for scope,g0 in [('full',p),('matched',p[p.matched])]:
        for (arm,seed),g in g0.groupby(['arm','seed']):
            d=dict(scope=scope,arm=arm,seed=int(seed),auroc=float(roc_auc_score(g.target,g.score)))
            for name,mask in [('normal',g.target.eq(0)),('impaired',g.target.eq(1)),('healthy_normal',g.target.eq(0)&g.pathology.eq('healthy'))]:d[name+'_n']=int(mask.sum());d[name+'_alerts']=int(g.positive[mask].sum())
            metrics.append(d)
    m=pd.DataFrame(metrics);m.to_csv(OUT/'metrics.csv',index=False)
    p.groupby(['arm','seed','vga']).agg(n=('participant','size'),alerts=('positive','sum')).to_csv(OUT/'severity.csv')
    e.groupby(['arm','seed','outer_fold','condition']).agg(n=('participant','size'),alerts=('positive','sum')).to_csv(OUT/'external_metrics.csv')
    passed=[]
    for arm,g in m[m.scope.eq('full')].groupby('arm'):
        if ((g.normal_alerts/g.normal_n<=.1)&(g.impaired_alerts/g.impaired_n>=.7)).all():passed.append(arm)
    (OUT/'decision.json').write_text(json.dumps(dict(fits=27,epochs_each=40,passed_arms=passed),indent=2));print(m[m.scope.eq('full')].to_string(index=False))

if __name__=='__main__':main()
