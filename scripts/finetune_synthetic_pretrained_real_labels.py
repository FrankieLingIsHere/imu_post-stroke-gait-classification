"""Fine-tune synthetic-pretrained encoder using real labels only."""
from pathlib import Path
import numpy as np,pandas as pd,torch
from torch.utils.data import DataLoader,TensorDataset,WeightedRandomSampler
from sklearn.metrics import roc_auc_score,brier_score_loss,balanced_accuracy_score
R=Path(__file__).resolve().parents[1]; P=R/'data/processed'; D=torch.device('cuda' if torch.cuda.is_available() else 'cpu'); torch.manual_seed(42); np.random.seed(42)
class Enc(torch.nn.Module):
 def __init__(self): super().__init__(); self.f=torch.nn.Sequential(torch.nn.Conv1d(3,64,9,padding=4),torch.nn.GroupNorm(8,64),torch.nn.GELU(),torch.nn.Conv1d(64,128,9,padding=4),torch.nn.GroupNorm(8,128),torch.nn.GELU(),torch.nn.Conv1d(128,128,9,padding=4),torch.nn.GELU())
 def forward(self,x): return self.f(x)
class Cls(torch.nn.Module):
 def __init__(self): super().__init__(); self.e=Enc(); self.h=torch.nn.Sequential(torch.nn.AdaptiveAvgPool1d(1),torch.nn.Flatten(),torch.nn.Dropout(.3),torch.nn.Linear(128,1))
 def forward(self,x): return self.h(self.e(x)).squeeze(1)
X=np.concatenate([np.load(P/'validated_acceleration_magnitude_windows_float32.npy'),np.load(P/'sint_maartenskliniek_external_windows_float32.npy')]); m=pd.concat([pd.read_csv(P/'validated_window_metadata.csv'),pd.read_csv(P/'sint_maartenskliniek_external_window_metadata.csv')],ignore_index=True); k=m.label.isin(['healthy','stroke']).to_numpy(); X=X[k]; m=m[k].reset_index(drop=True); y=(m.label=='stroke').astype('float32').to_numpy(); mean=X.reshape(-1,3).mean(0); std=X.reshape(-1,3).std(0).clip(1e-4); z=torch.from_numpy(((X-mean)/std).transpose(0,2,1).astype('float32')); yy=torch.from_numpy(y); keys=m.dataset_id.astype(str)+'|'+m.label.astype(str); cnt=keys.value_counts(); w=torch.tensor(keys.map(lambda q:1/cnt[q]).to_numpy(),dtype=torch.double); dl=DataLoader(TensorDataset(z,yy),128,sampler=WeightedRandomSampler(w,len(w),replacement=True))
model=Cls().to(D); ck=torch.load(P/'phase_aware_synthetic_pretrained_encoder.pt',map_location=D,weights_only=False); model.e.load_state_dict(ck['encoder']); opt=torch.optim.AdamW(model.parameters(),1e-3,weight_decay=1e-4)
for ep in range(12):
 model.train()
 for a,b in dl: opt.zero_grad(); loss=torch.nn.functional.binary_cross_entropy_with_logits(model(a.to(D)),b.to(D)); loss.backward(); opt.step()
raw=np.load(P/'revalexo_external_windows_float32.npy'); E=np.stack([np.linalg.norm(raw[:,:,0:3],axis=2),np.linalg.norm(raw[:,:,12:15],axis=2),np.linalg.norm(raw[:,:,6:9],axis=2)],2); em=pd.read_csv(P/'revalexo_external_window_metadata.csv'); ez=torch.from_numpy(((E-mean)/std).transpose(0,2,1).astype('float32')); model.eval()
with torch.no_grad(): p=torch.sigmoid(model(ez.to(D))).cpu().numpy()
g=em.assign(p=p).groupby('subject',as_index=False).p.mean(); g['y']=g.subject.map(em.drop_duplicates('subject').set_index('subject').group.map({'HC':0,'ST':1})); out={'model':'synthetic_pretrained_real_finetuned','participants':len(g),'auroc':roc_auc_score(g.y,g.p),'brier':brier_score_loss(g.y,g.p),'balanced_accuracy':balanced_accuracy_score(g.y,g.p>=.5),'healthy_false_positives':int(((g.y==0)&(g.p>=.5)).sum()),'device':str(D)}; print(out); pd.DataFrame([out]).to_csv(P/'synthetic_pretrained_revalexo_metrics.csv',index=False); torch.save({'model_state_dict':model.state_dict(),'mean':mean,'std':std,'strategy':'synthetic_self_supervised_pretraining_real_label_finetuning'},P/'synthetic_pretrained_real_finetuned.pt')
