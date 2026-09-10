# TVS common-task pilot v1

Subsequent continuation: the [hallway probe](TVS_HALLWAY_PROBE_2026-09-08.md)
is now complete. This report preserves the original Test6 protocol and result;
its next-task paragraph below records the decision at that earlier stage.


**Completed 2026-09-08.** Four new raw laboratory recordings were acquired and
CRC/SHA-verified. Three participants failed the fixed five-second duration
requirement. The sole eligible participant, PD/1000, received a positive call
at 0.50 (mean model score 0.887380). This is an additional specificity failure
observation, not a reliable population estimate or an improvement in the model.

This is new work following the completed two-person schema smoke test. Before
starting, searches found no prior TVS pilot lock, additional raw-pilot recordings
or pilot prediction artifacts in the project. The existing schema participants
HA/4109 and PD/4020 are excluded.

## Predeclared design

The versioned machine-readable protocol was written before raw acquisition or
scoring at `data/interim/public_imu_screen_2026-09-08/locked_pilot_v1/protocol.json`,
with a separate SHA-256 file. It fixes selection, adapter hash, metadata hash,
checkpoint hash, windowing, aggregation, threshold and exclusions.

- Two participants per group, selected as the first two lexicographic IDs among
  metadata-eligible people with native MM+, Stereophoto reference, no walking aid
  and no task annotation. This is a deterministic convenience pilot, not a
  representative or age-matched cohort.
- Selected: HA/1091, HA/1092, PD/1000, PD/1001.
- Same task for all four: **Test6 slow straight walk, TimeMeasure1, Trial2**.
- No replacements following download failure, exclusion or model output.
- Five-second raw lower-back magnitude windows in g, 100 Hz, 250-sample hop.
  Use the already-tested adapter's Stereophoto reference endpoints, with no
  padding, joining of short bouts, reference fallback or threshold tuning.
- Exclude invalid signal/timebase/reference or no complete window. Nonempty
  break/turn annotations are excluded conservatively. Reference turning labels
  are incomplete, so task documentation does not establish perfect turn removal.
- Frozen v0.2.0, checkpoint-fixed normalization, participant mean probability,
  descriptive threshold 0.50, abstention disabled.
- Report each group's participant accounting, positive-call rate and Wilson
  interval. There is no stroke group: no sensitivity or diagnostic AUROC.

The four selected compressed MAT members total **194,644,170 bytes**. Existing
metadata and range caches are reused. The full archive collection is not needed.
Raw member manifests record CRC, size and SHA-256. Acquisition or execution
failures must remain distinct from clinical/quality exclusions.

## Reproduce or resume

```powershell
& C:/Users/frank/.venv-cu130/Scripts/python.exe scripts/run_tvs_locked_pilot.py
```

The runner resumes the same lock and cached files. Once `results.json` exists,
it refuses to rerun or overwrite the evaluation. Read the saved result instead.
The result is an exploratory protocol-specific stress test, not evidence of
clinical validity or model improvement. This pilot will itself be inspected
evidence after execution and cannot later serve as a pristine final test.

## Executed result

| Participant | New raw bytes | Reference interval samples / duration | Eligible windows | Result |
|---|---:|---|---:|---|
| HA/1091 | 41,833,856 | [286, 704), 4.18 s | 0 | Excluded: short bout |
| HA/1092 | 53,092,967 | [289, 652), 3.63 s | 0 | Excluded: short bout |
| PD/1000 | 50,239,242 | [539, 1205), 6.66 s | 1 | Positive, score 0.8873795271 |
| PD/1001 | 50,550,665 | [561, 894), 3.33 s | 0 | Excluded: short bout |

All four transfers completed, with no replacement or acquisition failure. New
raw bytes total **195,716,730**, in addition to retained compressed range caches.
The project now has **six HA/PD raw laboratory participants**: two schema samples
and four pilot participants. All 40 metadata records remain acquired; **34 raw
laboratory recordings remain unacquired**. The six full archives are not downloaded.

Healthy accounting: selected 2, evaluated 0; rate and interval are undefined,
not zero. PD accounting: selected 2, evaluated 1, positive 1, negative 0.
Its descriptive Wilson 95% interval is 20.65%-100%, illustrating the lack of
precision. These convenience-selected, incompletely characterized participants
are not an age/site-matched cohort. No stroke sensitivity, diagnostic AUROC,
calibration claim, or clinical validation follows from this test.

The release smoke check passed before scoring. Independent verification checked
all four raw CRCs, lengths and SHA-256 values; protocol, metadata, adapter and
checkpoint hashes; window shapes; participant accounting; saved-score means and
group intervals. No predictions were rerun. Evidence files under `locked_pilot_v1/`:
`protocol.json`, `protocol.sha256`, per-person manifests/windows, `intake.json`,
`results.json`, and `verification.json`.

- Protocol SHA-256: `12fe7f664153cff95e49832ab960bd79fbfe632849cc7573070079534ca9e631`
- Results SHA-256: `76e760394b13f1b7c030036200d2dab8f70b3445192173b06a73345bcbbe33c2`

## Decision from the duration screen

Across all six acquired participants, final-trial availability is:

| Task | Healthy people with windows / total windows | PD people with windows / total windows |
|---|---:|---:|
| Test5 comfortable straight walk | 0 / 0 | 1 / 2 |
| Test6 slow straight walk | 0 / 0 | 2 / 5 |
| Test7 fast straight walk | 0 / 0 | 1 / 1 |
| Test10 hallway | 3 / 8 | 2 / 6 |

These are feasibility counts including the original schema participants, not
additional scored participants. Short straight-walking reference intervals do
not support the intended healthy comparison in the acquired files. Choosing
Test6 from metadata availability was too optimistic. A five-second eligibility
rule on a short walkway can preferentially retain slower gait; downloading more
people under the same rule is not a justified default.

The next task is a hallway-specific, turn-aware protocol using existing files.
First establish whether reference annotations permit usable straight portions;
otherwise label the task explicitly as mixed walking/turning and assess whether
that matches the intended model use. Empty turning fields do not prove no turns.
Preserve this completed pilot and its exclusions. Any subsequent hallway result
on these people is inspected exploratory evidence, not a pristine independent
test. No further raw acquisition or healthy/PD comparative scoring was performed
after this feasibility screen. The substantial historical false-positive issue
remains unresolved; model weights and threshold are unchanged.

## Additional implementation delivered

`scripts/screen_tvs_local_duration.py` checks all already acquired laboratory
files across the adapter's four tasks, using final trials and verified raw
hashes. It does not download, score, replace selected people or change this
pilot. Its saved `local_duration_screen.json` is post-selection feasibility
evidence for subsequent protocol design, not another validation result.

Three new runner tests cover changed-protocol rejection, preserving an existing
result without another acquisition, and treating a CRC failure as an acquisition
failure that stops scoring. The last test accompanies a correction separating
acquisition `ValueError`/`KeyError` from schema exclusions. That exception-path
correction was made while the original download process was running; its loaded
code predates the correction. Successful acquisition and all locked selection,
preprocessing and scoring behavior are identical. Any actual acquisition failure
in this run therefore requires explicit inspection before accepting results.

Two new offline MATLAB-fixture tests verify that a longer earlier trial cannot
replace an ineligible final trial, and that raw checksum failure stops the
duration screen. All five new checks passed, as did ten existing transport,
adapter and metadata checks. No model retraining or threshold search occurred.
