"""Paired participant-level comparison of original vs expanded Inception."""
from pathlib import Path
import pandas as pd
from sklearn.metrics import brier_score_loss, roc_auc_score

R=Path(__file__).resolve().parents[1]; P=R/'data/processed'
old=pd.read_csv(P/'inception_revalexo_fold_predictions.csv').groupby(['subject','group','label_binary'],as_index=False).probability.mean().rename(columns={'probability':'old_prob'})
new=pd.read_csv(P/'sint_sensitivity_revalexo_participant_predictions.csv').rename(columns={'prob':'new_prob'}).merge(old,on=['subject','label_binary'],how='left')
new['old_pred']=(new.old_prob>=.5).astype(int); new['new_pred']=(new.new_prob>=.5).astype(int); new['transition']=new.old_pred.astype(str)+'->'+new.new_pred.astype(str); new['correct_old']=new.old_pred.eq(new.label_binary); new['correct_new']=new.new_pred.eq(new.label_binary); new['delta']=new.new_prob-new.old_prob
new.to_csv(P/'sint_revalexo_paired_error_analysis.csv',index=False)
summary=[]
for name,col in [('old','old_prob'),('new','new_prob')]: summary.append({'model':name,'auroc':roc_auc_score(new.label_binary,new[col]),'brier':brier_score_loss(new.label_binary,new[col]),'mean_healthy_prob':new.loc[new.label_binary.eq(0),col].mean(),'mean_stroke_prob':new.loc[new.label_binary.eq(1),col].mean(),'healthy_false_positives':int(((new.label_binary==0)&(new[col]>=.5)).sum()),'stroke_false_negatives':int(((new.label_binary==1)&(new[col]<.5)).sum())})
pd.DataFrame(summary).to_csv(P/'sint_revalexo_paired_error_summary.csv',index=False)
print(pd.DataFrame(summary).to_string(index=False)); print('\nTransitions'); print(new.groupby(['group','transition']).size()); print('\nParticipant rows'); print(new[['subject','label_binary','old_prob','new_prob','delta','transition']].sort_values('subject').to_string(index=False))
