"""Acquire two size-selected TVS laboratory schema samples, not whole cohorts.

Uses resumable 1 MiB ranges and validates each ZIP member's length and CRC.
Cached chunks remain available for retry; no previous data are deleted.
Run with the project's existing Python 3.11 environment.
"""
import io
import json
from pathlib import Path
import struct
import urllib.request
import zipfile
import zlib
import hashlib
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data.http_ranges import download_range
from concurrent.futures import ThreadPoolExecutor

ROOT = Path(__file__).resolve().parents[1] / 'data/interim/public_imu_screen_2026-09-08'
ROOT.mkdir(parents=True, exist_ok=True)
if not (ROOT / 'tvs.json').exists():
    with urllib.request.urlopen('https://zenodo.org/api/records/15861907', timeout=15) as response:
        metadata = json.load(response)
    if metadata.get('id') != 15861907:
        raise RuntimeError('Unexpected dataset release')
    (ROOT / 'tvs.json').write_text(json.dumps(metadata, indent=2))
record = json.loads((ROOT / 'tvs.json').read_text(encoding='utf8'))

def read_piece(url, start, end):
    return download_range(url, start, end, ROOT / 'range_cache')


def read_range(url, start, end):
    # A global connection limit in http_ranges also covers metadata workers.
    ranges = [(i, min(i+1048575, end)) for i in range(start, end+1, 1048576)]
    with ThreadPoolExecutor(max_workers=2) as pool:
        return b''.join(pool.map(lambda pair: read_piece(url, *pair), ranges))


def main():
    manifest = []
    for cohort in ('HA', 'PD'):
        item = next(f for f in record['files'] if f['key'] == cohort+'.zip')
        url, size = item['links']['self'], item['size']
        tail_size = 200000
        tail = read_range(url, size-tail_size, size-1)
        archive = zipfile.ZipFile(io.BytesIO(tail))
        members = archive.infolist()
        inventory = [dict(name=i.filename, size=i.file_size, compressed=i.compress_size,
                          offset=i.header_offset+size-tail_size, crc32=i.CRC) for i in members]
        (ROOT / (cohort+'_inventory.json')).write_text(json.dumps(inventory, indent=2))
        candidates = [i for i in members if i.filename.endswith('/Laboratory/data.mat')]
        selected = min(candidates, key=lambda i:i.compress_size)
        if selected.compress_size > 60000000 or selected.file_size > 100000000:
            raise RuntimeError('Sample exceeds size cap')
        prefix = selected.filename.rsplit('/', 1)[0]+'/'
        for entry in [i for i in members if i.filename.startswith(prefix) and not i.is_dir()]:
            if entry.compress_size > 60000000 or entry.file_size > 100000000:
                raise RuntimeError('Member exceeds size cap')
            offset = entry.header_offset + size-tail_size
            header = read_range(url, offset, offset+29)
            if header[:4] != b'PK\x03\x04':
                raise RuntimeError('Invalid ZIP local header')
            name_len, extra_len = struct.unpack_from('<HH', header, 26)
            start = offset+30+name_len+extra_len
            compressed = read_range(url, start, start+entry.compress_size-1)
            if entry.compress_type == zipfile.ZIP_DEFLATED:
                raw = zlib.decompress(compressed, -15)
            elif entry.compress_type == zipfile.ZIP_STORED:
                raw = compressed
            else:
                raise RuntimeError('Unsupported compression')
            if len(raw) != entry.file_size or zlib.crc32(raw) != entry.CRC:
                raise RuntimeError('CRC or size mismatch')
            target = ROOT / (cohort+'_sample') / Path(entry.filename).name
            target.parent.mkdir(exist_ok=True)
            target.write_bytes(raw)
            manifest.append(dict(archive_url=url, member=entry.filename, bytes=len(raw),
                                 sha256=hashlib.sha256(raw).hexdigest(), crc_verified=True))
            print(cohort, entry.filename, len(raw), 'CRC verified', flush=True)
        (ROOT / 'sample_manifest.json').write_text(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
