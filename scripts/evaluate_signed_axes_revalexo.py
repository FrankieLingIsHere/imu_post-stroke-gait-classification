"""Train participant-disjoint signed-axis models and evaluate frozen RevalExo."""
from pathlib import Path
import numpy as np,pandas as pd,torch
from torch.utils.data import DataLoader,TensorDataset,WeightedRandomSampler
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.metrics import roc_auc_score,brier_score_loss,balanced_accuracy_score
class Block(torch.nn.Module):
 def __init__(self,ic,oc=16):
  super().__init__(); b=min(32,ic); self.b=torch.nn.Conv1d(ic,b,1,bias=False); self.br=torch.nn.ModuleList([torch.nn.Conv1d(b,oc,7,padding=3,bias=False),torch.nn.Conv1d(b,oc,15,padding=7,bias=False),torch.nn.Conv1d(b,oc,25,padding=12,bias=False)]); self.pool=torch.nn.Conv1d(ic,oc,1,bias=False); self.bn=torch.nn.BatchNorm1d(oc*4); self.res=torch.nn.Conv1d(ic,oc*4,1,bias=False)
 def forward(self,x): return torch.nn.functional.gelu(self.bn(torch.cat([v(self.b(x)) for v in self.br]+[self.pool(torch.nn.functional.max_pool1d(x,3,1,1))],1))+self.res(x))
class Net(torch.nn.Module):
 def __init__(self,ic): super().__init__(); self.f=torch.nn.Sequential(Block(ic),torch.nn.MaxPool1d(2),Block(64),torch.nn.AdaptiveAvgPool1d(1)); self.c=torch.nn.Sequential(torch.nn.Flatten(),torch.nn.Dropout(.3),torch.nn.Linear(64,1))
 def forward(self,x): return self.c(self.f(x)).squeeze(1)
R=Path(__file__).resolve().parents[1]; P=R/'data/processed'; D=torch.device('cuda' if torch.cuda.is_available() else 'cpu'); torch.manual_seed(42); np.random.seed(42)
m=pd.read_csv(P/'primary_signed_acceleration_window_metadata.csv'); X=np.load(P/'primary_signed_acceleration_windows_float32.npy'); y=(m.label=='stroke').astype(int).to_numpy(); people=m[['participant_key','label']].drop_duplicates('participant_key'); sg=StratifiedGroupKFold(5,shuffle=True,random_state=42); raw=np.load(P/'revalexo_external_windows_float32.npy'); E=np.concatenate([raw[:,:,0:3],raw[:,:,12:15],raw[:,:,6:9]],axis=2); em=pd.read_csv(P/'revalexo_external_window_metadata.csv'); ey=em.group.map({'HC':0,'ST':1}).to_numpy(); probs=[]
for fold,(tri,vi) in enumerate(sg.split(people,people.label,people.participant_key)):
 trp=set(people.iloc[tri].participant_key); tr=m.participant_key.isin(trp).to_numpy(); va=~tr; mu=X[tr].reshape(-1,9).mean(0); sd=X[tr].reshape(-1,9).std(0).clip(1e-4); xt=torch.from_numpy(((X[tr]-mu)/sd).transpose(0,2,1).astype('float32')); xv=torch.from_numpy(((X[va]-mu)/sd).transpose(0,2,1).astype('float32')); yt=torch.from_numpy(y[tr].astype('float32')); keys=m.loc[tr,['dataset_id','label']].astype(str).agg('|'.join,axis=1); cnt=keys.value_counts(); w=torch.tensor(keys.map(lambda q:1/cnt[q]).to_numpy(),dtype=torch.double); dl=DataLoader(TensorDataset(xt,yt),128,sampler=WeightedRandomSampler(w,len(w),replacement=True)); model=Net(9).to(D); opt=torch.optim.AdamW(model.parameters(),1e-3,weight_decay=1e-4); best=-1; state=None
 for ep in range(12):
  model.train()
  for a,b in dl: opt.zero_grad(); loss=torch.nn.functional.binary_cross_entropy_with_logits(model(a.to(D)),b.to(D)); loss.backward(); opt.step()
  model.eval();
  with torch.no_grad(): pv=torch.sigmoid(model(xv.to(D))).cpu().numpy()
  q=m.loc[va,['participant_key','label']].copy(); q['p']=pv; q=q.groupby(['participant_key','label'],as_index=False).p.mean(); score=roc_auc_score((q.label=='stroke').astype(int),q.p)
  if score>best: best=score; state={k:v.cpu() for k,v in model.state_dict().items()}
 model.load_state_dict(state); model.eval(); ez=torch.from_numpy(((E-mu)/sd).transpose(0,2,1).astype('float32'))
 with torch.no_grad(): probs.append(torch.sigmoid(model(ez.to(D))).cpu().numpy())
 torch.save({'model_state_dict':state,'mean':mu,'std':sd,'fold':fold,'representation':'signed_axes'},P/f'signed_axes_fold_{fold}_seed_42.pt'); print('fold',fold,'selected_participant_auroc',round(best,4),flush=True)
p=np.mean(probs,axis=0); g=em.assign(p=p).groupby(['subject','group'],as_index=False).p.mean(); g['y']=g.group.map({'HC':0,'ST':1}); out={'model':'signed_axes_inception','participants':len(g),'healthy':int((g.y==0).sum()),'stroke':int((g.y==1).sum()),'auroc':roc_auc_score(g.y,g.p),'brier':brier_score_loss(g.y,g.p),'balanced_accuracy':balanced_accuracy_score(g.y,g.p>=.5),'healthy_false_positives':int(((g.y==0)&(g.p>=.5)).sum()),'device':str(D)}; print(out); pd.DataFrame([out]).to_csv(P/'signed_axes_revalexo_metrics.csv',index=False); g.to_csv(P/'signed_axes_revalexo_predictions.csv',index=False)
