"""Validate fixed-duration experiment and describe late validation recovery."""
from benchmark_vga_regularization import *
import importlib.metadata
import platform

def simulated_stop(values,patience=8):
    best=float('inf');wait=0
    for epoch,value in enumerate(values,1):
        if value<best:best=value;wait=0
        else:wait+=1
        if wait>=patience:return epoch
    return len(values)

def main():
    h=pd.read_csv(OUT/'histories.csv');s=pd.read_csv(OUT/'selection.csv');p=pd.read_csv(OUT/'predictions.csv')
    c=pd.read_csv(OUT/'calibration.csv',dtype={'score':'float32'});e=pd.read_csv(OUT/'external_predictions.csv')
    people=pd.read_csv(OUT/'people.csv');split=pd.read_csv(OLD/'splits.csv')
    baseline_people=pd.read_csv(ROOT/'data/processed/vga_screen_v1/people.csv')
    pd.testing.assert_frame_equal(people.sort_values('participant').reset_index(drop=True),baseline_people.sort_values('participant').reset_index(drop=True))
    assert len(s)==27 and h.run.nunique()==27 and h.groupby('run').size().eq(40).all()
    assert np.isfinite(h[['loss','val_loss']]).all().all()
    assert len(people)==248 and len(p)==248*9 and not p.duplicated(['arm','seed','participant']).any()
    assert len(e)==16*4*27 and not e.duplicated(['arm','seed','outer_fold','participant','condition']).any()
    # Independently reconstruct exported decisions and metrics from prediction rows.
    for table in [p,c,e]:
        assert np.isfinite(table[['score','threshold']]).all().all()
        assert table.score.between(0,1).all()
        assert (table.score.astype('float32').ge(table.threshold.astype('float32'))==table.positive).all()
    for fold in [0,1,2]:
        roles={role:set(g.participant)&set(people.participant) for role,g in split[split.outer_fold.eq(fold)].groupby('role')}
        assert set(roles)=={'fit','validation','calibration','test'}
        for role,ids in roles.items():
            assert all(not ids&other for name,other in roles.items() if name!=role)
    metrics=pd.read_csv(OUT/'metrics.csv')
    assert len(metrics)==18
    for r in metrics.itertuples():
        g=p[p.arm.eq(r.arm)&p.seed.eq(r.seed)]
        if r.scope=='matched':g=g[g.matched]
        assert np.isclose(roc_auc_score(g.target,g.score),r.auroc)
        for name,mask in [('normal',g.target.eq(0)),('impaired',g.target.eq(1)),('healthy_normal',g.target.eq(0)&g.pathology.eq('healthy'))]:
            assert int(mask.sum())==getattr(r,name+'_n')
            assert int(g.loc[mask,'positive'].sum())==getattr(r,name+'_alerts')
    passed=[]
    for arm,g in metrics[metrics.scope.eq('full')].groupby('arm'):
        if ((g.normal_alerts/g.normal_n<=.1)&(g.impaired_alerts/g.impaired_n>=.7)).all():passed.append(arm)
    assert json.loads((OUT/'decision.json').read_text())==dict(fits=27,epochs_each=40,passed_arms=passed)
    dynamics=[]
    for r in s.itertuples():
        g=h[h.run==r.run].sort_values('epoch');best=g.loc[g.val_loss.idxmin()]
        assert best.epoch==r.best_epoch and np.isclose(best.val_loss,r.val_loss)
        assert (OUT/'checkpoints'/f'{r.run}.weights.h5').exists()
        np.testing.assert_allclose(g.scheduled_lr,[rate(i,r.arm=='warmup') for i in range(40)],atol=1e-12)
        cc=c[(c.arm==r.arm)&c.seed.eq(r.seed)&c.outer_fold.eq(r.fold)]
        assert set(cc.participant)==set(split[split.outer_fold.eq(r.fold)&split.role.eq('calibration')].participant)&set(people.participant)
        n=cc[cc.target.eq(0)];threshold=float(strict_threshold(n.score));assert np.allclose(cc.threshold,threshold)
        assert n.positive.sum()<=np.floor(.1*len(n)+1e-8)
        test=p[(p.arm==r.arm)&p.seed.eq(r.seed)&p.outer_fold.eq(r.fold)]
        assert set(test.participant)==set(split[split.outer_fold.eq(r.fold)&split.role.eq('test')].participant)&set(people.participant)
        assert not set(cc.participant)&set(test.participant)
        assert np.allclose(test.threshold,threshold)
        stop=simulated_stop(g.val_loss)
        dynamics.append(dict(run=r.run,arm=r.arm,fold=r.fold,seed=r.seed,best_epoch=r.best_epoch,simulated_patience8_stop=stop,best_after_stop=bool(r.best_epoch>stop),minimum_before_stop=float(g.iloc[:stop].val_loss.min()),minimum_full=r.val_loss,final_train=float(g.iloc[-1].loss),final_val=float(g.iloc[-1].val_loss),last5_train_delta=float(g.iloc[-1].loss-g.iloc[-5].loss),last5_val_delta=float(g.iloc[-1].val_loss-g.iloc[-5].val_loss)))
    for f in ['manifest.json','metadata_hashes.json','external_hashes.json']:
        for path,digest in json.loads((OUT/f).read_text()).items():assert sha(ROOT/path)==digest,path
    pd.DataFrame(dynamics).to_csv(OUT/'training_dynamics.csv',index=False)
    paired=s.pivot(index=['fold','seed'],columns='arm',values='val_loss')
    for arm in ['decay','warmup']:paired[arm+'_minus_fixed']=paired[arm]-paired.fixed
    paired.to_csv(OUT/'paired_validation.csv')
    # Same participant held out under both arms: enumerate both gains and losses.
    changes=[]
    for seed,g in p.groupby('seed'):
        control=g[g.arm.eq('fixed')].set_index('participant')
        for arm in ['decay','warmup']:
            candidate=g[g.arm.eq(arm)].set_index('participant').loc[control.index]
            assert candidate.target.equals(control.target)
            for label,target in [('normal',0),('impaired',1)]:
                ids=control.index[control.target.eq(target)]
                before=control.loc[ids,'positive'];after=candidate.loc[ids,'positive']
                changes.append(dict(seed=int(seed),arm=arm,label=label,n=len(ids),positive_to_negative=int((before&~after).sum()),negative_to_positive=int((~before&after).sum())))
    pd.DataFrame(changes).to_csv(OUT/'paired_call_changes.csv',index=False)
    # Selected checkpoint spot checks preserve evaluation batch ordering.
    raw=np.load(OLD/'windows.npy');meta=pd.read_csv(OLD/'cycles.csv');labels=pd.read_csv(OUT/'first_session_labels.csv')
    keep=meta.trial.isin(labels[labels.participant.isin(people.participant)].trial);x=canonical(raw[:,:,:6])[0][keep];meta=meta.loc[keep].reset_index(drop=True)
    norm=np.load(OUT/'checkpoints'/'fold0_scaler.npz');x-=norm['mean'];x/=norm['scale'];errors={};torch.set_num_threads(4)
    for arm in ['fixed','decay','warmup']:
        run=f'{arm}_fold0_seed42'
        with contextlib.redirect_stdout(io.StringIO()):model=upstream_builder()(dict(use_wandb=False,n_filters=32,n_layers=1,initial_lr=.001,evaluation_metric='AUC'),200,6)
        model.load_weights(OUT/'checkpoints'/f'{run}.weights.h5')
        replay=predict(model,x,meta,people[people.fold.eq(0)]).set_index('participant').score
        saved=p[(p.arm==arm)&p.seed.eq(42)&p.outer_fold.eq(0)].set_index('participant');err=float(abs(replay-saved.score).max());assert err<1e-5,(arm,err)
        assert (replay.ge(saved.threshold)==saved.positive).all();errors[arm]=err
    (OUT/'verification.json').write_text(json.dumps(dict(fits=27,epochs_each=40,source_checks=True,split_threshold_checks=True,reload_errors=errors),indent=2))
    environment=dict(python=platform.python_version(),packages={name:importlib.metadata.version(name) for name in ['torch','keras','numpy','pandas','scikit-learn','scipy']},gpu=torch.cuda.get_device_name() if torch.cuda.is_available() else None,recorded_at='post-run verification')
    (OUT/'environment.json').write_text(json.dumps(environment,indent=2))
    print(pd.DataFrame(dynamics).groupby('arm').agg(best_epoch_min=('best_epoch','min'),best_epoch_max=('best_epoch','max'),late_recoveries=('best_after_stop','sum')).to_string())

if __name__=='__main__':main()
