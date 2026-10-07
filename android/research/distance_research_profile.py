"""Export a phone-bound, rotation-only profile for the Android research trial.

Never upgrades it to full geometry, clinical distance readiness or validation.
The app imports this separately from its accepted full calibration reports.
"""
import hashlib
import json
from pathlib import Path
import numpy as np


def export_research_profile(lens_report, rotation_report, destination):
    if (not rotation_report.get('passed') or rotation_report.get('method')!='row-timed-gyro-pixel-fit-v1'
            or rotation_report.get('distanceReady') is not False
            or rotation_report.get('fullCalibrationReady') is not False):
        raise ValueError('No passing research rotation/timing candidate')
    expected=hashlib.sha256(Path(__file__).with_name('camera_imu_joint.py').read_bytes()).hexdigest()
    if rotation_report.get('processorSha256')!=expected:
        raise ValueError('Rotation report does not identify this processor version')
    lens=lens_report['lens'];binding=lens_report['binding']
    if not binding.get('installationId') or lens.get('heldOutP90Pixels',float('inf'))>1.5:
        raise ValueError('Missing installation binding or acceptable lens fit')
    K=np.asarray(lens['cameraMatrix']);R=np.asarray(rotation_report['rotationImuToCamera'])
    if K.shape!=(3,3) or R.shape!=(3,3) or not np.isfinite(K).all() or not np.isfinite(R).all() or not np.allclose(R@R.T,np.eye(3),atol=.001):
        raise ValueError('Invalid camera geometry')
    profile={'schemaVersion':1,'kind':'phone-camera-distance-research-profile-v1',
             'binding':binding,'lens':lens,'rotationTiming':rotation_report,
             'sourceBundleSha256':lens_report['bundleSha256'],
             'distanceReady':False,'fullCalibrationReady':False,'independentDistanceValidation':False,
             'limitations':['Rotation/timing development fit only; target stationarity not independently confirmed',
                            'Accelerometer/lever-arm calibration incomplete',
                            'Not a clinical distance or stopping reference']}
    Path(destination).write_text(json.dumps(profile,indent=2),encoding='utf-8')
    return profile
