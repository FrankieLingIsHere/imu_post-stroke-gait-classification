"""Execute the locked HR experiment; reuse existing baselines."""
from pathlib import Path
import sys,json
import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedKFold

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from src.features.directional_hr import trial_hr
from run_stance_variability import fit_model
from run_phase_nested_threshold import ARMS,sensitivity_threshold
from run_conditional_gait_comparison import sha

OUT=ROOT/'data/processed/directional_hr_v1'


def main():
    OUT.mkdir(exist_ok=True)
    prior=ROOT/'data/processed/phase_nested_threshold_v1'
    phase=ROOT/'data/processed/bilateral_phase_v1'
    people=pd.read_csv(phase/'participant_features.csv')
    trials=pd.read_csv(phase/'trial_features.csv')
    axes=pd.read_csv(ROOT/'data/processed/directional_axis_v1/axis_audit.csv').set_index('trial')
    inputs=[phase/'participant_features.csv',phase/'trial_features.csv',prior/'predictions.csv',ROOT/'docs/ML_HARMONIC_RATIO_PROTOCOL_2026-09-09.md',Path(__file__),ROOT/'src/features/directional_hr.py',ROOT/'data/processed/directional_axis_v1/axis_audit.csv']
    (OUT/'manifest.json').write_text(json.dumps({str(p.relative_to(ROOT)):sha(p) for p in inputs},indent=2))
    paths={p.stem.removesuffix('_meta'):p for p in (ROOT/'data/raw/voisard_2025/data').glob('*/*/*/*/*_meta.json')}
    rows=[]
    for r in trials.itertuples():
        p=paths[r.trial];m=json.loads(p.read_text(encoding='utf-8'));assert m['freq']==100
        signal_path=p.parent/(r.trial+'_processed_data.txt')
        y=pd.read_csv(signal_path,sep='\t',usecols=['LB_Acc_Y']).LB_Acc_Y.to_numpy()
        result=trial_hr(y,m.get('leftGaitEvents') or [],m.get('rightGaitEvents') or [],m['uturnBoundaries'])
        if not r.reference_valid:result['ml_log_hr']=np.nan
        quality=bool(axes.loc[r.trial,'comparison_status']=='compared' and abs(axes.loc[r.trial,'initial_x_gravity_fraction'])>=.9)
        rows.append(dict(participant=r.participant,trial=r.trial,reference_valid=r.reference_valid,quality_screen=quality,
                         signal_sha256=sha(signal_path),metadata_sha256=sha(p),**result))
    ledger=pd.DataFrame(rows);ledger.to_csv(OUT/'trial_features.csv',index=False)
    predictions=[];inner_rows=[];thresholds=[];coverage_rows=[]
    old=pd.read_csv(prior/'predictions.csv')
    for variant in ['main','orientation_screened']:
        trial_values=ledger.copy()
        if variant!='main':trial_values.loc[~trial_values.quality_screen,'ml_log_hr']=np.nan
        data=people.merge(trial_values.groupby('participant').ml_log_hr.mean(),on='participant',validate='one_to_one')
        assert len(data)==259
        data.to_csv(OUT/f'participants_{variant}.csv',index=False)
        coverage=data.assign(available=data.ml_log_hr.notna()).groupby(['target','pathology']).agg(n=('participant','size'),available=('available','sum')).reset_index()
        coverage['variant']=variant;coverage_rows.append(coverage)
        if variant=='main' and (coverage.available/coverage.n).min()<.95:
            pd.concat(coverage_rows).to_csv(OUT/'coverage.csv',index=False)
            (OUT/'decision.json').write_text(json.dumps({'passed':False,'reason':'main coverage failed; no fits'}));return
        for scope,subset in [('all_selected',data),('device_protocol_matched',data[data.matched])]:
            reuse=old[old.scope.eq(scope)].copy();reuse['variant']=variant;predictions.append(reuse)
            for fold in sorted(subset.fold.unique()):
                train,test=subset[subset.fold.ne(fold)],subset[subset.fold.eq(fold)]
                assert not set(train.participant)&set(test.participant)
                assert not set(train.loc[train.target.eq(2),'pathology'])&set(test.loc[test.target.eq(2),'pathology'])
                splits=list(StratifiedKFold(3,shuffle=True,random_state=20260909).split(train,train.target))
                for base in ['nuisance_cadence_phase','combined_phase']:
                    columns=ARMS[base]+['ml_log_hr'];arm=base+'_hr';parts=[]
                    for inner,(fi,vi) in enumerate(splits):
                        fit,val=train.iloc[fi],train.iloc[vi]
                        assert not set(fit.participant)&set(val.participant)
                        model=fit_model(fit,columns);row=val[['participant','target','pathology','fold']].copy()
                        row['score']=model.predict_proba(val[columns])[:,1]
                        row['scope'],row['variant'],row['arm'],row['outer_fold'],row['inner_fold']=scope,variant,arm,fold,inner
                        parts.append(row)
                    inner_scores=pd.concat(parts);assert inner_scores.participant.nunique()==len(train)
                    inner_rows.append(inner_scores);stroke=inner_scores.loc[inner_scores.target.eq(1),'score'];threshold=sensitivity_threshold(stroke)
                    thresholds.append(dict(scope=scope,variant=variant,arm=arm,fold=int(fold),threshold=threshold,inner_sensitivity=float(stroke.ge(threshold).mean())))
                    model=fit_model(train,columns);row=test[['participant','target','pathology','fold']].copy()
                    row['score']=model.predict_proba(test[columns])[:,1]
                    row['threshold']=threshold;row['positive']=row.score.ge(threshold)
                    row['scope'],row['variant'],row['arm']=scope,variant,arm;predictions.append(row)
    pd.concat(coverage_rows).to_csv(OUT/'coverage.csv',index=False)
    pred=pd.concat(predictions,ignore_index=True);pred.to_csv(OUT/'predictions.csv',index=False)
    pd.concat(inner_rows).to_csv(OUT/'inner_predictions.csv',index=False);pd.DataFrame(thresholds).to_csv(OUT/'thresholds.csv',index=False)
    metrics=[]
    for (variant,scope,arm),g in pred.groupby(['variant','scope','arm']):
        for rule,pos in [('nested',g.positive),('fixed_0.5',g.score.ge(.5))]:
            counts={t:int(pos[g.target.eq(t)].sum()) for t in [0,1,2]}
            metrics.append(dict(variant=variant,scope=scope,arm=arm,rule=rule,stroke_tp=counts[1],healthy_fp=counts[0],other_fp=counts[2],sensitivity=counts[1]/g.target.eq(1).sum(),other_fpr=counts[2]/g.target.eq(2).sum()))
    metrics=pd.DataFrame(metrics);metrics.to_csv(OUT/'metrics.csv',index=False)
    pred.groupby(['variant','scope','arm','target','pathology']).agg(n=('participant','size'),positive=('positive','sum')).to_csv(OUT/'pathology_counts.csv')
    gates=[]
    for scope,g in metrics[metrics.variant.eq('main')&metrics.rule.eq('nested')].groupby('scope'):
        g=g.set_index('arm');b=g.loc['nuisance_cadence_phase_hr'];checks=[]
        for base in ['nuisance_cadence','nuisance_cadence_phase']:
            a=g.loc[base];checks.append(bool(b.sensitivity>=.9 and b.stroke_tp>=a.stroke_tp and b.healthy_fp<=a.healthy_fp and a.other_fpr-b.other_fpr>=.05))
        gates.append(dict(scope=scope,passed=all(checks)))
    decision=dict(passed=all(g['passed'] for g in gates),gates=gates,inner_fits=72,outer_fits=24)
    (OUT/'decision.json').write_text(json.dumps(decision,indent=2))
    print(metrics[metrics.rule.eq('nested')].to_string(index=False));print(decision)


if __name__=='__main__':main()
