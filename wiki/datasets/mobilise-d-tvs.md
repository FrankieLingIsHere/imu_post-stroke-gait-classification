---
type: dataset
population: "TVS release describes 108 participants across six groups. Current intake: metadata for 20 healthy and 20 Parkinson's participants, two schema participants and a separate four-person raw-data pilot"
sensors: "McRoberts MM+ lower-back IMU, native Acc and Gyr at 100 Hz verified in two samples"
role: nonstroke_specificity_candidate
updated: 2026-09-08
---

Latest experiment (2026-09-09): [ElderNet checkpoint](../../docs/classification/archive/2026-09/ELDERNET_TRANSFER.md) was fine-tuned on TVS according to its pinned upstream README. The downloaded small PD4010 wrist fixture reproduced 416 predictions; this does not establish independent evaluation. Whole-cohort raw acquisition unchanged, fixture preprocessing and inference complete, stroke transfer not performed.


# Mobilise-D Technical Validation Study (TVS)


Current engineering decision: user authorizes lower research-prototype gates.
[Policy, dataset roles and CLI](../../docs/RESEARCH_PROTOTYPE_POLICY_2026-09-09.md).
TVS laterality prototype packaged on 32 participants/1,645 contacts under 85%
accuracy and 85% coverage gates. Earlier CV: HA 87.46%, PD 87.34%, corrected coverage
86.45%/85.45%. This is post-result prototype acceptance, not revised validation.
Original failed gates remain historical evidence. Frozen stroke model unchanged.
Acquisition unchanged, prototype fitting/packaging and real CLI smoke check complete.
Inputs require native TVS-frame gyro and supplied contact indices. No stroke output.


Current completion update (2026-09-09): [full cohort results](../../reports/TVS_COHORT_RESULT_2026-09-09.md).
All 30 additional files acquired; 36 raw participants local in total. All 40
registered people accounted for: 34 evaluated on 117 windows, five metadata
exclusions and one short-bout exclusion. Positive calls: 17/18 healthy and 16/16
PD overall; 14/15 healthy and 14/14 PD among newly opened people. Verification
passed; no process remains running. Cohort acquisition/scoring is complete,
not pending. Earlier launch descriptions below are historical. No model
improvement or validated correction is claimed.


TVS supports the non-stroke specificity track in
[[classification-project-status]]. It is distinct from the already downloaded
Mobilise-D CVS processed-outcome release. Version-pinned source:
[Zenodo 15861907](https://zenodo.org/records/15861907). TVS contains healthy,
PD, MS, proximal femoral fracture, COPD and CHF groups, with no stroke cohort.
The release describes 108 participants, while older loader documentation describes
115 collected participants. Neither number is our acquired raw cohort size.

## Key findings

| Acquisition layer | Current local state |
|---|---|
| HA/PD ZIP inventories | 20 laboratory participants per group identified |
| `test_list.json` and `infoForAlgo.mat` | Downloaded and CRC-verified for all 40 participants |
| Original schema `data.mat` | HA/4109 (18,408,703 bytes) and PD/4020 (31,207,433 bytes) |
| New raw-data pilot | HA/1091, HA/1092, PD/1000 and PD/1001 all acquired and CRC/SHA-verified; 195,716,730 new raw bytes |
| Remaining raw laboratory recordings | 34 of 40 HA/PD files not acquired; six acquired in total |
| Entire six-group archives | Not downloaded |
| New specificity pilot | Complete: three duration exclusions, one PD participant scored positive at 0.887380 |

The two raw samples contain 13 healthy and 12 PD trials with finite matching
N-by-3 Acc/Gyr arrays, declared 100 Hz rates and increasing timestamps. Native
Acc units are g according to the archived official mobgap loader, which converts
them to m/s². Our magnitude adapter retains g and does not subtract gravity.

The adapter uses the final trial of Test5/6/7/10 and Stereophoto continuous-walking
intervals, with MATLAB start-index correction. Five-second windows use a
250-sample hop, never cross bouts or recorded breaks, and are not padded.
The output is ten float32 windows: three healthy hallway windows and seven PD
comfortable/slow/fast windows. Frozen v0.2.0 inference returned finite outputs.
This task imbalance, incomplete turn annotations and PD rollator use prevent
interpreting the engineering smoke test as a controlled clinical comparison.

## New locked pilot and duration finding

The [four-person pilot](../../reports/TVS_LOCKED_PILOT_2026-09-08.md) advances
beyond the original smoke samples. Selection, reference, windowing, model hash,
aggregation, threshold and no-replacement exclusions were fixed before raw
acquisition/scoring. Its artifacts live in `locked_pilot_v1/`, with separate
per-person raw manifests. Do not count pilot files through the old sample manifest.

Healthy participants HA/1091 and HA/1092 have 4.18- and 3.63-second Test6 bouts,
respectively, and are excluded. This protocol therefore cannot estimate healthy
specificity. Longer walking duration can itself depend on gait speed, creating
selection bias when a five-second requirement is applied to a short walkway.
Do not fix this by padding, joining bouts or selecting replacements.

The new [offline duration screen](../../scripts/screen_tvs_local_duration.py)
checks final Test5/6/7/10 trials in acquired files without predictions or downloads.
`local_duration_screen.json` is feasibility evidence for subsequent task design,
not an accepted cohort or a revised version of this locked pilot. Hallway
duration alone does not establish suitable turn exclusion or a matched protocol.

Final pilot accounting: HA 0/2 evaluated; PD 1/2 evaluated, 1 positive. PD/1001
was also too short (3.33 seconds). Healthy specificity is undefined, and the
PD 1/1 interval is 20.65%-100%; neither supports clinical generalization. All
four transfers succeeded and no selected participant was replaced. Protocol,
raw files and score accounting passed independent verification.

Across all six raw files, hallway duration supports eight windows from three
healthy participants and six from two PD participants. These include schema
samples. The separate [hallway probe](../../reports/TVS_HALLWAY_PROBE_2026-09-08.md)
then scored only the four pilot people: five healthy windows and six PD windows,
2/2 healthy and 2/2 PD positive calls at 0.50. Neither reference system provides
turning information according to the archived release description; possible
turns were retained. This is not straight-only validation. The current model
is unsupported for these hallway recordings. Acquisition counts are unchanged.
The input-transfer check has now passed its magnitude/rate/units/normalization
checks without an identified correction. The user authorized a cohort-wide
hallway batch registering all 40 people: 35 metadata-eligible, five excluded;
30 additional raw members queued alongside five reused eligible files. See the
[input-transfer/cohort report](../../reports/TVS_INPUT_TRANSFER_AND_COHORT_2026-09-08.md)
and `scripts/status_tvs_cohort.py` for live file/intake counts. The earlier six-file
ledger above is the state before this new batch, not its completion count.

## Candidate coverage after excluding development samples

| Task | Healthy metadata candidates | PD metadata candidates |
|---|---:|---:|
| Test5 comfortable straight walk | 19 | 19 |
| Test6 slow straight walk | 19 | 19 |
| Test7 fast straight walk | 19 | 18 |
| Test10 hallway | 18 | 16 |

These counts require lower-back/reference availability, MM+ device metadata and
no task annotation under the current scanner. They are not final inclusion
counts. Duration, complete clinical/demographic metadata, quality and protocol
eligibility remain unresolved. License recorded in the release is CC BY-NC-ND
4.0. The authors frame use as algorithm validation, not deriving clinical
conclusions from small disease subgroups.

## Reuse and reproducibility

Local evidence root: `data/interim/public_imu_screen_2026-09-08/`.
`sample_manifest.json` records raw-member CRC/SHA verification.
`lab_metadata/intake_status.json` records 40 verified and zero pending metadata.
`prepared/` contains windows, provenance, exclusions and inference smoke output.

- [Sample downloader](../../scripts/acquire_tvs_schema_samples.py)
- [Resumable transport](../../src/data/http_ranges.py): 1 MiB ranges, partial-file
  resume, two active connections, backoff, timeout and integrity checks
- [Metadata intake](../../scripts/screen_tvs_lab_metadata.py): already completed,
  use `--offline` to inspect without another download
- [Window adapter](../../src/data/tvs.py) and
  [preparation runner](../../scripts/prepare_tvs_schema_windows.py)

Earlier timeouts and HTTP 504 responses were intermittent. Replayed requests
and the resumed intake succeeded. Do not retain “38 metadata transfers pending”
as current status or rebuild the downloader on that assumption.

Sources: [sample acquisition](../../reports/TVS_SAMPLE_ACQUISITION_2026-09-08.md),
[preprocessing/inference](../../reports/TVS_PREPROCESSING_INTEGRATION_2026-09-08.md),
[completed intake](../../reports/TVS_MATCHED_COHORT_INTAKE_2026-09-08.md).


## Positive-call mechanism diagnosis completed

The [controlled diagnosis](../../reports/TVS_POSITIVE_CALL_MECHANISM_2026-09-08.md)
used only four inspected TVS people and 24 development controls. No new cohort
participant was used. All 15 members called both healthy TVS people positive;
actual training batches had 32 healthy and 32 stroke windows per source. Final
head bias alone was small relative to healthy feature-logit contributions.
Offset/amplitude/filter probes did not remove either healthy false positive.
Temporal shuffling drove scores near zero, while constant signals produced high
positive scores. These demonstrate temporal-pattern dependence and a non-walking
failure mode, not a proven clinical cause of the real hallway errors. No model,
threshold, filter or normalization change was promoted. The cohort and subsequent differential-objective experiment are complete;
use [[classification-project-status]] for the current decision. Do not repeat
this diagnosis or tune on the four inspected people.


## Optical event-reference intake completed

[TVS intake and exploratory classifier](../../reports/TVS_OPTICAL_REFERENCE_AND_CLASSIFIER_2026-09-09.md):
32 local participants, 17 HA/15 PD. Raw optical markers and explicit event sides
verified. Optical/INDIP side agreement 1,584/1,584 matched contacts. Corrected
contact coverage 86.4% HA/85.4% PD fails gate. Initial denominator bug allowed
three exploratory fits, 87.46%/87.34% accuracy; saved as exploratory, not admitted.
Corrected intake rerun, no further fits. 163/225 trials usable; 45 missing optical,
17 partial/invalid. No stroke group, no stroke model promotion. Acquisition
unchanged, reference extraction complete, corrected model eligibility failed.
Next is explicit per-contact reference-quality handling, not dropped bad trials.
Independent calibration of Voisard is not established by TVS references.
