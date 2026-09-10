"""Frozen, rotation-invariant gait_cnn external-negative evaluation."""
import json,contextlib,io
import numpy as np
import pandas as pd
from scipy.signal import butter,filtfilt,resample
from benchmark_gait_cnn import ROOT,OUT as TRAIN,upstream_builder,sha,torch

OUT=ROOT/'data/processed/gait_cnn_duogait_v2'
BASE=ROOT/'data/archive/raw/duogait_2023/data'
CONDITIONS=['OG_st_control','OG_st_fatigue','OG_dt_control','OG_dt_fatigue']

def bounds(tab,n):
    intervals=[];reasons={}
    for r in tab.itertuples():
        flags=[f for f in ['is_outlier','turning_step','turning_interval','interrupted'] if str(getattr(r,f)).lower()=='true']
        if flags:
            for f in flags:reasons[f]=reasons.get(f,0)+1
            continue
        a=int(round(r.timestamps*128));b=int(r.ic_samples)
        if not (0<=a<b<=n and b-a>=16 and a<r.fo_samples<b and abs(b/128-r.ic_times)<.02 and abs((b-a)/128-r.stride_times)<.02):
            reasons['invalid_timing']=reasons.get('invalid_timing',0)+1;continue
        intervals.append((a,b))
    return intervals,reasons

def main():
    torch.set_num_threads(4);OUT.mkdir(parents=True,exist_ok=True)
    if (OUT/'metrics.csv').exists():raise FileExistsError('Completed evaluation')
    (OUT/'protocol.txt').write_text('Frozen lb_magnitude only; all9 fold/seed models separately; existing calibration thresholds; no fit or threshold selection. 128Hz physical10Hz filter, 200point Fourier strides, official row interval timestamps to ic_samples, all four exclusion flags. Filter only contiguous eligible runs. No directional result without verified mapping. Paired condition comparison. No stroke sensitivity available.')
    windows=[];rows=[];ledger=[];hashes={};ba=butter(3,10,fs=128)
    for condition in CONDITIONS:
        for folder in sorted((BASE/'repository_interim'/condition).iterdir()):
            if not folder.is_dir():continue
            p=folder/'SA.csv';ep=BASE/'repository_processed'/condition/folder.name/'left_foot_core_params.csv'
            raw=pd.read_csv(p);tab=pd.read_csv(ep);hashes[str(p.relative_to(ROOT))]=sha(p);hashes[str(ep.relative_to(ROOT))]=sha(ep)
            t=raw.timestamp.to_numpy();assert np.allclose(np.diff(t),1/128,atol=1.1e-5)
            # Event samples refer to the segmented recording, not the retained CSV index.
            sig=np.linalg.norm(raw[['AccX','AccY','AccZ']].to_numpy(float),axis=1)
            fp=folder/'LF.csv';foot=pd.read_csv(fp,usecols=['timestamp']).timestamp.to_numpy()
            hashes[str(fp.relative_to(ROOT))]=sha(fp)
            original,reasons=bounds(tab,len(foot));intervals=[]
            for a,b in original:
                if b>=len(foot):continue
                start,end=foot[a],foot[b]
                aa,bb=np.searchsorted(t,[start,end])
                if aa>=len(t) or bb>=len(t) or abs(t[aa]-start)>.004 or abs(t[bb]-end)>.004:
                    reasons['unsupported_alignment']=reasons.get('unsupported_alignment',0)+1;continue
                intervals.append((int(aa),int(bb)))
            mask=np.zeros(len(sig),bool)
            for a,b in intervals:mask[a:b]=True
            mask &= np.isfinite(sig);edges=np.diff(np.r_[False,mask,False].astype(int))
            filtered=np.full(len(sig),np.nan)
            for a,b in zip(np.where(edges==1)[0],np.where(edges==-1)[0]):
                if b-a>12:filtered[a:b]=filtfilt(*ba,sig[a:b])
            count=0
            for a,b in intervals:
                if not np.isfinite(filtered[a:b]).all():continue
                windows.append(resample(filtered[a:b],200).astype('float32')[:,None]);count+=1
                rows.append(dict(participant=folder.name,condition=condition,start=a,end=b))
            ledger.append(dict(participant=folder.name,condition=condition,total_rows=len(tab),cycles=count,**reasons))
    x=np.stack(windows);meta=pd.DataFrame(rows);meta.to_csv(OUT/'cycles.csv',index=False)
    pd.DataFrame(ledger).to_csv(OUT/'coverage.csv',index=False)
    results=[];saved=pd.read_csv(TRAIN/'predictions.csv')
    for fold in [0,1,2]:
        for seed in [42,137,202]:
            run=f'lb_magnitude_fold{fold}_seed{seed}';cp=TRAIN/'checkpoints'/f'{run}.weights.h5';npz=TRAIN/'checkpoints'/f'{run}.normalization.npz'
            hashes[str(cp.relative_to(ROOT))]=sha(cp);hashes[str(npz.relative_to(ROOT))]=sha(npz)
            norm=np.load(npz);z=x.copy();z-=norm['mean'];z/=norm['scale']
            with contextlib.redirect_stdout(io.StringIO()):model=upstream_builder()(dict(use_wandb=False,n_filters=32,n_layers=1,initial_lr=.02,evaluation_metric='AUC'),200,1)
            model.load_weights(cp);scores=model.predict(z,batch_size=256,verbose=0)[:,1]
            q=meta[['participant','condition']].copy();q['score']=scores;q=q.groupby(['participant','condition'],as_index=False).score.mean()
            threshold=saved[(saved.arm=='lb_magnitude')&(saved.seed==seed)&(saved.outer_fold==fold)].threshold.unique();assert len(threshold)==1
            q['threshold']=threshold[0];q['positive']=q.score.ge(threshold[0]);q['fold']=fold;q['seed']=seed;results.append(q)
    pred=pd.concat(results);pred.to_csv(OUT/'predictions.csv',index=False)
    metrics=pred.groupby(['fold','seed','condition']).agg(n=('participant','size'),fp=('positive','sum'),mean_score=('score','mean')).reset_index()
    metrics.to_csv(OUT/'metrics.csv',index=False)
    paired=[]
    for (fold,seed),g in pred.groupby(['fold','seed']):
        score=g.pivot(index='participant',columns='condition',values='score');pos=g.pivot(index='participant',columns='condition',values='positive')
        for condition in CONDITIONS[1:]:
            paired.append(dict(fold=fold,seed=seed,condition=condition,n=len(score),mean_delta=float((score[condition]-score[CONDITIONS[0]]).mean()),new_fp=int((pos[condition]&~pos[CONDITIONS[0]]).sum()),resolved_fp=int((~pos[condition]&pos[CONDITIONS[0]]).sum())))
    pd.DataFrame(paired).to_csv(OUT/'paired.csv',index=False)
    hashes[str(Path(__file__).relative_to(ROOT))]=sha(Path(__file__))
    (OUT/'manifest.json').write_text(json.dumps(hashes,indent=2));print(metrics.to_string(index=False));print('cycles',len(x))

from pathlib import Path
if __name__=='__main__':main()
