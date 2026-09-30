---
type: concept
---

# Gait app collection workflow

This page tracks what the local GaitTrace phone app can capture and what still requires observer, course or clinical validation. It is an implementation record, not evidence that the app is a validated rehabilitation instrument.

## Local participant workflow

The Android source now includes a local participant registry with a coded label, demographic and clinical profile fields, favorite/archive state, and a session-time profile snapshot. A worker can select the participant before setup, review earlier sessions in a dashboard, and enter outcome notes after recording. The result form supports protocol labels for the research walk, 10MWT, 2MWT, 6MWT and TUG. Its worker-entered course distance and stopwatch time can be exported as comparison metadata. The profiles and recordings stay on the device; there is no account, synchronization or server-backed history.

## Measurement boundary

For 10MWT, speed is calculated from the entered timed interval and measured 10 m zone. For 2MWT/6MWT, the worker enters loop length, full laps and remaining partial distance. TUG time is entered by the worker. These fields support a structured record, but the app does not automatically establish course boundaries, lap counts, chair rise/seat contact, or standardized administration. An optional Android foreground GPS distance cross-check is available after explicit opt-in; it begins only after walking starts and retains aggregate distance/accuracy metadata without saving coordinates. Its output is not ground truth and may be unreliable indoors or on short routes.

The phone estimates distance as candidate step events multiplied by a stride scale. It starts with a height heuristic and can store a participant-specific scale after a worker records a measured total route distance for a research walk or 2MWT/6MWT. This follows the general step × stride approach documented by consumer trackers, but uses this app's candidate events and placement; its result is explicitly experimental. GPS distance is a separate optional outdoor cross-check. Neither phone-derived output is validated for post-stroke gait. A lower-back single-phone IMU cannot identify left/right limb, paretic side, true per-step length, foot clearance or neurological cause of asymmetry. Sensor-derived symmetry should remain descriptive and unclassified until independently validated against synchronized reference measurements. See the [assessment specification](../../docs/REHAB_ASSESSMENT_PRODUCT_SPEC.md#phone-only-distance-approaches-in-current-products-and-literature).

## Responsive setup and automatic participant creation

Updated 2026-09-30. Home uses a compact navigation grid and one fixed primary Start action. Setup has separate person, test, and sound/readiness pages. Sound playback appears at the top of the final page. Optional settings and detailed instructions expand only on request. Shared screens bound the action area and allow scrolling at small heights or enlarged font sizes, while button labels can wrap within the available width.

Test setup requires a study label, age and an explicit sex selection, with Prefer not to say available. A new profile is saved on Start and its ID and snapshot travel with the recording. Existing profiles can be selected in setup. Identity uses the saved ID and normalized study label, never matching age/sex alone. Profile writes must succeed before recording begins, and retrying does not create another identity. Browser profiles use the same tab-only lifetime as browser recordings. Old unlinked recordings are not assigned to people by demographic guesses.

## Current implementation and gaps

The participant dashboard lists stored assessments per profile and plots up to twelve measured-speed outcomes for the most recent protocol when course length and walking aid match. This is descriptive history, not a clinical trajectory score. The registry supports searching coded labels and editing profiles while prior session snapshots remain unchanged. Spoken completion feedback summarizes actual movement evidence and compares only with a matching previous non-practice test for the same participant; it withholds praise when the data are unclear. New GPS permission/quality paths, translations, usability and device behavior still need physical review. Clinical protocols need a therapist-led reference comparison before any result is described as a validated clinical outcome.

## Test protocol explanations

The setup screen now opens a three-step illustrated tutorial in English, Malay or Simplified Chinese for every protocol. Each step has a short patient instruction and read-aloud control. Full explanations are retained under Worker protocol notes. It explains the intended clinical measure and setup, timing or rest rules, worker responsibilities, and the sensor app's limits. The 10MWT uses the client's chosen 12 m layout but says this is one selected variant; a worker must time the marked middle 10 m, and the app's 180-second recording is not the clinical time. The 2MWT and 6MWT each keep rests inside the protocol duration, but their pace and administration differ. The 6MWT guide describes the ATS 30 m course and scripted encouragement, which GaitTrace does not reproduce; it tells the worker to disable the app's voice and direction cues during a standardized test. The TUG guide describes the full chair-to-chair sequence and the worker stopwatch endpoint. See the sourced protocol detail in [the assessment specification](../../docs/REHAB_ASSESSMENT_PRODUCT_SPEC.md#protocol-workflow).

## Links

- [Client requirements and measurement boundary](../../docs/GAIT_APP_CLIENT_REQUIREMENTS.md)
- [Rehabilitation assessment specification](../../docs/REHAB_ASSESSMENT_PRODUCT_SPEC.md)
- [Current weekly app progress](../../docs/classification/WEEKLY_PROGRESS_2026-09-28.md)

### Setup menu refinement (30 September 2026)

Setup keeps secondary controls in a separate More menu: language, voice/direction/practice settings, optional GPS and participant details. Saved-person search and protocol choice open separate selectors rather than growing the setup page. Menus respect safe areas and scroll within screen bounds; Done closes them while preserving selections. All 88 automated tests and TypeScript checks pass. Physical small-screen visual review remains pending.
