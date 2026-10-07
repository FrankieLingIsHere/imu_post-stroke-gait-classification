"""Known-answer inputs for tests of the actual Android Java metric calculation.
Not gait synthesis, not participant data and not a physical validation dataset.
"""
import json
import numpy as np
from scipy.spatial.transform import Rotation
from pathlib import Path


def write_native_fixture(destination):
    t=np.arange(0,16.001,.005)
    def rotations(t):
        return Rotation.from_euler('xyz',np.column_stack([.3*np.sin(.7*t),.2*np.cos(.9*t),.25*np.sin(.6*t)])).as_matrix()
    R=rotations(t);rdd=np.gradient(np.gradient(R,.005,axis=0),.005,axis=0)
    pdd=np.column_stack([-.3*.8**2*np.sin(.8*t),-.2*1.1**2*np.cos(1.1*t),-.15*1.3**2*np.sin(1.3*t)])
    scale=2.7;bias=np.array([.02,-.01,.03]);lever=np.array([.01,-.01,.02]);gravity=np.array([0.,0.,-9.80665])
    force=np.einsum('nji,nj->ni',R,scale*pdd-rdd@lever-gravity)+bias
    gyro=Rotation.from_matrix(R[:-1].transpose(0,2,1)@R[1:]).as_rotvec()/.005;gyro=np.vstack([gyro,gyro[-1]])
    pt=np.arange(0,16.001,.08);Q=rotations(pt);position=np.column_stack([.2*pt+.3*np.sin(.8*pt),.2*np.cos(1.1*pt),.15*np.sin(1.3*pt)])
    fixture={'expectedScale':scale,'source':'synthetic-known-answer-not-phone-data',
             'imu':[{'t':float(v),'accel':force[i].tolist(),'gyro':gyro[i].tolist()} for i,v in enumerate(t)],
             'poses':[{'t':float(v),'Q':Q[i].tolist(),'p':position[i].tolist()} for i,v in enumerate(pt)]}
    Path(destination).write_text(json.dumps(fixture),encoding='utf-8')
    return Path(destination)


def write_lens_fixture(destination):
    """Known lens projections, not phone recordings or clinical validation."""
    import cv2
    rng=np.random.default_rng(619)
    K=np.array([[513.,0,324.],[0,507.,238.],[0,0,1.]])
    D=np.array([-.08,.02,.001,-.0006,.003])
    object_points=np.array([[x,y,0.] for y in range(1,7) for x in range(1,9)])
    center=np.array([4.5,3.5,0.]);views=[]
    for i in range(300):
        rv=rng.uniform([-.6,-.6,-.12],[.6,.6,.12])
        R=Rotation.from_rotvec(rv).as_matrix()
        tv=np.array([rng.uniform(-3.8,3.8),rng.uniform(-2.5,2.5),rng.uniform(12,18)])-R@center
        points=cv2.projectPoints(object_points,rv,tv,K,D)[0].reshape(-1,2)
        if np.any(points[:,0]<8) or np.any(points[:,0]>=632) or np.any(points[:,1]<8) or np.any(points[:,1]>=472):
            continue
        points+=rng.normal(0,.08,points.shape)
        views.append({'points':points.tolist(),'ids':list(range(48)),'sharpness':100.,'timestampNs':(i+1)*300000000})
    fixture={'source':'synthetic-known-answer-not-phone-data','expectedCameraMatrix':K.tolist(),
             'expectedDistortion':D.tolist(),'views':views}
    Path(destination).write_text(json.dumps(fixture),encoding='utf-8')
    return Path(destination)
