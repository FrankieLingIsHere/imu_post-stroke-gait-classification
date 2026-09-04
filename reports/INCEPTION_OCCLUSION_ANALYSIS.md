# Inception channel-occlusion analysis

The selected source-balanced Inception model was re-exported from the existing robust-training notebook with fold-0 normalization statistics. Occlusion was then applied to the fold-0 held-out participants only. One channel at a time was replaced by its normalized training mean; the reported effect is the change in predicted stroke probability.

| Channel | Mean absolute probability change | Mean signed change |
|---|---:|---:|
| Lower back (LB) | **0.188** | **+0.130** |
| Right foot (RF) | 0.104 | −0.039 |
| Left foot (LF) | 0.090 | +0.028 |

## Interpretation

The fold-0 model is most sensitive to the lower-back channel under this occlusion test. Removing lower-back information generally reduces stroke probability, while right-foot removal has a smaller opposite-signed effect. This supports lower-back information as an important model input, but it does not establish clinical specificity or rule out speed/protocol confounding.

This is a channel-level result only. Temporal occlusion and cross-fold aggregation remain required before making a stronger attribution claim.

Output: `data/processed/inception_channel_occlusion_windows.csv`.
