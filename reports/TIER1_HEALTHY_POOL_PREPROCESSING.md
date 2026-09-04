# Tier 1 healthy-pool preprocessing

The first supervised healthy enrichment pool was materialized from MAREA and DUO-GAIT only. MAREA uses matched Waist/LF/RF recordings, converts m/s² to g, uses walking timing segments, resamples 128 Hz to 100 Hz, and creates 5-second windows with a 2.5-second hop. DUO-GAIT uses author-segmented `OG_st_control` walking segments, uses SA/LF/RF, resamples 128 Hz to 100 Hz, and creates the same windows.

Dataset, participant, and trial metadata are retained. Camargo, GaitMotion, and OxWalk remain outside supervised pooling because their channel layouts do not provide the same validated three-sensor semantics.

Outputs: `data/processed/tier1_healthy_marea_duogait_windows_float32.npy` and `data/processed/tier1_healthy_marea_duogait_window_metadata.csv`.
