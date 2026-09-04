# Lower-back versus three-channel external failure analysis

This analysis compares both models on the same 17 RevalExo participants using frozen participant-level predictions.

The paired transition table is stored in `data/processed/lower_back_vs_three_channel_external_error_analysis.csv`; the healthy/stroke summary is stored in `data/processed/lower_back_vs_three_channel_external_error_summary.csv`.

The purpose is to determine whether bilateral foot information rescues healthy participants incorrectly classified as stroke, stroke participants incorrectly classified as healthy, or both. This guides the next preprocessing and calibration experiments instead of adding training data blindly.

Decision: retain the lower-back-only model as a transparent single-sensor comparator, but retain the three-channel model as the current prototype candidate. Further lower-back-only optimization is not justified until the external error mechanism is understood.
