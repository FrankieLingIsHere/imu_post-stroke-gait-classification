"""Row-timed camera/gyro calibration in pixel space.

Research prototype: fixed target, fixed intrinsics, gyro-driven camera rotations,
per-view nuisance translations. Does not estimate the IMU lever arm or odometry.
Hold out whole views; their rotations are never fit to the held-out points.
"""
import numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation, Slerp
from scipy.sparse import lil_matrix
import cv2
import hashlib
from pathlib import Path


def integrate_gyro(times, values, bias):
    times=np.asarray(times);values=np.asarray(values)-bias
    if len(times)<2 or np.any(np.diff(times)<=0): raise ValueError('Invalid gyro clock')
    rotations=np.empty((len(times),3,3));rotations[0]=np.eye(3)
    for i in range(1,len(times)):
        rotations[i]=rotations[i-1]@Rotation.from_rotvec((values[i-1]+values[i])*((times[i]-times[i-1])/2)).as_matrix()
    return Slerp(times,Rotation.from_matrix(rotations))


def project_rows(view, parameters, camera_position, gyro_curve, K, D):
    # t_imu=t_camera+offset. Native row positions are never display-rotated.
    times=view['times']+parameters[6]
    if times.min()<gyro_curve.times[0] or times.max()>gyro_curve.times[-1]:
        raise ValueError('Camera observations outside gyro coverage')
    Rci=Rotation.from_rotvec(parameters[:3]).as_matrix()
    Rwi0=Rotation.from_rotvec(parameters[7:10]).as_matrix()
    Rwc=np.einsum('ij,njk,kl->nil',Rwi0,gyro_curve(times).as_matrix(),Rci.T)
    camera_points=np.einsum('nji,nj->ni',Rwc,view['object']-camera_position)
    if np.any(camera_points[:,2]<=.01):
        # A smooth large residual keeps invalid trial states away from the solution.
        camera_points[:,2]=np.maximum(camera_points[:,2],.01)
    projected,_=cv2.projectPoints(camera_points,np.zeros(3),np.zeros(3),K,D)
    return projected.reshape(-1,2)


def fit_joint_rotation_timing(views, gyro_times, gyro_values, K, D, initial, max_evaluations=80):
    """Joint image fit with row-specific exposure times and actual gyro integration."""
    if len(views)<30: raise ValueError('Too few board views')
    gyro_times=np.asarray(gyro_times,dtype=float);gyro_values=np.asarray(gyro_values,dtype=float)
    if gyro_values.shape!=(len(gyro_times),3) or not np.isfinite(gyro_values).all():
        raise ValueError('Invalid gyro samples')
    if len(gyro_times)<20 or np.min(np.linalg.eigvalsh(np.cov(gyro_values.T)))<.001:
        raise ValueError('Insufficient three-axis rotational excitation')
    # Reserve margins for the bounded offset; do not extrapolate inertial motion.
    views=[v for v in views if v['times'].min()>gyro_times[0]+.16 and v['times'].max()<gyro_times[-1]-.16]
    if len(views)>100:
        views=[views[i] for i in np.linspace(0,len(views)-1,100,dtype=int)]
    training=[v for i,v in enumerate(views) if i%5!=0]
    holdout=[v for i,v in enumerate(views) if i%5==0]
    if len(training)<24 or len(holdout)<6: raise ValueError('Insufficient independent held-out views')
    Rci=np.asarray(initial['rotationImuToCamera']);bias=np.asarray(initial['gyroBiasRadS'])
    offset=float(np.clip(initial['residualTimeOffsetSeconds'],-.14,.14))
    curve=integrate_gyro(gyro_times,gyro_values,bias)
    first=training[0]
    q=curve(float(np.mean(first['times'])+offset)).as_matrix()
    initial_world=first['rotationWorldCamera']@Rci@q.T
    globals=np.r_[Rotation.from_matrix(Rci).as_rotvec(),bias,offset,Rotation.from_matrix(initial_world).as_rotvec()]
    p0=np.r_[globals,np.concatenate([v['positionWorldCamera'] for v in training])]
    rows=sum(len(v['image'])*2 for v in training)
    sparsity=lil_matrix((rows,len(p0)),dtype=int);at=0
    for i,v in enumerate(training):
        count=len(v['image'])*2;sparsity[at:at+count,:10]=1;sparsity[at:at+count,10+i*3:13+i*3]=1;at+=count
    cache={}
    def residual(p):
        key=tuple(p[3:6]);gyro_curve=cache.get(key)
        if gyro_curve is None:
            gyro_curve=integrate_gyro(gyro_times,gyro_values,p[3:6]);cache.clear();cache[key]=gyro_curve
        return np.concatenate([(project_rows(v,p,p[10+i*3:13+i*3],gyro_curve,K,D)-v['image']).ravel() for i,v in enumerate(training)])
    lower=np.full(len(p0),-np.inf);upper=np.full(len(p0),np.inf)
    lower[3:6]=-.2;upper[3:6]=.2;lower[6]=-.15;upper[6]=.15
    result=least_squares(residual,p0,bounds=(lower,upper),jac_sparsity=sparsity.tocsr(),
                         loss='soft_l1',f_scale=1.,max_nfev=max_evaluations,ftol=1e-5,xtol=1e-6,gtol=1e-5)
    p=result.x;curve=integrate_gyro(gyro_times,gyro_values,p[3:6]);holdout_errors=[]
    for v in holdout:
        # Only translation is fit on a held-out frame. Orientation/timing/bias remain fixed.
        position=least_squares(lambda x:(project_rows(v,p,x,curve,K,D)-v['image']).ravel(),
                               v['positionWorldCamera'],loss='soft_l1',f_scale=1.,max_nfev=80)
        error=project_rows(v,p,position.x,curve,K,D)-v['image']
        holdout_errors.append(float(np.sqrt(np.mean(error**2))))
    final=residual(p)
    J=result.jac.toarray() if hasattr(result.jac,'toarray') else result.jac
    # Marginal information for global variables after eliminating nuisance positions.
    A=J[:,:10];B=J[:,10:];information=A.T@A-A.T@B@np.linalg.pinv(B.T@B)@B.T@A
    singular=np.linalg.svd(information,compute_uv=False)
    condition=float(singular[0]/max(singular[-1],1e-12))
    covariance=np.linalg.pinv(information)*float(np.mean(final**2))
    std=np.sqrt(np.maximum(np.diag(covariance),0))
    rms=float(np.sqrt(np.mean(np.square(holdout_errors))));p90=float(np.percentile(holdout_errors,90))
    passed=bool(result.success and rms<1.5 and p90<2 and std[6]<.02 and np.max(std[:3])<np.deg2rad(3)
                and condition<1e8 and abs(p[6])<.145)
    return {'method':'row-timed-gyro-pixel-fit-v1',
            'processorSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'status':'rotation-timing-candidate' if passed else 'rejected',
            'fullCalibrationReady':False,
            'rotationImuToCamera':Rotation.from_rotvec(p[:3]).as_matrix().tolist(),
            'rotationWorldImuAtGyroOrigin':Rotation.from_rotvec(p[7:10]).as_matrix().tolist(),
            'gyroBiasRadS':p[3:6].tolist(),'residualTimeOffsetSeconds':float(p[6]),
            'trainingCoordinateRmsPixels':float(np.sqrt(np.mean(final**2))),
            'heldOutViewRmsPixels':rms,'heldOutViewP90Pixels':p90,'heldOutViews':len(holdout),
            'trainingViews':len(training),'offsetLinearizedStdSeconds':float(std[6]),
            'rotationLinearizedStdDegrees':np.rad2deg(std[:3]).tolist(),'globalInformationCondition':condition,
            'optimizerConverged':bool(result.success),'optimizerEvaluations':result.nfev,'passed':passed,
            'distanceReady':False,'limitations':['Fixed target required','Translation during each frame readout approximated as constant',
                   'Fixed intrinsics','Linearized uncertainty is not an external accuracy guarantee','Lever arm not fitted','Not odometry']}


def load_board_views(bundle, lens):
    from camera_calibration import read_bundle,board
    z,m,frames,imu,results=read_bundle(bundle);views=[]
    K=np.asarray(lens['cameraMatrix']);D=np.asarray(lens['distortion']);origin=int(m['startedBootNs'])
    if m['timestampSource']!='realtime':z.close();raise ValueError('This prototype requires the real-time hardware clock')
    detector=cv2.aruco.CharucoDetector(board())
    try:
        for f in frames:
            image=cv2.imdecode(np.frombuffer(z.read(f['file']),np.uint8),0)
            corners,ids,_,_=detector.detectBoard(image)
            if ids is None or len(ids)<16:continue
            obj,img=board().matchImagePoints(corners,ids);obj=obj.reshape(-1,3);img=img.reshape(-1,2)
            ok,rv,tv=cv2.solvePnP(obj,img,K,D)
            if not ok:continue
            meta=results[int(f['timestampNs'])]
            if meta.get('exposureNs') is None or meta.get('rollingShutterSkewNs') is None:
                raise ValueError('Per-frame exposure/readout metadata missing')
            times=(int(f['timestampNs'])-origin+meta['exposureNs']/2+img[:,1]/max(m['height']-1,1)*meta['rollingShutterSkewNs'])/1e9
            R=cv2.Rodrigues(rv)[0]
            views.append({'times':times,'object':obj,'image':img,'rotationWorldCamera':R.T,'positionWorldCamera':(-R.T@tv).ravel()})
        rows=[v for v in imu if v['sensor']=='gyroscope']
        gt=np.array([(int(v['timestampNs'])-origin)/1e9 for v in rows]);gv=np.array([[v[k] for k in ['x','y','z']] for v in rows])
        return views,gt,gv,K,D
    finally:z.close()


def screen_board_acceleration(views, gyro_times, gyro_values, K, D, alignment,
                              accel_times, accel_values):
    """Separate translation/accelerometer screen; never bridges board loss.

    Position derivatives depend on an explicit 3 mm smoothing assumption. This
    is a diagnostic, not a noise calibration or a distance validation result.
    """
    from scipy.interpolate import UnivariateSpline
    from camera_calibration import fit_accel_geometry
    Rci=np.asarray(alignment['rotationImuToCamera'])
    Rwi0=np.asarray(alignment['rotationWorldImuAtGyroOrigin'])
    p=np.r_[Rotation.from_matrix(Rci).as_rotvec(),alignment['gyroBiasRadS'],
            alignment['residualTimeOffsetSeconds'],Rotation.from_matrix(Rwi0).as_rotvec()]
    curve=integrate_gyro(gyro_times,gyro_values,p[3:6]);poses=[]
    for v in views:
        if v['times'].min()+p[6]<gyro_times[0] or v['times'].max()+p[6]>gyro_times[-1]:continue
        result=least_squares(lambda x:(project_rows(v,p,x,curve,K,D)-v['image']).ravel(),
                             v['positionWorldCamera'],loss='soft_l1',f_scale=1.,max_nfev=60)
        error=float(np.sqrt(np.mean((project_rows(v,p,result.x,curve,K,D)-v['image'])**2)))
        if result.success and error<2:
            poses.append((float(np.mean(v['times'])+p[6]),result.x))
    if len(poses)<30:return {'passed':False,'reason':'Insufficient rotation-consistent camera positions'}
    times=np.array([v[0] for v in poses]);positions=np.array([v[1] for v in poses])
    cuts=np.r_[0,np.flatnonzero(np.diff(times)>.25)+1,len(times)]
    pieces=[];durations=[]
    for start,end in zip(cuts[:-1],cuts[1:]):
        t=times[start:end]
        if len(t)<20 or t[-1]-t[0]<3:continue
        sample=np.arange(t[0]+.35,t[-1]-.35,.02)
        sample=sample[(sample>accel_times[0])&(sample<accel_times[-1])]
        if len(sample)<30:continue
        splines=[UnivariateSpline(t,positions[start:end,k],s=len(t)*.003**2) for k in range(3)]
        pdd=np.column_stack([v.derivative(2)(sample) for v in splines])
        Q=np.einsum('ij,njk->nik',Rwi0,curve(sample).as_matrix())
        Rwc=Q@Rci.T
        before=np.einsum('ij,njk,kl->nil',Rwi0,curve(sample-.005).as_matrix(),Rci.T)
        after=np.einsum('ij,njk,kl->nil',Rwi0,curve(sample+.005).as_matrix(),Rci.T)
        rdd=(before-2*Rwc+after)/.005**2
        force=np.column_stack([np.interp(sample,accel_times,accel_values[:,k]) for k in range(3)])
        pieces.append((pdd,rdd,Q,force));durations.append(float(sample[-1]-sample[0]))
    if not pieces:
        return {'passed':False,'reason':'No sufficiently long contiguous board tracking segments; no interpolation across losses',
                'acceptedPoseViews':len(poses),'maximumAcceptedPoseGapSeconds':float(np.max(np.diff(times)))}
    fit=fit_accel_geometry(*[np.concatenate([piece[k] for piece in pieces]) for k in range(4)])
    return {**fit,'contiguousSegments':len(pieces),'segmentSeconds':durations,
            'positionSmoothingAssumptionMetres':.003,'distanceReady':False,
            'limitations':['Internal board-based diagnostic','Adjacent derivative samples are correlated',
                           '3 mm spline smoothing assumption is not measured camera noise',
                           'No independent measured-route validation']}
