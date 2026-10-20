"""Lossless-clock adapters and diagnostic feature tracks for VIO references.

No clinical output: calibration/noise guesses must be disclosed by the caller.
Original JPEGs, all five distortion coefficients and native image axes are kept.
"""
import csv
import hashlib
import json
import time
import subprocess
import os
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
        profile = (json.loads(Path(profile_path).read_text()) if profile_path else
                   json.loads(bundle.read('research-profile.json'))
                   if 'research-profile.json' in bundle.namelist() else None)
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


class CudaLK:
    """One image upload per frame; both LK directions execute on CUDA.

    Shi-Tomasi corner selection also runs on CUDA; calibrated RANSAC stays CPU.
    CUDA uses 30 iterations, whereas CPU LK may terminate early on epsilon.
    These backends are recorded separately and are not bit-identical.
    """
    def __init__(self, max_features=150, min_distance=20, query_device=False):
        if cv2.cuda.getCudaEnabledDeviceCount() < 1:
            raise RuntimeError('OpenCV CUDA device unavailable; CPU wheels cannot enable CUDA.')
        cv2.cuda.setDevice(0)
        self.flow = cv2.cuda_SparsePyrLKOpticalFlow.create((21, 21), 3, 30)
        self.detector = cv2.cuda.createGoodFeaturesToTrackDetector(cv2.CV_8UC1, max_features, .01, min_distance)
        self.previous = None
        self.current = None
        self.calls = 0
        self.corner_calls = 0
        # OpenCV's Python DeviceInfo binding does not expose name() in 4.12.
        self.device = os.environ.get('GAITTRACE_GPU_NAME', 'CUDA device 0')
        if query_device:
            self.device = subprocess.check_output(['nvidia-smi', '--query-gpu=name',
                '--format=csv,noheader'], text=True, timeout=5).splitlines()[0].strip()

    def upload(self, image):
        self.previous = self.current
        self.current = cv2.cuda_GpuMat()
        self.current.upload(image)

    def track(self, points):
        gpu_points = cv2.cuda_GpuMat()
        gpu_points.upload(np.ascontiguousarray(points.reshape(1, -1, 2)))
        tracked, good, _ = self.flow.calc(self.previous, self.current, gpu_points, None)
        back, reverse_good, _ = self.flow.calc(self.current, self.previous, tracked, None)
        # download synchronizes the actual kernels; detection alone is not proof.
        result = tracked.download(), good.download(), back.download(), reverse_good.download()
        self.calls += 2
        return result

    def corners(self, mask, limit):
        gpu_mask = cv2.cuda_GpuMat()
        gpu_mask.upload(mask)
        result = self.detector.detect(self.current, mask=gpu_mask).download()
        self.corner_calls += 1
        return None if result is None else result.reshape(-1, 2)[:limit]


def cuda_probe():
    tracker = CudaLK(query_device=True)
    image = np.random.default_rng(0).integers(0, 256, (96, 96), dtype=np.uint8)
    tracker.upload(image)
    tracker.upload(image)
    p, ok, back, reverse = tracker.track(np.array([[48, 48]], np.float32))
    corners = tracker.corners(np.full(image.shape, 255, np.uint8), 10)
    if not ok.all() or not reverse.all() or np.linalg.norm(back.reshape(-1, 2)-[[48, 48]]) > .1:
        raise RuntimeError('CUDA LK kernel check failed.')
    if corners is None or len(corners) == 0:
        raise RuntimeError('CUDA corner kernel check failed.')
    return {'backend': 'cuda', 'device': tracker.device, 'kernelCheckPassed': True,
            'opencvVersion': cv2.__version__, 'cudaLKCalls': tracker.calls,
            'cudaCornerCalls': tracker.corner_calls}


def export_feature_tracks(directory, max_features=150, min_distance=20, backend='cpu'):
    """Diagnostic LK frontend; NOT the unchanged VINS-Mono frontend.

    Forward/backward consistency and calibrated epipolar rejection. Keep raw
    pixel rows for rolling-shutter factors, normalize with all five coefficients.
    No guessed holder mask, image rotation or undistorted-image row substitution.
    """
    started = time.perf_counter()
    if backend not in ('cpu', 'cuda'):
        raise ValueError('Unknown feature backend')
    tracker = CudaLK(max_features, min_distance) if backend == 'cuda' else None
    # Avoid oversubscribing the laptop for tiny frames and 150 feature points.
    cv2.setNumThreads(2)
    cv2.setRNGSeed(0)
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
    previous_normal = np.empty((0, 2), np.float64)
    previous_ids = np.empty(0, np.int64)
    previous_time = None
    counts = []
    stages = dict(decodeSeconds=0., imageUploadSeconds=0., flowSeconds=0.,
                  geometrySeconds=0., cornersSeconds=0., outputSeconds=0.)
    with (directory/'features.csv').open('w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['timestamp_ns', 'id', 'nx', 'ny', 'u', 'v', 'vx', 'vy'])
        for frame in frames:
            tick = time.perf_counter()
            image = cv2.imread(str(directory/frame['file']), cv2.IMREAD_GRAYSCALE)
            stages['decodeSeconds'] += time.perf_counter()-tick
            if image is None:
                raise ValueError('Unreadable replay frame')
            if tracker:
                tick = time.perf_counter()
                tracker.upload(image)
                stages['imageUploadSeconds'] += time.perf_counter()-tick
            timestamp = int(frame['timestamp_ns'])
            if previous is not None and len(points):
                tick = time.perf_counter()
                if tracker:
                    tracked, good, back, reverse_good = tracker.track(points)
                else:
                    tracked, good, _ = cv2.calcOpticalFlowPyrLK(previous, image, points.reshape(-1, 1, 2), None)
                    back, reverse_good, _ = cv2.calcOpticalFlowPyrLK(image, previous, tracked, None)
                stages['flowSeconds'] += time.perf_counter()-tick
                tick = time.perf_counter()
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
                stages['geometrySeconds'] += time.perf_counter()-tick
            tick = time.perf_counter()
            mask = np.full(image.shape, 255, np.uint8)
            for p in points:
                cv2.circle(mask, tuple(np.rint(p).astype(int)), min_distance, 0, -1)
            if len(points) < max_features:
                new = (tracker.corners(mask, max_features-len(points)) if tracker else
                       cv2.goodFeaturesToTrack(image, max_features-len(points), .01, min_distance, mask=mask))
                if new is not None:
                    new = new.reshape(-1, 2)
                    points = np.concatenate([points, new])
                    ids = np.concatenate([ids, np.arange(next_id, next_id+len(new))])
                    next_id += len(new)
            stages['cornersSeconds'] += time.perf_counter()-tick
            tick = time.perf_counter()
            normalized = cv2.undistortPoints(points.reshape(-1, 1, 2), K, D).reshape(-1, 2) if len(points) else np.empty((0, 2))
            velocity = np.zeros_like(normalized)
            if len(previous_ids) and len(ids):
                # IDs remain sorted after rejection/new allocation. Vectorize
                # velocity without converting hardware timestamps into floats.
                index = np.searchsorted(previous_ids, ids)
                valid = index < len(previous_ids)
                valid[valid] &= previous_ids[index[valid]] == ids[valid]
                velocity[valid] = (normalized[valid]-previous_normal[index[valid]])/((timestamp-previous_time)/1e9)
            writer.writerows([timestamp, int(ident), *normal, *pixel, *speed]
                             for ident, pixel, normal, speed in zip(ids, points, normalized, velocity))
            stages['outputSeconds'] += time.perf_counter()-tick
            counts.append(len(points))
            previous, previous_normal, previous_ids, previous_time = image, normalized, ids.copy(), timestamp
    summary = {'frames': len(counts), 'minFeatures': min(counts), 'medianFeatures': float(np.median(counts)),
               'frontend': 'diagnostic-'+backend+'-lk-fb-calibrated-f-v2', 'fullCalibrationReady': False,
               'distanceReady': False, 'featuresSha256': hashlib.sha256((directory/'features.csv').read_bytes()).hexdigest()}
    summary.update(backend=backend, opencvVersion=cv2.__version__,
                   frontendSourceSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   elapsedSeconds=time.perf_counter()-started, cpuThreads=2, ransacSeed=0,
                   cudaLKCalls=tracker.calls if tracker else 0,
                   cudaCornerCalls=tracker.corner_calls if tracker else 0,
                   gpuUsed=bool(tracker and (tracker.calls or tracker.corner_calls)),
                   gpuDevice=tracker.device if tracker else None,
                   cpuStages=['JPEG decoding', 'calibrated RANSAC', 'CSV output']+([] if tracker else ['Shi-Tomasi corner selection']),
                   kernelDifference='CUDA fixed 30 iterations; CPU epsilon early exit' if tracker else None)
    summary['stageTimings'] = stages
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


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--cuda-probe', action='store_true')
    parser.add_argument('--worker', action='store_true')
    parser.add_argument('--tracks', type=Path)
    parser.add_argument('--backend', choices=['cpu', 'cuda'], default='cuda')
    args = parser.parse_args()
    if args.worker:
        import sys, re, traceback
        for line in sys.stdin:
            request = {}
            try:
                request = json.loads(line)
                if request.get('command') == 'probe':
                    result = cuda_probe()
                    os.environ['GAITTRACE_GPU_NAME'] = result['device']
                elif request.get('command') == 'cpu-probe':
                    result = {'backend': 'cpu', 'gpuUsed': False, 'kernelCheckPassed': False,
                              'opencvVersion': cv2.__version__, 'worker': 'persistent-native-cpu'}
                elif request.get('command') == 'tracks':
                    directory = request['directory']
                    if not re.fullmatch(r'/jobs/(replay|benchmark)-[A-Za-z0-9]+', directory):
                        raise ValueError('Invalid worker workspace')
                    result = export_feature_tracks(directory, backend=request.get('backend', 'cuda'))
                else:
                    raise ValueError('Unknown worker command')
                response = {'id': request.get('id'), 'ok': True, 'result': result}
            except Exception as error:
                traceback.print_exc(file=sys.stderr)
                response = {'id': request.get('id'), 'ok': False, 'error': str(error)}
            print(json.dumps(response), flush=True)
    else:
        print(json.dumps(cuda_probe() if args.cuda_probe else export_feature_tracks(args.tracks, backend=args.backend)))
