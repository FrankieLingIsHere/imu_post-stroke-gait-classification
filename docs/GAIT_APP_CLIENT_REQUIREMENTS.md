# Gait app client requirements and measurement boundary

Updated 2026-09-29. This page translates the client brief into an implementation contract for the Android phone application.

## Target population and safety gate

The intended participants are people in long-term post-stroke gait retraining who can walk independently, with no aid, a single-point cane, or a quad stick. Acute stroke, non-ambulatory participants, and anyone requiring physical transfer or hands-on assistance are outside this app's safe self-test scope. The app must ask the participant to confirm that the path is clear and their usual support is available, and it must keep the instruction to stop whenever they feel unsafe. This is a research capture tool, not a clearance or diagnosis tool.

The placement stage is now open-ended. After the user taps Start, the phone gives the placement instruction and waits for the live baseline instead of expiring after 20 seconds. This lets an older participant take the time needed to secure the horizontal lower-back holder; the user can cancel safely if assistance is needed.

## Required participant profile

The local participant registry now stores a coded label, favorite/archive state, age, self-reported sex, height, weight, stroke type, lesion location, months since stroke, pre-morbid gait notes, joint/orthopaedic notes, and usual walking aid. Starting a test from a saved profile copies a snapshot into the session, so later profile changes do not rewrite an earlier record. Test setup now requires a study label, valid age and an explicit sex choice (including Prefer not to say). Selecting a saved person prefills these fields. Starting a test with a new label automatically saves and links a local participant profile. Height and clinical details remain optional. Duplicate labels require choosing the existing record or using a distinct study ID, and no identity is inferred from age/sex similarity. These fields are covariates for later analysis; they are not used for an in-app diagnosis or classification. Profiles remain on this device and are not synchronized.

## Calibration and placement

Before walking, the voice flow should say: “Stand as straight as you can, with your feet about shoulder width apart.” The three-sensor stationary baseline is the participant's individual static reference. A persistent comfortable trunk tilt should be retained as that participant's zero reference rather than automatically labelled abnormal. The current baseline already stores raw stationary streams separately and does not subtract them from walking data. The phone cannot verify anatomical lower-back location, contact pressure, or belt tightness from these sensors alone; those remain instructed and reviewable limitations.

## Assessment batteries

The client proposes 10MWT, TUG, and 2MWT/6MWT. A lower-back phone can support timing, motion, pauses, turning cues, and experimental cadence descriptors. It cannot establish a true 10-metre boundary, step length, foot clearance, or chair-transfer events without an external distance marker, manual event confirmation, computer vision, or additional foot sensors.

Before starting, Show me how opens a three-step tutorial with route/chair diagrams, one short instruction per step, and optional read-aloud in the selected language. Worker protocol notes retain the full detailed guide. It describes the measured purpose and setup of each test, pacing/rest rules, worker timing and distance duties, and which parts GaitTrace does not perform. The descriptions follow the Shirley Ryan AbilityLab RehabMeasures summaries, their administration sheets, and the ATS 6MWT statement. The 10MWT guide preserves the project's chosen 12 m layout (1 m + 10 m timed + 1 m) while noting that other course variants exist. The 6MWT guide identifies the ATS 30 m corridor and warns that course length changes the number of turns. These guides do not make the app a validated or fully automated test administrator.

The current app provides a protocol selector and a local worker-entered result form. For 10MWT the form records timed-zone seconds against the assumed 10 m zone and derives speed as 10 m / seconds. For 2MWT/6MWT it accepts a measured loop length, lap count, and remaining partial distance, and derives speed only when a timed interval is entered. TUG stores a worker-entered complete stopwatch time and observation fields. The research walk retains its separate 10/20/30 second sensor-capture duration. In addition, the device estimates distance from candidate movement events multiplied by a height-based or locally calibrated participant-specific scale. This is an experimental phone estimate, separate from measured-course outcomes. These are recording and data-entry supports; they do not implement all standardized verbal instructions, boundary/event detection, or validated clinical administration. The worker must check the actual protocol and course.

Therefore the remaining implementation and validation order is:

1. Validate each assisted protocol against a therapist-administered reference, with explicit trial/event timing and fatigue/rest behavior.
2. Add protocol-specific start/finish and event controls before treating phone capture timing as clinically aligned.
3. Treat phone-only speed/distance as experimental. The optional height-and-candidate-step estimate is exported with its heuristic label and is not a clinical result. The result form derives speed only from worker-entered measured distance and time.
4. Treat step length, bilateral step timing, and clinical symmetry as unavailable until limb identity and independent reference evidence exist.

## Analysis and feedback boundary

Exported research features may include candidate step count, cadence, step-time variability, baseline-relative trunk motion, pauses, placement-shift events, and coverage quality when the signal supports them. These are experimental descriptors. A single lower-back IMU cannot reliably identify paretic versus non-paretic limbs, true step length, foot clearance, or the cause of asymmetry.

Patient feedback should be supportive and non-diagnostic. The walk flow selects a translated cue from live motion context: encouragement only for sustained paired movement, a rest cue for measured quiet, and a safety cue for possible handling. At completion, a short spoken observation reflects the current movement record and, when available, compares with the same participant's previous non-practice run only when protocol, duration and walking aid match. Uncertain or missing data produce an uncertainty statement instead of praise. It must not claim that asymmetry is neurological without clinical assessment.

## Current status

Implemented locally: three-sensor permission/readiness checks, individual stationary baseline, lower-back landscape placement instructions, first-step recording gate, placement-shift review events, behavior-gated live and completion voice feedback, local searchable/editable participant profiles/favorites/archive and per-session snapshots, protocol selection, worker-entered assessment outcomes, local participant history dashboard, and feature-CSV columns for participant/test metadata and measured outcomes. Setup/placement and the movement fit check wait without a fixed timeout.

Implemented locally in this batch: optional Android foreground GPS distance cross-check, requested only after the user enables it; GPS watching begins after the first detected walking step. Only aggregate distance, fix count and median device-reported accuracy are saved/exported, not coordinates. Participant profiles can now be searched by coded label and edited without rewriting prior session snapshots. Neither GPS nor the candidate-step estimator is a clinical distance measure.

Not yet implemented or validated: automatic course boundary/lap or TUG event detection, automatic clinical event detection and standardized timed encouragement, bilateral limb attribution, clinical asymmetry scoring, and independent clinical validation. The local dashboard lists history and can plot measured-speed history when protocol, course length and walking aid match; it is not a validated progress model. GPS is best treated as a rough outdoor cross-check; short, indoor or obstructed routes can produce misleading distance. These changes have not been published or physically validated.

## 1 October usability and linkage refinement

Named setup settings and explicit Change test/radio controls replace ambiguous selection affordances. Height/walking aid are directly accessible in participant setup. Height remains optional for raw recording and measured-course outcomes; its heuristic estimate is explicitly experimental.

Recording inventory includes unassigned, practice and archived-participant histories. Existing explicit IDs restore missing profiles; unknown owners require a confirmed assignment from recording details, never demographic matching. Assignment does not rewrite captured measurements. Raw CSV carries participant identity and height; JSON supports six-minute recording imports. Comparative trends still require comparable measured device outcomes.


## Protocol-specific guidance implementation

Research walking keeps behaviour-based cues. Clinical capture now branches into worker-assisted 10MWT, TUG, 2MWT and 6MWT policies. TUG explains the seated start and full chair-to-chair sequence; 10MWT explains the marked path; endurance instructions explicitly allow rests without pausing time. Generic turn warnings/praise are suppressed during clinical capture; the worker gives standard timed instructions. App setup/Go/finish audio is optional. Live capture and preview share the clinical controller. Timing provenance is exported separately from worker-confirmed results. Physical validation remains pending.
