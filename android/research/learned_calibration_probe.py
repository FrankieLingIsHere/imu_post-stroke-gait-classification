"""GPU probe of pretrained few-image calibration, orchestrated by the notebook.

No neural weights are fitted. GeoCalib's shared-intrinsics geometric optimization
is not a meta-trained phone calibration network or metric-distance validation.
"""
import hashlib
import json
import re
import subprocess
import sys
import time
import zipfile
from pathlib import Path

GEOCALIB_REVISION = '97b8968e7798a66bf04fcf791fb535624241bda7'


def check_binding(meta, reference):
    binding = reference.get('binding') or {}
    for key in ('installationId', 'cameraId', 'width', 'height', 'imageAxes',
                'opticalSetup', 'stabilizationRequested'):
        if key not in binding or meta.get(key) != binding[key]:
            raise ValueError(f'Reference/capture binding mismatch: {key}')


def run_probe(archives, reference, checkout, dependencies, output):
    checkout, dependencies, output = map(Path, (checkout, dependencies, output))
    revision = subprocess.run(['git', '-C', str(checkout), 'rev-parse', 'HEAD'],
                              capture_output=True, text=True, check=True).stdout.strip()
    if revision != GEOCALIB_REVISION:
        raise ValueError('Unexpected GeoCalib source revision')
    sys.path[:0] = [str(dependencies), str(checkout)]
    import torch
    from geocalib import GeoCalib

    if not torch.cuda.is_available():
        raise RuntimeError('This research probe requires the requested CUDA runtime')
    output.mkdir(parents=True, exist_ok=True)
    torch.hub.set_dir(str(output / 'torch-hub'))
    torch.manual_seed(42)
    model = GeoCalib(weights='distorted').to('cuda')
    candidate = reference['upstreamParameters']['CalibParam']['INTRI']['Camera'][0]
    target = candidate['value']['ptr_wrapper']['data']['focal_length']
    trials = []
    for archive_path in map(Path, archives):
        with zipfile.ZipFile(archive_path) as archive:
            meta = json.loads(archive.read('manifest.json'))
            check_binding(meta, reference)
            if not re.fullmatch(r'[a-zA-Z0-9_-]+', str(meta.get('captureId', ''))):
                raise ValueError('Invalid capture identity')
            if meta.get('kind') != 'front-camera-distance-research-v1':
                raise ValueError('Use physical research trials, not adapted main-flow replays')
            start = meta['diagnostics']['walkStartedBootNs']
            end = meta['diagnostics']['walkEndedBootNs']
            index = [json.loads(line) for line in archive.read('frames.ndjson').decode().splitlines()
                     if line.strip()]
            frames = [f for f in index if start <= f['timestampNs'] <= end]
            if len(frames) < 5:
                raise ValueError('Not enough measured-motion frames')
            tensors, names = [], []
            for i, fraction in enumerate((.1, .3, .5, .7, .9)):
                frame = frames[round((len(frames) - 1) * fraction)]
                name = frame['file']
                if not name.startswith('frames/') or '..' in name:
                    raise ValueError('Invalid frame filename')
                path = output / f"{meta['captureId']}-view-{i}.jpg"
                path.write_bytes(archive.read(name))
                tensors.append(model.load_image(path).to('cuda'))
                names.append(name)
        torch.cuda.synchronize()
        started = time.perf_counter()
        result = model.calibrate(torch.stack(tensors), camera_model='simple_radial',
                                 shared_intrinsics=True)
        torch.cuda.synchronize()
        focal = result['camera'].f.detach().cpu().tolist()
        mean_focal = sum(focal[0]) / len(focal[0])
        mismatch = 100 * (mean_focal / (sum(target) / len(target)) - 1)
        trial = {'captureId': meta['captureId'], 'sourceArchive': str(archive_path),
                 'views': names, 'focalPixels': focal,
                 'distortion': result['camera'].dist.detach().cpu().tolist(),
                 'focalUncertaintyPixels': result['focal_uncertainty'].detach().cpu().tolist(),
                 'secondsGpuDesktop': time.perf_counter() - started,
                 'candidateMeanFocalMismatchPercent': mismatch}
        trials.append(trial)
        print(json.dumps(trial), flush=True)
    checkpoint = output / 'torch-hub/geocalib/distorted.tar'
    report = {'kind': 'pretrained-geocalib-few-view-retained-comparison-v1',
              'sourceCommit': revision,
              'checkpointSha256': hashlib.sha256(checkpoint.read_bytes()).hexdigest(),
              'device': torch.cuda.get_device_name(0), 'torchVersion': torch.__version__,
              'referenceCandidateFocalPixels': target, 'trials': trials,
              'neuralWeightsUpdated': False, 'ourRecordingModelTraining': False,
              'metricDistanceComputed': False, 'actualAndroidInference': False,
              'independentCalibrationValidation': False,
              'limitations': ['Same phone and retained room, no held-out phone.',
                              'Candidate calibration comparison, not physical truth.',
                              'Simple radial and centered principal point differ from saved lens model.',
                              'No camera/IMU timing, extrinsics or metric-distance estimate.',
                              'Internal uncertainty has not been calibrated on this optical setup.']}
    (output / 'geocalib-comparison.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    return report


if __name__ == '__main__':
    config = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
    reference = json.loads(Path(config.pop('reference')).read_text(encoding='utf-8'))['reference']
    run_probe(reference=reference, **config)
