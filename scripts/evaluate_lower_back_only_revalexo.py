from pathlib import Path
import numpy as np, pandas as pd, torch
from torch.utils.data import DataLoader, TensorDataset, WeightedRandomSampler
from sklearn.metrics import roc_auc_score,brier_score_loss,balanced_accuracy_score
class Block(torch.nn.Module):
 def __init__(self,ic,oc=16):
  super().__init__(); b=min(32,ic); self.b=torch.nn.Conv1d(ic,b,1,bias=False); self.br=torch.nn.ModuleList([torch.nn.Conv1d(b,oc,k,padding=k//2,bias=False) for k in (7,15,25)]); self.pool=torch.nn.Conv1d(ic,oc,1,bias=False); self.bn=torch.nn.BatchNorm1d(oc*4); self.res=torch.nn.Conv1d(ic,oc*4,1,bias=False) if ic!=oc*4 else torch.nn.Identity()
 def forward(self,x):
  z=self.b(x); q=[v(z) for v in self.br]; q.append(self.pool(torch.nn.functional.max_pool1d(x,3,1,1))); return torch.nn.functional.gelu(self.bn(torch.cat(q,1))+self.res(x))
class Net(torch.nn.Module):
 def __init__(self,channels):
  super().__init__(); self.f=torch.nn.Sequential(Block(channels),torch.nn.MaxPool1d(2),Block(64),torch.nn.AdaptiveAvgPool1d(1)); self.c=torch.nn.Sequential(torch.nn.Flatten(),torch.nn.Dropout(.3),torch.nn.Linear(64,1))
 def forward(self,x): return self.c(self.f(x)).squeeze(1)

ROOT=Path(__file__).resolve().parents[1]; P=ROOT/'data/processed'; D=torch.device('cuda' if torch.cuda.is_available() else 'cpu'); torch.manual_seed(42); np.random.seed(42)
X=np.concatenate([np.load(P/'validated_acceleration_magnitude_windows_float32.npy'),np.load(P/'sint_maartenskliniek_external_windows_float32.npy')]); m=pd.concat([pd.read_csv(P/'validated_window_metadata.csv'),pd.read_csv(P/'sint_maartenskliniek_external_window_metadata.csv')],ignore_index=True); keep=m.label.isin(['healthy','stroke']).to_numpy(); X=X[keep,:,0:1]; m=m.loc[keep].reset_index(drop=True); y=(m.label=='stroke').astype(int).to_numpy(); keys=m.dataset_id.astype(str)+'|'+m.label.astype(str); counts=keys.value_counts(); weights=torch.tensor(keys.map(lambda z:1/counts[z]).to_numpy(),dtype=torch.double); mean=X.mean((0,1)); std=X.std((0,1)).clip(1e-4); z=torch.from_numpy(((X-mean)/std).transpose(0,2,1).astype('float32')); model=Net(1).to(D); dl=DataLoader(TensorDataset(z,torch.from_numpy(y.astype('float32'))),128,sampler=WeightedRandomSampler(weights,len(weights),replacement=True)); opt=torch.optim.AdamW(model.parameters(),1e-3,weight_decay=1e-4)
for epoch in range(15):
 model.train(); losses=[]
 for a,b in dl: opt.zero_grad(); loss=torch.nn.functional.binary_cross_entropy_with_logits(model(a.to(D)),b.to(D)); loss.backward(); opt.step(); losses.append(loss.item())
 print({'epoch':epoch+1,'loss':float(np.mean(losses))},flush=True)
torch.save({'model_state_dict':model.state_dict(),'mean':mean,'std':std,'strategy':'full_expanded_lower_back_only_source_class_balanced','seed':42,'device':str(D)},P/'full_expanded_lower_back_only_seed_42.pt')
raw=np.load(P/'revalexo_external_windows_float32.npy'); x=np.linalg.norm(raw[:,:,0:3],axis=2)[:,:,None].astype('float32'); em=pd.read_csv(P/'revalexo_external_window_metadata.csv'); em['y']=em.group.map({'HC':0,'ST':1}); ez=torch.from_numpy(((x-mean)/np.maximum(std,1e-6)).transpose(0,2,1).astype('float32')); model.eval()
with torch.no_grad(): prob=torch.sigmoid(model(ez.to(D))).cpu().numpy()
g=em.assign(prob=prob).groupby(['subject','y'],as_index=False).prob.mean(); yy=g.y.to_numpy(); pp=g.prob.to_numpy(); result={'model':'full_expanded_lower_back_only','participants':len(g),'healthy':int((yy==0).sum()),'stroke':int((yy==1).sum()),'auroc':roc_auc_score(yy,pp),'brier':brier_score_loss(yy,pp),'balanced_accuracy':balanced_accuracy_score(yy,pp>=.5)}; pd.DataFrame([result]).to_csv(P/'full_expanded_lower_back_only_revalexo_metrics.csv',index=False); g.to_csv(P/'full_expanded_lower_back_only_revalexo_participant_predictions.csv',index=False); print(result)
