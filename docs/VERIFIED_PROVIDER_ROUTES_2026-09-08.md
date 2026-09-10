# Verified provider routes and executed gate results

Searched primary registry records, institutional pages and data-availability
statements on 2026-09-08. Downloaded registry JSON metadata only. No participant
archives acquired; no messages sent. Three candidate records were populated and
run through `src/data/recruitment_gate.py`; all remain on hold.

## Recommended order

1. **Paolo Brasiliano / Santa Lucia–Foro Italico cohort.** The paper reports
   85 stroke and 97 healthy participants, 10-m walking, synchronized 128-Hz OPAL
   sensors and documented L4–L5 placement. Other lower-limb sensors are on distal
   tibiae, not feet. Data are available by reasonable request; this does not
   establish raw export permission. Contact: `paolobrasilianores@gmail.com`.
   Ask specifically for unfiltered, gravity-retaining lower-back acceleration,
   annotations and a dictionary; overlap with related Santa Lucia cohorts must
   be checked. The current full gate fails because feet and non-stroke groups
   are absent, alongside unresolved schema/governance requirements.
   [Primary paper](https://www.nature.com/articles/s41598-026-43666-7).
2. **Santa Lucia multi-condition registry NCT04691102.** Correct title:
   Predictive Indices of Independent Activity of Daily-living in
   Neurorehabilitation. Registry groups include stroke, TBI, MCI, PD, MS and
   healthy subjects, with inertial motor-task assessments. The location contact
   is Marco Tramontano, `m.tramontano@hsantalucia.it`. This is the strongest
   verified route here for asking about non-stroke comparisons; raw files,
   compatible placement, usable counts and sharing permission remain unresolved.
   [Official registry/API](https://clinicaltrials.gov/api/v2/studies/NCT04691102).
3. **Shirley Ryan AbilityLab, NCT04219670.** The actual inpatient sensor study
   includes healthy controls in its description. Registry contacts are Arun
   Jayaraman (`a-jayaraman@northwestern.edu`) and Sara Prokup
   (`sprokup@ricres.org`). Request placement/export/annotation details and usable
   group counts. Estimated total enrollment is not a released paired dataset.
   [Official study](https://clinicaltrials.gov/study/NCT04219670).

## Gate interpretation that matters

The Brasiliano cohort is a plausible **primary lower-back paired-validation
lead**, not a complete match to the existing all-endpoints gate. Requiring feet
for a one-channel model unnecessarily restricts that primary role. Nevertheless,
do not silently waive the current protocol or pretend it supplies non-stroke
specificity. A documented role-specific protocol would be needed before accepting
it. Raw sample review and participant independence are required either way.

## Corrections and deprioritized routes

- Previous AbilityLab ID NCT04205279 was wrong: it is a UIC balance-training
  study. Corrected the shortlist and draft to NCT04219670.
  [Official incorrect-ID record](https://clinicaltrials.gov/study/NCT04205279).
- NCT05125172 is a Western Carolina sit-to-stand study, not Strathclyde GRAS.
  Withdrew that mapping. [Official API](https://clinicaltrials.gov/api/v2/studies/NCT05125172).
- Rzeszow NCT06187974 confirms paired groups and actual enrollment of 132, but
  IPD sharing is undecided and the raw lower-back contract remains unproved.
  [Official API](https://clinicaltrials.gov/api/v2/studies/NCT06187974).
- Istanbul NCT07036900 and UIC NCT04957355 explicitly list no IPD sharing.
  Do not treat either as an available archive route.
  [Istanbul API](https://clinicaltrials.gov/api/v2/studies/NCT07036900),
  [UIC API](https://clinicaltrials.gov/api/v2/studies/NCT04957355).

The uneven-surface stroke/healthy paper and its GitHub repository also surfaced,
but this pass did not establish a matching raw export. It is unscreened, not an
accepted alternative. Public searches rediscovered Voisard and Zhou, which do
not supply a new independent paired cohort.

## Saved evidence

`data/interim/provider_registry_verification_2026-09-08/` contains six official
registry snapshots, three screening JSON records and three executed gate outputs.
Unknown fields remain unknown. Public study methods are not substituted for a
provider-level raw-file schema sample. No candidate passed and no archive was
authorized by these screening results.
