"""Engineering readiness contract for a future continuous VIO adapter.

This consumes complete estimator states, not the old scalar-only replay CSV.
Limits are provisional research gates, not validated clinical tolerances.
No gate grants clinical distance or anatomical placement verification.
"""
import numpy as np


def assess_readiness(states, calibration):
    result={'status':'blocked','reasons':[], 'clinicalReady':False,
            'distanceReady':False,'researchTrackingReady':False,
            'contract':'vio-stable-start-v1'}
    if calibration.get('geometryVerified') is not True:
        result['reasons'].append('full-camera-imu-geometry-required')
    if calibration.get('measuredWhiteNoiseVerified') is not True or calibration.get('biasRandomWalkVerified') is not True:
        result['reasons'].append('complete-measured-noise-model-required')
    if calibration.get('deviceAndOpticsMatched') is not True:
        result['reasons'].append('device-and-optics-binding-required')
    if not states:
        result['reasons'].append('continuous-estimator-states-required')
        return result
    required={'timeSeconds','initialized','resetCount','trackedFeatures','translationCameraToImuMetres',
              'rotationCameraToImuQuaternionWxyz','velocityMetresPerSecond','accelBias','gyroBias',
              'timeOffsetSeconds','gravityNorm'}
    if any(not required.issubset(s) for s in states):
        result['reasons'].append('complete-vector-state-telemetry-required')
        return result
    try:
        t=np.array([s['timeSeconds'] for s in states],float)
        if not np.isfinite(t).all() or np.any(np.diff(t)<=0):raise ValueError()
        window=[s for s in states if s['timeSeconds']>=t[-1]-2.05]
        wt=np.array([s['timeSeconds'] for s in window],float)
        if len(window)<20 or wt[-1]-wt[0]<2 or np.max(np.diff(wt))>.15:
            result['reasons'].append('two-seconds-continuous-tracking-required')
        if any(s['initialized'] is not True for s in window) or len({s['resetCount'] for s in window})!=1:
            result['reasons'].append('initialization-or-reset-in-stability-window')
        vectors={k:np.asarray([s[k] for s in window],float) for k in
                 ('translationCameraToImuMetres','rotationCameraToImuQuaternionWxyz','velocityMetresPerSecond','accelBias','gyroBias')}
        for k,v in vectors.items():
            if v.shape!=(len(window),4 if 'Quaternion' in k else 3) or not np.isfinite(v).all():raise ValueError()
        scalar=np.asarray([[s[k] for k in ('timeOffsetSeconds','gravityNorm','trackedFeatures')] for s in window],float)
        if not np.isfinite(scalar).all():raise ValueError()
        norms=lambda k:np.linalg.norm(vectors[k],axis=1)
        if np.max(norms('translationCameraToImuMetres'))>.20 or np.max(norms('velocityMetresPerSecond'))>3 or np.max(norms('accelBias'))>.5 or np.max(norms('gyroBias'))>.1 or np.max(np.abs(scalar[:,0]))>.15 or np.any((scalar[:,1]<8.8)|(scalar[:,1]>10.8)):
            result['reasons'].append('physically-implausible-state')
        if np.min(scalar[:,2])<20:result['reasons'].append('insufficient-feature-support')
        translation=vectors['translationCameraToImuMetres']
        q=vectors['rotationCameraToImuQuaternionWxyz'];qn=np.linalg.norm(q,axis=1)
        if np.max(np.abs(qn-1))>.001:raise ValueError()
        degrees=np.degrees(2*np.arccos(np.clip(np.abs((q@q[0])/(qn*qn[0])),0,1)))
        if np.max(np.linalg.norm(translation-translation[0],axis=1))>.01 or np.max(degrees)>1 or np.ptp(scalar[:,0])>.002:
            result['reasons'].append('camera-imu-calibration-still-changing')
        result['stabilityWindowSeconds']=float(wt[-1]-wt[0])
    except (ValueError,TypeError,KeyError):
        result['reasons'].append('invalid-estimator-state')
    if not result['reasons']:
        result.update(status='research-ready',researchTrackingReady=True)
    return result
