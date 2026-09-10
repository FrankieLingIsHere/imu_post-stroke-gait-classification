# TVS input transfer and cohort-wide continuation

## Input-transfer result: completed

No mismatch was found in the tested magnitude reconstruction, sampling/timebase,
documented acceleration units or frozen normalization path. This does not rule
out all device, placement, task or domain differences, and it does not explain
the observed false positives. No preprocessing correction or model change was
justified or fitted from these four people.

The [input checker](../scripts/check_tvs_input_transfer.py) verified the release's
development-file hashes, loaded the frozen bundle and compared the saved hallway
windows with an independent float64 Euclidean magnitude reconstruction from each
raw MAT interval. Maximum error was 2.483e-7 g. Native acceleration was declared
100 Hz with a matching timebase. The archived official loader establishes stored
Acc in g; no additional g conversion belongs in this adapter.

Recomputing normalization from the verified development lower-back tensor exactly
reproduced all 15 members' constants: mean **1.0162991285 g**, standard deviation
**0.2063165307 g**. Inference applies these training constants once per member;
it does not fit TVS normalization. TVS participant mean magnitudes were
1.0105-1.0290 g, with standard deviations 0.2692-0.3709 g. These descriptive
differences are not sufficient to identify the failure mechanism or justify
rescaling to force lower scores.

Saved evidence: `input_transfer_check.json` and
`input_training_normalization_check.json` under
`data/interim/public_imu_screen_2026-09-08/`. No new prediction, fitting or
threshold sweep was performed in this check.

## What the score means

The label **healthy** comes from the dataset. The displayed score is the model's
**stroke-class score for that healthy participant**, not a healthy-class score
or a health rating.

1. A five-second window contains 500 lower-back acceleration magnitudes in g.
2. Each of 15 frozen models normalizes the window using its saved constants,
   computes a logit, then applies sigmoid: `1 / (1 + exp(-logit))`.
3. The 15 sigmoid outputs are averaged to obtain the window score.
4. Window scores are averaged equally within that participant. A mean at least
   0.50 produces a positive call under the recorded descriptive threshold.

For HA/1091, `(0.9664570317 + 0.9579290263) / 2 = 0.9621930290`.
That is a false-positive call for a participant labelled healthy. It is not a
calibrated 96.2% clinical probability of stroke. Overlapping windows are not
independent people, so evaluation counts and intervals use participants.

## Cohort-wide protocol

The user authorized moving beyond small pilots. The
[cohort runner](../scripts/run_tvs_cohort.py) therefore registers **all 40 HA/PD
laboratory participants**, not just another hand-picked subset. This covers the
healthy and Parkinson's groups currently screened, not all six TVS disease groups.
TVS still has no stroke cohort.

Eligibility is fixed before new cohort scoring: final Test10 hallway trial,
native MM+, lower-back acceleration and Stereophoto availability, no walking aid
and no task annotation; finite native 100 Hz signal and complete five-second
within-bout windows. Possible turns remain because reference turn truth is
unavailable. Exclusions, including short/missing reference bouts, remain in the
40-person denominator ledger. No participant is replaced.

Metadata decisions: **19 healthy and 16 PD eligible**, with five explicit
exclusions:

| Person | Reason before new raw acquisition |
|---|---|
| HA/1093 | Task annotation |
| PD/3006 | Lower-back and Stereophoto availability absent for selected task |
| PD/4012 | Task annotation |
| PD/4014 | Task annotation |
| PD/4020 | Lower-back/reference absent for selected task and walking aid/unknown |

Five eligible participants are already inspected and local: HA/1091, HA/1092,
HA/4109, PD/1000 and PD/1001. **Thirty additional members** are required, totaling
**1,252,087,764 compressed bytes** and **1,258,819,511 raw bytes**. Compressed
resume caches are retained alongside extracted data; this is roughly 2.51 GB
additional storage before small metadata/window artifacts. There was over 400 GB
free at launch. Full multi-gigabyte archive ZIPs are not needed.

The primary descriptive results will report newly opened healthy and PD people
separately, with inspected and combined strata also shown. Previously inspected
people are never relabelled untouched. The hallway choice was informed by earlier
TVS results, so even the extension is not a pristine clinical final test.

All participants form one automated queue. Files transfer through two concurrent,
disk-resumable range connections; serial file order is a transport detail, not
person-by-person scientific selection. Verified local raw files and existing
range caches are reused. Any acquisition failure stops scoring and preserves the
same locked queue for resumption. Eligibility exclusions are distinct from
transfer failures. Results are written only after complete intake, with unchanged
weights, normalization, averaging and 0.50 threshold.

Three new tests passed for explicit metadata exclusion reasons, preserving an
existing cohort result and stopping all cohort scoring after transfer failure.
The protocol, dependency hashes and per-person intake are saved under
`data/interim/public_imu_screen_2026-09-08/cohort_hallway_v1/`.

## Execution status: complete

Completed on 2026-09-08 at 23:52 Malaysia time and verified on 2026-09-09.
All 30 new files acquired; 34/40 people evaluated on 117 windows. Combined
positive calls: 17/18 healthy and 16/16 PD. See the
[completed result](TVS_COHORT_RESULT_2026-09-09.md) for new/inspected strata,
exclusions and integrity verification. No process remains running. Read saved
results or run `scripts/status_tvs_cohort.py`; do not restart this completed job.
