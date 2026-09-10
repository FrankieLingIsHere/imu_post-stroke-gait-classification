# TVS preprocessing integration

Scope fixed before inference: engineering smoke test on the two previously
opened schema-development participants. No thresholds, calibration, training,
classification accuracy or clinical specificity estimates. No untouched cohort
is opened. The existing v0.2.0 checkpoint and normalization stay fixed.

The adapter selects the last trial of Test5/6/7/10 (comfortable/slow/fast/hallway)
when present, and uses only Stereophoto ContinuousWalkingPeriod intervals. There
is no fallback to a different reference or earlier trial to increase yield.
MATLAB indexing follows the archived official mobgap loader: start is rounded
seconds times 100 minus one; end is rounded seconds times 100, Python-exclusive.

Native g-valued lower-back acceleration is converted to Euclidean magnitude
without gravity subtraction or extra filtering/normalization. The fixed input
is float32 (windows, 500, 1) at 100 Hz, with 250-sample hop. Windows never cross
bout boundaries or reference breaks, and short bouts are not padded or joined.
Invalid rates, timestamps, array values, overlapping bouts and out-of-bounds
references raise errors.

Actual output: **10 windows, 3 HA and 7 PD**. Healthy comfortable and slow trials
are too short; its fast trial has no reference bouts. Its three windows come
from hallway walking. PD contributes comfortable/slow/fast windows and has no
Test10. This task imbalance alone precludes a useful group comparison here.
Turn annotations are incomplete, so these are reference walking windows, not
verified straight-walking windows. Full quality/participant metadata eligibility
remains unresolved before a larger specificity study.

Five focused tests passed: MATLAB endpoints/exact five-second boundary, separate
short bouts, timestamp gaps/nonfinite acceleration, invalid bounds/missing
references, and break-crossing exclusion. Local prepared arrays, per-window
provenance and exclusions are under
`data/interim/public_imu_screen_2026-09-08/prepared/`.

Reproduce preprocessing and tests:

```powershell
& C:/Users/frank/.venv-cu130/Scripts/python.exe -m unittest discover -s tests -p test_tvs.py
& C:/Users/frank/.venv-cu130/Scripts/python.exe scripts/prepare_tvs_schema_windows.py
```

Input NPY SHA-256:
`91d4ab8ddd74b8560e47f6afa48208be3b5576d164e0a12be334fa3460189ee2`.

## Executed inference result

The checksum-verified v0.2.0 release passed its saved smoke prediction test
(absolute tolerance 1e-6), then returned ten finite probabilities in [0,1] for
the ten real TVS windows. `prepared/integration_smoke.json` records the input
and checkpoint hashes and outputs. This verifies the raw-file-to-model path;
it is not an estimate of diagnostic performance. Weights were not changed.
