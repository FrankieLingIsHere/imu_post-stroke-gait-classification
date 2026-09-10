# ElderNet: checkpoint execution and transfer applicability

> Latest: [feature fusion](ELDERNET_FUSION_RESULT.md) has now also been tested
> and failed. Earlier statements below that fusion is unexecuted are historical.

> Subsequent execution: the [lower-back frozen-encoder probe](ELDERNET_LOWER_BACK_RESULT.md)
> is now complete and failed both comparison gates. The unexecuted-transfer
> statements below describe the earlier wrist compatibility stage. End-to-end
> fine-tuning and cross-source validation remain unexecuted.

> Later follow-up: [partial late-layer adaptation](ELDERNET_PARTIAL_RESULT.md)
> has also completed, without meeting the replacement criteria. Full end-to-end
> unfreezing and feature fusion remain unexecuted.

Executed 2026-09-09. The gait-speed checkpoint runs locally and reproduces its
upstream wrist example. This is a completed compatibility/reproduction check,
not a stroke experiment or evidence that transfer improves false positives.

## Verified artifacts and execution

Pinned upstream [yonbrand/gait-quality](https://github.com/yonbrand/gait-quality/tree/437a38bcc69f42717fe73c1f7dbea7e1f7a50d23)
at commit `437a38bcc69f42717fe73c1f7dbea7e1f7a50d23` under
`models/pretrained/eldernet-437a38b/`. Downloaded 45 source/configuration/attribution
and fixture files including **one** gait-speed checkpoint, 46,218,839 bytes total.
The checkpoint itself is 44,734,819 bytes. No other gait checkpoints or whole
datasets were downloaded. Acquisition manifest records every file's SHA256.

Copyright 2022, University of Oxford. Upstream code/weights retain the bundled
academic-use license (`LICENSE.md`). The small TVS fixture retains its CC BY 4.0
attribution in `examples/README.md`: Del Din et al., Mobilise-D TVS V1.0.2,
DOI 10.5281/zenodo.15861907. Internal research use only under the model license.

Used existing `C:/Users/frank/.venv-cu130/Scripts/python.exe`; installed actipy
3.7.0 and PyYAML 6.0.3. No replacement of existing numerical packages.

- 139 model state keys matched, no required parameters missing.
- Two legacy variance-head keys are unused by the upstream mean-speed model:
  `regressor.var.bias` and `regressor.var.weight`. No random prediction layers.
- Real fixture: PD4010, left wrist, 78,000 samples at 100 Hz, supplied in g.
- Upstream preprocessing resampled to 30 Hz, 300 samples per 10-second window.
- All **416 upstream-selected walking windows** evaluated on CPU.
- Maximum absolute speed difference from upstream output: **3.234889220937731e-7 m/s**.
- All outputs pass upstream `rtol=1e-4, atol=1e-4` tolerance.
- Walking detection was **not** rerun: expected window locations were supplied.
- Calibration status remains `CalibOK=0`, as documented for this short fixture
  lacking stationary orientations. Factory calibration is described upstream;
  the run does not establish independent sensor calibration.

Predictions, versions and load diagnostics are saved in
`data/processed/eldernet_compatibility_v1/`. Reproduce:

```powershell
& C:/Users/frank/.venv-cu130/Scripts/python.exe scripts/classification/verify_eldernet.py
```

## Applicability decision

The pinned README explicitly identifies the model as **wrist-worn**, using
gravity-calibrated three-axis acceleration in g, and fine-tuned on Mobilise-D TVS.
It warns that lower-back inputs are outside its intended distribution. Our main
stroke model takes lower-back magnitude. Do not replicate magnitude across three
channels or interpret this pretrained head's lower-back output as gait speed.

TVS is not automatically an independent evaluation set for this checkpoint.
Upstream also explains that public participant identities were changed and the
old mapping destroyed. We have not established which local participants were
excluded from checkpoint training. The fixture run is reproduction only.

**Encoder transfer is technically plausible but not yet trained or evaluated.**
Voisard has genuine three-axis lower-back recordings, so a new lower-back input
contract could support an explicitly out-of-domain transfer experiment. It would
need complete 10-second gait-window coverage, training-only adaptation, matched
random-initialization controls and subject/pathology holdouts. Cross-source
performance additionally requires compatible three-axis data in each source.
That experiment must not be described as using a validated wrist gait-speed head.

GaitEncoder remains unsuitable for direct raw-IMU input, as already documented in
the prior hypothesis review. Oxford Stepcount is also a wrist walking/step model;
no additional checkpoint was acquired for that adjacent task.

Current status: upstream model/source acquisition complete for one checkpoint;
fixture raw acquisition and preprocessing complete; inference reproduction passed;
stroke fine-tuning, cross-source transfer and independent clinical evaluation
**not performed**. Existing deep-learning ensemble and phase+HR prototype unchanged.
