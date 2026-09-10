# TVS cohort-wide hallway result

**Completed 2026-09-08 at 23:52 Malaysia time; independently verified 2026-09-09.**
All 30 additional raw-file acquisitions completed. The fixed queue accounted for
all 40 registered HA/PD participants: 34 evaluated, five metadata exclusions and
one short-bout exclusion. No transfer failures remain and no cohort process is
running. Evaluation used 117 windows, unchanged v0.2.0 and threshold 0.50.

| Group | Newly opened: positive / evaluated | Previously inspected | Combined |
|---|---:|---:|---:|
| Healthy | 14/15 (93.3%) | 3/3 | 17/18 (94.4%) |
| Parkinson's | 14/14 (100%) | 2/2 | 16/16 (100%) |

For newly opened participants, positive-call Wilson 95% intervals are 70.2%-98.8%
for healthy and 78.5%-100% for PD. Combined intervals are 74.2%-99.0% and
80.6%-100%, respectively. These are descriptive intervals; the hallway task was
chosen after pilot inspection. Possible turns remain unannotated, age/site
matching is unverified and there is no stroke group. No sensitivity, diagnostic
AUROC or clinical calibration claim is supported.

The larger result confirms that the healthy failure was not confined to the
initial two participants. **The frozen model is unsuitable for the evaluated TVS
hallway use.** Healthy specificity in this sample is only 1/18 (5.6%). This is
evaluation progress, not improved model performance. It strengthens the evidence
of poor transfer but does not isolate the causal feature or acquisition factor.
See the [mechanism probes](TVS_POSITIVE_CALL_MECHANISM_2026-09-08.md).

## Accounting and verification

Metadata exclusions: HA/1093 (task annotation); PD/3006 (missing lower-back and
reference availability); PD/4012 and PD/4014 (task annotations); PD/4020 (missing
task signals/reference and walking aid/unknown). HA/3107 passed metadata but its
reference interval contained only 487 samples (4.87 seconds), so no full window
was available. No replacement or padding occurred.

Thirty new raw files total 1,258,819,511 bytes. There are now 36 acquired HA/PD
laboratory raw participants, including the original six; four unacquired raw
files belong to people excluded by the fixed metadata rules. All 40 metadata
records are local. The full six-group archive collection was not downloaded.

Independent verification checked all 30 new raw CRCs, sizes and SHA-256 values;
the protocol and locked dependency hashes; all evaluated raw/window hashes,
window shapes and finite values; saved score means, calls and participant/group
accounting. Earlier pilot results remain unchanged. No inference was rerun.

Artifacts under `data/interim/public_imu_screen_2026-09-08/cohort_hallway_v1/`:
`results.json`, `intake.json`, `protocol.json`, raw manifests, prepared windows
and `verification.json`. Result SHA-256:
`bea99bd274f79b4303e99cb682fc1d53bb98b9e04fea15d6e636d50d1bd2f813`.

## Next decision

Acquisition and cohort scoring are closed. Do not download or repeat this cohort
as the next task. No model correction has yet passed validation. Any new proposal
must address the demonstrated transfer/specificity problem and be evaluated
against stroke sensitivity on separate development validation, with these now
inspected TVS results kept distinct from untouched test evidence. The constant-
signal failure motivates an input-validity guard, but such a guard alone would
not solve the observed errors on moving healthy participants.
