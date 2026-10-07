"""Conservative monocular tracking prototype for short native-camera captures.

One triangulated map preserves a common arbitrary scale across PnP frames.
No map reset, keyframe expansion, loop closure or relocalization is implemented:
tracking loss terminates the segment instead of silently changing scale.
"""
import cv2
import numpy as np


def initialize_map(first_pixels, second_pixels, K, D):
    a=cv2.undistortPoints(np.asarray(first_pixels,dtype=np.float64).reshape(-1,1,2),K,D).reshape(-1,2)
    b=cv2.undistortPoints(np.asarray(second_pixels,dtype=np.float64).reshape(-1,1,2),K,D).reshape(-1,2)
    if len(a)<40 or a.shape!=b.shape:raise ValueError('Too few corresponding scene features')
    unit_a=np.column_stack([a,np.ones(len(a))]);unit_b=np.column_stack([b,np.ones(len(b))])
    unit_a/=np.linalg.norm(unit_a,axis=1,keepdims=True);unit_b/=np.linalg.norm(unit_b,axis=1,keepdims=True)
    U,_,Vt=np.linalg.svd(unit_b.T@unit_a)
    correction=np.diag([1.,1.,np.linalg.det(U@Vt)])
    rotation_only=U@correction@Vt
    angular=np.rad2deg(np.arccos(np.clip(np.sum((unit_a@rotation_only.T)*unit_b,axis=1),-1,1)))
    if np.median(angular)<.15:
        raise ValueError('Rotation-only or insufficient translation parallax; distance withheld')
    E,mask=cv2.findEssentialMat(a,b,np.eye(3),method=cv2.RANSAC,prob=.999,threshold=.002)
    if E is None or E.shape!=(3,3):raise ValueError('No unique initial camera motion')
    _,R,t,mask=cv2.recoverPose(E,a,b,np.eye(3),mask=mask)
    rays_a=np.column_stack([a,np.ones(len(a))]);rays_b=np.column_stack([b,np.ones(len(b))])@R
    angle=np.rad2deg(np.arccos(np.clip(np.sum(rays_a*rays_b,axis=1)/
                             (np.linalg.norm(rays_a,axis=1)*np.linalg.norm(rays_b,axis=1)),-1,1)))
    X=cv2.triangulatePoints(np.c_[np.eye(3),np.zeros(3)],np.c_[R,t],a.T,b.T)
    X=(X[:3]/X[3]).T
    valid=(mask.ravel()!=0)&(X[:,2]>.05)&((X@R.T+t.ravel())[:,2]>.05)&(angle>1)&np.isfinite(X).all(axis=1)
    if valid.sum()<40:raise ValueError('Insufficient translation parallax; scale withheld')
    return {'pointsMap':X[valid],'secondPixels':np.asarray(second_pixels).reshape(-1,2)[valid],
            'rotationCameraWorld':R,'positionWorldCamera':(-R.T@t).ravel(),
            'scaleUnits':'arbitrary-map-units','distanceReady':False}


def locate_camera(points_map, pixels, K, D):
    if len(points_map)<30:raise ValueError('Tracking lost: too few mapped features')
    ok,rv,tv,inliers=cv2.solvePnPRansac(np.asarray(points_map,dtype=np.float64),
        np.asarray(pixels,dtype=np.float64),K,D,iterationsCount=150,reprojectionError=2.,confidence=.999)
    if not ok or inliers is None or len(inliers)<30 or len(inliers)/len(points_map)<.65:
        raise ValueError('Tracking lost: inconsistent map pose')
    selected=inliers.ravel();rv,tv=cv2.solvePnPRefineLM(points_map[selected],pixels[selected],K,D,rv,tv)
    projected=cv2.projectPoints(points_map[selected],rv,tv,K,D)[0].reshape(-1,2)
    rms=float(np.sqrt(np.mean((projected-pixels[selected])**2)))
    if rms>1.5:raise ValueError('Tracking lost: excessive reprojection residual')
    R=cv2.Rodrigues(rv)[0]
    return R,(-R.T@tv).ravel(),selected,rms


def track_native_frames(frames,K,D):
    """Frames are (hardware exposure time in seconds, unrotated grey image)."""
    iterator=iter(frames);first_time,first=next(iterator)
    pixels=cv2.goodFeaturesToTrack(first,maxCorners=800,qualityLevel=.01,minDistance=8)
    if pixels is None or len(pixels)<80:raise ValueError('Not enough visible scene texture')
    first_pixels=pixels.reshape(-1,2);previous_pixels=first_pixels.copy();previous=first
    mapping=None;poses=[];previous_time=first_time
    for timestamp,image in iterator:
        if not np.isfinite(timestamp) or timestamp<=previous_time or timestamp-previous_time>.3:
            raise ValueError('Camera clock gap: segment ended without distance')
        tracked,status,_=cv2.calcOpticalFlowPyrLK(previous,image,previous_pixels.astype(np.float32),None,
            winSize=(21,21),maxLevel=3,criteria=(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,30,.01))
        if tracked is None or status is None:raise ValueError('Optical tracking failed')
        back,back_status,_=cv2.calcOpticalFlowPyrLK(image,previous,tracked,None,winSize=(21,21),maxLevel=3)
        if back is None or back_status is None:raise ValueError('Optical tracking failed')
        good=(status.ravel()!=0)&(back_status.ravel()!=0)&(np.linalg.norm(back.reshape(-1,2)-previous_pixels,axis=1)<1.)
        current=tracked.reshape(-1,2)[good]
        if mapping is None:
            first_pixels=first_pixels[good]
            if len(current)<80:raise ValueError('Initial feature tracking lost')
            if np.median(np.linalg.norm(current-first_pixels,axis=1))>12:
                try:mapping=initialize_map(first_pixels,current,K,D)
                except ValueError:
                    if timestamp-first_time>4:raise ValueError('Unable to initialize a stable scene map')
                else:
                    current=mapping['secondPixels'];poses.append((timestamp,mapping['rotationCameraWorld'],mapping['positionWorldCamera']))
        else:
            mapping['pointsMap']=mapping['pointsMap'][good]
            R,p,keep,_=locate_camera(mapping['pointsMap'],current,K,D)
            mapping['pointsMap']=mapping['pointsMap'][keep];current=current[keep]
            poses.append((timestamp,R,p))
        previous=image;previous_pixels=current;previous_time=timestamp
    if mapping is None or len(poses)<30:raise ValueError('Insufficient continuous visual trajectory')
    return {'times':np.array([v[0] for v in poses]),'rotationsCameraWorld':np.array([v[1] for v in poses]),
            'positionsMap':np.array([v[2] for v in poses]),'scaleUnits':'arbitrary-map-units','distanceReady':False,
            'limitations':['Prototype fixed map; no map expansion or relocalization',
                           'Rolling-shutter translation/rotation not corrected in visual frontend',
                           'Visual poses alone do not determine metres']}
