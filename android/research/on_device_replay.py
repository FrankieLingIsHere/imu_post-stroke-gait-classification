"""Load and audit real local replay artifacts from the calibration notebook.

No route-label scale fitting or generated sensor readings. Host execution is
not physical Android execution. Inputs and outputs remain in ignored dist/.
"""
import json
import os
import re
import subprocess
import hashlib
import time
import shutil
from datetime import datetime, timezone
from pathlib import Path


APP = Path(__file__).resolve().parents[1]
NATIVE = APP / 'modules/gait-camera-calibration/android/src/main/java/expo/modules/gaitcalibration'


def run_host_replay(folder: Path, output: Path, *, movement_ns=None, end_ns=None, config=None):
    """Fresh execution of the rebuilt production core, with explicit clock handoff."""
    def linux(path):
        path = str(Path(path).resolve()).replace('\\', '/')
        return '/mnt/' + path[0].lower() + path[2:]
    args = ['wsl.exe', '-d', 'Ubuntu', '--', '/root/gaittrace-vio/openvins-phone-full-replay',
            linux(config or folder / 'config.yaml'), linux(folder / 'imu.csv'), linux(folder / 'frames.csv')]
    if movement_ns is not None:
        args.append(str(movement_ns))
    if end_ns is not None:
        if movement_ns is None or end_ns <= movement_ns:
            raise ValueError('An explicit end must follow an explicit real movement boundary')
        args.append(str(end_ns))
    output.parent.mkdir(parents=True, exist_ok=True)
    began = time.monotonic()
    started = datetime.now(timezone.utc).isoformat()
    with output.open('w') as out, output.with_suffix('.stderr.txt').open('w') as err:
        run = subprocess.run(args, stdout=out, stderr=err)
    if run.returncode:
        raise RuntimeError(f'Host replay failed with code {run.returncode}: {output}')
    rows = states_from_debug(output, output.with_suffix('.states.ndjson'))
    return {'states': len(rows), 'initialized': sum(r['initialized'] for r in rows),
            'numericalReady': sum(r['numericalCalibrationReady'] for r in rows),
            'outputSha256': hashlib.sha256(output.read_bytes()).hexdigest(),
            'startedAtUtc': started, 'movementStartedBootNs': movement_ns, 'movementEndedBootNs': end_ns,
            'wallSeconds': time.monotonic() - began, 'freshHostExecution': True,
            'physicalAndroidExecution': False,
            'sourceRowsSynthetic': (folder/'fixture.json').exists() or 'on-device-checks' in str(folder)}


def states_from_debug(source: Path, destination: Path):
    rows = []
    for line in re.sub(r'\x1b\[[0-9;]*m', '', source.read_text()).splitlines():
        if line.startswith('{'):
            row = json.loads(line)
            if 'state' in row:
                rows.append(row)
    if not rows or any(b['state']['imu_time_s'] <= a['state']['imu_time_s'] for a, b in zip(rows, rows[1:])):
        raise ValueError('Missing or nonmonotonic replay states')
    destination.write_text(''.join(json.dumps(r, allow_nan=False) + '\n' for r in rows))
    return rows


def deliver_reference_replay(reference: Path, manifest: Path, states: Path, archive: Path, output: Path):
    """Execute the actual Java profile admission and saved-state result delivery."""
    output.mkdir(parents=True, exist_ok=True)
    java = APP / 'dist/native-distance-tools/jdk-17.0.20.1+1/bin'
    jar = APP / 'dist/phone-vio-native/json.jar'
    classes = output / 'classes'
    classes.mkdir(exist_ok=True)
    sources = [NATIVE / (n + '.java') for n in ['OnDeviceProfile', 'ReferenceTrackingProfile', 'OnDeviceResults']]
    sources += [APP / 'research/native-tests/ReferencePipelineReplayCheck.java']
    compile_result = subprocess.run([str(java / 'javac.exe'), '-cp', str(jar), '-d', str(classes), *map(str, sources)], capture_output=True, text=True)
    if compile_result.returncode:
        raise RuntimeError(compile_result.stdout + compile_result.stderr)
    run = subprocess.run([str(java / 'java.exe'), '-cp', str(classes) + os.pathsep + str(jar), 'expo.modules.gaitcalibration.ReferencePipelineReplayCheck', *map(str, [reference, manifest, states, output, archive])], capture_output=True, text=True)
    if run.returncode:
        raise RuntimeError(run.stdout + run.stderr)
    return {'stdout': run.stdout.strip(), 'output': str(output / 'delivered-result.json'), 'physicalAndroidExecution': False}


def evaluate_app_result(delivered: Path, output: Path):
    """Run production TypeScript result and persistence contracts on delivered states."""
    code = "const fs=require('node:fs'),a=require('./research/replay_app_contracts.cjs');const r=a.evaluate(JSON.parse(fs.readFileSync(process.argv[1],'utf8')));fs.writeFileSync(process.argv[2],JSON.stringify(r,null,2));console.log(JSON.stringify(r));"
    run = subprocess.run(['node', '-e', code, str(delivered), str(output)], cwd=APP, capture_output=True, text=True)
    if run.returncode:
        raise RuntimeError(run.stdout + run.stderr)
    return json.loads(run.stdout)


def deliver_self_calibrated_replay(profile: Path, manifest: Path, states: Path, archive: Path, output: Path):
    """Replay production delivery with an admitted setup from a different capture.

    The Java adapter explicitly labels host execution and the retained v2 input.
    This is not a new phone acquisition or independent accuracy validation.
    """
    output.mkdir(parents=True, exist_ok=True)
    java = APP / 'dist/native-distance-tools/jdk-17.0.20.1+1/bin'
    jar = APP / 'dist/phone-vio-native/json.jar'
    classes = output / 'classes'
    classes.mkdir(exist_ok=True)
    sources = [NATIVE / (n + '.java') for n in ['OnDeviceProfile', 'ReferenceTrackingProfile', 'OnDeviceResults']]
    sources.append(APP / 'research/native-tests/SelfCalibrationPipelineReplayCheck.java')
    for args in [[str(java / 'javac.exe'), '-cp', str(jar), '-d', str(classes), *map(str, sources)],
                 [str(java / 'java.exe'), '-cp', str(classes) + os.pathsep + str(jar),
                  'expo.modules.gaitcalibration.SelfCalibrationPipelineReplayCheck',
                  *map(str, [profile, manifest, states, output, archive])]]:
        run = subprocess.run(args, capture_output=True, text=True)
        if run.returncode:
            raise RuntimeError(run.stdout + run.stderr)
    return {'stdout': run.stdout.strip(), 'output': str(output / 'delivered-result.json'),
            'physicalAndroidExecution': False}


def check_setup_baseline_replay(imu: Path, states: Path, old_cue_ns: int, output: Path):
    """Run the production measured-baseline gate on a retained transport trace."""
    output.mkdir(parents=True, exist_ok=True)
    java = APP / 'dist/native-distance-tools/jdk-17.0.20.1+1/bin'
    jar = APP / 'dist/phone-vio-native/json.jar'
    sources = [NATIVE / 'SetupBaselineGate.java', APP / 'research/native-tests/SetupBaselineReplayCheck.java']
    classes = output / 'classes'
    classes.mkdir(exist_ok=True)
    subprocess.run([str(java / 'javac.exe'), '-cp', str(jar), '-d', str(classes),
                    *map(str, sources)], check=True, capture_output=True)
    run = subprocess.run([str(java / 'java.exe'), '-cp', str(classes) + os.pathsep + str(jar),
                          'expo.modules.gaitcalibration.SetupBaselineReplayCheck',
                          str(imu), str(states), str(old_cue_ns)], check=True, capture_output=True, text=True)
    result = json.loads(run.stdout)
    (output / 'baseline-result.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


def check_setup_completion_replay(states: Path, minimum_seconds: float, output: Path):
    """Actual live five-second convergence gate; no distance label involved."""
    output.mkdir(parents=True,exist_ok=True)
    java=APP/'dist/native-distance-tools/jdk-17.0.20.1+1/bin'
    jar=APP/'dist/phone-vio-native/json.jar';classes=output/'classes';classes.mkdir(exist_ok=True)
    sources=[NATIVE/(name+'.java') for name in ['OnDeviceProfile','ReferenceTrackingProfile','SetupConvergenceGate']]
    sources.append(APP/'research/native-tests/SetupConvergenceReplayCheck.java')
    subprocess.run([str(java/'javac.exe'),'-cp',str(jar),'-d',str(classes),*map(str,sources)],check=True,capture_output=True)
    r=subprocess.run([str(java/'java.exe'),'-cp',str(classes)+os.pathsep+str(jar),'expo.modules.gaitcalibration.SetupConvergenceReplayCheck',str(states),str(minimum_seconds)],check=True,capture_output=True,text=True)
    result=json.loads(r.stdout);(output/'completion.json').write_text(json.dumps(result,indent=2)+'\n');return result


def check_profile_admission(manifest: Path, states: Path, archive: Path, output: Path, *, previous_profile=True):
    """Actual admission decision, preserving any earlier saved setup on rejection."""
    m = json.loads(manifest.read_text())
    capture = m.get('captureId', archive.stem)
    folder = output / 'camera-calibration' / capture
    folder.mkdir(parents=True, exist_ok=True)
    for source, destination in [(manifest, folder/'manifest.json'), (states, folder/'on-device-states.ndjson'), (archive, folder.with_suffix('.zip'))]:
        shutil.copyfile(source, destination)
    previous = folder.parent/'on-device-profile.json'
    if previous_profile:
        previous.write_text('{"softwareControlPreviousProfile":"must-not-be-overwritten-on-rejection"}')
    before = previous.read_bytes() if previous.exists() else None
    java = APP/'dist/native-distance-tools/jdk-17.0.20.1+1/bin'
    jar = APP/'dist/phone-vio-native/json.jar'
    classes = output/'classes';classes.mkdir(exist_ok=True)
    sources = [NATIVE/(n+'.java') for n in ['OnDeviceProfile', 'ReferenceTrackingProfile']]
    sources += [APP/'research/native-tests/OnDeviceProfileReplayCheck.java']
    subprocess.run([str(java/'javac.exe'), '-cp', str(jar), '-d', str(classes), *map(str, sources)], check=True, capture_output=True)
    run = subprocess.run([str(java/'java.exe'), '-cp', str(classes)+os.pathsep+str(jar), 'expo.modules.gaitcalibration.OnDeviceProfileReplayCheck', str(output), capture], capture_output=True, text=True)
    result = {'accepted': run.returncode == 0, 'previousPreservedOnRejection': run.returncode == 0 or (previous.read_bytes() if previous.exists() else None) == before,
              'stdout': run.stdout.strip(), 'stderr': run.stderr.strip(), 'physicalAndroidExecution': False}
    (output/'admission-result.json').write_text(json.dumps(result, indent=2))
    return result
