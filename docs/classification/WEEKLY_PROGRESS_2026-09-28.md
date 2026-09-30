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
