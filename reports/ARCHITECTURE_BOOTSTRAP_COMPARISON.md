# Participant-bootstrap architecture comparison

The existing participant-level predictions were compared with 5,000 stratified bootstrap replicates per dataset. Each replicate resampled participants within dataset with replacement. The 0.5 threshold is descriptive for balanced accuracy; AUROC does not depend on that threshold.

## Difference from Inception CNN

| Dataset | Comparison | AUROC difference, mean [95% CI] | Balanced-accuracy difference, mean [95% CI] |
|---|---|---:|---:|
| Felius | Compact CNN − Inception | −0.008 [−0.049, 0.038] | −0.016 [−0.065, 0.036] |
| Felius | MiniROCKET − Inception | **+0.026 [−0.002, 0.059]** | **+0.058 [+0.000, 0.115]** |
| Voisard | Compact CNN − Inception | −0.007 [−0.036, 0.017] | −0.038 [−0.102, 0.024] |
| Voisard | MiniROCKET − Inception | −0.002 [−0.027, 0.022] | **+0.065 [+0.009, 0.125]** |

## Interpretation

1. Compact CNN and Inception CNN are practically indistinguishable within the observed uncertainty on both datasets.
2. MiniROCKET has a credible balanced-accuracy advantage over Inception in both datasets at the descriptive 0.5 threshold.
3. MiniROCKET's AUROC advantage is clearer in Felius but its confidence interval narrowly includes zero; in Voisard, AUROC is equivalent to Inception while balanced accuracy is higher.
4. MiniROCKET should be retained as the leading non-deep candidate and co-primary model, but this is not evidence of clinical superiority or speed independence.

## Protected decision

The pooled Inception development contract remains unchanged. The next model-selection gate should compare MiniROCKET and Inception on calibration, the frozen RevalExo test, and attribution/error patterns before any final replacement decision.

Raw bootstrap output: `data/processed/architecture_bootstrap_summary.csv` and `data/processed/architecture_bootstrap_comparison.csv`.
