"""Linux-side log handling and one-shot recovery for an owned replay directory."""
import re
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path, PurePosixPath

RESULTS = ('features.csv', 'features-summary.json', 'reference-states.csv',
           'reference-stdout.txt', 'reference-stderr.txt')
INPUTS = {'frames.csv', 'imu.csv', 'profile.json', 'reference.yaml', 'input-summary.json'}


def stage(directory, archive):
    folder = workspace(directory)
    with tarfile.open(archive, 'r:') as bundle:
        members = bundle.getmembers()
        if sum(member.size for member in members) > 350*1024**2:
            raise ValueError('Replay inputs exceed the transfer budget')
        names = set()
        for member in members:
            path = PurePosixPath(member.name)
            if (not path.parts or member.name in names or path.is_absolute() or '..' in path.parts or
                    not (member.isfile() or member.isdir()) or
                    not (member.name in INPUTS or path.parts[0] == 'frames')):
                raise ValueError('Invalid replay archive member')
            names.add(member.name)
        # Validate every entry before writing, and copy regular files only.
        for member in members:
            target = folder/member.name
            if member.isdir():target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with bundle.extractfile(member) as source, target.open('wb') as out:
                    shutil.copyfileobj(source, out)


def workspace(value):
    path = Path(value)
    if not re.fullmatch(r'/root/gaittrace-vio/jobs/replay-[A-Za-z0-9]+', str(path)):
        raise ValueError('Invalid owned replay workspace')
    if path.is_symlink() or path.resolve() != path:
        raise ValueError('Replay workspace must not redirect through a symlink')
    return path


def estimate(directory, engine):
    folder = workspace(directory)
    with (folder/'reference-stdout.txt').open('w') as out, \
            (folder/'reference-stderr.txt').open('w') as err:
        return subprocess.run([engine, str(folder)], stdout=out, stderr=err,
                              timeout=880).returncode


def recover(directory, destination):
    folder = workspace(directory)
    target = Path(destination)
    if not target.is_dir() or target.resolve() == folder:
        raise ValueError('Expected a separate existing replay output directory')
    for name in RESULTS:
        source = folder/name
        if source.is_symlink():
            raise ValueError('Unexpected symlink in replay results')
        if source.is_file():
            shutil.copyfile(source, target/name)


if __name__ == '__main__':
    action, directory, argument = sys.argv[1:]
    if action == 'estimate':
        sys.exit(estimate(directory, argument))
    elif action == 'recover':
        recover(directory, argument)
    elif action == 'stage':
        stage(directory, argument)
    else:
        raise ValueError('Unknown replay operation')
