"""One-time learned scene enrollment; original capture and prior profile survive.

GeoCalib supplies an experimental lens seed. The unchanged iKalibr reference
engine must still solve camera/IMU geometry and timing before phone use.
"""
import hashlib
import json
import os
import subprocess
import sys
import zipfile
from pathlib import Path

REVISION = 'geocalib-five-view-ikalibr-enrollment-v1'
CHECKOUT_REVISION = '97b8968e7798a66bf04fcf791fb535624241bda7'
CHECKPOINT_SHA256 = '13cc505928e3ff4eb26c00bff73861ab2b11b804a546323456cf5462e1f8f447'
BINDING = ('installationId', 'captureId', 'cameraId', 'width', 'height', 'imageAxes',
           'sensorOrientationDegrees', 'stabilizationRequested', 'capturePipeline', 'opticalSetup')


def inspect_capture(source):
    with zipfile.ZipFile(source) as archive:
        if len(set(archive.namelist())) != len(archive.namelist()):
            raise ValueError('ambiguous-capture')
        if sum(i.file_size for i in archive.infolist()) > 350 * 1024 ** 2:
            raise ValueError('capture-too-large')
        meta = json.loads(archive.read('manifest.json'))
        if (meta.get('kind') != 'phone-rapid-camera-imu-capture-v1'
                or meta.get('status') != 'completed' or meta.get('error')
                or any(k not in meta for k in BINDING)
                or meta.get('capturePipeline') != 'native-camera-imu-v2'
                or meta.get('timestampSource') != 'realtime'
                or meta.get('imageAxes') != 'native-sensor-unrotated-unmirrored'
                or (meta.get('width'), meta.get('height')) != (640, 480)
                or meta.get('opticalSetup') not in ('waist-bag-window', 'clear-lens')
                or meta.get('units') != {'accelerometer':'m/s2','gyroscope':'rad/s','magnetometer':'uT'}):
            raise ValueError('incomplete-or-unsupported-enrollment')
        if not isinstance(meta.get('alignmentMovementStartedBootNs'), int) or meta['alignmentMovementStartedBootNs']<=0:
            raise ValueError('movement-cue-missing')
        for name in ('imu.ndjson', 'frames.ndjson', 'capture-results.ndjson'):
            if name not in archive.namelist():
                raise ValueError('missing-real-capture-stream')
    return meta


def model_paths():
    base = Path(__file__).resolve().parents[1] / 'dist/few-shot-feasibility'
    python = os.environ.get('GAITTRACE_LEARNED_PYTHON')
    if not python:
        preferred = Path.home() / '.venv-cu130/Scripts/python.exe'
        python = str(preferred) if preferred.is_file() else sys.executable
    return {'python':python,'checkout':str(base/'GeoCalib'),
            'dependencies':str(base/'inference-deps'),'cache':str(base/'torch-hub')}

def runtime_ready():
    paths=model_paths()
    try:
        report=json.loads(Path(paths['checkout']).parent.joinpath('enrollment-runtime.json').read_text())
        return (report.get('kernelsExecuted') is True and report.get('sourceCommit')==CHECKOUT_REVISION
                and report.get('checkpointSha256')==CHECKPOINT_SHA256 and Path(paths['python']).is_file()
                and hashlib.sha256(Path(paths['cache'],'geocalib/distorted.tar').read_bytes()).hexdigest()==CHECKPOINT_SHA256)
    except (OSError,ValueError):return False


def run_enrollment(folder, reference_runner):
    folder = Path(folder)
    meta = inspect_capture(folder/'input.zip')
    request = {**model_paths(), 'source':str((folder/'input.zip').resolve()),
               'output':str(folder.resolve()), 'revision':REVISION,
               'workerSourceSha256':hashlib.sha256(Path(__file__).with_name('rapid_calibration_worker.py').read_bytes()).hexdigest(),
               'orchestratorSourceSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (folder/'learned-request.json').write_text(json.dumps(request))
    with (folder/'learned.log').open('w', encoding='utf-8') as log:
        try:
            subprocess.run([request['python'], str(Path(__file__).with_name('rapid_calibration_worker.py')),
                            str(folder/'learned-request.json')], stdout=log,
                           stderr=subprocess.STDOUT, check=True, timeout=300)
        except subprocess.CalledProcessError:
            failure=folder/'learned-failure.json'
            if failure.is_file():raise ValueError(json.loads(failure.read_text())['reason']) from None
            raise
    seed = json.loads((folder/'lens-seed.json').read_text())
    from rapid_calibration_worker import validate_seed
    validate_seed(seed,meta)
    if (seed.get('kind') != 'phone-learned-lens-seed-v1'
            or seed.get('calibrationSeedReady') is not True
            or seed.get('lensReady') is not False
            or any(seed['binding'].get(k) != meta[k] for k in BINDING)):
        raise ValueError('learned-seed-failed-integrity')
    result = reference_runner(folder)
    if result.get('lensProfile') != seed:
        raise ValueError('reference-did-not-use-learned-seed')
    from distance_validation import parameters
    parameters(result) # Reject impossible extrinsics/timing before returning a profile.
    from rapid_calibration_worker import refined_lens
    result['enrollment'] = {'method':REVISION, 'experimental':True,
                            'cameraSeed':seed['learned'], 'refinedLensCandidate':refined_lens(result),'neuralWeightsUpdated':False,
                            'shortScanGuaranteed':False, 'computerUsedOnce':True,
                            'ordinaryTestsRunOnPhone':True}
    # This is a candidate-label collection contract for future multi-phone training.
    # Labels remain explicitly solver-derived; no hidden clinical/truth upgrade.
    example = {'kind':'few-shot-camera-calibration-example-v1','schemaVersion':1,
               'binding':result['binding'],'sourceSha256':result['sourceSha256'],
               'device':meta['device'],'features':seed['learned']['viewPredictions'],
               'referenceParameters':result['upstreamParameters'],
               'labelSource':'ikalibr-candidate-not-independent-truth',
               'independentValidation':False,'enrollmentRevision':REVISION}
    if meta.get('artifactReplay'):example['artifactReplay']=meta['artifactReplay']
    (folder/'training-example.json').write_text(json.dumps(example, indent=2))
    result['trainingExample']=example
    temporary = folder/'result.json.tmp'
    temporary.write_text(json.dumps(result, indent=2)); temporary.replace(folder/'result.json')
    return result


def setup_model():
    """Pinned, local dependencies; never modifies the app or system policies."""
    paths = model_paths(); checkout = Path(paths['checkout'])
    checkout.parent.mkdir(parents=True, exist_ok=True)
    if not checkout.is_dir():
        subprocess.run(['git','clone','--no-checkout','https://github.com/cvg/GeoCalib.git',
                        str(checkout)],check=True)
        subprocess.run(['git','-C',str(checkout),'checkout',CHECKOUT_REVISION],check=True)
    revision = subprocess.run(['git','-C',str(checkout),'rev-parse','HEAD'],
                              check=True,capture_output=True,text=True).stdout.strip()
    if revision != CHECKOUT_REVISION:
        raise ValueError('Different GeoCalib checkout; preserve it and configure a separate pinned checkout')
    deps=Path(paths['dependencies'])
    if not all((deps/name).is_dir() for name in ['kornia','cv2','kornia_rs']):
        subprocess.run([paths['python'],'-m','pip','install','--target',paths['dependencies'],
                        '--no-deps','kornia==0.8.3','opencv-python==5.0.0.93','kornia_rs==0.2.0'],check=True)
    config=checkout.parent/'warmup-request.json';config.write_text(json.dumps(paths))
    checkout.parent.joinpath('enrollment-runtime.json').unlink(missing_ok=True)
    subprocess.run([paths['python'],str(Path(__file__).with_name('rapid_calibration_worker.py')),
                    '--warmup',str(config)],check=True,timeout=300)
    return paths


if __name__ == '__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--setup',action='store_true')
    args=parser.parse_args()
    if args.setup:print(json.dumps(setup_model(),indent=2))
