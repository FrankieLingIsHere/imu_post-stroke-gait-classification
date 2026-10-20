"""Notebook-driven synthetic pipeline checks; never independent phone validation.

Render rigid textured scenes and matching IMU, then execute the production
estimator, baseline gate, profile admission, saved result and TS contracts.
Keep every attempted result, including failed repeats. Do not tune against a
known walking length or select only successful runs.
"""
from pathlib import Path
import csv
import json
import zipfile
from on_device_vio_controls import create_control
from on_device_replay import (run_host_replay, check_setup_baseline_replay,
    check_setup_completion_replay, check_profile_admission, deliver_self_calibrated_replay, evaluate_app_result)
from calibration_ablation import write_geometry, summarize_states


def fixture(folder, **kwargs):
    metadata = create_control(folder, **kwargs)
    # The host core uses the same images via WSL; no image-content conversion.
    rows = list(csv.reader((folder/'frames.csv').open()))
    for row in rows[1:]:
        path = str(Path(row[1]).resolve()).replace('\\', '/')
        row[1] = '/mnt/'+path[0].lower()+path[2:]
    with (folder/'frames.csv').open('w', newline='') as f:
        csv.writer(f).writerows(rows)
    return metadata


def manifest(folder, *, calibration):
    m = dict(schemaVersion=1, captureId='calibration-1000' if calibration else 'analytic-walk',
        kind='phone-on-device-setup-capture-v1' if calibration else 'analytic-distance-control',
        installationId='analytic-control-not-a-phone', cameraId='analytic-front',
        width=640, height=480, imageAxes='native-sensor-unrotated-unmirrored',
        sensorOrientationDegrees=270, stabilizationRequested='off',
        capturePipeline='native-camera-imu-v3', opticalSetup='waist-bag-window',
        timestampSource='realtime', status='completed' if calibration else 'quiet-stop',
        error=None, alignmentMovementStartedBootNs=110000000000,
        physicalAndroidExecution=False, sourceRowsSynthetic=True,
        diagnostics=dict(walkStartedBootNs=110000000000, walkEndedBootNs=116000000000,
                         endBoundarySource='analytic-known-motion-boundary'))
    (folder/'manifest.json').write_text(json.dumps(m,indent=2))
    archive=folder/'capture.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_STORED) as z:
        for name in ['manifest.json','fixture.json','imu.csv','frames.csv']:
            z.write(folder/name,name)
        for image in (folder/'frames').glob('*.jpg'):
            z.write(image,'frames/'+image.name)
    return folder/'manifest.json', archive


def run_case(folder, *, repetitions=2, adaptive_completion=False, **specification):
    folder.mkdir(parents=True,exist_ok=True)
    print('Render setup:',folder.name,flush=True)
    metadata=fixture(folder/'setup', calibrating=True, excited=True,
                     quiet_seconds=10,duration_seconds=110 if adaptive_completion else 60,**specification)
    sm,sa=manifest(folder/'setup',calibration=True)
    print('Render independent walk:',folder.name,flush=True)
    fixture(folder/'walk',quiet_seconds=10,**specification)
    wm,wa=manifest(folder/'walk',calibration=False)
    results=[]
    for i in range(repetitions):
        d=folder/str(i+1);d.mkdir(exist_ok=True)
        result={'repeat':i+1,'synthetic':True,'specification':metadata}
        results.append(result)
        try:
            print('Run setup:',folder.name,i+1,flush=True)
            result['setupExecution']=run_host_replay(folder/'setup',d/'setup.ndjson',movement_ns=110000000000)
            result['setupMetrics']=summarize_states(d/'setup.states.ndjson')
            result['baseline']=check_setup_baseline_replay(folder/'setup/imu.csv',d/'setup.states.ndjson',110000000000,d/'baseline')
            states=d/'setup.states.ndjson'
            if adaptive_completion:
                result['completion']=check_setup_completion_replay(states,160,d/'completion')
                completion=result['completion']['firstEligibleCompletionSeconds']
                if completion is None:
                    raise ValueError('No stable completion before the unchanged safety timeout')
                rows=[json.loads(line) for line in states.read_text().splitlines()]
                states=d/'completed.states.ndjson'
                states.write_text(''.join(json.dumps(row)+'\n' for row in rows if row['timestampSeconds']<=completion))
            result['admission']=check_profile_admission(sm,states,sa,d/'admission',previous_profile=False)
            result['admission'].pop('stdout',None)
            if result['baseline']['oldCueWouldBeBlocked'] or not result['admission']['accepted']:
                raise ValueError('Measured baseline or production profile admission failed')
            profile=d/'admission/camera-calibration/on-device-profile.json'
            fit=json.loads(profile.read_text())['fit']
            write_geometry(d/'walk.yaml',dict(intrinsics=fit['cameraValues'],extrinsics=fit['imuToCamera'],
                           td=fit['timeOffsetSeconds'],acc_noise_density=.0057,gyro_noise_density=.000283),calibrating=False)
            result['walkExecution']=run_host_replay(folder/'walk',d/'walk.ndjson',config=d/'walk.yaml',
                                                   movement_ns=110000000000,end_ns=116000000000)
            result['delivery']=deliver_self_calibrated_replay(profile,wm,d/'walk.states.ndjson',wa,d/'delivery')
            app=evaluate_app_result(d/'delivery/delivered-result.json',d/'delivery/app-result.json')
            result['appResult']=app
            measured=app['completeRouteEstimateMetres']
            result['errorComparedAfterwardsMetres']=None if measured is None else measured-3
            # Criterion fixed before running; target length never enters config.
            result['passed']=app['reason']=='experimental-complete-route' and measured is not None and abs(measured-3)<=.30
            if not result['passed']:
                result['failure']='Actual saved-result quality or preset 0.30 m criterion failed'
        except Exception as e:
            result.update(passed=False,failure=str(e))
        (folder/'results.json').write_text(json.dumps(results,indent=2)+'\n')
        print('Result:',folder.name,i+1,result['passed'],result.get('failure',''),flush=True)
    return results


def audit_saved_case(folder, output):
    """Recheck every saved attempt with current production completion/admission.

    This is explicitly an artifact replay, not another solver execution or an
    independent trial. Completion is chosen by the live gate, never distance.
    """
    results=json.loads((folder/'results.json').read_text())
    audits=[]
    for r in results:
        d=folder/str(r['repeat']);out=output/str(r['repeat'])
        completion=check_setup_completion_replay(d/'setup.states.ndjson',160,out/'completion')
        end=completion['firstEligibleCompletionSeconds']
        if end is None:
            audits.append({'repeat':r['repeat'],'passed':False,'failure':'No completion gate acceptance'})
            continue
        rows=[json.loads(line) for line in (d/'setup.states.ndjson').read_text().splitlines()]
        states=out/'completed.states.ndjson'
        states.write_text(''.join(json.dumps(row)+'\n' for row in rows if row['timestampSeconds']<=end))
        admission=check_profile_admission(folder/'setup/manifest.json',states,folder/'setup/capture.zip',out/'admission',previous_profile=False)
        audits.append({'repeat':r['repeat'],'completion':completion,'currentAdmissionPassed':admission['accepted'],
                       'originalWholePipelinePassed':r['passed'],'passed':admission['accepted'] and r['passed'],
                       'distanceMetres':r.get('appResult',{}).get('completeRouteEstimateMetres'),
                       'freshSolverExecution':False,'physicalAndroidExecution':False})
    return audits
