"""Matched participant-disjoint ablation: signed 9-axis vs magnitude 3-channel."""
from pathlib import Path
import numpy as np,pandas as pd,torch
from torch.utils.data import DataLoader,TensorDataset,WeightedRandomSampler
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.metrics import roc_auc_score,brier_score_loss,balanced_accuracy_score
R=Path(__file__).resolve().parents[1]; P=R/'data/processed'; D=torch.device('cuda' if torch.cuda.is_available() else 'cpu'); torch.manual_seed(42); np.random.seed(42)
class Block(torch.nn.Module):
 def __init__(self,ic,oc=16):
  super().__init__(); b=min(32,ic); self.b=torch.nn.Conv1d(ic,b,1,bias=False); self.br=torch.nn.ModuleList([torch.nn.Conv1d(b,oc,7,padding=3,bias=False),torch.nn.Conv1d(b,oc,15,padding=7,bias=False),torch.nn.Conv1d(b,oc,25,padding=12,bias=False)]); self.pool=torch.nn.Conv1d(ic,oc,1,bias=False); self.bn=torch.nn.BatchNorm1d(oc*4); self.res=torch.nn.Conv1d(ic,oc*4,1,bias=False)
 def forward(self,x): return torch.nn.functional.gelu(self.bn(torch.cat([v(self.b(x)) for v in self.br]+[self.pool(torch.nn.functional.max_pool1d(x,3,1,1))],1))+self.res(x))
class Net(torch.nn.Module):
 def __init__(self,ic): super().__init__(); self.f=torch.nn.Sequential(Block(ic),torch.nn.MaxPool1d(2),Block(64),torch.nn.AdaptiveAvgPool1d(1)); self.c=torch.nn.Sequential(torch.nn.Flatten(),torch.nn.Dropout(.3),torch.nn.Linear(64,1))
 def forward(self,x): return self.c(self.f(x)).squeeze(1)
m=pd.read_csv(P/'primary_signed_acceleration_window_metadata.csv'); raw=np.load(P/'primary_signed_acceleration_windows_float32.npy'); mag=np.stack([np.linalg.norm(raw[:,:,0:3],axis=2),np.linalg.norm(raw[:,:,3:6],axis=2),np.linalg.norm(raw[:,:,6:9],axis=2)],2); y=(m.label=='stroke').astype(int).to_numpy(); people=m[['participant_key','label']].drop_duplicates('participant_key'); sg=StratifiedGroupKFold(5,shuffle=True,random_state=42); rows=[]
for name,X in [('magnitude',mag),('signed_axes',raw)]:
 for fold,(tri,vi) in enumerate(sg.split(people,people.label,people.participant_key)):
  trp=set(people.iloc[tri].participant_key); tr=m.participant_key.isin(trp).to_numpy(); va=~tr; mu=X[tr].reshape(-1,X.shape[2]).mean(0); sd=X[tr].reshape(-1,X.shape[2]).std(0).clip(1e-4); xt=torch.from_numpy(((X[tr]-mu)/sd).transpose(0,2,1).astype('float32')); xv=torch.from_numpy(((X[va]-mu)/sd).transpose(0,2,1).astype('float32')); yt=torch.from_numpy(y[tr].astype('float32')); keys=m.loc[tr,['dataset_id','label']].astype(str).agg('|'.join,axis=1); cnt=keys.value_counts(); w=torch.tensor(keys.map(lambda q:1/cnt[q]).to_numpy(),dtype=torch.double); dl=DataLoader(TensorDataset(xt,yt),128,sampler=WeightedRandomSampler(w,len(w),replacement=True)); model=Net(X.shape[2]).to(D); opt=torch.optim.AdamW(model.parameters(),1e-3,weight_decay=1e-4); best=-1; bp=None
  for ep in range(12):
   model.train()
   for a,b in dl: opt.zero_grad(); loss=torch.nn.functional.binary_cross_entropy_with_logits(model(a.to(D)),b.to(D)); loss.backward(); opt.step()
   model.eval();
   with torch.no_grad(): p=torch.sigmoid(model(xv.to(D))).cpu().numpy()
   q=m.loc[va,['participant_key','label']].copy(); q['p']=p; q=q.groupby(['participant_key','label'],as_index=False).p.mean(); score=roc_auc_score((q.label=='stroke').astype(int),q.p)
   if score>best: best=score; bp=p.copy()
  q=m.loc[va,['participant_key','label']].copy(); q['p']=bp; q=q.groupby(['participant_key','label'],as_index=False).p.mean(); yy=(q.label=='stroke').astype(int); rows.append({'representation':name,'fold':fold,'participants':len(q),'auroc':roc_auc_score(yy,q.p),'brier':brier_score_loss(yy,q.p),'balanced_accuracy':balanced_accuracy_score(yy,q.p>=.5)}); print(rows[-1],flush=True)
out=pd.DataFrame(rows); out.to_csv(P/'signed_vs_magnitude_metrics.csv',index=False); print(out.groupby('representation')[['auroc','brier','balanced_accuracy']].mean().round(4)); print('device',D)
