"""Optional validity wrapper for research inference; not a gait detector.

Rejected windows have no score. They must never be counted as healthy negatives.
The frozen release API and weights remain unchanged.
"""
import numpy as np
from .predict_lower_back import predict_windows, validate_bundle


def screen_windows(windows):
    values=np.asarray(windows,dtype=np.float32)
    if values.ndim!=3 or values.shape[1:]!=(500,1) or not len(values):
        raise ValueError('Expected nonempty (n_windows, 500, 1) input')
    finite=np.isfinite(values).all(axis=(1,2))
    reasons=[]
    for index,row in enumerate(values):
        if not finite[index]:reasons.append('nonfinite_signal')
        elif np.all(row==row[0]):reasons.append('constant_magnitude')
        else:reasons.append(None)
    return values,np.asarray([r is None for r in reasons]),reasons


def predict_windows_with_validity(bundle,windows,batch_size=256,device='cpu'):
    """Return per-window score/status; nonconstant does not certify valid gait."""
    validate_bundle(bundle)
    if batch_size<=0:raise ValueError('batch_size must be positive')
    values,eligible,reasons=screen_windows(windows)
    scores=iter(predict_windows(bundle,values[eligible],batch_size,device)) if eligible.any() else iter(())
    return [dict(window_index=i,status='scored' if ok else 'rejected',
                 stroke_score=float(next(scores)) if ok else None,reason=reasons[i])
            for i,ok in enumerate(eligible)]


def main():
    import argparse
    import json
    from pathlib import Path
    from .predict_lower_back import load_bundle
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('checkpoint','manifest','windows','output'):
        parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    bundle=load_bundle(args.checkpoint,args.manifest)
    rows=predict_windows_with_validity(bundle,np.load(args.windows,allow_pickle=False))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x',encoding='utf8') as f:
        json.dump(dict(scope='research window scores; validity screening is not a gait detector',
                       scored=sum(r['status']=='scored' for r in rows),
                       rejected=sum(r['status']=='rejected' for r in rows),windows=rows),f,indent=2,allow_nan=False)


if __name__=='__main__':main()
