"""Audit retained camera/IMU captures before claiming cross-device model training.

Reads manifests only. Repeated processing archives, adapted main-flow replays and
synthetic controls never create new training tasks. Device model is a conservative
grouping: different physical units of the same model still need explicit identity.
Experiment orchestration and saved outputs belong in the calibration notebook.
"""
import hashlib
import json
import os
import zipfile
from collections import Counter
from pathlib import Path


SKIP = {
    'node_modules', '.git', '.gradle', '.cxx', 'build', '_deps',
    'native-distance-tools', 'gradle-cache', 'phone-vio-native',
    'gait-main-native', 'calibration-cuda-tools', 'vio-cuda-tools',
}
PREFIXES = ('calibration-', 'distance-trial-', 'imu-noise-', 'gait-camera-')


def _category(meta):
    if meta.get('artifactReplay'):
        return 'historical-metadata-replay'
    identifier = str(meta.get('captureId', ''))
    device = meta.get('device') or {}
    installation = str(meta.get('installationId', ''))
    if ('synthetic' in identifier.lower() or 'synthetic' in installation.lower()
            or 'synthetic' in str(device).lower()):
        return 'synthetic-control'
    if identifier.startswith('gait-camera-main-contract-replay-'):
        return 'historical-metadata-replay'
    if identifier.startswith('calibration-'):
        return 'calibration-capture'
    if identifier.startswith('distance-trial-'):
        return 'distance-trial'
    if identifier.startswith('imu-noise-'):
        return 'stationary-noise'
    return 'unclassified-not-admitted'


def scan_archives(roots):
    rows, errors = [], []
    for root in map(Path, roots):
        if not root.is_dir():
            errors.append({'root': str(root), 'error': 'directory-unavailable'})
            continue
        for folder, dirs, files in os.walk(root, followlinks=False):
            dirs[:] = [d for d in dirs if d not in SKIP
                       and not Path(folder, d).is_symlink()]
            for name in files:
                if not name.lower().endswith('.zip'):
                    continue
                if root.name in {'Downloads', 'Telegram Desktop'} and not name.startswith(PREFIXES):
                    continue
                path = Path(folder, name)
                try:
                    with zipfile.ZipFile(path) as archive:
                        if 'manifest.json' not in archive.namelist():
                            continue
                        info = archive.getinfo('manifest.json')
                        if info.file_size > 4_000_000:
                            raise ValueError('oversized-manifest')
                        raw = archive.read(info)
                        meta = json.loads(raw)
                        if not isinstance(meta, dict) or not meta.get('captureId'):
                            raise ValueError('missing-capture-identity')
                        category = _category(meta)
                        rows.append({
                            'path': str(path), 'captureId': meta['captureId'],
                            'manifestSha256': hashlib.sha256(raw).hexdigest(),
                            'category': category, 'kind': meta.get('kind'),
                            'device': meta.get('device'),
                            'installationId': meta.get('installationId'),
                            'cameraId': meta.get('cameraId'),
                            'width': meta.get('width'), 'height': meta.get('height'),
                            'opticalSetup': meta.get('opticalSetup'),
                            'frames': meta.get('frames'),
                            'hasSynchronizedImu': 'imu.ndjson' in archive.namelist(),
                            'hasSavedFrameIndex': 'frames.ndjson' in archive.namelist(),
                            'lensCandidateAttached': isinstance(meta.get('lensProfile'), dict),
                        })
                except (OSError, ValueError, zipfile.BadZipFile, KeyError) as error:
                    errors.append({'path': str(path), 'error': str(error)})
    return rows, errors


def summarize(rows, errors):
    groups = {}
    for row in rows:
        groups.setdefault(row['captureId'], []).append(row)
    unique = [items[0] for items in groups.values()]
    physical = [r for r in unique if r['category'] in {
        'calibration-capture', 'distance-trial', 'stationary-noise'}]
    models = sorted({(r.get('device') or {}).get('manufacturer', 'unknown') + '/' +
                     (r.get('device') or {}).get('model', 'unknown') for r in physical})
    installations = {r['installationId'] for r in physical if r['installationId']}
    physical_camera = [r for r in physical if r['category'] != 'stationary-noise']
    return {
        'kind': 'camera-imu-few-shot-training-feasibility-v1',
        'archiveManifestCount': len(rows), 'distinctCaptureIds': len(unique),
        'distinctPhysicalCaptures': len(physical),
        'categories': dict(Counter(r['category'] for r in unique)),
        'physicalDeviceModels': models,
        'physicalInstallationCount': len(installations),
        'physicalCameraCaptures': len(physical_camera),
        'synchronizedPhysicalCameraCaptures': sum(r['hasSynchronizedImu'] for r in physical_camera),
        'heldOutDeviceModelPossible': len(models) > 1,
        'crossDeviceFewShotTrainingReady': False,
        'reasons': [
            'Only one observed physical device model; no held-out-device evaluation.'
            if len(models) == 1 else 'Device diversity alone does not establish calibration labels.',
            'Saved calibration solutions are candidate/proxy labels, not independent per-device truth.',
            'Whole-route distance labels do not supply synchronized ground-truth trajectories.',
            'Many adjacent frames or derived archive copies do not create independent tasks.',
        ],
        'modelTrainingExecuted': False, 'newPhysicalCapture': False,
        'scope': 'Available local manifest-bearing ZIPs; ordinary IMU-only exports are not camera calibration tasks.',
        'errors': errors,
    }
