# Selected baseline configuration

- Primary model: source-balanced global-normalization Inception-style CNN.
- Training sources: Felius and Voisard only.
- Input: 5-second windows, three acceleration magnitudes ordered `LB, LF, RF`.
- Split: fixed participant-disjoint folds.
- Normalization: statistics fitted inside each training fold.
- Evaluation unit: participant, by aggregating window probabilities.
- External test: RevalExo, frozen and excluded from all fitting decisions.
- Zenodo: not part of the primary probability.

The project currently has fold checkpoints for compact CNN experiments, but not a separately packaged full-data Inception checkpoint. The reproducible source of truth remains `notebooks/08_robust_pooled_training.ipynb` and its processed prediction/metric artifacts; a final deployment checkpoint should be exported only after the intended operating threshold and calibration protocol are formally specified.
