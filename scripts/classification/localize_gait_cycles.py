"""Trace positive subject decisions back to trials and strongest signal intervals."""
from benchmark_gait_channels import *

def main():
    torch.set_num_threads(4)
    raw=np.load(OLD/'windows.npy');meta=pd.read_csv(OLD/'cycles.csv');frame=canonical(raw[:,:,:6])[0]
    rows=[];peaks=[];errors=[]
    for folder,arms in [(ROOT/'data/processed/gait_frame_v1',['frame6']),(OUT,['acc3','gyro3'])]:
        selection=pd.read_csv(folder/'selection.csv');saved=pd.read_csv(folder/'predictions.csv')
        for r in selection[selection.arm.isin(arms)].itertuples():
            p=saved[(saved.arm==r.arm)&(saved.seed==r.seed)&(saved.outer_fold==r.fold)]
            ix=np.flatnonzero(meta.participant.isin(p.participant));z=frame[ix].copy()
            if r.arm=='acc3':z=z[:,:,:3].copy()
            if r.arm=='gyro3':z=z[:,:,3:].copy()
            norm=np.load(folder/'checkpoints'/f'{r.arm}_fold{r.fold}_scaler.npz');z-=norm['mean'];z/=norm['scale']
            with contextlib.redirect_stdout(io.StringIO()):model=upstream_builder()(dict(use_wandb=False,n_filters=32,n_layers=1,initial_lr=.02,evaluation_metric='AUC'),200,z.shape[-1])
            model.load_weights(folder/'checkpoints'/f'{r.run}.weights.h5');scores=model.predict(z,batch_size=256,verbose=0)[:,1]
            c=meta.iloc[ix].copy();c['score']=scores;c=c.merge(p[['participant','threshold','pathology','target']],on='participant',validate='many_to_one')
            c['above_threshold']=c.score.ge(c.threshold);c['arm']=r.arm;c['seed']=r.seed
            c['start_sec']=c.start/100;c['end_sec']=c.end/100
            c['margin']=c.score-c.threshold
            trial=c.groupby(['arm','seed','participant','pathology','target','trial'],as_index=False).agg(cycles=('score','size'),score=('score','mean'),maximum_cycle_score=('score','max'),above_threshold_fraction=('above_threshold','mean'),threshold=('threshold','first'))
            trial['positive']=trial.score.ge(trial.threshold);rows.append(trial)
            replay=trial.groupby('participant').score.mean();reference=p.set_index('participant').score
            delta=float(abs(replay-reference).max());assert delta<1e-4,(r.run,delta);errors.append(dict(run=r.run,max_error=delta))
            # Save only three strongest intervals per trial, avoiding duplicate waveform files.
            peaks.append(c[c.target.ne(1)].sort_values('score',ascending=False).groupby(['participant','trial']).head(3))
    pd.concat(rows).to_csv(OUT/'trial_localization.csv',index=False);pd.concat(peaks).to_csv(OUT/'strongest_nonstroke_cycles.csv',index=False)
    pd.DataFrame(errors).to_csv(OUT/'cycle_replay_verification.csv',index=False)
    print('Verified',len(errors),'models; max replay error',max(e['max_error'] for e in errors))

if __name__=='__main__':main()
