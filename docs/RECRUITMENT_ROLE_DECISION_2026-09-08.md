# Evaluation roles: implementation decision

Current continuation: public-only TVS metadata and sample integration are
complete as detailed in [the wiki handoff](../wiki/concepts/classification-project-status.md).
Contact requests below remain unsent and parked. The statement that no new data
were opened describes this earlier gate-implementation checkpoint, not the
subsequent TVS development samples. The role definitions remain current.

The user authorized continuation of the proposed role-specific screening.
No new dataset has been opened or accepted. The gate now supports:

| Profile | Required groups | Sensor requirement | Permitted endpoint |
|---|---|---|---|
| `primary_lower_back_paired` | Healthy, stroke | Documented native lower-back acceleration | Paired healthy/stroke evaluation only |
| `lower_back_nonstroke_specificity` | Healthy, non-stroke | Documented native lower-back acceleration | Healthy/non-stroke positive-call rates; no stroke sensitivity |
| `full_comparison` | Healthy, stroke, non-stroke | Original synchronized LB and bilateral feet contract | Combined planned endpoints and three-channel comparator |

The default remains `full_comparison` for backward compatibility. Unknown profile
names fail closed. Single-channel profiles do not require gyro units or cross-sensor
synchronization; the acquisition timebase and walking annotations remain mandatory.
Raw data, clinical labels, participant metadata, provider-sample review, overlap,
permissions and endpoint-specific sample-size evidence remain required in every role.

This explicitly supersedes the blanket requirement that every primary candidate
must have bilateral feet and all clinical groups. It does not permit relabeling
shank sensors as feet or merging unrelated cohorts into one binary validation set.
Passing a role does not support the other role's endpoint. Related Santa Lucia
cohorts must be deduplicated, and shared participants cannot supply independent
validation claims across stages.

## Executed screening

- Brasiliano: primary paired profile, **hold, 12 blockers**.
- Santa Lucia NCT04691102: specificity profile, **hold, 19 blockers**.
- AbilityLab NCT04219670: primary paired profile, **hold, 20 blockers**.

These are administrative evidence-field counts, not scientific quality scores.
The paper's known missing feet/non-stroke groups no longer disqualify the
Brasiliano primary role. Native export and annotations, governance, identity
checks, provider sample and precision planning are still unresolved.

All 19 repository tests passed, including role boundaries, invalid profiles and
preservation of core evidence requirements. Updated machine-readable screenings
are saved beside the original strict-profile outputs in
`data/interim/provider_registry_verification_2026-09-08/` with `_role_` filenames.

The practical next action is the two [prepared provider requests](PRIORITY_PROVIDER_REQUESTS_READY.md).
They are ready for sender identity and explicit sending authorization; none has
been sent. There is no remaining reason to rebuild this screening gate while
awaiting provider evidence.
