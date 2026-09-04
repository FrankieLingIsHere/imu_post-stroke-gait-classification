"""Select synthetic healthy ratio by participant-disjoint internal validation only."""
from pathlib import Path
import os
import numpy as np,pandas as pd,torch
from torch.utils.data import DataLoader,TensorDataset,WeightedRandomSampler
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.metrics import roc_auc_score,brier_score_loss,balanced_accuracy_score
R=Path(__file__).resolve().parents[1]; P=R/'data/processed'; D=torch.device('cuda' if torch.cuda.is_available() else 'cpu'); SEED=int(os.getenv('RUN_SEED','42')); torch.manual_seed(SEED); np.random.seed(SEED)
class Block(torch.nn.Module):
 def __init__(self,ic,oc=16):
  super().__init__(); b=min(32,ic); self.b=torch.nn.Conv1d(ic,b,1,bias=False); self.br=torch.nn.ModuleList([torch.nn.Conv1d(b,oc,k,padding=k//2,bias=False) for k in (7,15,25)]); self.pool=torch.nn.Conv1d(ic,oc,1,bias=False); self.bn=torch.nn.BatchNorm1d(oc*4); self.res=torch.nn.Conv1d(ic,oc*4,1,bias=False) if ic!=oc*4 else torch.nn.Identity()
 def forward(self,x): z=self.b(x); return torch.nn.functional.gelu(self.bn(torch.cat([v(z) for v in self.br]+[self.pool(torch.nn.functional.max_pool1d(x,3,1,1))],1))+self.res(x))
class Net(torch.nn.Module):
 def __init__(self): super().__init__(); self.f=torch.nn.Sequential(Block(3),torch.nn.MaxPool1d(2),Block(64),torch.nn.AdaptiveAvgPool1d(1)); self.c=torch.nn.Sequential(torch.nn.Flatten(),torch.nn.Dropout(.3),torch.nn.Linear(64,1))
 def forward(self,x): return self.c(self.f(x)).squeeze(1)
X=np.load(P/'validated_acceleration_magnitude_windows_float32.npy'); m=pd.read_csv(P/'validated_window_metadata.csv'); k=m.label.isin(['healthy','stroke']).to_numpy(); X=X[k]; m=m[k].reset_index(drop=True); y=(m.label=='stroke').astype(int).to_numpy(); S=np.load(P/'healthy_window_diffusion_synthetic_500x3_float32.npy'); sm=pd.read_csv(P/'healthy_window_diffusion_synthetic_metadata.csv'); people=m[['participant_key','label']].drop_duplicates('participant_key'); sg=StratifiedGroupKFold(5,shuffle=True,random_state=SEED); rng=np.random.default_rng(SEED); rows=[]
for ratio in [float(v) for v in os.getenv('RATIOS','0,0.05,0.1,0.2').split(',')]:
 for fold,(tri,vi) in enumerate(sg.split(people,people.label,people.participant_key)):
  trp=set(people.iloc[tri].participant_key); tr=m.participant_key.isin(trp).to_numpy(); va=~tr; xr=X[tr]; mr=m.loc[tr].reset_index(drop=True); n=int(round(ratio*len(xr))); si=np.array([],int) if n==0 else np.concatenate([rng.choice(np.where(sm.dataset_condition.eq(src))[0],n//2+(i<n%2),replace=False) for i,src in enumerate(['marea_2017','duogait_2023'])]); xs=S[si] if n else np.empty((0,500,3),dtype='float32'); ms=sm.iloc[si].reset_index(drop=True).copy() if n else pd.DataFrame(columns=['dataset_condition']); ms['dataset_id']='synthetic_'+ms.get('dataset_condition',pd.Series(dtype=str)); ms['label']='healthy'; xx=np.concatenate([xr,xs]); yy=np.concatenate([y[tr],np.zeros(n,int)]); mu=xr.mean((0,1)); sd=xr.std((0,1)).clip(1e-4); z=torch.from_numpy(((xx-mu)/sd).transpose(0,2,1).astype('float32')); cell=(mr.dataset_id.astype(str)+'|'+mr.label.astype(str)).tolist()+(['synthetic_'+str(v)+'|healthy' for v in ms.dataset_condition] if n else []); target={c:(1-ratio)/4 for c in set(mr.dataset_id.astype(str)+'|'+mr.label.astype(str))}; target.update({'synthetic_marea_2017|healthy':ratio/2,'synthetic_duogait_2023|healthy':ratio/2}); cnt=pd.Series(cell).value_counts(); w=torch.tensor([target[c]/cnt[c] for c in cell],dtype=torch.double); dl=DataLoader(TensorDataset(z,torch.from_numpy(yy.astype('float32'))),128,sampler=WeightedRandomSampler(w,len(z),replacement=True)); model=Net().to(D); opt=torch.optim.AdamW(model.parameters(),1e-3,weight_decay=1e-4); best=-1; bestp=None
  xv=torch.from_numpy(((X[va]-mu)/sd).transpose(0,2,1).astype('float32'))
  for ep in range(10):
   model.train()
   for a,b in dl: opt.zero_grad(); loss=torch.nn.functional.binary_cross_entropy_with_logits(model(a.to(D)),b.to(D)); loss.backward(); opt.step()
   model.eval()
   with torch.no_grad(): p=torch.sigmoid(model(xv.to(D))).cpu().numpy()
   q=m.loc[va,['participant_key','label']].copy(); q['p']=p; q=q.groupby(['participant_key','label'],as_index=False).p.mean(); score=roc_auc_score((q.label=='stroke').astype(int),q.p)
   if score>best: best=score; bestp=q
  q=bestp; yyv=(q.label=='stroke').astype(int); rows.append({'seed':SEED,'ratio':ratio,'fold':fold,'participants':len(q),'synthetic_windows':n,'auroc':roc_auc_score(yyv,q.p),'brier':brier_score_loss(yyv,q.p),'balanced_accuracy':balanced_accuracy_score(yyv,q.p>=.5)}); print(rows[-1],flush=True)
out=pd.DataFrame(rows); out.to_csv(P/f'native_synthetic_ratio_internal_metrics_seed_{SEED}.csv',index=False); print(out.groupby('ratio')[['auroc','brier','balanced_accuracy']].mean().round(4)); print('device',D)
