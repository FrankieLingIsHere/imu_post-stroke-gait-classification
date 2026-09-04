"""Sensitivity training: Felius + Voisard + Sint, participant-disjoint and source-balanced."""
from pathlib import Path
import numpy as np, pandas as pd, torch
from torch.utils.data import DataLoader, TensorDataset, WeightedRandomSampler
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.metrics import roc_auc_score, balanced_accuracy_score, brier_score_loss

R=Path(__file__).resolve().parents[1]; P=R/'data/processed'; D=torch.device('cuda' if torch.cuda.is_available() else 'cpu'); torch.manual_seed(42); np.random.seed(42)

class Block(torch.nn.Module):
 def __init__(self,ic,oc=16):
  super().__init__(); b=min(32,ic); self.b=torch.nn.Conv1d(ic,b,1,bias=False); self.br=torch.nn.ModuleList([torch.nn.Conv1d(b,oc,7,padding=3,bias=False),torch.nn.Conv1d(b,oc,15,padding=7,bias=False),torch.nn.Conv1d(b,oc,25,padding=12,bias=False)]); self.pool=torch.nn.Conv1d(ic,oc,1,bias=False); self.bn=torch.nn.BatchNorm1d(oc*4); self.res=torch.nn.Conv1d(ic,oc*4,1,bias=False) if ic!=oc*4 else torch.nn.Identity()
 def forward(self,x):
  z=self.b(x); q=[v(z) for v in self.br]; q.append(self.pool(torch.nn.functional.max_pool1d(x,3,1,1))); return torch.nn.functional.gelu(self.bn(torch.cat(q,1))+self.res(x))
class Net(torch.nn.Module):
 def __init__(self):
  super().__init__(); self.f=torch.nn.Sequential(Block(3),torch.nn.MaxPool1d(2),Block(64),torch.nn.AdaptiveAvgPool1d(1)); self.c=torch.nn.Sequential(torch.nn.Flatten(),torch.nn.Dropout(.3),torch.nn.Linear(64,1))
 def forward(self,x): return self.c(self.f(x)).squeeze(1)

def main():
 X=np.concatenate([np.load(P/'validated_acceleration_magnitude_windows_float32.npy'),np.load(P/'sint_maartenskliniek_external_windows_float32.npy')]); m=pd.concat([pd.read_csv(P/'validated_window_metadata.csv'),pd.read_csv(P/'sint_maartenskliniek_external_window_metadata.csv')],ignore_index=True); keep=m.label.isin(['healthy','stroke']).to_numpy(); X=X[keep]; m=m.loc[keep].reset_index(drop=True); m['label_binary']=(m.label=='stroke').astype(int); m['source']=m.dataset_id; m['group']=m.participant_key.astype(str); y=m.label_binary.to_numpy(int)
 people=m[['group','label_binary']].drop_duplicates('group'); sg=StratifiedGroupKFold(5,shuffle=True,random_state=42); rows=[]
 for fold,(tri,vi) in enumerate(sg.split(people,people.label_binary,people.group)):
  trp=set(people.iloc[tri].group); vap=set(people.iloc[vi].group); tr=m.group.isin(trp).to_numpy(); va=~tr
  mean=X[tr].reshape(-1,3).mean(0); std=X[tr].reshape(-1,3).std(0).clip(1e-4); xt=torch.from_numpy(((X[tr]-mean)/std).transpose(0,2,1).astype('float32')); xv=torch.from_numpy(((X[va]-mean)/std).transpose(0,2,1).astype('float32')); yt=torch.from_numpy(y[tr].astype('float32')); yv=y[va]
  keys=m.loc[tr,['source','label_binary']].astype(str).agg('|'.join,axis=1); counts=keys.value_counts(); weights=torch.tensor(keys.map(lambda z:1/counts[z]).to_numpy(),dtype=torch.double); sampler=WeightedRandomSampler(weights,len(weights),replacement=True); dl=DataLoader(TensorDataset(xt,yt),128,sampler=sampler); model=Net().to(D); opt=torch.optim.AdamW(model.parameters(),1e-3,weight_decay=1e-4); best=-1; best_state=None
  for epoch in range(12):
   model.train()
   for a,b in dl: opt.zero_grad(); loss=torch.nn.functional.binary_cross_entropy_with_logits(model(a.to(D)),b.to(D)); loss.backward(); opt.step()
   model.eval();
   with torch.no_grad(): p=torch.sigmoid(model(xv.to(D))).cpu().numpy()
   score=roc_auc_score(yv,p)
   if score>best: best=score; best_state={k:v.cpu() for k,v in model.state_dict().items()}
  g=m.loc[va,['group','label_binary']].copy(); g['p']=p; g=g.groupby(['group','label_binary'],as_index=False).p.mean(); rows.append({'fold':fold,'participants':len(g),'auroc':roc_auc_score(g.label_binary,g.p),'brier':brier_score_loss(g.label_binary,g.p),'balanced_accuracy':balanced_accuracy_score(g.label_binary,g.p>=.5),'val_sources':','.join(sorted(m.loc[va,'source'].unique()))}); torch.save({'model_state_dict':best_state,'mean':mean,'std':std,'fold':fold,'strategy':'sint_sensitivity_source_class_balanced','seed':42},P/f'sint_sensitivity_inception_fold_{fold}_seed_42.pt'); print(rows[-1],flush=True)
 pd.DataFrame(rows).to_csv(P/'sint_sensitivity_inception_metrics.csv',index=False); print(pd.DataFrame(rows).mean(numeric_only=True),flush=True)
if __name__=='__main__': main()
