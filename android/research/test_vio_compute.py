import csv
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

import cv2
import numpy as np

from vio_reference import export_feature_tracks, cuda_probe
from vio_compute import backend, cuda_features, probe_compute, setup_compute, CudaWorker


class ComputeChecks(unittest.TestCase):
    def test_archive_stage_preserves_frame_bytes_and_clocks_and_rejects_traversal(self):
        import io, tarfile
        from vio_workspace import stage
        with tempfile.TemporaryDirectory() as temp:
            output=Path(temp)/'output';output.mkdir()
            archive=Path(temp)/'inputs.tar'
            content={'frames/00000.jpg':b'unchanged JPEG bytes', 'frames.csv':b'timestamp_ns,file\n123456789,frames/00000.jpg\n'}
            with tarfile.open(archive,'w') as bundle:
                for name,data in content.items():
                    member=tarfile.TarInfo(name);member.size=len(data);bundle.addfile(member,io.BytesIO(data))
            with patch('vio_workspace.workspace',return_value=output):stage('owned',archive)
            for name,data in content.items():self.assertEqual((output/name).read_bytes(),data)
            with tarfile.open(archive,'w') as bundle:
                bundle.addfile(tarfile.TarInfo('../escaped'))
            with patch('vio_workspace.workspace',return_value=output):
                with self.assertRaises(ValueError):stage('owned',archive)
            self.assertFalse((Path(temp)/'escaped').exists())

    def test_cpu_is_the_measured_default_but_cuda_remains_selectable(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(backend(), 'cpu')
        with patch.dict(os.environ, {'GAITTRACE_VIO_BACKEND': 'cuda'}):
            self.assertEqual(backend(), 'cuda')

    def test_workspace_recovery_preserves_partial_results_and_failure_logs(self):
        from vio_workspace import recover, RESULTS
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp)/'source';source.mkdir()
            target = Path(temp)/'output';target.mkdir()
            (source/'features.csv').write_text('real features')
            (source/'reference-stderr.txt').write_text('solver failed: retained diagnostic')
            (source/'frames.csv').write_text('must stay local')
            with patch('vio_workspace.workspace', return_value=source):
                recover('owned-linux-directory', target)
            self.assertEqual((target/'reference-stderr.txt').read_text(), 'solver failed: retained diagnostic')
            self.assertEqual((target/'features.csv').read_text(), 'real features')
            self.assertFalse((target/'frames.csv').exists())
            self.assertFalse((target/'reference-states.csv').exists())
            self.assertEqual(len(RESULTS), 5)

    def test_workspace_rejects_unowned_paths_and_symlink_results(self):
        from vio_workspace import workspace, recover
        for value in ('/root', '/root/gaittrace-vio/jobs/replay-test/../other', '/tmp/replay-123'):
            with self.assertRaises(ValueError):workspace(value)
        with patch('vio_workspace.workspace', return_value=Path('owned')), \
                patch('vio_workspace.Path.is_dir', return_value=True), \
                patch('vio_workspace.Path.is_symlink', return_value=True):
            with self.assertRaisesRegex(ValueError, 'symlink'):recover('owned', 'target')

    def test_cpu_wheel_cannot_claim_gpu_and_no_silent_fallback(self):
        with patch('vio_reference.cv2.cuda.getCudaEnabledDeviceCount', return_value=0):
            with self.assertRaisesRegex(RuntimeError, 'CUDA device unavailable'):
                cuda_probe()
            with self.assertRaises(RuntimeError):
                export_feature_tracks('does-not-exist', backend='cuda')

    def test_cpu_selection_is_explicit_and_never_probes_gpu(self):
        with patch.dict(os.environ, {'GAITTRACE_VIO_BACKEND': 'cpu'}), patch('vio_compute.subprocess.run') as run:
            self.assertEqual(backend(), 'cpu')
            self.assertFalse(probe_compute()['gpuUsed'])
            run.assert_not_called()
        with patch.dict(os.environ, {'GAITTRACE_VIO_BACKEND': 'invalid'}):
            with self.assertRaises(ValueError):
                backend()

    def test_missing_kernel_evidence_cannot_pass_preflight(self):
        with patch.dict(os.environ, {'GAITTRACE_VIO_BACKEND': 'cuda'}), patch('vio_compute.worker_request',
                return_value={'backend':'cuda','kernelCheckPassed':True}):
            with self.assertRaisesRegex(ValueError, 'not verified'):
                probe_compute()

    def test_old_image_is_rebuilt_from_current_recipe_before_probe(self):
        import contextlib, io, subprocess
        with patch.dict(os.environ, {'GAITTRACE_VIO_BACKEND': 'cuda'}), patch('vio_compute.subprocess.run',
                return_value=subprocess.CompletedProcess([], 0, stdout='old-recipe')) as run, \
                patch('vio_compute.probe_compute', return_value={'kernelCheckPassed': True}), contextlib.redirect_stdout(io.StringIO()):
            setup_compute()
            commands = [c.args[0] for c in run.call_args_list]
            self.assertEqual(len(commands), 2)
            self.assertIn('--build-arg', commands[1])
            self.assertTrue(any(c.startswith('GAITTRACE_RECIPE_SHA256=') for c in commands[1]))

    def test_gpu_timeout_stops_only_its_named_worker(self):
        import subprocess, queue
        worker = CudaWorker.__new__(CudaWorker)
        worker.name='gaittrace-vio-worker-owned';worker.closed=False
        worker.lock=__import__('threading').Lock();worker.responses=MagicMock()
        worker.responses.get.side_effect=queue.Empty
        worker.process=MagicMock();worker.process.poll.return_value=None
        worker.process.wait.side_effect=subprocess.TimeoutExpired([], 5)
        worker.log=MagicMock()
        with patch('vio_compute.subprocess.run') as run:
            with self.assertRaisesRegex(TimeoutError, 'processing budget'):
                worker.request({'command':'probe'}, timeout=.01)
            self.assertEqual(run.call_args.args[0][-1], worker.name)
            self.assertTrue(worker.closed)

    def test_unsafe_workspace_never_reaches_gpu_worker(self):
        with patch('vio_compute.worker_request') as run:
            with self.assertRaises(ValueError):
                cuda_features('/root/gaittrace-vio/jobs/replay-test/../other')
            run.assert_not_called()

    def test_frame_clocks_and_known_translation_cpu_and_opt_in_cuda(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            image = np.random.default_rng(3).integers(0, 256, (160, 200), dtype=np.uint8)
            (folder/'profile.json').write_text(json.dumps({'lens': {
                'cameraMatrix': [[180, 0, 100], [0, 180, 80], [0, 0, 1]], 'distortion': [0]*5}}))
            times = [1000000000, 1033000000, 1071000000]
            with (folder/'frames.csv').open('w', newline='') as f:
                w = csv.writer(f);w.writerow(['timestamp_ns', 'file'])
                for i, t in enumerate(times):
                    name = str(i)+'.jpg'
                    cv2.imwrite(str(folder/name), cv2.warpAffine(image, np.float32([[1, 0, i*2], [0, 1, 0]]), (200, 160)))
                    w.writerow([t, name])
            modes = ['cpu', 'cuda'] if os.environ.get('GAITTRACE_RUN_CUDA_CHECKS') == '1' else ['cpu']
            for mode in modes:
                with self.subTest(backend=mode):
                    summary = export_feature_tracks(folder, backend=mode)
                    self.assertEqual(summary['gpuUsed'], mode == 'cuda')
                    self.assertEqual(summary['cudaLKCalls'], 4 if mode == 'cuda' else 0)
                    self.assertFalse(summary['distanceReady'])
                    with (folder/'features.csv').open() as f:
                        rows = list(csv.DictReader(f))
                    self.assertEqual(sorted(set(int(r['timestamp_ns']) for r in rows)), times)
                    velocities = [float(r['vx']) for r in rows if int(r['timestamp_ns']) == times[1] and float(r['vx']) != 0]
                    self.assertGreater(len(velocities), 8)
                    self.assertAlmostEqual(float(np.median(velocities)), (2/180)/.033, delta=.02)


if __name__ == '__main__':
    unittest.main()
