from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]; P=ROOT/'data/processed'
lb=pd.read_csv(P/'full_expanded_lower_back_only_revalexo_participant_predictions.csv').rename(columns={'prob':'lb_prob','y':'label'})
three=pd.read_csv(P/'full_expanded_prototype_revalexo_participant_predictions.csv').rename(columns={'prob':'three_prob','label_binary':'label'})
d=lb.merge(three,on=['subject','label'])
d['lb_pred']=(d.lb_prob>=.5).astype(int); d['three_pred']=(d.three_prob>=.5).astype(int); d['lb_correct']=d.lb_pred.eq(d.label); d['three_correct']=d.three_pred.eq(d.label)
def category(r):
 if r.lb_correct and r.three_correct:return 'both_correct'
 if (not r.lb_correct) and r.three_correct:return 'three_channel_rescued'
 if r.lb_correct and (not r.three_correct):return 'lower_back_only_correct'
 return 'both_wrong'
d['transition']=d.apply(category,axis=1)
d.to_csv(P/'lower_back_vs_three_channel_external_error_analysis.csv',index=False)
rows=[]
for label,name in [(0,'healthy'),(1,'stroke')]:
 q=d[d.label.eq(label)]; rows.append({'group':name,'participants':len(q),'lb_errors':int((~q.lb_correct).sum()),'three_channel_errors':int((~q.three_correct).sum()),'lb_mean_probability':q.lb_prob.mean(),'three_channel_mean_probability':q.three_prob.mean()})
summary=pd.DataFrame(rows); summary.to_csv(P/'lower_back_vs_three_channel_external_error_summary.csv',index=False)
print(summary.to_string(index=False)); print(d.transition.value_counts().to_string())
