# MiniROCKET calibration

Calibration was fitted using an inner participant subset from each outer training fold. Outer validation participants were not used to fit the calibrator.

| Metric | Mean across five outer folds |
|---|---:|
| Raw AUROC | 0.9713 |
| Calibrated AUROC | 0.9673 |
| Calibrated Brier score | 0.0603 |
| Calibrated ECE-10 | 0.0857 |

Calibration slightly reduced AUROC, as expected when transforming scores, while producing usable probability estimates. These results are internal only and do not replace the frozen RevalExo evaluation.

Artifacts: `data/processed/minirocket_ridge_fold_*_seed_42_calibrated.joblib`, predictions in `data/processed/minirocket_calibrated_oof_participant_predictions.csv`, and fold summary in `data/processed/minirocket_calibration_summary.csv`.
