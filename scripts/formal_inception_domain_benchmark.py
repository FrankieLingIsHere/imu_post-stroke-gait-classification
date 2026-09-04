"""Matched compact formal benchmark: Inception baseline vs Zenodo domain penalty."""
from pathlib import Path
import numpy as np,pandas as pd,torch
from torch import nn
from sklearn.metrics import roc_auc_score
R=Path(__file__).resolve().parents[1]; D=torch.device('cuda' if torch.cuda.is_available() else 'cpu')
X=np.load(R/'data/processed/validated_acceleration_magnitude_windows_float32.npy'); m=pd.read_csv(R/'data/processed/validated_window_metadata.csv'); keep=m.label.isin(['healthy','stroke']).to_numpy(); X=X[keep]; m=m.loc[keep].reset_index(drop=True); m['y']=(m.label=='stroke').astype(int)
Z=np.load(R/'data/processed/zenodo_benchmark_acceleration_magnitude_windows_float32.npy'); splits=pd.read_csv(R/'data/interim/participant_splits.csv'); rows=[]
class B(nn.Module):
 def __init__(self,i,o=16):
  super().__init__(); self.b=nn.Conv1d(i,min(32,i),1,bias=False); self.br=nn.ModuleList([nn.Conv1d(min(32,i),o,k,padding=k//2,bias=False) for k in (7,15,25)]); self.p=nn.Conv1d(i,o,1,bias=False); self.bn=nn.BatchNorm1d(o*4); self.r=nn.Conv1d(i,o*4,1,bias=False) if i!=o*4 else nn.Identity()
 def forward(self,x): return nn.functional.gelu(self.bn(torch.cat([q(self.b(x)) for q in self.br]+[self.p(nn.functional.max_pool1d(x,3,1,1))],1))+self.r(x))
class N(nn.Module):
 def __init__(self,da=False):
  super().__init__(); self.f=nn.Sequential(B(3),nn.MaxPool1d(2),B(64),nn.AdaptiveAvgPool1d(1)); self.c=nn.Linear(64,1); self.d=nn.Linear(64,3); self.da=da
 def forward(self,x):
  h=self.f(x).squeeze(-1); return self.c(h).squeeze(1),self.d(h)
for fi in sorted(splits.fold.unique()):
 roles=splits[splits.fold.eq(fi)].set_index('participant_key').role; tr=m.participant_key.map(roles).eq('training').to_numpy(); te=m.participant_key.map(roles).eq('validation').to_numpy(); mu=X[tr].reshape(-1,3).mean(0); sd=X[tr].reshape(-1,3).std(0).clip(1e-3); a=torch.from_numpy(((X[tr]-mu)/sd).transpose(0,2,1).astype('float32')); y=torch.from_numpy(m.loc[tr,'y'].to_numpy('float32')); e=torch.from_numpy(((X[te]-mu)/sd).transpose(0,2,1).astype('float32')); ey=m.loc[te,'y'].to_numpy(); z=torch.from_numpy(((Z-mu)/sd).transpose(0,2,1).astype('float32'))
 for mode in ('baseline','domain_adversarial'):
  model=N().to(D); opt=torch.optim.AdamW(model.parameters(),1e-3,weight_decay=1e-4)
  for ep in range(4):
   model.train()
   for i in range(0,len(a),64):
    xb,yb=a[i:i+64].to(D),y[i:i+64].to(D); logit,dom=model(xb); loss=nn.functional.binary_cross_entropy_with_logits(logit,yb)
    if mode=='domain_adversarial':
     k=np.random.randint(0,len(z),min(64,len(z))); _,zd=model(z[k].to(D)); labels=torch.cat([torch.zeros(len(xb),dtype=torch.long),torch.full((len(k),),2,dtype=torch.long)]).to(D); loss=loss+0.03*nn.functional.cross_entropy(torch.cat([dom,zd]),labels)
    opt.zero_grad(); loss.backward(); opt.step()
  model.eval();
  with torch.no_grad(): p=torch.sigmoid(model(e.to(D))[0]).cpu().numpy()
  rows.append({'fold':fi,'mode':mode,'auroc':roc_auc_score(ey,p),'participants':m.loc[te,'participant_key'].nunique()})
out=R/'data/processed/formal_inception_domain_benchmark.csv'; r=pd.DataFrame(rows); r.to_csv(out,index=False); print(r.groupby('mode').auroc.agg(['mean','std']).to_string()); print('Wrote',out)
