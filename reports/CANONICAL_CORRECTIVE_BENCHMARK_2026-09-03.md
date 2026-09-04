# Canonical corrective benchmark

Date: 2026-09-03  
Evidence notebook: `notebooks/34_canonical_inceptiontime_minirocket_corrective_benchmark.ipynb`

## Decision

**No candidate produced a reliable improvement.** The notebook-29 lower-back
ensemble remains selected, and architecture rotation on the existing 314
development participants now stops.

This was a five-seed, participant-level leave-one-source-out comparison over
Felius, Voisard, and Sint. RevalExo and NONAN were not loaded. The replacement
gate required both mean false positives and false negatives to decrease, at
least 10% fewer total errors, paired-bootstrap support, no mean total-error
increase in any held-out source, and non-inferior discrimination and
calibration. None of the two models or three fixed fusions passed.

## Overall participant-level results

Values are means over 15 matched held-out-source/seed evaluations.

| Method | AUROC | Brier | Balanced accuracy | Specificity | Sensitivity | FP | FN | Total errors |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **Notebook-29 incumbent** | **0.8882** | **0.1425** | 0.8140 | **0.7743** | 0.8537 | 9.80 | **11.93** | **21.73** |
| Incumbent + MiniROCKET | 0.8869 | 0.1427 | **0.8145** | 0.7733 | **0.8557** | **9.33** | 12.80 | 22.13 |
| Canonical 10k MiniROCKET | 0.8572 | 0.1582 | 0.8029 | 0.7710 | 0.8348 | 9.40 | 13.87 | 23.27 |
| Incumbent + both candidates | 0.8860 | 0.1599 | 0.7954 | 0.7471 | 0.8437 | 10.20 | 14.67 | 24.87 |
| Incumbent + InceptionTime | 0.8857 | 0.1713 | 0.7834 | 0.7479 | 0.8190 | 10.47 | 15.73 | 26.20 |
| InceptionTime canonical mechanics | 0.8273 | 0.2360 | 0.7418 | 0.6939 | 0.7897 | 13.07 | 19.07 | 32.13 |

The closest candidate was the fixed incumbent + MiniROCKET fusion. It reduced
mean FP by 0.47 but increased mean FN by 0.87, increased total errors by 0.40,
slightly reduced AUROC, and slightly worsened Brier score. Its total-error
delta 95% paired-bootstrap interval was -1.60 to +2.53; this does not establish
improvement.

## Population/source result for the closest candidate

| Held-out source | Incumbent total errors | Fusion total errors | Error delta | Balanced-accuracy delta | Specificity delta | Sensitivity delta |
|---|---:|---:|---:|---:|---:|---:|
| Felius | 38.60 | 41.60 | +3.00 | -0.0073 | +0.0118 | -0.0264 |
| Sint | 5.20 | 5.80 | +0.60 | -0.0100 | -0.0400 | +0.0200 |
| Voisard | 21.40 | 19.00 | -2.40 | +0.0186 | +0.0250 | +0.0122 |

MiniROCKET was complementary on Voisard, where both error burden and balanced
accuracy improved. That gain did not transport: it increased Felius false
negatives and reduced Sint specificity. Pooling those outcomes into one average
would hide a clinically important population trade-off, so the fusion is not
admitted.

## Implementation fidelity and boundaries

- InceptionTime used six Inception modules, 40/20/10 kernels, 32 filters per
  branch, bottlenecks, residual shortcuts after modules 3 and 6, global average
  pooling, Adam, and training-only normalization. Inner validation selected 8,
  24, and 16 epochs for the Felius, Sint, and Voisard holdouts respectively.
  This is the audited architecture translated to PyTorch under the project
  training protocol; it is not the original 1,500-epoch five-network paper
  ensemble.
- MiniROCKET requested 10,000 kernels (9,996 realized, as the implementation
  rounds to a multiple of 84), used 32 maximum dilations,
  `StandardScaler(with_mean=False)`, logarithmic RidgeClassifierCV alphas, and
  training-only participant-grouped Platt calibration. Bias windows were
  source/class and participant balanced.
- InceptionTime ran on the NVIDIA RTX 5060 Laptop GPU with mixed precision.
  MiniROCKET used the canonical CPU/Numba implementation with 16 workers.
- The source arrays, incumbent prediction file, software versions, upstream
  commits, seeds, and gate are recorded in
  `data/processed/canonical_corrective_decision.json`.

## Interpretation and stop rule

The negative result is not evidence that every imaginable InceptionTime
training schedule or every MiniROCKET adaptation must fail. It is evidence that
the predeclared canonical-mechanics corrections do not replace the incumbent
under the project's leakage-safe cross-source clinical criteria. Continuing to
tune architectures against the same 314 people would increase adaptive
overfitting risk.

The next work should therefore freeze/package the notebook-29 model and seek a
new untouched paired lower-back IMU cohort with healthy, stroke, and relevant
non-stroke gait variation. Existing frozen cohorts remain evaluation-only and
must not be recycled for another selection round.
