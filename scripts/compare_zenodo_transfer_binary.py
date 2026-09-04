"""Compare scratch vs Zenodo-pretrained encoder on the existing binary windows."""
from pathlib import Path
import numpy as np, pandas as pd, torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.metrics import roc_auc_score
ROOT=Path(__file__).resolve().parents[1]; device=torch.device('cuda' if torch.cuda.is_available() else 'cpu')
X=np.load(ROOT/'data/processed/validated_gait_windows_float32.npy'); m=pd.read_csv(ROOT/'data/processed/validated_window_metadata.csv'); m['y']=m['label'].map({'healthy':0,'stroke':1}); keep=m.y.notna().to_numpy(); X=X[keep]; m=m.loc[keep].reset_index(drop=True)
people=np.array(sorted(m.participant_key.unique())); rng=np.random.default_rng(20260824); rng.shuffle(people); folds=np.array_split(people,3)
class Net(nn.Module):
 def __init__(self):
  super().__init__(); self.encoder=nn.Sequential(nn.Conv1d(18,64,9,padding=4),nn.BatchNorm1d(64),nn.GELU(),nn.Conv1d(64,128,9,padding=4),nn.BatchNorm1d(128),nn.GELU(),nn.Conv1d(128,128,9,padding=4),nn.GELU(),nn.AdaptiveAvgPool1d(1)); self.head=nn.Sequential(nn.Flatten(),nn.Dropout(.3),nn.Linear(128,1))
 def forward(self,x): return self.head(self.encoder(x)).squeeze(1)
pre=torch.load(ROOT/'data/processed/zenodo_temporal_contrastive_encoder.pt',map_location='cpu',weights_only=False)['encoder']; base=Net(); base.encoder.load_state_dict({k.replace('f.',''):v for k,v in pre.items()},strict=False)
rows=[]
for fold,testp in enumerate(folds):
 tr=~m.participant_key.isin(testp); te=~tr; mean=X[tr].reshape(-1,18).mean(0); std=X[tr].reshape(-1,18).std(0).clip(1e-3); xtr=torch.from_numpy(((X[tr]-mean)/std).transpose(0,2,1).astype('float32')); xte=torch.from_numpy(((X[te]-mean)/std).transpose(0,2,1).astype('float32')); ytr=torch.from_numpy(m.loc[tr,'y'].to_numpy('float32')); yte=m.loc[te,'y'].to_numpy()
 for mode in ('scratch','temporal_contrastive'):
  model=Net().to(device); 
  if mode=='temporal_contrastive': model.encoder.load_state_dict(base.encoder.state_dict())
  opt=torch.optim.AdamW(model.parameters(),lr=1e-3,weight_decay=1e-4); loader=DataLoader(TensorDataset(xtr,ytr),64,shuffle=True); model.train()
  for _ in range(8):
   for xb,yb in loader: xb,yb=xb.to(device),yb.to(device); loss=nn.functional.binary_cross_entropy_with_logits(model(xb),yb); opt.zero_grad(); loss.backward(); opt.step()
  model.eval();
  with torch.no_grad(): p=torch.sigmoid(model(xte.to(device))).cpu().numpy()
  rows.append({'fold':fold,'mode':mode,'participants':len(testp),'auroc':roc_auc_score(yte,p)})
out=ROOT/'data/processed/zenodo_temporal_transfer_binary_comparison.csv'; pd.DataFrame(rows).to_csv(out,index=False); print(pd.DataFrame(rows).groupby('mode').auroc.agg(['mean','std']).to_string()); print('Wrote',out)
