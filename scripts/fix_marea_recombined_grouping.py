from pathlib import Path
import pandas as pd
P=Path(__file__).resolve().parents[1]/'data'/'processed'; f=P/'marea_recombined_healthy_metadata.csv'; m=pd.read_csv(f); m['participant_key']=m['parent_a'].astype(str); m.to_csv(f,index=False); print('synthetic windows',len(m),'effective parent participants',m.participant_key.nunique())
