"""Recover the authors' pinned build sources from their distributed image layer.

Run inside WSL as root. This reads an existing content blob without changing the
working reference image. Output belongs in a local, ignored build context.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import tarfile

LAYER = "a06fd00b59fa0e661d8ab47f89fa80c40d7c291d08c5a6d6ba435deb8356d15a"
COMMITS = {
    "": "1fd2b88853ac2798c926c48cdd5b86fda15fde9d",
    "thirdparty/ctraj": "48d5bc7b2dc144cd35f8b31100a8c3db0d6353c5",
    "thirdparty/veta": "8097ba552ee797b22727b7963930458d6f27c073",
}


def recover(blob: Path, destination: Path) -> dict:
    destination = destination.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    with blob.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    if digest.hexdigest() != LAYER:
        raise ValueError("Unexpected authors' image layer")
    count = 0
    with tarfile.open(blob, "r|*") as archive:
        for member in archive:
            name = PurePosixPath(member.name)
            if name.is_absolute() or ".." in name.parts:
                raise ValueError("Unsafe archive member")
            if not str(name).startswith("home/iKalibr/src/"):
                continue
            target = destination.joinpath(*name.parts)
            if not target.resolve().is_relative_to(destination):
                raise ValueError("Member leaves build context")
            if member.isfile():
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.extractfile(member) as source, target.open("wb") as output:
                    shutil.copyfileobj(source, output)
                target.chmod(member.mode)
                count += 1
            elif member.isdir():
                target.mkdir(parents=True, exist_ok=True)
            elif member.issym():
                link = PurePosixPath(member.linkname)
                resolved = (target.parent / str(link)).resolve()
                if link.is_absolute() or not resolved.is_relative_to(destination):
                    # The catkin root symlink points into the base ROS install.
                    # Configure the package directly instead of extracting it.
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                if not target.is_symlink():
                    target.symlink_to(str(link))
            # No hard links or special device entries are extracted.
    root = destination / "home/iKalibr/src/ikalibr"
    for relative, expected in COMMITS.items():
        folder = root / relative
        actual = subprocess.check_output(
            ["git", "-C", str(folder), "rev-parse", "HEAD"], text=True
        ).strip()
        if actual != expected:
            raise ValueError(f"Unexpected source identity: {relative}: {actual}")
        subprocess.run(["git", "-C", str(folder), "diff", "--quiet", "HEAD"], check=True)
    report = {"layerSha256": LAYER, "sourceCommits": COMMITS, "filesRecovered": count}
    (destination / "source-provenance.json").write_text(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--blob", type=Path, default=Path(
        "/var/lib/containerd/io.containerd.content.v1.content/blobs/sha256") / LAYER)
    arguments = parser.parse_args()
    print(json.dumps(recover(arguments.blob, arguments.destination), indent=2))
