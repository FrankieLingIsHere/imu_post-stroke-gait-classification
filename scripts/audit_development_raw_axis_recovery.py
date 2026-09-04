"""Inventory raw tri-axial development files before rebuilding the raw-axis contract."""
from pathlib import Path
import csv, json, numpy as np, pandas as pd
R=Path(__file__).resolve().parents[1]; rows=[]
for source,root,patterns in [
 ('voisard_2025',R/'data/raw/voisard_2025',['*_raw_data_LB.txt']),
 ('felius_2024',R/'data/raw/felius_2024',['*.csv']),
 ('sint_maartenskliniek',R/'data/raw/sint_maartenskliniek',['*.csv'])]:
 for pat in patterns:
  for f in root.rglob(pat):
   try:
    if f.suffix.lower()=='.txt':
     with f.open(errors='ignore') as h: header=h.readline().strip().split('\t'); n=sum(1 for _ in h)
     rows.append({'source':source,'file':str(f.relative_to(R)),'format':'txt','header':'|'.join(header),'rows':n})
    else:
     with f.open(errors='ignore',newline='') as h: header=next(csv.reader(h)); n=sum(1 for _ in h)
     rows.append({'source':source,'file':str(f.relative_to(R)),'format':'csv','header':'|'.join(header),'rows':n})
   except Exception as e: rows.append({'source':source,'file':str(f.relative_to(R)),'format':'error','header':str(e),'rows':-1})
out=R/'data/processed/development_raw_axis_inventory.csv'; pd.DataFrame(rows).to_csv(out,index=False); print('files',len(rows)); print(pd.DataFrame(rows).groupby(['source','format']).size()); print('output',out)
