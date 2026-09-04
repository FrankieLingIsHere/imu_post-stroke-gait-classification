"""Self-supervised pretraining probe using synthetic cycles without labels."""
from pathlib import Path
import numpy as np, torch
from torch import nn
from torch.utils.data import DataLoader,TensorDataset
R=Path(__file__).resolve().parents[1]; P=R/'data/processed'; D=torch.device('cuda' if torch.cuda.is_available() else 'cpu'); torch.manual_seed(42)
real=np.concatenate([np.load(P/'marea_full_gait_cycles_float32.npy'),np.load(P/'duogait_full_gait_cycles_ms2_float32.npy')]); syn=np.load(P/'marea_duogait_conditioned_synthetic_healthy_cycles_float32.npy'); X=np.concatenate([real,syn]); mu=real.mean((0,1)); sd=real.std((0,1)).clip(1e-4); X=((X-mu)/sd).transpose(0,2,1).astype('float32'); dl=DataLoader(TensorDataset(torch.from_numpy(X)),128,shuffle=True,pin_memory=True)
class Enc(nn.Module):
 def __init__(self):
  super().__init__(); self.f=nn.Sequential(nn.Conv1d(3,64,9,padding=4),nn.GroupNorm(8,64),nn.GELU(),nn.Conv1d(64,128,9,padding=4),nn.GroupNorm(8,128),nn.GELU(),nn.Conv1d(128,128,9,padding=4),nn.GELU())
 def forward(self,x): return self.f(x)
class AE(nn.Module):
 def __init__(self): super().__init__(); self.e=Enc(); self.d=nn.Sequential(nn.Conv1d(128,64,9,padding=4),nn.GELU(),nn.Conv1d(64,3,9,padding=4))
 def forward(self,x): return self.d(self.e(x))
m=AE().to(D); o=torch.optim.AdamW(m.parameters(),2e-3,weight_decay=1e-4)
for ep in range(1,21):
 m.train(); lossv=[]
 for (x,) in dl:
  x=x.to(D); mask=(torch.rand(x.size(0),1,x.size(2),device=D)<.15); pred=m(x.masked_fill(mask,0)); loss=nn.functional.smooth_l1_loss(pred[mask.expand_as(pred)],x[mask.expand_as(x)]); o.zero_grad(); loss.backward(); o.step(); lossv.append(loss.item())
 print(ep,round(float(np.mean(lossv)),4),flush=True)
torch.save({'encoder':m.e.state_dict(),'mean':mu.astype('float32'),'std':sd.astype('float32'),'real_cycles':len(real),'synthetic_cycles':len(syn),'device':str(D)},P/'phase_aware_synthetic_pretrained_encoder.pt'); print('saved',D)
