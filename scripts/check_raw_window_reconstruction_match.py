"""Check whether processed Voisard windows resolve to raw sensor triplets."""
from pathlib import Path
import pandas as pd
R=Path(__file__).resolve().parents[1]; P=R/'data/processed'; m=pd.read_csv(P/'validated_window_metadata.csv'); rows=[]
for src in sorted(m.dataset_id.unique()):
 q=m[m.dataset_id.eq(src)]; ok=[]
 for _,r in q.iterrows():
  if src!='voisard_2025': ok.append(False); continue
  hits=list((R/'data/raw/voisard_2025/data').rglob(f"{r.trial_id}_raw_data_LB.txt")); ok.append(bool(hits) and all((hits[0].parent/f"{r.trial_id}_raw_data_{c}.txt").exists() for c in ['LB','LF','RF']))
 rows.append({'source':src,'processed_windows':len(q),'matched_complete_triplet_windows':sum(ok),'match_rate':sum(ok)/len(q) if len(q) else 0})
 out=P/'raw_reconstruction_match_audit.csv'; pd.DataFrame(rows).to_csv(out,index=False); print(pd.DataFrame(rows).to_string(index=False)); print('output',out)
