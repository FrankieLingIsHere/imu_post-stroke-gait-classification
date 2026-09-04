# MAREA recombined synthetic healthy trial

## Classifier ablation result

The corrected ablation grouped synthetic windows by their real MAREA parent participants: 314 real participants versus 334 effective participants after adding 705 synthetic windows. On frozen RevalExo, AUROC stayed at `0.914`, while Brier worsened from `0.161` to `0.172` and balanced accuracy worsened from `0.714` to `0.643`. Decision: reject this recombination method for final training. An earlier run that treated each synthetic ID as a new participant was invalid and discarded.

The first interpolation artifact reduced variance and spectral energy. This control recombines two real MAREA windows at a random interior cut with a 20-sample cross-fade. It preserves real amplitude segments and the exact canonical `500 × 3` contract. The artifact remains excluded from classifier training until the quality gate and frozen-external ablation pass.
