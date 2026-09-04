"""Source-conditioned healthy-window diffusion in the classifier's native 500x3 contract."""
from pathlib import Path
import os
import numpy as np,pandas as pd,torch
from torch.utils.data import DataLoader,TensorDataset
R=Path(__file__).resolve().parents[1]; P=R/'data/processed'; D=torch.device('cuda' if torch.cuda.is_available() else 'cpu'); torch.manual_seed(42); np.random.seed(42)
X=np.load(P/'tier1_healthy_marea_duogait_windows_float32.npy'); m=pd.read_csv(P/'tier1_healthy_marea_duogait_window_metadata.csv'); src=(m.dataset_id=='duogait_2023').astype('float32').to_numpy(); mu=X.mean((0,1)); sd=X.std((0,1)).clip(1e-4); Z=((X-mu)/sd).transpose(0,2,1).astype('float32'); amp=np.std(X,axis=1).astype('float32'); ac=amp.mean(0); az=amp.std(0).clip(1e-4); C=((amp-ac)/az).astype('float32'); dl=DataLoader(TensorDataset(torch.from_numpy(Z),torch.from_numpy(src),torch.from_numpy(C)),128,shuffle=True,pin_memory=True)
class Net(torch.nn.Module):
 def __init__(self):
  super().__init__(); self.i=torch.nn.Conv1d(3,64,7,padding=3); self.c=torch.nn.Linear(6,64); self.b=torch.nn.ModuleList([torch.nn.Sequential(torch.nn.Conv1d(64,64,7,padding=3),torch.nn.GroupNorm(8,64),torch.nn.GELU(),torch.nn.Conv1d(64,64,7,padding=3)) for _ in range(8)]); self.o=torch.nn.Conv1d(64,3,7,padding=3)
 def forward(self,x,t,s,c):
  h=self.i(x)+self.c(torch.cat([torch.sin(t[:,None]),torch.cos(t[:,None]),s[:,None],c],1)).unsqueeze(-1)
  for b in self.b: h=h+b(h)
  return self.o(torch.nn.functional.gelu(h))
T=200; beta=torch.linspace(1e-4,.02,T,device=D); alpha=1-beta; ab=torch.cumprod(alpha,0); net=Net().to(D); opt=torch.optim.AdamW(net.parameters(),2e-4,weight_decay=1e-4)
for ep in range(1,81):
 for x,s,c in dl:
  x=x.to(D); s=s.to(D); c=c.to(D); t=torch.randint(T,(len(x),),device=D); n=torch.randn_like(x); xt=ab[t,None,None].sqrt()*x+(1-ab[t,None,None]).sqrt()*n; loss=(net(xt,t.float()/T,s,c)-n).pow(2).mean(); opt.zero_grad(); loss.backward(); opt.step()
 if ep%20==0: print(ep,round(float(loss),4),flush=True)
net.eval(); N=int(os.getenv('SYNTHETIC_N','1200')); rng=np.random.default_rng(42); si=torch.from_numpy((np.arange(N)%2).astype('float32')).to(D); ci=torch.from_numpy(C[rng.integers(0,len(X),N)].astype('float32')).to(D); z=torch.randn(N,3,500,device=D)
with torch.no_grad():
 for t in range(T-1,-1,-1):
  e=net(z,torch.full((N,),t/T,device=D),si,ci); mean=(z-beta[t]/(1-ab[t]).sqrt()*e)/alpha[t].sqrt(); z=mean+((beta[t]*(1-ab[t-1])/(1-ab[t])).sqrt())*torch.randn_like(z) if t else mean
Y=(z.transpose(1,2).cpu().numpy()*sd+mu).astype('float32'); np.save(P/'healthy_window_diffusion_synthetic_500x3_float32.npy',Y); pd.DataFrame({'dataset_condition':np.where(np.arange(N)%2,'duogait_2023','marea_2017'),'label':'healthy','synthetic':True}).to_csv(P/'healthy_window_diffusion_synthetic_metadata.csv',index=False); torch.save({'state_dict':net.state_dict(),'mean':mu,'std':sd,'amp_mean':ac,'amp_std':az,'contract':'500x3 native healthy window','device':str(D)},P/'healthy_window_diffusion.pt'); print('device',D,'generated',Y.shape)
