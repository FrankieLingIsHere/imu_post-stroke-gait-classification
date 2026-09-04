"""Lightweight temporal contrastive pretraining for IMU windows."""
from pathlib import Path
import numpy as np, pandas as pd, torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset
ROOT=Path(__file__).resolve().parents[1]; device=torch.device('cuda' if torch.cuda.is_available() else 'cpu')
X=np.load(ROOT/'data/processed/zenodo_stroke_windows_float32.npy'); m=pd.read_csv(ROOT/'data/processed/zenodo_stroke_window_metadata.csv')
p=np.array(sorted(m.participant.unique())); tr=set(p[:-2]); keep=m.participant.isin(tr).to_numpy(); x=X[keep]; mean=x.reshape(-1,18).mean(0); std=x.reshape(-1,18).std(0).clip(1e-3); x=torch.from_numpy(((x-mean)/std).transpose(0,2,1).astype('float32'))
class Enc(nn.Module):
 def __init__(self):
  super().__init__(); self.f=nn.Sequential(nn.Conv1d(18,64,9,padding=4),nn.BatchNorm1d(64),nn.GELU(),nn.Conv1d(64,128,9,padding=4),nn.BatchNorm1d(128),nn.GELU(),nn.Conv1d(128,128,9,padding=4),nn.GELU(),nn.AdaptiveAvgPool1d(1))
 def forward(self,z): return self.f(z).squeeze(-1)
class Net(nn.Module):
 def __init__(self): super().__init__(); self.e=Enc(); self.p=nn.Sequential(nn.Linear(128,128),nn.GELU(),nn.Linear(128,64))
 def forward(self,z): return nn.functional.normalize(self.p(self.e(z)),dim=1)
def aug(z):
 z=z.clone(); z=z*(1+0.05*torch.randn(z.size(0),18,1,device=z.device)); z=z+0.02*torch.randn_like(z); return z
net=Net().to(device); opt=torch.optim.AdamW(net.parameters(),2e-3,weight_decay=1e-4); loader=DataLoader(TensorDataset(x),64,shuffle=True,pin_memory=True); hist=[]
for ep in range(1,16):
 net.train(); total=0
 for (z,) in loader:
  a,b=aug(z.to(device)),aug(z.to(device)); q=torch.cat([net(a),net(b)]); sim=q@q.T/0.2; sim=sim.masked_fill(torch.eye(len(q),device=device).bool(),-1e9); target=(torch.arange(len(q),device=device)+len(q)//2)%(len(q)); loss=nn.functional.cross_entropy(sim,target); opt.zero_grad(); loss.backward(); opt.step(); total+=loss.item()*len(z)
 hist.append({'epoch':ep,'loss':total/len(x)}); print(hist[-1],flush=True)
torch.save({'encoder':net.e.state_dict(),'mean':mean.astype('float32'),'std':std.astype('float32')},ROOT/'data/processed/zenodo_temporal_contrastive_encoder.pt'); pd.DataFrame(hist).to_csv(ROOT/'data/processed/zenodo_temporal_contrastive_history.csv',index=False); print('device',device)
