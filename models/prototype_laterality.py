"""Local research prototype: gyro + supplied contacts -> left/right side.

This does not detect contacts or classify stroke. Load only the locally built,
trusted joblib artifact. Gyro axes/units must match the TVS native training frame.
"""
from pathlib import Path
import argparse,json
import numpy as np
import pandas as pd
import joblib
from scipy.signal import butter,sosfiltfilt


def features(gyro,contacts):
    x=np.asarray(gyro,dtype=float);indices=np.asarray(contacts)
    if x.ndim!=2 or x.shape[1]!=3 or len(x)<32 or not np.isfinite(x).all():
        raise ValueError('Expected finite (samples,3) gyro with at least 32 samples')
    if indices.ndim!=1 or not np.isfinite(indices).all() or not np.equal(indices,np.rint(indices)).all():
        raise ValueError('Contacts must be zero-based integer sample indices')
    indices=indices.astype(int)
    if len(set(indices))!=len(indices) or (indices<0).any() or (indices>=len(x)).any():
        raise ValueError('Duplicate or out-of-bounds contacts')
    filtered=sosfiltfilt(butter(4,[.5,2],btype='bandpass',fs=100,output='sos'),x,axis=0)
    first=np.gradient(filtered,axis=0);second=np.gradient(first,axis=0)
    return pd.DataFrame(np.c_[filtered,first,second][indices],columns=[f'f{k}' for k in range(9)])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model',type=Path,required=True)
    parser.add_argument('--gyro',type=Path,required=True,help='NPY, native TVS-frame gyro at 100Hz')
    parser.add_argument('--contacts',type=Path,required=True,help='NPY, zero-based sample indices')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    artifact=joblib.load(args.model)
    if artifact['task']!='contact_laterality' or artifact['sampling_hz']!=100:raise ValueError('Unsupported model contract')
    gyro=np.load(args.gyro,allow_pickle=False);contacts=np.load(args.contacts,allow_pickle=False)
    table=features(gyro,contacts)
    side=artifact['model'].predict(table) if len(table) else np.array([],dtype=int)
    pd.DataFrame({'ic_sample':contacts,'side':np.where(side==0,'left','right'),'status':'research_prototype'}).to_csv(args.output,index=False)
    print(json.dumps({'contacts':len(side),'task':'contact_laterality','stroke_output':False}))


if __name__=='__main__':main()
