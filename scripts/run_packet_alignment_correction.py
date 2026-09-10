"""Versioned native timeline correction: fixed-fold features and frozen FP test."""
from pathlib import Path
import sys,json,hashlib
import numpy as np
import pandas as pd
from scipy.signal import butter,sosfiltfilt

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.data.voisard_aligned import load_aligned_lower_back
from src.features.voisard import _events_outside_uturn,_walking_bounds
from scripts.run_conditional_gait_comparison import run_cv,score_metrics
from scripts.benchmark_binary_hard_negative_exposure_loco import bounds
from models.predict_lower_back import load_bundle,predict_windows

P=ROOT/'data/processed';OUT=P/'packet_alignment_v1'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    OUT.mkdir(exist_ok=True)
    if (OUT/'verification.json').exists():raise FileExistsError('Completed correction already exists')
    base=pd.read_csv(P/'conditional_gait_v1/trial_features.csv')
    oldpeople=pd.read_csv(P/'conditional_gait_v1/participant_contract.csv')
    hm=pd.read_csv(P/'differential_gait_v1/other_metadata.csv')
    oldx=np.load(P/'differential_gait_v1/other_windows.npy')
    corrected=np.full_like(oldx,np.nan)
    paths={p.stem.removesuffix('_meta'):p for p in (ROOT/'data/raw/voisard_2025/data').glob('*/*/*/*/*_meta.json')}
    protocol=dict(change='native packet reconstruction using earliest first packet of four synchronized raw sensors, linear interior interpolation <=150 samples; no filtering/centering',
        feature_comparison='only lb_rms changes; same participant folds, models, weighting, threshold; reference-only features unchanged',
        frozen_comparison='v0.2.0 old versus aligned native input on identical legacy nonstroke window positions; no refit',
        scope='259 feature participants / 138 nonstroke frozen stress participants; no final independent sensitivity estimate',
        hashes={str(p.relative_to(ROOT)):sha(p) for p in [Path(__file__),ROOT/'src/data/voisard_aligned.py',P/'conditional_gait_v1/participant_contract.csv',P/'conditional_gait_v1/trial_features.csv',P/'differential_gait_v1/other_windows.npy']})
    (OUT/'protocol.json').write_text(json.dumps(protocol,indent=2))
    audit=[];rows=[]
    for i,r in enumerate(base.itertuples()):
        p=paths[r.trial];m=json.loads(p.read_text());x,info=load_aligned_lower_back(p.parent,r.trial)
        lp,la=_events_outside_uturn(m['leftGaitEvents'],m['uturnBoundaries']);rp,ra=_events_outside_uturn(m['rightGaitEvents'],m['uturnBoundaries']);spans=_walking_bounds(lp+rp,la+ra)
        valid=all(0<=a<b<=len(x) and np.isfinite(x[a:b]).all() for a,b in spans)
        rms=float(np.sqrt(np.mean(np.concatenate([x[a:b] for a,b in spans])**2)*3)) if valid else np.nan
        rows.append(dict(participant=r.participant,trial=r.trial,lb_rms_old=r.lb_rms,lb_rms=rms,valid=valid))
        # Independent signal-only verification against provider processing:
        # compare filtered magnitudes to avoid their documented sign/axis changes.
        q=pd.read_csv(p.parent/(r.trial+'_processed_data.txt'),sep='\t')[['LB_Acc_X','LB_Acc_Y','LB_Acc_Z']].to_numpy()
        start=info['lb_first']-info['origin'];native=x[start:]
        if np.isfinite(native).all():
            filtered=sosfiltfilt(butter(8,14,fs=m['freq'],output='sos'),native,axis=0)
            n=min(len(filtered),len(q)-start)
            delta=np.linalg.norm(filtered[:n],axis=1)-np.linalg.norm(q[start:start+n],axis=1)
            check=float(np.nanmax(np.abs(delta[30:-30])))
        else:check=np.nan
        audit.append(dict(participant=r.participant,trial=r.trial,**info,aligned_rows=len(x),valid_features=valid,provider_filtered_norm_max_error=check))
        indices=hm.index[hm.trial_id.eq(r.trial)].to_numpy()
        if len(indices):
            lengths=[info['native_rows']]+[len(pd.read_csv(p.parent/f'{r.trial}_raw_data_{s}.txt',sep='\t',usecols=['PacketCounter'])) for s in ['LF','RF']]
            starts=[left for a,b in bounds(m) for left in range(int(a),int(b)-500+1,250) if left+500<=min(lengths)]
            assert len(starts)==len(indices),(r.trial,len(starts),len(indices))
            raw=pd.read_csv(p.parent/f'{r.trial}_raw_data_LB.txt',sep='\t')[['Acc_X','Acc_Y','Acc_Z']].to_numpy('float32')/9.80665
            for ix,left in zip(indices,starts):
                np.testing.assert_allclose(oldx[ix,:,0],np.linalg.norm(raw[left:left+500],axis=1),rtol=1e-6,atol=1e-6)
                if left+500<=len(x):corrected[ix,:,0]=np.linalg.norm(x[left:left+500]/9.80665,axis=1)
        if (i+1)%250==0:print('aligned',i+1,'/',len(base),flush=True)
    trials=pd.DataFrame(rows);trials.to_csv(OUT/'trial_features.csv',index=False)
    audit=pd.DataFrame(audit);audit.to_csv(OUT/'alignment_audit.csv',index=False)
    newpeople=oldpeople.drop(columns='lb_rms').merge(trials.groupby('participant').lb_rms.mean(),on='participant',validate='one_to_one')
    assert set(newpeople.participant)==set(oldpeople.participant)
    newpeople.to_csv(OUT/'participant_contract.csv',index=False)
    pred=pd.concat([run_cv(newpeople,'all_selected'),run_cv(newpeople[newpeople.matched],'device_protocol_matched')],ignore_index=True)
    pred.to_csv(OUT/'feature_predictions.csv',index=False)
    metrics=[dict(scope=s,arm=a,**score_metrics(g)) for (s,a),g in pred.groupby(['scope','arm'])]
    pd.DataFrame(metrics).to_csv(OUT/'feature_metrics.csv',index=False)
    keep=np.isfinite(corrected).all(axis=(1,2));np.save(OUT/'aligned_nonstroke_windows.npy',corrected)
    # Never drop missing people silently; record common-window coverage.
    hm.assign(common_window=keep).to_csv(OUT/'frozen_window_coverage.csv',index=False)
    bundle=load_bundle(ROOT/'models/checkpoints/stroke-gait-lower-back-ensemble-v0.2.0.pt',ROOT/'models/checkpoints/stroke-gait-lower-back-ensemble-v0.2.0.manifest.json')
    scores=[]
    for name,x in [('old',oldx),('aligned',corrected)]:
        y=predict_windows(bundle,x[keep],device='cuda')
        frame=hm.loc[keep,['participant_key','cohort']].copy();frame['score']=y
        person=frame.groupby(['participant_key','cohort'],as_index=False).score.mean();person['version']=name;scores.append(person)
    result=pd.concat(scores,ignore_index=True);result.to_csv(OUT/'frozen_nonstroke_predictions.csv',index=False)
    assert result.groupby('version').participant_key.nunique().eq(138).all()
    print('FROZEN',result.assign(positive=result.score.ge(.5)).groupby('version').positive.agg(['sum','count']).to_string(),flush=True)
    print(pd.DataFrame(metrics).to_string(index=False),flush=True)
    (OUT/'verification.json').write_text(json.dumps(dict(participants=len(newpeople),trials=len(trials),common_windows=int(keep.sum()),total_windows=len(keep),
        invalid_feature_trials=int((~trials.valid).sum()),provider_norm_error_max=float(audit.provider_filtered_norm_max_error.max()),
        frozen_sha256=sha(ROOT/'models/checkpoints/stroke-gait-lower-back-ensemble-v0.2.0.pt'),hashes={p.name:sha(p) for p in OUT.glob('*.csv')}),indent=2))


if __name__=='__main__':main()
