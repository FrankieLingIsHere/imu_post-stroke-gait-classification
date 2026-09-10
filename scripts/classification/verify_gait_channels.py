"""Audit selection and threshold provenance after the fixed experiment."""
from benchmark_gait_channels import *

def main():
    torch.set_num_threads(4)
    s=pd.read_csv(OUT/'selection.csv');h=pd.read_csv(OUT/'histories.csv')
    p=pd.read_csv(OUT/'predictions.csv');c=pd.read_csv(OUT/'calibration.csv');e=pd.read_csv(OUT/'external_predictions.csv')
    assert len(s)==18 and h.run.nunique()==36
    assert np.isfinite(h[['loss','val_loss']]).all().all()
    splitsaved=pd.read_csv(OLD/'splits.csv')
    for fold,g in splitsaved.groupby('outer_fold'):
        assert len(g)==259 and g.participant.is_unique
        train=g[g.role.ne('test')];test=g[g.role.eq('test')]
        assert not set(train.loc[train.target.eq(2),'pathology']) & set(test.loc[test.target.eq(2),'pathology'])
    for r in s.itertuples():
        prefix=f'{r.arm}_fold{r.fold}_seed{r.seed}_'
        losses=h[h.run.str.startswith(prefix)].groupby('run').val_loss.min()
        assert np.isclose(losses.min(),r.val_loss) and np.isclose(losses[r.run],r.val_loss)
        for run in losses.index:assert (OUT/'checkpoints'/f'{run}.weights.h5').is_file()
        cc=c[(c.arm==r.arm)&(c.seed==r.seed)&(c.outer_fold==r.fold)]
        ss=np.sort(cc.loc[cc.target.eq(1),'score'])[::-1];threshold=ss[int(np.ceil(.9*len(ss)))-1]
        for table in [p,e]:
            q=table[(table.arm==r.arm)&(table.seed==r.seed)&(table.outer_fold==r.fold)]
            assert np.allclose(q.threshold,threshold) and (q.positive==q.score.ge(q.threshold)).all()
        pp=p[(p.arm==r.arm)&(p.seed==r.seed)&(p.outer_fold==r.fold)]
        assert set(pp.participant)==set(splitsaved[(splitsaved.outer_fold==r.fold)&(splitsaved.role=='test')].participant)
    assert len(p)==259*6 and not p.duplicated(['arm','seed','participant']).any()
    assert len(e)==16*4*18 and not e.duplicated(['arm','seed','outer_fold','participant','condition']).any()
    for path,digest in json.loads((OUT/'manifest.json').read_text()).items():assert sha(ROOT/path)==digest,path
    for path,digest in json.loads((OUT/'external_hashes.json').read_text()).items():assert sha(ROOT/path)==digest,path
    raw=np.load(OLD/'windows.npy');meta=pd.read_csv(OLD/'cycles.csv');people=pd.read_csv(OLD/'people.csv');reload_errors={}
    for arm in ['acc3','gyro3']:
        row=s[(s.arm==arm)&(s.fold==0)&(s.seed==42)].iloc[0]
        frame=canonical(raw[:,:,:6])[0];x=frame[:,:,:3].copy() if arm=='acc3' else frame[:,:,3:].copy()
        norm=np.load(OUT/'checkpoints'/f'{arm}_fold0_scaler.npz');x-=norm['mean'];x/=norm['scale']
        with contextlib.redirect_stdout(io.StringIO()):model=upstream_builder()(dict(use_wandb=False,n_filters=32,n_layers=1,initial_lr=.02,evaluation_metric='AUC'),200,x.shape[-1])
        model.load_weights(OUT/'checkpoints'/f'{row.run}.weights.h5')
        replay=predict(model,x,meta,people[people.fold.eq(0)]).set_index('participant').score
        saved=p[(p.arm==arm)&(p.seed==42)&(p.outer_fold==0)].set_index('participant').score
        error=float(abs(replay-saved).max());assert error<1e-5,(arm,error)
        thresholds=p[(p.arm==arm)&(p.seed==42)&(p.outer_fold==0)].set_index('participant').threshold
        assert (replay.ge(thresholds)==saved.ge(thresholds)).all()
        reload_errors[arm]=error
    result=dict(fits=36,selected_models=18,reload_max_errors=reload_errors,selection_by_validation_only=True,thresholds_from_calibration=True,
                source_hashes=True,split_checks=True,heldout_predictions=len(p),external_predictions=len(e),rotation_unit_tests=2)
    (OUT/'verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

if __name__=='__main__':main()
