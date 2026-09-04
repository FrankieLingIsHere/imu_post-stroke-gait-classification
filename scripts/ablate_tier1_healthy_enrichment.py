from pathlib import Path
import os
import numpy as np,pandas as pd,torch
from torch.utils.data import DataLoader,TensorDataset,WeightedRandomSampler
from sklearn.metrics import roc_auc_score,brier_score_loss,balanced_accuracy_score
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/'data/processed'; D=torch.device('cuda' if torch.cuda.is_available() else 'cpu'); torch.manual_seed(42); np.random.seed(42)
class Block(torch.nn.Module):
 def __init__(self,ic,oc=16):
  super().__init__(); b=min(32,ic); self.b=torch.nn.Conv1d(ic,b,1,bias=False); self.br=torch.nn.ModuleList([torch.nn.Conv1d(b,oc,k,padding=k//2,bias=False) for k in (7,15,25)]); self.pool=torch.nn.Conv1d(ic,oc,1,bias=False); self.bn=torch.nn.BatchNorm1d(oc*4); self.res=torch.nn.Conv1d(ic,oc*4,1,bias=False) if ic!=oc*4 else torch.nn.Identity()
 def forward(self,x):
  z=self.b(x); q=[v(z) for v in self.br]; q.append(self.pool(torch.nn.functional.max_pool1d(x,3,1,1))); return torch.nn.functional.gelu(self.bn(torch.cat(q,1))+self.res(x))
class Net(torch.nn.Module):
 def __init__(self):
  super().__init__(); self.f=torch.nn.Sequential(Block(3),torch.nn.MaxPool1d(2),Block(64),torch.nn.AdaptiveAvgPool1d(1)); self.c=torch.nn.Sequential(torch.nn.Flatten(),torch.nn.Dropout(.3),torch.nn.Linear(64,1))
 def forward(self,x): return self.c(self.f(x)).squeeze(1)
base=np.concatenate([np.load(P/'validated_acceleration_magnitude_windows_float32.npy'),np.load(P/'sint_maartenskliniek_external_windows_float32.npy')]); bm=pd.concat([pd.read_csv(P/'validated_window_metadata.csv'),pd.read_csv(P/'sint_maartenskliniek_external_window_metadata.csv')],ignore_index=True); keep=bm.label.isin(['healthy','stroke']).to_numpy(); base=base[keep]; bm=bm.loc[keep].reset_index(drop=True); bm['y']=(bm.label=='stroke').astype(int); bm['source']=bm.dataset_id; bm['group']=bm.participant_key.astype(str)
extra_file=os.getenv('EXTRA_HEALTHY_FILE','tier1_healthy_marea_duogait_windows_float32.npy'); extra=np.load(P/extra_file); em=pd.read_csv(P/(os.getenv('EXTRA_HEALTHY_META','tier1_healthy_marea_duogait_window_metadata.csv'))); em['y']=0; em['source']=em.dataset_id; em['group']=em.participant_key.astype(str)
raw=np.load(P/'revalexo_external_windows_float32.npy'); ex=np.stack([np.linalg.norm(raw[:,:,0:3],axis=2),np.linalg.norm(raw[:,:,12:15],axis=2),np.linalg.norm(raw[:,:,6:9],axis=2)],2).astype('float32'); xm=pd.read_csv(P/'revalexo_external_window_metadata.csv'); xm['y']=xm.group.map({'HC':0,'ST':1})
rows=[]
for mode in ('baseline','tier1_healthy_enriched'):
 X=base; m=bm
 if mode!='baseline': X=np.concatenate([base,extra]); m=pd.concat([bm,em],ignore_index=True)
 mean=X.mean((0,1)); std=X.std((0,1)).clip(1e-4); z=torch.from_numpy(((X-mean)/std).transpose(0,2,1).astype('float32')); y=torch.from_numpy(m.y.to_numpy('float32')); keys=m.source.astype(str)+'|'+m.y.astype(str); counts=keys.value_counts(); w=torch.tensor(keys.map(lambda q:1/counts[q]).to_numpy(),dtype=torch.double); dl=DataLoader(TensorDataset(z,y),128,sampler=WeightedRandomSampler(w,len(w),replacement=True)); model=Net().to(D); opt=torch.optim.AdamW(model.parameters(),1e-3,weight_decay=1e-4)
 for epoch in range(15):
  model.train(); losses=[]
  for a,b in dl: opt.zero_grad(); loss=torch.nn.functional.binary_cross_entropy_with_logits(model(a.to(D)),b.to(D)); loss.backward(); opt.step(); losses.append(loss.item())
  print(mode,epoch+1,float(np.mean(losses)),flush=True)
 model.eval(); ez=torch.from_numpy(((ex-mean)/std).transpose(0,2,1).astype('float32'))
 with torch.no_grad(): p=torch.sigmoid(model(ez.to(D))).cpu().numpy()
 g=xm.assign(prob=p).groupby(['subject','y'],as_index=False).prob.mean(); yy=g.y.to_numpy(); pp=g.prob.to_numpy(); result={'mode':mode,'training_participants':int(m.group.nunique()),'training_windows':len(m),'external_participants':len(g),'auroc':roc_auc_score(yy,pp),'brier':brier_score_loss(yy,pp),'balanced_accuracy':balanced_accuracy_score(yy,pp>=.5)}; rows.append(result); g.to_csv(P/f'{mode}_revalexo_participant_predictions.csv',index=False)
out_name=os.getenv('ABLATION_OUT','tier1_healthy_enrichment_ablation_metrics.csv'); pd.DataFrame(rows).to_csv(P/out_name,index=False); print(pd.DataFrame(rows).to_string(index=False))
