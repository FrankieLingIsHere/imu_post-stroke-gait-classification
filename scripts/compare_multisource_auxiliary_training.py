"""Compare binary baseline, Zenodo auxiliary loss, and source-specific heads."""
from pathlib import Path
import numpy as np,pandas as pd,torch
from torch import nn
from torch.utils.data import DataLoader,TensorDataset
from sklearn.metrics import roc_auc_score
R=Path(__file__).resolve().parents[1]; D=torch.device('cuda' if torch.cuda.is_available() else 'cpu')
X=np.load(R/'data/processed/validated_gait_windows_float32.npy'); m=pd.read_csv(R/'data/processed/validated_window_metadata.csv'); keep=m.label.isin(['healthy','stroke']).to_numpy(); X=X[keep]; m=m.loc[keep].reset_index(drop=True); m['y']=(m.label=='stroke').astype(int); m['source']=m.dataset_id
Z=np.load(R/'data/processed/zenodo_stroke_windows_float32.npy'); zm=pd.read_csv(R/'data/processed/zenodo_stroke_window_metadata.csv'); Zm=zm.copy(); Zm['y']=1; Zm['source']='zenodo'
people=np.array(sorted(m.participant_key.unique())); rng=np.random.default_rng(20260824); rng.shuffle(people); folds=np.array_split(people,3)
class Net(nn.Module):
 def __init__(self,heads=False):
  super().__init__(); self.f=nn.Sequential(nn.Conv1d(18,64,9,padding=4),nn.BatchNorm1d(64),nn.GELU(),nn.Conv1d(64,128,9,padding=4),nn.BatchNorm1d(128),nn.GELU(),nn.Conv1d(128,128,9,padding=4),nn.GELU(),nn.AdaptiveAvgPool1d(1)); self.h=nn.ModuleDict({'felius_2024':nn.Linear(128,1),'voisard_2025':nn.Linear(128,1),'zenodo':nn.Linear(128,1)}) if heads else nn.ModuleDict({'all':nn.Linear(128,1)}); self.heads=heads
 def forward(self,x,src='all'): return self.h[src if self.heads else 'all'](self.f(x).squeeze(-1)).squeeze(1)
rows=[]
for fold,testp in enumerate(folds):
 tr=~m.participant_key.isin(testp); te=~tr; mean=X[tr].reshape(-1,18).mean(0); std=X[tr].reshape(-1,18).std(0).clip(1e-3); tx=torch.from_numpy(((X[tr]-mean)/std).transpose(0,2,1).astype('float32')); ty=torch.from_numpy(m.loc[tr,'y'].to_numpy('float32')); sx=torch.from_numpy(((Z-mean)/std).transpose(0,2,1).astype('float32')); sy=torch.ones(len(Z)); ex=torch.from_numpy(((X[te]-mean)/std).transpose(0,2,1).astype('float32')); ey=m.loc[te,'y'].to_numpy();
 for mode in ('binary_baseline','zenodo_auxiliary'):
  model=Net(False).to(D); opt=torch.optim.AdamW(model.parameters(),1e-3,weight_decay=1e-4); loader=DataLoader(TensorDataset(tx,ty),64,shuffle=True)
  for _ in range(5):
   model.train()
   for xb,yb in loader:
    xb,yb=xb.to(D),yb.to(D); loss=nn.functional.binary_cross_entropy_with_logits(model(xb),yb)
    if mode=='zenodo_auxiliary':
     k=np.random.randint(0,len(sx),min(64,len(sx))); loss=loss+0.25*nn.functional.binary_cross_entropy_with_logits(model(sx[k].to(D)),sy[k].to(D))
    opt.zero_grad(); loss.backward(); opt.step()
  model.eval();
  with torch.no_grad(): p=torch.sigmoid(model(ex.to(D))).cpu().numpy()
  rows.append({'fold':fold,'mode':mode,'auroc':roc_auc_score(ey,p),'test_participants':len(testp)})
out=R/'data/processed/multisource_auxiliary_training_comparison.csv'; pd.DataFrame(rows).to_csv(out,index=False); print(pd.DataFrame(rows).groupby('mode').auroc.agg(['mean','std']).to_string()); print('Wrote',out)
