# Local optical references and exploratory laterality classifier

**Independent-modality reference files were located locally. Corrected eligibility
failed, so the exploratory classifier is not admitted. No new stroke classifier.**

## Newly verified use of existing files

Inspected 30 already downloaded TVS cohort laboratory MAT files plus the two
original schema samples: 32 participants (17 healthy, 15 PD), no stroke group.
Existing acquisition reports described optical/pressure systems; this work verifies
the concrete event-side fields and their usable coverage, not a new dataset.
No data downloaded. These participants are development data, not untouched tests.

The selected Test5/6/7/10 recordings contain raw Stereophoto marker fields, including
left/right foot markers, and optical ContinuousWalkingPeriod initial-contact times
with explicit Left/Right labels. INDIP provides a second event-reference stream.
The raw optical modality is independent of lower-back gyro, but supplied events
remain processed reference outputs with potential correlated errors.

Across 225 selected trial records, 163 passed strict reference/gyro checks, 45 had
no optical side contacts and 17 had invalid/partial reference times or labels.
All 32 participants have usable contacts in other trials. Optical/INDIP agreement
was 1,584/1,584 sides among contacts matched one-to-one within 150ms. This does not
establish agreement on unmatched/missing contacts or prove timing ground truth.
Mean trial timing MAE among matched contacts is 24.0ms healthy and 28.0ms PD.

## Corrected coverage

| Cohort | Declared optical contacts | Usable gyro/optical contacts | Coverage |
|---|---:|---:|---:|
| Healthy | 952 | 823 | 86.4% |
| PD | 962 | 822 | 85.4% |

These rates fail the locked 95% gate. Trials with no declared optical events have
no countable event denominator and remain explicitly in the trial ledger. Thus
event coverage is not the fraction of all walking that has a valid reference.

## New classifier attempt and accounting correction

[Protocol](../docs/TVS_OPTICAL_LATERALITY_PROTOCOL_2026-09-09.md) specified a fresh
linear SVC using nine gyro features (all three axes, filtered values/first/second
gradients) at supplied optical contacts. Participant-stratified three-fold CV,
train-only scaling and participant-balanced weights. This predicts contact side,
not stroke diagnosis. No cross-device frame correction was inferred from labels.

The first run incorrectly set the expected count to zero when parsing a partially
invalid reference trial failed. That eligibility-accounting bug allowed three fits.
Their participant-macro accuracies were 87.46% healthy and 87.34% PD, both below
the 90% performance gate anyway. The initial artifacts are preserved in
`initial_attempt/`, with exploratory predictions/metrics explicitly named.

After fixing the denominator to count declared contacts before parsing, extraction
and eligibility were rerun. Coverage failed and no further model fitting occurred.
Those three initial fits are exploratory, not a protocol-qualified experiment.
Three parser tests passed (explicit sides/deduplication, conflicting labels, empty
reference). The discovered eligibility issue is disclosed rather than hidden.

## Decision

The available optical route is useful for a future reference-quality-aware
measurement evaluation. It cannot prove anatomical calibration or contact labels
in the separate Voisard recordings. No local TVS stroke recordings were found in
this scoped intake, so a new stroke classifier is not justified by this result.
Keep the existing release unchanged. Do not reuse the exploratory accuracy as an
independent validation claim or silently drop partial-reference trials.

The next concrete measurement task is a separately specified per-contact reference
quality policy using optical annotations, retaining valid events within partial
trials and explicitly accounting for unknown intervals. This is a new eligibility
design, not permission to relax today's gate. Independent calibration of Voisard
still requires source-specific evidence.

## Artifacts and state

Runner `scripts/run_tvs_optical_laterality.py` and artifacts under
`data/processed/tvs_optical_laterality_v1/`: hashes, features, trial coverage,
participants, corrected decision, and preserved exploratory fits. Metadata/raw
acquisition unchanged. Optical intake/extraction complete. Corrected classifier
eligibility failed, three earlier exploratory fits retained, no accepted model.
No running job. Stroke HR results remain 44/49 stroke, 5/19 healthy FP, 47/76 other
FP in the primary matched comparison. Frozen CNN results unchanged.
