# MAREA versus DUO-GAIT full-cycle comparison

This comparison is performed before pooling the two healthy sources in a generator. It retains source identity and checks whether format compatibility also corresponds to similar signal distributions.

Run: `python scripts/compare_marea_duogait_cycles.py`.

## Initial result

The first comparison exposed a unit mismatch: MAREA magnitudes are approximately in `m/s²`, while DUO-GAIT raw accelerometer values are in `g`. DUO-GAIT therefore appeared about 9.5 times smaller (`mean 1.480` versus MAREA `14.010`). This is a preprocessing issue, not evidence that the sources are biomechanically incompatible. DUO-GAIT must be multiplied by standard gravity before any pooling or generator training, then re-audited.
