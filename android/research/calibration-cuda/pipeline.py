"""Fresh full-pipeline validation worker; never replaces a phone profile.

Notebook orchestration owns fresh volumes and stage/container timing. Reuses the
production capture conversion and COLMAP bridge, then the experimental solver.
"""
import argparse
import json
import math
import os
from pathlib import Path
import re
import runpy
import signal
import subprocess
import sys
import time

import yaml

ROOT = Path('/data')
ENGINE = Path('/opt/ikalibr-cuda-devel/lib/ikalibr/ikalibr_prog')


def prepare():
    if any(ROOT.iterdir()):
        raise ValueError('Fresh pipeline requires an empty volume.')
    environment = subprocess.check_output(['bash', '-c', 'source /opt/ros/noetic/setup.bash && env -0'])
    os.environ.update(dict(row.decode().split('=', 1) for row in environment.split(b'\0') if row))
    # Updating PYTHONPATH after interpreter startup does not update sys.path.
    # The production bridge starts Python after sourcing ROS; match that here.
    sys.path[:0] = [p for p in os.environ.get('PYTHONPATH', '').split(':') if p]
    from workspace import import_capture
    began = time.perf_counter()
    import_capture('/transfer', ROOT)
    copied = time.perf_counter()
    runpy.run_path('/bridge/prepare.py', run_name='__main__')
    converted = time.perf_counter()
    config = yaml.safe_load((ROOT/'config.yaml').read_text())
    config['Configor']['Preference']['UseCudaInSolving'] = os.environ['BENCHMARK_MODE'] == 'cuda'
    (ROOT/'config.yaml').write_text(yaml.safe_dump(config, sort_keys=False))
    master = subprocess.Popen(['roscore'], stdout=(ROOT/'roscore-prepare.log').open('w'),
                              stderr=subprocess.STDOUT, start_new_session=True)
    worker = None
    try:
        for _ in range(30):
            ready = subprocess.run(['rosparam','set','/ikalibr_prog/config_path','/data/config.yaml'],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if ready.returncode == 0: break
            time.sleep(1)
        else: raise RuntimeError('ROS startup failed.')
        log = ROOT/'reference-initial.log'
        with log.open('w') as stream:
            worker = subprocess.Popen(['xvfb-run','-a','-s','-screen 0 1280x720x24 +extension GLX',
                                       str(ENGINE),'__name:=ikalibr_prog'], stdout=stream,
                                      stderr=subprocess.STDOUT, start_new_session=True)
            started = time.perf_counter()
            while True:
                if 'images have been output to' in log.read_text(errors='replace'): break
                if worker.poll() is not None: raise RuntimeError('Initialization stopped without exported images.')
                if time.perf_counter()-started > 900: raise TimeoutError('Initialization exceeded 900 seconds.')
                time.sleep(.5)
    finally:
        for child in (worker, master):
            if child is not None and child.poll() is None:
                os.killpg(child.pid, signal.SIGTERM)
                try: child.wait(timeout=20)
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid, signal.SIGKILL); child.wait(timeout=10)
    bases = list((ROOT/'output').rglob('sfm_ws'))
    if len(bases) != 1: raise ValueError('Missing or ambiguous upstream SfM workspace.')
    sfm = bases[0]
    images = sfm.parent/'images' if (sfm.parent/'images').is_dir() else sfm.parent
    if not (sfm/'matches.txt').is_file(): raise ValueError('No upstream matches.')
    info = json.loads((sfm.parent/'info.json').read_text())['info']['images']
    ordered = [r['value'] for r in sorted(info, key=lambda r:r['key'])]
    if any(not re.fullmatch(r'[0-9]+\.jpg', name) for name in ordered): raise ValueError('Invalid image list.')
    selected = ordered[::max(1, math.ceil(len(ordered)/200))]
    if len(selected)<100: raise ValueError('Insufficient measured keyframes.')
    K = json.loads((ROOT/'provenance.json').read_text())['metadata']['lensProfile']['lens']['cameraMatrix']
    (ROOT/'sfm-images.txt').write_text('\n'.join(selected)+'\n')
    (ROOT/'sfm-stage.json').write_text(json.dumps({'workspace':str(sfm.relative_to(ROOT)),
        'images':str(images.relative_to(ROOT)), 'cameraParameters':','.join(str(v) for v in
        [K[0][0],K[1][1],K[0][2],K[1][2]]), 'measuredKeyframes':len(selected)}, indent=2))
    (ROOT/'pipeline-prepare.json').write_text(json.dumps({'importSeconds':copied-began,
        'conversionSeconds':converted-copied, 'initializationAndPlanSeconds':time.perf_counter()-converted,
        'freshRawCapture':True, 'reusedSfm':False, 'distanceReady':False}, indent=2))


def finish():
    from benchmark import run, digest
    run(prepared=True)
    provenance = json.loads((ROOT/'provenance.json').read_text())
    provenance['solverBackend'] = os.environ['BENCHMARK_MODE']
    meta = provenance['metadata']
    result = {'schemaVersion':1, 'kind':'phone-reference-camera-imu-calibration-v1',
        'method':'ikalibr-tro-2025', 'status':'reference-solved-review-required',
        'sourceSha256':provenance['sourceSha256'], 'binding':{k:meta[k] for k in
        ['installationId','captureId','cameraId','width','height','imageAxes','sensorOrientationDegrees',
         'stabilizationRequested','capturePipeline','opticalSetup']}, 'lensProfile':meta['lensProfile'],
        'software':{'image':os.environ['BENCHMARK_IMAGE_ID'], 'executableSha256':digest(ENGINE),
                    'experimentalBackend':os.environ['BENCHMARK_MODE'],
                    'baseImage':'ulong2/ie_kalibr_image@sha256:2de8ac994a86951b6255e4b8485eae9982ea3ed03bac33dd9d0ee254e383587c'},
        'upstreamParameters':json.loads((ROOT/'output/ikalibr_param.json').read_text()),
        'cameraImuCandidateReady':False, 'fullCalibrationReady':False, 'distanceReady':False,
        'independentDistanceValidation':False,
        'reviewRequired':['parameter-conventions-and-physical-bounds','repeatability-and-residuals',
                          'complete-noise-model','independent-distance-validation'],
        'provenance':{**{k:v for k,v in provenance.items() if k!='metadata'},
                      'sfm':json.loads((ROOT/'sfm-complete.json').read_text())}}
    (ROOT/'result.json').write_text(json.dumps(result, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=['prepare','finish','export'])
    stage = parser.parse_args().stage
    if stage == 'prepare': prepare()
    elif stage == 'finish': finish()
    else:
        from workspace import export_outputs
        export_outputs(ROOT, '/transfer')
