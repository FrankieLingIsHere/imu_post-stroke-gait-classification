"""Benchmark the full expanded prototype on untouched RevalExo."""
from pathlib import Path
import os
import sys, numpy as np, pandas as pd, torch
from sklearn.metrics import roc_auc_score,brier_score_loss,balanced_accuracy_score
R=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(R/'scripts')); from train_sint_sensitivity_inception import Net
P=R/'data/processed'; D=torch.device('cuda' if torch.cuda.is_available() else 'cpu')
def main():
 raw=np.load(P/'revalexo_external_windows_float32.npy'); x=np.stack([np.linalg.norm(raw[:,:,0:3],axis=2),np.linalg.norm(raw[:,:,12:15],axis=2),np.linalg.norm(raw[:,:,6:9],axis=2)],2).astype('float32'); m=pd.read_csv(P/'revalexo_external_window_metadata.csv'); m['label_binary']=m.group.map({'HC':0,'ST':1}); ckname=os.getenv('CHECKPOINT','full_expanded_inception_prototype_seed_42.pt'); output_prefix=os.getenv('OUTPUT_PREFIX','full_expanded_prototype'); ck=torch.load(P/ckname,map_location='cpu',weights_only=False); model=Net(); model.load_state_dict(ck['model_state_dict']); model.to(D).eval(); z=torch.from_numpy(((x-np.asarray(ck['mean']))/np.maximum(np.asarray(ck['std']),1e-6)).transpose(0,2,1).astype('float32'))
 with torch.no_grad(): p=torch.sigmoid(model(z.to(D))).cpu().numpy()
 g=m.assign(prob=p).groupby(['subject','label_binary'],as_index=False).prob.mean(); y=g.label_binary.to_numpy(); q=g.prob.to_numpy(); out={'model':'full_expanded_inception_prototype','checkpoint':ckname,'participants':len(g),'healthy':int((y==0).sum()),'stroke':int((y==1).sum()),'auroc':roc_auc_score(y,q),'brier':brier_score_loss(y,q),'balanced_accuracy':balanced_accuracy_score(y,q>=.5)}; print(out); g.to_csv(P/f'{output_prefix}_revalexo_participant_predictions.csv',index=False); pd.DataFrame([out]).to_csv(P/f'{output_prefix}_revalexo_metrics.csv',index=False)
if __name__=='__main__': main()
