"""Verify saved split/threshold/checkpoint evidence without refitting."""
import contextlib, io, json, os
os.environ['KERAS_BACKEND']='torch'
import numpy as np
import pandas as pd
import keras
import torch
from benchmark_gait_cnn import OUT, ARMS, upstream_builder, predict, sha, ROOT

def main():
    torch.set_num_threads(4)
    pred=pd.read_csv(OUT/'predictions.csv');cal=pd.read_csv(OUT/'calibration_predictions.csv')
    split=pd.read_csv(OUT/'splits.csv');hist=pd.read_csv(OUT/'histories.csv')
    assert len(pred)==259*12 and hist.run.nunique()==36
    assert np.isfinite(hist[['loss','val_loss']]).all().all()
    for _,g in split.groupby('outer_fold'):
        assert g.participant.is_unique and len(g)==259
        train=g[g.role.ne('test')];test=g[g.role.eq('test')]
        assert not set(train.loc[train.target.eq(2),'pathology']) & set(test.loc[test.target.eq(2),'pathology'])
    for (arm,seed,fold),g in pred.groupby(['arm','seed','outer_fold']):
        c=cal[(cal.arm==arm)&(cal.seed==seed)&(cal.outer_fold==fold)]
        scores=np.sort(c.loc[c.target.eq(1),'score'])[::-1]
        threshold=scores[int(np.ceil(.9*len(scores)))-1]
        np.testing.assert_allclose(g.threshold,threshold,atol=1e-12)
        assert (g.positive==g.score.ge(g.threshold)).all()
        run=f'{arm}_fold{fold}_seed{seed}'
        assert (OUT/'checkpoints'/f'{run}.weights.h5').is_file()
    for path,digest in json.loads((OUT/'manifest.json').read_text()).items():
        assert sha(ROOT/path)==digest,path
    x=np.load(OUT/'windows.npy');meta=pd.read_csv(OUT/'cycles.csv');people=pd.read_csv(OUT/'people.csv')
    parity={}
    for arm,channels in ARMS.items():
        run=f'{arm}_fold0_seed42'
        norm=np.load(OUT/'checkpoints'/f'{run}.normalization.npz')
        z=x[:,:,channels].copy()
        z-=norm['mean']
        z/=norm['scale']
        with contextlib.redirect_stdout(io.StringIO()):
            model=upstream_builder()(dict(use_wandb=False,n_filters=32,n_layers=1,initial_lr=.02,evaluation_metric='AUC'),200,len(channels))
        model.load_weights(OUT/'checkpoints'/f'{run}.weights.h5')
        saved=pred[(pred.arm==arm)&(pred.seed==42)&(pred.outer_fold==0)].iloc[0]
        replay=predict(model,z,meta,people[people.fold.eq(0)])
        actual=replay.loc[replay.participant.eq(saved.participant),'score'].iloc[0]
        parity[arm]=float(abs(actual-saved.score));assert parity[arm]<1e-6,(arm,actual,saved.score)
    result=dict(fits=36,participants=259,split_checks=True,threshold_checks=True,
        manifest_checks=True,reload_max_errors=parity,keras=keras.__version__,torch=torch.__version__,
        variable_device=str(model.weights[0].value.device),epochs_min=int(hist.groupby('run').epoch.max().min()),
        epochs_max=int(hist.groupby('run').epoch.max().max()))
    (OUT/'verification.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
