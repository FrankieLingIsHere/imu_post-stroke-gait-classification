"""Nominal-ML, stride-resolved amplitude harmonic ratio."""
import numpy as np


def stride_log_hr(signal):
    x=np.asarray(signal,dtype=float)
    if len(x)<50 or not np.isfinite(x).all():
        return np.nan
    # Periodic interpolation avoids duplicating the end point in the FFT.
    phase=np.arange(128)*len(x)/128
    y=np.interp(phase,np.arange(len(x)+1),np.r_[x,x[0]])
    amp=np.abs(np.fft.rfft(y-y.mean()))[1:11]
    odd,even=amp[::2].sum(),amp[1::2].sum()
    if odd+even<=1e-12 or even<=1e-8*(odd+even):
        return np.nan
    return float(np.log1p(odd/even))


def trial_hr(y,left,right,turn):
    segments=[[[],[]],[[],[]]]
    invalid=0
    for side,events in enumerate([left,right]):
        previous=-np.inf
        for p in events:
            if len(p)!=2 or not np.isfinite(p).all() or not previous<p[0]<p[1]:
                for seg in segments: seg[side].append(None)
                invalid+=1
                continue
            previous=p[1]
            if p[1]<turn[0]: segments[0][side].append(p)
            elif p[0]>turn[1]: segments[1][side].append(p)
    values=[]
    for seg in segments:
        for side in [0,1]:
            opposite=[p[1] for p in seg[1-side] if p is not None]
            for a,b in zip(seg[side],seg[side][1:]):
                if a is None or b is None or not a[0]<a[1]<b[0]<b[1] or sum(a[1]<c<b[1] for c in opposite)!=1:
                    invalid+=1;continue
                start,end=int(a[1]),int(b[1])
                if start!=a[1] or end!=b[1] or start<0 or end>len(y):
                    invalid+=1;continue
                value=stride_log_hr(y[start:end])
                if np.isfinite(value):values.append(value)
                else:invalid+=1
    return dict(ml_log_hr=float(np.mean(values)) if len(values)>=2 else np.nan,
                valid_strides=len(values),invalid_strides=invalid)
