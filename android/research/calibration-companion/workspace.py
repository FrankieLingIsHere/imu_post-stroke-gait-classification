"""Copy a reference job across the host boundary only at stage boundaries.

The published solver writes/flushes large pair lists. Keep its working files on
Linux storage instead of flushing each line through a Windows bind mount.
"""
import argparse
import hashlib
import json
import shutil
from pathlib import Path


def import_capture(source, destination):
    source, destination = Path(source), Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    capture = source / 'input.zip'
    digest = hashlib.sha256(capture.read_bytes()).hexdigest()
    shutil.copyfile(capture, destination / 'input.zip')
    if (source / 'lens-seed.json').is_file():
        shutil.copyfile(source / 'lens-seed.json', destination / 'lens-seed.json')
    if hashlib.sha256((destination / 'input.zip').read_bytes()).hexdigest() != digest:
        raise ValueError('Capture copy verification failed.')
    (destination / 'workspace-transfer.json').write_text(json.dumps({
        'sourceSha256': digest,
        'storage': 'linux-docker-volume',
        'rawCaptureUnchanged': True,
    }, indent=2))


def export_outputs(source, destination):
    source, destination = Path(source), Path(destination)
    record = json.loads((source / 'workspace-transfer.json').read_text())
    if hashlib.sha256((destination / 'input.zip').read_bytes()).hexdigest() != record['sourceSha256']:
        raise ValueError('Original capture changed during processing.')
    if hashlib.sha256((source / 'input.zip').read_bytes()).hexdigest() != record['sourceSha256']:
        raise ValueError('Working capture changed during processing.')
    # Host job/status/log files are never copied into the temporary workspace.
    # Preserve partial solver evidence on failure; never overwrite the raw ZIP.
    for path in source.iterdir():
        if path.name == 'input.zip':
            continue
        if path.is_symlink() or (path.is_dir() and any(p.is_symlink() for p in path.rglob('*'))):
            raise ValueError('Unexpected symbolic link in reference output.')
        if path.is_dir():
            shutil.copytree(path, destination / path.name, dirs_exist_ok=True)
        elif path.is_file():
            shutil.copyfile(path, destination / path.name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['import', 'export'])
    args = parser.parse_args()
    if args.mode == 'import':
        import_capture('/transfer', '/data')
    else:
        export_outputs('/data', '/transfer')
