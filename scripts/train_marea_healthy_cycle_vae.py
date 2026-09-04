from pathlib import Path
import numpy as np, torch, pandas as pd
from torch.utils.data import DataLoader,TensorDataset
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/'data'/'processed'; device=torch.device('cuda' if torch.cuda.is_available() else 'cpu'); torch.manual_seed(42); np.random.seed(42)
X=np.load(P/'marea_full_gait_cycles_float32.npy'); mu=X.mean((0,1)); sd=X.std((0,1)).clip(1e-4); Z=((X-mu)/sd).astype('float32'); ds=DataLoader(TensorDataset(torch.from_numpy(Z)),128,shuffle=True)
class VAE(torch.nn.Module):
 def __init__(self):
  super().__init__(); self.enc=torch.nn.Sequential(torch.nn.Conv1d(3,32,7,2,3),torch.nn.GELU(),torch.nn.Conv1d(32,64,7,2,3),torch.nn.GELU(),torch.nn.Conv1d(64,64,7,2,3),torch.nn.GELU()); self.mu=torch.nn.Linear(64*25,32); self.lv=torch.nn.Linear(64*25,32); self.dec=torch.nn.Sequential(torch.nn.Linear(32,64*25),torch.nn.GELU(),torch.nn.Unflatten(1,(64,25)),torch.nn.ConvTranspose1d(64,64,4,2,1),torch.nn.GELU(),torch.nn.ConvTranspose1d(64,32,4,2,1),torch.nn.GELU(),torch.nn.ConvTranspose1d(32,3,4,2,1))
 def forward(self,x):
  h=self.enc(x); a=self.mu(h.flatten(1)); l=self.lv(h.flatten(1)); z=a+torch.exp(.5*l)*torch.randn_like(a); return self.dec(z)[...,:200],a,l
net=VAE().to(device); opt=torch.optim.AdamW(net.parameters(),2e-3,weight_decay=1e-5)
for epoch in range(120):
 net.train(); loss_sum=0
 for (x,) in ds:
  x=x.to(device).transpose(1,2); rec,a,l=net(x); recon=(rec-x).pow(2).mean(); var_loss=(rec.std(2)-x.std(2)).pow(2).mean(); spec_loss=(torch.fft.rfft(rec,dim=2).abs()-torch.fft.rfft(x,dim=2).abs()).pow(2).mean(); kl=-.5*(1+l-a.pow(2)-l.exp()).mean(); loss=recon+.20*var_loss+.02*spec_loss+.0005*kl; opt.zero_grad(); loss.backward(); opt.step(); loss_sum+=loss.item()
 if (epoch+1)%20==0: print(epoch+1,loss_sum/len(ds),recon.item(),kl.item(),flush=True)
net.eval(); n=1500
with torch.no_grad(): y=net.dec(torch.randn(n,32,device=device))[...,:200].transpose(1,2).cpu().numpy()*sd+mu
np.save(P/'marea_vae_synthetic_healthy_cycles_v2_float32.npy',y.astype('float32')); pd.DataFrame({'dataset_id':['marea_2017_vae_v2']*n,'label':['healthy']*n,'synthetic':[True]*n,'parent_source':['marea_2017']*n,'phase_points':[200]*n}).to_csv(P/'marea_vae_synthetic_healthy_cycle_metadata_v2.csv',index=False); torch.save({'state_dict':net.state_dict(),'mean':mu,'std':sd},P/'marea_healthy_cycle_vae_v2.pt'); print('device',device,'generated',y.shape)
