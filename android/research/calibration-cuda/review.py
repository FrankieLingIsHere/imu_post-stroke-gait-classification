"""Review saved fresh pipeline outputs; does not execute or admit calibration."""
import hashlib
import json
from pathlib import Path
import re
import zipfile

import numpy as np
from distance_validation import parameters


def digest(path):
    with Path(path).open('rb') as stream:
        value = hashlib.sha256()
        for chunk in iter(lambda:stream.read(1024*1024),b''):
            value.update(chunk)
    return value.hexdigest()


def review(folder):
    folder = Path(folder)
    runs, refs = [], {}
    for mode in ('cpu','cuda'):
        path = folder/mode
        timing = json.loads((path/'pipeline.json').read_text())
        benchmark = json.loads((path/'benchmark.json').read_text())
        result = json.loads((path/'result.json').read_text())
        sfm = json.loads((path/'sfm-complete.json').read_text())
        prep = json.loads((path/'pipeline-prepare.json').read_text())
        assert timing['completed'] and timing['exportExitCode']==0
        assert all(s['exitCode']==0 for s in timing['stages'].values())
        assert benchmark['converged'] and benchmark['freshPipelineInputs']
        assert prep['freshRawCapture'] and prep['reusedSfm'] is False
        with zipfile.ZipFile(path/'input.zip') as archive:
            meta = json.loads(archive.read('manifest.json'))
        assert result['sourceSha256']==digest(path/'input.zip')==benchmark['sourceCaptureSha256']
        assert all(result['binding'][key]==meta[key] for key in result['binding'])
        assert result['lensProfile']==meta['lensProfile']
        assert all(result[key] is False for key in ('cameraImuCandidateReady','fullCalibrationReady',
                                                  'distanceReady','independentDistanceValidation'))
        assert sfm['backend']==mode and sfm['registeredImages']>2
        R,t,td,tr = parameters(result) # Existing geometry/frame/timing bounds.
        assert np.allclose(R.T@R,np.eye(3),atol=1e-7) and abs(np.linalg.det(R)-1)<1e-7
        residual = json.loads((path/'output/residuals/reproj_error/gaittrace/camera/residuals.json').read_text())['reproj_errors']
        values=np.array([[v['r0c0'],v['r1c0']] for v in residual],float)
        assert len(values)>100 and np.isfinite(values).all()
        norms=np.linalg.norm(values,axis=1)
        log = (path/'reference-final.log').read_text(errors='replace')
        reports = re.findall(r'Ceres Solver Report:.*',log)
        assert len(reports)>=7 and all('CONVERGENCE' in r for r in reports)
        samples=benchmark['gpuSamples']
        utilization=[int(s['gpu'].split(',')[1].strip()) for s in samples if 'gpu' in s]
        engine_pids=set(re.findall(r'\[I\]-\[(\d+)\]',log))
        measured_pids={line.split(',')[0].strip() for s in samples
                       for line in s.get('processes','').splitlines() if line}
        gpu_confirmed=bool(utilization and max(utilization)>0 and engine_pids&measured_pids)
        if mode=='cuda': assert gpu_confirmed
        refs[mode]=(R,t,td,tr)
        runs.append({'mode':mode, 'stages':timing['stages'],
            'computeWallSeconds':timing['computeWallSeconds'],
            'totalWallSecondsIncludingExport':timing['totalWallSecondsIncludingExport'],
            'exportWallSeconds':timing['exportWallSeconds'], 'preparation':prep,
            'registeredImages':sfm['registeredImages'], 'measuredKeyframes':sfm['measuredKeyframes'],
            'reprojectionResidualCount':len(values), 'reprojectionRmsPixels':float(np.sqrt(np.mean(norms**2))),
            'reprojectionMedianPixels':float(np.median(norms)), 'reprojectionP90Pixels':float(np.quantile(norms,.9)),
            'reprojectionP99Pixels':float(np.quantile(norms,.99)),
            'translationMetres':t.tolist(), 'translationNormMetres':float(np.linalg.norm(t)),
            'cameraTimeOffsetMs':td*1000, 'readoutMs':tr*1000,
            'finalWeightedCost':float(re.search(r'Final cost: ([0-9.e+\-]+)',reports[-1])[1]),
            'convergedReports':len(reports), 'emptyInitializationReports':sum('Iterations: -2' in r for r in reports),
            'finalSolverGpuConfirmed':gpu_confirmed,
            'peakFinalSolverGpuUtilizationPercent':max(utilization) if utilization else None,
            'sourceSha256':result['sourceSha256'], 'captureBagSha256':benchmark['captureBagSha256'],
            'engineSha256':result['software']['executableSha256'], 'sfm':sfm,
            'cameraJsonSha256':digest(path/'camera.json'), 'imuJsonSha256':digest(path/'imu.json'),
            'freshSfmPointsSha256':benchmark['fixedSfmPointsSha256'],
            'cameraBindingAndLensPreserved':True, 'researchGeometryBoundsPassed':True})
    for key in ('sourceSha256','engineSha256','cameraJsonSha256','imuJsonSha256'):
        assert runs[0][key]==runs[1][key]
    a,b=refs['cpu'],refs['cuda']
    angle=np.arccos(np.clip((np.trace(a[0].T@b[0])-1)/2,-1,1))
    return {'kind':'experimental-calibration-full-pipeline-review-v1',
        'scope':'one fresh full pipeline per backend; same retained development capture; no independent physical test',
        'runs':runs, 'computeReductionPercent':100*(1-runs[1]['computeWallSeconds']/runs[0]['computeWallSeconds']),
        'includingExportReductionPercent':100*(1-runs[1]['totalWallSecondsIncludingExport']/runs[0]['totalWallSecondsIncludingExport']),
        'parameterDifferences':{'translationMm':float(np.linalg.norm(a[1]-b[1])*1000),
            'rotationDegrees':float(np.degrees(angle)), 'timeOffsetMs':abs(a[2]-b[2])*1000,
            'readoutMs':abs(a[3]-b[3])*1000},
        'processingAndResearchBoundsPassed':True, 'clinicalAccuracyValidated':False,
        'distanceReady':False, 'savedPhoneProfileChanged':False,
        'limitations':['n=1 full run per backend on one development capture',
            'CPU/GPU SfM features and reconstruction can differ; not a fixed-input solver equivalence test',
            'reported reprojection errors are in-sample fitted residuals, not held-out accuracy',
            'no independently measured extrinsics/noise model/walking-distance accuracy']}
