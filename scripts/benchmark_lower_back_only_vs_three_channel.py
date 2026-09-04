from pathlib import Path
import numpy as np, pandas as pd, torch
from torch.utils.data import DataLoader, TensorDataset, WeightedRandomSampler
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.metrics import roc_auc_score, brier_score_loss, balanced_accuracy_score

ROOT=Path(__file__).resolve().parents[1]; P=ROOT/'data/processed'; DEVICE=torch.device('cuda' if torch.cuda.is_available() else 'cpu'); torch.manual_seed(42); np.random.seed(42)
class Block(torch.nn.Module):
 def __init__(self,ic,oc=16):
  super().__init__(); b=min(32,ic); self.b=torch.nn.Conv1d(ic,b,1,bias=False); self.br=torch.nn.ModuleList([torch.nn.Conv1d(b,oc,k,padding=k//2,bias=False) for k in (7,15,25)]); self.pool=torch.nn.Conv1d(ic,oc,1,bias=False); self.bn=torch.nn.BatchNorm1d(oc*4); self.res=torch.nn.Conv1d(ic,oc*4,1,bias=False) if ic!=oc*4 else torch.nn.Identity()
 def forward(self,x):
  z=self.b(x); q=[v(z) for v in self.br]; q.append(self.pool(torch.nn.functional.max_pool1d(x,3,1,1))); return torch.nn.functional.gelu(self.bn(torch.cat(q,1))+self.res(x))
class Net(torch.nn.Module):
 def __init__(self,channels):
  super().__init__(); self.f=torch.nn.Sequential(Block(channels),torch.nn.MaxPool1d(2),Block(64),torch.nn.AdaptiveAvgPool1d(1)); self.c=torch.nn.Sequential(torch.nn.Flatten(),torch.nn.Dropout(.3),torch.nn.Linear(64,1))
 def forward(self,x): return self.c(self.f(x)).squeeze(1)

X=np.concatenate([np.load(P/'validated_acceleration_magnitude_windows_float32.npy'),np.load(P/'sint_maartenskliniek_external_windows_float32.npy')]); m=pd.concat([pd.read_csv(P/'validated_window_metadata.csv'),pd.read_csv(P/'sint_maartenskliniek_external_window_metadata.csv')],ignore_index=True); keep=m.label.isin(['healthy','stroke']).to_numpy(); X=X[keep]; m=m.loc[keep].reset_index(drop=True); m['y']=(m.label=='stroke').astype(int); m['group']=m.participant_key.astype(str); m['source']=m.dataset_id
people=m[['group','y']].drop_duplicates('group'); sg=StratifiedGroupKFold(5,shuffle=True,random_state=42); all_rows=[]
for channels,name in [([0],'lower_back_only'),([0,1,2],'three_channel')]:
 rows=[]
 for fold,(tri,vi) in enumerate(sg.split(people,people.y,people.group)):
  trp=set(people.iloc[tri].group); tr=m.group.isin(trp).to_numpy(); va=~tr; xx=X[:,:,channels]; mean=xx[tr].mean(axis=(0,1)); std=xx[tr].std(axis=(0,1)).clip(1e-4); xt=torch.from_numpy(((xx[tr]-mean)/std).transpose(0,2,1).astype('float32')); xv=torch.from_numpy(((xx[va]-mean)/std).transpose(0,2,1).astype('float32')); yt=torch.from_numpy(m.loc[tr,'y'].to_numpy('float32')); yv=m.loc[va,'y'].to_numpy(); keys=m.loc[tr,['source','y']].astype(str).agg('|'.join,axis=1); counts=keys.value_counts(); weights=torch.tensor(keys.map(lambda z:1/counts[z]).to_numpy(),dtype=torch.double); dl=DataLoader(TensorDataset(xt,yt),128,sampler=WeightedRandomSampler(weights,len(weights),replacement=True)); model=Net(len(channels)).to(DEVICE); opt=torch.optim.AdamW(model.parameters(),1e-3,weight_decay=1e-4); best=-1; bestp=None
  for epoch in range(12):
   model.train()
   for a,b in dl: opt.zero_grad(); loss=torch.nn.functional.binary_cross_entropy_with_logits(model(a.to(DEVICE)),b.to(DEVICE)); loss.backward(); opt.step()
   model.eval()
   with torch.no_grad(): p=torch.sigmoid(model(xv.to(DEVICE))).cpu().numpy()
   score=roc_auc_score(yv,p)
   if score>best: best=score; bestp=p.copy()
  g=m.loc[va,['group','y']].copy(); g['p']=bestp; g=g.groupby(['group','y'],as_index=False).p.mean(); row={'model':name,'fold':fold,'participants':len(g),'auroc':roc_auc_score(g.y,g.p),'brier':brier_score_loss(g.y,g.p),'balanced_accuracy':balanced_accuracy_score(g.y,g.p>=.5)}; rows.append(row); all_rows.append(row); print(row,flush=True)
 pd.DataFrame(rows).to_csv(P/f'{name}_matched_internal_metrics.csv',index=False)
pd.DataFrame(all_rows).to_csv(P/'lower_back_vs_three_channel_matched_metrics.csv',index=False)
print(pd.DataFrame(all_rows).groupby('model')[['auroc','brier','balanced_accuracy']].mean())
