"""Lossless-clock adapters and diagnostic feature tracks for VIO references.

No clinical output: calibration/noise guesses must be disclosed by the caller.
Original JPEGs, all five distortion coefficients and native image axes are kept.
"""
import csv
import hashlib
import json
import zipfile
from pathlib import Path

import cv2
import numpy as np


def _rows(bundle, name):
    return [json.loads(line) for line in bundle.read(name).decode().splitlines() if line.strip()]


def _rate(times):
    times = np.asarray(times, dtype=np.int64)
    if len(times) < 2 or np.any(np.diff(times) <= 0):
        raise ValueError('Stream needs strictly increasing hardware timestamps')
    return float((len(times)-1)*1e9/(int(times[-1])-int(times[0])))


def export_capture(source, destination, profile_path=None):
    """Pair asynchronous accel/gyro at gyro times; never upsample the camera.

    Acceleration is linearly interpolated only between bracketing real samples.
    Frame clocks are exposure/readout midpoint, without the profile time offset;
    VINS applies that offset when associating IMU and camera observations.
    """
    source, destination = Path(source), Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(source) as bundle:
        manifest = json.loads(bundle.read('manifest.json'))
        profile = (json.loads(bundle.read('research-profile.json'))
                   if 'research-profile.json' in bundle.namelist()
                   else json.loads(Path(profile_path).read_text()) if profile_path else None)
        if not profile:
            raise ValueError('A matching profile is required; no borrowed device geometry')
        binding_keys=['installationId', 'cameraId', 'width', 'height', 'imageAxes', 'sensorOrientationDegrees']
        if manifest.get('capturePipeline'):
            binding_keys.extend(['capturePipeline','opticalSetup'])
        for key in binding_keys:
            if manifest.get(key) != profile['binding'].get(key):
                raise ValueError('Profile mismatch: '+key)
        if manifest['timestampSource'] != 'realtime':
            raise ValueError('No verified common camera/IMU clock')
        if manifest['units'].get('accelerometer') != 'm/s2' or manifest['units'].get('gyroscope') != 'rad/s':
            raise ValueError('IMU SI units are required')
        streams = _rows(bundle, 'imu.ndjson')
        acc = [r for r in streams if r['sensor'] == 'accelerometer']
        gyro = [r for r in streams if r['sensor'] == 'gyroscope']
        ats = np.array([r['timestampNs'] for r in acc], dtype=np.int64)
        gts = np.array([r['timestampNs'] for r in gyro], dtype=np.int64)
        arate, grate = _rate(ats), _rate(gts)
        av = np.array([[r[k] for k in ['x', 'y', 'z']] for r in acc])
        gv = np.array([[r[k] for k in ['x', 'y', 'z']] for r in gyro])
        if not np.isfinite(av).all() or not np.isfinite(gv).all():
            raise ValueError('Nonfinite IMU')
        valid = (gts >= ats[0]) & (gts <= ats[-1])
        idx = np.clip(np.searchsorted(ats, gts[valid], side='right'), 1, len(ats)-1)
        gaps = ats[idx]-ats[idx-1]
        if np.max(gaps) > 20_000_000:
            raise ValueError('Acceleration interpolation spans a gap over 20 ms')
        weight = (gts[valid]-ats[idx-1])/gaps
        interp = av[idx-1]*(1-weight[:, None])+av[idx]*weight[:, None]
        with (destination/'imu.csv').open('w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['timestamp_ns', 'gx', 'gy', 'gz', 'ax', 'ay', 'az'])
            writer.writerows([[int(t), *g, *a] for t, g, a in zip(gts[valid], gv[valid], interp)])
        frames = _rows(bundle, 'frames.ndjson')
        camera = {r['timestampNs']: r for r in _rows(bundle, 'capture-results.ndjson')}
        _rate([r['timestampNs'] for r in frames])
        frame_rows = []
        for frame in frames:
            timestamp = frame['timestampNs']
            metadata = camera[timestamp]
            exposure, skew = metadata['exposureNs'], metadata['rollingShutterSkewNs']
            if exposure is None or skew is None or exposure < 0 or skew < 0:
                raise ValueError('Missing exposure/readout timing')
            # Rounded integer nanoseconds; no epoch or arrival-time substitution.
            midpoint = timestamp+(int(exposure)+int(skew))//2
            name = frame['file']
            path = Path(name)
            if path.is_absolute() or '..' in path.parts or len(path.parts) != 2 or path.parts[0] != 'frames':
                raise ValueError('Unsafe frame path')
            target = destination/path
            target.parent.mkdir(exist_ok=True)
            data = bundle.read(name)
            image = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_GRAYSCALE)
            if image is None or image.shape != (manifest['height'], manifest['width']):
                raise ValueError('Invalid frame dimensions')
            target.write_bytes(data)
            frame_rows.append([midpoint, name, timestamp, exposure, skew])
        with (destination/'frames.csv').open('w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['timestamp_ns', 'file', 'sensor_timestamp_ns', 'exposure_ns', 'readout_ns'])
            writer.writerows(frame_rows)
        (destination/'profile.json').write_text(json.dumps(profile, indent=2))
        summary = {'kind': 'vio-reference-input-v1', 'captureId': manifest['captureId'],
                   'sourceSha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                   'frameCount': len(frame_rows), 'cameraHz': _rate([r[0] for r in frame_rows]),
                   'accelHz': arate, 'gyroHz': grate, 'pairedImuCount': int(valid.sum()),
                   'discardedUnbracketedGyro': int((~valid).sum()),
                   'maxAccelerationInterpolationGapNs': int(np.max(gaps)),
                   'timeOffsetSeconds': profile['rotationTiming']['residualTimeOffsetSeconds'],
                   'readoutSeconds': float(np.median([r[4] for r in frame_rows]))/1e9,
                   'walkStartedBootNs': manifest.get('diagnostics', {}).get('walkStartedBootNs'),
                   'fullCalibrationReady': False, 'distanceReady': False,
                   'limitations': ['JPEG replay, not original native luma',
                       'Full camera/IMU geometry and sensor noise not established',
                       'No route ground truth is used to set scale',
                       'Includes setup; timed clinical boundaries are not inferred']}
        (destination/'input-summary.json').write_text(json.dumps(summary, indent=2))
        return summary


def export_feature_tracks(directory, max_features=150, min_distance=20):
    """Diagnostic LK frontend; NOT the unchanged VINS-Mono frontend.

    Forward/backward consistency and calibrated epipolar rejection. Keep raw
    pixel rows for rolling-shutter factors, normalize with all five coefficients.
    No guessed holder mask, image rotation or undistorted-image row substitution.
    """
    directory = Path(directory)
    profile = json.loads((directory/'profile.json').read_text())
    K = np.asarray(profile['lens']['cameraMatrix'], np.float64)
    D = np.asarray(profile['lens']['distortion'], np.float64)
    with (directory/'frames.csv').open() as file:
        frames = list(csv.DictReader(file))
    previous = None
    points = np.empty((0, 2), np.float32)
    ids = np.empty(0, np.int64)
    next_id = 0
    previous_normal = {}
    previous_time = None
    counts = []
    with (directory/'features.csv').open('w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['timestamp_ns', 'id', 'nx', 'ny', 'u', 'v', 'vx', 'vy'])
        for frame in frames:
            image = cv2.imread(str(directory/frame['file']), cv2.IMREAD_GRAYSCALE)
            timestamp = int(frame['timestamp_ns'])
            if previous is not None and len(points):
                tracked, good, _ = cv2.calcOpticalFlowPyrLK(previous, image, points.reshape(-1, 1, 2), None)
                back, reverse_good, _ = cv2.calcOpticalFlowPyrLK(image, previous, tracked, None)
                p = tracked.reshape(-1, 2)
                valid = (good.ravel()!=0) & (reverse_good.ravel()!=0)
                valid &= np.linalg.norm(back.reshape(-1, 2)-points, axis=1) < 1
                valid &= (p[:, 0]>1) & (p[:, 0]<image.shape[1]-2) & (p[:, 1]>1) & (p[:, 1]<image.shape[0]-2)
                old, points, ids = points[valid], p[valid], ids[valid]
                if len(points) >= 8:
                    a = cv2.undistortPoints(old.reshape(-1, 1, 2), K, D).reshape(-1, 2)
                    b = cv2.undistortPoints(points.reshape(-1, 1, 2), K, D).reshape(-1, 2)
                    _, keep = cv2.findFundamentalMat(a, b, cv2.FM_RANSAC, 1/float(K[0, 0]), .99)
                    if keep is not None:
                        points, ids = points[keep.ravel()!=0], ids[keep.ravel()!=0]
            mask = np.full(image.shape, 255, np.uint8)
            for p in points:
                cv2.circle(mask, tuple(np.rint(p).astype(int)), min_distance, 0, -1)
            if len(points) < max_features:
                new = cv2.goodFeaturesToTrack(image, max_features-len(points), .01, min_distance, mask=mask)
                if new is not None:
                    new = new.reshape(-1, 2)
                    points = np.concatenate([points, new])
                    ids = np.concatenate([ids, np.arange(next_id, next_id+len(new))])
                    next_id += len(new)
            normalized = cv2.undistortPoints(points.reshape(-1, 1, 2), K, D).reshape(-1, 2) if len(points) else []
            now = {}
            for ident, pixel, normal in zip(ids, points, normalized):
                velocity = ((normal-previous_normal[int(ident)])/((timestamp-previous_time)/1e9)
                            if int(ident) in previous_normal else np.zeros(2))
                writer.writerow([timestamp, int(ident), *normal, *pixel, *velocity])
                now[int(ident)] = normal
            counts.append(len(points))
            previous, previous_normal, previous_time = image, now, timestamp
    summary = {'frames': len(counts), 'minFeatures': min(counts), 'medianFeatures': float(np.median(counts)),
               'frontend': 'diagnostic-python-lk-fb-calibrated-f-v1', 'fullCalibrationReady': False,
               'distanceReady': False, 'featuresSha256': hashlib.sha256((directory/'features.csv').read_bytes()).hexdigest()}
    (directory/'features-summary.json').write_text(json.dumps(summary, indent=2))
    return summary


def write_reference_config(directory, noise_multiplier=1):
    """Explicit provisional EuRoC-reference noise; not phone-calibrated values.

    Online extrinsic refinement starts with the measured rotation and zero
    translation guess. No route length or assumed step length enters this fit.
    """
    if not np.isfinite(noise_multiplier) or noise_multiplier <= 0:
        raise ValueError('Positive noise multiplier required')
    directory = Path(directory)
    profile = json.loads((directory/'profile.json').read_text())
    summary = json.loads((directory/'input-summary.json').read_text())
    rotation = np.asarray(profile['rotationTiming']['rotationImuToCamera'], np.float64).T
    config = cv2.FileStorage(str(directory/'reference.yaml'), cv2.FILE_STORAGE_WRITE)
    config.write('extrinsicRotation', rotation)
    config.write('extrinsicTranslation', np.zeros((3, 1)))
    config.write('td', summary['timeOffsetSeconds'])
    config.write('readout', summary['readoutSeconds'])
    noise = {'acc_n': .08, 'acc_w': .00004, 'gyr_n': .004, 'gyr_w': .000002}
    for name, value in noise.items():
        config.write(name, value*noise_multiplier)
    config.release()
    assumptions = {'noiseSource': 'VINS-Mono EuRoC example, provisional only',
                   'noiseMultiplier': noise_multiplier, 'noise': {k: v*noise_multiplier for k,v in noise.items()},
                   'translationSource': 'zero initial guess; online refinement enabled',
                   'rotationSource': 'transpose of measured IMU-to-camera research rotation',
                   'timingSource': 'exposure/readout midpoint plus VINS td association',
                   'rollingShutter': 'upstream raw-row velocity factor; not exposure deblurring',
                   'fullCalibrationReady': False, 'distanceReady': False,
                   'scope': 'offline estimator feasibility only, not a clinical metric validation'}
    (directory/'reference-assumptions.json').write_text(json.dumps(assumptions, indent=2))
    return assumptions


def summarize_reference(directory, source, prefix='reference'):
    """Report state integrity without admitting it as a clinical distance."""
    directory=Path(directory)
    with zipfile.ZipFile(source) as bundle:
        manifest=json.loads(bundle.read('manifest.json'))
    start=manifest['diagnostics']['walkStartedBootNs']/1e9
    with (directory/(prefix+'-states.csv')).open() as file:
        rows=list(csv.DictReader(file))
    ready=[r for r in rows if r['initialized']=='1']
    walking=[r for r in ready if float(r['imu_time_s'])>=start]
    if not walking:
        raise ValueError('No initialized states after the app movement trigger')
    speed=np.array([np.linalg.norm([float(r[k]) for k in ['vx','vy','vz']]) for r in ready])
    positions=np.array([[float(r[k]) for k in ['px','py','pz']] for r in walking])
    stderr=(directory/(prefix+'-stderr.txt')).read_text()
    result={'captureId':manifest['captureId'],'initializedFrames':len(ready),
            'initializedFramesAfterAppTrigger':len(walking),
            'lastFrameInitialized':rows[-1]['initialized']=='1',
            'reboots':stderr.count('system reboot!'),
            'maxInitializedStateSpeedMetresPerSecond':float(np.max(speed)),
            'maxInitializedAccelerationBiasNorm':max(float(r['ba_norm']) for r in ready),
            'maxInitializedGyroBiasNorm':max(float(r['bg_norm']) for r in ready),
            'initialTimeOffsetSeconds':json.loads((directory/'input-summary.json').read_text())['timeOffsetSeconds'],
            'finalTimeOffsetSeconds':float(rows[-1]['td']),
            'distanceReady':False,'fullCalibrationReady':False,'independentDistanceValidation':False,
            'limitations':['App movement trigger is not verified first step/course boundary',
                'IMU position state is not an accepted complete walking-distance measurement',
                'Online estimated calibration and reference noise remain provisional',
                'No ground-truth route length is used to fit scale']}
    if 'tic_norm' in rows[0]:
        result['maxInitializedCameraImuTranslationNormMetres']=max(float(r['tic_norm']) for r in ready)
        result['maxCameraImuTranslationNormAfterAppTriggerMetres']=max(float(r['tic_norm']) for r in walking)
        result['lastInitializedCameraImuTranslationNormMetres']=float(ready[-1]['tic_norm'])
        result['maxInitializedRotationChangeDegrees']=max(float(r['rotation_change_deg']) for r in ready)
        result['finalInitializedGravityNorm']=float(ready[-1]['g_norm'])
    if result['reboots']==0 and result['lastFrameInitialized']:
        result['provisionalImuPositionPathAfterAppTriggerMetres']=float(np.linalg.norm(np.diff(positions,axis=0),axis=1).sum())
        result['provisionalImuPositionDisplacementAfterAppTriggerMetres']=float(np.linalg.norm(positions[-1]-positions[0]))
    else:
        result['provisionalImuPositionPathAfterAppTriggerMetres']=None
        result['provisionalImuPositionDisplacementAfterAppTriggerMetres']=None
        result['limitations'].append('Reset/incomplete final tracking: do not stitch or report a route distance')
    (directory/(prefix+'-integrity.json')).write_text(json.dumps(result,indent=2))
    return result
