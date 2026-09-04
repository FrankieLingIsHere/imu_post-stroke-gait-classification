"""Leave-one-source-out: source-balanced ERM versus group-robust real-data training."""
from pathlib import Path
import numpy as np,pandas as pd,torch
from sklearn.metrics import roc_auc_score,brier_score_loss,balanced_accuracy_score
R=Path(__file__).resolve().parents[1]; P=R/'data/processed'; D=torch.device('cuda' if torch.cuda.is_available() else 'cpu'); torch.manual_seed(42); np.random.seed(42)
class Block(torch.nn.Module):
 def __init__(self,ic,oc=16):
  super().__init__(); b=min(32,ic); self.b=torch.nn.Conv1d(ic,b,1,bias=False); self.br=torch.nn.ModuleList([torch.nn.Conv1d(b,oc,k,padding=k//2,bias=False) for k in (7,15,25)]); self.p=torch.nn.Conv1d(ic,oc,1,bias=False); self.bn=torch.nn.BatchNorm1d(oc*4); self.r=torch.nn.Conv1d(ic,oc*4,1,bias=False) if ic!=oc*4 else torch.nn.Identity()
 def forward(self,x): z=self.b(x); return torch.nn.functional.gelu(self.bn(torch.cat([q(z) for q in self.br]+[self.p(torch.nn.functional.max_pool1d(x,3,1,1))],1))+self.r(x))
class Net(torch.nn.Module):
 def __init__(self): super().__init__(); self.f=torch.nn.Sequential(Block(3),torch.nn.MaxPool1d(2),Block(64),torch.nn.AdaptiveAvgPool1d(1)); self.c=torch.nn.Sequential(torch.nn.Flatten(),torch.nn.Dropout(.3),torch.nn.Linear(64,1))
 def forward(self,x): return self.c(self.f(x)).squeeze(1)
X=np.concatenate([np.load(P/'validated_acceleration_magnitude_windows_float32.npy'),np.load(P/'sint_maartenskliniek_external_windows_float32.npy')]); m=pd.concat([pd.read_csv(P/'validated_window_metadata.csv'),pd.read_csv(P/'sint_maartenskliniek_external_window_metadata.csv')],ignore_index=True); k=m.label.isin(['healthy','stroke']).to_numpy(); X=X[k]; m=m[k].reset_index(drop=True); m['y']=(m.label=='stroke').astype(int); sources=sorted(m.dataset_id.unique()); rng=np.random.default_rng(42); rows=[]
for held in sources:
 tr=m.dataset_id.ne(held).to_numpy(); te=~tr; mu=X[tr].reshape(-1,3).mean(0); sd=X[tr].reshape(-1,3).std(0).clip(1e-4); pools=[]
 for src in sources:
  if src==held: continue
  for cls in [0,1]:
   ix=np.where(tr & m.dataset_id.eq(src).to_numpy() & m.y.eq(cls).to_numpy())[0]
   if len(ix): pools.append((f'{src}|{cls}',ix))
 for mode in ['source_balanced_erm','group_dro']:
  model=Net().to(D); opt=torch.optim.AdamW(model.parameters(),1e-3,weight_decay=1e-4); q=torch.ones(len(pools),device=D)/len(pools)
  for ep in range(12):
   model.train()
   for step in range(50):
    xb=[]; yb=[]; gid=[]
    for gi,(_,ix) in enumerate(pools):
     take=rng.choice(ix,min(32,len(ix)),replace=len(ix)<32); xb.append(X[take]); yb.append(m.y.iloc[take].to_numpy()); gid.extend([gi]*len(take))
    xb=torch.from_numpy(((np.concatenate(xb)-mu)/sd).transpose(0,2,1).astype('float32')).to(D); yb=torch.from_numpy(np.concatenate(yb).astype('float32')).to(D); gid=torch.tensor(gid,device=D); lossvec=torch.nn.functional.binary_cross_entropy_with_logits(model(xb),yb,reduction='none'); gl=torch.stack([lossvec[gid.eq(i)].mean() for i in range(len(pools))])
    if mode=='group_dro':
     with torch.no_grad(): q=q*torch.exp(.1*gl.detach()); q=q/q.sum()
     loss=(q*gl).sum()
    else: loss=gl.mean()
    opt.zero_grad(); loss.backward(); opt.step()
  model.eval(); z=torch.from_numpy(((X[te]-mu)/sd).transpose(0,2,1).astype('float32'))
  with torch.no_grad(): p=torch.sigmoid(model(z.to(D))).cpu().numpy()
  g=m.loc[te,['participant_key','y']].copy(); g['p']=p; g=g.groupby(['participant_key','y'],as_index=False).p.mean(); rows.append({'held_out_source':held,'mode':mode,'participants':len(g),'healthy':int((g.y==0).sum()),'stroke':int((g.y==1).sum()),'auroc':roc_auc_score(g.y,g.p),'brier':brier_score_loss(g.y,g.p),'balanced_accuracy':balanced_accuracy_score(g.y,g.p>=.5),'healthy_false_positives':int(((g.y==0)&(g.p>=.5)).sum())}); print(rows[-1],flush=True)
out=pd.DataFrame(rows); out.to_csv(P/'group_robust_leave_one_source_out_metrics.csv',index=False); print(out.to_string(index=False)); print('device',D)
