"""Train final internal domain model and evaluate RevalExo without fitting on it."""
from pathlib import Path
import json,numpy as np,pandas as pd,torch
from torch import nn
R=Path(__file__).resolve().parents[1]; D=torch.device('cuda' if torch.cuda.is_available() else 'cpu'); nb=json.loads((R/'notebooks/08_robust_pooled_training.ipynb').read_text(encoding='utf-8')); env={'__name__':'__main__'}
for c in nb['cells'][:5]:
 if c['cell_type']=='code': exec(''.join(c['source']),env)
X=env['magnitude_windows']; Z=np.load(R/'data/processed/zenodo_benchmark_acceleration_magnitude_windows_float32.npy'); stats=env['pooled_stats'](np.arange(len(X))); w=env['source_class_balanced_weights'](np.arange(len(X))); ds=env['GaitDataset'](np.arange(len(X)),'source_class_balanced_global',stats,env['source_stats'](np.arange(len(X))),w); dl=torch.utils.data.DataLoader(ds,env['BATCH_SIZE'],shuffle=True); model=env['InceptionCNN']().to(D); domain=nn.Linear(64,3).to(D); opt=torch.optim.AdamW(list(model.parameters())+list(domain.parameters()),1e-3,weight_decay=1e-4); z=torch.from_numpy(((Z-stats[0])/stats[1]).transpose(0,2,1).astype('float32'))
for ep in range(env['EPOCHS']):
 model.train()
 for sig,lab,ww,_ in dl:
  sig,lab,ww=sig.to(D),lab.to(D),ww.to(D); h=model.features(sig).flatten(1); loss=(nn.functional.binary_cross_entropy_with_logits(model.classifier(h).squeeze(1),lab,reduction='none')*ww).mean(); k=np.random.randint(0,len(z),min(64,len(z))); labels=torch.cat([torch.zeros(len(h),dtype=torch.long),torch.full((len(k),),2,dtype=torch.long)]).to(D); loss=loss+0.03*nn.functional.cross_entropy(domain(torch.cat([h,model.features(z[k].to(D)).flatten(1)])),labels); opt.zero_grad(); loss.backward(); opt.step()
torch.save({'model':model.state_dict(),'mean':stats[0],'std':stats[1]},R/'data/processed/notebook17_domain_full_internal.pt')
E=np.load(R/'data/processed/revalexo_external_windows_float32.npy'); E=np.stack([np.linalg.norm(E[:,:,0:3],axis=2),np.linalg.norm(E[:,:,6:9],axis=2),np.linalg.norm(E[:,:,12:15],axis=2)],2); E=torch.from_numpy(((E-stats[0])/stats[1]).transpose(0,2,1).astype('float32')); model.eval()
with torch.no_grad(): p=torch.sigmoid(model(E.to(D))[0]).cpu().numpy()
em=pd.read_csv(R/'data/processed/revalexo_external_window_metadata.csv'); em['probability']=p; part=em.groupby(['subject','group'],as_index=False).probability.mean(); part['y']=(part.group=='ST').astype(int); out=R/'data/processed/notebook17_domain_revalexo_predictions.csv'; part.to_csv(out,index=False); from sklearn.metrics import roc_auc_score; print('AUROC',roc_auc_score(part.y,part.probability),'participants',len(part)); print('Wrote',out)
