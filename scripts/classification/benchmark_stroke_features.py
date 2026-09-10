"""Reconstruct inputs and verify held-out benchmark; never score full-fit training accuracy."""
from pathlib import Path
import sys,json
import numpy as np
import pandas as pd
import joblib
from sklearn.metrics import roc_auc_score,balanced_accuracy_score,brier_score_loss
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from models.prototype_stroke_features import FEATURES,validate,predict_frame
from src.features.bilateral_phase import extract_phase,FEATURES as PHASE
from src.features.directional_hr import trial_hr
from src.features.voisard import _events_outside_uturn,_stride_time_stats,_straight_walk_span_samples
from run_stance_variability import fit_model
from run_phase_nested_threshold import sensitivity_threshold
from run_conditional_gait_comparison import sha
OUT=ROOT/'data/processed/stroke_feature_benchmark_v1'


def wilson(k,n):
    z=1.959963984540054;p=k/n;d=1+z*z/n
    center=(p+z*z/(2*n))/d;half=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return center-half,center+half


def main():
    OUT.mkdir(exist_ok=True);source=ROOT/'data/processed/directional_hr_v1';package=ROOT/'models/prototypes/stroke-phase-hr-v0.1.0'
    people=pd.read_csv(source/'participants_main.csv');trials=pd.read_csv(ROOT/'data/processed/bilateral_phase_v1/trial_features.csv')
    stored_hr=pd.read_csv(source/'trial_features.csv').set_index('trial')
    manifest=json.loads((package/'manifest.json').read_text())
    assert sha(package/'model.joblib')==manifest['checkpoint_sha256'] and manifest['features']==FEATURES
    assert sha(source/'participants_main.csv')==manifest['input_sha256']
    paths={p.stem.removesuffix('_meta'):p for p in (ROOT/'data/raw/voisard_2025/data').glob('*/*/*/*/*_meta.json')}
    rows=[]
    for r in trials.itertuples():
        p=paths[r.trial];m=json.loads(p.read_text(encoding='utf-8'))
        assert sha(p)==r.metadata_sha256==stored_hr.loc[r.trial,'metadata_sha256']
        signal=p.parent/f'{r.trial}_processed_data.txt';assert sha(signal)==stored_hr.loc[r.trial,'signal_sha256']
        y=pd.read_csv(signal,sep='\t',usecols=['LB_Acc_Y']).LB_Acc_Y.to_numpy()
        phase=extract_phase(m['leftGaitEvents'],m['rightGaitEvents'],m['uturnBoundaries'],m['freq'])
        hr=trial_hr(y,m['leftGaitEvents'],m['rightGaitEvents'],m['uturnBoundaries'])['ml_log_hr']
        lp,la=_events_outside_uturn(m['leftGaitEvents'],m['uturnBoundaries']);rp,ra=_events_outside_uturn(m['rightGaitEvents'],m['uturnBoundaries'])
        _,_,ln=_stride_time_stats(lp,la,m['freq']);_,_,rn=_stride_time_stats(rp,ra,m['freq'])
        span=_straight_walk_span_samples(lp+rp,la+ra,m['uturnBoundaries'])
        if not r.reference_valid:
            phase.update({k:np.nan for k in PHASE});hr=np.nan
        rows.append(dict(participant=r.participant,trial=r.trial,age=m.get('age'),xsens_fraction=float(m['sensor']=='MTw Awinda XSens'),
                         protocol_length_m=float(m['protocol'].split('m')[0]),cadence=(ln+rn)*60*m['freq']/span if span>0 else np.nan,
                         ml_log_hr=hr,**{k:phase[k] for k in PHASE}))
    reconstructed=pd.DataFrame(rows);reconstructed.to_csv(OUT/'reconstructed_trials.csv',index=False)
    reconstructed=reconstructed.groupby('participant')[FEATURES].mean().reindex(people.participant)
    required=people.set_index('participant')[FEATURES];np.testing.assert_allclose(reconstructed,required,rtol=1e-10,atol=1e-10,equal_nan=True)
    availability=[]
    for name in FEATURES:
        delta=(reconstructed[name]-required[name]).abs()
        availability.append(dict(feature=name,available=int(required[name].notna().sum()),missing=int(required[name].isna().sum()),max_reconstruction_difference=float(delta.max())))
    pd.DataFrame(availability).to_csv(OUT/'feature_audit.csv',index=False)
    assert validate(people)[1].eq('ok').all()
    saved=pd.read_csv(source/'predictions.csv');inner=pd.read_csv(source/'inner_predictions.csv');thresholds=pd.read_csv(source/'thresholds.csv')
    base_predictions=pd.read_csv(ROOT/'data/processed/phase_nested_threshold_v1/predictions.csv')
    arms={'nuisance_cadence':['age','xsens_fraction','protocol_length_m','cadence'],
          'nuisance_cadence_phase_hr':FEATURES}
    outputs=[];checks=[]
    for scope,data in [('all_selected',people),('device_protocol_matched',people[people.matched])]:
        for fold in sorted(data.fold.unique()):
            train,test=data[data.fold.ne(fold)],data[data.fold.eq(fold)]
            assert not set(train.participant)&set(test.participant)
            assert not set(train.loc[train.target.eq(2),'pathology'])&set(test.loc[test.target.eq(2),'pathology'])
            for arm,columns in arms.items():
                model=fit_model(train,columns);score=model.predict_proba(test[columns])[:,1]
                reference=saved[saved.variant.eq('main')&saved.scope.eq(scope)&saved.arm.eq(arm)&saved.fold.eq(fold)].set_index('participant').reindex(test.participant)
                np.testing.assert_allclose(score,reference.score,rtol=1e-9,atol=1e-10)
                if arm.endswith('_hr'):
                    calibration=inner[inner.variant.eq('main')&inner.scope.eq(scope)&inner.arm.eq(arm)&inner.outer_fold.eq(fold)]
                    assert set(calibration.participant)==set(train.participant)
                    assert calibration.participant.nunique()==len(calibration)
                    threshold=sensitivity_threshold(calibration.loc[calibration.target.eq(1),'score'])
                    recorded=thresholds[thresholds.variant.eq('main')&thresholds.scope.eq(scope)&thresholds.arm.eq(arm)&thresholds.fold.eq(fold)].threshold.item()
                    assert abs(threshold-recorded)<1e-12
                    # Exercise deployed row validation on held-out data, using fold-specific thresholds.
                    api=predict_frame(test,model,threshold);assert api.status.eq('ok').all()
                    np.testing.assert_allclose(api.score,score)
                else:
                    old=base_predictions[base_predictions.scope.eq(scope)&base_predictions.arm.eq(arm)&base_predictions.fold.eq(fold)]
                    assert old.threshold.nunique()==1;threshold=old.threshold.iloc[0]
                row=test[['participant','target','pathology','fold']].copy();row['score']=score;row['threshold']=threshold;row['positive']=score>=threshold;row['scope']=scope;row['arm']=arm
                outputs.append(row);checks.append(dict(scope=scope,fold=int(fold),arm=arm,train_n=len(train),test_n=len(test),score_max_difference=float(np.max(abs(score-reference.score.to_numpy())))))
    pred=pd.concat(outputs);pred.to_csv(OUT/'held_out_predictions.csv',index=False);pd.DataFrame(checks).to_csv(OUT/'fold_verification.csv',index=False)
    metrics=[];intervals=[]
    for (scope,arm),g in pred.groupby(['scope','arm']):
        y=g.target.eq(1);pos=g.positive
        k={t:int(pos[g.target.eq(t)].sum()) for t in [0,1,2]};n={t:int(g.target.eq(t).sum()) for t in [0,1,2]}
        metrics.append(dict(scope=scope,arm=arm,n=len(g),stroke_tp=k[1],stroke_fn=n[1]-k[1],healthy_fp=k[0],other_fp=k[2],sensitivity=k[1]/n[1],healthy_specificity=1-k[0]/n[0],other_fpr=k[2]/n[2],auroc=roc_auc_score(y,g.score),balanced_accuracy=balanced_accuracy_score(y,pos),brier=brier_score_loss(y,g.score)))
        for label,num,den in [('sensitivity',k[1],n[1]),('healthy_specificity',n[0]-k[0],n[0]),('other_fpr',k[2],n[2])]:
            lo,hi=wilson(num,den);intervals.append(dict(scope=scope,arm=arm,metric=label,value=num/den,lower=lo,upper=hi))
    metrics=pd.DataFrame(metrics);metrics.to_csv(OUT/'metrics.csv',index=False);pd.DataFrame(intervals).to_csv(OUT/'intervals.csv',index=False)
    pred.groupby(['scope','arm','pathology']).agg(n=('participant','size'),positive=('positive','sum')).to_csv(OUT/'pathology_counts.csv')
    pred.groupby(['scope','arm','fold','target']).agg(n=('participant','size'),positive=('positive','sum')).to_csv(OUT/'fold_counts.csv')
    verification=dict(reconstructed_trials=len(rows),participants=len(people),feature_count=len(FEATURES),feature_reconstruction_passed=True,refits=12,
                      scope='reproduction and packaged-interface held-out benchmark on reused development data; not new external validation',
                      full_package_threshold='not used for held-out metrics; it was selected using all development labels',
                      package_sha256=sha(package/'model.joblib'),script_sha256=sha(Path(__file__)))
    (OUT/'verification.json').write_text(json.dumps(verification,indent=2));print(metrics.to_string(index=False));print(json.dumps(verification,indent=2))


if __name__=='__main__':main()
