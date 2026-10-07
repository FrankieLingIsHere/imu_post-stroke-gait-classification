"""Analytic camera/IMU control for the offline estimator harness, not gait data."""
import csv
from pathlib import Path

import cv2
import numpy as np


def motion(t):
    return np.array([.6*np.sin(.8*t), .35*np.cos(1.1*t), .12*t+.2*np.sin(1.3*t)])


def create_control(directory, duration=20):
    directory=Path(directory); directory.mkdir(parents=True,exist_ok=True)
    def rotation(t):
        angle=.15*np.sin(.9*t)
        return np.array([[np.cos(angle),-np.sin(angle),0], [np.sin(angle),np.cos(angle),0], [0,0,1]])
    with (directory/'imu.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['timestamp_ns','gx','gy','gz','ax','ay','az'])
        for t in np.arange(0,duration+.1,.005):
            acceleration=np.array([-.384*np.sin(.8*t),-.4235*np.cos(1.1*t),-.338*np.sin(1.3*t)])
            specific=rotation(t).T@(acceleration+np.array([0,0,9.80665]))
            w.writerow([round((1+t)*1e9),0,0,.135*np.cos(.9*t),*specific])
    rng=np.random.default_rng(47)
    world=rng.uniform([-2.5,-1.5,7],[2.5,1.5,12],size=(150,3))
    with (directory/'features.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['timestamp_ns','id','nx','ny','u','v','vx','vy'])
        previous=None
        for t in np.arange(.1,duration,1/30):
            camera=(world-motion(t))@rotation(t)
            normal=camera[:,:2]/camera[:,2,None]
            velocity=(normal-previous)*30 if previous is not None else np.zeros_like(normal)
            for ident,((x,y),(vx,vy)) in enumerate(zip(normal,velocity)):
                u,v=500*x+320,500*y+240
                if 1<u<639 and 1<v<479:w.writerow([round((1+t)*1e9),ident,x,y,u,v,vx,vy])
            previous=normal
    fs=cv2.FileStorage(str(directory/'reference.yaml'),cv2.FILE_STORAGE_WRITE)
    fs.write('extrinsicRotation',np.eye(3));fs.write('extrinsicTranslation',np.zeros((3,1)))
    for name,value in {'td':0.,'readout':0.,'acc_n':.08,'acc_w':.00004,'gyr_n':.004,'gyr_w':.000002}.items():
        fs.write(name,value)
    fs.release()


def evaluate_control(directory, prefix='reference'):
    with (Path(directory)/(prefix+'-states.csv')).open() as f:
        rows=[r for r in csv.DictReader(f) if r['initialized']=='1']
    if len(rows)<100:raise AssertionError('Control never maintains sufficient initialized poses')
    estimate=np.array([[float(r[k]) for k in ['px','py','pz']] for r in rows])
    true=np.array([motion(float(r['imu_time_s'])-1) for r in rows])
    # Only rigid gauge alignment, NEVER a similarity alignment that hides scale error.
    a,b=estimate-estimate.mean(axis=0),true-true.mean(axis=0)
    u,_,vt=np.linalg.svd(a.T@b)
    correction=np.diag([1,1,np.linalg.det(u@vt)])
    aligned=a@(u@correction@vt)+true.mean(axis=0)
    rmse=float(np.sqrt(np.mean(np.sum((aligned-true)**2,axis=1))))
    result={'kind':'analytic-nongait-harness-control','initializedFrames':len(rows),
            'rigidOnlyPositionRmseMetres':rmse,'similarityScaleFitted':False,
            'passed':rmse<.1,'independentDistanceValidation':False,'distanceReady':False}
    if not result['passed']:raise AssertionError(str(result))
    return result
