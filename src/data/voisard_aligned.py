"""Native Voisard acceleration on the shared packet clock, without filtering."""
from pathlib import Path
import numpy as np
import pandas as pd


def align_packets(frame, origin, max_gap_samples=150):
    """Keep unsupported edges NaN; interpolate only bounded interior gaps.

    origin is the acquisition's common counter origin, never inferred from gait
    annotations. Counter rounding tolerates floating point representation only.
    """
    counters=frame.PacketCounter.to_numpy(float)
    rounded=np.rint(counters)
    if not np.isfinite(counters).all() or not np.allclose(counters,rounded,rtol=0,atol=1e-6):
        raise ValueError('Nonintegral/nonfinite packet counters')
    # XSens 16-bit packet rollover; all other backward jumps remain errors.
    jumps=np.diff(rounded)
    wrapped=jumps < -32768
    rounded=rounded+np.r_[0,np.cumsum(wrapped)]*65536
    if np.any(np.diff(rounded)<=0):raise ValueError('Duplicate/reset counters require explicit handling')
    ix=(rounded-int(origin)).astype(int)
    if ix[0]<0:raise ValueError('Origin later than first packet')
    x=frame[['Acc_X','Acc_Y','Acc_Z']].to_numpy(float)
    result=np.full((ix[-1]+1,3),np.nan)
    result[ix]=x
    for i,gap in enumerate(np.diff(ix)-1):
        if 0<gap<=max_gap_samples and np.isfinite(x[i:i+2]).all():
            for j in range(3):result[ix[i]+1:ix[i+1],j]=np.linspace(x[i,j],x[i+1,j],int(gap)+2)[1:-1]
    return result


def load_aligned_lower_back(trial_dir: Path, trial: str):
    paths=[trial_dir/f'{trial}_raw_data_{s}.txt' for s in ['HE','LB','LF','RF']]
    first=[pd.read_csv(p,sep='\t',usecols=['PacketCounter'],nrows=1).PacketCounter.iloc[0] for p in paths]
    origin=int(round(min(first)))
    raw=pd.read_csv(paths[1],sep='\t')
    return align_packets(raw,origin),dict(origin=origin,lb_first=int(round(raw.PacketCounter.iloc[0])),native_rows=len(raw),
                                         gap_count=int(raw.PacketCounter.diff().gt(1.5).sum()))
