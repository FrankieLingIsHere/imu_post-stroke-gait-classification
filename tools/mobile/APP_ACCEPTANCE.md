# GaitTrace reproducible feature acceptance

## Current app status - 20 October 2026

Local package: **0.3.19 / build 31**. Automatic distance checks phone setup before participant entry; **Record motion only** remains available without camera calibration and does not provide measured camera distance. New study IDs are automatic. Final setup guidance names actual outstanding checks and suppresses obsolete/repeated coaching.

Current evidence: **296 app tests**, TypeScript/native contracts and ten browser flows; **38 current-screen replays of historical Android numerical traces**; current Android first-use/smoke checks and a complete virtual-motion practice recording saved with all three sensor streams and participant linkage. This does not establish physical calibration convergence, distance accuracy, audible TTS or elderly independent use. Full details and reproducible controls are in the dated 20 October section below. Earlier dated sections are historical evidence and do not override this current status. No Git push or OTA publication.


## Handheld setup confirmations and calibration audit - 11 October 2026

Local setup now acknowledges each requested, measured movement (top-edge tilt, side-edge tilt and in-plane rotation) before the next instruction. If the fit finishes while an instruction is still speaking, the acknowledgment still finishes before saving. Failed guidance stops safely and cannot admit a late capture completion. All new cues have Malay and Chinese translations. The phone stays in its usual bag/window during this one-time handheld setup, before wearing it; it can be seen while moving, with a supported quiet baseline first. Ordinary mounted walking still uses the participant's natural quiet posture.

The old left/right cue was mapped to native X, although the corresponding portrait-screen motion rotates Y. Guidance now uses screen edges and maps X/Y with the actual display rotation, including naturally landscape tablets. Raw saved IMU axes remain unchanged. Android documents these fixed sensor axes and screen remapping in [Sensors Overview](https://developer.android.com/develop/sensors-and-location/sensors/sensors_overview#sensors-coords).

A separate Camera2 prior error was fixed: pixel-edge factory coordinates are converted to OpenCV integer-centre coordinates, with no truncation of odd/off-centre crops. Complete factory intrinsics no longer require optional focal-length/physical-size fields. Tests check source-point projection through the real transform. See [Camera2 intrinsic calibration](https://developer.android.com/reference/android/hardware/camera2/CameraCharacteristics#LENS_INTRINSIC_CALIBRATION). This correction does not establish that the bag/window optics are accurate.

Verification: 287 ordinary app tests, TypeScript, native transport/baseline/failure contracts and ten browser flows pass. The rebuilt x86_64 package passed the 17-control native preview/voice/start/cancel scenario, with every operation targeting emulator-5560. Speech completion callbacks were observed; audible voice is not established. New setup component regressions cover 23 cases, including an unfinished final acknowledgment, failed acknowledgment and all four screen rotations. The actual native package is BFDB26129A45840702B07259E943A45D5620AB13E01424F0251076834C8A81DF; UI controls/replies/screens are retained in android/dist/emulator-lab/interactions/2026-10-11T11-08-14-105Z/.


Final rebuilt-JNI rerun: all ten declared outcomes pass with source APK bfdb26129a45840702b07259e943a45d5620ab13e01424f0251076834c8a81df; the 130 s and 140.55 s recovery cases still complete. Its recorded native traces pass through the revised screen in 33 checks. Full current hashes/paths are in android/dist/setup-usability-review/confirmations/verification.json. The first rerun failed from emulator ENOSPC before the noise estimator started; its traceback/logs remain. Disposable test copies were removed, capacity/output-first cleanup added, and a complete fresh rerun passed. Partial suites now report passed=false.

### Numerical findings: do not equate a saved fit with accurate calibration

The notebook freshly compared joint estimation, optics-only with oracle alignment/timing, and alignment-first then optics. Stage flags are host-only; the app cannot select these experimental modes. On the same 180 s software fixture, the joint fit retained 8.6 cm translation error and principal-point errors of -9.5/+3.7 px. Alignment-first retained 18.2 cm translation error. The oracle optics fit was much closer, but it knows parameters an unknown phone does not supply reliably. Therefore the naive staged approach was rejected for production.

Frozen fits were evaluated on a separately rendered scene and motion, without scaling them to route truth:

| Frozen calibration | Held-out synthetic trajectory RMSE | Synthetic path-length error |
| --- | ---: | ---: |
| Previously saved Android perturbed-prior fit | 8.3 cm | -3.69% |
| Fresh host joint fit | 7.4 cm | -2.67% |
| Host alignment-first/optics fit | 15.0 cm | -3.58% |
| New depth-ordered renderer fit | 9.6 cm | -4.22% |

These are 38 s analytic 3D loops (known path 25.65 m), not patient walking or phone distance validation. A separate oracle control with 90-degree camera/IMU rotation, nonzero translation and a 20 ms clock offset produced 4.6 cm RMSE and -1.15% path error; it checks convention/timing execution, not estimation of unknown parameters. Ideal straight 3 m endpoint checks alone looked much better (errors below 1 cm), demonstrating that those checks can miss calibration bias.

The renderer also had incorrect overlap order for parallel textured planes. New v2 controls render far-to-near; all original controls and failures are retained. Correcting this did not eliminate the calibration bias. Current evidence supports coupled parameter estimation as a problem; it does not identify one proven root cause or a production fix.

**Still unresolved:** an accuracy-qualified automatic calibration method and an independent on-phone validation stage before profile saving. The current app admission still uses measured coverage, numerical uncertainty and a fresh stable tail; it does not run the held-out research test or prove absolute accuracy. We have not silently loosened its thresholds, claimed those recommendations are implemented in the app, or deployed the worse staged estimator. Physical mounted optics, novice ease, OEM scheduling and clinical distance remain unverified.

Research orchestration/results are in the existing phone_camera_imu_calibration notebook; reusable code is tools/mobile/calibration_audit.py. Generated evidence stays in android/dist/emulator-lab/calibration-audit/parameter-groups-v1/. No phone APK, OTA, Git commit or push was produced. Current native source requires a new compatible phone package; build 29 is unchanged.


Current layout batch: android/src/components/Screen.tsx; screens/HistoryScreen.tsx, DetailsScreen.tsx and PrepareScreen.tsx; experienceMessages.ts; tests/historyLayout.test.cjs; tools/mobile/build-lab-apk.ps1, interact.cjs, verify-usability.cjs, README.md and scenarios/{list-layout-review,audio-control-layout,compact-review-export}.json; acceptance/wiki/index/log and the existing weekly pages. Preserve unrelated changes; generated packages, captures and logs remain local. Publication requires review and explicit approval.

## Recording visibility and action-area audit - 11 October 2026

The recording list previously reserved six fixed action rows, crowding out the recordings. It now has one explicitly named Export or delete button; selection, bulk export/deletion, storage and Home are in a separate Manage recordings panel. The shorter list heading and page caption replace repeated introductory text. Pagination is within the list and changing page resets its scroll position. Required G.A.I.T. reviews retain their priority and entry points; selection persists when closing the management panel.

Shared Screen action areas are independently scrollable and limited to 30% of the available frame. On small screens or enlarged text, recording-detail navigation moves into the content scroll area. Participant identity is part of the detail content, with a short section title rather than a large repeated date heading. This prevents a long participant label and four fixed tabs from eliminating the result viewport. Roomy screens retain fixed tabs. Preparation has one full-width Continue/Start bottom action; Previous is within the page. Secondary export/settings labels use 18 sp with the existing large touch targets and respect system text scaling.

Final software checks pass 282 app tests, TypeScript, 2,058 native assertions and ten browser checks. Eleven native smoke checkpoints and eight package-matched interaction scenarios (172 controls) pass, covering Home/test selection, saved participants, recording management, compact settings and sound/readiness, details/export, worker outcomes and signal/G.A.I.T. review. Compact scenarios use 720x1280 and 130% text; normal runs use 1080x2340. English-layout emulator evidence is in android/dist/list-layout/ and android/dist/acceptance/usability-summary.json. The final Recordings translation entry was added after that APK build and checked in the complete source software suite; native Malay/Chinese geometry was not exercised in this batch. The lab now disables preview OTA only in its generated x86_64 package and verifies the manifest; interaction replies record the installed APK hash. This prevents a cached update or older installed package from masquerading as a fresh source check.

The review retains failures: initial test-fixture cross-realm comparison, translation encoding caught by the catalog check, stale cached UI, a smoke run with compact-display settings left active, and obsolete-package aggregate verification. Screenshot review also found details-page crowding and clipped two-column preparation controls that ordinary button bounds checks missed. Android can clip reported element rectangles to the viewport; the recording-entry assertion does not prove an entire card is visible. Long forms and enlarged-text content still scroll. No physical distance, audible speech, OEM behaviour or older-adult usability validation is claimed. The phone build29 APK is unchanged; no push, OTA, phone installation or research-data publication.



Earlier refinement scope: android/src/screens/{PrepareScreen,ParticipantsScreen,ResultScreen,DetailsScreen}.tsx, android/src/{store.ts,theme.ts,i18n.tsx,experienceMessages.ts}; android/tests/experience.test.cjs; tools/mobile/smoke.cjs, verify-usability.cjs and result-worker-review/compact-review-export scenarios; this acceptance guide and workflow wiki/index/log plus weekly progress pages. Builds, screenshots, recordings and failure reports remain local/ignored. No Git push or OTA publication.


## Patient-paced phone setup - 11 October 2026

### Front-camera handling for a first-time user - 11 October 2026

The native module selects LENS_FACING_FRONT. Setup happens before putting the bag on the lower back: keep the phone horizontal in its usual bag, securely supported within comfortable reach, screen facing the user. Sit or stand slightly to one side so the preview contains static room furniture rather than mostly the user's face. No target board or camera-facing-away handling is required. Partial bag obstruction still has to leave usable room features; the app does not claim automatic anatomical/face-occlusion verification.

Initial speech states this handling position explicitly. Subsequent voice guidance presents one action at a time: gently turn the screen left/right, gently tip towards the user/back, then rotate slightly like a steering wheel. These intuitive direction labels assume the instructed horizontal hold; the actual numerical all-axis and convergence gates are unchanged. New movement prompts may follow a completed previous prompt rather than waiting 25 seconds; repeated unchanged prompts remain spaced by 25 seconds and never build a voice backlog. Plain labels replace technical ones: Camera view, Gentle movements, Final check. Malay and Chinese cover all new screen and spoken text.

Fresh full sandbox: 280 app/component tests, TypeScript, 2,058 native assertions and ten browser checks pass. Added a real-screen test for screen-facing-user preparation and ordered prompts which cannot replace unfinished speech. Existing slow-user and same-capture completion tests still pass. This is simulated hardware/UI evidence, not an observed novice or older-adult usability study. Current build29 APK remains unchanged; these local source changes need packaging together with the pending native setup fix. No push, OTA or phone retry.



Ordinary phone setup now waits for measured quality without the former 120-second expiry. Slow stillness, delayed speech, pauses and insufficient movement do not close the capture or force a new attempt. The fixed bounds remain on legacy research captures, not on the ordinary phone setup. Cancel, actual camera/sensor/storage failures, leaving the app and OS termination remain separate interruptions; there is no promise of restoring an in-memory estimator after a process kill. Keep-awake remains enabled.

The screen shows the actual saved front-camera image as a live view, one current instruction and three observed requirements: room tracking, movement coverage and stable camera/sensor fit. Initial speech asks for a bright furnished room, avoiding blank walls and fingers over the lens. Missing multi-direction tilt and roll/steering-wheel rotation receive specific spoken reminders, limited to one pending reminder and no more frequently than every 25 seconds. Stable motion coverage does not claim a completed fit. All new text and speech have Malay and Chinese translations. The ambiguous elapsed-seconds counter has been removed; completion depends on the three requirements rather than a view-count goal or timer.

Freshness is now checked when completing the native setup: five stable seconds of old states cannot finish a camera that has frozen. Native timing tests cover a 15-minute delay before movement and a one-hour open quality wait; app screen tests cover a ten-minute pause, missing rotation, preview URI normalization, non-overlapping help and completion using the same capture. The initial new-test harness accidentally awaited the entire pending capture inside React act; it was corrected, and the interrupted initial runner report is retained locally. This was a test orchestration defect, not a phone capture result.

Verification: full software suite passes 279 app tests, TypeScript, 2,058 native assertions and ten browser checks. Android native Kotlin compilation passes. After removing only the elapsed-counter display, the 17 setup screen/guidance tests and TypeScript were rerun and pass. No physical phone was used; audible TTS, actual room/bag convergence, heat/storage limits and OEM behaviour remain unverified. No APK has been repackaged, installed, published or pushed: the existing build29 package does NOT include this native change.

Reproduce:

```powershell
# In android/
node --test tests/onDeviceSetup.test.cjs
npm.cmd run test:sandbox
```

Final and initial logs are under android/dist/setup-guidance/. The previous historical-view regression procedures remain below. Required native changes: GuidedCaptureClock, SetupConvergenceGate, OnDeviceVio and GaitCameraCalibrationModule; app changes: PhoneSetupScreen, phoneSetupGuidance, phoneSetupMessages and cameraCalibration event contract; regression changes: GuidedCaptureClockCheck, SetupFailureRecoveryCheck and onDeviceSetup.test.cjs. Acceptance/wiki/weekly pages are updated in the same local batch.

## Earlier setup failure regressions - 11 October 2026

Reproduced historical setup failure conditions rather than relying on normal-flow UI checks. Fresh production Java/OpenCV 4.12 JNI checks cover duplicate/blurred views, missing side angles, bounded replacement beyond 48 views, noisy views that must not force success, fitting notification and partial-board visibility. Capture queue checks cover saturation, concurrent draining and nonmonotonic clocks; they do not prove an Android camera cannot freeze.

Fresh replays of retained physical captures (not new captures): calibration-1791375553281 remains incomplete with 7 admitted views and missing side/up-down angle coverage; calibration-1791376539280 now solves the lens with 24 admitted views and all coverage gates met. The former cannot be repaired by inventing absent observations. Neither lens result grants camera-IMU or distance readiness.

New phone-only regressions exercise the actual SetupConvergenceGate: incomplete tilt remains pending through 47 seconds, adding the missing motion recovers in the same gate, integrity loss and tracking gaps clear readiness, later continuous states recover, duplicate timestamps reset readiness and sparse updates never pass. These are explicitly invented estimator states, not real images or proof of physical convergence.

Found and repaired a separate late-start timeout: a movement cue beginning at capture second 90 formerly had only 30 seconds before the absolute 120-second timeout, despite requesting 50 seconds. GuidedCaptureClock now retains the 120-second initial bound and extends the deadline when needed to allow the full 50-second movement plus ten seconds for settling. The native watchdog rechecks that deadline. No timer alone grants setup success. This native correction is NOT in the already packaged 0.3.17/build29 APK; a subsequent package is required. No installation, push or OTA occurred.

Fresh sandbox: 277 app tests, TypeScript, 2,049 Java assertions and ten browser checks pass. Native Kotlin compilation passes. Additional actual OpenCV/queue checks pass. Logs and retained failures are local under android/dist/setup-regressions/. Initial npm.ps1 execution-policy and relative Gradle init-path launch errors were corrected without changing machine policy; failed launch log is retained.

Reproduce from workspace root:

```powershell
C:/Users/frank/.venv/Scripts/python.exe -m unittest android/research/test_setup_view_regressions.py -v
```

From android/: `npm.cmd run test:sandbox`. Native states/clock regressions are included in that sandbox. The desktop view suite requires existing ignored OpenCV/JDK/fixture files under android/dist/native-distance-tools; missing prerequisites fail explicitly.

Remaining evidence: real Android camera/IMU execution, bag obstruction/blur/lighting, OEM freezes, audible instructions and unfamiliar-user completion. The checks prevent the reproduced logic errors; they cannot guarantee usable observations in every room.

## Local collector packaging - 11 October 2026

Current local collector package: **GaitTrace 0.3.17 / build 29**, embedded update **3f8767cd**, runtime `44ce3bbc749a7a1753796c29cf901b8454c77af3`. Signed ARM64 APK: `dist/apk/GaitTrace-0.3.17-build29.apk` (75,002,498 bytes). Certificate matches build 28 for an in-place update; do not uninstall. Signature, ZIP integrity, native libraries/licenses, version, update channel, fresh source runtime and embedded bundle identity are verified. This is a local package, with no Git push or OTA publication. Install the new APK once; the installed old runtime cannot be assumed to receive this bundle by OTA.

The 0.3.17 software suite passes 277 app/component tests, TypeScript, 1,090 native assertions and ten browser checks. The unchanged UI/workflow has six build-28 emulator replays (128 controls); this ARM64 build has not been launched on a physical phone. Heard speech, physical distance, OEM behaviour, clinical validity and an older-adult study remain unverified. Older delivery notes below are historical.

The styling is accepted for the collector stage: consistent teal/off-white, scalable type, strong labelled actions and selection states. Course illustrations and richer progress visuals remain possible future polish; no decorative redesign was introduced for packaging. APKs, credentials and build/signing logs stay ignored. Release metadata is organized under android/releases/, with detailed local evidence under android/dist/releases/0.3.17-build29/.

## Persistent labels, worker drafts and compact exports - 11 October 2026

Current visual examples: [Compact language buttons](../../android/dist/emulator-lab/interactions/2026-10-11T06-51-36-585Z/2.png), [Compact export panel](../../android/dist/emulator-lab/interactions/2026-10-11T06-51-36-585Z/12.png), [Worker form](../../android/dist/emulator-lab/interactions/2026-10-11T06-53-08-017Z/9.png).

Current verification: 277 app/component tests, TypeScript, 1,090 native assertions and ten browser checks pass. The final emulator APK builds and installed smoke checks pass. Six current-build interaction scenarios pass (128 recorded controls): collector navigation, worker draft/outcome review, compact review/export, small-screen settings, returning participants and signal/G.A.I.T. navigation. Actual emulator storage retains the 12-second draft and modified outcome without manufacturing speed/distance or changing raw streams. A fresh-screen software reopen restores draft values; save failure prevents leaving until retry succeeds.

At 720x1280 with font scale 1.3, pinned identity, tabs, Export and Done remain in bounds. Secondary tools/import and long worker content still scroll; the primary Start action stays fixed. This batch does not repeat full-duration native walking captures. Those earlier captures remain historical evidence. Audible TTS, actual distance, OEM behaviour, clinical interpretation and an older-adult usability study remain separate evidence gaps.

Reproduce using tools/mobile/README.md, then independently start each named scenario from English Home on emulator-5560 with tools/mobile/interact.cjs. compact-review-export.json sets display/font before navigating because Android restarts on configuration changes. Exact controls, replies, XML and screenshots are retained in android/dist/acceptance/usability-summary.json. Initial component-mock/input-selector/configuration-state failures remain local; the language-wrap defect found visually is corrected. No phone release, Git push or OTA publication.

Earlier same-day sections below retain their prior-build evidence. Use the current manifest for this batch.

Profile/setup/worker fields retain their labels and units after entry, with stronger input outlines. Language buttons wrap into fewer columns on narrow screens instead of splitting words. Participant identity stays above the recording-review tabs and worker form. One Export recording action opens the format panel, leaving more room for signals and assessment content. Worker outcomes show test measurements first; Optional observations and notes expands supplementary fields. The required G.A.I.T. assessment stays accessible outside that optional group.

Save worker draft stores unfinished entries within the same recording, without completing its assessment or manufacturing clinical speed. Leaving the worker screen saves edits first; a failed save keeps the screen open with a retry message. Reopening restores the draft and retains the latest G.A.I.T. form. Final outcome saving clears the draft. Drafts disappear with the recording under existing deletion rules.

Styling direction: keep the teal/off-white palette, large scalable text and generous touch targets; strengthen input/selection boundaries, retain plain text labels, and reduce competing fixed actions. Further visual polish should use concise course illustrations, restrained spacing and one clear primary action per stage. Avoid shrinking type, icon-only menus, decorative motion during walking, or colours that imply clinical recovery. These are design recommendations, not an older-adult usability study.

## Current collector UI follow-up - 11 October 2026

New sessions now show test choices directly after participant confirmation. Continue is disabled until the user chooses a test; returning to preparation keeps that choice. Explicit protocols supplied by a retry retain their setup. Research walk is a secondary selectable option, not an implicit default for a new recording.

Recording Summary puts the required worker assessment card before the movement summary. Unfinished required assessments get a primary action; completed/practice reviews keep an outline action. Patient results remain separate from this recording-review screen. Tools and help is a separate full-screen panel with a fixed Done action. Import is at its top, and tool navigation/import closes the panel before opening the destination.

Previous procedure: build/install the emulator-only APK as described in tools/mobile/README.md. Independently start each scenario from English Home on emulator-5560. Reproduce collector-navigation.json, result-worker-review.json, small-screen-settings.json, returning-participant.json and usability-review.json with tools/mobile/interact.cjs. The fixtures are synthetic EMU-labelled records, never patient/clinical evidence. The runner captures exact actions, UI XML, replies and screenshots; assert-enabled checks the native Continue gate. Failed attempts remain retained.

### Previous executed evidence (before labels/drafts/export refinement)

Final isolated software suite passes: 277 component tests, TypeScript, 1,090 native assertions and ten browser checks. Installed emulator APK build and smoke checks pass. Five current-build scenarios pass with 102 controls: collector-navigation 23, result-worker-review 30, small-screen-settings 11, returning-participant 12 and usability-review 26. Exact evidence folders and APK identity are in android/dist/acceptance/usability-summary.json. Native Continue reports enabled=false before test selection. Import and worker assessment opening need zero scrolling in the revised checks. Actual modified-test persistence still preserves 12 seconds, no manufactured distance/speed and every raw sample.

This UI batch does not rerun native real-duration walking captures; controlled software protocol flows remain current, and earlier native capture evidence below remains historical. Failures from obsolete controls and overlapping early test orchestration are retained in android/dist/acceptance/collector-choice-initial-failures.md. The final suite was run alone.

Local screenshots:

- [Direct test selection](../../android/dist/emulator-lab/interactions/2026-10-11T06-26-52-501Z/8.png)
- [Separate Tools and help panel](../../android/dist/emulator-lab/interactions/2026-10-11T06-26-52-501Z/22.png)
- [Assessment-first recording review](../../android/dist/emulator-lab/interactions/2026-10-11T06-23-59-518Z/6.png)

### Prior senior UI/UX findings - resolved in current follow-up

- Some profile and worker inputs still use placeholders as their visible labels. Add persistent labels and explicit units/required markers without changing their validation rules.
- The worker outcome form still needs scrolling. Group its fields into a short test-specific section, optional observations and final review; preserve a draft before a multi-step redesign.
- Participant identity should remain visible near the top of review, so workers can confirm whose record they are editing without scrolling past signal content.
- Fixed export actions consume substantial review-screen height. A single Export entry opening format choices would leave more space for assessment and signal content.
- Keep estimated capture outcomes distinct from a confirmed clinical test. Existing provisional-finish labels remain necessary; no UI styling makes an unvalidated distance reliable.

This is an expert walkthrough, not an older-adult usability study. Heard TTS, real phone-in-bag operation, distance accuracy and clinical interpretation remain physical evidence gaps. Current changes are local/unpublished. The historical test records below remain unchanged.

### Local change scope for publication review

App: android/src/screens/PrepareScreen.tsx, DetailsScreen.tsx and HomeScreen.tsx; android/src/experienceMessages.ts. Checks: android/tests/experience.test.cjs and researchNavigation.test.cjs; android/e2e/observer-form.spec.cjs; tools/mobile/interact.cjs, smoke.cjs and affected scenario controls. Notes: this guide, workflow wiki/index/log and weekly progress pages. Generated builds/reports/screenshots stay ignored; unrelated existing changes are preserved.


This is the current testing procedure, not a claim of clinical validation.
Every command targets **emulator-5560**, never a connected physical phone.
All generated recordings use `EMU-SYNTHETIC-NOT-PATIENT` and practice mode.
Do not add these recordings to a research dataset.

## Executed results — 10 October 2026

All five native IMU recording routes saved actual emulator sensor streams and
retained their participant links. These were practice fixtures, with Phone
distance and audible voice disabled. Quality correctly remains `repeat` where
virtual sampling is irregular; a flow pass does not admit training data.

| Native route | Saved capture duration | Completion evidence |
| --- | --- | --- |
| Research walk, 10 s | 10.103 s | Completed; raw accelerometer, gyroscope and magnetometer saved |
| 10MWT fallback | 20.500 s | `auto-stop-estimate`; not verified 10 m timing |
| TUG fallback | 100.698 s | Qualified motion followed by quiet finish; not confirmed chair contact |
| 2MWT | 120.099 s | Full Android wall-clock duration; rests did not terminate capture |
| 6MWT | 360.099 s | Full Android wall-clock duration; automatic saving |

TUG needed a stronger synthetic movement sequence after the initial virtual
input did not qualify. Both attempts remain in the interaction logs; the final
saved endpoint is not a timeout or emergency stop. No timed protocol was shortened.

Native settings passed at 720×1280 with font scale 1.3: Start and modal Done were
fully within the screen. Patient Home language changes passed English, Malay and
Chinese. Participant/history/dashboard links passed for the five sessions.
Actual native JSON/CSV/features share sheets opened without sending files.
Research signal review displayed saved curves rather than a blank fixture.

The consolidated report is `android/dist/sandbox-checks/verification.json`.
The final run passed 264 app/component tests, TypeScript, 1,090 native Java
assertions and 10 browser checks. Eight integrated recording scenarios are
included in the component count, not additional physical trials.
Native raw-record verification is
`android/dist/acceptance/native-recordings/verification-summary.json`.
An overall evidence manifest is `android/dist/acceptance/verification.json`.

### Bugs corrected during testing

- Native fullscreen settings hid their Done action. The native screen now has an
  explicit viewport height and a non-collapsing action footer; web layout keeps
  its original scroll footer.
- The app rejected its own long exports. JSON now avoids unnecessary whitespace,
  JSON import is bounded at 40 MB, and CSV import at 128 MB. CSV parsing processes
  rows individually, verifies metadata consistency and recomputes capture quality.
- Android's whole-file UTF-8 reader ran out of memory on the actual 47 MB six-minute
  CSV. Native import now reads 256 KB byte ranges and preserves Unicode split
  across their boundaries. Regression tests cover malformed UTF-8 and size bounds.
- Reimporting an older copy could replace a newer local assessment or participant
  assignment. Duplicate imports now reopen the existing recording without replacing
  it. Use a distinct practice fixture ID when testing fresh import persistence.

The actual six-minute export fixture contains 20,170 acceleration, 20,283 gyro
and 12,807 magnetic readings. Production JSON/CSV round trips preserve these
counts, participant identity and duration provenance. These are emulator signals.

```powershell
node tools/mobile/check-export-roundtrip.cjs
```

To repeat native import, push the generated `native-import.json` and
`native-import.csv` to **the emulator's** Downloads as `EMU-six.json` and
`EMU-six.csv`. From Home, with the import section collapsed:

```powershell
node tools/mobile/interact.cjs --scenario tools/mobile/scenarios/six-minute-imports.json
```

For the native clinical form, begin in Recording details with an unfinished
practice fixture and its Signals tab open. This fills test ratings, saves and
reopens all 31 items; these are explicitly not real clinical observations:

```powershell
node tools/mobile/worker-form.cjs
```

If a scenario's starting screen differs, restore its stated precondition rather
than guessing coordinates. `tap-file-row` selects the Android file row associated
with its preview control; it does not tap the preview icon. Exact Android control
labels, screen replies, timestamps, screenshots and XML are retained per action.

The native form run saved and reopened all 31 test ratings, with a visible Finish
action and assessor/limb/source metadata. Its exact controls are generated in
`android/dist/emulator-lab/worker-form/controls.json`; the retained native saved
record is `saved-native.json`. The first attempt stopped at a long criterion
because the automation did not scroll to its radio choices; the resumed run
records each required scroll and completes persistence. This was a harness
visibility issue, not an invented clinical score.

For selected export and storage cancellation, begin in Recording details:

```powershell
node tools/mobile/interact.cjs --scenario tools/mobile/scenarios/selected-export-storage.json
```

The exported native CSV was inspected and contained exactly the selected record.
Both selected-delete and delete-all Android dialogs were cancelled, preserving
the fixture records. Actual deletion/owned-file cleanup and failure recovery are
tested in the storage suite; this native scenario tests the confirmation UI.
Android renders the dialog control as `CANCEL`, which the recorded controls use.

## Software recording flows

From the workspace root:

```powershell
node --test --test-name-pattern='Acceptance:' android/tests/experience.test.cjs
```

These eight scenarios render the **actual RecordScreen and ClinicalCapture
together**, run their timers and callbacks, then use the **actual local store**
to write and reopen the recording and participant index. Sensor windows, camera
distance callbacks, clock and filesystem are substituted. Recording quality is
not validated by these scenarios; separate sensor/quality tests cover those rules.

Each passed scenario writes its exact chronological controls and saved result
to `android/dist/acceptance/<protocol>-<duration>.json`.

| Scenario | Controls after preparing a practice participant | Required reply |
| --- | --- | --- |
| Research 10/20/30 s | Quiet baseline; short movement; settle; countdown; remain still; fresh motion pulse; walk; rest; resume | Timer does not begin while still; one saved result after chosen duration; rest retained |
| 10MWT, IMU fallback | Baseline and fit; settle; Go; movement; sustained stop | Saved provisional `auto-stop-estimate`, never a verified timed-zone result |
| 10MWT, tracked | Baseline and fit; camera-ready callback; Go; controlled progress at 1 m; rest; 11 m; 12 m | Neither rest nor 11 m ends recording; 12 m ends it with `distance-ended` |
| TUG | Baseline and fit; settle; Go; movement; sustained final stillness | Saved provisional endpoint; chair contact remains unverified |
| 2MWT | Baseline and fit; Go; motion; 10 s rest; resume; full 120 s clock | Rest does not stop capture; automatic duration finish |
| 6MWT | Same controls; full 360 s simulated clock | Automatic duration finish, without shortening protocol time |

The tracked 10MWT fixture is named `10mwt-180-tracked.json` to distinguish it from
the fallback fixture. It supplies controlled distance events; production native boundary rules are
also exercised separately by the Java contract suite.

Every scenario requires exactly one stop/save, a Result route, the same
participant ID and snapshot, an unfinished assessment, a readable recording
file and an indexed history entry. Simulated results remain practice-only.

## Actual Android interaction

Start the lab and build the current source following [README](README.md).
The version/build number alone cannot prove the current JavaScript was loaded.
Retain the APK hash and active bundle hash when testing a rebuilt APK.

```powershell
node tools/mobile/interact.cjs --scenario tools/mobile/scenarios/research-recording.json
```

Start this scenario from Home with a clean disposable emulator app. It performs:

1. Set virtual acceleration, gyroscope and magnetic field to a quiet baseline.
2. Tap Start a walk; enter the synthetic study ID and age 67 using the Android
   keyboard; dismiss the keyboard; select Female.
3. Open Language and audio settings; disable voice; enable Practice walk; Done.
   This deliberately does not claim audible speech validation.
4. Continue; disable Phone distance; choose 10 seconds; Continue; consent; Start.
5. Wait for baseline/fit; apply five seconds of virtual paired motion; settle;
   wait for the start cue; apply walking-like inputs for fifteen seconds.
6. Require Your walk is saved; open summary/signals; inspect Signals and Sensors.

Virtual motion updates are synthetic acceleration/rotation commands. Their
timing is logged; emulator events are not evidence of measured human gait.
Disabling Phone distance exercises the native IMU capture route, not camera VIO.

After creating the synthetic participant, return to Home and run:

```powershell
node tools/mobile/clinical-scenarios.cjs
```

This runs all four clinical **native APK recording routes**, not their previews.
It explicitly records unknown stroke history for the synthetic profile, uses
voice-off practice mode, disables distance tracking, and fills a 3 m course for
endurance tests after scrolling to the course field. It sends virtual motion for
the fit check, settles for Go, supplies test movement, and waits for automatic
saving. The 2MWT and 6MWT use full Android wall-clock time, including stationary
rests. Emergency/early stops must not be mistaken for a completed timed test.
The runner checks the saved protocol/end reason and sensor counts, not just the
appearance of the saved screen. Exact generated scenarios and logs remain at
`android/dist/emulator-lab/clinical-scenarios/`.

```powershell
node tools/mobile/verify-recordings.cjs
```

This retains the five native protocol files and verifies participant linkage,
practice flags, raw streams, unfinished assessment and correct completion
provenance. It does not validate a real 10 m route or TUG chair contact.

Every interaction writes `replies.json`, numbered PNG screenshots and UI XML
under `android/dist/emulator-lab/interactions/<timestamp>/`. A failure retains
`failure.json`, `failed.png` and `failed.xml`; do not discard failed attempts.
Optional permission taps explicitly log whether the dialog was present.

## Other feature coverage and reproduction

Run the consolidated suite from `android`:

```powershell
npm.cmd run test:sandbox
```

| Feature | Executable checks |
| --- | --- |
| Participant creation, clinical intake, returning identity, snapshots and linkage | `experience.test.cjs`, `recording.test.cjs` |
| Complete 31-item G.A.I.T., drafts, branches, completion gates and reopening | `e2e/observer-form.spec.cjs`, `experience.test.cjs` |
| English clinical form under Malay/Chinese patient language | `e2e/observer-form.spec.cjs` |
| Protocol tutorials and all four clinical UI previews | `e2e/observer-form.spec.cjs` — previews do not save recordings |
| Timer, stillness, handling, fresh pulse, retry, speech callbacks and interruption | `experience.test.cjs` |
| JSON/CSV/features, selected bulk export, import bounds and legacy metadata | `recording.test.cjs` |
| Selected/all deletion, owned-file cleanup and failure recovery | `recordingStorage.test.cjs` |
| Dashboard includes linked/unassigned/archived/practice rows and separates trends | `experience.test.cjs` |
| Camera permission denial, retry, grant and cancellation in Android | `scenarios/camera-permission.json` with an explicitly reset virtual fixture |
| Virtual sensor readback, font scale, portrait restriction and resume | `scenarios/platform-controls.json`, `smoke.cjs` |
| Native capture, timing, transport, admission and distance boundaries | `android/research/test_vio_bootstrap.py` |

The report at `android/dist/sandbox-checks/verification.json` records exit status
and logs for each layer. Browser traces/screenshots remain under `dist/flow-lab`.
The checks above are not a blanket pass for every native OS file-picker/share
application, voice engine, camera, phone model or installed OTA combination.

## Physical validation remains separate

After software flow checks, independently test measured distance, real camera
tracking, OEM sensor continuity, speech heard fully and phone-in-bag operation.
An emulator's fixed camera cannot prove VIO accuracy or initialize a valid
per-phone camera/IMU calibration. Simulated callbacks never substitute for that
claim. Clinical timing and G.A.I.T. interpretation still need observer evidence.

## Waist-bag setup review - 11 October 2026

Reviewed the one-time PhoneSetupScreen, native baseline/convergence gates, profile reuse, and per-walk RecordScreen/ClinicalCapture flow from the perspective of a phone inside the waist bag. Preview is useful only before wearing the bag; it is inaccessible after lower-back mounting. Current framing feedback appears only after initial speech and capture startup, so it is not a pre-capture aid. The initial framing/movement workload remains too complex for a first-time amateur, and error wording implies retained capture even when no capture began.

Fresh Android emulator walkthrough failed before camera startup: its TTS engine was not bound. Retry reproduced the failure; Back returned to Home. Failure evidence is retained in android/dist/emulator-lab/interactions/2026-10-11T08-56-24-955Z/ and retry controls/replies in 2026-10-11T08-57-18-701Z/. Reproduction: tools/mobile/scenarios/setup-usability-review.json. This is a failing acceptance scenario, not a successful calibration. The 18 mocked setup-screen tests and complete 282-test/TypeScript/native-contract/ten-browser-check sandbox suite pass separately. These cannot establish audible TTS, physical camera convergence or easy waist-bag handling. No app behaviour changed or publication performed. Full audit: android/dist/setup-usability-review/review.md.

## Calibration preflight corrections - 11 October 2026

Implemented a separate framing screen before native calibration: request camera permission, open the actual Expo front-camera preview, wait for onCameraReady, offer a short voice sample, then let the reachable user press Start calibration. The required opening speech completes after the preview is released and before the native Camera2/IMU capture begins. Initial speech failure returns to framing rather than claiming retained capture. The retained-attempt message requires an actual returned capture URI; a prior-profile message is conditional on a saved profile. Errors and save status now appear at the top, with scroll reset when error state changes. Repeated headings were removed and the preview size reduced; on the normal emulator layout the voice sample was reached with zero scroll gestures. All new wording has Malay/Chinese translations. Device calibration remains separate from the natural-posture checks before each walk; numerical quality thresholds are unchanged.

A new participant can perform walk preparation in the usual lower-back position with voice-led checks once the phone has a compatible saved calibration. First calibration of an unknown camera/IMU pair remains before wearing the bag. We have not established that ordinary body-mounted walking supplies sufficient all-axis calibration information, and do not ask stroke patients to bend or twist to force it. A normal held/bagged calibration is not evidence of an on-body first-calibration workflow. Removing rigid upright posture from per-walk checks does not relax the camera-IMU calibration admission gates.

Fresh final sandbox: 284 app tests (including 20 setup tests), TypeScript, native-contract checks and ten browser checks pass. Final emulator package SHA-256 717F449CD41114999F24D20D258EBF4166E116B1F7FD895E776C52ECF78C85C2. Two exact-package replays pass: setup-preview-startup.json (17 controls) and setup-voice-unavailable.json (24 controls), both retained under android/dist/emulator-lab/interactions/. Normal startup has actual Android TTS onDone callbacks for the sample and opening instruction, native capture startup, observable pending tracking and successful cancellation back to Home. Full numerical calibration did NOT complete; no calibration motion was supplied. TTS callbacks do not establish audible sound.

Unavailable speech is a controlled emulator-only fixture: disable com.google.android.tts on emulator-5560, force-stop/reopen GaitTrace, run the unavailable scenario and restore the package in finally. It verifies visible sample failure, unsaved status, failed calibration-start speech returning to framing, and Back/Home recovery. Earlier failures are retained: an unavailable-speech scenario first assumed absence when TTS had successfully bound; then the correctly unavailable fixture exposed an off-screen error. The second failure led to moving errors to the top. Encoding and test-expectation failures were also corrected and retained in local logs.

Normal final replay: android/dist/emulator-lab/interactions/2026-10-11T09-24-50-501Z/. Unavailable final replay: android/dist/emulator-lab/interactions/2026-10-11T09-23-41-376Z/. Report and screenshots: android/dist/setup-usability-review/{preflight-results.json,preflight.png,voice-recovery.png}. No physical phone operations, Git push, OTA publication or phone APK release. Physical calibration convergence, mounted ease of use, partially occluded bag window, audible TTS and clinical distance remain unverified.

## Android numerical setup proof - 11 October 2026

A separate emulator-only instrumentation APK executes the actual production JNI engine, Java sensor/frame transport, quiet baseline, patient-paced clock, fresh stable-tail gate and profile admission. Its three native libraries are byte-identical to those extracted from GaitTrace's current x86_64 lab APK (source APK SHA-256 717F449CD41114999F24D20D258EBF4166E116B1F7FD895E776C52ECF78C85C2). Inputs are synchronized analytically rendered camera/IMU controls. No test transport was added to the patient app; no physical phone or patient-release configuration was changed.

| Scenario | Actual numerical outcome | Declared response |
| --- | --- | --- |
| nominal-a | Profile saved at 60 s | Pass |
| nominal-b | Profile saved at 60 s | Pass |
| noise-15hz | Profile saved at 60 s | Pass |
| distortion-occlusion | Profile saved at 60 s | Pass |
| slow-view-recovery | Profile saved at 130 s | Pass |
| missing-axis-recovery | Profile saved at 140.55 s | Pass |
| missing-axis-withheld | Withheld; previous lab profile preserved | Pass |
| blank-withheld | Withheld; previous lab profile preserved | Pass |
| different-camera-short | Withheld; previous lab profile preserved | Pass |
| geometry-long-recovery | Profile saved at 94.17 s | Pass |

The 130 s view-recovery and 140.55 s missing-axis recovery cases pass beyond the previous 120 s cutoff. Permanently missing directions or a blank scene cannot save a profile. The inaccurate-prior fixture failed its original 60 s completion expectation; this failure is retained. A longer fresh replay completed at 94.17 s with unchanged gates and byte-identical image/IMU prefixes. The final 60 s pending control was explicitly declared after this investigation; it is not relabeling the earlier failure as an original pass.

Ten captured numerical traces also pass through the actual React setup screen: no forced retry during pending progress, no premature save, recorded profiles pass TypeScript validation, and successful delivery enables Continue after a controlled speech callback. Together with the twenty existing setup cases, thirty screen checks pass. These are component replays with substituted speech/bridge delivery; they do not recreate live Camera2 scheduling or constitute one continuous full-APK calibration session. Earlier actual Android UI/TTS startup and unavailable-voice recovery runs remain separate. The ordinary full sandbox passes 284 app tests, TypeScript, native contracts and ten browser checks.

**Completion is not proof of calibration accuracy.** Comparing accepted fits against known rendered geometry exposes bias: the perturbed-prior recovery has about 2.1% focal error, 18.5 px vertical principal-point error and 17.5 cm camera/IMU translation error; missing-axis recovery has about 11.2 cm translation error. These do not justify a universal accurate self-calibration claim. No observed elderly ease of use, physical mounted setup, partial real bag-window optics, audible TTS, OEM scheduling or clinical distance validation is established. In particular, this is not evidence that first calibration can be completed by ordinary walking while already wearing the phone.

Reproducible sources: tools/mobile/{CalibrationReplayInstrumentation.java,build-calibration-replay.ps1,calibration_replay.py}; Android JNI setup proof cells in notebooks/phone_camera_imu_calibration.ipynb. Final review and full hashes/traces: android/dist/emulator-lab/calibration-replay/final-proof/{review.md,verification.json}; original failures and fresh runs remain in sibling folders. Exact numbered procedures are in the per-case result.json files. Every operation explicitly targets emulator-5560. Nothing has been committed, pushed, published through OTA or packaged as a new patient APK.

## Visual-rejection calibration bias correction - 11 October 2026

Found and corrected a programmatic-construction mismatch: OpenVINS' header fallback uses visual chi-square multiplier 5, while the pinned supplied estimator configurations use 1. The local production engine now explicitly uses 1 for MSCKF and SLAM updates. Pixel uncertainty remains 1 px, FEJ remains enabled, and baseline/coverage/stable-tail/readiness limits are unchanged. This improves rejection of inconsistent image observations; it does not qualify all phones or implement independent on-phone accuracy admission. [Pinned upstream settings](https://github.com/rpng/open_vins/blob/69488123ed9362dd44b6f28e7f4680abbff1442b/config/euroc_mav/estimator_config.yaml).

Fresh host diagnostics on the same depth-corrected 110 s development capture:

| Quantity | Old multiplier 5 | Corrected multiplier 1 |
| --- | ---: | ---: |
| Camera/IMU translation error | 7.89 cm | 0.99 cm |
| Principal-point error X/Y | -9.16/+14.42 px | -1.55/+0.97 px |
| Wrong-prior, nonzero-clock/alignment translation error (separate control) | 7.95 cm | 1.94 cm |

On a separate textured scene/motion, using the same corrected frozen-geometry tracker for both profiles, trajectory RMSE improved from 3.76 cm to 2.41 cm. Path-length error changed from +0.006% to -1.10%; the new fit is not better on every metric. With the old tracker as well as old fit, RMSE was 9.64 cm and path error -4.22%. These are analytic 3D motions, not patient gait. No true scale/route length was supplied to candidates. Data previously inspected for development are not a pristine final test.

Fresh Android execution uses native libraries extracted unchanged from rebuilt x86_64 app APK `2c7ba51b2d099a16269ba6cb3e5054ce4147b5bed9df12c2733bad408e418f90`. The extra depth-corrected control passed at its normal 60 s save point: translation error 2.19 cm, principal-point errors -0.74/-2.27 px. This avoids relying solely on the legacy v1 overlap renderer.

The ten unchanged legacy expectations initially returned 9/10: the short perturbed-prior capture now saves at 60 s, contradicting its old expected-pending assertion. The failed report is retained in `android/dist/emulator-lab/calibration-replay/runs/20261011T113314Z/`. After reviewing the saved fit (3.56 cm translation error), the reusable suite expectation was explicitly changed to accepted, and a separate fresh replay passed in `bias-correction-v2/different-camera-short-corrected/`. The original failure was not rewritten. The other nine declared expectations passed in that fresh regression; those results were not re-executed just to replace the aggregate. Blank and withheld-axis controls remain pending and preserve the earlier profile. View recovery completes at 130 s; missing-axis recovery at 121.25 s. All ten recorded traces pass through the actual React setup screen in 33 component checks, with speech/bridge delivery substituted. This is not a continuous Camera2-to-save full-APK run.

Bias remains: the late-axis saved fit has 6.84 cm translation error, and distortion/occlusion rose from about 0.6 cm to 3.02 cm. Numerical uncertainty alone still cannot establish absolute accuracy. A warm restart worsened the wrong-alignment case to 17.50 cm error; optics-first was inconsistent. Neither warm restarts, staging nor experimental pixel-noise inflation is deployed. An independent on-phone admission stage and arbitrary-phone qualification remain unfinished. Physical mounted optics, audible TTS, OEM behavior, clinical distance and older-adult usability are unverified.

Final sandbox: 287 app tests, TypeScript, native contracts and ten browser flows pass. Reproducible experiments and saved outputs are in `notebooks/phone_camera_imu_calibration.ipynb`; reusable diagnostics in `tools/mobile/calibration_audit.py`, and Android replay in `tools/mobile/calibration_replay.py`. Generated evidence remains local under `android/dist/emulator-lab/calibration-audit/optics-first-v2/` and `calibration-replay/bias-correction-v2/`. Every device operation targeted emulator-5560; no physical phone retry was requested.

Nothing is committed, pushed or published through OTA. The recorded phone build 29 is unchanged. Current source runtime is `9ba6d7cf81e52d3097ae56e63ce03844de28a57e`, different from the recorded phone runtime; the native correction requires a matching new phone APK, not forced OTA compatibility.

## Local phone package - 0.3.18 / build 30 - 11 October 2026

Prepared and verified the signed ARM64 APK at `android/dist/apk/GaitTrace-0.3.18-build30.apk` (75,010,690 bytes). Embedded update edc50efa-4102-44eb-a012-efd8193bbf22; runtime e8a5c2991c5321ce31b835ef8854a8a87daaddd1; APK SHA-256 f72d94bc70651f001b0879cd75ea54b4f3df18dca618e730a96eed32a37ed0e8. Signing certificate matches build 29, permitting an in-place update without uninstalling. The APK's actual Expo constants config and Android manifest both report 0.3.18/build 30; stale isolated-workspace constants metadata was caught and corrected, with the earlier proof retained locally. Fingerprint asset equals fresh source fingerprint, embedded manifest matches generated output, expected current speech strings and ARM64 native libraries/licenses are present, and OTA is enabled for preview. Runtime policy continues to separate incompatible native updates.

The final version-bumped sandbox passes 287 app tests, TypeScript, native contracts and ten browser flows. No new ARM64 physical launch was performed, no phone was connected or operated, and no emulator-only APK was supplied as a phone release. Recent numerical/component evidence remains separate from physical distance, audibility, OEM and elderly-user validation. Calibration bias is reduced, not eliminated; independent on-phone accuracy admission is unfinished. Installation does not re-fit previously saved calibration.

Build/signing/provenance and retained verifier failures are local in `android/dist/releases/0.3.18-build30/`; archived build-29 source provenance is `android/releases/native-0.3.17-build29.json`. Source version, changelog and native distribution records were updated together. No commit, push, public APK upload or OTA publication. Source/review pages remain local for publication review.

## First-use and final-check corrections - 20 October 2026

Current local package: GaitTrace 0.3.19 / build 31, embedded update 8e25fd12, runtime 7b8003b238a19ac35c4387219076cdd97cf27172. APK: android/dist/apk/GaitTrace-0.3.19-build31.apk, 75,014,786 bytes. Signature matches build 30; install over the existing app. Native timing/diagnostics additions require this APK, not an incompatible OTA. No publication was performed.

New-user flow: Start a walk -> check compatible phone setup -> if missing, a primary Set up this phone action explains holding the usual bagged phone before wearing it -> framing/voice preview -> quiet baseline and guided movements -> native final checks -> saved confirmation -> Continue returns to the preserved preparation page -> automatic study ID, age/sex and optional worker details -> test choice, clinical history and readiness -> recording. Camera calibration is once per phone/optical setup for automatic distance; the per-walk personal standing reference remains separate. An explicit Record motion only alternative preserves sensor collection without camera calibration and does not claim measured camera distance. The separate Google trial also does not use this camera preflight. Do not infer that TUG timing alone mathematically needs camera calibration; this preflight follows the enabled camera-distance mode.

IDs are stable pseudonymous GT labels generated from the new participant identity, checked against existing labels, never merged by matching age/sex. The main preparation screen has no manual study-ID field. Walking aid and health details is one clearly named secondary action; manual ID overrides remain inside worker details. Participant management also pre-fills an automatic ID. Secondary controls now have a tinted surface, visible outline and correctly colored icons. Required demographics, clinical-history checks, recording linkage and raw signals are unchanged.

The old generic final message did not say which readiness check remained; it could repeat after movement coverage, and a queued instruction could continue after native completion. The new screen announces coverage once and uses current measured uncertainty to distinguish optical fit, camera/IMU alignment, timing and position uncertainty. Native convergence diagnostics additionally distinguish insufficient frame rate, stale/gapped readings, a changing fit and an accumulating stable window. These diagnostics inspect the same existing five-second/60-frame/freshness/quality gate; no gate was relaxed. Delayed/slow-frame guidance explicitly says larger movements are unnecessary. The actual GuidedCaptureClock supplies remaining minimum movement time; the final status cannot say Complete while it is positive. Already-playing speech finishes, but obsolete pending coaching is suppressed once native capture completes. New text/cues have English, Malay and Chinese entries. This names blockers; it does not prove a root cause for the user's unprovided physical trace or guarantee convergence on every phone.

Verification: 296 app/component tests; TypeScript; native Java transport/clock/quality contracts, including sparse, stale and changing-fit diagnostics; ten Playwright browser flows. Thirty-eight screen checks replay the retained 11 October Android numerical states through the current React screen. This is a historical artifact replay with substituted speech/bridge delivery, not fresh Android numerical or physical acquisition. Fresh package-matched emulator scenarios: tools/mobile/scenarios/first-use-setup.json (22 controls) and setup-preview-startup.json (17 controls). Every device action targets emulator-5560. The first scenario verifies the early gate, framing and safe return, and a generated participant ID. The second checks actual preview, voice completion callbacks, native capture startup and cancellation. TTS was not heard and virtual camera/IMU did not establish full numerical calibration or distance. The same compiled feature source is packaged for ARM64, whose launch is not physically checked.

Local evidence: android/dist/first-use-review/; UI controls/screens/replies: android/dist/emulator-lab/interactions/2026-10-20T01-05-39-480Z/ and 2026-10-20T01-07-20-536Z/. Initial failing controls/tests, including the obsolete browser manual-ID selector, are retained under first-use-review/initial-failure/ and first-use-*-tests.txt. Source-specific native metadata is in emulator-lab/emulator-apk.json. Final software logs and signed phone packaging proof are in android/dist/releases/0.3.19-build31/. Packaging failures from build 30 remain historical, not reused as this build's passing evidence.

Git audit: application/runtime/licensing code and reusable testing/research modules are legitimate source to review for GitHub. Dependencies, Expo cache, APKs, generated datasets/videos/screens/logs and signing credentials remain ignored/local; no real source was deleted or hidden to make status appear clean. Unrelated manuscript/wiki changes and the calibration notebook remain preserved for separate review. Shared wiki/log/older weekly files need hunk review because they combine work streams. The complete grouped file inventory is android/dist/publication-review-2026-10-20/scope.json and review.md. Nothing is staged, committed, pushed or publicly uploaded in this batch.

Final delivery addendum: motion-only collection is an explicit alternate action; camera distance still needs setup. Changing test selection resets its panel to the top. The current emulator smoke suite passes 12 checks. A complete actual Android SDK practice recording with declared virtual motion passed preparation, first-motion start, save and signal/sensor review (2026-10-20T01-33-06-060Z). The saved file contains accelerometer 569, gyroscope 570 and magnetometer 357 samples over 10.102 seconds, age/sex and the matching participant ID/snapshot. These are software-control data, not patient gait or physical sensor-rate/accuracy validation. Earlier stale-selector failures are retained, including off-screen Research walk and obsolete Your walk is saved; the corrected complete scenario passes. tools/mobile/scenarios/research-recording.json uses a unique EMU-SYNTHETIC worker label and practice mode. Companion proof: android/dist/first-use-review/saved-recording-verification.json.
