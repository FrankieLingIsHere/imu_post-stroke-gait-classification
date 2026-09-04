"""Build participant-level source/population robustness metrics for expanded Inception."""
from pathlib import Path
import sys,numpy as np,pandas as pd,torch
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.metrics import roc_auc_score,brier_score_loss,balanced_accuracy_score
R=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(R/'scripts')); from train_sint_sensitivity_inception import Net
P=R/'data/processed'; D=torch.device('cuda' if torch.cuda.is_available() else 'cpu')
def score(d,prob,scope):
 g=d.assign(prob=prob).groupby(['participant_key','dataset_id','label_binary'],as_index=False).prob.mean(); y=g.label_binary.to_numpy(); p=g.prob.to_numpy()
 return {'scope':scope,'participants':len(g),'healthy':int((y==0).sum()),'stroke':int((y==1).sum()),'auroc':roc_auc_score(y,p) if len(np.unique(y))==2 else np.nan,'brier':brier_score_loss(y,p),'balanced_accuracy':balanced_accuracy_score(y,p>=.5) if len(np.unique(y))==2 else np.nan}
def main():
 X=np.concatenate([np.load(P/'validated_acceleration_magnitude_windows_float32.npy'),np.load(P/'sint_maartenskliniek_external_windows_float32.npy')]); d=pd.concat([pd.read_csv(P/'validated_window_metadata.csv'),pd.read_csv(P/'sint_maartenskliniek_external_window_metadata.csv')],ignore_index=True); keep=d.label.isin(['healthy','stroke']).to_numpy(); X=X[keep]; d=d.loc[keep].reset_index(drop=True); d['label_binary']=(d.label=='stroke').astype(int); d['source']=d.dataset_id; people=d[['participant_key','label_binary']].drop_duplicates('participant_key'); sg=StratifiedGroupKFold(5,shuffle=True,random_state=42); pred=np.full(len(d),np.nan)
 for fold,(ti,vi) in enumerate(sg.split(people,people.label_binary,people.participant_key)):
  va=d.participant_key.isin(set(people.iloc[vi].participant_key)).to_numpy(); ck=torch.load(P/f'sint_sensitivity_inception_fold_{fold}_seed_42.pt',map_location='cpu',weights_only=False); model=Net(); model.load_state_dict(ck['model_state_dict']); model.to(D).eval(); z=torch.from_numpy(((X[va]-ck['mean'])/np.maximum(ck['std'],1e-6)).transpose(0,2,1).astype('float32'))
  with torch.no_grad(): pred[va]=torch.sigmoid(model(z.to(D))).cpu().numpy()
 rows=[score(d,pred,'expanded_internal_oof')]
 for source,g in d.assign(prob=pred).groupby('source'): rows.append(score(g.drop(columns='prob'),g.prob.to_numpy(),source))
 ext=pd.read_csv(P/'full_expanded_prototype_revalexo_participant_predictions.csv').rename(columns={'subject':'participant_key','prob':'prob'}); ext['dataset_id']='revalexo'; rows.append(score(ext,ext.prob.to_numpy(),'revalexo_external'))
 out=pd.DataFrame(rows); out.to_csv(P/'population_robustness_matrix.csv',index=False); print(out.to_string(index=False)); d.assign(prob=pred).to_csv(P/'expanded_internal_oof_window_predictions.csv',index=False)
if __name__=='__main__': main()
