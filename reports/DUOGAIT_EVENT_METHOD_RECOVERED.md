# DUO-GAIT event method recovered

The official DUO-GAIT repository was cloned locally under `data/raw/duogait_2023/code/`. Its README points to the TRIPOD processing pipeline. The event detector is implemented in `src/LFRF_parameters/event_detection/imu_event_detection.py` and uses the Tunca et al. method: gyroscope-magnitude stance thresholding, stance-count cleanup, selected gyroscope axis, tilt integration with bias correction, peak-prominence search regions, and IC/FO candidate selection. The released pipeline uses error-state trajectory estimation with zero-velocity updates and excludes turning, acceleration/deceleration, interrupted, and 3-SD outlier strides.

This resolves the event-method uncertainty. The next adapter task is to run the official preprocessing with DUO-GAIT's recorded thresholds and retain only clean synchronized SA/LF/RF cycles.
