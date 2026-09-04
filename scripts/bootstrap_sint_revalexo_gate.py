"""Paired participant bootstrap for original vs Sint-expanded RevalExo models."""
from pathlib import Path
import numpy as np, pandas as pd
from sklearn.metrics import roc_auc_score, brier_score_loss
R=Path(__file__).resolve().parents[1]; P=R/'data/processed'; rng=np.random.default_rng(42); n=20000
d=pd.read_csv(P/'sint_revalexo_paired_error_analysis.csv'); y=d.label_binary.to_numpy(); a=d.old_prob.to_numpy(); b=d.new_prob.to_numpy(); rows=[]
for i in range(n):
 idx=rng.integers(0,len(d),len(d)); yy=y[idx]
 if len(np.unique(yy))<2: continue
 rows.append((roc_auc_score(yy,b[idx])-roc_auc_score(yy,a[idx]), brier_score_loss(yy,b[idx])-brier_score_loss(yy,a[idx])))
r=np.asarray(rows); out=pd.DataFrame({'metric':['AUROC delta expanded-original','Brier delta expanded-original'],'mean':[r[:,0].mean(),r[:,1].mean()],'ci_low':[np.quantile(r[:,0],.025),np.quantile(r[:,1],.025)],'ci_high':[np.quantile(r[:,0],.975),np.quantile(r[:,1],.975)],'replicates':[len(r)]*2}); out.to_csv(P/'sint_revalexo_bootstrap_gate.csv',index=False); print(out.to_string(index=False))
