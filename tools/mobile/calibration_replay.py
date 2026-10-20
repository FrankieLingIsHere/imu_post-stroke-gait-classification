"""Reusable emulator numerical checks; orchestrate from the calibration notebook.

Separate test package, actual production JNI, explicitly synthetic inputs.
Nothing is injected into GaitTrace and no physical phone is selected.
"""
import hashlib
import json
import subprocess
import sys
import time
import re
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
ADB = WORKSPACE / 'android/dist/native-distance-tools/android-sdk/platform-tools/adb.exe'
OUT = WORKSPACE / 'android/dist/emulator-lab/calibration-replay'


def adb(*args, **kwargs):
    return subprocess.run([str(ADB), '-s', 'emulator-5560', *args], check=True,
                          capture_output=True, **kwargs)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def discard_remote_fixture(remote):
    # Linux emulator input copies only. Originals/hashes/results stay on Windows.
    if not re.fullmatch(r'/data/local/tmp/gait-setup-[A-Za-z0-9-]+',remote):
        raise ValueError('Refusing cleanup outside the numerical lab input directory')
    return adb('shell','rm','-rf',remote).stdout.decode('utf-8')


def run_case(name, fixture, *, expect=True, output_root=None):
    output_root=output_root or OUT
    destination=output_root/name
    destination.mkdir(parents=True, exist_ok=True)
    remote='/data/local/tmp/gait-setup-'+output_root.name+'-'+name
    capacity=adb('shell','df','-k','/data').stdout.decode('utf-8')
    (destination/'storage-before.txt').write_text(capacity)
    available=int(capacity.strip().splitlines()[-1].split()[3])*1024
    required=sum(p.stat().st_size for p in fixture.rglob('*') if p.is_file())+128*1024*1024
    if available<required:raise RuntimeError('Emulator lab storage is insufficient; retained '+str(destination/'storage-before.txt'))
    # Each named fixture has its own directory; no destructive recursive cleanup.
    print('Transfer numerical fixture:',name,flush=True)
    transfer=adb('push',str(fixture),remote)
    (destination/'transfer.txt').write_bytes(transfer.stdout+transfer.stderr)
    print('Run unchanged Android JNI:',name,flush=True)
    started=time.monotonic()
    command=['shell','am','instrument','-w','-e','fixture',remote,'-e','expect',
             'accept' if expect else 'reject',
             'com.gaittrace.calibrationlab/expo.modules.gaitcalibration.CalibrationReplayInstrumentation']
    run=adb(*command,timeout=240)
    (destination/'instrumentation.txt').write_bytes(run.stdout+run.stderr)
    # am instrument's shell exit code is insufficient: read the actual assertion.
    lines=run.stdout.decode('utf-8').splitlines()
    result_lines=[line[len('INSTRUMENTATION_RESULT: result='):] for line in lines
                  if line.startswith('INSTRUMENTATION_RESULT: result=')]
    if len(result_lines)!=1:
        raise RuntimeError('No current instrumentation result; retained log: '+str(destination/'instrumentation.txt'))
    report=json.loads(result_lines[0])
    report['caseName']=name
    if b'INSTRUMENTATION_CODE: -1' not in run.stdout or not report.get('passed'):
        report['passed']=False
    report['fixtureSpecification']=json.loads((fixture/'fixture.json').read_text(encoding='utf-8'))
    report['procedure']=[['adb','-s','emulator-5560',*command]]
    report['inputSha256']={p.relative_to(fixture).as_posix():digest(p)
                          for p in sorted(fixture.rglob('*')) if p.is_file() and p.name!='capture.zip'}
    directory=report['captureDirectory']
    states=adb('shell','run-as','com.gaittrace.calibrationlab','cat',directory+'/on-device-states.ndjson').stdout
    (destination/'states.ndjson').write_bytes(states)
    report['statesSha256']=hashlib.sha256(states).hexdigest()
    report['testApkSha256']=digest(OUT/'Calibration-emulator-only.apk')
    report['sourceApkSha256']=digest(WORKSPACE/'android/dist/emulator-lab/GaitTrace-emulator-x86_64.apk')
    report['totalWallSeconds']=time.monotonic()-started
    (destination/'result.json').write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'))
    # Only after the actual output and input hashes have been retained locally.
    discard_remote_fixture(remote)
    print(name,'PASS' if report['passed'] else 'FAIL','accepted=',report['accepted'],
          'completion=',report['completionSeconds'],'reason=',report['rejection'],flush=True)
    return report


def run_suite():
    """Fixed cases; retains every failure and never tunes against route length."""
    adb('install','-r',str(OUT/'Calibration-emulator-only.apk'))
    execution=OUT/'runs'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    execution.mkdir(parents=True,exist_ok=True)
    fixtures=OUT/'fixtures'
    matrix=[
      ('nominal-a',WORKSPACE/'android/dist/on-device-checks/simulation-matrix/nominal/setup',{},True),
      ('nominal-b',WORKSPACE/'android/dist/on-device-checks/simulation-matrix/nominal/setup',{},True),
      ('noise-15hz',WORKSPACE/'android/dist/on-device-checks/simulation-matrix/noise-15hz/setup',{},True),
      # The visual-rejection correction now converges on this 60 s control.
      # The old pending expectation failed in runs/20261011T113314Z and remains
      # retained; this updated expectation is separately replayed, not relabelled.
      # Withheld axes and blank images remain the true negative controls below.
      ('different-camera-short',WORKSPACE/'android/dist/on-device-checks/simulation-matrix/different-camera/setup',{},True),
      ('geometry-long-recovery',None,dict(quiet_seconds=10,duration_seconds=180,frame_hz=30,seed=1211,
          camera_values=[460,450,330,230,0,0,0,0],prior_values=[440,440,320,240,0,0,0,0]),True),
      ('distortion-occlusion',WORKSPACE/'android/dist/on-device-checks/simulation-matrix/distortion-occlusion/setup',{},True),
      ('slow-view-recovery',None,dict(quiet_seconds=80,duration_seconds=145,blank_until_seconds=15),True),
      ('missing-axis-recovery',None,dict(quiet_seconds=10,duration_seconds=180,single_axis_seconds=90),True),
      ('missing-axis-withheld',None,dict(quiet_seconds=10,duration_seconds=135,single_axis_seconds=1000),False),
      ('blank-withheld',None,dict(quiet_seconds=10,duration_seconds=60,blank=True),False),
    ]
    results=[]
    for name,fixture,options,expect in matrix:
        if fixture is None:
            fixture=fixtures/name
            if not (fixture/'fixture.json').exists():
                print('Render physically consistent control:',name,flush=True)
                # Reuse the existing OpenCV environment; the notebook kernel
                # need not install duplicate native image dependencies.
                python=Path.home()/'.venv/Scripts/python.exe'
                code='import json,sys; from pathlib import Path; from on_device_vio_controls import create_control; create_control(Path(sys.argv[1]),calibrating=True,excited=True,**json.loads(sys.argv[2]))'
                subprocess.run([str(python),'-c',code,str(fixture),json.dumps(options)],
                               cwd=WORKSPACE/'android/research',check=True)
        try:
            results.append(run_case(name,fixture,expect=expect,output_root=execution))
        except Exception as error:
            failed={'kind':'android-jni-setup-proof-suite','serial':'emulator-5560','passed':False,
                    'suiteCompleted':False,'expectedCaseNames':[case[0] for case in matrix],
                    'cases':results,'failedCase':name,'failure':str(error),'evidenceDirectory':str(execution)}
            for destination in [OUT/'verification.json',execution/'verification.json']:
                destination.write_text(json.dumps(failed,indent=2)+'\n')
            raise
        summary={'kind':'android-jni-setup-proof-suite','serial':'emulator-5560',
                 'passed':len(results)==len(matrix) and all(r['passed'] for r in results),
                 'suiteCompleted':len(results)==len(matrix),'expectedCaseNames':[case[0] for case in matrix],
                 'cases':results,'evidenceDirectory':str(execution),
                 'realPhoneValidation':False,'fullAppUiReplay':False,
                 'limitations':['Analytic rigid textured scenes and global-shutter inputs',
                   'Identity true camera-IMU alignment; no arbitrary-phone proof',
                   'No physical waist-bag, audible TTS or novice usability validation']}
        (OUT/'verification.json').write_bytes((json.dumps(summary,indent=2)+'\n').encode('utf-8'))
        (execution/'verification.json').write_bytes((json.dumps(summary,indent=2)+'\n').encode('utf-8'))
    return summary
