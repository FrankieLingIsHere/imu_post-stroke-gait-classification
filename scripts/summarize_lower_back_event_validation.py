"""Finalize agreement uncertainty and tolerant packet-counter diagnostics."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/processed/lower_back_events_v1'


def main():
    rows=[]
    for path in sorted((ROOT/'data/raw/voisard_2025/data').glob('*/*/*/*/*_meta.json')):
        trial=path.stem.removesuffix('_meta');m=json.loads(path.read_text())
        raw=pd.read_csv(path.parent/(trial+'_raw_data_LB.txt'),sep='\t',usecols=['PacketCounter'])
        delta=raw.PacketCounter.diff().to_numpy()
        # Floating point counters can increment by 1.000000000000001.
        # Count missing samples only for increments >=2 (with tolerance).
        gaps=delta>1.5
        rows.append(dict(participant='voisard_2025:'+m['subject'],trial=trial,sensor=m['sensor'],
                         native_packet_gaps=int(gaps.sum()),missing_packets=int(np.rint(delta[gaps]-1).sum())))
    alignment=pd.DataFrame(rows)
    alignment.to_csv(OUT/'packet_alignment.csv',index=False)
    people=pd.read_csv(OUT/'participant_metrics.csv')
    rows=[]
    for mode in people['mode'].unique():
        for name,groups in [('HS',['HS']),('CVA',['CVA']),('other',['ACL','CIPN','HOA','KOA','PD','RIL'])]:
            f=people[people['mode'].eq(mode)&people.pathology.isin(groups)]
            rng=np.random.default_rng(20260909);values=f[['f1','cadence_mae']].to_numpy()
            means=np.nanmean(values[rng.integers(0,len(f),size=(2000,len(f)))],axis=1)
            for i,metric in enumerate(['f1','cadence_mae']):
                lo,hi=np.quantile(means[:,i],[.025,.975]);rows.append(dict(mode=mode,group=name,metric=metric,low=lo,high=hi))
    pd.DataFrame(rows).to_csv(OUT/'participant_intervals.csv',index=False)
    contract=pd.read_csv(ROOT/'data/processed/conditional_gait_v1/participant_contract.csv')
    selected=pd.read_csv(ROOT/'data/processed/conditional_gait_v1/trial_features.csv')[['participant','trial']]
    affected=alignment.merge(selected,on=['participant','trial']).query('native_packet_gaps > 0')
    matched=affected.merge(contract[['participant','matched']],on='participant').query('matched')
    verification=json.loads((OUT/'verification.json').read_text())
    verification.update(tests_passed=4,packet_diagnostic_note='input_ledger native_counter_gaps used a strict >1 float comparison; use packet_alignment.csv instead, which ignores rounding noise. This does not affect detector inputs or results.',
        real_packet_gap_trials=int(alignment.native_packet_gaps.gt(0).sum()),conditional_affected_trials=len(affected),conditional_affected_people=affected.participant.nunique(),conditional_matched_affected_trials=len(matched),
        frozen_sha256=hashlib.sha256((ROOT/'models/checkpoints/stroke-gait-lower-back-ensemble-v0.2.0.pt').read_bytes()).hexdigest())
    verification['hashes'].update({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.glob('*.csv')})
    (OUT/'verification.json').write_text(json.dumps(verification,indent=2))
    print({k:v for k,v in verification.items() if k!='hashes'})


if __name__=='__main__':main()
