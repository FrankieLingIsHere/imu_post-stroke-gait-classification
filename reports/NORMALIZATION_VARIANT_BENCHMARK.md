# Normalization variant benchmark

This benchmark compares the locked global z-score baseline with global robust median/IQR scaling under identical participant-disjoint folds, source/class-balanced sampling, architecture, seed, and GPU execution. It evaluates both the lower-back-only research track and the three-channel comparator. RevalExo is frozen and is not used to fit statistics, choose a transform, or choose a threshold.

Run with:

```powershell
python scripts/benchmark_normalization_variants.py
```

Results are written to `data/processed/normalization_variant_benchmark.csv`. Acceptance requires improvement in external calibration and healthy specificity, not AUROC alone.

## Completed result

The GPU run completed with five participant-disjoint folds and eight epochs per fold.

| Track | Normalization | External AUROC | External Brier | External balanced accuracy | Mean healthy FPs | Mean stroke FNs |
|---|---|---:|---:|---:|---:|---:|
| Lower back | Global z-score | 0.769 | 0.215 | 0.590 | 5.6 | 0.2 |
| Lower back | Robust median/IQR | 0.783 | 0.202 | 0.627 | 4.8 | 0.6 |
| Three channel | Global z-score | 0.926 | 0.173 | 0.639 | 3.8 | 1.8 |
| Three channel | Robust median/IQR | 0.911 | 0.171 | 0.666 | 4.4 | 0.4 |

Robust scaling is promising for lower-back ranking and balanced accuracy, but it is not a universal replacement: stroke false negatives increased in the lower-back track, while three-channel AUROC fell and healthy false positives increased. Global z-score therefore remains locked as the baseline. Robust scaling is retained only as a lower-back candidate for repeated-seed calibration and specificity analysis.

## Repeated-seed check

Three GPU seeds (42, 52, 62) produced the following frozen-external means ± standard deviation:

| Track | Normalization | AUROC | Balanced accuracy | Brier | Healthy FPs | Stroke FNs |
|---|---|---:|---:|---:|---:|---:|
| Lower back | Global z-score | 0.767 ± 0.058 | 0.591 ± 0.078 | 0.213 ± 0.015 | 5.53 ± 1.36 | 0.27 ± 0.59 |
| Lower back | Robust median/IQR | 0.772 ± 0.032 | 0.591 ± 0.088 | 0.214 ± 0.019 | 5.53 ± 1.36 | 0.27 ± 0.46 |
| Three channel | Global z-score | 0.917 ± 0.038 | 0.661 ± 0.060 | 0.169 ± 0.020 | 4.33 ± 1.40 | 0.60 ± 2.32 |
| Three channel | Robust median/IQR | 0.916 ± 0.034 | 0.651 ± 0.105 | 0.170 ± 0.019 | 4.80 ± 1.57 | 0.13 ± 0.35 |

The lower-back robust AUROC difference is only 0.006 and does not change balanced accuracy or false-positive mean. The result is therefore insufficient to replace the baseline. The repeated raw output is `data/processed/normalization_variant_benchmark_repeated_seeds.csv`.

## Nuisance-augmentation probe

A first mild augmentation probe (per-window gain 0.90–1.10, Gaussian noise SD 0.015, and temporal roll up to eight samples) was run on GPU with seed 42. It degraded frozen external performance: lower-back z-score AUROC was 0.751 with Brier 0.224 and 6.2 healthy false positives, while robust scaling was 0.734 with Brier 0.247 and 6.6 false positives. Three-channel z-score reached AUROC 0.917, Brier 0.163, and 5.0 false positives; robust scaling reached 0.911, 0.194, and 5.2 false positives. This augmentation recipe is rejected. The result is retained as a negative experiment in `data/processed/normalization_variant_benchmark_seed_42_augmented.csv`.
