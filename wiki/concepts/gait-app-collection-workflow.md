---
type: concept
---

# Gait app collection workflow

This page tracks what the local GaitTrace phone app can capture and what still requires observer, course or clinical validation. It is an implementation record, not evidence that the app is a validated rehabilitation instrument.

## Local participant workflow

The Android source now includes a local participant registry with a coded label, demographic and clinical profile fields, favorite/archive state, and a session-time profile snapshot. A worker can select the participant before setup, review earlier sessions in a dashboard, and enter outcome notes after recording. The result form supports protocol labels for the research walk, 10MWT, 2MWT, 6MWT and TUG. Its worker-entered course distance and stopwatch time can be exported as comparison metadata. The profiles and recordings stay on the device; there is no account, synchronization or server-backed history.

## Measurement boundary

Optional research-reference forms calculate 10MWT speed from an entered timed interval and measured 10 m zone; 2MWT/6MWT can store measured laps and partial distance; TUG can store a reference time. The patient path does not require these entries. The phone separately estimates whole-walk distance/speed, but does not establish course boundaries, lap counts, chair rise/seat contact, or standardized administration. An optional Android foreground GPS distance cross-check is available after explicit opt-in; it retains aggregate distance/accuracy metadata without saving coordinates. Its output is not ground truth and may be unreliable indoors or on short routes.

The phone estimates distance as candidate step events multiplied by a stride scale. It starts with a height heuristic and can store a participant-specific scale after a worker records a measured total route distance for a research walk or 2MWT/6MWT. This follows the general step × stride approach documented by consumer trackers, but uses this app's candidate events and placement; its result is explicitly experimental. GPS distance is a separate optional outdoor cross-check. Neither phone-derived output is validated for post-stroke gait. A lower-back single-phone IMU cannot identify left/right limb, paretic side, true per-step length, foot clearance or neurological cause of asymmetry. Sensor-derived symmetry should remain descriptive and unclassified until independently validated against synchronized reference measurements. See the [assessment specification](../../docs/REHAB_ASSESSMENT_PRODUCT_SPEC.md#phone-only-distance-approaches-in-current-products-and-literature).

## Responsive setup and automatic participant creation

Updated 2026-10-01. Home uses a compact navigation grid and one fixed primary Start action. Setup has separate person, test, and sound/readiness pages. Sound playback appears at the top of the final page. Named language/audio settings and detailed instructions open on request. Height/walking aid have a direct button on the person page, and the current test is labelled Change test with selection marks. Shared screens bound the action area and allow scrolling at small heights or enlarged font sizes, while button labels can wrap within the available width.

Test setup requires a study label, age and an explicit sex selection, with Prefer not to say available. A new profile is saved on Start and its ID and snapshot travel with the recording. Existing profiles can be selected in setup. Identity uses the saved ID and normalized study label, never matching age/sex alone. Profile writes must succeed before recording begins, and retrying does not create another identity. Browser profiles use the same tab-only lifetime as browser recordings. Old unlinked recordings are not assigned to people by demographic guesses.

## Current implementation and gaps

The participant dashboard lists every stored recording, including practice and archived profiles, with a separate unassigned queue and plots up to twelve measured-speed outcomes for the most recent protocol when known course length and walking aid match; practice and simulated recordings are excluded from that trend. This is descriptive history, not a clinical trajectory score. The registry supports searching coded labels and editing profiles while prior session snapshots remain unchanged. Spoken completion feedback summarizes actual movement evidence and compares only with a matching previous non-practice test for the same participant; it withholds praise when the data are unclear. New GPS permission/quality paths, translations, usability and device behavior still need physical review. Clinical protocols need a therapist-led reference comparison before any result is described as a validated clinical outcome.

## Test protocol explanations

The setup screen now opens a three-step illustrated tutorial in English, Malay or Simplified Chinese for every protocol. Each step has a short patient instruction and read-aloud control. Full explanations are retained under Worker protocol notes. It explains the intended clinical measure and setup, timing or rest rules, worker responsibilities, and the sensor app's limits. The 10MWT uses the client's chosen 12 m layout but says this is one selected variant; a worker must time the marked middle 10 m, and the app's three-minute capture limit is not the clinical time. The 2MWT and 6MWT each keep rests inside the protocol duration, but their pace and administration differ. The 6MWT guide describes the ATS 30 m course and scripted encouragement, which GaitTrace does not reproduce; it suppresses extra walking commentary and turn reminders automatically, while the worker supplies the standard timed encouragement. The TUG guide describes the full chair-to-chair sequence and the worker stopwatch endpoint. See the sourced protocol detail in [the assessment specification](../../docs/REHAB_ASSESSMENT_PRODUCT_SPEC.md#protocol-workflow).

## Links

- [Client requirements and measurement boundary](../../docs/GAIT_APP_CLIENT_REQUIREMENTS.md)
- [Rehabilitation assessment specification](../../docs/REHAB_ASSESSMENT_PRODUCT_SPEC.md)
- [Current weekly app progress](../../docs/classification/WEEKLY_PROGRESS_2026-09-28.md)

### Discoverability and identity linkage (1 October 2026)

Home exposes Progress dashboard directly and names its secondary area Import and app information. Setup names Language and audio settings, shows a direct Set height and walking aid entry, and uses Change test plus radio marks to distinguish choices from static text. Height is explicitly useful for an experimental distance estimate but remains optional; missing height must not be replaced with a guess. Raw collection and measured-course outcomes do not require that heuristic.

Participant IDs on saved/imported recordings recover missing local profiles without merging by age, sex or labels. Recordings with no explicit ID remain visible under Needs participant assignment. Their detail page lets a user choose and confirm a known participant, or create one and return; original measurements and historical snapshots are not rewritten. Unknown identity still needs human confirmation. Raw CSV now round-trips participant ID, label and height. Six-minute JSON files pass the bounded import duration check. CSV remains a single-recording raw import; JSON retains richer session metadata.

Dashboard lists include practice, unassigned and archived-participant recordings. Only actual device recordings with known comparable protocol/course/aid and measured outcomes enter speed trends. Older Android index entries are checked against their saved file one at a time; new summaries carry a device-recording flag. Automated tests cover linkage, import/export and dashboard visibility; physical small-screen review remains pending.


## Protocol-specific capture and preview (1 October 2026)

Research walking retains the first-step start. Clinical modes use shared protocol definitions for instructions and preview. Their sensor capture begins before Go; the app clock starts at the speech-start callback, or automatically after stillness with voice off. Standing calibration is retained when returning to the TUG chair. 10MWT/TUG now auto-save after sustained movement followed by eight seconds of quiet; that endpoint is unverified and the three-minute capture ceiling is incomplete. 2MWT/6MWT use 120/360-second clocks including rests. Generic praise and straight-path warnings do not play during clinical capture. Standardized 6MWT encouragement is not yet implemented.

Clinical preview runs the same capture-screen controller with simulated readiness and no persisted data; setup checks and research-walk preview remain labelled explanatory stages. JSON/raw CSV preserve Go offset and finish provenance; JSON also contains the protocol-specific phone estimate. No automatic boundary, lap or chair event verification or acoustic timing validation is claimed. Optional measured outcomes remain separate for research reference. See the product spec for the full control matrix and source links.


## Supervisor measurement-first implementation (2 October 2026)

The first local batch adds structured hemisphere, affected body side, chronicity known/unknown with whole months, and history provenance to clinical setup. Older saved profiles can be reviewed in place; clinical protocols require the minimum history before starting, while research walking does not. New fields travel in the participant snapshot and tidy feature CSV. This is user-entered history, not a diagnosis inferred from sensors.

The menu presents 10MWT and TUG as primary, 2MWT as secondary, and keeps 6MWT/research walk accessible under Other tests. The current 12 m course/central 10 m timed-zone variant is explicitly tagged; there has been no switch to the separate 10 m course/central 6 m instrument-sheet variant. Marking an optional reference assessment complete still requires worker time or measured endurance distance/laps. Patient capture and phone estimates save independently. Reference clinical speed uses the stored timed-zone distance.

The app now waits for five consecutive seconds of suitable standing/sensor readings and preserves that baseline before the guided movement check. It records device gravity and raw axes, not anatomical placement or body center of mass. Automated tests and TypeScript pass; actual phone/holder and therapist-reference checks remain pending. Offline Start/Stop/Lap commands, a different 10MWT variant, validated symmetry metrics and few-shot adaptation remain separate future work. See [[gait-app-ai-model-strategy#supervisor-alignment-review-2-october-2026]].

## Corrected patient workflow target (2 October 2026)

The user confirmed that patients must complete tests with the phone inaccessible on the lower back: no worker-operated stop or entered stopwatch/distance should be needed in the patient path. The local clinical controller now arms after spoken instructions and three seconds of live stillness, starts capture before Go, and saves without further taps. 2MWT/6MWT use fixed clocks including rests. 10MWT/TUG use an eight-second quiet-stop heuristic after sustained motion; long rests can end early, and 180 seconds is an incomplete safety ceiling. Their optional worker form supports paired development reference, not patient operation.

The path is one tap before mounting, unhurried audio setup, five-second standing reference, movement/fit check, documented Go cue, automatic stop and raw-data save. The phone still cannot see 10MWT tape crossings or confirm TUG chair contact. It reports whole-walk experimental distance/speed from accepted candidate steps and height or prior measured-route calibration; timed-test mean speed includes rests. If inputs or usable steps are absent, distance is unavailable. Two or three preparation steps are a fit check, not distance calibration. See the [product specification](../../docs/REHAB_ASSESSMENT_PRODUCT_SPEC.md#local-hands-free-implementation-status--2-october-2026).

## Free distance provider feasibility (2 October 2026)

Release documentation is maintained in [android/CHANGELOG.md](../../android/CHANGELOG.md), with build/use guidance in the module README. Version 0.3.0 is an application/source version; the next Android build number is not assigned yet. Publication-review documents remain ignored in `android/dist/`, rather than serving as release records.

**Local implementation update:** Google Recording API comparison capture is now integrated in source as an opt-in Android experiment. It uses the accountless `FitnessLocal` API, not legacy Fit OAuth. Preparation requests activity permission while the phone is accessible; Go-to-finish detailed records, arrival/poll timing, missing-output and cleanup diagnostics are saved separately from IMU/clinical outcomes. No Google distance controls the test end. EN/MS/ZH UI, JSON and CSV exports are included; app version 0.3.0 requires a new native APK. Expo autolinking and SDK binary method checks passed; native compilation and phone accuracy/latency trials remain pending. See [build and physical validation guide](../../android/modules/gait-google-recording/README.md). No paid service or account was activated.

Additional external-service check: IndoorAtlas's free access is a 30-day trial followed by paid plans, while Spectacular AI's native Android wrapper requires a commercial licence. Neither was enrolled or integrated. A measured printed-marker course with local AprilTag/OpenCV pose estimation is another free-software candidate: it adds a physical metric reference while preserving lower-back screen-out mounting. Researcher course preparation, camera calibration, backward-facing visibility and protocol boundary validation are required. User acceptance of fixed printed references is pending. No calibrated app output is claimed; details and primary sources are in the product specification.

The user requires automatic distance with no paid service. Official provider documentation confirms that Google Recording API offers on-device distance data but no clinical lumbar calibration guarantee; Health Connect stores source records; fused location is already an outdoor cross-check; Wi-Fi RTT requires surveyed compatible infrastructure. A provider name is not an accuracy validation.

The user confirmed screen/selfie-camera-out mounting; rear lenses face the body. Keep the lower-back position and arrangement. ARCore is unsuitable because front-camera mode disables world tracking, even on supported phones. OpenVINS is the free open-source feasibility candidate for a custom front-camera/IMU implementation. Source inspection of the Android port at `f0c465695c67c0eac786f4edf83a68109a6a58a9` found rear-camera selection, not working front-camera support. Adaptation needs device/capture-mode camera–IMU calibration, timestamp and acquisition-rate checks, an unobstructed selfie lens, GPL license compliance and paired clinical-course validation. No subscription or billing account is proposed. No native camera integration, new APK, real-device tracking test or accuracy result was produced. The [product specification](../../docs/REHAB_ASSESSMENT_PRODUCT_SPEC.md#free-distance-provider-feasibility-audit--2-october-2026) records primary sources, development prerequisites and the fail-on-lost-tracking contract. Existing distance remains experimental.
