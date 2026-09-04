"""GPU masked-reconstruction pretraining for the Zenodo stroke-only stream."""
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

ROOT = Path(__file__).resolve().parents[1]
X = np.load(ROOT / "data/processed/zenodo_stroke_windows_float32.npy")
M = pd.read_csv(ROOT / "data/processed/zenodo_stroke_window_metadata.csv")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
rng = np.random.default_rng(20260824)
people = np.array(sorted(M.participant.unique())); rng.shuffle(people)
val_people = set(people[-2:]); train_people = set(people[:-2])
train_idx = M.participant.isin(train_people).to_numpy(); val_idx = M.participant.isin(val_people).to_numpy()
mean = X[train_idx].reshape(-1, 18).mean(0).astype("float32")
std = X[train_idx].reshape(-1, 18).std(0).clip(1e-3).astype("float32")
def norm(a): return ((a - mean.reshape(1,1,-1)) / std.reshape(1,1,-1)).astype("float32")
train = torch.from_numpy(norm(X[train_idx])).transpose(1,2); val = torch.from_numpy(norm(X[val_idx])).transpose(1,2)

class MaskedAE(nn.Module):
    def __init__(self):
        super().__init__(); self.encoder = nn.Sequential(nn.Conv1d(18,64,9,padding=4),nn.BatchNorm1d(64),nn.GELU(),nn.Conv1d(64,128,9,padding=4),nn.BatchNorm1d(128),nn.GELU(),nn.Conv1d(128,128,9,padding=4),nn.GELU()); self.decoder=nn.Sequential(nn.Conv1d(128,64,9,padding=4),nn.GELU(),nn.Conv1d(64,18,9,padding=4))
    def forward(self,x): return self.decoder(self.encoder(x))
model=MaskedAE().to(device); opt=torch.optim.AdamW(model.parameters(),lr=2e-3,weight_decay=1e-4); loss_fn=nn.SmoothL1Loss()
loader=DataLoader(TensorDataset(train),batch_size=64,shuffle=True,pin_memory=True)
history=[]
for epoch in range(1,16):
    model.train(); total=0
    for (x,) in loader:
        x=x.to(device,non_blocking=True); mask=(torch.rand(x.shape[0],1,x.shape[2],device=device)<0.15); masked=x.masked_fill(mask,0)
        pred=model(masked); loss=loss_fn(pred[mask.expand_as(pred)],x[mask.expand_as(x)])
        opt.zero_grad(set_to_none=True); loss.backward(); opt.step(); total += loss.item()*len(x)
    model.eval();
    with torch.no_grad():
        xv=val[:].to(device); mask=(torch.rand(xv.shape[0],1,xv.shape[2],device=device)<0.15); pred=model(xv.masked_fill(mask,0)); vloss=loss_fn(pred[mask.expand_as(pred)],xv[mask.expand_as(xv)]).item()
    history.append({"epoch":epoch,"train_loss":total/len(train),"val_loss":vloss}); print(history[-1],flush=True)
OUT=ROOT/"data/processed"; torch.save({"model":model.state_dict(),"mean":mean,"std":std,"train_people":sorted(train_people),"val_people":sorted(val_people)},OUT/"zenodo_masked_encoder.pt"); pd.DataFrame(history).to_csv(OUT/"zenodo_masked_pretraining_history.csv",index=False); print("device",device,"checkpoint",OUT/"zenodo_masked_encoder.pt")
