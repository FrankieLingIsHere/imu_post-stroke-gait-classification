"""Persistent, disk-resumable HTTP range transfers for version-pinned archives.

The caller must validate the extracted archive member's CRC/checksum. There is
no total-transfer deadline: timeout measures connection setup or socket inactivity.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import threading
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import requests

_connections = threading.BoundedSemaphore(2)
_local = threading.local()


def _session():
    if not hasattr(_local, 'session'):
        _local.session = requests.Session()
        _local.session.headers.update({'Accept-Encoding': 'identity',
                                       'User-Agent': 'TVS-research-intake/1.0'})
    return _local.session


def download_range(url, start, end, cache, *, attempts=3, timeout=(15, 45), backoff=2):
    if start < 0 or end < start or attempts < 1:
        raise ValueError('Invalid byte range or attempt count')
    cache = Path(cache)
    cache.mkdir(parents=True, exist_ok=True)
    target = cache/hashlib.sha256(f'{url}:{start}:{end}'.encode()).hexdigest()
    part = target.with_suffix('.part')
    state_path = target.with_suffix('.state.json')
    digest_path = target.with_suffix('.sha256')
    expected = end-start+1
    if target.exists():
        content = target.read_bytes()
        if len(content) != expected:
            raise ValueError('Invalid completed range cache size')
        digest = hashlib.sha256(content).hexdigest()
        if digest_path.exists() and digest_path.read_text() != digest:
            raise ValueError('Range cache checksum mismatch')
        # Legacy caches are still verified by the caller's ZIP CRC.
        return content
    state = json.loads(state_path.read_text()) if state_path.exists() else {}
    if part.exists() and not state:
        raise ValueError('Partial range has no provenance')
    for attempt in range(attempts):
        offset = part.stat().st_size if part.exists() else 0
        if offset > expected:
            raise ValueError('Partial range exceeds requested length')
        if offset == expected:
            break
        headers = {'Range': f'bytes={start+offset}-{end}'}
        if state.get('validator'):
            headers['If-Range'] = state['validator']
        delay = backoff * 2**attempt
        print(f'GET bytes {start+offset}-{end}, attempt {attempt+1}/{attempts}', flush=True)
        try:
            with _connections, _session().get(url, headers=headers, stream=True,
                                             timeout=timeout) as response:
                if response.status_code in (408, 429, 500, 502, 503, 504):
                    retry_after = response.headers.get('Retry-After', '')
                    if retry_after.isdigit():
                        delay = max(delay, int(retry_after))
                    elif retry_after:
                        try:
                            delay = max(delay, (parsedate_to_datetime(retry_after)-datetime.now(timezone.utc)).total_seconds())
                        except (ValueError, TypeError):
                            pass
                    response.raise_for_status()
                if response.status_code != 206:
                    raise ValueError(f'Expected partial response, got HTTP {response.status_code}; body not downloaded')
                match = re.fullmatch(r'bytes (\d+)-(\d+)/(\d+)', response.headers.get('Content-Range', ''))
                if not match or tuple(map(int, match.groups()[:2])) != (start+offset, end):
                    raise ValueError('Server returned the wrong range')
                total = int(match[3])
                if total <= end or state.get('total', total) != total:
                    raise ValueError('Archive length changed')
                if response.headers.get('Content-Encoding', 'identity') != 'identity':
                    raise ValueError('Encoded response cannot be mapped to archive bytes')
                validator = response.headers.get('ETag')
                if not validator or validator.startswith('W/'):
                    validator = response.headers.get('Last-Modified')
                if state.get('validator') and validator != state['validator']:
                    raise ValueError('Archive validator changed during resume')
                state = dict(total=total, validator=validator)
                state_path.write_text(json.dumps(state))
                with part.open('ab') as handle:
                    for block in response.iter_content(chunk_size=65536):
                        if offset+len(block) > expected:
                            raise ValueError('Server exceeded requested range')
                        handle.write(block)
                        handle.flush()
                        offset += len(block)
                    os.fsync(handle.fileno())
                if offset != expected:
                    raise requests.ConnectionError('Incomplete response body')
            break
        except (requests.Timeout, requests.ConnectionError, requests.HTTPError,
                requests.exceptions.ChunkedEncodingError) as error:
            status = error.response.status_code if getattr(error, 'response', None) is not None else None
            print(f'{type(error).__name__} HTTP={status}; retained {part.stat().st_size if part.exists() else 0}/{expected} bytes', flush=True)
            if attempt+1 == attempts:
                raise
            # Respect long Retry-After without silently hammering the server.
            if delay > 60:
                raise RuntimeError(f'Server requested {delay}s retry delay; resume later') from error
            time.sleep(delay)
    content = part.read_bytes()
    if len(content) != expected:
        raise ValueError('Range completion length mismatch')
    digest_path.write_text(hashlib.sha256(content).hexdigest())
    part.replace(target)
    return content
