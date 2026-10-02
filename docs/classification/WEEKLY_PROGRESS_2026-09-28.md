# Week of 28 September 2026: local rehabilitation assessment workflow

## Outcome

Extended the GaitTrace Android workflow to locally link participant profiles, sensor sessions and worker-entered rehabilitation outcomes. Nothing was published or pushed in this batch. The workflow remains on-device and needs implementation review, physical-device review and clinical comparison before use as an outcome instrument.

## Implemented in source

- Added a local participant registry with coded labels, favorite/archive actions, demographics, stroke history, height/weight, pre-morbid gait and orthopaedic notes, and usual walking aid. Selecting a profile carries a snapshot into the session.
- Added protocol labels for the research capture walk, 10MWT, 2MWT, 6MWT and TUG. The research-walk duration remains separate from standardized protocol labels.
- Added a result form for completion status, timed interval, measured course distance, laps, rests, perceived exertion, symptoms, worker notes and optional observed scale/score. Results are written into the local session JSON.
- Added a participant dashboard that lists that person's saved non-practice assessments and plots up to twelve measured-speed values when protocol, course and walking aid match.
- Extended the comparison-feature CSV with participant metadata and worker-entered protocol outcomes. Measured speed is distance divided by the entered time. The height-based candidate-step distance remains an experimental export descriptor and is not substituted for measured-course results.
- Added an explicit single-phone distance estimate from candidate step events. It starts from a height-based scale and, after a worker enters the measured total distance for a supported full walk, can calibrate a participant-specific event-to-distance scale stored locally. JSON and feature CSV distinguish this estimate and its method from measured-course distance/speed.
- Removed the automatic timeout from mounting and movement-check phases so users can take the time required for setup.

## Measurement and safety limits

The protocol screen/form is a structured capture aid, not a complete validated administration of 10MWT, TUG, 2MWT or 6MWT. A worker must set/measure the course and observe protocol events. There is no GPS capture, boundary/lap automation, chair-event detection, bilateral limb attribution or automatic neurological asymmetry score. The dashboard's measured-speed chart is descriptive only. Profile search/edit and full translation coverage for newly added screens remain unfinished. Single-phone distance estimates and the personal calibration are experimental; neither is validated speed or distance for this post-stroke population.

## Evidence state

No new participant recordings, therapist comparisons, clinical evaluations or model experiments were performed. No test or build command was run in this work batch. Physical handling, speech, protocol flow, exports and small-screen layouts remain to be reviewed on a device. Preserve the source changes locally for user review; do not push until the proposed file scope is reviewed and approved.

## Follow-up: 29 September 2026

Added an optional Android foreground GPS distance cross-check. The participant must enable it; the app requests location permission during setup, starts watching after the first detected step, and saves aggregate distance, accepted-fix count and median reported accuracy. It does not save coordinates or upload a route. The result is explicitly a rough outdoor cross-check; short, indoor or obstructed routes may be unreliable. Raw and feature CSV exports, JSON, and the result view include the GPS summary separately from measured-course outcomes and the candidate-step estimate.

The local participant registry now supports coded-label search and editing. Editing updates the current profile while previous session snapshots remain unchanged. Completion voice feedback now uses current movement evidence and compares only against the same participant on a matching protocol, duration and walking-aid setup; unclear movement gets an uncertainty message. Added deterministic checks for GPS filtering/export privacy and evidence-based spoken feedback. TypeScript check and application tests pass after updating the test harness to mock the new Expo native module. No physical GPS validation or Android build was performed. Because this adds an Expo native module and Android location permission, distributing this change requires a new APK build; it cannot be delivered as an OTA-only update.

The setup screen now provides a full, listenable guide for the research walk, 10MWT, 2MWT, 6MWT and TUG in English, Malay and Simplified Chinese. The guide distinguishes source protocol timing from the app's sensor-recording timer, describes worker course/stopwatch/lap duties, allows 2MWT/6MWT rest without stopping the protocol clock, and notes that ATS 6MWT cueing and the 30 m course are not reproduced by GaitTrace. It directs workers to turn off app voice and direction reminders during a standardized 6MWT. The 10MWT guidance uses the project's 12 m layout but identifies it as the selected project setup, not the sole accepted format. Added translation-coverage checks for every complete protocol guide. Validation: all 81 app tests pass and TypeScript check passes; no native build or physical-device review was performed.


## Follow-up: 30 September 2026 ? layout and participant usability

Replaced the five-button home footer with one primary Start action and a compact navigation grid. Setup now separates person, protocol and sound/readiness into three pages with persistent Previous/Continue/Start controls. The sound sample appears first on the readiness page; optional settings open in a separate More menu. Language, voice/direction/practice settings, GPS and optional participant details no longer expand the underlying setup page. Saved participants have a searchable separate selector, and the test chooser shows only the current selection until opened. Menus use safe-area insets and bounded scrolling with a persistent Done action. Two additional renderer checks verify menu state preservation and protocol selection. Shared screen action areas are height-bounded and scrollable for constrained screens and larger fonts, and full-width button styling no longer conflicts with horizontal rows.

New participants are created directly on starting a test, requiring a study label, age and explicit sex choice (Prefer not to say is accepted). Existing profiles can be selected in setup. Duplicate labels cannot silently merge people, storage failures block recording, and retrying preserves the participant identity. Historical session snapshots remain separate. Browser participant functions now support the same tab-only lifetime as browser recordings.

Replaced the patient-facing paragraphs with three short tutorial steps per protocol, scalable path/chair diagrams and read-aloud. Detailed protocol notes remain available separately. Malay and Chinese coverage is checked against the actual guide/tutorial objects, correcting two pre-existing exact-key mismatches in the longer notes. This batch adds no native dependencies.

Verification: TypeScript passes, all 88 app tests pass, and both Android and web production bundles export successfully to the ignored local `android/dist/ui-review/` directory. Tests include creation/linking, identity changes, retry deduplication, storage-failure gating, translation coverage from actual guide data, and tutorial navigation/speech cancellation. Browser visual inspection was unavailable because the browser runtime reported no connected browsers. Phone screen geometry and device speech playback therefore remain pending physical review; renderer tests and bundle export are not presented as that review. Changes are local and unpublished.


## Proposed publication scope for the 30 September fixes

These local source/documentation changes are ready for review. Generated bundles and dependencies remain ignored. No native configuration or dependency changes are included.

```text
M android/App.tsx
 M android/src/components/BigButton.tsx
 M android/src/components/Screen.tsx
 M android/src/screens/HomeScreen.tsx
 M android/src/screens/ParticipantsScreen.tsx
 M android/src/screens/PrepareScreen.tsx
 M android/src/store.web.ts
 M android/src/translations.ts
 M android/tests/experience.test.cjs
 M docs/GAIT_APP_CLIENT_REQUIREMENTS.md
 M docs/REHAB_ASSESSMENT_PRODUCT_SPEC.md
 M docs/classification/WEEKLY_PROGRESS_2026-09-28.md
 M wiki/concepts/gait-app-collection-workflow.md
 M wiki/index.md
 M wiki/log.md
?? android/src/components/ProtocolTutorial.tsx
?? android/src/experienceMessages.ts
?? android/src/protocolGuides.ts
?? android/src/protocolTutorials.ts
?? android/src/testParticipant.ts
```

## Follow-up: 1 October 2026 ? discoverability and recording identity

Replaced ambiguous setup More options with Language and audio settings, exposed height/walking aid on the person page, and labelled the current test Change test with radio marks. Home exposes Progress dashboard and labels its secondary controls Import and app information. Height remains optional with an explanation that it supports an experimental heuristic, not measured distance; users should not invent an unknown height.

Saved/imported explicit participant IDs can restore missing local profiles. Unknown identities remain in a visible Needs participant assignment queue; recording details allow explicit selection and confirmation or creation of a profile followed by return. Assignment preserves raw signals, demographics and existing historical snapshots. The dashboard now includes practice and archived-profile recordings but excludes practice/simulation from measured-speed trends and requires known comparable protocol/course/aid. New native index entries identify device recordings; older entries are checked against the saved file without retaining all raw streams in dashboard state.

Raw CSV includes participant ID, label and height and imports those columns when present; older CSV remains supported and unassigned when identity is absent. JSON imports now accept six-minute recordings within a ten-minute safety bound. Single-recording raw CSV import remains the supported format; a combined multi-session CSV is not a bulk import path.

Validation: Android and web production bundles export successfully to ignored local output. 93 automated tests pass, including Android/browser assignment persistence, raw-data preservation, profile recovery without demographic merging, CSV identity round-trip, six-minute JSON import and dashboard inclusion of unassigned/practice/archived history. TypeScript passes. No physical-device usability validation was performed. No new native dependencies. Changes remain local for review.

### Proposed publication scope ? 1 October

- New: `android/src/participantLinks.ts`, `android/src/components/RecordingParticipant.tsx`.
- Modified app: `experienceMessages.ts`, `exportData.ts`, `reviewRecording.ts`, `store.ts`, `store.web.ts`; screens `DashboardScreen.tsx`, `DetailsScreen.tsx`, `HistoryScreen.tsx`, `HomeScreen.tsx`, `PrepareScreen.tsx`.
- Tests: `android/tests/experience.test.cjs`, `android/tests/recording.test.cjs`.
- Documentation: `docs/GAIT_APP_CLIENT_REQUIREMENTS.md`, this weekly page, `wiki/concepts/gait-app-collection-workflow.md`, `wiki/index.md`, `wiki/log.md`.

Dependencies and generated bundles are excluded. Publication requires review and approval of this scope.


## Follow-up: 1 October — protocol-specific recording guidance

Implemented shared protocol definitions and a separate clinical capture controller. Research walking retains its first-step clock; clinical modes capture before Go and start their independent clock at the speech-start callback or worker tap. 10MWT/TUG use worker-confirmed finish, with a three-minute capture ceiling explicitly distinct from clinical completion. 2MWT/6MWT clock 120/360 seconds including rests. Generic directional warnings and behaviour praise are suppressed during clinical capture. The worker supplies standardized timed cues; automatic clinical event detection remains unavailable. Standing baseline is preserved before the TUG seated start.

Clinical browser preview reuses the same controller without sensor persistence; common setup/research preview is explanatory, and no readiness is claimed. Removed obsolete 20-second setup wording from that walkthrough. The movement-check stop instruction is now emitted when the required sustained motion has been observed. New English/Malay/Chinese guidance and selected-state symbols were repaired after finding shell encoding corruption; a regression test rejects replacement runs and missing Chinese script.

Protocol metadata (Go offset, source, elapsed time, end reason) survives JSON and raw CSV round-trip. Worker outcomes remain separate. Tests cover complete intro before starting, delayed/missing Go, 2/6-minute deadlines with rests, sensor loss, manual TUG/10MWT finish, capture-limit status, all clinical branches, baseline preservation and metadata round-trip. Physical speech/timing/layout validation remains pending; automated tests inject events.

Additional publication scope: `android/App.tsx`; new `android/src/protocolFlow.ts`, `protocolMessages.ts`, `components/ClinicalCapture.tsx`; modified `placement.ts`, `sensors.ts`, `protocolGuides.ts`, `protocolTutorials.ts`, `translations.ts`, `screens/RecordScreen.tsx`, `screens/ResultScreen.tsx`, `screens/WalkthroughScreen.tsx`; `docs/REHAB_ASSESSMENT_PRODUCT_SPEC.md`, together with the earlier 1 October files/tests/wiki scope. No new native packages. Keep local for review before publishing.

Final verification for protocol flow: 102 tests pass, TypeScript passes, and Android/web production exports succeed. Refreshed the local preview at http://127.0.0.1:8765/ and verified HTTP 200. No connected browser was available for visual inspection. Source changes remain unpublished.

## GaitTrace AI model research synthesis — 1 October 2026

Reviewed the actual horizontal lower-back Android workflow, protocol outcome boundaries, frozen classifier and healthy virtual-IMU pilot against primary research on trunk asymmetry, smartphone gait events, longitudinal stroke mechanics and digital-measure validation. The research recommendation is to prioritize quality-gated straight-walk segmentation, cadence/step timing and trunk-pattern regularity with uncertainty, then comparable within-person trends anchored to worker-measured 10MWT/TUG/2MWT/6MWT outcomes. The grant's clinically parameterized healthy-to-stroke-like synthesis remains a separate primary research objective and is not yet complete. The 15-member stroke classifier is not suitable as a patient-facing diagnosis or recovery score; its specificity stress and missing independent cohort remain unchanged. Detailed citations, model stack and admission gates are in [the wiki strategy](../../wiki/concepts/gait-app-ai-model-strategy.md). This was a literature and local-evidence review only: no dataset acquisition, model fit, app behavior change or clinical validation. Files remain local for publication review.

## Publication verification — 1 October 2026

The approved app, protocol and research-note scope passed 102 automated tests, TypeScript, Android and web exports, and a Git whitespace check. Physical-device validation remains pending. No native packages or app configuration changed.


## Supervisor direction review - 2 October 2026

Compared the supplied academic-supervisor synthesis with current Android profiles, sensor calibration, clinical capture, outcomes and the previous functional-model strategy. Existing registry/linkage/dashboard and worker-managed clinical flows are implemented; structured hemisphere/affected-side/onset fields, speech intent recognition, five-second calibration and validated recovery estimators are not. Recommended a measurement-contract and paired-validation sprint before few-shot training, with primary 10MWT/TUG and secondary 2MWT. Corrected hemisphere versus lesion location, 10MWT course/timed-zone variants, distance-dependent 2MWT, voice latency versus clinical boundaries, and Android 11 offline-recognition limitations. A native speech addition would require a new APK.

Updated the existing product specification, AI strategy, wiki index and append-only log. The grant synthesis deliverable remains separate pending supervisor confirmation of any scope replacement. This was source/literature review only: no app behavior change, dataset acquisition, experiment rerun, new model fit or clinical validation. Documentation changes remain local for publication review; demo artifacts remain excluded.


## Supervisor alignment: first app batch - 2 October 2026

Implemented structured clinical intake for affected hemisphere, affected body side, explicit known/unknown stroke chronicity and history source on participant and test setup; clinical tests require it before recording. Existing profiles remain available for completion. The participant snapshot and tidy feature export retain the added metadata. Reordered clinical test choices around 10MWT/TUG, then 2MWT, with 6MWT/research walk still accessible. Tagged the existing 12 m/central 10 m 10MWT variant, removed a fallback speed numerator when the timed distance is unknown, and require worker time or endurance distance for a completed assessment.

Changed stationary baseline capture from three to five continuous suitable seconds of actual three-sensor readings and preserve it before the movement check. Raw values are unchanged; old baselines remain readable. This does not validate lower-back anatomy, new symmetry features, speech recognition or clinical outcomes. No native dependencies changed. TypeScript and 105 automated tests passed; physical-device/therapist comparison remains pending. Local changes await publication review together with the earlier supervisor strategy notes; demo files remain excluded.

## Autonomous distance/speed requirement correction - 2 October 2026

The user clarified that a patient must run a test with the phone inaccessible on the lower back, without a worker stopping capture or entering stopwatch/distance results. Current 10MWT/TUG controls therefore remain a reference-collection route, not the final patient flow. 2MWT already has an automatic 120-second clock; its phone distance is experimental. Revised the product and wiki plan for automatic start/finish event candidates, quality-gated distance/speed and explicit unavailable outcomes. Tape crossings and TUG seat contact require paired reference validation because the current IMU does not observe them directly. This review changed planning documents only; no automatic clinical endpoint implementation or validation result is claimed. Local changes await publication review.

## Hands-free clinical capture implementation - 2 October 2026

Removed the worker-presence checkbox and the worker start/finish requirement from the patient clinical flow. After setup and the full spoken protocol instruction, the phone waits for three seconds of live stillness, starts raw capture before the spoken Go and records the Go callback. 2MWT and 6MWT stop and save at 120 and 360 seconds; rests stay in the clock. 10MWT and TUG provisionally stop after at least two seconds of sustained movement followed by eight seconds of quiet. Long rests can cause an early finish, while the 180-second ceiling is incomplete; neither path verifies tape marks or chair contact. The emergency touch stop remains a fallback.

Patient results and JSON/tidy feature CSV retain phone-based distance and speed separately from optional measured-course research outcomes. Timed-test mean speed uses the whole Go-to-finish interval, including rests. The 10MWT display says whole-walk speed, not central timed-zone speed. Distance still depends on accepted candidate steps and participant calibration or an experimental height heuristic; without those inputs it is unavailable. Protocol instructions and tutorials were updated in English, Malay and Chinese. TypeScript and automated tests pass; actual holder, device audio, false-stop, slow/asymmetric walking and paired clinical validation remain pending. All changes are local for publication review; no new native package was added.

## Free distance-provider feasibility audit - 2 October 2026

Audited official Google Recording API, Health Connect, fused location, Wi-Fi RTT and ARCore against the user's no-paid-service, one-lower-back-phone, automatic-distance requirement. Reused the previous consumer-service assessment instead of presenting it as a new finding. New evidence: modern accountless Recording API includes distance, but publishes no clinical calibration guarantee; ARCore gives metre-scale camera/IMU pose and Google lists Redmi Note 10 Pro as supported. Local ARCore is a plausible free SDK route only with an exposed rear-camera-out mount; the current screen-out configuration points the rear camera at the body and selfie-camera mode has no world tracking. Wi-Fi RTT requires compatible surveyed AP infrastructure and does not meet universal phone-only use.

Documented provider capabilities, costs/physical prerequisites, horizontal progression, tracking-failure withholding and paired reference validation in the existing product spec and wiki. User clarification resolved the arrangement: screen/selfie camera faces the room, rear camera faces the body. ARCore is therefore excluded without changing the mounting. Investigated OpenVINS and inspected Android-port commit `f0c465695c67c0eac786f4edf83a68109a6a58a9`; it prefers the rear camera. A front-camera adaptation is an untested free prototype candidate, requiring per-device/capture-mode camera–IMU calibration, native acquisition/timestamp checks and paired course validation. It is not an implemented distance provider. No anatomical relocation is proposed. No paid account or API key was created; no native integration/new APK, trial, model training or accuracy result is claimed. Documentation-only audit remains local with the existing unpublished app changes for final user review.

Renewed external-service request: verified IndoorAtlas's 30-day trial/paid plans and Spectacular AI's commercial native Android wrapper; neither qualifies as verified ongoing free Android deployment. Checked official AprilTag/OpenCV pose-estimation requirements for a measured printed-marker alternative. Documented physical scale, camera calibration, course-frame geometry, backward-facing camera coverage, crossing convention and loss-of-tracking constraints. Asked whether researcher-prepared printed references are acceptable; no assumption of acceptance or software integration. Updated existing product spec/wiki/index/log in the same local batch. No app code, dependencies or generated research artifacts changed in this follow-up.

## Google on-device distance comparison integration - 2 October 2026

Publication scope reviewed and explicitly approved by the user: earlier clinical/hands-free changes and the Google comparison batch. Added `android/CHANGELOG.md` and README/wiki links at the user's request to organize version records. Version 0.3.0 is the source/app version; APK build assignment, native compilation and phone validation remain pending. Generated publication reviews stay ignored in `android/dist/`. TypeScript and all 117 tests were rechecked successfully before staging. Commit/push results are recorded by Git, not inferred from source versioning.

User authorized integration for testing. Added a local Expo Android module using Google Play services Fitness 21.3.0 and accountless `LocalRecordingClient` distance/steps. Preparation includes an opt-in checkbox, full Play services capability check and physical-activity permission before mounting. Research capture-start or clinical audible-Go defines a fixed query window. Two-second polls and bounded final reads preserve record intervals, first-seen times, query/return timing, null for missing output, API errors and cleanup state. Boundary-straddling/overlapping/invalid records are excluded rather than prorated. Google outputs are experimental comparison data and never stop the clinical test or replace raw IMU/reference measurements.

Added translated EN/MS/ZH setup/result text, JSON diagnostic persistence/validation and named Google summary columns in raw/feature CSV. Existing exports and unrelated local app changes remain intact. App/package version 0.3.0 with matching lockfile records the native change; existing remote build numbering/runtime policy remains. New APK required; no new paid subscription/account or cloud build initiated. Source module is autolinked and expected API symbols were verified against Google's published SDK AAR. TypeScript, all 117 automated tests, Android/web Metro exports and whitespace checks passed. These are JavaScript/contract checks, separately from native/device verification; the current environment has no detected Java/Android SDK in usual locations, so native compile and physical accuracy/latency validation are pending. The module README provides the actual-holder measured-course trial plan. Product spec, wiki workflow/index/log updated in the same local batch; no push.


## Dedicated short Google distance experiment - 2 October 2026

User requested a separate experiment because setting up a 12 m course is impractical for initial API testing. Local Android source now exposes Home > Import, research tools and app information > Research tools > Google distance trial, with measured 2/3/5 m routes (default 3 m). No clinical-test chooser is required. Participant linkage, permission-before-mounting, five-second standing reference and movement/fit checks are retained. The spoken cue asks the user to return to the start after setup, wait for Begin, then walk to the mark and stand still. Raw IMU starts after first-step detection; four seconds of continuous quiet automatically ends the trial, with a 60-second safety limit. Google querying begins at the audible cue (first-step fallback), retains a fixed stop boundary, and allows delayed post-stop reads for up to 30 seconds of waiting plus request time. The rest tail is part of the Google query interval; its mean speed is not moving-only speed.

The result asks whether the finish was reached before offering a direct full-JSON export. Reference route, completion and endpoint survive JSON and raw CSV review. Google records remain distinct from measured reference and raw IMU; no missing data is fabricated or replaced by a height estimate. A rest can terminate this engineering experiment early; the user can report that explicitly. Trials have versioned metadata and practice tagging, remain linked to participants/history, and are excluded from clinical speed trends and personal distance calibration. Normal clinical flows are unchanged. EN/MS/ZH text added.

Verification: TypeScript, 123 automated tests and Android/web Metro exports passed. These are software/contract checks, not native compilation, physical validation or measured accuracy. Google short-route availability and latency must be assessed on the actual holder; a new APK containing the Google module remains required and has not been built. This follow-up is local pending publication review. No model training or new dataset acquisition.

Publication follow-up: user approved pushing the short-trial batch and starting the existing Android preview APK build on 2 October 2026. Build status and identifiers remain pending until EAS confirms completion.


Build/publication result (2 October 2026): commit `54fb0f4` was pushed to main and all three GitHub workflows passed. EAS preview build `d3529b4c-e5f5-443c-9a15-01e4f7286bc8` completed successfully as GaitTrace **0.3.0 / Android build 6**, using the existing application/signing identity. Native Google module compilation passed. Runtime `a48c2ed43ddd2142beaa39b7f8031b8fff327407` matches the published Android preview update group `8e92c2d5-ef7f-499d-b5ad-470471c488b2`. [Direct APK](https://expo.dev/artifacts/eas/5sYVRhaXoeMJQDYTPrjgfXq7aSLe2wTlboCAzbZFoqU.apk). Local download target: `android/dist/apk/GaitTrace-0.3.0-build6.apk` (ignored). Physical installation and Google distance accuracy/latency remain unvalidated. Build-result documentation is retained locally for review; generated APK/log/metadata are not source commits.


### Actual 3 m trial evidence - 2 October 2026

Inspected export `gait-2026-10-02T09-41-45-834Z-18c37e2e.json` from build 6: 7.465 s of raw accelerometer/gyroscope/magnetometer at 82.15/81.77/36.61 Hz, finite samples and monotonic native timestamps with maximum gaps below 41 ms. Google returned no records across 10 successful reads including a final read 30.457 s after capture end; distance/steps/speed remain unavailable. No API errors or application boundary exclusions occurred. This is an availability failure for this trial, not measured Google distance error or proof of the underlying cause. User confirmed tapping Stop immediately at the finish, so automatic quiet-stop was not tested. The separate height-based estimate was 4.94361 m against the entered 3 m reference (conditionally +64.79%); it is not validated distance. Seven candidate peaks/70.59 steps per minute remain unverified, and clinical symmetry is undetermined. Raw data may support engineering analysis; this short trial does not validate gait outcomes or training labels.

Local audit: `android/dist/verification-google/trial-18c37e2e-review.md` and `.json` (ignored); original export remains outside source. Concrete next gap: separate broader-context/aggregate provider diagnostics while subscribed, preserving original test-window provenance and not attributing setup movement to the 3 m trial. Provider batching/availability/query behavior is unresolved. No implementation fix, model training, new dataset acquisition or push in this review.


### Connected-phone diagnostics (no new walk) - 2 October 2026

User chose diagnostics only. ADB confirmed installed 0.3.0/build 6 on Redmi Note 10 Pro / Android 11, granted activity recognition for both GaitTrace and Play services, Play services 26.36.33 and exposed hardware step-counter/detector sensors. Historical sensorservice entries show Google's Fitness LocalSensorAdapter requested 60,000,000 microseconds sampling/batching on a step counter (17:38:58 registration, 17:42:16 removal). Earlier JSON final empty read was about 17:42:16, 30.457 seconds after capture stop. This makes observation latency a plausible unresolved issue, not a proven root cause or new successful distance query. Narrow provider query behavior remains unresolved. Release APK private storage is unavailable through run-as; no bypass attempted.

Ignored diagnostic report: `android/dist/verification-google/connected-phone-diagnostics-2026-10-02.md`. Next implementation candidate is diagnostic-only broader-context queries plus a longer bounded read window while preserving fixed trial timing and separate context totals. No new walk, recording, app-data reset, code change, APK install, permission change, model training or push.


### Stationary Google API access check - local implementation, 2 October 2026

User clarified that basic API-access testing should not require walking or long waits, and requested a fresh call while connected by cable. Added a dedicated Research tools quick-check screen: availability/permission, subscription, 60-second and 600-second context reads, then unsubscribe. No participant, placement, countdown or gait recording. Explicit API-success versus records-available states prevent interpreting empty responses as failed connectivity or zero walking. Context counts are not trial distance; waving is not gait validation. Four-second request timeouts, failure cleanup and late-subscription cleanup included, with translated EN/MS/ZH UI and structured technical logs.

TypeScript, all 126 automated tests and Android Metro export passed. Native runtime fingerprint is unchanged and matches installed 0.3.0/build 6 (`a48c2ed43ddd2142beaa39b7f8031b8fff327407`), so no new APK is required for this screen. Publication was authorized on 2 October 2026; compatible update delivery and actual phone execution remain pending. No 90-second wait or normal clinical timing change was implemented. Earlier 10 successful API calls remain historical evidence, not a fresh live run of this check.
