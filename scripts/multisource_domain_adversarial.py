"""Balanced binary training plus low-weight gradient-reversal domain penalty."""
from pathlib import Path
import numpy as np,pandas as pd,torch
from torch import nn
from sklearn.metrics import roc_auc_score
R=Path(__file__).resolve().parents[1]; D=torch.device('cuda' if torch.cuda.is_available() else 'cpu')
X=np.load(R/'data/processed/validated_gait_windows_float32.npy'); m=pd.read_csv(R/'data/processed/validated_window_metadata.csv'); keep=m.label.isin(['healthy','stroke']).to_numpy(); X=X[keep]; m=m.loc[keep].reset_index(drop=True); m['y']=(m.label=='stroke').astype(int)
Z=np.load(R/'data/processed/zenodo_stroke_windows_float32.npy'); people=np.array(sorted(m.participant_key.unique())); rng=np.random.default_rng(20260824); rng.shuffle(people); folds=np.array_split(people,3); rows=[]
class GRL(torch.autograd.Function):
 @staticmethod
 def forward(ctx,x,a): ctx.a=a; return x
 @staticmethod
 def backward(ctx,g): return -ctx.a*g,None
class Net(nn.Module):
 def __init__(self):
  super().__init__(); self.f=nn.Sequential(nn.Conv1d(18,64,9,padding=4),nn.BatchNorm1d(64),nn.GELU(),nn.Conv1d(64,128,9,padding=4),nn.BatchNorm1d(128),nn.GELU(),nn.Conv1d(128,128,9,padding=4),nn.GELU(),nn.AdaptiveAvgPool1d(1)); self.cls=nn.Linear(128,1); self.dom=nn.Linear(128,3)
 def feat(self,x): return self.f(x).squeeze(-1)
 def forward(self,x,a=.1):
  h=self.feat(x); return self.cls(h).squeeze(1),self.dom(GRL.apply(h,a))
for fold,testp in enumerate(folds):
 tr=~m.participant_key.isin(testp); te=~tr; mean=X[tr].reshape(-1,18).mean(0); std=X[tr].reshape(-1,18).std(0).clip(1e-3); model=Net().to(D); opt=torch.optim.AdamW(model.parameters(),1e-3,weight_decay=1e-4)
 pools=[]
 for di,(src,arr,q) in enumerate([('felius_2024',X[tr & (m.dataset_id=='felius_2024')],m.loc[tr & (m.dataset_id=='felius_2024'),'y'].to_numpy()),('voisard_2025',X[tr & (m.dataset_id=='voisard_2025')],m.loc[tr & (m.dataset_id=='voisard_2025'),'y'].to_numpy()),('zenodo',Z,np.ones(len(Z),int))]): pools.append((torch.from_numpy(((arr-mean)/std).transpose(0,2,1).astype('float32')),torch.from_numpy(q.astype('float32')),torch.full((len(arr),),di,dtype=torch.long)))
 for _ in range(8):
  model.train()
  for _ in range(30):
   batch=[]
   for x,y,d in pools:
    k=np.random.randint(0,len(x),min(32,len(x))); batch.append((x[k],y[k],d[k]))
   xb=torch.cat([b[0] for b in batch]).to(D); yb=torch.cat([b[1] for b in batch]).to(D); db=torch.cat([b[2] for b in batch]).to(D); logit,dom=model(xb); loss=nn.functional.binary_cross_entropy_with_logits(logit[:64],yb[:64])+0.05*nn.functional.cross_entropy(dom,db); opt.zero_grad(); loss.backward(); opt.step()
 model.eval()
 with torch.no_grad():
  q=te; ex=torch.from_numpy(((X[q]-mean)/std).transpose(0,2,1).astype('float32')); p=torch.sigmoid(model(ex.to(D))[0]).cpu().numpy()
 rows.append({'fold':fold,'auroc':roc_auc_score(m.loc[q,'y'],p),'participants':m.loc[q,'participant_key'].nunique()})
out=R/'data/processed/domain_adversarial_comparison.csv'; result=pd.DataFrame(rows); result.to_csv(out,index=False); print(result.auroc.agg(['mean','std']).to_string()); print('Wrote',out)
