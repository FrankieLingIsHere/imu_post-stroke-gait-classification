"""Localize saved errors without selecting models or thresholds."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'data/processed/gait_channel_ablation_v1'

def main():
    old=ROOT/'data/processed/gait_frame_v1'
    p=pd.concat([pd.read_csv(old/'predictions.csv'),pd.read_csv(OUT/'predictions.csv')],ignore_index=True)
    p['margin']=p.score-p.threshold
    p.to_csv(OUT/'all_participant_predictions.csv',index=False)
    p.groupby(['arm','seed','pathology']).agg(n=('participant','size'),positive=('positive','sum'),mean_score=('score','mean'),mean_margin=('margin','mean')).to_csv(OUT/'pathology_localization.csv')
    stable=p.groupby(['arm','participant','target','pathology']).agg(runs=('positive','size'),positive_runs=('positive','sum'),mean_margin=('margin','mean'),min_margin=('margin','min'),max_margin=('margin','max')).reset_index()
    stable.to_csv(OUT/'participant_consistency.csv',index=False)
    stable[stable.target.ne(1)&stable.positive_runs.eq(3)].to_csv(OUT/'consistent_false_positive_ids.csv',index=False)
    # Participant-level comparison keeps seeds paired; does not promote an ensemble.
    comparisons=[]
    for scope,data in [('full',p),('matched',p[p.matched])]:
        for seed,g in data.groupby('seed'):
            base=g[g.arm.eq('frame6')].set_index('participant')
            for arm in ['acc3','gyro3']:
                b=g[g.arm.eq(arm)].set_index('participant').loc[base.index]
                masks={'stroke':base.target.eq(1),'healthy':base.target.eq(0),'neuro':base.pathology.isin(['PD','RIL','CIPN'])}
                d=dict(scope=scope,seed=int(seed),arm=arm)
                for name,mask in masks.items():
                    d[name+'_n']=int(mask.sum());d[name+'_base_positive']=int(base.positive[mask].sum());d[name+'_positive']=int(b.positive[mask].sum())
                    d[name+'_resolved']=int((base.positive[mask]&~b.positive[mask]).sum());d[name+'_new']=int((~base.positive[mask]&b.positive[mask]).sum())
                d['passed']=bool((d['neuro_base_positive']-d['neuro_positive'])/d['neuro_n']>=.05 and d['stroke_positive']>=d['stroke_base_positive'] and d['healthy_positive']<=d['healthy_base_positive'])
                comparisons.append(d)
    pd.DataFrame(comparisons).to_csv(OUT/'paired_comparisons.csv',index=False)
    p.groupby(['arm','outer_fold','seed']).threshold.first().to_csv(OUT/'thresholds.csv')
    cal=pd.concat([pd.read_csv(old/'calibration.csv'),pd.read_csv(OUT/'calibration.csv')],ignore_index=True)
    cal[cal.target.eq(1)].groupby(['arm','outer_fold','seed']).agg(n=('participant','size'),detected=('positive','sum'),minimum_score=('score','min'),threshold=('threshold','first')).to_csv(OUT/'calibration_resolution.csv')
    stroke=cal[cal.target.eq(1)]
    setting=stroke.loc[stroke.groupby(['arm','outer_fold','seed']).score.idxmin()].copy()
    assert np.allclose(setting.score,setting.threshold,atol=1e-7,rtol=0)
    setting.to_csv(OUT/'threshold_setting_participants.csv',index=False)
    overlap=[]
    for (arm,seed,fold),g in p.groupby(['arm','seed','outer_fold']):
        for pathology,h in g.groupby('pathology'):
            overlap.append(dict(arm=arm,seed=int(seed),fold=int(fold),pathology=pathology,n=len(h),q10=h.score.quantile(.1),median=h.score.median(),q90=h.score.quantile(.9),threshold=h.threshold.iloc[0]))
    pd.DataFrame(overlap).to_csv(OUT/'score_overlap.csv',index=False)
    e=pd.concat([pd.read_csv(old/'external_predictions.csv'),pd.read_csv(OUT/'external_predictions.csv')],ignore_index=True)
    e['margin']=e.score-e.threshold;e.to_csv(OUT/'all_external_predictions.csv',index=False)
    paired=[]
    for (arm,seed,fold),g in e.groupby(['arm','seed','outer_fold']):
        score=g.pivot(index='participant',columns='condition',values='score');pos=g.pivot(index='participant',columns='condition',values='positive')
        for condition in ['OG_st_fatigue','OG_dt_control','OG_dt_fatigue']:
            for person in score.index:
                paired.append(dict(arm=arm,seed=int(seed),fold=int(fold),participant=person,condition=condition,score_delta=float(score.loc[person,condition]-score.loc[person,'OG_st_control']),new_fp=bool(pos.loc[person,condition] and not pos.loc[person,'OG_st_control']),resolved_fp=bool(not pos.loc[person,condition] and pos.loc[person,'OG_st_control'])))
    pd.DataFrame(paired).to_csv(OUT/'external_paired_conditions.csv',index=False)
    e.groupby(['arm','participant','condition']).agg(runs=('positive','size'),positive_runs=('positive','sum'),mean_margin=('margin','mean')).to_csv(OUT/'external_consistency.csv')
    result=dict(fits=36,passed_arms=[arm for arm in ['acc3','gyro3'] if all(d['passed'] for d in comparisons if d['arm']==arm)],localization_complete=True,causal_root_cause_proved=False)
    (OUT/'comparison_decision.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

if __name__=='__main__':main()
