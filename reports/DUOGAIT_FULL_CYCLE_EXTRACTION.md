# DUO-GAIT full-cycle extraction

DUO-GAIT cycles were extracted from the official processed left-foot initial-contact samples, while synchronized raw `SA/LF/RF` acceleration signals supplied the waveform. Only clean stride intervals within a physiological duration range were retained. The event source is recorded in the metadata; no arbitrary windows or guessed events were used.

Outputs: `data/processed/duogait_full_gait_cycles_float32.npy` and `duogait_full_gait_cycle_metadata.csv`.
