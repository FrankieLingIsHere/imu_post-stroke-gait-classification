# Rehabilitation assessment product specification

Updated 2026-09-29. This specification expands the client brief from a research walk recorder into a rehabilitation assessment workflow.

## Clinical protocol basis

The Shirley Ryan AbilityLab Rehabilitation Measures Database describes the 10-Meter Walk Test (10MWT), Timed Up and Go (TUG), and Six-Minute Walk Test (6MWT) as standardized measures with defined setups and observer or equipment requirements. The current references are:

- [10 Meter Walk Test](https://www.sralab.org/rehabilitation-measures/10-meter-walk-test)
- [Timed Up and Go](https://www.sralab.org/rehabilitation-measures/timed-and-go)
- [6 Minute Walk Test](https://www.sralab.org/rehabilitation-measures/6-minute-walk-test)
- [2 Minute Walk Test](https://www.sralab.org/rehabilitation-measures/2-minute-walk-test)
- [ATS 6MWT statement](https://www.thoracic.org/statements/resources/pfet/sixminute.pdf)
- [TUG administration instructions](https://www.sralab.org/sites/default/files/2017-06/Timed%20Up%20and%20Go%20Test%20Instructions.pdf)
- [2MWT administration instructions](https://www.sralab.org/sites/default/files/2017-07/2%20Minute%20Walk%20Test%20Instructions.pdf)

These sources are protocol references, not evidence that a lower-back phone alone can reproduce the measures.

## What the phone can and cannot measure

The lower-back IMU can record synchronized accelerometer, gyroscope, and magnetometer streams; identify recording start and stop; describe pauses, motion coverage, turns, placement shifts, and experimental timing features; and preserve a clinician-entered distance or event marker.

The phone cannot reliably derive travelled distance or absolute speed from double-integrated lower-back acceleration without an external position reference. It also cannot prove the 10MWT boundary, chair contact in TUG, bilateral limb identity, step length, or foot clearance. Those values must be supplied by a measured course, clinician marker, camera, BLE/UWB reference, wheel counter, or validated additional sensors.

## Phone-only distance approaches in current products and literature

Consumer trackers use a practical two-path pattern. [Fitbit documents](https://support.google.com/googlehealth/answer/14237111?hl=en) GPS-derived distance during a GPS-tracked workout; without GPS it computes steps × stride length, with stride length estimated from body information or manually calibrated. [Google Fit](https://support.google.com/fit/answer/10066680?hl=en) says it uses device sensors for step and distance activity tracking, but does not publish enough implementation detail to treat its output as a clinical measurement. [Apple's Core Motion API](https://developer.apple.com/documentation/coremotion/cmpedometerdata/distance) exposes OS-estimated pedometer distance on supported devices. These consumer estimates are designed for activity tracking and do not establish accuracy for a horizontally mounted lower-back phone or post-stroke gait.

There is a research precedent for a single phone: [GaitTrack](https://pmc.ncbi.nlm.nih.gov/articles/PMC4229704/) used phone accelerometry plus gait and demographic features in 30 chronic lung-disease participants performing a 6MWT on a measured 15 m path. The report gives a mean absolute percentage distance difference of 5.87% for the retained sample, but also describes an equipment-failure outlier and does not validate post-stroke patients or this app's lower-back landscape placement. Its model was trained and evaluated in a small condition-specific cohort, so its accuracy must not be copied as an expected GaitTrace result.

GaitTrace therefore uses a transparent step-distance approach, not double integration: candidate events × estimated metres per event. It starts from the existing height-based heuristic and, after a worker enters the measured total distance for an eligible full walk, can save a local participant-specific scale for subsequent captures. Calibration is only attempted on the research walk, 2MWT and 6MWT paths when at least eight candidate events support it; 10MWT timed-zone distance is not used to calibrate a recording that may include acceleration/deceleration zones, and TUG includes non-walking transitions. The estimated output and calibration method are exported separately from measured course outcomes. It remains experimental because candidate peaks can miss or double-count steps and step length changes with asymmetry, speed, fatigue and aid use. An optional Android foreground GPS cross-check is available by explicit opt-in. It begins after the first detected step, saves only aggregate distance and device-reported accuracy (no coordinate trace), and is unsuitable as ground truth for short or indoor routes.

## Protocol workflow

Implementation status (2026-09-29): The Android app now has a protocol chooser, searchable/editable local participant profiles with session snapshots, an outcome-entry form, a participant history dashboard, and an optional foreground GPS distance cross-check. The form stores measured course/time values and derives speed only from those values. This is a worker-assisted capture workflow, not a complete validated implementation of these standardized clinical batteries. Automatic boundary, lap, chair-rise, or seat-contact detection is not implemented.

### 10MWT

The in-app guide now distinguishes the project-selected 12 m layout (1 m acceleration, central 10 m timed zone, 1 m deceleration) from the database's acknowledgement that 6, 8, 10, and 12 m course variants exist. The worker times only the marked 10 m zone, records the speed condition and usual aid, and enters the result. The database describes two comfortable-speed trials and two fast-as-safe trials, averaged separately. GaitTrace currently captures one sensor session with a 180 s ceiling; it does not detect zone crossings or manage four trials. That capture duration must not be mistaken for the 10MWT result. Speed is `10 m / worker-entered timed-zone seconds`.

### TUG

The in-app guide describes the standard sequence: use a standard armchair, mark 3 m, stand on “Go”, walk at a comfortable and safe pace, turn, return and sit. A worker starts timing on “Go” and stops when the participant is seated again. Aid, assistance and practice status must be recorded. GaitTrace does not detect chair rise, the 3 m line or seat contact; its 180 s sensor window is not the TUG score.

### 2MWT and 6MWT

The app explains these separately. The 2MWT measures distance in two minutes and permits slowing or resting while the timer continues. The 6MWT is self-paced and measures six-minute distance; rests are allowed with the timer running. The ATS 6MWT standard uses a 30 m corridor, and changing to a shorter loop adds turns and may change distance, so record and hold course length constant. For either test, a worker starts the protocol stopwatch at “Go”, counts complete laps, measures the final partial distance, and records rests. GaitTrace now captures before Go and starts the endurance clock on the speech-start callback (or worker tap with voice off). Rests do not pause that clock. It does not count laps or implement the standardized timed encouragement: walking commentary and turn reminders are suppressed, and the worker supplies the standard messages. Optional app voice gives preparation, Go and finish cues. GaitTrace is a parallel sensor capture aid; do not treat its timer or voice prompts as clinical protocol administration.

The protocol chooser opens a translated three-step patient tutorial for each option, using short instructions, scalable route/chair diagrams and read-aloud. Full instructions are retained under Worker protocol notes. It states the test purpose, course/setup, pacing/rest rules, worker actions and the exact boundary between the clinical score and the app's sensor capture. The short research walk is explicitly labelled non-standardized. Full wording is in English, Malay and Simplified Chinese. Sources are linked above and summarized in the UI; this is protocol education, not a claim of clinical validation.

## Participant and worker records

Use a local participant registry first, because the current app has no authenticated server. Test setup creates and links a profile automatically on Start for a new study label, requiring age and an explicit sex choice. Known labels must be explicitly selected so two people with similar demographics cannot be merged. Existing historical snapshots are preserved. Each participant record should have a generated internal ID, display name or coded label, favorite flag, age, biological sex, height, weight, stroke type, lesion location, time since stroke, pre-morbid asymmetry, joint/orthopaedic history, assistive device, and notes. A worker selects a participant before a test; the app copies the profile snapshot into the assessment record so later profile edits do not rewrite historical measurements.

The registry must support create, search, favorite, archive, and export. Do not use a patient's name as the research identifier by default. If the app will be used across workers or devices, local-only profiles are insufficient and an authenticated encrypted backend plus a data-governance decision is required.

## Assessment form and dashboard

Every test record should contain protocol, trial number, worker ID, date/time, measured setup, assistive device, safety observations, rests, symptoms, perceived exertion, completion status, and free-text clinical notes. The dashboard should show per-participant longitudinal plots for measured speed, distance, test time, cadence/timing descriptors, pauses, and worker-entered scores. It should show within-person change and measurement quality, not a stroke classification score.

## Humanized voice policy

Voice guidance should be generated from measured state and the participant's own history, with varied but controlled templates. Examples:

- Current paired movement is sustained: “Your movement looks steady right now. Keep this comfortable pace.”
- A measured pause occurs: “A short rest is okay. Begin again when you feel ready.”
- A prior comparable run exists: “Your clear movement pattern is stronger than your previous run.”
- Signal quality is uncertain: “I cannot read this part clearly. Continue only if the phone is secure.”

The app must not say that a person is walking well when the signal is missing, handling is suspected, or the comparison is not supported. Comparative feedback belongs after enough of the current test is recorded; a live cue cannot honestly compare a not-yet-completed run with its history.

## Delivery sequence

1. Replace fixed 10–30 second research walks with a protocol selector and explicit “research walk” fallback.
2. Add local participant registry, favorites, profile snapshots, and structured assessment forms.
3. Add measured-course and manual boundary/lap events before enabling speed or distance outputs.
4. Add TUG chair/event workflow and 2MWT/6MWT loop workflow with worker confirmation.
5. Add longitudinal dashboard and controlled behavior-based voice templates.
6. Validate each protocol against therapist-administered reference measurements before presenting it as a rehabilitation outcome.


## Implemented protocol control — 1 October 2026

The shared `protocolFlow.ts` contract defines start, finish, guidance and duration policies. Phone placement, sensor readiness, the standing baseline and movement/settling checks remain shared. The standing reference is preserved before a TUG participant returns to the chair.

| Mode | Start | Active guidance | Finish |
| --- | --- | --- | --- |
| Research walk | Existing countdown then detected first step | Sparse behaviour-based cues and optional direction reminders | Selected sensor duration |
| 10MWT | Worker readiness, capture before Go | Explain the marked path before starting; no generic mid-walk coaching | Worker confirmation after deceleration; 180 s capture limit |
| TUG | After checks, sit; worker confirms readiness; capture before Go | Explain chair-to-chair sequence before starting; no guessed turn/seat announcements | Worker confirmation after seated; 180 s capture limit |
| 2MWT | Capture before Go; clock from cue | Measured-route/rest instructions; worker administers protocol; no straight-path warnings | 120 s from Go, rests included |
| 6MWT | Capture before Go; clock from cue | Worker supplies standard timed instructions; no extra app praise or turn warnings | 360 s from Go, rests included |

The worker-presence checkbox is required for live clinical modes. The same `ClinicalCapture` component is used for their browser previews, with explicit simulated readiness and no saved sensor data. Shared checks and research walking remain explanatory preview stages, not hardware simulation. Preview can trigger a labelled finish event to avoid waiting six minutes.

The app does not detect 10MWT boundaries, TUG transitions or laps. The worker records the clinical stopwatch and distance separately. A capture limit or interruption does not mark the clinical assessment completed. The TTS start callback is a software timestamp, not a verified acoustic timestamp; the selected protocol stopwatch remains the outcome reference. Worker-tap time and spoken-Go time are distinguished. Extra latency and OS scheduling need device validation.

JSON and raw CSV carry `protocolExecution` provenance: flow version, protocol, offset of Go from capture start, cue source, elapsed time from Go, end reason and unverified clinical status. Raw CSV only reconstructs available metadata; absent measured outcomes remain absent. Pre-Go samples are retained rather than trimmed silently.
