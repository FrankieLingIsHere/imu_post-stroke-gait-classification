"""Stationary phone noise characterization, not a full VIO calibration.

Kalibr continuous white-noise convention: discrete sigma = density/sqrt(dt).
Use overlapping Allan deviation of measured values at native sample times.
No interpolation/decimation, borrowed noise constants or inferred accel bias.
"""
import hashlib
import json
import zipfile
from pathlib import Path

import numpy as np


def characterize(times_ns, values, sensor):
    times = np.asarray(times_ns, dtype=np.int64)
    values = np.asarray(values, dtype=float)
    if values.shape != (len(times), 3) or len(times) < 100 or not np.isfinite(values).all():
        raise ValueError('Invalid sensor values')
    intervals = np.diff(times).astype(float) / 1e9
    if np.any(intervals <= 0):
        raise ValueError('Nonmonotonic sensor clock')
    duration = (int(times[-1])-int(times[0])) / 1e9
    if duration < 180:
        raise ValueError('At least three minutes of stationary data required')
    dt = float(np.mean(intervals))
    jitter = float(np.std(intervals) / dt)
    # A uniform-clock Allan estimator is inappropriate for substantial gaps/jitter.
    if jitter > .05 or np.max(intervals) > max(.020, 2*dt):
        raise ValueError('Sensor gaps or timing jitter prevent noise fitting')
    norm = np.linalg.norm(values, axis=1)
    if sensor == 'accelerometer':
        if not 8.8 < np.mean(norm) < 10.8 or np.std(norm) > .10 or np.max(np.std(values, axis=0)) > .15:
            raise ValueError('Phone moved or acceleration units are invalid')
    elif sensor == 'gyroscope':
        if np.linalg.norm(np.mean(values, axis=0)) > .05 or np.max(np.std(values, axis=0)) > .02:
            raise ValueError('Phone moved or angular-rate units are invalid')
    else:
        raise ValueError('Noise fitting supports accelerometer and gyroscope only')
    # Use 20 ms to 1 s for a short-term white-noise candidate. Preserve all points
    # to 10 s for review; do not pretend this identifies long-term random walk.
    factors = np.unique(np.maximum(1, np.round(np.geomspace(max(dt,.02),10,30)/dt).astype(int)))
    summed = np.vstack([np.zeros((1,3)), np.cumsum(values,axis=0)])
    taus, deviation = [], []
    for m in factors:
        means = (summed[m:]-summed[:-m])/m
        if len(means) <= m or len(means)-m < 100:
            continue
        taus.append(float(m*dt))
        deviation.append(np.sqrt(np.mean((means[m:]-means[:-m])**2,axis=0)/2))
    taus, deviation = np.asarray(taus), np.asarray(deviation)
    short = (taus <= 1) & (taus >= max(dt,.02))
    if np.sum(short) < 5 or np.any(deviation[short] <= 0):
        raise ValueError('Insufficient nonzero Allan samples')
    slopes = [float(np.polyfit(np.log(taus[short]),np.log(deviation[short,i]),1)[0]) for i in range(3)]
    density = np.median(deviation[short]*np.sqrt(taus[short,None]),axis=0)
    candidate = all(-.65 <= v <= -.35 for v in slopes)
    return {'durationSeconds':duration,'sampleCount':len(times),'sampleRateHz':1/dt,
            'intervalCoefficientOfVariation':jitter,'maxGapSeconds':float(np.max(intervals)),
            'meanAxes':np.mean(values,axis=0).tolist(),'stdAxes':np.std(values,axis=0).tolist(),
            'whiteNoiseSlopes':slopes,'whiteNoiseDensityCandidate':density.tolist() if candidate else None,
            'whiteNoiseCandidateReady':candidate,'biasRandomWalkReady':False,
            'allan':{'tauSeconds':taus.tolist(),'deviationAxes':deviation.tolist()}}


def process_noise(source):
    source = Path(source)
    report = {'schemaVersion':1,'kind':'phone-imu-noise-report-v1','status':'rejected',
              'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),
              'whiteNoiseCandidateReady':False,'biasRandomWalkReady':False,
              'fullCalibrationReady':False,'distanceReady':False,'errors':[]}
    try:
        with zipfile.ZipFile(source) as bundle:
            meta = json.loads(bundle.read('manifest.json'))
            report['binding'] = {k:meta.get(k) for k in ('installationId','captureId','device','capturePipeline')}
            if meta.get('kind') != 'phone-imu-noise-capture-v1' or meta.get('status') != 'completed' or meta.get('error') or not meta.get('installationId'):
                raise ValueError('A completed device-bound stationary noise capture is required')
            if meta.get('units') != {'accelerometer':'m/s2','gyroscope':'rad/s','magnetometer':'uT'}:
                raise ValueError('Unknown IMU units')
            rows = [json.loads(v) for v in bundle.read('imu.ndjson').decode().splitlines() if v.strip()]
            groups = {s:[r for r in rows if r['sensor']==s] for s in ('accelerometer','gyroscope','magnetometer')}
            mag = groups['magnetometer']
            if len(mag)<100 or any(b['timestampNs']<=a['timestampNs'] for a,b in zip(mag,mag[1:])) or not np.isfinite([[r[k] for k in ('x','y','z')] for r in mag]).all():
                raise ValueError('Magnetometer stream missing or invalid')
            mt=np.asarray([r['timestampNs'] for r in mag],dtype=np.int64)
            if (int(mt[-1])-int(mt[0]))/1e9<180 or np.max(np.diff(mt))/1e9>.15:
                raise ValueError('Magnetometer coverage insufficient or interrupted')
            report['magnetometerSamples'] = len(mag)
            report['sensors'] = {s:characterize([r['timestampNs'] for r in groups[s]],
                [[r[k] for k in ('x','y','z')] for r in groups[s]],s) for s in ('accelerometer','gyroscope')}
            report['whiteNoiseCandidateReady'] = all(v['whiteNoiseCandidateReady'] for v in report['sensors'].values())
            report['status'] = 'white-noise-candidate' if report['whiteNoiseCandidateReady'] else 'review-required'
            report['limitations'] = ['Short capture does not identify long-term bias random walk.',
                'Stationary acceleration mean includes gravity; it is not accelerometer bias.',
                'Phone filtering, temperature and repeatability need review before estimator use.']
    except (ValueError,KeyError,TypeError,zipfile.BadZipFile) as error:
        report['errors'].append(str(error))
    return report
