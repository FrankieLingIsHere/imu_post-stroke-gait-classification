"""Shared encoder with source-specific binary heads and a Zenodo domain head."""
from pathlib import Path
import numpy as np,pandas as pd,torch
from torch import nn
from sklearn.metrics import roc_auc_score
R=Path(__file__).resolve().parents[1]; D=torch.device('cuda' if torch.cuda.is_available() else 'cpu')
X=np.load(R/'data/processed/validated_gait_windows_float32.npy'); m=pd.read_csv(R/'data/processed/validated_window_metadata.csv'); keep=m.label.isin(['healthy','stroke']).to_numpy(); X=X[keep]; m=m.loc[keep].reset_index(drop=True); m['y']=(m.label=='stroke').astype(int)
Z=np.load(R/'data/processed/zenodo_stroke_windows_float32.npy'); people=np.array(sorted(m.participant_key.unique())); rng=np.random.default_rng(20260824); rng.shuffle(people); folds=np.array_split(people,3); rows=[]
class Net(nn.Module):
 def __init__(self):
  super().__init__(); self.f=nn.Sequential(nn.Conv1d(18,64,9,padding=4),nn.BatchNorm1d(64),nn.GELU(),nn.Conv1d(64,128,9,padding=4),nn.BatchNorm1d(128),nn.GELU(),nn.Conv1d(128,128,9,padding=4),nn.GELU(),nn.AdaptiveAvgPool1d(1)); self.h=nn.ModuleDict({'felius_2024':nn.Linear(128,1),'voisard_2025':nn.Linear(128,1)}); self.domain=nn.Linear(128,3)
 def feat(self,x): return self.f(x).squeeze(-1)
 def forward(self,x,source): return self.h[source](self.feat(x)).squeeze(1)
for fold,testp in enumerate(folds):
 tr=~m.participant_key.isin(testp); te=~tr; mean=X[tr].reshape(-1,18).mean(0); std=X[tr].reshape(-1,18).std(0).clip(1e-3); model=Net().to(D); opt=torch.optim.AdamW(model.parameters(),1e-3,weight_decay=1e-4); blocks=[]
 for src in ('felius_2024','voisard_2025'):
  q=tr & (m.dataset_id==src); blocks.append((torch.from_numpy(((X[q]-mean)/std).transpose(0,2,1).astype('float32')),torch.from_numpy(m.loc[q,'y'].to_numpy('float32')),src))
 zn=torch.from_numpy(((Z-mean)/std).transpose(0,2,1).astype('float32')); zy=torch.full((len(Z),),2,dtype=torch.long)
 for _ in range(5):
  model.train()
  for xb,yb,src in blocks:
   for i in range(0,len(xb),64):
    a,b=xb[i:i+64].to(D),yb[i:i+64].to(D); loss=nn.functional.binary_cross_entropy_with_logits(model(a,src),b); k=np.random.randint(0,len(zn),min(64,len(zn))); loss=loss+0.05*nn.functional.cross_entropy(model.domain(model.feat(zn[k].to(D))),zy[k].to(D)); opt.zero_grad(); loss.backward(); opt.step()
 model.eval()
 for src in ('felius_2024','voisard_2025'):
  q=te & (m.dataset_id==src); ex=torch.from_numpy(((X[q]-mean)/std).transpose(0,2,1).astype('float32')); ey=m.loc[q,'y'].to_numpy()
  with torch.no_grad(): p=torch.sigmoid(model(ex.to(D),src)).cpu().numpy()
  rows.append({'fold':fold,'source':src,'auroc':roc_auc_score(ey,p),'participants':m.loc[q,'participant_key'].nunique()})
out=R/'data/processed/source_specific_heads_comparison.csv'; result=pd.DataFrame(rows); result.to_csv(out,index=False); print(result.groupby('source').auroc.agg(['mean','std']).to_string()); print('Wrote',out)
