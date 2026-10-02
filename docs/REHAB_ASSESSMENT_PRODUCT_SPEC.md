# Rehabilitation assessment product specification

Updated 2026-10-02. This specification expands the client brief from a research walk recorder into a rehabilitation assessment workflow. Native camera-distance feasibility remains separate from the implemented IMU capture flow.

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

## Free distance-provider feasibility audit — 2 October 2026

Requirement: compute distance and speed automatically while one phone is mounted horizontally at the lower back, with no paid API, no per-test entered distance, and no reach-back stop control. The lower-back anatomical location is non-negotiable. No reviewed provider documents a clinically calibrated solution using only the currently captured IMU signals in post-stroke gait. An API returning metres does not establish traceable calibration or clinical accuracy. Existing height/step estimates remain experimental and are not upgraded by this audit.

| Route | Verified capability | Fit to this requirement |
| --- | --- | --- |
| [Google Recording API on mobile](https://developer.android.com/health-and-fitness/recording-api) | Accountless on-device collection; documented steps, distance-delta and calories types; uses Google Play services and activity-recognition permission. | A possible OS comparison stream. The documentation supplies no calibration/error guarantee for a lumbar phone, short indoor clinical zones or asymmetric walking. Do not present it as a calibrated replacement merely because the API supplies distance. |
| [Health Connect](https://developer.android.com/health-and-fitness/health-connect/experiences/workouts) | Stores and shares source-attributed DistanceRecord, SpeedRecord and exercise routes. Recent on-device step capture is platform/version dependent. | Record access does not create an independently measured clinical distance. It does not solve this app's measurement gap on Android 11. |
| [Android fused location](https://developers.google.com/location-context/fused-location-provider) | Combines device positioning signals and can provide position/velocity updates. | Already used by the optional Expo location cross-check. Requested accuracy is not a guarantee; adding a map/cloud API does not supply a new short-indoor position reference. Retain as an outdoor cross-check. |
| [Wi-Fi RTT](https://developer.android.com/develop/connectivity/wifi/wifi-rtt) | Ranges to compatible access points; three or more known AP locations enable multilateration, documented typical position accuracy 1–2 m. | Requires compatible phone/AP infrastructure and surveyed AP positions. This is not a universal, zero-extra-hardware solution or established accuracy for 10MWT timing zones. |
| [ARCore local motion tracking](https://developers.google.com/ar/develop/fundamentals) | Combines camera features and IMU; [Pose translations](https://developers.google.com/ar/reference/java/com/google/ar/core/Pose) are in metres. Google lists [Redmi Note 10 Pro](https://developers.google.com/ar/devices) as supported. | Rejected for the confirmed mounting: screen/selfie camera faces the room, rear lenses face the body. ARCore front-camera mode disables world tracking. Device support does not remove this restriction. |
| [OpenVINS](https://github.com/rpng/open_vins) and [Android port](https://github.com/goldbattle/open_vins_mobile) | Open-source camera/IMU estimator with an Android native port. IMU supplies monocular metric scale; camera/IMU calibration and timestamp alignment are essential. | Candidate for a custom front-camera prototype, not a ready service. Inspected port selects the rear camera; front selection, correct front-camera calibration and real-device validation are required. GPL-3.0 obligations must be respected when distributing a derivative. No API subscription is proposed. |

Placement resolved by the user on 2 October: **screen/selfie camera faces the room; rear camera faces the body**. Keep both the lower-back location and this mounting arrangement. ARCore is consequently unsuitable. Recommendation: evaluate a **local OpenVINS front-camera/IMU prototype** separately from the patient app before integration. This is an engineering feasibility proposal, not verified front-camera support or calibrated distance. No cloud subscription, billing account or paid external service is proposed.

This route gives a metric position signal, not a clinically certified gait result. [Published VIO benchmarking](https://arxiv.org/abs/2207.06780) is evidence about camera tracking, not stroke/holder validation. Poor light, weak visual texture and excessive movement can pause tracking. The selfie camera is not an equivalent fallback: [ARCore front-camera configuration](https://developers.google.com/ar/reference/java/com/google/ar/core/CameraConfig.FacingDirection) disables world tracking.

Source inspection was pinned to Android-port commit `f0c465695c67c0eac786f4edf83a68109a6a58a9`: [Camera2ResView.kt](https://github.com/goldbattle/open_vins_mobile/blob/f0c465695c67c0eac786f4edf83a68109a6a58a9/app/src/main/java/com/openvins/android/Camera2ResView.kt) explicitly prefers `LENS_FACING_BACK`. Changing that selection alone is insufficient. Follow [OpenVINS calibration guidance](https://docs.openvins.com/gs-calibration.html) for front-camera intrinsics/distortion, camera-to-IMU geometry, time alignment and IMU noise. Keep calibration versioned for the actual device and capture mode; do not reuse another phone's rear-camera configuration. Calibration is a research-team preparation task, not a repetitive patient exercise. A two-to-three-step fit check cannot establish metric calibration. The guidance recommends higher IMU acquisition rates than the app's 50 Hz export; investigate native acquisition separately and preserve native timestamps rather than inventing samples through upsampling.

Before app integration, prove tracking with the real phone and holder on an existing measured course. Verify that the selfie lens sees through the holder without obstruction or optical distortion. Confirm stationary drift, repeated straight-walk length, turns, intentional rests and camera occlusion. Compare supported results to the marked reference using distance bias, absolute/relative error, repeatability and tracking-loss rate; agree acceptable error with the clinical supervisor instead of promising an untested percentage. Validate automatic endpoints separately against observed boundary crossings. Camera displacement is not automatically course progression or clinical speed.

Implementation must define a consistent position frame, estimate horizontal route progression rather than count all trunk sway as travelled distance, preserve timestamps/calibration identity/tracking failures beside untouched IMU axes, and keep course-boundary events distinct from TUG chair-contact candidates. Lost tracking must withhold a complete distance result instead of silently filling it with the height heuristic. Automatic end-of-course cues require a separately defined and validated course coordinate frame. No native camera integration, front-camera proof or clinical validation has been executed in this audit. Native integration would require a new APK; it cannot be delivered solely as an Expo JavaScript update. Current shell checks did not find a Java/Android SDK build toolchain in the usual locations, so no local native build is claimed.

### External-service recheck and physical visual reference

The user's renewed request for a free external service prompted additional checks on 2 October. [IndoorAtlas pricing](https://www.indooratlas.com/pricing/) offers a 30-day non-production trial followed by paid plans; its [setup documentation](https://www.indooratlas.com/get-started/) requires venue mapping. This does not satisfy ongoing zero-payment operation or establish clinical gait-distance accuracy. [Spectacular AI](https://github.com/SpectacularAI/sdk) advertises non-commercial use of its public SDK, but its [native Android wrapper](https://spectacularai.github.io/docs/sdk/wrappers/mobile.html) requires a commercial licence. Do not confuse free public desktop tooling or sample code with free Android deployment. No account, trial, payment or service integration was initiated.

An additional no-subscription candidate is a prepared course with measured printed fiducials, using [AprilTag pose estimation](https://github.com/AprilRobotics/apriltag#pose-estimation) or [OpenCV ArUco](https://docs.opencv.org/4.x/d5/dae/tutorial_aruco_detection.html). These algorithms use known marker size and calibrated camera parameters to recover relative pose. This supplies an explicit physical scale rather than a participant stride assumption; it does not establish clinical accuracy by itself. Software can run locally without a paid API. Printing and measuring course references is a researcher setup task, not a per-test patient distance entry or stopwatch action.

Feasibility constraints: marker dimensions must be measured after printing; front-camera intrinsics/distortion must match the active resolution/focus and holder optics; marker locations must be surveyed in one course frame. The outward selfie camera looks behind the walker during forward travel, so marker coverage must be designed for that view, turns and rests. Small endpoint tags cannot be assumed visible over 10 metres. Boards distributed along the course may be needed. Crossing time must refer to the protocol's body/foot boundary convention rather than silently treating the lower-back camera as the crossing point. Occlusion or inconsistent pose must yield unavailable measurement, not height-based substitution labelled as calibrated. Do not sum noisy camera sway into travelled distance.

Current decision: no reviewed service supplies a verified, continuously free, clinically calibrated replacement for the present mounting. Evaluate marker-referenced camera measurement if researcher-prepared courses are acceptable; otherwise retain the front-camera OpenVINS feasibility route without promising validated distance. The user was asked whether fixed printed references are acceptable; this environmental constraint remains unresolved. Neither route has been integrated or physically validated. Existing app distance remains experimental.

### Google Recording API comparison implementation — local, 2 October 2026

Implemented an opt-in **Google distance test · experimental** using a local Expo Android module with `play-services-fitness:21.3.0`, `FitnessLocal` and `LocalRecordingClient`. The UI requests physical-activity permission before inaccessible-phone setup and checks the full distance-capable Play services requirement. No legacy Google Fit OAuth, Fit app, Google account, API key or paid service was added. The Android module is discovered by Expo autolinking; its activity permission is declared in the app and library manifests. App/package version is now 0.3.0, retaining the existing EAS remote build numbering and fingerprint runtime policy. A new native APK is required; old APKs/Expo Go show a translated explanation if the experiment is enabled.

Registration starts during preparation. Reads use only research capture start or clinical audible Go through actual capture finish, poll every two seconds and perform bounded final reads before saving. Capture/IMU/clinical stop logic is independent of Google output. The experiment records original distance/step interval values and first-seen times, poll query/response times, API errors and registration cleanup status. Identical records are deduplicated; invalid, overlapping or boundary-straddling intervals are excluded from sums without prorating. Missing output stays null. Sparse/rejected/error-bearing intervals withhold whole-test speed; 95% interval coverage is a software completeness gate, not a clinical accuracy claim. The result card, permission errors and opt-in explanation are translated into English, Malay and Chinese. JSON retains diagnostics; raw and feature CSV append explicitly named Google comparison columns. JSON import preserves valid optional summaries and rejects malformed values; legacy exports remain readable.

Both registrations are released after final reads, cancellation, setup error or late subscription completion following cancellation. Cleanup errors are exported. Android registrations survive process death, so force-kill cleanup cannot be guaranteed. The bounded final-read window may miss later provider batches; no zero or height fallback substitutes for missing Google records. Physical distance bias, availability and reporting delay remain unanswered until real-phone trials. Test plan and build constraints: [native module README](../android/modules/gait-google-recording/README.md). Native compile/new APK and physical validation remain pending; source integration and JavaScript checks must not be represented as a verified Android trial.

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
| 10MWT | After checks, stand at start and stay still for 3 s; capture before spoken Go | Explain the marked path before starting; no generic mid-walk coaching | Provisional automatic save after sustained movement then 8 s quiet; 180 s safety ceiling |
| TUG | After standing checks, sit and stay still for 3 s; capture before spoken Go | Explain chair-to-chair sequence before starting; no guessed turn/seat announcements | Provisional automatic save after sustained movement then 8 s quiet; 180 s safety ceiling |
| 2MWT | After 3 s stillness, capture before Go; clock from cue | Route and rest instructions; no straight-path warnings | 120 s from Go, rests included; automatic save |
| 6MWT | After 3 s stillness, capture before Go; clock from cue | No extra app praise or turn warnings | 360 s from Go, rests included; automatic save |

The worker-presence checkbox and worker start/finish buttons have been removed from live clinical modes. The same `ClinicalCapture` component is used for browser previews, with explicitly simulated readiness and no saved sensor data. Shared checks and research walking remain explanatory preview stages, not hardware simulation. Preview can trigger a labelled finish event to avoid waiting six minutes.

The app does not detect 10MWT boundaries, TUG chair contact or laps. Its quiet-stop endpoint can be wrong when a participant takes a long rest. The separately entered course/stopwatch form is optional research reference, not a patient requirement. A capture limit or interruption does not mark the clinical assessment completed. The TTS start callback is a software timestamp, not a verified acoustic timestamp. Extra latency and OS scheduling need device validation.

JSON and raw CSV carry `protocolExecution` provenance: flow version, protocol, offset of Go from capture start, cue source, elapsed time from Go, end reason and unverified clinical status. Raw CSV only reconstructs available metadata; absent measured outcomes remain absent. Pre-Go samples are retained rather than trimmed silently.


## Supervisor review: proposed next scope - 2 October 2026

Recommendations only; no app behavior changed in this review. Extend existing profiles, recording linkage, clinical flows and dashboard rather than rebuilding them. Prioritize 10MWT/TUG, use 2MWT secondarily and retain 6MWT in advanced/legacy access. Agree the exact course variant, timed distance and trial count with the clinician before editing speed arithmetic: a central 10 m zone with two 2 m zones requires 14 m total; the AbilityLab instrument sheet instead times central 6 m of a 10 m course. 2MWT requires measured distance, not just a timer.

Structure hemisphere, lesion location, affected body side and onset/chronicity with explicit unknown/source handling; subcortical is not a hemisphere. Walker eligibility differs from the earlier cane-only brief and needs clinical confirmation. Extend the current three-second stationary reference to five quality-gated seconds of natural stance, retaining original phone orientation and raw signals. This does not prove anatomical placement or body midline.

Evaluate Start/Stop/Lap commands on actual devices and all supported languages before promising offline recognition. Android 11 requires a separately verified route; native microphone integration requires a new APK. Record recognized commands separately from observed foot-crossing/chair-contact events. Worker timing remains the clinical reference until error is measured. Preserve standardized timed-test cueing.

Validate QC, cadence, lumbar regularity and phase detection before recovery trends. Few-shot adaptation follows repeated reference-labelled trials and a fixed-estimator calibration baseline; historical best is not the sole comparison. Full evidence and implementation gates: [AI model strategy](../wiki/concepts/gait-app-ai-model-strategy.md#supervisor-alignment-review-2-october-2026).


### First implementation batch - 2 October 2026

Clinical test setup now asks for affected hemisphere, affected body side, whole months since stroke or an explicit unknown, and whether the history is self/caregiver-reported or taken from a clinical record. Subcortical location remains a separate optional lesion-location field in the participant editor. Existing local profiles remain readable; a 10MWT, TUG, 2MWT or 6MWT cannot start until this minimum stroke history is reviewed. Research walking is unaffected. The selected clinical fields are saved in the participant and each session snapshot; the tidy feature CSV includes them. Participant age and sex requirements remain.

The clinical test menu places 10MWT and TUG first, 2MWT next, and research walk/6MWT under Other tests. The current 12 m/central 10 m course is explicitly tagged `10mwt-12m-central10m-v1`; the UI has not adopted another protocol variant pending clinical agreement. The result form shows the stored course/timed-zone lengths, computes speed from the stored timed distance, and requires worker stopwatch time for a completed 10MWT/TUG or measured distance/laps for a completed endurance test. These are form checks, not automatic event detection or standardized multi-trial administration.

The stationary capture now requires five continuously suitable seconds and five seconds of fresh readings from all three sensors before preserving the original three-axis reference. The baseline is captured before the movement/fit check, so later movement or the TUG return to sitting does not overwrite it. Old three-second recordings remain readable. Five seconds of a steady mounted phone still cannot confirm anatomical position or biological midline. No native packages or permissions changed; device testing remains necessary.

## Product correction: autonomous patient capture and phone estimates - 2 October 2026

The patient holds the phone only before mounting it on the lower back. Worker-ready and worker-finish buttons have been removed from the patient flow. The outcome-entry form remains optional for paired research reference collection; it is not a patient prerequisite. Automatic 10MWT/TUG saving now exists, but its stop event is provisional and not a clinical endpoint.

Target flow: one tap before mounting; unhurried spoken placement instructions; five-second standing reference and short movement/fit check; a clearly signalled Go and recorded start-event source; automatic finish and save; phone-generated distance/speed only when quality gates pass. Preserve raw data and return an explicit unavailable result when an event or distance is ambiguous. Two or three preparation steps check movement and fit, not personal step length.

For **2MWT**, automatically stop after 120 seconds from a documented cue or first-motion event, including rests. Estimate distance from accepted step events and a validated personal distance model; optional outdoor location may cross-check longer routes. For **10MWT**, the mounted IMU cannot observe tape crossings. A research estimator can infer crossing times from cumulative progress on the selected 12 m course, but pauses, step-length changes and early stops can make the result uncertain. Until paired validation establishes error, call it a phone-estimated walk rather than a clinically equivalent 10MWT speed. For **TUG**, candidate rise, turn, return and sitting phases need synchronized reference validation. Quiet standing or resting is not proof of final seat contact.

During development, collect multiple marked-distance walks with synchronized video/stopwatch or instrumented reference on the actual holder, including slow/asymmetric walking, aids, rests and phone shifts. Keep personal calibration versioned; do not overwrite it with the current test and then call that test accurate. Validate event/boundary, distance and speed errors on held-out patients and phones, with clinician-agreed acceptance limits. A published commercial sensor system showed speed/asymmetry-dependent error after stroke, so its performance cannot be transferred to this phone: [original study](https://pubmed.ncbi.nlm.nih.gov/37557187/). Speech recognition can assist with commands, but cannot be the sole patient stop mechanism when device/language support or speech is unreliable.

### Local hands-free implementation status — 2 October 2026

Clinical capture now arms after the full spoken explanation and three seconds of live stillness. It records before the spoken Go callback. Timed 2MWT/6MWT sessions save automatically at 120/360 seconds, including rests. In 10MWT/TUG, a provisional endpoint requires at least two seconds of sustained motion followed by eight seconds of quiet; a 180-second ceiling marks an incomplete capture. Emergency touch stop remains available but is not part of the normal patient path. Raw streams, Go offset/source and endpoint reason are retained. The phone does **not** claim a verified 10MWT timed-zone speed or TUG seat-contact time.

Post-hoc phone distance uses accepted candidate step peaks multiplied by a stored measured-route participant calibration where available, otherwise the experimental `0.413 × height` step-length heuristic. Without height/calibration or usable steps, distance is unavailable. Timed-test mean speed divides this distance by the whole Go-to-finish clock, including rests; 10MWT shows only whole-walk estimated speed. Neither the short fit check nor a quiet stop calibrates distance. Patient results and exports separate phone estimates from optional measured-course outcomes. A physical-device/holder study against synchronized floor-mark and chair references remains required.
