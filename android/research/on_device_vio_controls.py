"""Analytic scene/IMU fixtures for transport checks, never physical validation.

Invoke from the existing phone_camera_imu_calibration notebook. All generated
images and traces belong under ignored dist/, not in the dataset or source tree.
"""
from pathlib import Path
import csv
import json
import numpy as np
import cv2


def create_control(folder: Path, *, blank=False, calibrating=False, excited=False,
                   duration_seconds=None, quiet_seconds=3, frame_hz=20, seed=1209,
                   camera_values=None, prior_values=None, imu_noise_scale=0,
                   top_occlusion_fraction=0, gravity_vector=None,
                   single_axis_seconds=0, blank_until_seconds=0,
                   true_extrinsics=None, prior_extrinsics=None,
                   true_time_offset_seconds=0, prior_time_offset_seconds=0,
                   motion_rate=1):
    folder.mkdir(parents=True, exist_ok=True)
    frames = folder / "frames"
    frames.mkdir(exist_ok=True)
    config = f"%YAML:1.0\n---\ncalibrating: {int(calibrating)}\n"
    camera_values = camera_values or [400,400,320,240,0,0,0,0]
    gravity_vector = np.array(gravity_vector if gravity_vector is not None else [0,0,9.80665],dtype=float)
    if gravity_vector.shape!=(3,) or not np.isfinite(gravity_vector).all() or abs(np.linalg.norm(gravity_vector)-9.80665)>.001:
        raise ValueError('Analytic gravity must have physical magnitude')
    # Walking is on a level plane, independently of how the camera is tilted.
    direction=np.array([1.,0,0]);unit_gravity=gravity_vector/9.80665
    direction-=unit_gravity*np.dot(direction,unit_gravity)
    if np.linalg.norm(direction)<.01:
        direction=np.array([0.,1,0]);direction-=unit_gravity*np.dot(direction,unit_gravity)
    direction/=np.linalg.norm(direction)
    prior_values = prior_values or camera_values
    true_extrinsics=true_extrinsics or [0,0,0,1,0,0,0]
    prior_extrinsics=prior_extrinsics or [0,0,0,1,0,0,0]
    for e in (true_extrinsics,prior_extrinsics):
        if len(e)!=7 or not np.isfinite(e).all() or abs(np.linalg.norm(e[:4])-1)>1e-6:
            raise ValueError('Expected a unit JPL quaternion and camera-frame translation')
    if not np.isfinite([true_time_offset_seconds,prior_time_offset_seconds]).all() or max(abs(true_time_offset_seconds),abs(prior_time_offset_seconds))>.15:
        raise ValueError('Invalid camera/IMU timing control')
    # OpenVINS uses JPL quaternions (opposite vector sign to Hamilton/OpenCV).
    q=np.array(true_extrinsics[:3]);w=true_extrinsics[3]
    cross=np.array([[0,-q[2],q[1]],[q[2],0,-q[0]],[-q[1],q[0],0]])
    imu_to_camera=(2*w*w-1)*np.eye(3)-2*w*cross+2*np.outer(q,q)
    camera_in_imu=-imu_to_camera.T@np.array(true_extrinsics[4:])
    if len(camera_values)!=8 or len(prior_values)!=8:
        raise ValueError('Expected eight radtan4 camera parameters')
    if frame_hz <= 0 or quiet_seconds < 3 or imu_noise_scale < 0 or not 0<=top_occlusion_fraction<1 or single_axis_seconds<0 or blank_until_seconds<0 or not .1<=motion_rate<=3:
        raise ValueError('Invalid analytic fixture specification')
    for name, values in [("intrinsics", prior_values),
                         ("extrinsics", prior_extrinsics)]:
        config += f"{name}: !!opencv-matrix\n   rows: {len(values)}\n   cols: 1\n   dt: d\n   data: [{', '.join(map(str, values))}]\n"
    config += f"td: {prior_time_offset_seconds}\nacc_noise_density: 0.0057\ngyro_noise_density: 0.000283\n"
    (folder / "config.yaml").write_text(config)
    # Three metre translation with smooth acceleration and deceleration.
    # Quiet start permits the actual estimator's static initialization.
    def trajectory(t):
        u = np.clip((t - quiet_seconds) / 6, 0, 1)
        x = 3 * (10*u**3 - 15*u**4 + 6*u**5)
        a = (3 / 36) * (60*u - 180*u**2 + 120*u**3) if quiet_seconds < t < quiet_seconds+6 else 0
        return x, a
    duration=duration_seconds if duration_seconds is not None else (45 if excited else quiet_seconds+9)
    if duration < quiet_seconds+6:
        raise ValueError('Capture ends before the motion finishes')
    noise_rng = np.random.default_rng(seed+1)
    def pose(t):
        u=max(0,t-quiet_seconds)
        ramp=min(1,u/2)**3 * (10-15*min(1,u/2)+6*min(1,u/2)**2)
        v=u*motion_rate
        p=ramp*np.array([.7*np.sin(1.05*v),.6*np.sin(1.3*v),.5*np.sin(1.6*v)])
        angles=ramp*np.array([.5*np.sin(1.2*v),.45*np.sin(.9*v),.4*np.sin(1.55*v)])
        if single_axis_seconds:
            # Start with rotation/translation on one axis only. Additional axes
            # begin smoothly after corrective guidance would be given. The same
            # pose drives both image projection and physical IMU derivatives.
            v=np.clip((u-single_axis_seconds)/2,0,1)
            gain=v**3*(10-15*v+6*v*v)
            p[1:]*=gain;angles[1:]*=gain
        return p,cv2.Rodrigues(angles)[0]
    with (folder / "imu.csv").open("w", newline="") as f:
        w = csv.writer(f); w.writerow(["ns","gx","gy","gz","ax","ay","az"])
        for i in range(int((duration+.5)*200)+1):
            t = i / 200
            if excited:
                p,r=pose(t);h=.0001
                before,_=pose(t-h);after,rnext=pose(t+h)
                acceleration=r.T@((before-2*p+after)/h**2+gravity_vector)
                omega=cv2.Rodrigues(r.T@rnext)[0].ravel()/h
                signal=np.r_[omega,acceleration]
            else:signal=np.r_[np.zeros(3),direction*trajectory(t)[1]+gravity_vector]
            if imu_noise_scale:
                # Density-to-sample conversion for the actual 200 Hz fixture.
                signal+=noise_rng.normal(size=6)*np.r_[np.full(3,.000283),np.full(3,.0057)]*np.sqrt(200)*imu_noise_scale
            w.writerow([int((100+t)*1e9),*signal])
    rng = np.random.default_rng(seed)
    # Project actual textured world planes. Fixed-size screen-space dots would
    # not rotate/scale with the camera and violate the estimator's rigid scene.
    panels=[(-10,10,-6,6,12)]
    for x,y,z in [(-2,-1,4),(2,1,5),(0,-1.4,7),(-3,1.5,6),(3,-1,8)]:
        panels.append((x-1.5,x+1.5,y-1.2,y+1.2,z))
    textures=[cv2.resize(rng.integers(25,240,(100,100),dtype=np.uint8),(640,640),interpolation=cv2.INTER_NEAREST) for _ in panels]
    camera=np.array([[camera_values[0],0,camera_values[2]],[0,camera_values[1],camera_values[3]],[0,0,1.]])
    # Inverse map: each distorted output pixel samples its undistorted ray.
    # This changes the rendered optics, independently of the estimator prior.
    yy,xx=np.mgrid[0:480,0:640]
    pixels=np.stack([xx,yy],axis=-1).astype(np.float32).reshape(-1,1,2)
    undistorted=cv2.undistortPoints(pixels,camera,np.array(camera_values[4:]),P=camera).reshape(480,640,2)
    texcorners=np.float32([[0,0],[639,0],[639,639],[0,639]])
    with (folder / "frames.csv").open("w", newline="") as f,(folder/'truth.csv').open('w',newline='') as truth:
        w = csv.writer(f);w.writerow(["ns","filename"])
        tw=csv.writer(truth);tw.writerow(['camera_ns','physical_imu_ns','px','py','pz'])
        for i in range(int(duration*frame_hz)+1):
            t=i/frame_hz;image=np.full((480,640),20,dtype=np.uint8)
            physical_t=t+true_time_offset_seconds
            if excited:translation,rotation=pose(physical_t)
            else:translation=direction*trajectory(physical_t)[0];rotation=np.eye(3)
            tw.writerow([int((100+t)*1e9),int((100+physical_t)*1e9),*translation])
            if not blank and t>=blank_until_seconds:
                translation=translation+rotation@camera_in_imu
                rotation=rotation@imu_to_camera.T
                # Parallel world-Z planes: far surfaces must not overwrite near
                # surfaces. Old v1 controls are retained, never regenerated in place.
                for (x0,x1,y0,y1,z),texture in sorted(zip(panels,textures),key=lambda item:-item[0][4]):
                    corners=np.array([[x0,y0,z],[x1,y0,z],[x1,y1,z],[x0,y1,z]])
                    p=(corners-translation)@rotation
                    uv=(p@camera.T);uv=np.float32(uv[:,:2]/uv[:,2:])
                    homography=cv2.getPerspectiveTransform(texcorners,uv)
                    layer=cv2.warpPerspective(texture,homography,(640,480))
                    mask=np.zeros((480,640),dtype=np.uint8);cv2.fillConvexPoly(mask,np.round(uv).astype(np.int32),255)
                    image[mask>0]=layer[mask>0]
            if any(camera_values[4:]):
                image=cv2.remap(image,undistorted[:,:,0],undistorted[:,:,1],cv2.INTER_LINEAR)
            image[:int(480*top_occlusion_fraction)]=0
            name=frames/f"{i:05d}.jpg";cv2.imwrite(str(name),image,[cv2.IMWRITE_JPEG_QUALITY,95])
            w.writerow([int((100+t)*1e9),str(name)])
    metadata={"kind":"analytic-software-control", "blank":blank,
            "calibrating":calibrating,"excited":excited,"knownTranslationMetres":None if excited else 3,
            "physicalPhoneAccuracyTest":False,"rendering":"perspective-textured-rigid-planes-depth-ordered-v2", "seed":seed,
            "durationSeconds":duration,"quietSeconds":quiet_seconds,"frameHz":frame_hz,
            "cameraValues":camera_values,"priorValues":prior_values,"imuNoiseScale":imu_noise_scale,
            "topOcclusionFraction":top_occlusion_fraction,"gravityVector":gravity_vector.tolist(),
            "walkingDirection":direction.tolist(),"walkingPlane":"perpendicular-to-gravity",
            "singleAxisSeconds":single_axis_seconds,"blankUntilSeconds":blank_until_seconds,
            "trueExtrinsics":true_extrinsics,"priorExtrinsics":prior_extrinsics,
            "trueTimeOffsetSeconds":true_time_offset_seconds,"priorTimeOffsetSeconds":prior_time_offset_seconds,"motionRate":motion_rate}
    (folder/'fixture.json').write_text(json.dumps(metadata,indent=2)+'\n')
    return metadata
