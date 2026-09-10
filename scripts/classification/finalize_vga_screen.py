"""Required strict-float32 threshold finalization; no fitting or test selection."""
from pathlib import Path
import numpy as np
import pandas as pd
import json,hashlib
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'data/processed/vga_screen_v1'

def strict_threshold(scores):
    normal=np.sort(np.asarray(scores,dtype='float32'))
    if len(normal)==0 or not np.isfinite(normal).all():raise ValueError('Finite normal calibration scores required')
    return np.nextafter(normal[int(np.ceil(.9*len(normal)))-1],np.float32(np.inf))

def main():
    archive=OUT/'initial_threshold_outputs';archive.mkdir(exist_ok=True)
    for name in ['predictions.csv','calibration.csv','external_predictions.csv','metrics.csv','external_metrics.csv','severity.csv','decision.json']:
        p=OUT/name
        if not (archive/name).exists():(archive/name).write_bytes(p.read_bytes())
    cal=pd.read_csv(archive/'calibration.csv',dtype={'score':'float32'})
    pred=pd.read_csv(archive/'predictions.csv',dtype={'score':'float32'});ext=pd.read_csv(archive/'external_predictions.csv',dtype={'score':'float32'})
    changes=[]
    for (seed,fold),g in cal.groupby(['seed','outer_fold']):
        normal=np.sort(g.loc[g.target.eq(0),'score'].to_numpy(dtype='float32'))
        cut=normal[int(np.ceil(.9*len(normal)))-1]
        threshold=strict_threshold(normal)
        assert threshold>cut and not np.float32(cut)>=threshold
        for name,table in [('calibration',cal),('predictions',pred),('external',ext)]:
            mask=table.seed.eq(seed)&table.outer_fold.eq(fold);before=table.loc[mask,'positive'].copy()
            table.loc[mask,'threshold']=float(threshold);table.loc[mask,'positive']=table.loc[mask,'score'].ge(threshold)
            changes.append(dict(table=name,seed=int(seed),fold=int(fold),changed=int((before!=table.loc[mask,'positive']).sum())))
    cal.to_csv(OUT/'calibration.csv',index=False);pred.to_csv(OUT/'predictions.csv',index=False);ext.to_csv(OUT/'external_predictions.csv',index=False)
    metrics=[]
    for scope,g0 in [('full',pred),('matched',pred[pred.matched])]:
        from sklearn.metrics import roc_auc_score
        for seed,g in g0.groupby('seed'):
            d=dict(scope=scope,seed=int(seed),auroc=float(roc_auc_score(g.target,g.score)))
            for name,mask in [('normal',g.target.eq(0)),('impaired',g.target.eq(1)),('healthy_group',g.pathology.eq('healthy')),('diagnosed_normal',g.target.eq(0)&g.pathology.ne('healthy'))]:
                d[name+'_n']=int(mask.sum());d[name+'_alerts']=int(g.positive[mask].sum())
            metrics.append(d)
    m=pd.DataFrame(metrics);m.to_csv(OUT/'metrics.csv',index=False)
    pred.groupby(['seed','vga']).agg(n=('participant','size'),alerts=('positive','sum')).to_csv(OUT/'severity.csv')
    ext.groupby(['seed','outer_fold','condition']).agg(n=('participant','size'),alerts=('positive','sum')).to_csv(OUT/'external_metrics.csv')
    g=m[m.scope.eq('full')];passed=bool(((g.normal_alerts/g.normal_n<=.1)&(g.impaired_alerts/g.impaired_n>=.7)).all())
    (OUT/'decision.json').write_text(json.dumps(dict(fits=18,passed=passed,new_target='clinician VGA>0',clinical_validation=False,strict_float32_boundary_corrected=True),indent=2))
    pd.DataFrame(changes).to_csv(OUT/'threshold_correction.csv',index=False)
    (OUT/'finalizer_sha256.txt').write_text(hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    print(pd.DataFrame(changes).groupby('table').changed.sum().to_string())

if __name__=='__main__':main()
