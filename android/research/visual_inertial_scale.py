"""Metric scale initializer for consistent monocular camera poses.

This is a research building block, not a complete walking odometry system.
Inputs must share one world frame, clock and map scale. Unit translations from
independent recoverPose calls do NOT satisfy that contract. No GPS, step-length
formula or known walking distance is used to fit scale.
"""
import numpy as np


def fit_metric_scale(visual_acceleration, imu_rotation, rotation_second_derivative,
                     measured_specific_force, minimum_samples=80):
    """Fit scale, IMU bias, gravity and IMU-to-camera lever arm simultaneously.

    Camera acceleration is in arbitrary map units/s². Rotation maps IMU axes to
    the same map/world axes. Specific force is SI m/s², including gravity as
    SensorManager reports it. Derivatives require synchronized smooth poses;
    never differentiate across tracking loss or interpolate long missing gaps.
    """
    pdd=np.asarray(visual_acceleration,dtype=float)
    R=np.asarray(imu_rotation,dtype=float)
    Rdd=np.asarray(rotation_second_derivative,dtype=float)
    force=np.asarray(measured_specific_force,dtype=float)
    n=len(pdd)
    if n<minimum_samples or pdd.shape!=(n,3) or force.shape!=(n,3) or R.shape!=(n,3,3) or Rdd.shape!=(n,3,3):
        raise ValueError('Insufficient synchronized camera/IMU samples or invalid dimensions')
    if not all(np.isfinite(x).all() for x in [pdd,R,Rdd,force]):
        raise ValueError('Nonfinite camera/IMU input')
    if not np.allclose(R@R.transpose(0,2,1),np.eye(3),atol=1e-5) or np.any(np.linalg.det(R)<.999):
        raise ValueError('Invalid IMU rotation matrices')
    # s*pdd + R*b - g - Rdd*lever = R*specific_force.
    matrix=np.concatenate([pdd[:,:,None],R,-np.broadcast_to(np.eye(3),(n,3,3)),-Rdd],axis=2)
    target=np.einsum('nij,nj->ni',R,force)
    # Whole time blocks held out, not alternating rows of the same instant.
    holdout=np.arange(n)>=int(n*.8)
    A=matrix[~holdout].reshape(-1,10);y=target[~holdout].ravel()
    norms=np.linalg.norm(A,axis=0)
    scaled=A/np.maximum(norms,1e-12)
    singular=np.linalg.svd(scaled,compute_uv=False)
    rank=int(np.linalg.matrix_rank(scaled,tol=1e-6))
    condition=float(singular[0]/max(singular[-1],1e-12))
    out={'method':'visual-inertial-scale-initializer-v1','status':'rejected',
         'distanceReady':False,'rank':rank,'scaledCondition':condition,
         'trainingSamples':int((~holdout).sum()),'heldOutSamples':int(holdout.sum()),
         'limitations':['Requires one consistent visual map; independent unit-baseline poses invalid',
                        'Derivatives and camera/IMU alignment must be verified separately',
                        'Held-out residual is an internal check, not measured-route validation',
                        'No visual tracking frontend or continuous odometry in this initializer']}
    if rank<10 or condition>1e4:
        out['reason']='Metric scale is unobservable or poorly conditioned; distance withheld'
        return out
    solution=np.linalg.lstsq(A,y,rcond=None)[0]
    error=np.einsum('nij,j->ni',matrix[holdout],solution)-target[holdout]
    rms=float(np.sqrt(np.mean(error**2)))
    residual=A@solution-y
    variance=float(residual@residual/max(len(y)-10,1))
    covariance=np.linalg.inv(A.T@A)*variance
    uncertainty=float(np.sqrt(max(covariance[0,0],0)))
    scale=float(solution[0]);bias=solution[1:4];gravity=solution[4:7];lever=solution[7:10]
    passed=bool(scale>0 and uncertainty/scale<.15 and rms<.6 and
                abs(np.linalg.norm(gravity)-9.80665)<.5 and np.linalg.norm(bias)<1.5 and np.linalg.norm(lever)<.2)
    out.update({'status':'scale-candidate' if passed else 'rejected',
                'metresPerMapUnit':scale,'scaleLinearizedStd':uncertainty,
                'accelerometerBiasMps2':bias.tolist(),'gravityWorldMps2':gravity.tolist(),
                'imuToCameraLeverArmMetres':lever.tolist(),'heldOutCoordinateRmsMps2':rms,
                'reason':'Candidate requires independent measured-route validation' if passed else 'Physical or residual gates failed'})
    return out


def screen_route(trajectory, gyro_times, gyro_values, accel_times, accel_values,
                 rotation_imu_to_camera, residual_time_offset_seconds):
    """Connect consistent visual poses to a withheld/experimental metric report.

    Not an EKF/VIO backend: no bias propagation, map refinement or loop closure.
    Uses physical IMU samples, never an entered route length. No clinical stop
    rule may consume this research output.
    """
    from scipy.interpolate import CubicSpline
    from scipy.signal import savgol_filter
    from scipy.spatial.transform import Rotation,Slerp
    from camera_imu_joint import integrate_gyro
    times=np.asarray(trajectory['times'])+residual_time_offset_seconds
    if len(times)<30 or times[-1]-times[0]<6 or np.any(np.diff(times)<=0) or np.max(np.diff(times))>.3:
        raise ValueError('Need at least six seconds of uninterrupted consistent-map poses')
    if times[0]<max(gyro_times[0],accel_times[0]) or times[-1]>min(gyro_times[-1],accel_times[-1]):
        raise ValueError('Visual trajectory falls outside native IMU coverage')
    Rwc=np.asarray(trajectory['rotationsCameraWorld']).transpose(0,2,1)
    Rwi=Rwc@np.asarray(rotation_imu_to_camera)
    q=integrate_gyro(gyro_times,gyro_values,np.zeros(3))
    observed=Rwi[:-1].transpose(0,2,1)@Rwi[1:]
    predicted=q(times[:-1]).as_matrix().transpose(0,2,1)@q(times[1:]).as_matrix()
    error=Rotation.from_matrix(observed@predicted.transpose(0,2,1)).magnitude()
    gyro_rms=float(np.sqrt(np.mean(error**2)))
    if gyro_rms>np.deg2rad(5):
        return {'status':'rejected','distanceReady':False,'reason':'Visual rotation disagrees with gyro',
                'rotationConsistencyRmsDegrees':float(np.rad2deg(gyro_rms))}
    sample=np.arange(times[0],times[-1],.02)
    positions=CubicSpline(times,trajectory['positionsMap'])(sample)
    positions=savgol_filter(positions,31,3,axis=0) # Explicit 0.62 s research smoothing.
    pdd=savgol_filter(positions,31,3,deriv=2,delta=.02,axis=0)
    Q=Slerp(times,Rotation.from_matrix(Rwi))(sample).as_matrix()
    rdd=savgol_filter(Q,31,3,deriv=2,delta=.02,axis=0)
    specific_force=np.column_stack([np.interp(sample,accel_times,accel_values[:,k]) for k in range(3)])
    # Remove derivative boundary transients; no extrapolated samples.
    report=fit_metric_scale(pdd[20:-20],Q[20:-20],rdd[20:-20],specific_force[20:-20])
    report['rotationConsistencyRmsDegrees']=float(np.rad2deg(gyro_rms))
    report['positionSmoothingWindowSeconds']=.62
    if report['status']=='scale-candidate':
        gravity=np.asarray(report['gravityWorldMps2']);vertical=gravity/np.linalg.norm(gravity)
        increments=np.diff(positions,axis=0)*report['metresPerMapUnit']
        horizontal=increments-np.outer(increments@vertical,vertical)
        report['experimentalHorizontalCameraPathMetres']=float(np.linalg.norm(horizontal,axis=1).sum())
        report['experimentalElapsedSeconds']=float(sample[-1]-sample[0])
        report['limitations'] += ['Camera path includes residual body sway; not validated clinical walking distance',
                                  'No continuous inertial fusion or loop closure',
                                  'Visual frontend rolling-shutter correction remains incomplete']
    return report
