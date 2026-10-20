"""Versioned local research processing, independent of marked route length."""
import hashlib
import json
import os
import zipfile
from pathlib import Path, PurePosixPath

import numpy as np

BASE = Path(__file__).resolve().parent
LEGACY = 'fixed-time-v2'
CORRECTED = 'fixed-time-rows-quiet-v1'
ENGINE = '/root/gaittrace-vio/distance-build-v3/vins_reference'
LEGACY_ENGINE = '/root/gaittrace-vio/reference-build/vins_reference'


def processing_spec():
    mode = os.environ.get('GAITTRACE_DISTANCE_PIPELINE', LEGACY)
    if mode not in (LEGACY, CORRECTED):
        raise ValueError('Invalid GAITTRACE_DISTANCE_PIPELINE research method.')
    backend = os.environ.get('GAITTRACE_VIO_BACKEND', 'cpu')
    if backend not in ('cpu', 'cuda'):
        raise ValueError('Invalid GAITTRACE_VIO_BACKEND research backend.')
    digest = hashlib.sha256()
    for name in ('distance_pipeline.py', 'distance_validation.py', 'vio_reference.py',
                 'vio_compute.py', 'vio_workspace.py', 'vio-reference/replay.cpp',
                 'vio-reference/fixed_time_observation.h', 'vio-reference/compat.h',
                 'vio-reference/CMakeLists.txt'):
        digest.update(name.encode()+b'\0')
        digest.update((BASE/name).read_bytes().replace(b'\r\n', b'\n'))
    return {'mode': mode, 'featureBackend': backend, 'revision': mode+':'+backend+':'+digest.hexdigest(),
            'fixedTimeRowCorrection': mode == CORRECTED,
            'quietInitializationRequired': mode == CORRECTED,
            'enginePath': ENGINE if mode == CORRECTED else LEGACY_ENGINE,
            'distanceReady': False}


def quiet_initialization(source, sigma):
    """First continuous two-second quiet interval before measured motion.

    Keep its baseline and following practice. Raw capture is never modified.
    Quietness is not proof of placement. No distance labels enter this function.
    """
    if not np.isfinite(sigma) or sigma <= 0:
        raise ValueError('Invalid initialization noise candidate.')
    with zipfile.ZipFile(source) as bundle:
        meta = json.loads(bundle.read('manifest.json'))
        samples = [json.loads(line) for line in bundle.read('imu.ndjson').decode().splitlines() if line.strip()]
    streams = []
    for sensor in ('accelerometer', 'gyroscope'):
        rows = [r for r in samples if r['sensor'] == sensor]
        times = np.array([r['timestampNs'] for r in rows], dtype=np.int64)
        values = np.array([[r[k] for k in ('x', 'y', 'z')] for r in rows], dtype=float)
        if len(times) < 2 or np.any(np.diff(times) <= 0) or not np.isfinite(values).all():
            raise ValueError('Initialization requires finite, monotonic native IMU.')
        streams.append((times, np.linalg.norm(values, axis=1)))
    (at, av), (gt, gv) = streams
    boundary = meta.get('diagnostics', {}).get('walkStartedBootNs')
    if type(boundary) is not int or boundary <= max(int(at[0]), int(gt[0])):
        raise ValueError('Measured first-motion boundary is missing.')
    threshold = 3 * float(sigma)
    for i in range(0, len(at), 10):
        end = int(at[i]); start = end - 2_000_000_000
        if end >= boundary: break
        if start < max(int(at[0]), int(gt[0])): continue
        ai = int(np.searchsorted(at, start))
        gi = int(np.searchsorted(gt, start)); gj = int(np.searchsorted(gt, end, side='right'))
        a, g = av[ai:i+1], gv[gi:gj]
        # Native approximately 200 Hz streams: prohibit sparse windows or gaps.
        if (len(a) <= 100 or len(g) <= 100 or at[ai]-start > 20_000_000 or gt[gi]-start > 20_000_000
                or end-gt[gj-1] > 20_000_000
                or np.max(np.diff(at[ai:i+1])) > 20_000_000
                or np.max(np.diff(gt[gi:gj])) > 20_000_000): continue
        if np.std(a) <= threshold and np.max(g) < .08:
            return {'rule': 'first-two-second-noise-bound-quiet-window-before-measured-motion-v1',
                    'startBootNs': start, 'quietEndBootNs': end,
                    'excludedPrefixSeconds': (start-meta['startedBootNs'])/1e9,
                    'accelerationNormStdLimit': threshold, 'gyroNormMaximumLimit': .08,
                    'quietWindowSeconds': 2, 'placementAnatomicallyVerified': False,
                    'rawCaptureModified': False, 'groundTruthUsedToSetScale': False}
    raise ValueError('No continuous quiet baseline before measured motion; capture retained for review.')


def validate_engine_capabilities(capabilities, spec):
    if (capabilities.get('distanceProtocolVersion') != 2 or capabilities.get('fixedGeometry') is not True
            or capabilities.get('fixedTimeOffset') is not True): return False
    return (not spec['fixedTimeRowCorrection'] or
            capabilities.get('fixedTimeRowCorrection') is True and
            capabilities.get('replayInitializationWindow') is True)


def setup_distance_engine():
    """Build reviewed wrapper locally; never replace the legacy executable."""
    import subprocess
    from calibration_companion import linux_path
    from vio_compute import wsl_prefix
    spec = processing_spec()
    if spec['mode'] == CORRECTED:
        build = str(PurePosixPath(ENGINE).parent)
        print('Preparing corrected research distance engine (local computer)...', flush=True)
        subprocess.run(wsl_prefix()+['cmake', '-S', linux_path(BASE/'vio-reference'), '-B', build,
            '-DCMAKE_BUILD_TYPE=Release', '-DVINS_SOURCE=/root/gaittrace-vio/vins-mono',
            '-DCeres_DIR=/root/gaittrace-vio/ceres-install/lib/cmake/Ceres'], check=True, timeout=120)
        subprocess.run(wsl_prefix()+['cmake', '--build', build, '--parallel', '2'], check=True, timeout=900)
        subprocess.run(wsl_prefix()+['ctest', '--test-dir', build, '--output-on-failure'], check=True, timeout=60)
    probe = subprocess.run(wsl_prefix()+[spec['enginePath'], '--capabilities'], capture_output=True, text=True, check=True, timeout=10)
    if not validate_engine_capabilities(json.loads(probe.stdout), spec):
        raise ValueError('Distance engine lacks the selected processing capabilities.')
    print('Research distance processing:', spec['revision'], '; distance accuracy remains unvalidated.', flush=True)
    return spec
