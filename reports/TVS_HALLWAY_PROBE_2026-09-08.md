# TVS hallway-task probe: completed

The frozen v0.2.0 model called both healthy participants and both PD participants
positive at 0.50. All four supplied valid five-second inputs. **This probe does
not support using the current classifier on these hallway recordings.** It
demonstrates an additional transfer failure, not a reduction in false positives.

## Turn compatibility and decision before scoring

The locally archived version-15861907 dataset description explicitly states:
"Neither reference system includes turning information". Source: the description
in `data/interim/public_imu_screen_2026-09-08/tvs.json`, originally from
[the versioned TVS release](https://zenodo.org/records/15861907).
Inspection of Stereophoto and INDIP fields in all four Test10/Trial1 recordings
found empty sharp-turn flags and empty break fields. Empty fields do not certify
straight walking or supply turn boundaries. A reference-based straight-only
comparison is therefore unavailable from these annotations.

Before hallway scoring, a separate protocol fixed an **exploratory hallway-task
stress test**, retaining possible turns and using the existing adapter to avoid
recorded breaks. No unvalidated gyroscope threshold was used to manufacture
turn labels. This task-level test evaluates a broader walking context; it is
not evidence of straight-walking performance or a test of turn causality.

Selection reused the same four previously inspected people, excluded both old
schema participants, and downloaded nothing. The hallway task was selected for
duration after seeing the first pilot's exclusions and one PD score. This is
explicitly adaptive exploratory evidence, not pristine independent validation.
All four have MM+ lower-back/reference metadata, no walking aid and no task
annotation. Age/site matching and complete clinical eligibility are unverified.

## Locked execution and results

TimeMeasure1, Test10, Trial1; Stereophoto walking intervals; 100 Hz native Acc in
g; magnitude; 500-sample windows, 250-sample hop; no padding, gravity subtraction,
retuning or abstention. The same frozen v0.2.0 weights, checkpoint normalization,
participant mean aggregation and descriptive 0.50 threshold were used.

| Group / person | Windows | Mean model score | Call at 0.50 |
|---|---:|---:|---|
| Healthy / 1091 | 2 | 0.962193 | Positive |
| Healthy / 1092 | 3 | 0.978089 | Positive |
| PD / 1000 | 3 | 0.947829 | Positive |
| PD / 1001 | 3 | 0.515021 | Positive |

Accounting: 4 selected, 4 evaluated, 0 excluded; 11 windows. Healthy positive
calls: 2/2. PD positive calls: 2/2. For either group, the descriptive binomial
Wilson 95% interval is approximately 34.24%-100%, and convenience selection
further limits inference. Model scores are not calibrated clinical stroke
probabilities. There is no stroke group: no sensitivity or diagnostic AUROC.
Do not pool this result with the previous Test6 call as five independent people.

The high scores in both healthy recordings show that the observed failure is
not limited to PD gait. They do not identify whether task, sensor/domain shift,
preprocessing or learned features caused it. Turning cannot be isolated with
these reference annotations. No performance improvement is claimed.

## Implementation and verification

- [Offline runner](../scripts/run_tvs_hallway_probe.py) locks raw, source,
  metadata, adapter, runner, checkpoint and previous-result hashes before scoring.
  It refuses changed artifacts, missing/invalid participant input and existing
  results. All four must pass before any hallway scoring; no replacements.
- Annotation availability is recorded explicitly, with `straight_only_verified`
  false for every person. The frozen adapter itself was not modified.
- Three new checks cover nested empty/present turn annotations, protocol
  mutation rejection and preservation of an existing result. These and five
  existing adapter checks passed (eight tests in this run).
- The release inference smoke check passed. Independent checks verified saved
  participant/window accounting, score means and calls, protocol/runner hashes,
  and that the earlier Test6 result remained byte-for-byte unchanged.

Artifacts: `data/interim/public_imu_screen_2026-09-08/hallway_probe_v1/`
contains protocol/hash, intake, per-person windows/provenance, results and
verification. To inspect, read saved JSON. Re-executing the runner after results
exist deliberately fails instead of overwriting them.

## Consequence and next implementation target

Hallway feasibility and frozen scoring are completed; do not repeat them or
download more people to rerun the same probe. Six raw participants remain local,
with metadata for 40 and 34 raw files unacquired. The original Test6 pilot remains
intact. No download or evaluation process is left running.

The next bounded investigation is the input-transfer path: compare these failed
windows against the frozen release's input contract and saved development signal
statistics before proposing a model change. A concrete, reproducible mismatch
could justify a preprocessing correction; absence of a mismatch would instead
leave domain generalization as an unresolved model limitation. Do not select a
new threshold, normalization transform or turn filter to rescue these four
observed outputs. Any correction needs separate development validation and
new evaluation data; these people are now inspected diagnostic evidence.
