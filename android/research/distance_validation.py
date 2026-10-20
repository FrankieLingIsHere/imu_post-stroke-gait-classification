"""Phone-to-local-computer distance validation using the pinned VINS-Mono replay.

No measured route length is used by the estimator or calibration. Published
estimator + diagnostic LK frontend, provisional noise, no clinical admission.
"""
import csv, hashlib, json, math, os, subprocess, zipfile
from pathlib import Path
import cv2
import numpy as np
from vio_reference import export_capture, write_reference_config
from distance_pipeline import processing_spec, quiet_initialization, validate_engine_capabilities, LEGACY_ENGINE

ENGINE=LEGACY_ENGINE # Historical callers; live selection uses processing_spec().
VINS_COMMIT='90dabb5ec79946ae42fd2e1e91d4e69aabe1e25d'
BINDING=['installationId','cameraId','width','height','imageAxes','sensorOrientationDegrees','stabilizationRequested','capturePipeline','opticalSetup']

def inspect_capture(source):
    with zipfile.ZipFile(source) as z:
        if len(z.namelist())!=len(set(z.namelist())):raise ValueError('Ambiguous capture archive.')
        if sum(v.file_size for v in z.infolist())>350*1024**2:raise ValueError('Capture size is invalid.')
        meta=json.loads(z.read('manifest.json'));reference=json.loads(z.read('reference-calibration.json'))
    gait=meta.get('kind')=='gait-camera-imu-distance-capture-v1'
    if gait:
        import re
        if (not re.fullmatch(r'[a-zA-Z0-9_-]{1,160}',meta.get('sessionId','')) or meta.get('captureId')!='gait-camera-'+meta['sessionId']
            or meta.get('protocol') not in ['research-walk','10mwt','tug','2mwt','6mwt']):raise ValueError('Invalid gait recording binding.')
    if (meta.get('kind') not in ['front-camera-distance-research-v1','gait-camera-imu-distance-capture-v1']
        or meta.get('status') not in (['completed'] if gait else ['quiet-stop','walk-time-limit','time-limit']) or meta.get('error') or not meta.get('diagnostics',{}).get('placementCompleted')):
        raise ValueError('A completed distance walk is needed. The partial capture is retained on the phone.')
    if (reference.get('kind')!='phone-reference-camera-imu-calibration-v1' or reference.get('method')!='ikalibr-tro-2025'
        or reference.get('status')!='reference-solved-review-required'
        or any(reference.get(k) is not False for k in ['distanceReady','fullCalibrationReady','independentDistanceValidation','cameraImuCandidateReady'])
        or not reference.get('binding',{}).get('installationId')
        or any(reference['binding'].get(k)!=meta.get(k) for k in BINDING)):
        raise ValueError('Reference calibration does not match this capture.')
    lens=reference.get('lensProfile',{})
    if any(lens.get('binding',{}).get(k)!=meta.get(k) for k in BINDING):
        raise ValueError('Lens calibration does not match this capture.')
    if lens.get('kind')=='phone-learned-lens-seed-v1':
        from rapid_calibration_worker import validate_seed
        validate_seed(lens,reference['binding'])
    elif lens.get('lensReady') is not True or not math.isfinite(lens.get('lens',{}).get('heldOutP90Pixels',math.inf)) or lens['lens']['heldOutP90Pixels']>1.5:
        raise ValueError('Invalid lens calibration.')
    return meta,reference

def parameters(reference):
    p=reference['upstreamParameters']['CalibParam']
    def item(section,key,topic):
        rows=[v['value'] for v in p[section][key] if v['key']==topic]
        if len(rows)!=1:raise ValueError('Missing or ambiguous reference parameter: '+key)
        return rows[0]
    # Both upstreams express camera -> reference IMU, no transpose here.
    q=item('EXTRI','SO3_CmToBr','/gaittrace/camera')
    x,y,z,w=[float(q[k]) for k in ['qx','qy','qz','qw']]
    if abs(x*x+y*y+z*z+w*w-1)>1e-5:raise ValueError('Invalid reference rotation.')
    R=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],
                [2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],
                [2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
    t=item('EXTRI','POS_CmInBr','/gaittrace/camera')
    t=np.array([t['r0c0'],t['r1c0'],t['r2c0']],float)
    # Require reference IMU to actually be the identity frame and zero clock.
    iq=item('EXTRI','SO3_BiToBr','/gaittrace/imu');it=item('EXTRI','POS_BiInBr','/gaittrace/imu')
    if any(abs(float(iq[k])-v)>1e-8 for k,v in [('qx',0),('qy',0),('qz',0),('qw',1)]) or any(abs(float(v))>1e-8 for v in it.values()) or abs(item('TEMPORAL','TO_BiToBr','/gaittrace/imu'))>1e-8:
        raise ValueError('Nonidentity reference IMU requires a separate adapter.')
    td=float(item('TEMPORAL','TO_CmToBr','/gaittrace/camera'))
    tr=float(item('TEMPORAL','RS_READOUT','/gaittrace/camera'))
    if not np.isfinite(R).all() or not np.isfinite(t).all() or np.linalg.norm(t)>.25 or not math.isfinite(td) or abs(td)>.15 or not 0<=tr<=.1:
        raise ValueError('Reference geometry or timing outside research bounds.')
    return R,t,td,tr

def noise_settings(meta,report):
    defaults={'acc_n':.08,'acc_w':.00004,'gyr_n':.004,'gyr_w':.000002}
    source='VINS-Mono EuRoC example, provisional, not measured phone noise'
    if report is None:return defaults,source
    binding=report.get('binding',{})
    if any(binding.get(k)!=meta.get(k) for k in ['installationId','device','capturePipeline']):return defaults,source+'; saved noise profile does not match this phone pipeline'
    if report.get('whiteNoiseCandidateReady') is not True or report.get('biasRandomWalkReady') is not False or report.get('distanceReady') is not False:return defaults,source+'; saved noise profile is not a short-term candidate'
    for sensor,key in [('accelerometer','acc_n'),('gyroscope','gyr_n')]:
        values=np.asarray(report.get('sensors',{}).get(sensor,{}).get('stdAxes',[]),float)
        if values.shape!=(3,) or not np.isfinite(values).all() or np.min(values)<=0 or np.max(values)>(.15 if key=='acc_n' else .02):raise ValueError('Invalid measured noise candidate.')
        rate=float(report['sensors'][sensor]['sampleRateHz'])
        if not 150<=rate<=250:raise ValueError('Noise sample rate does not match the approximately 200 Hz native capture.')
        defaults[key]=float(np.max(values))
    return defaults,'Phone stationary per-sample max-axis standard deviation candidate; VINS discrete measurement-noise convention; random walk remains provisional'


def prepare_reference(source,directory,processing=None):
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
    meta,reference=inspect_capture(source);R,t,td,tr=parameters(reference)
    lens=reference['lensProfile']['lens']
    if reference['lensProfile'].get('kind')=='phone-learned-lens-seed-v1':
        from rapid_calibration_worker import refined_lens
        lens=refined_lens(reference)
    adapter={'kind':'ikalibr-vins-replay-adapter-v1','binding':reference['binding'],'lens':lens,
             'rotationTiming':{'rotationImuToCamera':R.T.tolist(),'residualTimeOffsetSeconds':td}}
    path=directory/'adapter.json';path.write_text(json.dumps(adapter))
    summary=export_capture(source,directory,path)
    # Record candidate geometry explicitly; do not relabel this as completed calibration.
    write_reference_config(directory)
    noise_path=directory.parent/'noise-report.json'
    noise,noise_source=noise_settings(meta,json.loads(noise_path.read_text()) if noise_path.is_file() else None)
    corrected=processing is not None and processing['fixedTimeRowCorrection']
    initialization=quiet_initialization(source,noise['acc_n']) if corrected else None
    config=cv2.FileStorage(str(directory/'reference.yaml'),cv2.FILE_STORAGE_WRITE)
    for key,value in [('extrinsicRotation',R),('extrinsicTranslation',t.reshape(3,1)),('td',td),('readout',tr),('estimate_extrinsic',0),('estimate_td',0),*noise.items()]:config.write(key,value)
    config.write('fixed_time_row_correction',int(corrected))
    if initialization:config.write('replay_start_ns',str(initialization['startBootNs']))
    config.release()
    assumptions={'geometrySource':'saved iKalibr camera-to-reference-IMU candidate; geometry/time held fixed',
                 'referenceSourceSha256':reference['sourceSha256'],
                 'timeConvention':'both use camera midpoint + camera-to-IMU offset; raw pixel row minus image-height/2',
                 'initialCameraToImuRotation':R.tolist(),'initialCameraPositionInImuMetres':t.tolist(),
                 'initialTimeOffsetSeconds':td,'readoutSeconds':tr,
                 'noiseSource':noise_source,'noiseParameters':noise,'noiseRandomWalkValidated':False,
                 'biasSource':'VINS estimates biases online; iKalibr biases not pre-subtracted',
                 'processing':processing,'initialization':initialization,
                 'rowTimingCorrectionApplied':bool(corrected),
                 'groundTruthUsedToSetScale':False,'distanceReady':False,'fullCalibrationReady':False}
    (directory/'reference-assumptions.json').write_text(json.dumps(assumptions,indent=2))
    return summary

def horizontal_distance(positions,times,geometry):
    """Research trajectory measure, independent of marked distance/scale labels."""
    positions=np.asarray(positions,float)[:,:2];times=np.asarray(times,float)
    if geometry not in ['straight','with-turns']:raise ValueError('Invalid route geometry.')
    if geometry=='straight':
        delta=positions[-1]-positions[0];distance=float(np.linalg.norm(delta))
        centered=positions-positions[0]
        axis=delta/distance if distance>.05 else np.linalg.svd(centered,full_matrices=False)[2][0]
        along=centered@axis;across=centered-along[:,None]*axis
        # A return/large corner cannot be passed off as a straight-route distance.
        span=float(np.ptp(along));lateral=float(np.max(np.linalg.norm(across,axis=1)))
        if span-distance>.25 or lateral>max(.25,.15*distance):return None
        return distance
    # Smooth short-period pelvis sway; preserve every original state separately.
    smoothed=np.array([np.mean(positions[np.abs(times-t)<=.175],axis=0) for t in times])
    selected=[0]
    for i in range(1,len(times)-1):
        if times[i]-times[selected[-1]]>=.35:selected.append(i)
    selected.append(len(times)-1)
    smoothed[0]=positions[0];smoothed[-1]=positions[-1]
    return float(np.linalg.norm(np.diff(smoothed[selected],axis=0),axis=1).sum())


def assess_states(rows,stderr,start,end,route_geometry='straight',standing_end=None):
    """Never stitch resets or confuse a late initialized segment with a full route."""
    ready=[r for r in rows if r['initialized']=='1']
    walk=[r for r in ready if start<=float(r['imu_time_s'])<=end]
    result={'experimentalSegmentMetres':None,'completeRouteEstimateMetres':None,'reason':'not-initialized',
            'fullRouteCovered':False,'initializedFrames':len(ready),'walkingFrames':len(walk)}
    if len(walk)<2:return result
    relevant=[r for r in rows if start-.2<=float(r['imu_time_s'])<=end]
    reboot=any(r.get('reboot')=='1' for r in relevant) or ('system reboot!' in stderr and not any('reboot' in r for r in rows))
    times=np.array([float(r['imu_time_s']) for r in walk]);positions=np.array([[float(r[k]) for k in ['px','py','pz']] for r in walk])
    speed=np.array([np.linalg.norm([float(r[k]) for k in ['vx','vy','vz']]) for r in walk])
    bias=np.array([[float(r['ba_norm']),float(r['bg_norm'])] for r in walk])
    if (reboot or rows[-1]['initialized']!='1' or not np.isfinite(positions).all() or not np.isfinite(speed).all()
        or not np.isfinite(bias).all() or np.any(np.diff(times)<=0) or np.max(np.diff(times))>.2 or np.max(speed)>3
        or max(bias[:,0])>1 or max(bias[:,1])>.2
        or any(not all(math.isfinite(float(r.get(k,v))) for k,v in [('tic_norm',0),('g_norm',9.80665),('rotation_change_deg',0)]) or float(r.get('tic_norm',0))>.25 or not 9.3<=float(r.get('g_norm',9.80665))<=10.3 or float(r.get('rotation_change_deg',0))>20 for r in walk)):
        result['reason']='tracking-integrity-failed';return result
    # Optimized poses can jump without a reboot or a matching reported velocity.
    # Apply the same existing 3 m/s plausibility bound to observed displacement,
    # including the near-trigger bracket and finishing tail. Never stitch jumps.
    stop=standing_end if standing_end is not None else end
    continuity=[r for r in ready if start-.2<=float(r['imu_time_s'])<=stop]
    ct=np.array([float(r['imu_time_s']) for r in continuity])
    cp=np.array([[float(r[k]) for k in ['px','py','pz']] for r in continuity])
    if len(continuity)>=2:
        if not np.isfinite(cp).all() or not np.isfinite(ct).all() or np.any(np.diff(ct)<=0):
            result.update(reason='tracking-integrity-failed',trackingIssue='invalid-pose-clock-or-values');return result
        displacement_rate=float(np.max(np.linalg.norm(np.diff(cp,axis=0),axis=1)/np.diff(ct)))
        result['maxPoseDisplacementRateMetresPerSecond']=displacement_rate
        if displacement_rate>3:
            result.update(reason='tracking-integrity-failed',trackingIssue='pose-discontinuity');return result
    # Z is gravity-up in VINS. Horizontal pelvis/IMU trajectory, not rear camera arc.
    segment=horizontal_distance(positions,times,route_geometry)
    if segment is None:result['reason']='route-geometry-mismatch';return result
    result.update(experimentalSegmentMetres=segment,reason='partial-route',firstTrackedWalkSeconds=float(times[0]-start),lastTrackedWalkSeconds=float(times[-1]-start))
    all_walk=[r for r in rows if start-.15<=float(r['imu_time_s'])<=end]
    before=[r for r in ready if start-.2<=float(r['imu_time_s'])<=start]
    if before and all(r['initialized']=='1' for r in all_walk) and end-times[-1]<=.2:
        # Include a near-trigger initialized sample, so the start is not silently lost.
        first=before[-1];pos=np.vstack([[float(first[k]) for k in ['px','py']],positions[:,:2]])
        full=horizontal_distance(pos,np.r_[float(first['imu_time_s']),times],route_geometry)
        if full is None:result['reason']='route-geometry-mismatch';return result
        result.update(completeRouteEstimateMetres=full,fullRouteCovered=True,reason='experimental-complete-route')
    if standing_end is not None and standing_end>end:
        tail=[r for r in ready if end<=float(r['imu_time_s'])<=standing_end]
        if len(tail)>=2:
            p=np.array([[float(r[k]) for k in ['px','py']] for r in tail])
            if not np.isfinite(p).all():
                result.update(completeRouteEstimateMetres=None,fullRouteCovered=False,reason='tracking-integrity-failed');return result
            drift=float(np.max(np.linalg.norm(p-p[0],axis=1)))
            result['standingDriftMetres']=drift
            if drift>.15:result.update(completeRouteEstimateMetres=None,fullRouteCovered=False,reason='standing-drift')
    return result

def central_10m_estimate(rows,start,end,integrity):
    """Experimental 1 + 10 + 1 m zones, derived only after common integrity admission."""
    result={'status':'unavailable','timedDistanceMetres':10,'accelerationMetres':1,'decelerationMetres':1,
            'timedZoneSeconds':None,'speedMps':None,'startOffsetSeconds':None,'endOffsetSeconds':None,
            'clinicalOutcomeVerified':False,'boundarySource':'estimated-trajectory-crossings'}
    if not integrity['fullRouteCovered'] or integrity['completeRouteEstimateMetres']<12:return result
    ready=[r for r in rows if r['initialized']=='1' and start-.2<=float(r['imu_time_s'])<=end]
    before=[r for r in ready if float(r['imu_time_s'])<=start]
    if not before:return result
    route=[before[-1]]+[r for r in ready if float(r['imu_time_s'])>start]
    times=np.array([float(r['imu_time_s']) for r in route]);p=np.array([[float(r[k]) for k in ['px','py']] for r in route])
    axis=(p[-1]-p[0])/np.linalg.norm(p[-1]-p[0]);along=(p-p[0])@axis
    def cross(mark):
        pairs=np.flatnonzero((along[:-1]<mark)&(along[1:]>=mark))
        if not len(pairs):return None
        i=pairs[0];return float(times[i]+(mark-along[i])/(along[i+1]-along[i])*(times[i+1]-times[i]))
    a,b=cross(1),cross(11)
    if a is None or b is None or b<=a:return result
    return {**result,'status':'experimental','timedZoneSeconds':b-a,'speedMps':10/(b-a),'startOffsetSeconds':a-start,'endOffsetSeconds':b-start}

def distance_report(folder,reference_metres):
    folder=Path(folder);source=folder/'input.zip';meta,reference=inspect_capture(source);replay=folder/'replay'
    with (replay/'reference-states.csv').open() as f:rows=list(csv.DictReader(f))
    with zipfile.ZipFile(source) as z:frames=[json.loads(v) for v in z.read('frames.ndjson').decode().splitlines() if v.strip()]
    start=meta['diagnostics']['walkStartedBootNs']/1e9
    capture_end=max(v['timestampNs'] for v in frames)/1e9
    boundary=meta['diagnostics'].get('walkEndedBootNs',0)/1e9
    request=json.loads((folder/'request.json').read_text())
    geometry=request.get('routeGeometry','straight')
    gait=meta.get('kind')=='gait-camera-imu-distance-capture-v1'
    if gait and (request.get('sessionId')!=meta['sessionId'] or request.get('protocol')!=meta['protocol'] or reference_metres is not None):raise ValueError('Gait result is not bound to the requested recording.')
    if not start<boundary<=capture_end:
        integrity={'experimentalSegmentMetres':None,'completeRouteEstimateMetres':None,'reason':'boundary-unavailable','fullRouteCovered':False}
    else:integrity=assess_states(rows,(replay/'reference-stderr.txt').read_text(),start,boundary,geometry,capture_end)
    estimate=integrity['completeRouteEstimateMetres']
    return {'schemaVersion':1,'kind':'gait-camera-distance-result-v1' if gait else 'phone-distance-validation-result-v1','method':'vins-mono-offline-reference-v1',
            'captureId':meta['captureId'],'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),
            'referenceCalibrationSha256':reference['sourceSha256'],'binding':{k:meta[k] for k in BINDING},
            'distanceReady':False,'independentDistanceValidation':False,'groundTruthUsedToSetScale':False,
            'referenceDistanceMetres':reference_metres,'routeGeometry':geometry,
            'distanceMethod':'horizontal-endpoint-displacement' if geometry=='straight' else 'smoothed-horizontal-trajectory-350ms',
            'walkBoundarySource':meta['diagnostics'].get('endBoundarySource','unavailable'),**integrity,
            'errorMetres':None if estimate is None or reference_metres is None else estimate-reference_metres,
            'errorPercent':None if estimate is None or reference_metres is None else 100*(estimate-reference_metres)/reference_metres,
            **({'sessionId':meta['sessionId'],'protocol':meta['protocol'],'intervalSeconds':(boundary-start) if boundary>start else None,
                'meanSpeedMps':estimate/(boundary-start) if estimate is not None and boundary>start else None,
                'testOutcome':central_10m_estimate(rows,start,boundary,integrity) if meta['protocol']=='10mwt' else None,
                'speedScope':'whole-protocol-capture-including-rests','clinicalOutcomeVerified':False} if gait else {}),
            'noise':json.loads((replay/'reference-assumptions.json').read_text()),
            'software':{'vinsCommit':VINS_COMMIT,'frontend':'diagnostic-python-lk-fb-calibrated-f-v1'},
            'limitations':['Research feasibility only; not clinical stopping or scoring',
                'Noise assumptions disclosed separately; calibrated geometry/time held fixed',
                'App motion trigger is not independently verified course crossing',
                'Partial route is not compared with full marked route','Motion-detected boundaries are not independently verified clinical crossings']}

def run_distance(folder):
    folder=Path(folder);request=json.loads((folder/'request.json').read_text());reference_metres=request['referenceDistanceMetres']
    processing=processing_spec()
    if request.get('processingRevision',processing['revision'])!=processing['revision']:
        raise ValueError('Processing method changed; resubmit the saved capture without repeating the walk.')
    profile=folder/'noise-report.json'
    digest=hashlib.sha256(profile.read_bytes()).hexdigest() if profile.is_file() else None
    if 'noiseProfileSha256' in request and request['noiseProfileSha256']!=digest:
        raise ValueError('Noise inputs changed; resubmit the saved capture without repeating the walk.')
    engine=processing['enginePath']
    replay=folder/'replay';prepare_reference(folder/'input.zip',replay,processing)
    if os.name!='nt':raise RuntimeError('Configure the pinned VINS engine for this computer first.')
    prefix=['wsl.exe','-d','Ubuntu','-u','root','--']
    commit=subprocess.check_output(prefix+['git','-C','/root/gaittrace-vio/vins-mono','rev-parse','HEAD'],text=True).strip()
    if commit!=VINS_COMMIT:raise RuntimeError('VINS checkout does not match the pinned research version.')
    subprocess.run(prefix+['git','-C','/root/gaittrace-vio/vins-mono','diff','--exit-code','HEAD','--','vins_estimator'],check=True,capture_output=True)
    binary_hash=subprocess.check_output(prefix+['sha256sum',engine],text=True).split()[0]
    if processing['fixedTimeRowCorrection']:
        probe=subprocess.run(prefix+[engine,'--capabilities'],check=True,capture_output=True,text=True,timeout=10)
        if not validate_engine_capabilities(json.loads(probe.stdout),processing):raise ValueError('Restart the updated helper; selected distance engine is incompatible.')
    from vio_compute import run_replay
    try:compute=run_replay(replay,engine)
    except subprocess.CalledProcessError as error:
        # The wrapper's documented exit 6 means no emitted feature frame, not
        # an estimator crash. Import that specific negative result only when
        # recovered files prove it; other errors remain processing failures.
        features=json.loads((replay/'features-summary.json').read_text()) if (replay/'features-summary.json').is_file() else {}
        states=list(csv.DictReader((replay/'reference-states.csv').read_text().splitlines())) if (replay/'reference-states.csv').is_file() else None
        stdout=(replay/'reference-stdout.txt').read_text() if (replay/'reference-stdout.txt').is_file() else ''
        if error.returncode!=6 or states!=[] or features.get('medianFeatures')!=0 or 'frames=0 initialized_frames=0' not in stdout:raise
        compute=json.loads((replay/'compute-summary.json').read_text());compute['dataRejection']='no-usable-feature-frames'
    result=distance_report(folder,reference_metres)
    result['software']['executableSha256']=binary_hash
    result['software']['processing']=processing
    result['noise']['profileSha256']=digest
    features=json.loads((replay/'features-summary.json').read_text())
    result['software']['frontend']=features['frontend']
    result['compute']={**compute,'features':features}
    (folder/'result.json').write_text(json.dumps(result,indent=2));return result
