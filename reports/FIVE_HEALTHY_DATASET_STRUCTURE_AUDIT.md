# Five external healthy-dataset structure audit

## Result

The five sources do **not** all structurally match the Voisard/Felius training contract. They may still be useful, but they must not be pooled as if they were equivalent.

| Source | Healthy signal structure observed | Canonical 3-channel feasibility | Current decision |
|---|---|---|---|
| GaitMotion | Separate Normal/Stroke directories; paired left/right files; sequence lengths and task IDs vary; release is multimodal pathological-gait data | Not yet demonstrated for lower-back + bilateral feet; pickle compatibility also requires the release environment | Audit/adapter required; do not pool yet |
| DUO-GAIT | Author-segmented files include LF and sacrum/SA; control release has multiple placements but the selected OG control subset is not a guaranteed LB/LF/RF triplet | Partial; sacrum can be a trunk proxy, but right-foot completeness must be verified per recording | Healthy-domain or conditional inclusion after completeness gate |
| OxWalk | Healthy walking data with hip/wrist-oriented placements and coarse age metadata | No direct LB/LF/RF equivalence | Do not synthesize canonical LB/RF/LF from it; use separate domain/age validation |
| MAREA | Healthy multi-sensor activity data; Waist/LF/RF subset was previously mapped into the project window contract | Feasible for the mapped subset, subject to source-specific preprocessing and protocol metadata | Candidate for canonical healthy augmentation |
| Camargo | Healthy locomotion data with a separate source structure and sensor/task conventions | Not demonstrated as a complete LB/LF/RF triplet | Adapter audit required; separate until verified |

## Required gate before synthesis

For each source, verify at recording level: body location, left/right identity, axes, sampling rate, units, synchronization, contiguous walking duration, and whether all three canonical channels exist for the same participant and trial. Only complete recordings may enter canonical synthesis.

Resampling to 100 Hz and windowing to 500 samples are format operations, not evidence that the body locations or biomechanics match. A missing lower-back or foot signal must not be reconstructed by copying, reshaping, or assigning another location as an equivalent channel.

## Correct synthetic-data scope

The first synthetic generator should use only verified canonical windows from the five external sources, with source and parent-participant provenance retained. Sources that fail the canonical gate remain valuable as separate healthy-domain evaluation, self-supervised pretraining, or a future cross-sensor translation study; they are not silently discarded.

The incorrectly generated Voisard/Felius-only synthetic artifact is quarantined under `data/processed/archive_invalid_synthesis_2026-09-01/` and is excluded from this audit.
