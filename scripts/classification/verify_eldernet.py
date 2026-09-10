"""Verify the pinned gait-speed checkpoint on its wrist reproduction fixture.

Copyright 2022, University of Oxford. Upstream ElderNet/SSL-wearables code and
weights retain the academic-use license bundled in the pinned source directory.
This verifies inference, not stroke discrimination or independent generalization.
"""
from pathlib import Path
import sys
import json
import hashlib
import importlib.metadata

ROOT = Path(__file__).resolve().parents[2]
UPSTREAM = ROOT / 'models/pretrained/eldernet-437a38b'
sys.path.insert(0, str(UPSTREAM))
import numpy as np
import pandas as pd
import torch
import yaml
from gait_quality.io import read_recording
from gait_quality.preprocessing import preprocess
from gait_quality.weights import build_model, load_weights
from gait_quality.detection import run_batch


def main():
    out = ROOT / 'data/processed/eldernet_compatibility_v1'
    out.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((UPSTREAM / 'acquisition.json').read_text())
    for f in manifest['files']:
        p = UPSTREAM / f['path']
        assert hashlib.sha256(p.read_bytes()).hexdigest() == f['sha256'], p
    torch.set_num_threads(4)
    cfg = yaml.safe_load((UPSTREAM / 'pipelines/config.yaml').read_text())
    model_cfg = cfg['models']['gait_speed'].copy()
    weight_path = UPSTREAM / model_cfg['trained_model_path']
    model_cfg['trained_model_path'] = str(weight_path)
    model = build_model(model_cfg, device='cpu')
    loading = load_weights(weight_path, model, device='cpu')
    recording = read_recording(UPSTREAM / 'examples/toy_wrist.csv.gz', fs=100)
    processed = preprocess(recording, cfg['pipeline'], detect_nonwear=False,
                           drop_first_last_days=False)
    expected = pd.read_csv(UPSTREAM / 'examples/expected/toy_wrist_windows.csv')
    acc = processed[['x', 'y', 'z']].to_numpy()
    starts = expected.start_sample.to_numpy(int)
    windows = np.stack([acc[i:i+300] for i in starts])
    assert windows.shape == (len(expected), 300, 3)
    assert np.isfinite(windows).all()
    predicted = np.concatenate([run_batch(windows[i:i+32], model, 'cpu')
                                for i in range(0, len(windows), 32)])
    errors = np.abs(predicted - expected.gait_speed_m_s.to_numpy())
    passed = bool(np.allclose(predicted, expected.gait_speed_m_s, rtol=1e-4, atol=1e-4))
    pd.DataFrame(dict(start_sample=starts, predicted_speed_m_s=predicted,
                     upstream_expected_speed_m_s=expected.gait_speed_m_s,
                     absolute_difference=errors)).to_csv(out / 'fixture_predictions.csv', index=False)
    result = dict(checkpoint_loaded=True, matched_keys=len(loading['matched']),
                  missing_keys=loading['missing'], unused_keys=loading['unused'],
                  windows=len(windows), participant='PD4010', placement='left wrist',
                  max_absolute_difference=float(errors.max()), reproduction_passed=passed,
                  calibration_ok=processed.attrs.get('calibration_ok', processed.attrs.get('CalibOK')),
                  window_selection='upstream expected walking windows; detection not rerun',
                  independent_validation=False, stroke_evaluation=False,
                  upstream_commit=manifest['commit'],
                  versions={n: importlib.metadata.version(n) for n in ['torch','numpy','pandas','scipy','actipy']})
    (out / 'verification.json').write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    if not passed:
        raise RuntimeError('Upstream gait-speed prediction reproduction failed')


if __name__ == '__main__':
    main()
