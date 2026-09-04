# DUO-GAIT cycle-event audit

The DUO-GAIT `OG_st_control` source contains complete same-participant `SA/LF/RF` CSV signals. The trajectory JSON files contain `time`, position, velocity, and rotation fields sampled at approximately 128 Hz, but no explicit heel-strike or toe-off fields were found in the inspected files.

Decision: DUO-GAIT is a canonical-channel candidate, but not yet a verified full-cycle source. The next adapter must detect candidate events from the foot signals or recover the dataset's event-generation procedure, then validate cycle duration, bilateral timing, and interruption handling. Until then, DUO-GAIT may not enter the full-cycle generator.
