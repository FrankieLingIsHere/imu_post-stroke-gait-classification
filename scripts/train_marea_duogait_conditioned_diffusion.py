from pathlib import Path
import numpy as np, pandas as pd, torch
from torch.utils.data import DataLoader,TensorDataset
P=Path(__file__).resolve().parents[1]/'data'/'processed'; dev=torch.device('cuda' if torch.cuda.is_available() else 'cpu'); torch.manual_seed(42)
a=np.load(P/'marea_full_gait_cycles_float32.npy'); b=np.load(P/'duogait_full_gait_cycles_ms2_float32.npy'); X=np.concatenate([a,b]); s=np.concatenate([np.zeros(len(a)),np.ones(len(b))]); mu=X.mean((0,1)); sd=X.std((0,1)).clip(1e-4); X=((X-mu)/sd).astype('float32')
# Continuous conditioning exposes cadence/duration and per-channel amplitude variation.
ma=pd.read_csv(P/'marea_full_gait_cycle_metadata.csv'); du=pd.read_csv(P/'duogait_full_gait_cycle_metadata_ms2.csv'); md=pd.concat([ma,du],ignore_index=True)
dur=md['cycle_duration_sec'].to_numpy('float32'); amp=np.std(X,axis=1).astype('float32'); C=np.column_stack([dur,amp]); cm=C.mean(0); cs=C.std(0).clip(1e-4); C=((C-cm)/cs).astype('float32')
dl=DataLoader(TensorDataset(torch.from_numpy(X),torch.from_numpy(s).float(),torch.from_numpy(C)),128,shuffle=True)
class Net(torch.nn.Module):
 def __init__(self):
  super().__init__(); self.i=torch.nn.Conv1d(3,64,5,padding=2); self.coarse=torch.nn.Sequential(torch.nn.AvgPool1d(4),torch.nn.Conv1d(3,64,5,padding=2),torch.nn.GroupNorm(8,64),torch.nn.GELU(),torch.nn.Conv1d(64,64,5,padding=2)); self.phase=torch.nn.Conv1d(2,64,1); self.c=torch.nn.Linear(7,64); self.b=torch.nn.ModuleList([torch.nn.Sequential(torch.nn.Conv1d(64,64,5,padding=2),torch.nn.GroupNorm(8,64),torch.nn.GELU(),torch.nn.Conv1d(64,64,5,padding=2)) for _ in range(6)]); self.o=torch.nn.Conv1d(64,3,5,padding=2)
 def forward(self,x,t,s,c):
  ph=torch.linspace(0,6.283185, x.shape[-1], device=x.device); pe=torch.stack([torch.sin(ph),torch.cos(ph)]).unsqueeze(0).expand(x.shape[0],-1,-1); h=self.i(x)+torch.nn.functional.interpolate(self.coarse(x),size=x.shape[-1],mode='linear',align_corners=False)+self.phase(pe)+self.c(torch.cat([torch.sin(t[:,None]),torch.cos(t[:,None]),s[:,None],c],1)).unsqueeze(-1)
  for z in self.b: h=h+z(h)
  return self.o(torch.nn.functional.gelu(h))
T=100; beta=torch.linspace(1e-4,.02,T,device=dev); ab=torch.cumprod(1-beta,0); net=Net().to(dev); opt=torch.optim.AdamW(net.parameters(),2e-4)
for ep in range(100):
 for x,s,c in dl:
  x=x.to(dev).transpose(1,2); s=s.to(dev); c=c.to(dev); t=torch.randint(T,(len(x),),device=dev); n=torch.randn_like(x); xt=ab[t,None,None].sqrt()*x+(1-ab[t,None,None]).sqrt()*n; loss=(net(xt,t.float()/T,s,c)-n).pow(2).mean(); opt.zero_grad(); loss.backward(); opt.step()
 if (ep+1)%20==0: print(ep+1,float(loss.detach()),flush=True)
net.eval(); n=1500; s=torch.arange(n,device=dev).float()%2; rng=np.random.default_rng(42); ci=[]
for q in range(n):
 ix=rng.integers(0, len(a) if q%2==0 else len(a), size=1)[0] if q%2==0 else rng.integers(len(a),len(X))
 ci.append(C[ix])
c=torch.from_numpy(np.asarray(ci,dtype='float32')).to(dev); z=torch.randn(n,3,200,device=dev)
with torch.no_grad():
 for t in range(T-1,-1,-1):
  eps=net(z,torch.full((n,),t/T,device=dev),s,c); alpha=1-beta[t]; abar=ab[t]; mean=(z-beta[t]/(1-abar).sqrt()*eps)/alpha.sqrt()
  if t: z=mean+((beta[t]*(1-ab[t-1])/(1-abar)).sqrt())*torch.randn_like(z)
  else: z=mean
Y=(z.transpose(1,2).cpu().numpy()*sd+mu).astype('float32'); np.save(P/'marea_duogait_conditioned_synthetic_healthy_cycles_float32.npy',Y); pd.DataFrame({'label':['healthy']*n,'synthetic':[True]*n}).to_csv(P/'marea_duogait_conditioned_synthetic_metadata.csv',index=False); torch.save(net.state_dict(),P/'marea_duogait_conditioned_diffusion.pt'); print('device',dev,'generated',Y.shape)
