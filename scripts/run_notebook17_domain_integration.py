"""Execute notebook-17 definitions with Zenodo domain penalty."""
from pathlib import Path
import json, numpy as np, pandas as pd, torch
from torch import nn
from torch.utils.data import DataLoader
R=Path(__file__).resolve().parents[1]; D=torch.device('cuda' if torch.cuda.is_available() else 'cpu')
nb=json.loads((R/'notebooks/08_robust_pooled_training.ipynb').read_text(encoding='utf-8')); env={'__name__':'__main__'}
for cell in nb['cells'][:5]:
    if cell['cell_type']=='code': exec(''.join(cell['source']),env)
Z=np.load(R/'data/processed/zenodo_benchmark_acceleration_magnitude_windows_float32.npy'); rows=[]
for fold in range(5):
    env['set_seed'](42); tr,va=env['fold_indices'](fold); stats=env['pooled_stats'](tr); ds=env['GaitDataset'](tr,'source_class_balanced_global',stats,env['source_stats'](tr),env['source_class_balanced_weights'](tr)); vs=env['GaitDataset'](va,'source_class_balanced_global',stats,env['source_stats'](tr)); tl=DataLoader(ds,env['BATCH_SIZE'],shuffle=True); vl=DataLoader(vs,env['BATCH_SIZE']); model=env['InceptionCNN']().to(D); domain=nn.Linear(64,3).to(D); opt=torch.optim.AdamW(list(model.parameters())+list(domain.parameters()),1e-3,weight_decay=1e-4); z=torch.from_numpy(((Z-stats[0])/stats[1]).transpose(0,2,1).astype('float32')); best=(-1,None)
    for epoch in range(env['EPOCHS']):
        model.train()
        for sig,lab,w,_ in tl:
            sig,lab,w=sig.to(D),lab.to(D),w.to(D); h=model.features(sig).flatten(1); loss=(nn.functional.binary_cross_entropy_with_logits(model.classifier(h).squeeze(1),lab,reduction='none')*w).mean(); k=np.random.randint(0,len(z),min(64,len(z))); labels=torch.cat([torch.zeros(len(h),dtype=torch.long),torch.full((len(k),),2,dtype=torch.long)]).to(D); loss=loss+0.03*nn.functional.cross_entropy(domain(torch.cat([h,model.features(z[k].to(D)).flatten(1)])),labels); opt.zero_grad(); loss.backward(); opt.step()
        p=env['predict'](model,vl); fr=env['participant_frame'](va,p,'domain_adversarial',fold,42); auc=env['metric_row'](fr)['roc_auc']; best=(auc,{k:v.detach().cpu().clone() for k,v in model.state_dict().items()}) if auc>best[0] else best
    model.load_state_dict(best[1]); p=env['predict'](model,vl); fr=env['participant_frame'](va,p,'domain_adversarial',fold,42); row=env['metric_row'](fr); row.update({'fold':fold}); rows.append(row); print(fold,row['roc_auc'],flush=True)
out=R/'data/processed/notebook17_domain_integration_results.csv'; pd.DataFrame(rows).to_csv(out,index=False); print('Wrote',out)
