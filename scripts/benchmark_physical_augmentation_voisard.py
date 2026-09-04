"""Held-out Voisard test of predeclared real-signal physical augmentation."""
from pathlib import Path
import numpy as np,pandas as pd,torch
from sklearn.metrics import roc_auc_score,brier_score_loss,balanced_accuracy_score
R=Path(__file__).resolve().parents[1]; P=R/'data/processed'; D=torch.device('cuda' if torch.cuda.is_available() else 'cpu'); torch.manual_seed(42); rng=np.random.default_rng(42)
class Block(torch.nn.Module):
 def __init__(self,ic,oc=16):
  super().__init__(); b=min(32,ic); self.b=torch.nn.Conv1d(ic,b,1,bias=False); self.br=torch.nn.ModuleList([torch.nn.Conv1d(b,oc,k,padding=k//2,bias=False) for k in (7,15,25)]); self.p=torch.nn.Conv1d(ic,oc,1,bias=False); self.bn=torch.nn.BatchNorm1d(oc*4); self.r=torch.nn.Conv1d(ic,oc*4,1,bias=False) if ic!=oc*4 else torch.nn.Identity()
 def forward(self,x): z=self.b(x); return torch.nn.functional.gelu(self.bn(torch.cat([q(z) for q in self.br]+[self.p(torch.nn.functional.max_pool1d(x,3,1,1))],1))+self.r(x))
class Net(torch.nn.Module):
 def __init__(self): super().__init__(); self.f=torch.nn.Sequential(Block(3),torch.nn.MaxPool1d(2),Block(64),torch.nn.AdaptiveAvgPool1d(1)); self.c=torch.nn.Sequential(torch.nn.Flatten(),torch.nn.Dropout(.3),torch.nn.Linear(64,1))
 def forward(self,x): return self.c(self.f(x)).squeeze(1)
X=np.concatenate([np.load(P/'validated_acceleration_magnitude_windows_float32.npy'),np.load(P/'sint_maartenskliniek_external_windows_float32.npy')]); m=pd.concat([pd.read_csv(P/'validated_window_metadata.csv'),pd.read_csv(P/'sint_maartenskliniek_external_window_metadata.csv')],ignore_index=True); k=m.label.isin(['healthy','stroke']).to_numpy(); X=X[k]; m=m[k].reset_index(drop=True); m['y']=(m.label=='stroke').astype(int); tr=m.dataset_id.ne('voisard_2025').to_numpy(); te=~tr; mu=X[tr].reshape(-1,3).mean(0); sd=X[tr].reshape(-1,3).std(0).clip(1e-4); pools=[]
for src in ['felius_2024','sint_maartenskliniek']:
 for cls in [0,1]: pools.append(np.where(tr&m.dataset_id.eq(src).to_numpy()&m.y.eq(cls).to_numpy())[0])
def augment(a):
 gain=rng.uniform(.95,1.05,size=(len(a),1,3)).astype('float32'); z=a*gain+rng.normal(0,.01,size=a.shape).astype('float32'); scale=rng.uniform(.92,1.08,size=len(a)); base=np.arange(500); out=np.empty_like(z)
 for i,s in enumerate(scale): out[i]=np.stack([np.interp(base, np.clip(base/s,0,499), z[i,:,c]) for c in range(3)],1)
 return out
rows=[]
for mode in ['baseline','physical_aug']:
 model=Net().to(D); opt=torch.optim.AdamW(model.parameters(),1e-3,weight_decay=1e-4)
 for ep in range(12):
  model.train()
  for step in range(50):
   ids=np.concatenate([rng.choice(ix,min(32,len(ix)),replace=len(ix)<32) for ix in pools]); a=X[ids]; a=augment(a) if mode=='physical_aug' else a; xb=torch.from_numpy(((a-mu)/sd).transpose(0,2,1).astype('float32')).to(D); yb=torch.from_numpy(m.y.iloc[ids].to_numpy('float32')).to(D); opt.zero_grad(); loss=torch.nn.functional.binary_cross_entropy_with_logits(model(xb),yb); loss.backward(); opt.step()
 model.eval(); z=torch.from_numpy(((X[te]-mu)/sd).transpose(0,2,1).astype('float32'))
 with torch.no_grad(): p=torch.sigmoid(model(z.to(D))).cpu().numpy()
 g=m.loc[te,['participant_key','y']].copy(); g['p']=p; g=g.groupby(['participant_key','y'],as_index=False).p.mean(); rows.append({'mode':mode,'participants':len(g),'auroc':roc_auc_score(g.y,g.p),'brier':brier_score_loss(g.y,g.p),'balanced_accuracy':balanced_accuracy_score(g.y,g.p>=.5),'healthy_false_positives':int(((g.y==0)&(g.p>=.5)).sum())}); g.to_csv(P/f'voisard_heldout_{mode}_predictions.csv',index=False); print(rows[-1],flush=True)
pd.DataFrame(rows).to_csv(P/'physical_augmentation_voisard_metrics.csv',index=False); print(pd.DataFrame(rows).to_string(index=False)); print('device',D)
