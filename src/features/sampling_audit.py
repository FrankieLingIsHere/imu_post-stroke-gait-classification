"""Paired bandwidth/peak-stability audit. No diagnostic classification."""
from fractions import Fraction
import numpy as np
from scipy.signal import butter, sosfiltfilt, resample_poly, welch, find_peaks


def reduce_rate(x, fs, target):
    ratio = Fraction(target / fs).limit_denominator(10000)
    return resample_poly(x, ratio.numerator, ratio.denominator, axis=0)


def peaks(x, fs):
    """Fixed 0.3-3 Hz magnitude peaks, NOT the app estimator or heel strikes."""
    norm = np.linalg.norm(x, axis=1)
    y = sosfiltfilt(butter(4, [.3, 3], btype='bandpass', fs=fs, output='sos'), norm)
    return find_peaks(y, distance=max(1, round(.3*fs)), prominence=.35*np.std(y))[0]/fs


def audit_segment(x, fs, target):
    x = np.asarray(x, float)
    if x.ndim != 2 or x.shape[1] != 3 or not np.isfinite(x).all() or len(x)<fs*6:
        raise ValueError('Need six seconds of finite three-axis signal')
    f, p = welch(x, fs=fs, nperseg=min(len(x),round(fs*4)), axis=0)
    p = p.sum(axis=1); dynamic=p[f>=.3].sum()
    y = reduce_rate(x,fs,target)
    # Same 8 Hz analysis band on both versions; assess interpolation error in its interior.
    source=sosfiltfilt(butter(4,8,fs=fs,output='sos'),x,axis=0)
    reduced=sosfiltfilt(butter(4,8,fs=target,output='sos'),y,axis=0)
    t=np.arange(len(x))/fs; ty=np.arange(len(y))/target
    restored=np.column_stack([np.interp(t,ty,reduced[:,j]) for j in range(3)])
    keep=(t>=1)&(t<=min(t[-1],ty[-1])-1)
    baseline=source[keep]; comparison=restored[keep]
    scale=np.sqrt(np.mean((baseline-baseline.mean(axis=0))**2))
    a=peaks(x,fs); b=peaks(y,target)
    a=a[(a>=1)&(a<=t[-1]-1)];b=b[(b>=1)&(b<=t[-1]-1)]
    # One-to-one nearest candidate matching within 100 ms, labels not used.
    errors=[]; available=list(b)
    for v in a:
        if available:
            i=int(np.argmin(np.abs(np.array(available)-v)))
            if abs(available[i]-v)<=.1: errors.append(abs(available.pop(i)-v))
    return dict(target_hz=target,seconds=len(x)/fs,
        energy_above_target_nyquist=float(p[f>=target/2].sum()/dynamic) if dynamic>0 else np.nan,
        energy_above_8hz=float(p[f>8].sum()/dynamic) if dynamic>0 else np.nan,
        band8_nrmse=float(np.sqrt(np.mean((baseline-comparison)**2))/scale) if scale>1e-10 else np.nan,
        peak_count_native=len(a),peak_count_reduced=len(b),
        peak_match_f1=2*len(errors)/(len(a)+len(b)) if len(a)+len(b) else np.nan,
        peak_shift_ms=float(np.mean(errors)*1000) if errors else np.nan,
        count_cadence_delta=60*abs(len(a)-len(b))/max(t[-1]-2,1))
