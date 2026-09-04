"""Controlled fold-fitted normalization benchmark for the two project tracks."""
from pathlib import Path
import os
import numpy as np, pandas as pd, torch
from sklearn.model_selection import GroupKFold
from sklearn.metrics import roc_auc_score, balanced_accuracy_score, brier_score_loss
from torch.utils.data import DataLoader, TensorDataset, WeightedRandomSampler

ROOT=Path(__file__).resolve().parents[1]; P=ROOT/'data'/'processed'; SEED=int(os.getenv('NORM_SEED','42')); AUGMENT=os.getenv('NORM_AUGMENT','0')=='1'; OUT=P/(f'normalization_variant_benchmark_seed_{SEED}'+('_augmented' if AUGMENT else '')+'.csv')
DEVICE=torch.device('cuda' if torch.cuda.is_available() else 'cpu'); torch.manual_seed(SEED); np.random.seed(SEED)
class Block(torch.nn.Module):
 def __init__(self,ic,oc=16):
  super().__init__(); b=min(32,ic); self.b=torch.nn.Conv1d(ic,b,1,bias=False); self.br=torch.nn.ModuleList([torch.nn.Conv1d(b,oc,k,padding=k//2,bias=False) for k in (7,15,25)]); self.pool=torch.nn.Conv1d(ic,oc,1,bias=False); self.bn=torch.nn.BatchNorm1d(oc*4); self.res=torch.nn.Conv1d(ic,oc*4,1,bias=False) if ic!=oc*4 else torch.nn.Identity()
 def forward(self,x):
  z=self.b(x); q=[v(z) for v in self.br]; q.append(self.pool(torch.nn.functional.max_pool1d(x,3,1,1))); return torch.nn.functional.gelu(self.bn(torch.cat(q,1))+self.res(x))
class Net(torch.nn.Module):
 def __init__(self,c):
  super().__init__(); self.f=torch.nn.Sequential(Block(c),torch.nn.MaxPool1d(2),Block(64),torch.nn.AdaptiveAvgPool1d(1)); self.c=torch.nn.Sequential(torch.nn.Flatten(),torch.nn.Dropout(.3),torch.nn.Linear(64,1))
 def forward(self,x): return self.c(self.f(x)).squeeze(1)
X=np.load(P/'validated_acceleration_magnitude_windows_float32.npy'); m=pd.read_csv(P/'validated_window_metadata.csv'); keep=m.label.isin(['healthy','stroke']).to_numpy(); X=X[keep]; m=m.loc[keep].reset_index(drop=True); y=(m.label=='stroke').astype(int).to_numpy(); groups=m.participant_key.astype(str).to_numpy(); source=m.dataset_id.astype(str).to_numpy()
raw=np.load(P/'revalexo_external_windows_float32.npy'); E=np.stack([np.linalg.norm(raw[:,:,0:3],axis=2),np.linalg.norm(raw[:,:,12:15],axis=2),np.linalg.norm(raw[:,:,6:9],axis=2)],2).astype('float32'); em=pd.read_csv(P/'revalexo_external_window_metadata.csv'); ey=em.group.map({'HC':0,'ST':1}).to_numpy(); eg=em.subject.astype(str).to_numpy()
rows=[]
for track,idx in [('lower_back',[0]),('three_channel',[0,1,2])]:
 for norm in ['global_zscore','global_robust']:
  for fold,(tr,va) in enumerate(GroupKFold(5).split(X,y,groups)):
   a=X[:,:,idx]; e=E[:,:,idx]; train=a[tr];
   if norm=='global_zscore': center=train.mean((0,1)); scale=train.std((0,1)).clip(1e-4)
   else: center=np.median(train,(0,1)); scale=np.subtract(*np.percentile(train,[75,25],axis=(0,1))).clip(1e-4)
   z=torch.from_numpy(((a-center)/scale).transpose(0,2,1).astype('float32')); ez=torch.from_numpy(((e-center)/scale).transpose(0,2,1).astype('float32'))
   yt=torch.from_numpy(y[tr].astype('float32')); keys=pd.Series(source[tr])+'|'+pd.Series(y[tr]).astype(str); cnt=keys.value_counts(); w=torch.tensor(keys.map(lambda q:1/cnt[q]).to_numpy(),dtype=torch.double); dl=DataLoader(TensorDataset(z[tr],yt),128,sampler=WeightedRandomSampler(w,len(w),replacement=True))
   net=Net(len(idx)).to(DEVICE); opt=torch.optim.AdamW(net.parameters(),1e-3,weight_decay=1e-4)
   for _ in range(8):
    net.train()
    for xx,yy in dl:
     xx=xx.to(DEVICE)
     if AUGMENT:
      gain=torch.empty((xx.shape[0],xx.shape[1],1),device=DEVICE).uniform_(.90,1.10)
      xx=xx*gain + torch.randn_like(xx)*.015
      shift=int(torch.randint(-8,9,(1,)).item()); xx=torch.roll(xx,shift,dims=-1)
     opt.zero_grad(); loss=torch.nn.functional.binary_cross_entropy_with_logits(net(xx),yy.to(DEVICE)); loss.backward(); opt.step()
   net.eval();
   with torch.no_grad(): pv=torch.sigmoid(net(z[va].to(DEVICE))).cpu().numpy(); pe=torch.sigmoid(net(ez.to(DEVICE))).cpu().numpy()
   # Window metrics are diagnostic; participant aggregation is primary.
   vp=pd.DataFrame({'g':groups[va],'y':y[va],'p':pv}).groupby('g').agg(y=('y','first'),p=('p','mean')); ep=pd.DataFrame({'g':eg,'y':ey,'p':pe}).groupby('g').agg(y=('y','first'),p=('p','mean'))
   for split,df in [('internal',vp),('revalexo',ep)]: rows.append({'track':track,'normalization':norm,'fold':fold,'split':split,'participants':len(df),'auroc':roc_auc_score(df.y,df.p),'balanced_accuracy':balanced_accuracy_score(df.y,df.p>=.5),'brier':brier_score_loss(df.y,df.p),'healthy_false_positives':int(((df.y==0)&(df.p>=.5)).sum()),'stroke_false_negatives':int(((df.y==1)&(df.p<.5)).sum())})
pd.DataFrame(rows).to_csv(OUT,index=False); print(pd.DataFrame(rows).groupby(['track','normalization','split']).agg({'auroc':'mean','balanced_accuracy':'mean','brier':'mean','healthy_false_positives':'mean','stroke_false_negatives':'mean'}).round(4)); print('device',DEVICE,'wrote',OUT)
