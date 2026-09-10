"""All-local-cohort agreement with Voisard algorithm-derived annotations."""
from pathlib import Path
import hashlib
import importlib.metadata
import json
import sys
import warnings

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.features.lower_back_events import COLS, detect_lower_back_events, match_events
from src.features.voisard import _events_outside_uturn, _walking_bounds

OUT = ROOT/'data/processed/lower_back_events_v1'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    OUT.mkdir(exist_ok=True)
    if (OUT/'verification.json').exists():
        raise FileExistsError('Completed; inspect saved evidence')
    paths = sorted((ROOT/'data/raw/voisard_2025/data').glob('*/*/*/*/*_meta.json'))
    protocol = dict(mobgap='1.2.0',algorithm='GsdAdaptiveIonescu defaults + IcdShinImproved norm defaults',
        modes=['reference_bouts','autonomous'],scope='all 1356 local trials; no classifier-window exclusion',
        reference='algorithm-derived [toe-off, heel-strike]; compare second element',
        tolerance_seconds=.15, input='provider processed LB_Acc m/s2 on annotation timeline; no additional rescaling, interpolation or centering; trailing all-acc-NaN rows trimmed',
        cadence_metric='absolute detected-minus-reference count *60 / reference straight-bout seconds; includes zero detections',
        gate='each HS/CVA/other: participant-macro F1 >= .85; participant-macro count-cadence MAE <=5 steps/min; >=95% trials have >=2 straight-region detections',
        limits='reference-bout mode uses reference segmentation; autonomous mode never sees metadata except fs; reference regions used only for scoring, not autonomous prediction; no independent gold standard',
        hashes={str(p.relative_to(ROOT)):sha(p) for p in [Path(__file__),ROOT/'src/features/lower_back_events.py',ROOT/'src/features/voisard.py']},
        packages={x:importlib.metadata.version(x) for x in ['mobgap','numpy','scipy','pandas','numba','tpcp']})
    if (OUT/'protocol.json').exists() and not (OUT/'failed_raw_timeline_protocol.json').exists():
        (OUT/'failed_raw_timeline_protocol.json').write_bytes((OUT/'protocol.json').read_bytes())
    (OUT/'protocol.json').write_text(json.dumps(protocol,indent=2))
    rows, events, bouts, ledger = [], [], [], []
    for index,path in enumerate(paths):
        m=json.loads(path.read_text());trial=path.stem.removesuffix('_meta');person='voisard_2025:'+m['subject'];fs=float(m['freq'])
        rawpath=path.parent/(trial+'_raw_data_LB.txt')
        native=pd.read_csv(rawpath,sep='\t')
        processed_path=next(path.parent.glob('*processed_data.txt'))
        processed=pd.read_csv(processed_path,sep='\t')
        raw=processed[['LB_Acc_X','LB_Acc_Y','LB_Acc_Z','LB_Gyr_X','LB_Gyr_Y','LB_Gyr_Z']].copy()
        raw.columns=COLS
        valid=np.flatnonzero(raw[COLS[:3]].notna().any(axis=1))
        if not len(valid):raise ValueError(f'No lower-back data: {trial}')
        raw=raw.iloc[:valid[-1]+1]
        refall=np.array(sorted(e[1] for side in ['leftGaitEvents','rightGaitEvents'] for e in m[side]),dtype=int)
        lp,la=_events_outside_uturn(m['leftGaitEvents'],m['uturnBoundaries']);rp,ra=_events_outside_uturn(m['rightGaitEvents'],m['uturnBoundaries'])
        bounds=[(a,b+1) for a,b in _walking_bounds(lp+rp,la+ra)]
        reference_valid=bool(bounds) and all(0<=a<b<=len(raw) for a,b in bounds)
        if not reference_valid:bounds=[]
        duration=sum(b-a for a,b in bounds)/fs if bounds else np.nan
        refs=[refall[(refall>=a)&(refall<b)] for a,b in bounds]
        ledger.append(dict(participant=person,trial=trial,metadata_sha256=sha(path),raw_sha256=sha(rawpath),processed_sha256=sha(processed_path),
            samples=len(raw),native_rows=len(native),native_counter_gaps=int(native.PacketCounter.diff().gt(1).sum()),trailing_rows_trimmed=len(processed)-len(raw)))
        for mode in ['reference_bouts','autonomous']:
            detected=[];statuses=[];messages=[];pred_bouts=[]
            if not reference_valid:messages.append('reference bounds outside available processed lower-back timeline')
            spans=bounds if mode=='reference_bouts' else [(0,len(raw))]
            for start,end in spans:
                try:
                    with warnings.catch_warnings(record=True) as caught:
                        warnings.simplefilter('always')
                        result=detect_lower_back_events(raw.iloc[start:end],fs,known_gait=mode=='reference_bouts')
                    messages.extend(str(w.message) for w in caught)
                    statuses.append(result['status'])
                    detected.extend(start+e for e in result['events'])
                    pred_bouts.extend(dict(start=start+r['start'],end=start+r['end'],contacts=r['contacts'],cadence=r['cadence']) for r in result['bouts'])
                except Exception as exc:
                    statuses.append('exception');messages.append(type(exc).__name()+': '+str(exc))
            detected=np.array(sorted(set(detected)),dtype=int)
            matches=[];nref=npred=0
            for (a,b),ref in zip(bounds,refs):
                pred=detected[(detected>=a)&(detected<b)]
                matches.append(match_events(ref,pred,round(.15*fs)));nref+=len(ref);npred+=len(pred)
            tp=sum(x['tp'] for x in matches);fp=sum(x['fp'] for x in matches);fn=sum(x['fn'] for x in matches)
            residuals=[r/fs for x in matches for r in x['residuals']]
            lo=min(e[0] for side in ['leftGaitEvents','rightGaitEvents'] for e in m[side]);hi=int(refall.max())+1
            idle_events=int(((detected<lo)|(detected>=hi)).sum()) if reference_valid else 0
            idle_seconds=(lo+len(raw)-hi)/fs if reference_valid else 0
            rows.append(dict(participant=person,trial=trial,pathology=m['pathologyKey'],sensor=m['sensor'],mode=mode,
                status='|'.join(statuses),warnings=' | '.join(messages),reference_valid=reference_valid,tp=tp,fp=fp,fn=fn,reference_contacts=nref,predicted_contacts=npred,
                f1=2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else np.nan,cadence_abs_error=abs(npred-nref)*60/duration,
                cadence_bias=(npred-nref)*60/duration,cadence_available=npred>=2,
                matched_timing_mae_ms=np.mean(np.abs(residuals))*1000 if residuals else np.nan,
                idle_events=idle_events,idle_seconds=idle_seconds,straight_seconds=duration))
            events.extend(dict(participant=person,trial=trial,mode=mode,sample=int(e)) for e in detected)
            bouts.extend(dict(participant=person,trial=trial,mode=mode,**r) for r in pred_bouts)
        if (index+1)%150==0:print('processed',index+1,'/',len(paths),flush=True)
    trials=pd.DataFrame(rows);trials.to_csv(OUT/'trial_metrics.csv',index=False)
    pd.DataFrame(events).to_csv(OUT/'detected_contacts.csv',index=False)
    pd.DataFrame(bouts).to_csv(OUT/'detected_bouts.csv',index=False)
    pd.DataFrame(ledger).to_csv(OUT/'input_ledger.csv',index=False)
    people=trials.groupby(['participant','pathology','mode'],as_index=False).agg(trials=('trial','size'),tp=('tp','sum'),fp=('fp','sum'),fn=('fn','sum'),
        cadence_mae=('cadence_abs_error','mean'),cadence_bias=('cadence_bias','mean'),coverage=('cadence_available','mean'),idle_events=('idle_events','sum'),idle_seconds=('idle_seconds','sum'))
    people['f1']=2*people.tp/(2*people.tp+people.fp+people.fn)
    people.to_csv(OUT/'participant_metrics.csv',index=False)
    summary=[]
    for mode in people['mode'].unique():
        for name,groups in [('HS',['HS']),('CVA',['CVA']),('other',['ACL','CIPN','HOA','KOA','PD','RIL'])]:
            f=people[people['mode'].eq(mode)&people.pathology.isin(groups)];t=trials[trials['mode'].eq(mode)&trials.pathology.isin(groups)]
            summary.append(dict(mode=mode,group=name,people=len(f),trials=len(t),f1=f.f1.mean(),cadence_mae=f.cadence_mae.mean(),
                trial_coverage=t.cadence_available.mean(),invalid_reference_trials=int((~t.reference_valid).sum()),idle_events=int(t.idle_events.sum()),idle_minutes=t.idle_seconds.sum()/60,
                passed=bool(f.f1.mean()>=.85 and f.cadence_mae.mean()<=5 and t.cadence_available.mean()>=.95)))
    summary=pd.DataFrame(summary);summary.to_csv(OUT/'summary.csv',index=False)
    people.groupby(['mode','pathology']).agg(people=('participant','size'),f1=('f1','mean'),cadence_mae=('cadence_mae','mean'),coverage=('coverage','mean')).to_csv(OUT/'pathology_summary.csv')
    assert len(trials)==2*len(paths) and not trials.duplicated(['trial','mode']).any()
    (OUT/'verification.json').write_text(json.dumps(dict(trials=len(paths),participants=people.participant.nunique(),all_trials_accounted=True,
        promoted=False,all_groups_passed=bool(summary[summary['mode'].eq('autonomous')].passed.all()),hashes={p.name:sha(p) for p in OUT.glob('*.csv')}),indent=2))
    print(summary.to_string(index=False),flush=True)


if __name__=='__main__':main()
