"""Controlled calibration diagnosis on retained captures, orchestrated in notebook.

Reference geometry substitutions diagnose a cause, not autonomous enrollment.
No known route length enters a configuration or estimate.
"""
from pathlib import Path
import json
import cv2
import numpy as np


def read_geometry(path: Path):
    f = cv2.FileStorage(str(path), cv2.FILE_STORAGE_READ)
    if not f.isOpened():
        raise ValueError('Missing replay configuration')
    try:
        return {'intrinsics': f.getNode('intrinsics').mat().reshape(-1).tolist(),
                'extrinsics': f.getNode('extrinsics').mat().reshape(-1).tolist(),
                'td': f.getNode('td').real(),
                'acc_noise_density': f.getNode('acc_noise_density').real(),
                'gyro_noise_density': f.getNode('gyro_noise_density').real()}
    finally:
        f.release()


def write_geometry(path: Path, parameters: dict, *, calibrating: bool):
    text = '%YAML:1.0\n---\ncalibrating: '+str(int(calibrating))+'\n'
    for name in ['intrinsics', 'extrinsics']:
        a = parameters[name]
        if not np.isfinite(a).all():
            raise ValueError('Nonfinite geometry')
        text += f'{name}: !!opencv-matrix\n   rows: {len(a)}\n   cols: 1\n   dt: d\n   data: [{", ".join(map(str,a))}]\n'
    for name in ['td', 'acc_noise_density', 'gyro_noise_density']:
        text += name+': '+str(parameters[name])+'\n'
    path.write_text(text)


def geometry_cases(factory: Path, reference: Path, output: Path):
    output.mkdir(parents=True, exist_ok=True)
    a, b = read_geometry(factory), read_geometry(reference)
    specifications = [('factory-fixed', a, False), ('reference-fixed', b, False),
                      ('reference-learning', b, True)]
    for name, keys in [('camera-only-fixed', ['intrinsics']),
                       ('alignment-only-fixed', ['extrinsics']),
                       ('clock-only-fixed', ['td'])]:
        specifications.append((name, {**a, **{k:b[k] for k in keys}}, False))
    result = {}
    for name, p, learning in specifications:
        path = output/(name+'.yaml')
        write_geometry(path,p,calibrating=learning)
        result[name] = path
    return result


def summarize_states(path: Path):
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    active = [r for r in rows if r['initialized']]
    if not active:
        return {'initialized':0,'numericalReady':0}
    last = active[-1]
    positions = np.array([[r['state'][k] for k in ['px','py','pz']] for r in active])
    velocities = np.array([[r['state'][k] for k in ['vx','vy','vz']] for r in active])
    return {'initialized':len(active),'numericalReady':sum(r['numericalCalibrationReady'] for r in rows),
            'finalPositionStdMetres':last['positionStdMetres'],
            'maxPositionNormMetres':float(np.linalg.norm(positions,axis=1).max()),
            'maxSpeedMps':float(np.linalg.norm(velocities,axis=1).max()),
            'cameraValues':last['cameraValues'],'imuToCamera':last['imuToCamera'],
            'timeOffsetSeconds':last['timeOffsetSeconds'],
            'groundTruthUsedToSetScale':False,'physicalAndroidExecution':False}


def endpoint_metrics(path: Path, start_seconds: float, end_seconds: float):
    """Offline geometry diagnostic at saved boundaries; not app admission.

    No marked-route length enters this calculation. A small covariance or a
    plausible endpoint alone does not establish valid tracking.
    """
    rows = [json.loads(line)['state'] for line in path.read_text().splitlines()]
    active = [r for r in rows if r['initialized']]
    if not active or not start_seconds < end_seconds:
        raise ValueError('Missing initialized interval')
    times = np.array([r['imu_time_s'] for r in active])
    if np.any(np.diff(times) <= 0):
        raise ValueError('Nonmonotonic states')
    if start_seconds < times[0] or end_seconds > times[-1]:
        raise ValueError('Saved walking boundaries not covered')
    positions = np.array([[r[k] for k in ['px','py','pz']] for r in active])
    delta = np.array([np.interp(end_seconds,times,positions[:,i])-
                      np.interp(start_seconds,times,positions[:,i]) for i in range(3)])
    return {'horizontalEndpointMetres':float(np.linalg.norm(delta[:2])),
            'endpoint3dMetres':float(np.linalg.norm(delta)),
            'boundarySource':'saved-motion-start-and-end',
            'groundTruthUsedToSetScale':False,'appAdmissionExecuted':False}
