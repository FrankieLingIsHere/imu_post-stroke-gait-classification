"""Calibration-bias experiments orchestrated from the existing calibration notebook.

Host ablations are diagnostic software evidence, not Android or phone accuracy.
Never use route truth to scale a saved calibration or label a model validated.
"""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import time
import numpy as np

WORKSPACE=Path(__file__).resolve().parents[2]
CPP=WORKSPACE/'android/modules/gait-camera-calibration/android/src/main/cpp'
OUT=WORKSPACE/'android/dist/emulator-lab/calibration-audit'
BINARY='/root/gaittrace-vio/openvins-calibration-audit'

def linux(path):
    p=str(Path(path).resolve()).replace('\\','/')
    return '/mnt/'+p[0].lower()+p[2:]

def build_host():
    OUT.mkdir(parents=True,exist_ok=True)
    flags=subprocess.check_output(['wsl','-d','Ubuntu','--','pkg-config','--cflags','--libs','opencv4'],text=True).split()
    command=['wsl','-d','Ubuntu','--','g++','-std=c++17','-O2','-DGAIT_OPENVINS_HOST',
             '-I'+linux(CPP),'-I/root/gaittrace-vio/open-vins/ov_msckf/src',
             '-I/root/gaittrace-vio/open-vins/ov_core/src','-I/root/gaittrace-vio/open-vins/ov_init/src',
             '-I/usr/include/eigen3',linux(CPP/'openvins_engine.cpp'),
             '-L/root/gaittrace-vio/openvins-build','-Wl,-rpath,/root/gaittrace-vio/openvins-build',
             '-lov_msckf_lib',*flags,'-lpthread','-o',BINARY]
    run=subprocess.run(command,capture_output=True,text=True)
    (OUT/'build.txt').write_text(run.stdout+run.stderr,encoding='utf-8')
    if run.returncode:raise RuntimeError('Audit compilation failed: '+str(OUT/'build.txt'))
    hashes=subprocess.check_output(['wsl','-d','Ubuntu','--','sha256sum',BINARY,
        '/root/gaittrace-vio/openvins-build/libov_msckf_lib.so'],text=True)
    report={'command':command,'sourceSha256':hashlib.sha256((CPP/'openvins_engine.cpp').read_bytes()).hexdigest(),
            'binaries':hashes,'hostOnly':True,'physicalAccuracyValidated':False}
    (OUT/'build.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report

def config_for(fixture,destination,*,group='joint',fit=None,calibrating=True,pixel_sigma=1,chi_multiplier=5):
    if not .25<=pixel_sigma<=5 or not 1<=chi_multiplier<=5:
        raise ValueError('Invalid visual consistency ablation')
    spec=json.loads((fixture/'fixture.json').read_text())
    k=fit['cameraValues'] if fit else spec['priorValues']
    e=fit['imuToCamera'] if fit else spec.get('priorExtrinsics',[0,0,0,1,0,0,0])
    td=fit['timeOffsetSeconds'] if fit else spec.get('priorTimeOffsetSeconds',0)
    text='%YAML:1.0\n---\ncalibrating: '+str(int(calibrating))+'\n'
    for name,values in [('intrinsics',k),('extrinsics',e)]:
        text+=f'{name}: !!opencv-matrix\n   rows: {len(values)}\n   cols: 1\n   dt: d\n   data: [{", ".join(map(str,values))}]\n'
    text+=f'td: {td}\nacc_noise_density: 0.0057\ngyro_noise_density: 0.000283\ndiagnostic_calibration_group: {group}\n'
    text+=f'diagnostic_pixel_sigma: {pixel_sigma}\ndiagnostic_chi_multiplier: {chi_multiplier}\n'
    destination.write_text(text,encoding='utf-8')
    return destination

def replay(fixture,output,*,group='joint',fit=None,calibrating=True,pixel_sigma=1,chi_multiplier=5):
    output.mkdir(parents=True,exist_ok=True)
    spec=json.loads((fixture/'fixture.json').read_text())
    config=config_for(fixture,output/'config.yaml',group=group,fit=fit,calibrating=calibrating,pixel_sigma=pixel_sigma,chi_multiplier=chi_multiplier)
    # CSV contains Windows paths: generate a separate path-only view, leaving source untouched.
    import csv
    with (fixture/'frames.csv').open(newline='') as src,(output/'frames.csv').open('w',newline='') as dst:
        reader=csv.reader(src);writer=csv.writer(dst);writer.writerow(next(reader))
        for row in reader:writer.writerow([row[0],linux(fixture/'frames'/Path(row[1].replace('\\','/')).name)])
    command=['wsl','-d','Ubuntu','--',BINARY,linux(config),linux(fixture/'imu.csv'),linux(output/'frames.csv'),
             str(int((100+spec['quietSeconds'])*1e9))]
    binaries=subprocess.check_output(['wsl','-d','Ubuntu','--','sha256sum',BINARY,
        '/root/gaittrace-vio/openvins-build/libov_msckf_lib.so'],text=True)
    began=time.monotonic()
    with (output/'raw.txt').open('w') as stdout,(output/'stderr.txt').open('w') as stderr:
        run=subprocess.run(command,stdout=stdout,stderr=stderr)
    rows=[]
    for line in (output/'raw.txt').read_text().splitlines():
        line=re.sub(r'\x1b\[[0-9;]*m','',line)
        if line.startswith('{'):rows.append(json.loads(line))
    (output/'states.ndjson').write_text(''.join(json.dumps(r)+'\n' for r in rows))
    report={'command':command,'binaries':binaries,'fixtureMetadataSha256':hashlib.sha256((fixture/'fixture.json').read_bytes()).hexdigest(),'exitCode':run.returncode,'wallSeconds':time.monotonic()-began,'rows':len(rows),
            'initialized':sum(r['initialized'] for r in rows),'group':group,'frozenGeometry':not calibrating,
            'hostOnly':True,'physicalAccuracyValidated':False,'fixture':str(fixture),
            'pixelSigma':pixel_sigma,'chiMultiplier':chi_multiplier,
            'lastState':rows[-1] if rows else None}
    if rows and calibrating:
        last=rows[-1];true=np.array(spec['cameraValues']);got=np.array(last['cameraValues'])
        report['truthErrors']={'focalRelative':(got[:2]/true[:2]-1).tolist(),
          'principalPixels':(got[2:4]-true[2:4]).tolist(),
          'translationMetres':float(np.linalg.norm(np.array(last['imuToCamera'][4:])-np.array(spec.get('trueExtrinsics',[0,0,0,1,0,0,0])[4:]))),
          'timeOffsetSeconds':last['timeOffsetSeconds']-spec.get('trueTimeOffsetSeconds',0),
          'rotationDegrees':float(np.degrees(2*np.arccos(np.clip(abs(np.dot(np.array(last['imuToCamera'][:4]),np.array(spec.get('trueExtrinsics',[0,0,0,1,0,0,0])[:4]))),0,1))))}
    if rows and not calibrating and spec.get('knownTranslationMetres') is not None:
        valid=[r for r in rows if r['initialized'] and r['integrity']]
        def p(r):return np.array([r['state'][k] for k in ('px','py','pz')])
        start=[r for r in valid if r['timestampSeconds']<=100+spec['quietSeconds']]
        end=[r for r in valid if r['timestampSeconds']>=100+spec['quietSeconds']+6]
        if start and end:
            displacement=float(np.linalg.norm(p(end[-1])-p(start[-1])))
            report['heldOutDisplacementMetres']=displacement
            report['heldOutErrorMetres']=displacement-spec['knownTranslationMetres']
        else:report['heldOutFailure']='No initialized quiet start or complete finish'
    if rows and not calibrating and (fixture/'truth.csv').exists():
        truth=np.genfromtxt(fixture/'truth.csv',delimiter=',',skip_header=1)
        lookup={int(r[0]):r[2:5] for r in truth}
        pairs=[(np.array([r['state'][k] for k in ('px','py','pz')]),lookup[round(r['timestampSeconds']*1e9)])
               for r in rows if r['initialized'] and r['integrity'] and round(r['timestampSeconds']*1e9) in lookup
               and r['timestampSeconds']>=100+spec['quietSeconds']+2]
        if len(pairs)>60:
            estimated=np.array([p[0] for p in pairs]);known=np.array([p[1] for p in pairs])
            a=estimated-estimated.mean(axis=0);b=known-known.mean(axis=0)
            u,_,vt=np.linalg.svd(a.T@b);rotation=u@np.diag([1,1,np.linalg.det(u@vt)])@vt
            errors=np.linalg.norm(a@rotation-b,axis=1)
            estimated_length=np.linalg.norm(np.diff(estimated,axis=0),axis=1).sum()
            known_length=np.linalg.norm(np.diff(known,axis=0),axis=1).sum()
            report['heldOutMotion']={'rigidAlignmentOnly':True,'scaleFitted':False,'matchedPoses':len(pairs),
              'ateRmseMetres':float(np.sqrt(np.mean(errors**2))),'ateMaxMetres':float(errors.max()),
              'estimatedPathMetres':float(estimated_length),'truePathMetres':float(known_length),
              'pathRelativeError':float(estimated_length/known_length-1) if known_length>0 else None}
    (output/'result.json').write_text(json.dumps(report,indent=2)+'\n')
    if run.returncode or not rows:raise RuntimeError('Audit replay failed; retained '+str(output))
    return report
