from pathlib import Path
import numpy as np, torch
from torch.utils.data import DataLoader,TensorDataset
P=Path(__file__).resolve().parents[1]/'data'/'processed'; device=torch.device('cuda' if torch.cuda.is_available() else 'cpu'); torch.manual_seed(42); np.random.seed(42)
X=np.load(P/'marea_full_gait_cycles_float32.npy'); meta=__import__('pandas').read_csv(P/'marea_full_gait_cycle_metadata.csv'); cond=meta.cycle_duration_sec.to_numpy('float32'); cond=(cond-cond.mean())/(cond.std()+1e-6); mu=X.mean((0,1)); sd=X.std((0,1)).clip(1e-4); X=((X-mu)/sd).astype('float32'); dl=DataLoader(TensorDataset(torch.from_numpy(X),torch.from_numpy(cond)),128,shuffle=True)
T=100; beta=torch.linspace(1e-4,.02,T,device=device); alpha=1-beta; abar=torch.cumprod(alpha,0)
class Net(torch.nn.Module):
 def __init__(self):
  super().__init__(); self.t=torch.nn.Sequential(torch.nn.Linear(33,64),torch.nn.GELU(),torch.nn.Linear(64,64)); self.inp=torch.nn.Conv1d(3,64,5,padding=2); self.blocks=torch.nn.ModuleList([torch.nn.Sequential(torch.nn.Conv1d(64,64,5,padding=2),torch.nn.GroupNorm(8,64),torch.nn.GELU(),torch.nn.Conv1d(64,64,5,padding=2)) for _ in range(6)]); self.out=torch.nn.Conv1d(64,3,5,padding=2)
 def forward(self,x,t,c):
  h=self.inp(x); te=self.t(torch.cat([torch.sin(t[:,None]*torch.arange(16,device=x.device)),torch.cos(t[:,None]*torch.arange(16,device=x.device)),c[:,None]],1)).unsqueeze(-1)
  for b in self.blocks: h=h+b(h)+te
  return self.out(torch.nn.functional.gelu(h))
net=Net().to(device); opt=torch.optim.AdamW(net.parameters(),2e-4,weight_decay=1e-5)
for ep in range(100):
 for x,c in dl:
  x=x.to(device).transpose(1,2); c=c.to(device); ti=torch.randint(T,(len(x),),device=device); noise=torch.randn_like(x); xt=abar[ti,None,None].sqrt()*x+(1-abar[ti,None,None]).sqrt()*noise; pred=net(xt,ti.float()/T,c); loss=(pred-noise).pow(2).mean(); opt.zero_grad(); loss.backward(); opt.step()
 if (ep+1)%20==0: print(ep+1,float(loss),flush=True)
net.eval(); n=1500; z=torch.randn(n,3,200,device=device); cc=torch.randn(n,device=device).clamp(-2,2)
with torch.no_grad():
 for ti in range(T-1,-1,-1):
  tt=torch.full((n,),ti/T,device=device); eps=net(z,tt,cc); z=(z-beta[ti]/(1-abar[ti]).sqrt()*eps)/alpha[ti].sqrt();
  if ti>0: z=z+beta[ti].sqrt()*torch.randn_like(z)
Y=(z.transpose(1,2).cpu().numpy()*sd+mu).astype('float32'); np.save(P/'marea_diffusion_synthetic_healthy_cycles_float32.npy',Y); torch.save({'state_dict':net.state_dict(),'mean':mu,'std':sd},P/'marea_cycle_diffusion.pt'); print('device',device,'generated',Y.shape)
