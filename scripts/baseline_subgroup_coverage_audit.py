"""Coverage and participant-level subgroup audit for frozen baseline predictions."""
from pathlib import Path
import pandas as pd
from sklearn.metrics import roc_auc_score,balanced_accuracy_score
R=Path(__file__).resolve().parents[1]
p=pd.read_csv(R/'data/processed/repeated_pooled_outer_predictions.csv')
ages=pd.read_csv(R/'data/processed/continuous_age_regression_predictions.csv')[['participant_key','age']].drop_duplicates('participant_key')
p=p.merge(ages,on='participant_key',how='left'); p=p.groupby(['participant_key','dataset_id','label_binary','age'],as_index=False).raw_probability.mean(); p['age_band']=pd.cut(p.age,[-1,39,59,74,200],labels=['<40','40-59','60-74','75+'])
rows=[]
for keys,g in p.groupby(['dataset_id','age_band'],dropna=False):
 y=g.label_binary; prob=g.raw_probability; n=len(g); classes=y.nunique(); h=int((y==0).sum()); s=int((y==1).sum()); estimable=(str(keys[1])!='nan' and h>=5 and s>=5); rows.append({'dataset_id':keys[0],'age_band':str(keys[1]),'participants':n,'healthy':h,'stroke':s,'auroc':roc_auc_score(y,prob) if estimable else None,'balanced_accuracy':balanced_accuracy_score(y,(prob>=.5).astype(int)) if estimable else None,'evidence':'estimable' if estimable else 'descriptive_only'})
out=R/'data/processed/baseline_subgroup_coverage_audit.csv'; result=pd.DataFrame(rows); result.to_csv(out,index=False); print(result.to_string(index=False)); print('Wrote',out)
