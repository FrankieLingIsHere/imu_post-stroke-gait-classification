"""Shared, small utilities for the dataset access scripts.

All downloaders preserve the repository-provided file names and write an
inventory beside the downloaded files. They intentionally do not assume a
schema or sensor-channel naming convention.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_ROOT = PROJECT_ROOT / "data" / "raw"
CHUNK_BYTES = 1024 * 1024


def get_json(url: str) -> dict:
    request = Request(url, headers={"User-Agent": "post-stroke-gait-project/0.1"})
    with urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def download_files(files: Iterable[dict], destination: Path) -> None:
    """Download files, resuming an incomplete target when the server allows it."""
    destination.mkdir(parents=True, exist_ok=True)
    inventory: list[dict] = []
    for file_info in files:
        name = file_info["name"]
        url = file_info["download_url"]
        size = file_info.get("size")
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        existing_bytes = target.stat().st_size if target.exists() else 0
        if target.exists() and (size is None or existing_bytes == size):
            print(f"Already present: {target.name}")
        else:
            headers = {"User-Agent": "post-stroke-gait-project/0.1"}
            mode = "wb"
            if existing_bytes:
                headers["Range"] = f"bytes={existing_bytes}-"
                mode = "ab"
                print(
                    f"Resuming {target.name} at {existing_bytes} of "
                    f"{size or 'unknown'} bytes"
                )
            else:
                print(f"Downloading {target.name} ({size or 'unknown'} bytes)")
            request = Request(url, headers=headers)
            with urlopen(request, timeout=120) as response:
                if existing_bytes and response.status != 206:
                    raise RuntimeError(
                        f"{target.name} cannot be resumed safely: server returned "
                        f"HTTP {response.status} instead of HTTP 206."
                    )
                with target.open(mode) as stream:
                    while chunk := response.read(CHUNK_BYTES):
                        stream.write(chunk)
            if size is not None and target.stat().st_size != size:
                raise RuntimeError(
                    f"{target.name} is incomplete: expected {size} bytes, found "
                    f"{target.stat().st_size} bytes."
                )
        if size is not None and target.stat().st_size != size:
            raise RuntimeError(
                f"Size mismatch for {target}: expected {size} bytes, "
                f"found {target.stat().st_size} bytes"
            )
        inventory.append({"name": name, "source_url": url, "bytes": target.stat().st_size})
    (destination / "download_manifest.json").write_text(
        json.dumps(inventory, indent=2), encoding="utf-8"
    )


def print_tree(root: Path) -> None:
    """Print the actual local hierarchy after a download or manual extraction."""
    print(f"\\nLocal inventory: {root}")
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if path.is_dir():
            print(f"[DIR]  {relative}")
        else:
            print(f"[FILE] {relative} ({path.stat().st_size} bytes)")
