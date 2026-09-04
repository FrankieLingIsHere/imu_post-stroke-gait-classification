"""Evaluate expanded Sint sensitivity checkpoints on untouched RevalExo."""
from pathlib import Path
import sys
import numpy as np, pandas as pd, torch
from sklearn.metrics import roc_auc_score,brier_score_loss,balanced_accuracy_score
sys.path.insert(0, str(Path(__file__).resolve().parent))
from train_sint_sensitivity_inception import Net

R=Path(__file__).resolve().parents[1]; P=R/'data/processed'; D=torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def main():
 raw=np.load(P/'revalexo_external_windows_float32.npy'); x=np.stack([np.linalg.norm(raw[:,:,0:3],axis=2),np.linalg.norm(raw[:,:,12:15],axis=2),np.linalg.norm(raw[:,:,6:9],axis=2)],2).astype('float32'); m=pd.read_csv(P/'revalexo_external_window_metadata.csv'); m['label_binary']=m.group.map({'HC':0,'ST':1}); probs=[]
 for fold in range(5):
  ck=torch.load(P/f'sint_sensitivity_inception_fold_{fold}_seed_42.pt',map_location='cpu',weights_only=False); model=Net(); model.load_state_dict(ck['model_state_dict']); model.to(D).eval(); z=torch.from_numpy(((x-np.asarray(ck['mean']))/np.maximum(np.asarray(ck['std']),1e-6)).transpose(0,2,1).astype('float32'))
  with torch.no_grad(): probs.append(torch.sigmoid(model(z.to(D))).cpu().numpy())
 p=np.mean(probs,0); g=m.assign(prob=p).groupby(['subject','label_binary'],as_index=False).prob.mean(); y=g.label_binary.to_numpy(); q=g.prob.to_numpy(); out={'model':'sint_sensitivity_inception','participants':len(g),'healthy':int((y==0).sum()),'stroke':int((y==1).sum()),'auroc':roc_auc_score(y,q),'brier':brier_score_loss(y,q),'balanced_accuracy':balanced_accuracy_score(y,q>=.5)}; print(out); g.to_csv(P/'sint_sensitivity_revalexo_participant_predictions.csv',index=False); pd.DataFrame([out]).to_csv(P/'sint_sensitivity_revalexo_metrics.csv',index=False)
if __name__=='__main__': main()
