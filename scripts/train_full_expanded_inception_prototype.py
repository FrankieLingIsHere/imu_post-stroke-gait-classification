"""Train the full expanded prototype after the Sint inclusion gate."""
from pathlib import Path
import os
import numpy as np,pandas as pd,torch
from torch.utils.data import DataLoader,TensorDataset,WeightedRandomSampler
from train_sint_sensitivity_inception import Net
R=Path(__file__).resolve().parents[1]; P=R/'data/processed'; D=torch.device('cuda' if torch.cuda.is_available() else 'cpu'); torch.manual_seed(42); np.random.seed(42)
def main():
 X=np.concatenate([np.load(P/'validated_acceleration_magnitude_windows_float32.npy'),np.load(P/'sint_maartenskliniek_external_windows_float32.npy')]); m=pd.concat([pd.read_csv(P/'validated_window_metadata.csv'),pd.read_csv(P/'sint_maartenskliniek_external_window_metadata.csv')],ignore_index=True); keep=m.label.isin(['healthy','stroke']).to_numpy(); X=X[keep]; m=m.loc[keep].reset_index(drop=True); m['source']=m.dataset_id; m['y']=(m.label=='stroke').astype(int)
 synfile=os.getenv('SYNTHETIC_CYCLES','')
 if synfile:
  cyc=np.load(P/synfile); old=np.linspace(0,1,cyc.shape[1]); new=np.linspace(0,1,500); sw=np.stack([np.interp(new,old,cyc[i,:,j]) for i in range(len(cyc)) for j in range(3)]).reshape(len(cyc),3,500).transpose(0,2,1).astype('float32'); sm=pd.DataFrame({'label':'healthy','dataset_id':'synthetic_phase_aware','participant_key':['synthetic_parent_'+str(i//25) for i in range(len(sw))]}); sm['source']=sm.dataset_id; sm['y']=0; X=np.concatenate([X,sw]); m=pd.concat([m,sm],ignore_index=True); print('synthetic added',len(sw),'effective parents',sm.participant_key.nunique(),flush=True)
 mean=X.reshape(-1,3).mean(0); std=X.reshape(-1,3).std(0).clip(1e-4); z=torch.from_numpy(((X-mean)/std).transpose(0,2,1).astype('float32')); y=torch.from_numpy(m.y.to_numpy('float32')); keys=m[['source','y']].astype(str).agg('|'.join,axis=1); counts=keys.value_counts(); weights=torch.tensor(keys.map(lambda q:1/counts[q]).to_numpy(),dtype=torch.double); dl=DataLoader(TensorDataset(z,y),128,sampler=WeightedRandomSampler(weights,len(weights),replacement=True)); model=Net().to(D); opt=torch.optim.AdamW(model.parameters(),1e-3,weight_decay=1e-4)
 for epoch in range(15):
  model.train(); losses=[]
  for a,b in dl: opt.zero_grad(); loss=torch.nn.functional.binary_cross_entropy_with_logits(model(a.to(D)),b.to(D)); loss.backward(); opt.step(); losses.append(loss.item())
  print({'epoch':epoch+1,'loss':float(np.mean(losses))},flush=True)
 out={'model_state_dict':model.state_dict(),'mean':mean,'std':std,'strategy':'full_expanded_with_optional_phase_aware_synthesis' if synfile else 'full_expanded_felius_voisard_sint_source_class_balanced','seed':42,'participants':int(m.participant_key.nunique()),'windows':len(m),'device':str(D)}; outpath=P/('full_expanded_inception_phase_synthetic_seed_42.pt' if synfile else 'full_expanded_inception_prototype_seed_42.pt'); torch.save(out,outpath); print('saved',outpath,out['participants'],out['windows'],D)
if __name__=='__main__': main()
