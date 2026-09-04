# Attribution audit status

The planned Inception occlusion analysis was not completed because the available serialized checkpoints do not match the Inception CNN used in the architecture comparison.

Verified checkpoint state:

- `data/processed/cnn_magnitude_fold_*.pt` contains a compact `GaitCNN` state dictionary with `features.*` and `classifier.*` keys.
- The Inception implementation in `notebooks/08_robust_pooled_training.ipynb` uses `InceptionBlock` and `features.*` with a different internal structure.
- No serialized checkpoint containing the current Inception architecture and fold-fitted normalization metadata was found in `data/processed/`.

No attribution result was generated, and no model or finding was changed. Running the analysis against the compact checkpoint would answer a different question and would be invalid as Inception attribution.

## Required before attribution

Export the selected Inception model state for each validation fold together with its fold-fitted mean and standard deviation, then rerun channel and temporal occlusion on held-out participants only. Until then, attribution remains an unmet reproducibility item.
