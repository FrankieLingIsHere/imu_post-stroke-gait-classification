"""Local CUDA feature execution and Linux storage, never a distance estimator."""
import json
import hashlib
import os
import secrets
import subprocess
import time
import atexit
import queue
import threading
import tarfile
import tempfile
from pathlib import Path

BASE = Path(__file__).resolve().parent
IMAGE = 'gaittrace-vio:cuda-v1'
_verified_status = None
_verified_at = None
_worker = None
_cpu_native = False
_cpu_status = None
JOBS = '/root/gaittrace-vio/jobs'


class CudaWorker:
    """Retain CUDA context and WSL runtime across short phone jobs."""
    def __init__(self, use_gpu=True):
        subprocess.run(wsl_prefix()+['mkdir', '-p', JOBS], check=True, capture_output=True)
        self.name = 'gaittrace-vio-worker-'+secrets.token_hex(8)
        self.lock = threading.Lock()
        self.responses = queue.Queue()
        self.closed = False
        log = BASE.parent/'dist/vio-cuda-worker.log'
        log.parent.mkdir(parents=True, exist_ok=True)
        self.log = log.open('a', encoding='utf-8')
        command = cuda_command(use_gpu=use_gpu)+['-i', '--name', self.name, '--mount',
            f'type=bind,src={JOBS},dst=/jobs', IMAGE, '/bridge/vio_reference.py', '--worker']
        self.process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=self.log, text=True, bufsize=1,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        threading.Thread(target=self._read, daemon=True).start()
        atexit.register(self.close)

    def _read(self):
        try:
            for line in self.process.stdout:
                self.responses.put(json.loads(line))
        except Exception as error:
            self.responses.put(error)
        finally:
            self.responses.put(RuntimeError('CUDA worker exited; capture remains saved'))

    def request(self, command, timeout=60):
        with self.lock:
            if self.closed or self.process.poll() is not None:
                raise RuntimeError('CUDA worker is not running; restart the helper')
            request = {**command, 'id': secrets.token_hex(8)}
            try:
                self.process.stdin.write(json.dumps(request)+'\n');self.process.stdin.flush()
                try:response = self.responses.get(timeout=timeout)
                except queue.Empty:raise TimeoutError('CUDA worker exceeded its processing budget')
                if isinstance(response, Exception):raise response
                if response.get('id') != request['id']:
                    raise RuntimeError('Unexpected CUDA worker response')
                if not response.get('ok'):
                    raise RuntimeError('CUDA worker: '+response.get('error', 'unknown failure'))
                return response['result']
            except Exception:
                self.close()
                raise

    def close(self):
        if self.closed:return
        self.closed = True
        try:
            if self.process.stdin:self.process.stdin.close()
            self.process.wait(timeout=5)
        except (OSError, subprocess.SubprocessError):
            subprocess.run(wsl_prefix()+['docker', 'stop', '--time', '5', self.name],
                           capture_output=True, timeout=20)
            self.process.terminate()
        finally:
            self.log.close()


def worker_request(command, timeout=60, use_gpu=True):
    global _worker
    if _worker is None or _worker.closed:
        _worker = CudaWorker(use_gpu=use_gpu)
    return _worker.request(command, timeout)


def wsl_prefix():
    return ['wsl.exe', '-d', 'Ubuntu', '-u', 'root', '--'] if os.name == 'nt' else []


def backend():
    value = os.environ.get('GAITTRACE_VIO_BACKEND', 'cpu')
    if value not in ('cuda', 'cpu'):
        raise ValueError('GAITTRACE_VIO_BACKEND must be cuda or cpu')
    return value


def cuda_command(directory=None, use_gpu=True):
    from calibration_companion import linux_path
    command = wsl_prefix()+['docker', 'run', '--rm', '--network', 'none',
        '-e', 'CUDA_CACHE_PATH=/cuda-cache', '--mount', 'type=volume,src=gaittrace-vio-cuda-cache,dst=/cuda-cache',
        '--mount', f'type=bind,src={linux_path(BASE)},dst=/bridge,readonly']
    if use_gpu:command += ['--gpus', 'all']
    if directory:
        command += ['--mount', f'type=bind,src={directory},dst=/data']
    if _verified_status:
        # Reuse actual startup device identification; no nvidia-smi subprocess
        # per short feature job. CUDA kernels still execute and synchronize.
        command += ['-e', 'GAITTRACE_GPU_NAME='+_verified_status['device']]
    return command


def probe_compute(cached_only=False):
    global _verified_status, _verified_at
    if backend() == 'cpu':
        return _cpu_status or {'backend': 'cpu', 'gpuUsed': False, 'kernelCheckPassed': False,
                'reason': 'CPU selected; native worker unavailable, Windows fallback'}
    if cached_only:
        if _verified_status is None:
            raise ValueError('Restart the helper to run its CUDA kernel preflight')
        return {**_verified_status, 'kernelCheckAgeSeconds': time.monotonic()-_verified_at,
                'preflightSource': 'actual helper-startup kernel execution'}
    status = worker_request({'command': 'probe'})
    if (status.get('backend') != 'cuda' or status.get('kernelCheckPassed') is not True or
            status.get('cudaLKCalls', 0) < 2 or status.get('cudaCornerCalls', 0) < 1):
        raise ValueError('CUDA kernel execution was not verified')
    _verified_status, _verified_at = status, time.monotonic()
    return status


def setup_compute():
    global _cpu_native, _cpu_status
    from calibration_companion import linux_path
    if backend() == 'cuda':
        digest = hashlib.sha256((BASE/'vio-cuda/Dockerfile').read_bytes().replace(b'\r\n', b'\n')).hexdigest()
        exists = subprocess.run(wsl_prefix()+['docker', 'image', 'inspect', '--format',
            '{{index .Config.Labels "org.gaittrace.cuda-recipe-sha256"}}', IMAGE], capture_output=True, text=True)
        if exists.returncode or exists.stdout.strip() != digest:
            print('Building the local CUDA optical-flow backend (one-time setup)...', flush=True)
            subprocess.run(wsl_prefix()+['docker', 'build', '--build-arg', 'GAITTRACE_RECIPE_SHA256='+digest, '-t', IMAGE,
                linux_path(BASE/'vio-cuda')], check=True)
    else:
        exists = subprocess.run(wsl_prefix()+['docker', 'image', 'inspect', IMAGE], capture_output=True)
        _cpu_native = exists.returncode == 0
        if _cpu_native:
            _cpu_status = worker_request({'command': 'cpu-probe'}, use_gpu=False)
    status = probe_compute()
    print('Distance processing backend:', json.dumps(status), flush=True)
    return status


def cuda_features(directory, log_directory=None):
    if not directory.startswith(JOBS+'/replay-') or '/' in directory[len(JOBS)+1:]:
        raise ValueError('Invalid Linux replay workspace')
    result = worker_request({'command': 'tracks', 'directory': '/jobs/'+Path(directory).name,
                             'backend': 'cuda'}, timeout=900)
    if log_directory:
        (Path(log_directory)/'frontend-stdout.txt').write_text(json.dumps(result, indent=2))
    return result


def run_replay(replay, engine):
    """Stage once into Linux storage; never flush per-frame files through /mnt/c.

    GPU failure fails this attempt, rather than silently claiming acceleration.
    Outputs are recovered on failure. Retain the Linux workspace if recovery fails.
    """
    from calibration_companion import linux_path
    from vio_reference import export_feature_tracks
    prefix = wsl_prefix()
    root = JOBS
    subprocess.run(prefix+['mkdir', '-p', root], check=True, capture_output=True)
    directory = subprocess.check_output(prefix+['mktemp', '-d', root+'/replay-XXXXXXXXXXXX'], text=True).strip()
    if not directory.startswith(root+'/replay-') or '/' in directory[len(root)+1:]:
        raise RuntimeError('Unexpected Linux workspace path')
    timings = {}
    recovered = False
    selected = backend()
    try:
        tick = time.perf_counter()
        inputs = ['frames', 'frames.csv', 'imu.csv', 'profile.json', 'reference.yaml', 'input-summary.json']
        # One sequential archive crosses /mnt/c instead of hundreds of JPEG
        # file opens. Packing time is included in the measured import stage.
        with tempfile.TemporaryDirectory(prefix='vio-transfer-', dir=replay.parent) as temp:
            archive = Path(temp)/'inputs.tar'
            with tarfile.open(archive, 'w') as bundle:
                for name in inputs:bundle.add(replay/name, arcname=name)
            subprocess.run(prefix+['python3', linux_path(BASE/'vio_workspace.py'),
                           'stage', directory, linux_path(archive)],
                           check=True, capture_output=True, timeout=180)
        timings['importSeconds'] = time.perf_counter()-tick
        tick = time.perf_counter()
        print('Distance trial: '+selected.upper()+' optical flow...', flush=True)
        if selected == 'cuda':
            cuda_features(directory, replay)
        elif _cpu_native:
            worker_request({'command': 'tracks', 'directory': '/jobs/'+Path(directory).name,
                            'backend': 'cpu'}, timeout=900, use_gpu=False)
        else:
            # Explicit portability path; no GPU claim for CPU execution.
            export_feature_tracks(replay, backend='cpu')
            for name in ('features.csv', 'features-summary.json'):
                subprocess.run(prefix+['cp', linux_path(replay/name), directory+'/'+name], check=True)
        timings['featureStageSeconds'] = time.perf_counter()-tick
        tick = time.perf_counter()
        print('Distance trial: published VINS estimator (CPU)...', flush=True)
        # Keep the estimator's verbose per-frame logs on Linux too. Transfer
        # them once with the results, including on a failed attempt.
        subprocess.run(prefix+['python3', linux_path(BASE/'vio_workspace.py'),
                       'estimate', directory, engine], check=True, capture_output=True, timeout=900)
        timings['estimatorSeconds'] = time.perf_counter()-tick
    finally:
        # Only generated result files return; original captures stay untouched.
        tick = time.perf_counter()
        try:
            subprocess.run(prefix+['python3', linux_path(BASE/'vio_workspace.py'),
                           'recover', directory, linux_path(replay)],
                           check=True, capture_output=True, timeout=120)
            recovered = True
        finally:
            timings['exportSeconds'] = time.perf_counter()-tick
            record = {'storage': 'linux-native', 'requestedBackend': selected,
                      'estimatorBackend': 'cpu', 'timings': timings,
                      'outputsRecovered': recovered}
            record['transferStrategy'] = 'archive-import-linux-logs-batched-output-v2'
            record['featureWorker'] = ('persistent-cuda-context' if selected == 'cuda' else
                                      'persistent-native-cpu' if _cpu_native else 'windows-cpu')
            if selected == 'cuda':
                image = subprocess.run(prefix+['docker', 'image', 'inspect', '--format', '{{.Id}}', IMAGE],
                                       capture_output=True, text=True, timeout=15)
                record['cudaImageId'] = image.stdout.strip() if image.returncode == 0 else None
            if recovered:
                subprocess.run(prefix+['rm', '-rf', '--', directory], check=True, capture_output=True)
            else:
                record['retainedWorkspace'] = directory
            (replay/'compute-summary.json').write_text(json.dumps(record, indent=2))
    return json.loads((replay/'compute-summary.json').read_text())


if __name__ == '__main__':
    setup_compute()
