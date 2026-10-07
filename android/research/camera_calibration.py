"""Offline device calibration from native timestamped frames, never from a claimed route length.

Research orchestration and saved outputs live in the camera/IMU notebook. This module
provides reusable loading, board generation, geometry fitting and admission checks.
Passing geometry checks does not validate an odometry engine or clinical distance.
"""
from pathlib import Path
import base64
import hashlib
import json
import zipfile
import cv2
import numpy as np
from scipy.interpolate import CubicSpline
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation

BOARD = {"squaresX": 9, "squaresY": 7, "squareLengthM": .020,
         "markerLengthM": .015, "dictionary": "DICT_4X4_100"}


def point_reprojection_rms(projected, observed):
    """Compare corresponding 2D points, never NumPy's N-by-N broadcast grid."""
    projected=np.asarray(projected).reshape(-1,2)
    observed=np.asarray(observed).reshape(-1,2)
    if projected.shape!=observed.shape or not len(projected):
        raise ValueError('Reprojection point correspondence mismatch')
    return float(np.sqrt(np.mean((projected-observed)**2)))


def camera_observation_time_seconds(frame, result, origin_ns, clock_offset_ns, height):
    """Exposure midpoint at the mean observed feature row, not callback arrival."""
    if result.get('exposureNs') is None or result.get('rollingShutterSkewNs') is None:
        raise ValueError('Exposure/rolling-shutter capture metadata missing; timing calibration withheld')
    row=float(frame.get('meanFeatureRow',(height-1)/2))
    fraction=np.clip(row/max(height-1,1),0,1)
    return (int(frame['timestampNs'])-origin_ns+clock_offset_ns+result['exposureNs']/2+
            fraction*result['rollingShutterSkewNs'])/1e9


def board():
    return cv2.aruco.CharucoBoard((9, 7), .020, .015,
                                 cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_100))


def write_board(output):
    """Print at actual size; verify physical square size, not screen pixels."""
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    image = board().generateImage((1800, 1400), marginSize=0)
    ok, png = cv2.imencode('.png', image)
    assert ok
    (output / 'board.png').write_bytes(png.tobytes())
    encoded = base64.b64encode(png).decode('ascii')
    html = f'''<!doctype html><html><head><meta charset="utf-8"><title>GaitTrace calibration board</title>
    <style>@page{{size:A4 landscape;margin:15mm}}body{{font:14px sans-serif}}img{{width:180mm;height:140mm;display:block}}@media print{{button{{display:none}}}}</style></head>
    <body><button onclick="print()">Print board</button><p>Print at 100% / actual size. Each square must measure 20 mm.
    Verify with a ruler; do not use fit-to-page. Keep flat. This is researcher setup, not a patient test.</p>
    <img src="data:image/png;base64,{encoded}" alt="9 by 7 ChArUco squares with unique marker IDs">
    <p>Board: 180 × 140 mm. Use the same holder/window used for capture. Lens must see the board.</p></body></html>'''
    (output / 'print-board.html').write_text(html, encoding='utf-8')
    return output / 'print-board.html'


def read_bundle(path):
    """No ZIP extraction; reject unsafe paths, oversized payloads and non-native captures."""
    z = zipfile.ZipFile(path)
    try:
        return _read_bundle_open(z)
    except Exception:
        z.close()
        raise


def _read_bundle_open(z):
    entries = z.infolist()
    if sum(v.file_size for v in entries) > 512 * 1024**2 or len(entries) > 2000:
        z.close()
        raise ValueError('Calibration archive exceeds size/count bounds')
    if len({v.filename for v in entries}) != len(entries) or any(
            '\\' in v.filename or v.filename.startswith('/') or '..' in Path(v.filename).parts for v in entries):
        z.close()
        raise ValueError('Unsafe calibration archive')
    m = json.loads(z.read('manifest.json'))
    if m.get('schemaVersion') != 1 or m.get('status') != 'completed' or m.get('error') is not None:
        z.close()
        raise ValueError('Capture did not complete; inspect its native error before calibrating')
    if m.get('facing') != 'front' or m.get('imageAxes') != 'native-sensor-unrotated-unmirrored':
        raise ValueError('Unsupported calibration image pipeline')
    if m.get('units') != {'accelerometer': 'm/s2', 'gyroscope': 'rad/s', 'magnetometer': 'uT'}:
        raise ValueError('Unexpected native sensor units')
    def rows(name):
        return [json.loads(v) for v in z.read(name).decode('utf-8').splitlines() if v.strip()]
    frames, imu, results = rows('frames.ndjson'), rows('imu.ndjson'), rows('capture-results.ndjson')
    if len(frames) < 80:
        raise ValueError('Too few actual camera frames for calibration')
    for sensor in ['accelerometer', 'gyroscope', 'magnetometer']:
        samples = [v for v in imu if v['sensor'] == sensor]
        if len(samples) < 100 or not all(np.isfinite([v['x'], v['y'], v['z']]).all() for v in samples):
            raise ValueError(f'Insufficient/invalid {sensor} capture')
        if np.any(np.diff([int(v['timestampNs']) for v in samples]) <= 0):
            raise ValueError(f'Nonmonotonic native {sensor} clock')
    if np.any(np.diff([int(v['timestampNs']) for v in frames]) <= 0):
        raise ValueError('Nonmonotonic native camera clock')
    return z, m, frames, imu, {int(v['timestampNs']): v for v in results}


def fit_gyro_alignment(camera_times, rotations_world_camera, gyro_times, gyro_values):
    """Fit IMU->camera rotation, gyro bias and residual time offset; hold out time pairs."""
    t = np.asarray(camera_times)
    r = np.asarray(rotations_world_camera)
    pairs = np.diff(t) < .25
    mids = ((t[1:] + t[:-1]) / 2)[pairs]
    wc = np.array([Rotation.from_matrix(a.T @ b).as_rotvec() / dt
                   for a, b, dt in zip(r[:-1], r[1:], np.diff(t))])[pairs]
    valid = (mids > gyro_times[0]+.5) & (mids < gyro_times[-1]-.5)
    mids, wc = mids[valid], wc[valid]
    if len(mids) < 50:
        raise ValueError('Too few continuous board poses for clock/rotation calibration')
    if np.linalg.eigvalsh(np.cov(wc.T)).min() < .001:
        raise ValueError('Motion does not excite three axes; tilt and translate in multiple directions')
    train = np.arange(len(mids)) % 5 != 0
    def gyro_at(times):
        return np.column_stack([np.interp(times, gyro_times, gyro_values[:, k]) for k in range(3)])
    initial, _ = Rotation.align_vectors(wc[train], gyro_at(mids[train]))
    def predicted(p):
        return Rotation.from_rotvec(p[:3]).apply(gyro_at(mids+p[6])-p[3:6])
    result = least_squares(lambda p: (predicted(p)[train]-wc[train]).ravel(),
                           np.r_[initial.as_rotvec(), np.zeros(4)],
                           bounds=(np.r_[np.full(6,-np.inf),-.5], np.r_[np.full(6,np.inf),.5]),
                           loss='soft_l1', f_scale=.04, max_nfev=400)
    residual = predicted(result.x)-wc
    holdout = float(np.sqrt(np.mean(residual[~train]**2)))
    singular = np.linalg.svd(result.jac, compute_uv=False)
    condition = float(singular.max()/max(singular.min(),1e-12))
    uncertainty = np.sqrt(np.diag(np.linalg.pinv(result.jac.T @ result.jac))*np.mean(residual[train]**2))
    return {'rotationImuToCamera': Rotation.from_rotvec(result.x[:3]).as_matrix().tolist(),
            'gyroBiasRadS': result.x[3:6].tolist(), 'residualTimeOffsetSeconds': float(result.x[6]),
            'offsetStdSeconds': float(uncertainty[6]), 'heldOutGyroRmseRadS': holdout,
            'fitCondition': condition, 'pairs': len(mids),
            'passed': bool(result.success and holdout<.08 and uncertainty[6]<.02 and condition<1e5
                           and abs(result.x[6])<.48)}


def fit_accel_geometry(pdd, rdd, Q, accel):
    """Screen board-relative lever arm, constant bias and gravity consistency."""
    count=len(pdd)
    A=np.concatenate([rdd,Q,np.tile(np.eye(3),(count,1,1))],axis=2).reshape(-1,9)
    y=(np.einsum('nij,nj->ni',Q,accel)-pdd).ravel()
    training=np.repeat(np.arange(count)%5!=0,3)
    coefficients,_,rank,singular=np.linalg.lstsq(A[training],y[training],rcond=None)
    residual=(A@coefficients-y).reshape(-1,3)
    error=float(np.sqrt(np.mean(residual[np.arange(count)%5==0]**2)))
    lever,bias,gravity=coefficients[:3],coefficients[3:6],coefficients[6:]
    condition=float(singular[0]/max(singular[-1],1e-12))
    passed=bool(rank==9 and condition<1e4 and np.linalg.norm(lever)<.2 and np.linalg.norm(bias)<1.5 and abs(np.linalg.norm(gravity)-9.80665)<.5 and error<.6)
    return {'cameraToImuInCameraM':lever.tolist(),'accelerometerBiasMps2':bias.tolist(),
            'gravityBoardMps2':gravity.tolist(),'heldOutRmseMps2':error,'fitRank':int(rank),'fitCondition':condition,'passed':passed}


def process_bundle(path, output):
    """Return a bounded geometry candidate or explicit rejection; never distanceReady."""
    output = Path(output); output.mkdir(parents=True, exist_ok=True)
    sha = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    report = {'schemaVersion':1, 'kind':'phone-camera-imu-calibration-v1',
              'processorVersion':'2-row-aware',
              'bundleSha256':sha, 'status':'rejected', 'distanceReady':False,
              'independentDistanceValidation':False, 'board':BOARD, 'errors':[]}
    try:
        z,m,frames,imu,results = read_bundle(path)
        with z:
            report['binding']={k:m.get(k) for k in ['installationId','captureId','cameraId','width','height','imageAxes','sensorOrientationDegrees','stabilizationRequested']}
            if m.get('capturePipeline'):
                report['binding'].update({k:m.get(k) for k in ['capturePipeline','opticalSetup']})
            for name in ['accelerometer','gyroscope','magnetometer']:
                ts=np.array([int(v['timestampNs']) for v in imu if v['sensor']==name])/1e9
                if ts[-1]-ts[0]<30 or np.max(np.diff(ts))>.15:
                    raise ValueError(f'{name} has inadequate coverage or a sensor gap above 150 ms')
            focus=[v['focusDioptres'] for v in results.values() if v.get('focusDioptres') is not None]
            if focus and np.ptp(focus)>.05:
                raise ValueError('Camera focus changed; fixed optics are required')
            for v in results.values():
                if v.get('videoStabilizationMode') not in (0,None) or v.get('opticalStabilizationMode') not in (0,None):
                    raise ValueError('Camera stabilization changed the calibration geometry')
            detector = cv2.aruco.CharucoDetector(board())
            object_points=[];image_points=[];accepted=[]
            for f in frames:
                image = cv2.imdecode(np.frombuffer(z.read(f['file']),np.uint8),cv2.IMREAD_GRAYSCALE)
                if image is None or image.shape != (m['height'],m['width']):
                    raise ValueError('Frame dimensions do not match camera pipeline')
                corners,ids,_,_ = detector.detectBoard(image)
                if ids is None or len(ids)<16: continue
                obj,img=board().matchImagePoints(corners,ids)
                object_points.append(obj);image_points.append(img);accepted.append(f)
            if len(accepted)<30: raise ValueError('Not enough views of the board; at least 30 diverse detections required')
            train=np.arange(len(accepted))%5!=0
            rms,K,D,_,_=cv2.calibrateCamera([v for i,v in enumerate(object_points) if train[i]],
                    [v for i,v in enumerate(image_points) if train[i]],(m['width'],m['height']),None,None)
            poses=[];errors=[];heldout_errors=[]
            for i,(obj,img,f) in enumerate(zip(object_points,image_points,accepted)):
                ok,rv,tv=cv2.solvePnP(obj,img,K,D)
                if not ok: continue
                projected,_=cv2.projectPoints(obj,rv,tv,K,D)
                err=point_reprojection_rms(projected,img)
                errors.append(err)
                if not train[i]: heldout_errors.append(err)
                if err>1.0: continue
                f={**f,'meanFeatureRow':float(np.mean(img.reshape(-1,2)[:,1]))}
                R=cv2.Rodrigues(rv)[0];poses.append((f,R.T,(-R.T@tv).ravel()))
            report['lens']={'cameraMatrix':K.tolist(),'distortion':D.ravel().tolist(),'trainingRmsPixels':float(rms),
                            'views':len(poses),'detectedViews':len(accepted),
                            'reprojectionP90Pixels':float(np.percentile(errors,90)) if errors else None,
                            'heldOutP90Pixels':float(np.percentile(heldout_errors,90)) if heldout_errors else None}
            if not poses or not heldout_errors or rms>1 or np.percentile(heldout_errors,90)>1.5:
                raise ValueError('Lens reprojection error is too high; inspect print scale, blur and holder optics')
            normals=np.array([v[1][:,2] for v in poses])
            if np.linalg.norm(np.ptp(normals,axis=0))<.3:
                raise ValueError('Board views lack tilt diversity')
            origin=int(m['startedBootNs'])
            camera_offset=0 if m['timestampSource']=='realtime' else float(np.median([int(v['arrivalBootNs'])-int(v['timestampNs']) for v in frames]))
            times=[]
            for f,_,_ in poses:
                meta=results.get(int(f['timestampNs']))
                if meta is None:
                    raise ValueError('Exposure/rolling-shutter capture metadata missing; timing calibration withheld')
                times.append(camera_observation_time_seconds(f,meta,origin,camera_offset,m['height']))
            report['timingConvention']='exposure midpoint at mean detected feature row plus estimated residual clock offset; not a full rolling-shutter model'
            def samples(name):
                rows=[v for v in imu if v['sensor']==name]
                return np.array([(int(v['timestampNs'])-origin)/1e9 for v in rows]),np.array([[v[k] for k in ['x','y','z']] for v in rows])
            gt,gv=samples('gyroscope')
            alignment=fit_gyro_alignment(times,np.array([v[1] for v in poses]),gt,gv)
            report['cameraImuRotationTiming']=alignment
            if not alignment['passed']: raise ValueError('Held-out gyro/clock alignment did not pass')
            # Lever arm / accelerometer calibration from metric board poses. Smooth before derivatives.
            from scipy.signal import savgol_filter
            times=np.asarray(times);R=np.array([v[1] for v in poses]);P=np.array([v[2] for v in poses])
            if len(times)<50 or np.max(np.diff(times))>.3: raise ValueError('Too many board pose gaps for translation calibration')
            grid=np.arange(times[0]+.4,times[-1]-.4,.05)
            if len(grid)<80: raise ValueError('Too little continuous dynamic calibration')
            smooth_p=savgol_filter(np.column_stack([np.interp(grid,times,P[:,k]) for k in range(3)]),15,3,axis=0)
            smooth_R=savgol_filter(np.array([np.interp(grid,times,R[:,i,j]) for i in range(3) for j in range(3)]).T,15,3,axis=0).reshape(-1,3,3)
            # Reproject smoothed rotation matrices onto SO(3).
            smooth_R=np.array([Rotation.from_matrix(v).as_matrix() for v in smooth_R])
            pdd=CubicSpline(grid,smooth_p)(grid,2);rdd=CubicSpline(grid,smooth_R)(grid,2)
            at,av=samples('accelerometer');rot=np.array(alignment['rotationImuToCamera'])
            accel=np.column_stack([np.interp(grid+alignment['residualTimeOffsetSeconds'],at,av[:,k]) for k in range(3)])
            Q=smooth_R@rot
            report['translationAcceleration']=fit_accel_geometry(pdd,rdd,Q,accel)
            if not report['translationAcceleration']['passed']: raise ValueError('Translation/acceleration calibration did not pass; no full calibration activated')
            report['status']='geometry-candidate'
            report['limitations']=['Printed square size must be physically checked','Held-out frames are not an independent walking-distance validation',
               'Rolling-shutter model is approximate','Full IMU noise/random-walk characterization not measured','Only matching native image pipeline can reuse this geometry']
    except (ValueError,KeyError,TypeError,zipfile.BadZipFile,cv2.error,OSError) as e:
        report['errors'].append(str(e))
    (output/'calibration-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    return report
