---
type: concept
status: active
updated: 2026-09-03
---

# Prior-method code alignment

Executed notebook `33_prior_method_code_alignment_audit.ipynb` compared the
project's model-improvement code with fixed commits of official InceptionTime,
MiniROCKET, HAROOD, ERM++, AttentionDeepMIL, GroupDRO, HAR-Bench, and IMUEval
repositories, plus the published IMUDiffusion specification. No frozen signal
was loaded.

## Main correction

Most previous negative results reject a specific local approximation, not the
named research family:

- The release CNN has two compact Inception-style modules; official
  InceptionTime uses six modules, residuals every three modules, approximately
  40/20/10 kernels, 32 filters, and a five-network ensemble.
- Historical MiniROCKET uses 2,000 features, 16 dilations, and fixed Ridge or
  logistic heads. The canonical 10,000-feature, 32-dilation, scaled RidgeCV
  configuration has not been tested on the lower-back three-source contract.
- The CORAL mean-plus-covariance objective closely matches HAROOD and remains a
  valid local result, although its penalty weight was fixed.
- The ERM++-style member includes head warm-up, weight decay, and SMA but lacks
  ERM++ pretrained initialization and its complete validation/full-data
  retraining procedure.
- The previous GroupDRO run assigned adversarial weights to source×class cells,
  whereas HAROOD assigns them to source-domain minibatches. It was also a
  single fixed-duration seed.
- The attention MIL operator matches official gated attention, but participant
  gait bags are a project-specific adaptation of the MIL assumption.
- Local healthy DDPMs use time-domain magnitude, 100–200 steps, roughly 80–100
  epochs, and no self-attention. IMUDiffusion uses STFT representations, 3,000
  steps, 4,500 epochs, ResNet/self-attention blocks, separate sensor schedules,
  and activity-specific generators. The local failures cannot reject
  IMUDiffusion.
- The normalization comparison is not HAR-Bench instance normalization. Its
  RevalExo rows are descriptive only because that script repeatedly loads the
  frozen cohort.

## Protected finding

The [[evidence-gated-model-improvement|selected lower-back ensemble]] remains
the incumbent because its own three-source, five-seed held-out-source result is
valid. It must be described as a compact Inception-style ERM + HAROOD-style
CORAL + ERM++-style ensemble, not as a faithful reproduction of all upstream
methods.

## Completed corrective benchmark

Executed notebook `34_canonical_inceptiontime_minirocket_corrective_benchmark.ipynb`
completed the one authorized comparison against the unchanged incumbent. It
used notebook 29's participant-safe inner validation, three complete source
holdouts, five seeds, and training-only preprocessing. RevalExo, NONAN,
synthesis, MIL, GroupDRO, and threshold search were excluded.

No candidate passed. InceptionTime canonical mechanics increased mean total
errors from 21.73 to 32.13. Canonical 10k MiniROCKET increased them to 23.27.
The closest incumbent/MiniROCKET fusion reduced FP from 9.80 to 9.33 but
increased FN from 11.93 to 12.80 and total errors to 22.13. It helped Voisard
but regressed Felius and Sint. Architecture rotation stops and new paired-cohort
evaluation is now the next requirement. See
`../../reports/CANONICAL_CORRECTIVE_BENCHMARK_2026-09-03.md`.

Full report:
`../../reports/PRIOR_METHOD_CODE_ALIGNMENT_AUDIT_2026-09-03.md`.
