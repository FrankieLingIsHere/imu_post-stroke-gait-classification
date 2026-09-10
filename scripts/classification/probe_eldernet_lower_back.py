"""Locked frozen-encoder transfer probe on actual lower-back XYZ.

Upstream ElderNet: Copyright 2022, University of Oxford; academic-use license
in models/pretrained/eldernet-437a38b/LICENSE.md applies to the reused encoder.
"""
from pathlib import Path
import sys, json, hashlib, importlib.util
import numpy as np
import pandas as pd
import torch
from scipy.signal import resample_poly
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from src.data.voisard_aligned import load_aligned_lower_back
from src.features.voisard import _events_outside_uturn, _walking_bounds
UP = ROOT / 'models/pretrained/eldernet-437a38b'
OUT = ROOT / 'data/processed/eldernet_lower_back_v1'
SEED = 20260909


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def to_eldernet_window(chunk):
    """Native Voisard m/s^2 -> g, then anti-aliased 100 -> 30 Hz."""
    chunk = np.asarray(chunk)
    if chunk.shape != (1000, 3) or not np.isfinite(chunk).all():
        raise ValueError('Expected finite 10-second native XYZ window')
    return resample_poly(chunk / 9.80665, 3, 10, axis=0).T.astype('float32')


def build_encoder(pretrained):
    # Import upstream under its expected names in this standalone process.
    spec = importlib.util.spec_from_file_location('models', UP / 'models.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules['models'] = module
    spec.loader.exec_module(module)
    sys.path.insert(0, str(UP))
    base = module.Resnet(feature_extractor=torch.nn.Sequential())
    model = module.ElderNet(base.feature_extractor, linear_model_output_size=128,
                           is_simclr=True)
    # Upstream constructors reset RNG internally: explicitly initialize the
    # matched random control after construction with the protocol seed.
    torch.manual_seed(SEED)
    for layer in model.modules():
        if isinstance(layer, (torch.nn.Conv1d, torch.nn.Linear)):
            torch.nn.init.kaiming_normal_(layer.weight, mode='fan_out', nonlinearity='relu')
            if layer.bias is not None:
                torch.nn.init.zeros_(layer.bias)
    if pretrained:
        state = torch.load(UP / 'weights/gait_speed_weights.pt', map_location='cpu', weights_only=True)
        state = {k:v for k,v in state.items() if not k.startswith('regressor.')}
        model.load_state_dict(state, strict=True)
    return model.eval().requires_grad_(False)


def fit_head(train, columns):
    assert set(train.target) == {0,1,2}
    weights = train.target.map({t:m/train.target.eq(t).sum() for t,m in [(0,.25),(1,.5),(2,.25)]}) * len(train)
    return make_pipeline(StandardScaler(), LogisticRegression(C=1.,max_iter=3000,random_state=SEED)).fit(
        train[columns], train.target.eq(1), logisticregression__sample_weight=weights)


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    if (OUT/'decision.json').exists():
        raise FileExistsError('Completed experiment: inspect saved result instead of rerunning')
    torch.set_num_threads(4)
    sources = [ROOT/'docs/classification/ELDERNET_LOWER_BACK_PROTOCOL.md', Path(__file__),
        ROOT/'data/processed/directional_hr_v1/participants_main.csv',
        ROOT/'data/processed/bilateral_phase_v1/trial_features.csv',
        ROOT/'src/data/voisard_aligned.py', UP/'models.py', UP/'weights/gait_speed_weights.pt']
    (OUT/'manifest.json').write_text(json.dumps({str(p.relative_to(ROOT)):sha(p) for p in sources},indent=2))
    acquisition = json.loads((UP/'acquisition.json').read_text())
    for item in acquisition['files']:
        assert sha(UP/item['path']) == item['sha256']
    people = pd.read_csv(sources[2])
    trials = pd.read_csv(sources[3])
    paths = {p.stem.removesuffix('_meta'):p for p in (ROOT/'data/raw/voisard_2025/data').glob('*/*/*/*/*_meta.json')}
    windows=[]; rows=[]; ledger=[]
    for r in trials.itertuples():
        p=paths[r.trial]; assert sha(p)==r.metadata_sha256
        m=json.loads(p.read_text()); assert m['freq']==100
        count=0; invalid=0
        if r.reference_valid:
            left=_events_outside_uturn(m.get('leftGaitEvents') or [],m['uturnBoundaries'])
            right=_events_outside_uturn(m.get('rightGaitEvents') or [],m['uturnBoundaries'])
            bounds=_walking_bounds(left[0]+right[0],left[1]+right[1])
            if any(b-a>=1000 for a,b in bounds):
                raw,_=load_aligned_lower_back(p.parent,r.trial)
                for a,b in bounds:
                    for start in range(int(a),min(int(b),len(raw))-999,500):
                        chunk=raw[start:start+1000]
                        if not np.isfinite(chunk).all(): invalid+=1;continue
                        windows.append(to_eldernet_window(chunk))
                        rows.append(dict(participant=r.participant,trial=r.trial,start=start,
                                         raw_sha256=sha(p.parent/(r.trial+'_raw_data_LB.txt'))))
                        count+=1
        ledger.append(dict(participant=r.participant,trial=r.trial,windows=count,invalid_windows=invalid,
                           reference_valid=bool(r.reference_valid)))
    ledger=pd.DataFrame(ledger);ledger.to_csv(OUT/'trial_coverage.csv',index=False)
    coverage=people[['participant','target','pathology','fold','matched']].merge(
        ledger.groupby('participant').windows.sum(),on='participant',how='left',validate='one_to_one')
    coverage['available']=coverage.windows.gt(0)
    coverage.to_csv(OUT/'participant_coverage.csv',index=False)
    coverage.groupby('pathology').agg(n=('participant','size'),available=('available','sum')).to_csv(OUT/'coverage_by_pathology.csv')
    print(coverage.groupby('pathology').available.agg(['sum','count']).to_string(),flush=True)
    x=np.stack(windows); meta=pd.DataFrame(rows);meta.to_csv(OUT/'window_metadata.csv',index=False)
    assert x.shape[1:]==(3,300) and np.isfinite(x).all()
    device='cuda' if torch.cuda.is_available() else 'cpu'
    predictions=[]; inner_rows=[]; thresholds=[]
    for arm in ['random','pretrained']:
        model=build_encoder(arm=='pretrained').to(device)
        embeds=[]
        with torch.inference_mode():
            for i in range(0,len(x),64):
                embeds.append(model(torch.from_numpy(x[i:i+64]).to(device)).cpu().numpy())
        z=np.concatenate(embeds);assert z.shape==(len(x),128) and np.isfinite(z).all()
        columns=[f'e{i}' for i in range(128)]
        frame=pd.concat([meta[['participant','trial']],pd.DataFrame(z,columns=columns)],axis=1)
        pooled=frame.groupby(['participant','trial'])[columns].mean().groupby('participant').mean()
        data=coverage[coverage.available].merge(pooled,on='participant',validate='one_to_one')
        data.to_csv(OUT/f'{arm}_embeddings.csv',index=False)
        for scope,subset in [('all_available',data),('matched_available',data[data.matched])]:
            for fold in sorted(subset.fold.unique()):
                train,test=subset[subset.fold.ne(fold)],subset[subset.fold.eq(fold)]
                assert not set(train.participant)&set(test.participant)
                assert not set(train.loc[train.target.eq(2),'pathology'])&set(test.loc[test.target.eq(2),'pathology'])
                parts=[]
                for inner,(a,b) in enumerate(StratifiedKFold(3,shuffle=True,random_state=SEED).split(train,train.target)):
                    fit,val=train.iloc[a],train.iloc[b]
                    head=fit_head(fit,columns)
                    row=val[['participant','target','pathology']].copy()
                    row['score']=head.predict_proba(val[columns])[:,1]
                    row['arm'],row['scope'],row['outer_fold'],row['inner_fold']=arm,scope,int(fold),inner
                    parts.append(row)
                scores=pd.concat(parts);assert scores.participant.is_unique and set(scores.participant)==set(train.participant)
                inner_rows.append(scores)
                stroke=scores.loc[scores.target.eq(1),'score'].to_numpy()
                threshold=float(np.sort(stroke)[::-1][int(np.ceil(.9*len(stroke)))-1])
                thresholds.append(dict(arm=arm,scope=scope,fold=int(fold),threshold=threshold))
                head=fit_head(train,columns)
                row=test[['participant','target','pathology','fold']].copy()
                row['score']=head.predict_proba(test[columns])[:,1]
                row['positive']=row.score.ge(threshold)
                row['arm'],row['scope'],row['threshold']=arm,scope,threshold
                predictions.append(row)
        print(arm,'encoding and nested head fits complete',flush=True)
    pred=pd.concat(predictions);pred.to_csv(OUT/'predictions.csv',index=False)
    pd.concat(inner_rows).to_csv(OUT/'inner_predictions.csv',index=False)
    pd.DataFrame(thresholds).to_csv(OUT/'thresholds.csv',index=False)
    metrics=[]
    for (scope,arm),g in pred.groupby(['scope','arm']):
        assert g.participant.is_unique
        d=dict(scope=scope,arm=arm,n=len(g),auroc=float(roc_auc_score(g.target.eq(1),g.score)))
        for t,name in [(0,'healthy'),(1,'stroke'),(2,'other')]:
            h=g[g.target.eq(t)];d[name+'_n']=len(h);d[name+'_positive']=int(h.positive.sum())
        h=g[g.pathology.isin(['CIPN','PD','RIL'])];d['neuro_n']=len(h);d['neuro_fp']=int(h.positive.sum())
        metrics.append(d)
    metrics=pd.DataFrame(metrics);metrics.to_csv(OUT/'metrics.csv',index=False)
    pred.groupby(['scope','arm','pathology']).agg(n=('participant','size'),positive=('positive','sum')).to_csv(OUT/'pathology_counts.csv')
    gates=[]
    for scope,g in metrics.groupby('scope'):
        g=g.set_index('arm');a,b=g.loc['random'],g.loc['pretrained']
        gates.append(dict(scope=scope,passed=bool((a.neuro_fp-b.neuro_fp)/a.neuro_n>=.05 and b.stroke_positive>=a.stroke_positive and b.healthy_positive<=a.healthy_positive)))
    result=dict(promising=all(g['passed'] for g in gates),gates=gates,device=device,
                windows=len(x),available_participants=int(coverage.available.sum()),total_participants=len(coverage),
                head_fits=48,encoder_finetuned=False,independent_validation=False)
    (OUT/'decision.json').write_text(json.dumps(result,indent=2))
    print(metrics.to_string(index=False),flush=True);print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':main()
