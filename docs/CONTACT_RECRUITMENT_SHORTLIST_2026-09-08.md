# Contact-based recruitment shortlist

Current status: contact-only leads are parked under the user's public-data
preference. No outreach has been sent. Resume the TVS specificity work described
in [the current wiki handoff](../wiki/concepts/classification-project-status.md).
This historical contact list is neither a public-download list nor the current
acquisition queue. The role-specific gate supersedes blanket bilateral-foot
requirements for lower-back-only evaluation.

**Correction after primary-source verification:** use [verified provider routes](VERIFIED_PROVIDER_ROUTES_2026-09-08.md) as the current ranking. The earlier shortlist contained incorrect registry mappings; corrected below. Unverified secondary claims are not acceptance evidence.

Date: 2026-09-08

Purpose: identify investigators who may hold a paired or prospective cohort suitable for an untouched external evaluation of the frozen lower-back wearable gait model.

This is an outreach shortlist, not an accepted dataset list. Registry evidence establishes that a study exists and identifies its population, sensors, or contact route. It does not establish that raw signals, channel order, units, participant-level metadata, or data-sharing permission are available. No archive should be downloaded until the provider-level schema sample passes `data/interim/recruitment_acceptance_checklist.md`.

## Priority 1

| Priority | Study and contact | Registry evidence | Why contact | Known blockers |
|---|---|---|---|---|
| 1 | [NCT04219670](https://clinicaltrials.gov/study/NCT04219670), Inpatient Stroke Recovery Using Sensors. Arun Jayaraman, Shirley Ryan AbilityLab, `a-jayaraman@northwestern.edu`; Sara Prokup, `sprokup@ricres.org` | The protocol describes stroke patients and healthy controls, wireless wearable sensors, gait-quality outcomes during clinical tests, and a estimated enrollment of 400. The study is registered as recruiting. | Best direct route to a paired clinical cohort with a machine-learning and wearable-sensor provenance. | Registry text does not specify lower-back plus bilateral-foot placement, raw-file access, channel order, or whether the healthy and stroke recordings share the required walking protocol. |
| 2 | [NCT04691102](https://clinicaltrials.gov/study/NCT04691102), Predictive Indices of Independent Activity of Daily-living in Neurorehabilitation, Santa Lucia IRCCS. Marco Tramontano, `m.tramontano@hsantalucia.it` | The protocol describes stroke, TBI, MCI, Parkinson disease, multiple sclerosis, and healthy groups. It specifies seven APDM Opal sensors at the trunk, sacrum, tibias, and wrists, sampled at 128 Hz, with 10-meter walk and figure-of-eight tasks. | Strongest route for clinical specificity and hard-negative groups, and the protocol names a complete sensor system and task battery. | The stated placement is not the frozen lower-back plus bilateral-foot contract. Raw IMU access, healthy-control count, channel export, and external-sharing terms must be confirmed. |
| 3 | [NCT07036900](https://clinicaltrials.gov/study/NCT07036900), Effects of Flexion and Extension Type Arm Slings, Istanbul University-Cerrahpasa. Ceren Bayrak Dörtkol, `cerenbayrakdortkol@gmail.com`; Tahire Başak Demir, `tahirebasakdemir@gmail.com` | Prospective case-control study with stroke and healthy participants. It uses two shoe-mounted PABLO inertial sensors at 110 Hz and applies the same gait assessment to both groups. | A compact paired cohort with explicit healthy controls and an identified data-collection team. Useful for a protocol-transfer conversation even if the present study is not a direct drop-in. | No lower-back channel, no public raw-data commitment, and the registry states that participant data are not planned for sharing. Treat as a collaboration or prospective-replication lead, not a download target. |

## Priority 2

| Priority | Study and contact | Registry evidence | Why contact | Known blockers |
|---|---|---|---|---|
| 4 | [NCT06187974](https://clinicaltrials.gov/study/NCT06187974), University of Rzeszów. Maciej Kochman. | Completed prospective case-control study with 132 participants, including ischemic stroke and age/sex-matched healthy volunteers. Gait was assessed with PABLO inertial sensors and clinical tests. | The study design is close to the desired paired clinical comparison and may provide a contact route to a completed cohort. | The documented sensor is lower-limb focused rather than lower-back plus bilateral-foot. The registry lists IPD sharing as undecided. Ask whether raw synchronized signals and metadata remain available before any further work. |
| 5 | Strathclyde recovery program | **Prior NCT05125172 mapping withdrawn:** that ID belongs to a Western Carolina sit-to-stand study. | Institutional collaboration route only, pending specific cohort verification. | Do not use the previous GRAS/FOSTER registry attribution. |
| 6 | [NCT04957355](https://clinicaltrials.gov/study/NCT04957355), UIC reactive-balance and gait study. Tanvi Bhatt, `tbhatt6@uic.edu`; Rudri Purohit, `rpuroh2@uic.edu` | The recruiting study uses three-dimensional inertial sensors, GaitRite, and standardized walking tests in chronic stroke participants. | Distinct investigator route for a prospective specificity or hard-negative collaboration, especially if the team can add healthy or non-stroke comparison participants. | The registered study is stroke-only and does not match the lower-back plus bilateral-foot contract. It is a collaboration lead, not a direct external-test download. |

## Secondary evidence leads

Recent Europe PMC records show that paired wearable-IMU stroke/healthy studies are still being conducted, but the records are not evidence of public raw-data availability:

- [Deep Learning-Based Automated Clinical Gait Assessment From Kinematic Data in People With Stroke](https://europepmc.org/article/MED/42616771), PMID 42616771. The abstract reports wearable IMUs and 18 healthy controls, with authors at Hong Kong Polytechnic University. Contact should begin with the corresponding author or institution, and sensor placement/raw-data availability must be confirmed.
- [Identifying key gait features in stroke patients using wearable inertial sensors](https://europepmc.org/article/MED/41796232), PMID 41796232. The article reports a stroke-versus-healthy wearable MIMU study associated with Santa Lucia researchers. It may overlap with an already-known Santa Lucia cohort and must be deduplicated before contact or reuse.
- [Development and clinical validation of a stroke-specific Gait Deviation Index](https://europepmc.org/article/MED/41593749), PMID 41593749. The article reports 22 healthy controls and 69 post-stroke subjects, but the available record does not establish a raw lower-back plus bilateral-foot release. Treat it as a paper-level contact lead only.

## First-contact questions

1. Do you hold raw, synchronized accelerometer and gyroscope signals rather than only derived gait features?
2. Which sensors were placed at the lower back or lumbar region, and which were placed on the left and right feet or ankles?
3. What were the sampling rate, units, axis conventions, channel order, and device model?
4. Were healthy controls and stroke participants recorded under the same walking task, footwear, surface, instructions, and preprocessing pipeline?
5. Are participant IDs, age, sex, walking aid, footwear, speed, stroke severity, stroke side, chronicity, and clinical scales available?
6. Can the study provide a small de-identified schema sample or data dictionary before any data-use agreement or archive transfer?
7. Are there restrictions on external evaluation, publication, model release, or onward sharing?
8. Can the team add a prospective healthy-control and non-stroke neurological/orthopedic arm if the existing cohort is not compatible?

## Minimal outreach wording

> Subject: Request for a schema discussion about wearable gait data and independent evaluation
>
> I am preparing an independent, participant-level evaluation of a research model for post-stroke gait classification. Your study appears relevant because it includes clinically characterized walking data and wearable sensing. I am not requesting a full archive at this stage. Could you confirm whether the study contains raw synchronized signals, the sensor placements and sampling rate, participant-level clinical metadata, and a pathway for controlled external evaluation? A small de-identified schema sample or data dictionary would be sufficient for the first compatibility check. Any analysis would preserve participant confidentiality, follow the study's consent and governance requirements, and keep your cohort as an untouched external test or prospective collaboration rather than mixing it into model development.

## Decision rule

No candidate is accepted until the provider confirms the schema and governance details. In particular, a study with healthy controls and stroke participants is not automatically a matching cohort. The final external role requires a documented lower-back plus bilateral-foot contract, raw or losslessly reconstructable signals, clinically traceable labels, participant-level metadata, and no overlap with existing development or tuning sources.
