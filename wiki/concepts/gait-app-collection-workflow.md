---
type: concept
---

# Gait app collection workflow

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


## Calibration preflight corrections - 11 October 2026

Implemented a separate framing screen before native calibration: request camera permission, open the actual Expo front-camera preview, wait for onCameraReady, offer a short voice sample, then let the reachable user press Start calibration. The required opening speech completes after the preview is released and before the native Camera2/IMU capture begins. Initial speech failure returns to framing rather than claiming retained capture. The retained-attempt message requires an actual returned capture URI; a prior-profile message is conditional on a saved profile. Errors and save status now appear at the top, with scroll reset when error state changes. Repeated headings were removed and the preview size reduced; on the normal emulator layout the voice sample was reached with zero scroll gestures. All new wording has Malay/Chinese translations. Device calibration remains separate from the natural-posture checks before each walk; numerical quality thresholds are unchanged.

A new participant can perform walk preparation in the usual lower-back position with voice-led checks once the phone has a compatible saved calibration. First calibration of an unknown camera/IMU pair remains before wearing the bag. We have not established that ordinary body-mounted walking supplies sufficient all-axis calibration information, and do not ask stroke patients to bend or twist to force it. A normal held/bagged calibration is not evidence of an on-body first-calibration workflow. Removing rigid upright posture from per-walk checks does not relax the camera-IMU calibration admission gates.

Fresh final sandbox: 284 app tests (including 20 setup tests), TypeScript, native-contract checks and ten browser checks pass. Final emulator package SHA-256 717F449CD41114999F24D20D258EBF4166E116B1F7FD895E776C52ECF78C85C2. Two exact-package replays pass: setup-preview-startup.json (17 controls) and setup-voice-unavailable.json (24 controls), both retained under android/dist/emulator-lab/interactions/. Normal startup has actual Android TTS onDone callbacks for the sample and opening instruction, native capture startup, observable pending tracking and successful cancellation back to Home. Full numerical calibration did NOT complete; no calibration motion was supplied. TTS callbacks do not establish audible sound.

Unavailable speech is a controlled emulator-only fixture: disable com.google.android.tts on emulator-5560, force-stop/reopen GaitTrace, run the unavailable scenario and restore the package in finally. It verifies visible sample failure, unsaved status, failed calibration-start speech returning to framing, and Back/Home recovery. Earlier failures are retained: an unavailable-speech scenario first assumed absence when TTS had successfully bound; then the correctly unavailable fixture exposed an off-screen error. The second failure led to moving errors to the top. Encoding and test-expectation failures were also corrected and retained in local logs.

Normal final replay: android/dist/emulator-lab/interactions/2026-10-11T09-24-50-501Z/. Unavailable final replay: android/dist/emulator-lab/interactions/2026-10-11T09-23-41-376Z/. Report and screenshots: android/dist/setup-usability-review/{preflight-results.json,preflight.png,voice-recovery.png}. No physical phone operations, Git push, OTA publication or phone APK release. Physical calibration convergence, mounted ease of use, partially occluded bag window, audible TTS and clinical distance remain unverified.

## Waist-bag setup review - 11 October 2026

Reviewed the one-time PhoneSetupScreen, native baseline/convergence gates, profile reuse, and per-walk RecordScreen/ClinicalCapture flow from the perspective of a phone inside the waist bag. Preview is useful only before wearing the bag; it is inaccessible after lower-back mounting. Current framing feedback appears only after initial speech and capture startup, so it is not a pre-capture aid. The initial framing/movement workload remains too complex for a first-time amateur, and error wording implies retained capture even when no capture began.

Fresh Android emulator walkthrough failed before camera startup: its TTS engine was not bound. Retry reproduced the failure; Back returned to Home. Failure evidence is retained in android/dist/emulator-lab/interactions/2026-10-11T08-56-24-955Z/ and retry controls/replies in 2026-10-11T08-57-18-701Z/. Reproduction: tools/mobile/scenarios/setup-usability-review.json. This is a failing acceptance scenario, not a successful calibration. The 18 mocked setup-screen tests and complete 282-test/TypeScript/native-contract/ten-browser-check sandbox suite pass separately. These cannot establish audible TTS, physical camera convergence or easy waist-bag handling. No app behaviour changed or publication performed. Full audit: android/dist/setup-usability-review/review.md.

## Publication compatibility check - 11 October 2026

The requested UI publication was checked against the recorded native build before pushing. Current source fingerprint `f048c5198b15e19c653e3b6c5c1750b94cf3cebf` differs from build29 runtime `44ce3bbc749a7a1753796c29cf901b8454c77af3`; the native runtime verifier correctly rejected OTA publication. Layout-only changes are JavaScript, but the current complete screens depend on unpublished app and storage/distance routes. Repository HEAD remains build-15-era source. Pushing those files alone would not publish a reproducible current application.

Patient-paced native setup changes are implemented and software-tested locally, not included in the unchanged build29 phone APK. A new native package is required for those changes; physical first-time setup and heard guidance are still unverified. Prepared an explicit expanded-source review at android/dist/publication-review-layout-setup/review.md (238 proposed app/pipeline/lab/documentation files). Root AGENTS changes, saved-output calibration notebook, dependencies, generated outputs, APKs, credentials and demo media are excluded. No Git push or OTA publication was performed. Expanded scope requires review under the workspace publication rule; a matching signed native package/release record must be verified before publishing this source through automatic OTA CI.

## Recording visibility and action-area audit - 11 October 2026

The recording list previously reserved six fixed action rows, crowding out the recordings. It now has one explicitly named Export or delete button; selection, bulk export/deletion, storage and Home are in a separate Manage recordings panel. The shorter list heading and page caption replace repeated introductory text. Pagination is within the list and changing page resets its scroll position. Required G.A.I.T. reviews retain their priority and entry points; selection persists when closing the management panel.

Shared Screen action areas are independently scrollable and limited to 30% of the available frame. On small screens or enlarged text, recording-detail navigation moves into the content scroll area. Participant identity is part of the detail content, with a short section title rather than a large repeated date heading. This prevents a long participant label and four fixed tabs from eliminating the result viewport. Roomy screens retain fixed tabs. Preparation has one full-width Continue/Start bottom action; Previous is within the page. Secondary export/settings labels use 18 sp with the existing large touch targets and respect system text scaling.

Final software checks pass 282 app tests, TypeScript, 2,058 native assertions and ten browser checks. Eleven native smoke checkpoints and eight package-matched interaction scenarios (172 controls) pass, covering Home/test selection, saved participants, recording management, compact settings and sound/readiness, details/export, worker outcomes and signal/G.A.I.T. review. Compact scenarios use 720x1280 and 130% text; normal runs use 1080x2340. English-layout emulator evidence is in android/dist/list-layout/ and android/dist/acceptance/usability-summary.json. The final Recordings translation entry was added after that APK build and checked in the complete source software suite; native Malay/Chinese geometry was not exercised in this batch. The lab now disables preview OTA only in its generated x86_64 package and verifies the manifest; interaction replies record the installed APK hash. This prevents a cached update or older installed package from masquerading as a fresh source check.

The review retains failures: initial test-fixture cross-realm comparison, translation encoding caught by the catalog check, stale cached UI, a smoke run with compact-display settings left active, and obsolete-package aggregate verification. Screenshot review also found details-page crowding and clipped two-column preparation controls that ordinary button bounds checks missed. Android can clip reported element rectangles to the viewport; the recording-entry assertion does not prove an entire card is visible. Long forms and enlarged-text content still scroll. No physical distance, audible speech, OEM behaviour or older-adult usability validation is claimed. The phone build29 APK is unchanged; no push, OTA, phone installation or research-data publication.




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

Current verification: 277 app/component tests, TypeScript, 1,090 native assertions and ten browser checks pass. The final emulator APK builds and installed smoke checks pass. Six current-build interaction scenarios pass (128 recorded controls): collector navigation, worker draft/outcome review, compact review/export, small-screen settings, returning participants and signal/G.A.I.T. navigation. Actual emulator storage retains the 12-second draft and modified outcome without manufacturing speed/distance or changing raw streams. A fresh-screen software reopen restores draft values; save failure prevents leaving until retry succeeds.

At 720x1280 with font scale 1.3, pinned identity, tabs, Export and Done remain in bounds. Secondary tools/import and long worker content still scroll; the primary Start action stays fixed. This batch does not repeat full-duration native walking captures. Those earlier captures remain historical evidence. Audible TTS, actual distance, OEM behaviour, clinical interpretation and an older-adult usability study remain separate evidence gaps.

Reproduce using tools/mobile/README.md, then independently start each named scenario from English Home on emulator-5560 with tools/mobile/interact.cjs. compact-review-export.json sets display/font before navigating because Android restarts on configuration changes. Exact controls, replies, XML and screenshots are retained in android/dist/acceptance/usability-summary.json. Initial component-mock/input-selector/configuration-state failures remain local; the language-wrap defect found visually is corrected. No phone release, Git push or OTA publication.

Earlier same-day sections below retain their prior-build evidence. Use the current manifest for this batch.

Profile/setup/worker fields retain their labels and units after entry, with stronger input outlines. Language buttons wrap into fewer columns on narrow screens instead of splitting words. Participant identity stays above the recording-review tabs and worker form. One Export recording action opens the format panel, leaving more room for signals and assessment content. Worker outcomes show test measurements first; Optional observations and notes expands supplementary fields. The required G.A.I.T. assessment stays accessible outside that optional group.

Save worker draft stores unfinished entries within the same recording, without completing its assessment or manufacturing clinical speed. Leaving the worker screen saves edits first; a failed save keeps the screen open with a retry message. Reopening restores the draft and retains the latest G.A.I.T. form. Final outcome saving clears the draft. Drafts disappear with the recording under existing deletion rules.

Styling direction: keep the teal/off-white palette, large scalable text and generous touch targets; strengthen input/selection boundaries, retain plain text labels, and reduce competing fixed actions. Further visual polish should use concise course illustrations, restrained spacing and one clear primary action per stage. Avoid shrinking type, icon-only menus, decorative motion during walking, or colours that imply clinical recovery. These are design recommendations, not an older-adult usability study.

## Usability corrections - 11 October 2026

Executed Android follow-up: three current-APK scenarios passed with 52 recorded control steps. Evidence covers returning-participant selection/aid changes, cancelling and reopening the large six-minute CSV, overview-to-180-185-second graph inspection, the worker overview/Next missing item action, and Start/Done bounds at 720x1280 with font scale 1.3. The verified record is `android/dist/acceptance/usability-summary.json`. Every screenshot, UI hierarchy and reply is retained; earlier failed viewport/state assumptions remain in the interaction logs. These are emulator interactions, not audible speech or physical distance measurements.

Returning participants now confirm their saved identity and walking aid without repeating age/sex/history entry. New participants still complete intake; Edit participant details remains available. Existing clinical completeness gates remain enforced.

IMU-only 10MWT/TUG now warn after eight seconds of qualified final quiet. The warning must finish, followed by a ten-second chance to resume. Movement cancels that pending save, including stale speech callbacks. A failed warning keeps capture running to its limit. Estimated finish speech and result cards explicitly require worker review. This mitigates premature stopping but cannot distinguish every long rest from a true endpoint. Camera-tracked 10MWT still requires its 12 m course boundary.

Signals default to a whole-recording, extrema-preserving overview. Tap a moment to open its five-second detail; retain previous/next navigation and exact raw exports. Axis legend controls have at least 48-pixel targets. The worker assessment keeps original English scoring criteria, adds a Next missing item action, and compacts the paper-order overview without hiding criteria from the question pages.

Imports can be cancelled during chunked reads and cooperative CSV validation (yield every 500 rows). Cancellation discards parsed data before persistence. The save phase is atomic and no longer offers cancellation; JSON parsing remains synchronous after the cancellable read. Duplicate imports still preserve newer local assessments.

Validation: 273 component tests, TypeScript, 1,090 native assertions and ten browser checks passed. This is controlled software evidence, not audible TTS, elderly-user comprehension, camera geometry or distance accuracy validation. Native screen checks are recorded separately below. No physical phone was operated and no publication was performed.



## Elderly experience follow-up - 10 October 2026

Clinical cues are now shorter, with a separate ready warning that finishes before
capture/Go. The clinical clock still starts on Go's speech-start callback. Motion
or missing readiness during the warning returns to the quiet gate rather than
repeating all setup. The waiting screen no longer displays walking instructions
at the same time. Phone checks use plain wording, and technical result limitations
remain in review. Tutorial course rules and sensor admission thresholds are unchanged.

All new patient wording has English/Malay/Chinese entries; the agreed English
worker form is unchanged. Import now shows real read percentage followed by a
checking/saving state. The rebuilt native APK showed 62% reading, then processing,
and opened review. Small-screen Start/Done bounds passed again at 720x1280/font 1.3.

Latest checks: 267 component tests, TypeScript, 1,090 native Java assertions and ten
browser checks pass. Four delayed-speech clinical replays and their exact controls
are saved in `android/dist/acceptance/elder-audio-flow.json`; the procedure and
quality checklist are in [APP_ACCEPTANCE](../../tools/mobile/APP_ACCEPTANCE.md).
The earlier native five-protocol capture runs used voice off. This new evidence
is controlled speech sequencing, not a real older-adult usability study or heard
voice validation. IMU-only 10MWT/TUG can still mistake a long rest for the endpoint;
they remain provisional. Independent first-time use is not yet demonstrated.
No physical phone, push or OTA was used.

## Native recording-flow acceptance - 10 October 2026

The current reproducible procedure is
[GaitTrace feature acceptance](../../tools/mobile/APP_ACCEPTANCE.md). Actual
Android 11 emulator interactions completed research walk, 10MWT fallback, TUG
fallback, 2MWT and 6MWT, with locally saved raw three-sensor streams and the same
participant. Endurance captures used full Android wall-clock time: 120.099 s and
360.099 s. Practice flags remain explicit and irregular virtual streams remain
`repeat`, not accepted patient data. The 10MWT/TUG IMU-only endpoints remain
provisional. Controlled integrated replay separately checks the tracked 10MWT
1/11/12 m boundaries; native camera distance capture is not proven by this replay.

Native checks also exercised Home language changes, participant/dashboard links,
signal curves, Android share sheets and small-screen settings at 720×1280/font
1.3. A hidden native modal footer was corrected. Long-export testing found both
inconsistent import bounds and Android whole-file-reader memory exhaustion.
Exports now use compact JSON; bounded JSON/CSV imports allow 40/128 MB and native
reads use 256 KB byte chunks with Unicode-boundary preservation. CSV processing
retains rows one at a time and rejects conflicting metadata. Raw streams are not
resampled or fabricated by these repairs.

The preceding acceptance passed 264 app/component tests, TypeScript, 1,090 native Java
assertions and 10 browser checks. Fresh native six-minute JSON/CSV imports saved
every raw sample unchanged; optimized CSV opening took approximately 23 s on the
emulator. The native 31-item G.A.I.T. test form saved and reopened all ratings.
Selected export contained exactly the chosen recording; native deletion dialogs
were cancelled. Duplicate JSON/CSV imports now reopen existing records without
erasing newer local notes, ratings or participant assignments. All test ratings
and sensor inputs remain non-clinical fixtures.

Exact tap/text/scroll/sensor/wait actions, timestamps, screenshots, XML and failures
are retained locally in `android/dist/emulator-lab/interactions/`; raw captures and
software evidence live under `android/dist/acceptance/`. Generated fixtures are
excluded from research/model evidence. No physical phone, APK release, push or
OTA publication occurred. Camera distance accuracy, heard speech and OEM-specific
phone-in-bag performance remain physical checks rather than an all-feature claim.

## Android emulator interaction lab - 10 October 2026

The workspace now has Android 11 Emulator plus Appium 3.8.0/UiAutomator2 8.7.0.
[Workspace instructions](../../tools/mobile/README.md) describe launch, actual APK
interaction, UI replies/screenshots and reusable scenarios. All commands target
emulator-5560 rather than any physical device. The lab uses production app source
compiled for x86_64, with six packaged native libraries verified. Downloads and
AVD/build/output files are local/ignored; AGENTS.md records the reuse workflow.

Fresh APK smoke passed 11 checkpoints. Actual camera denial/error/retry/grant/
cancel-to-Home passed, as did three virtual sensor set/readbacks and font controls.
Landscape refusal matches the portrait-only app. Initial ARM/Hermes, packaging
filter and harness expectation failures are retained; no phone was retried.
Explicit virtual APK installation and installed-ABI verification prevent Appium
preserve-data mode from silently testing an older binary.

These cover named UI/platform scenarios, not every recording/export flow or
physical camera/IMU geometry. Audible speech, OEM/thermal behaviour and independently
measured distance remain unverified. See the local emulator-lab verification JSON.

## Phone-free software verification - 10 October 2026

`npm run test:sandbox` now orchestrates app/component tests, TypeScript, actual
production Java contract checks and Playwright against the actual Expo web UI.
It uses controlled hardware boundaries and clocks, never the connected phone or
its patient records. All 251 app tests, TypeScript, 1090 Java assertions and 10
browser flow checks passed in a fresh consolidated runner execution. Its
authoritative result is `android/dist/sandbox-checks/verification.json`.
Browser checks cover all four clinical previews, enrollment and the complete
31-item G.A.I.T. form with drafts/reopening and English clinical language policy.
Missing native dependencies fail rather than silently skipping validation.
Audible speech, Android camera/sensor scheduling and independently measured
distance remain unverified by this sandbox. See [instructions](../../android/FLOW_TESTING.md).

## Cable-connected physical checks - 10 October 2026

Redmi Note 10 Pro / Android 11 reports build 28, all three IMU hardware sensors
and granted camera/activity permissions. Home language switching works in
English, Malay and Chinese. Prepare pages and required intake gates were exercised
using a non-patient test identity.

Actual Start test attempts exposed a permission-activity lifecycle bug: the app
treated the Android permission screen as abandonment and silently cancelled
startup. Local repair avoids requesting already-granted sensor permission and
preserves startup through permission pauses, waiting for foreground return.
Two regression checks bring the passing app suite to 251; TypeScript passes.
Signed corrected build 28 has update `8394c378`, unchanged native runtime and
matching certificate. Android blocked USB installation; the APK is in Downloads
awaiting manual in-place installation. Corrected physical startup remains unverified.

Retained setup capture `calibration-1791634564413` ends with `quality-time-limit`
after approximately 120 seconds despite real sensor/image capture; it does not
establish accepted calibration. Voice was reported absent or incomplete; operator
navigation may have interrupted the sample. Media and TTS streams are unmuted on
the speaker, but audible completion remains unverified. No complete physical flow
or distance acceptance is claimed. Cable-slack movement tests responsiveness and
negative controls, not a measured 1 + 10 + 1 m clinical course.

## 10MWT boundary contract — 10 October 2026

The local build-28 candidate uses one native `ten-metre-boundaries-v1` record
for the 1 + 10 + 1 m course. Origin and initial direction remain fixed; crossing
times at 1, 11 and 12 m are interpolated between accepted poses. The same 12 m
time ends the walking interval, and saved speed is 10 divided by the 1-to-11 m
interval. Recorded poses verify the saved evidence without selecting a different
endpoint direction. Missing or inconsistent evidence withholds timed-zone speed.

Personal standing reference remains per recording, accepts stable natural lean,
and does not establish anatomical trunk orientation. The new native package
requires an APK update. Software replay and packaging do not establish successful
fresh-phone setup, measured boundary accuracy or clinical validity. Publication
and physical acceptance remain separate.

## Setup reliability and physical acceptance - 9 October 2026

Current status, updated **10 October 2026**:

Local continuation, 10 October 2026: installed 0.3.15/build 27 is unchanged.
Nothing was installed, published or pushed; no phone retry was requested.

The patient placement flow now accepts a stable personal stance instead of
requiring the phone to be within 20 degrees of a landscape upright reference.
A fresh five-second quiet accelerometer/gyroscope window and all three actual
sensor streams are still required. Stable natural lean is not a placement failure.
Movement/fit and countdown checks use this same rule. The final quiet reference
can refresh after the fit check, before recording; it cannot be re-zeroed mid-walk.
Raw walking axes remain unchanged. JSON and raw/feature CSV exports retain the
unit gravity reference, measured phone angle, false anatomical-verification flag
and false raw-correction flag. Phone angle is not a measured trunk angle or an
attribution to neurological/orthopaedic disease. Existing gravity-projected derived
signals remain separate from the raw data. Relative direction guidance uses the
measured gravity vector, without an absolute upright-angle requirement.

English, Malay and Chinese instructions tell patients to use their comfortable
usual stance and walking aid rather than straighten their back. Initial stable
lean does not trigger the shift warning. Later sustained >15-degree changes still
request placement/posture review; one phone cannot distinguish a slipped pouch
from a genuine change of posture. Loose movement, shaking, missing samples and
invalid gravity remain rejected. Anatomical lower-back placement and anatomical
forward/lateral axes cannot be established from gravity alone.

All current automated checks pass: **248 app tests**, TypeScript and **1,090 Java
assertions**. The previous ten simulated full pipelines and two intentional
rejection controls passed; four additional setup/profile-to-export walks at 35
and 55 degrees pass, yielding **2.986513 m** and **2.990441 m** for level 3 m routes,
twice each. No target distance is used to fit scale. Source hashes, outputs and
scope are in `android/dist/on-device-checks/posture-simulation/verification.json`.
The new simulation initially exposed a generator defect: rotating gravity while
retaining X-directed travel made the path inclined, invalidating comparison of
horizontal output against 3D path length. Those outputs are preserved as invalid
fixtures; the corrected level-plane walks reuse the same admitted camera profiles.
They are not unsuccessful clinical or physical walks.

The previous quiet-first startup, full lens/noise consistency, bounded stable-tail
completion and 1 m + 10 m + 1 m monitor repairs remain intact. There are no failing
checks in this defined automated suite. This does not establish universal phone
setup, independent cross-phone distance accuracy or clinical validity; simulation
cannot remove those evidence gaps. Installed build 27 has none of these unpublished
local fixes. Research, notebook, wiki and weekly status are synchronized locally.
All captures, rendered frames, dependencies, binaries and generated outputs remain
local and excluded from source publication.

Method rationale: [Postural transitions with a single waist sensor](https://pmc.ncbi.nlm.nih.gov/articles/PMC7271521/) uses the gravity vector from static calibration as a tilt reference. [Trunk posture from randomly oriented accelerometers](https://pmc.ncbi.nlm.nih.gov/articles/PMC9573549/) distinguishes gravity-based orientation from anatomical registration. These support the reference approach; they do not validate this app, its thresholds or attribution of lean to stroke.

Earlier settlement evidence follows; prior pending-delivery descriptions are
historical.

The first authorized physical setup on build 25 stopped before useful capture:
Android's permission activity briefly paused GaitTrace, which the interruption
handler incorrectly treated as leaving the test. The compatible JS correction
waits for permission and activity resume before speech/capture, checks existing
camera grants first, and still cancels an active capture when backgrounded.
Added regression coverage passes with the fresh 241-test suite and TypeScript.
Physical retest of the corrected bundle is pending. Earlier installed-APK proof
below belongs to the initial bundle; this failed scan is not calibration evidence.

The incremental package initially reused its embedded update identity; Expo could
load the original cached JS despite new APK bytes. A second immediate stop still
ran that old flow. Regenerated update resources with fresh ID `03e822a3...` and
added an APK update-identity guard. Two synthetic ZIP regressions and rejection
of the actual stale-ID package pass; fresh-ID package acceptance passes. Active
phone bundle and successful scan remain pending. Local records are preserved.

Local follow-up requires confirmed completed speech before the phone-setup
capture/movement/Continue actions. Voice failure stops the attempt; interruption
awaits native stop and stale completions cannot change a retry. Failed stop blocks
another capture. Audio cancellation also clears its timeout, preventing an old
watchdog from interrupting a new instruction. Matching saved profiles are offered
for reuse. Home separates phone-only setup from optional computer reference tools.
New patient copy is available in EN/MS/ZH; the clinical form remains English.

ADB confirms build 24 installed on the Redmi, a clean launch in the inspected
logs, camera/activity permissions and hardware availability of all three IMU
sensors. Found its cached native fingerprint did not match source, so the assumed
compatible-update handoff is superseded. Corrected signed **0.3.13/build 25**
regenerates resources, packages these fixes and matches fresh source runtime
`89e68fa8...`. It retains the release certificate and requires one normal in-place
installation. ADB now confirms build 25 installed and launching, with its APK
digest/runtime matching the local signed file. Original installation date and
camera/activity permissions are retained. A source/runtime publication guard is
implemented.

These fixes are in the installed build-25 bundle. The remaining acceptance
work is actual phone speech, mounted 1 + 10 + 1 m distance/endpoints, failures/rests,
TUG/endurance behaviour, record/profile/assessment linkage and export/deletion.
Fresh-phone enrollment and accuracy need physical evidence. Numerical convergence
and software controls do not establish clinical accuracy or a trained cross-device
few-shot model. Publication remains subject to user review; generated checks stay
local. See `android/research/DISTANCE_PHONE_CHECKS.md` for the current handoff.

Verification: TypeScript, 238 app tests, 10 Playwright flows and Android Hermes
bundle export, full native assembly and APK signature/runtime checks pass. Software speech tests hold actual completion boundaries;
they do not establish that Android audio was heard fully during a mounted walk.

## Supervisor-facing evidence and collection milestone - 9 October 2026

The current local supervisor deck follows collection, variable identification,
specialist model training and eventual rehabilitation feedback:
`android/dist/weekly-progress/2026-10-05/GaitTrace-supervisor-progress-2026-10-05-theory-illustrated.pptx`.
Actual shared-app screenshots show profiles, tutorials, the English G.A.I.T.
worker wizard/notes, physical-recording signal review and local history linkage.
They are captured in the browser flow lab, not reconstructed UI or Android
hardware validation. Fictional profile/notes are labelled; an unchanged real
6 October JSON supplies the waveform. Demonstration linkage does not identify
its actual participant or change native records.

The illustrated revision adds explanatory visuals to all nine text-only slides.
Editable process diagrams clarify sensor physics, calibration admission,
collection dependencies and proposed synthesis/model work. Generated, clearly
labelled concept scenes show screen-outward lower-back mounting and a separate
observer camera. Actual screenshots, evidence plots and method references are
preserved. All 20 slides were rendered and individually inspected, with source
media, notes, bounds and template preservation checked. The methods-only deck
and new local `supervisor-illustrated-evidence/` provenance remain available.
These visuals add no clinical validation or new model results.

The current revision replaces the box flows on slides 13–14 with labelled
physical theory illustrations: phone translation/rotation/gravity and local
axes, lens projection, camera/IMU spatial/time alignment and trajectory recovery.
Editable equations and prior-method references remain. Slide 12 now explains
its existing image as a virtual-camera view of fixed textured panels at varied
depths, with IMU generated from the same known motion. It tests tracking
integration rather than synthesizing patient gait. Its original notes were
restored from the earlier 17-slide deck after a serialization error was found.
All other slides and source media are preserved. Images, prompts and final
checks are local under `supervisor-theory-illustrated-evidence/`.

The existing phone camera/IMU notebook retains the executed artifact review,
feature outputs and source hashes. Full screenshots, final renders and passing
layout/template checks remain locally under `supervisor-evidence/` beside the
deck; the presentation and media are excluded from source publication.

The current 20-slide methods revision preserves the original 17-slide deck.
Slide 13 explains the rigid-body forward model: sensor-frame specific force
is `Rᵀ(p̈ − g)`, and angular velocity comes from local rotation changes.
Scripted motion supplies tracker controls, while healthy optical marker motion
supplies the earlier virtual-IMU pilot. Therapist-supported timing/sway transforms
and realistic phone attachment/noise remain future clinical synthesis work.
Slides 14–15 distinguish prior reference methods from current self-setup:

| Method and verified reference | Actual project role |
| --- | --- |
| [Zhang, TPAMI 2000](https://www.microsoft.com/en-us/research/publication/a-flexible-new-technique-for-camera-calibration/), [OpenCV ChArUco](https://docs.opencv.org/4.x/da/d13/tutorial_aruco_calibration.html) | Earlier planar-view lens fitting and guided corner capture |
| [COLMAP, Schönberger and Frahm, CVPR 2016](https://colmap.github.io/) | Earlier offline scene/camera reconstruction for the reference pipeline |
| [iKalibr, Chen et al., T-RO 2025](https://github.com/Unsigned-Long/iKalibr) | Earlier targetless camera/IMU spatial and temporal reference calibration, not ETH Kalibr |
| [VINS-Mono, Qin et al., T-RO 2018](https://github.com/HKUST-Aerial-Robotics/VINS-Mono) | Earlier desktop physical-distance replay |
| [GeoCalib, Veicht et al., ECCV 2024](https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/05636.pdf) | Explored frozen learned lens initialization on the computer, not the current Android solver |
| [OpenVINS, Geneva et al., ICRA 2020](https://pgeneva.com/downloads/papers/Geneva2020ICRA.pdf) | Current native phone visual-inertial estimation and geometric self-setup |
| [Yang et al., T-RO 2023](https://yangyulin.net/papers/2023_tro_full_calib.pdf) | Sensor-model and observability foundation for guided varied motion and rejecting insufficient information |

The current port estimates camera intrinsics, camera/IMU alignment and time
offset. It does not reproduce full IMU scale/misalignment/g-sensitivity fitting
from the observability paper. Profile binding, guided speech, stable-tail and
numerical admission gates are our engineering integration. Their thresholds
and estimated uncertainty do not establish measured distance accuracy. New
methods renders, citations and layout/preservation checks remain locally in
`supervisor-methods-evidence/`. No new calibration or training was executed.

Physical phone trials, analytic camera/IMU controls and the earlier healthy
GAITEX virtual-IMU pilot have different purposes. Physical captures expose real
noise/placement/tracking and provide future labelable observations. Analytic
virtual camera trajectories test software contracts, not clinical gait training.
The GAITEX component calculates ideal six-axis signals from healthy optical
pelvis-marker motion (18 parents/55 windows); it is not validated L5 attachment
or stroke-like synthesis. Its saved plot is replayed, not regenerated.

Current mounted front-camera footage depicts the surroundings for tracking.
It cannot replace external video of the patient's trunk, feet and aid. Earlier
Expo camera trials have event metadata but no quantified frame/IMU alignment;
new native frame timestamps still do not automatically synchronize an external
observer camera. The next collection deliverable is matched video/IMU/assessment
bundles with verified timing, therapist ratings and explicit invalid-trial reasons.
Candidate cadence/alternating timing are exploratory; foot identity, confidence,
strength and neurological cause are not established by these phone traces.
Clinically parameterized synthesis and recovery/few-shot models remain later
research work. Local wiki/progress/deck updated together; no publication.

## Independent-phone production requirement - 9 October 2026

The user now requires every supported future phone to perform initial setup,
calibration, capture, distance/speed calculation and test boundaries entirely
on device. Earlier permission for a one-time computer step is superseded.
Lower-back horizontal placement, the existing front-facing waist-bag window,
voice-led EN/MS/ZH guidance and 1 + 10 + 1 m 10MWT remain fixed.

Local 0.3.12/native code 24 now implements independent phone enrollment and
live distance tracking through a pinned OpenVINS Android library. Factory
metadata is a prior, not a supplied verified calibration. Completed voice cues,
all-axis excitation, uncertainty, plausible geometry and a stable tail gate the
saved phone/window profile. The main recorder uses real live states for estimated
1 + 10 + 1 m stopping and preserves rests. No paid service, target board,
computer pairing or transfer is needed in this path.

231 app tests, 617 native assertions and local ARM64 APK packaging pass. Actual
host controls converge under stronger all-axis motion, including perturbed
starting camera priors. The real Java admission accepts the stable control.
The admitted profile then produces 2.88629 m in a separate 3 m software control,
accepted by the actual app result rule without scale fitting. Blank footage and
insufficient excitation cannot enroll. These are synthetic software executions,
not physical phone accuracy or model training. Rotational readout compensation
omits translation, noise assumptions remain provisional, TUG chair contact is
unverified and no cross-device neural model is trained.

A release-signed ARM64 APK is now ready locally: **GaitTrace 0.3.12 / build 24**.
Its certificate matches installed build 23, so it supports an in-place update
without uninstalling. Packaged native libraries, licenses, version, EN/MS/ZH
strings, preview request headers and fingerprint runtime are verified. The
read-only update endpoint check returned 204 for this runtime: no compatible
OTA is currently published. After installing this native binary, compatible
JavaScript/asset updates can use preview; native changes still require an APK.
Physical fresh-phone setup, mounted accuracy/failure-rate, audio and runtime
acceptance remain. Production/clinical readiness is **not** claimed. No push,
OTA or public release publication has occurred.
The [current method](../../android/research/ON_DEVICE_DISTANCE.md),
[product contract](../../docs/REHAB_ASSESSMENT_PRODUCT_SPEC.md) and
[phone checklist](../../android/research/DISTANCE_PHONE_CHECKS.md) record the
current workflow. Earlier computer instructions below are historical developer
paths, superseded for ordinary first use.

## Experimental board-free enrollment - 9 October 2026

Implemented a separate **Quick phone setup (experimental)** screen under Phone
calibration. Real front-camera/three-axis IMU capture stays in the usual optical
window; the app waits for completed voice guidance, collects ten seconds quiet
and fifty seconds varied motion, transfers once to the authenticated local helper,
selects ten clear textured views, runs frozen GeoCalib on five support and five
disjoint check views, then runs the existing iKalibr camera/IMU reference solver.
The computer display switches to scene features instead of ChArUco instructions.
No printed target or manually measured square is required in this path.

Only a completed, bound, geometry-checked result can be **explicitly selected**.
The learned lens remains an experimental seed: centered principal point, one
radial coefficient and four assumed-zero distortion terms, no invented Zhang
reprojection score. View disagreement over 8%, poor texture/blur, insufficient
all-axis motion, incompatible clocks or impossible geometry reject enrollment.
These are engineering gates, not clinical or distance-accuracy thresholds.
Previous board/reference profiles survive failed capture, processing or import.
Normal main recording still calculates camera distance on the phone afterwards.

Enrollment ZIP includes original camera/IMU capture, result, and a provenance-bound
training example. Cleanup deletes raw/recovery/export copies but preserves the
small reusable profile. New participants reuse that phone profile; a different
phone/installation/camera/window needs its own enrollment.

Added executable first-order MAML focal-residual training, candidate-label
loading/deduplication, model-level train/validation/test separation, labelled
support adaptation, checkpoint/report export and research inference. Five phone
models with two physical enrollments each is the conservative software minimum
(three training / one validation / one held-out test), not a sufficient scientific
validation sample. We still have only one real model. The app uses frozen
GeoCalib plus geometric refinement; no locally trained cross-device neural model
is deployed. GPU trainer/checkpoint code was executed on explicit synthetic
software fixtures only; those outputs cannot be imported as phone profiles or
used as real training evidence. A solver-derived focal label is not independent
truth, and this head does not learn metric distance, timing or extrinsics.

Fresh replay GPU support/query focal difference: **3.0136%** on one retained
physical alignment capture with adapted enrollment metadata. It is a historical
artifact replay, not a new phone run, and is excluded from future training.
Full camera/IMU replay outcome is recorded in the executed calibration notebook.
Android packaging, TypeScript, rendered flow/voice sequencing and rejection/
recovery tests run locally. Cross-phone acquisition, actual Android runtime,
repeatability and measured-route error checks remain for the physical handoff.
New signed APK required; local build uses a test key. No source push/OTA/release.


### Completed enrollment software evidence

The retained-capture full chain completed in **1,175.15 seconds (~19.6 minutes)**
including neural stage, SfM, solver and export. GeoCalib and SfM features/matching
used the GPU; mapping/calibration optimization used CPU. The five-view consistency
was 3.0136%, but that is **not absolute lens accuracy**: the learned seed focal
length was ~359 px, whereas the solver refined it to ~476/484 px and a shifted
principal point. The replay therefore demonstrates why the initial neural seed
must never directly supply the walking camera parameters.

Current Android Java and desktop adapters use the refined candidate for this
new path, with explicit Brown/OpenCV coefficient-order conversion and bounds.
Actual Java input preparation plus the unchanged phone C++ frontend/estimator
host replay and TypeScript integrity rule completed on retained gait data,
returning **2.88999 m**, versus ~3.157 m under the previous calibration. This is
method sensitivity on a historical replay, not an independently verified 3 m
error or physical Android/cross-phone test. No measured length was fitted.

Final checks: **224 app tests, 94 research tests, TypeScript, web export and full
ARM64 Android APK packaging pass**. Native enrollment/export methods, refined-lens
adapter and current JavaScript are present; APK signature is a local Android
Debug key, not the installed release key. A release-signed build-24 APK remains
pending. Original capture/result artifacts are retained; metadata replay examples
are explicitly excluded from future training. No source push or OTA publication.

## Few-shot enrollment feasibility - 9 October 2026

Fresh local manifest audit in the executed camera/IMU notebook finds **17 physical
captures (6 calibration, 10 distance, 1 noise), all on one Xiaomi M2101K6G
installation**. The 52 available manifest-bearing archives also include duplicate
copies, four synthetic controls and four historical metadata adapters; these do
not add independent training tasks. All 16 physical camera captures include IMU.
No held-out phone is available. Ordinary gait exports do not substitute for
camera/IMU calibration tasks; saved solver profiles are candidate/proxy labels.

The requested Face-ID-like setup is a research target. A pretrained image
calibration model plus a small few-shot residual/uncertainty head and observable
camera/IMU refinement is the proposed route. First compare few-view estimates on
whole held-out recordings from this phone; evaluate transfer only after additional
phone/reference profiles exist. No neighboring-frame train/test split, arbitrary
scale fitting or model-calculated distance labels should establish accuracy.
Single-phone self-supervised adaptation is possible as an experiment but does
not demonstrate cross-device enrollment.

Executed pretrained GeoCalib ECCV 2024 five-view inference on the RTX 5060 GPU
for three retained walking clips. Estimated mean focal lengths differ from the
saved candidate by -0.778%, -0.098% and -2.205%; desktop calculations take
1.752/0.784/0.812 seconds, excluding loading/setup. These are proxy lens-parameter
comparisons, not distance errors, fresh calibration truth or phone benchmarks.
The neural weights are frozen; shared-view geometric optimization is not training
our requested cross-device few-shot network. Simplified distortion, centered
principal point and missing sensor timing/extrinsics remain. The first PyTorch
policy failure was transient; normal retry succeeded with no policy changes.
Dependencies/checkpoints stay ignored. That probe was desktop-only; the subsequent board-free enrollment implementation is described above.
See [audit and proposed experiment](../../android/research/ON_DEVICE_DISTANCE.md#few-shot-request-audited-training-feasibility-9-october).

## Main recording integration - 9 October 2026

The main implementation now processes camera distance **on the Android phone**,
reusing the saved one-time camera/IMU calibration. This corrects the earlier
computer-dependent main integration. Target remains **0.3.12 / native code 24**;
a replacement signed APK is required and has not been published. The separate
historical computer research trial remains available for comparison.

Start test > participant > Choose your test > Camera distance (experimental).
Capture follows the ordinary Go/first-step and end boundaries. After capture,
Java validates the calibration/binding and hardware clocks, and the Android C++
VINS library calculates the trajectory. No HTTP or paired computer is used.
The result remains linked to the participant, mandatory G.A.I.T., exports and
permanent recording deletion. Background results preserve worker edits and
cannot resurrect deleted records. A saved capture can be retried on the phone.

The single admission rule remains complete tracking plus integrity checks,
otherwise unavailable with raw IMU retained and no substitute distance. 10MWT
uses **1 m approach + 10 m measured section + 1 m finish**. Estimated 1 m/11 m
crossings require a complete accepted estimated 12 m route. Calculation is
after recording; this is not live distance stopping or verified clinical timing.

A small Bayesian gyro-bias model learns from ten blocks in the existing two-second
quiet interval. It seeds initialization only when its uncertainty/bias limits pass.
It does not modify raw IMU or replace camera geometry/timing calibration. New
participants on the same phone reuse calibration. No cross-device few-shot neural
network has been trained, and arbitrary new phones cannot yet be calibrated by
an ordinary room scan or a few walking steps. The retained Redmi front-camera
capture does not expose factory lens intrinsics. See the peer-reviewed rationale
and implementation limits in [phone-only distance](../../android/research/ON_DEVICE_DISTANCE.md).

Verification evidence is recorded in the existing camera/IMU notebook and ignored
`android/dist/phone-vio-native/` outputs. ARM64 library/AAR builds and actual Java
input preparation pass. Host execution of the exact Android frontend/core replays
the retained walk at approximately **3.157 m**, close to the previous computer
implementation's **3.1569 m**. This is implementation agreement on historical
input, not new physical accuracy or Android runtime performance evidence.
Consecutive-run reset, app, type, research and web checks are recorded in the
final notebook verification (218 app tests, 86 research tests, TypeScript and web
export). Full local APK packaging also passes with the native engine and embedded
JavaScript; its debug signing key cannot update the installed release app. Saved
noise calibration survives raw capture cleanup. Release signing remains pending.
Mounted-phone JNI/runtime, temperature, timing and
storage checks remain. User-deferred extra 3 m accuracy trials remain deferred.
No clinical validation, AI gait-model training, source push or OTA publication.

## Integrated research distance helper - 8 October 2026

The corrected pipeline is integrated and its local helper is running. The normal
`Start phone calibration.cmd` launcher explicitly selects
`fixed-time-rows-quiet-v1`, builds the separate corrected VINS wrapper and runs
its actual CTest. Direct Python defaults retain `fixed-time-v2` for historical
replays. Both are research modes. No APK or saved calibration change.

The corrected mode applies saved camera row timing and selects the first
continuous two-second quiet interval before measured motion from native IMU.
It retains that baseline and following practice, extracts camera features from
the full capture, then excludes only the placement prefix from estimator input.
Quietness is not proof of lower-back anatomy. Original ZIPs stay unchanged.

Fresh complete HTTP upload, immutable ZIP preparation, native CPU feature
extraction, VINS estimation, guard assessment and durable result delivery ran on
all five retained physical captures. Among the four reported measured attempts
(altered-start trial excluded), results are **3.14808 m**, **3.23556 m**,
**rejected**, and **3.15688 m**. Latest alone has explicitly confirmed corrected
foot references. Its confirmed 3 m error is +0.15688 m / +5.23%. Original phone
reports remain intact. One retained trial still has an impossible pose jump and
is withheld. These are development replays, not fresh prospective validation.

The app's actual TypeScript upload/poll/import/save/reopen code passes for all
five, using real HTTP and simulated Expo filesystem. Reloading durable service
jobs also passes. A separately labelled synthetic blank-camera/stationary-IMU
control returns unavailable, never zero or invented distance, and passes the same
app import path. No real Android network/storage or new physical walk was done.

All **83 research tests** pass. The 250-case factor CTest passes in the corrected
build. Processing revision includes source identity, selected CPU/CUDA frontend
and mode. Job identity additionally includes the noise-profile digest, preserving
older outputs and preventing reuse across changed processing/noise. Reports expose
`software.processing.revision`, `noise.initialization` and `noise.profileSha256`.
Changed pending inputs fail explicitly. Legacy executable SHA stays `17b688f8`,
corrected executable SHA starts `e03883b2`. Calibration/profile/clinical readiness
flags remain false where required by their research contracts.

Saved executions in the existing notebook include the failed Windows/Linux path
attempt, the corrected build, source-version replay rerun, environment-specific
legacy fixture failure, and timestamp-dependent ZIP-fixture failure plus fixes.
The ZIP test now reuses the same bytes for idempotence. Failed build products were
moved into ignored evidence rather than left at the repository root.

**Calibration status:** lens/profile processing completed and is reusable for
this research camera/holder setup. Reliable distance and full independent
camera/IMU calibration are not established. No recapture is requested. Next is
three fresh precisely marked 3 m trials with the same foot landmark and standing
posture at both endpoints, return to the same start after practice, and wait for
Finished before touching the phone. Keep every unavailable result. Existing
build 23 remains compatible; no new APK, push or OTA.

## Retained distance investigation - 8 October 2026

Historical isolated-candidate checkpoint, superseded by the integrated helper above.

**The candidate is isolated and not active in the live helper.** Original phone
reports, calibration, APK and distance scale remain unchanged. The pinned VINS
fixed-time branch uses `ProjectionFactor`, omitting the row correction in
`ProjectionTdFactor`. Our wrapper loaded 30.48 ms readout but skipped that
correction. Opt-in `fixed_time_row_correction: 1` applies the upstream first-order
row model, default off, without upstream edits. See the [pinned estimator](https://github.com/HKUST-Aerial-Robotics/VINS-Mono/blob/90dabb5ec79946ae42fd2e1e91d4e69aabe1e25d/vins_estimator/src/estimator.cpp)
and [time/row factor](https://github.com/HKUST-Aerial-Robotics/VINS-Mono/blob/90dabb5ec79946ae42fd2e1e91d4e69aabe1e25d/vins_estimator/src/factor/projection_td_factor.cpp).

Fresh replays retain saved features, native IMU, fixed geometry/time and measured
noise. A second experiment excludes initial placement motion, starting at the
first two-second quiet interval before measured motion, keeping quiet baseline
and practice. Acceleration norm standard deviation must be below three times
measured max-axis noise sigma (0.080401 m/s²), gyro maximum below 0.08 rad/s.
This infers quietness, not anatomy. It is not yet a production selection rule.

| Reported 3 m capture (all `distance-trial-` prefix) | Original report | Row correction + quiet-prefix exclusion |
| --- | --- | --- |
| `1791467656506` | Geometry rejection | 3.14808 m; standing drift 0.03039 m |
| `1791468160915` | Standing drift rejection | 3.23556 m; standing drift 0.08445 m |
| `1791468384841` | Standing drift rejection | Still rejected: pose discontinuity |
| `1791468615419` | 3.24120 m (+8.04%) | 3.15688 m (+5.23%); standing drift 0.03433 m |

Three of four reported measured attempts return complete candidates, versus one
original. Only latest foot references are explicitly confirmed. Altered-start
`1791467944213` stays excluded from accuracy, even though it tracks. These are
development replays, not prospective repeatability or clinical validation.
Row correction alone recovers two failed trials, but the second gives 3.33767 m,
outside nominal tolerance. Quiet-prefix exclusion reduces it to 3.23556 m.

The third remains unreliable: its quiet-prefix replay has a position jump
implying 29.36 m/s despite plausible reported velocity. Added consecutive-pose
integrity checks use the existing 3 m/s bound, including near-start bracket and
finishing tail. Original first rejection also has a 6.51 m/s jump. No gate
relaxation, route-label scale fit or failed-distance admission.

Actual CTest passes 250 cases against unchanged upstream factors. Fresh
zero-readout controls maintain 559 initialized poses, identical off/on states
and 0.00001035 m rigid-only RMSE, no scale fit. Incompatible online time fitting
with the opt-in is rejected. All 74 research tests pass, including three pose-jump
cases. Synthetic checks establish consistency, not physical accuracy.

Executions and saved-state reassessment are in the existing camera/IMU notebook,
including a preserved summary-path failure/retry. Artifacts stay ignored under
`android/dist/distance-investigation/`. Candidate binary SHA starts `8b1a364c`,
live binary stays `17b688f8`. Next integrate explicit opt-in/provenance and verify
the complete helper service on retained captures before prospective phone trials.
Pause more requested walks. No new APK, repeat calibration, source push or OTA.

## Corrected latest walk and five-attempt reliability review - 8 October 2026

This is the original live-helper checkpoint before the isolated investigation
above. Preserve its automatic reports as historical evidence.

Latest `distance-trial-1791468615419` started at 22:10:15 MYT. The user confirms the corrected measured 3 m walk. Its automatic result is **3.24120 m**, **+0.24120 m / +8.0400%**, with complete tracking, no resets and 0.05700 m finishing standing drift. It passes the existing single-trial 0.30 m pilot tolerance. Camera saved 1,694 frames at 29.81 Hz, acceleration/angular rate ran at 210.47 Hz and magnetic readings at 50.00 Hz. Reported callback drops/rejections are zero, but timestamps include a **133.22 ms maximum camera gap**, so zero counters do not prove every scheduled image was saved. Walking-state maximum gap is 66.62 ms. Measured-motion interval is 8.9782 s, followed by 4.2905 s finishing stillness. Processing stages total 28.23 s excluding preparation/upload, using native CPU features and CPU VINS. Saved geometry and measured noise were unchanged, with no fitted distance scale.

The four immediately preceding captures were initially reported as measured walks with unreliable-tracker messages. The user subsequently clarified that the complete **3.38890 m** trial (`distance-trial-1791467944213`, 21:59:04 MYT) involved a **30 cm start-position change after practice**, and says it is not usable for accuracy. Its raw/result files remain retained, but it is excluded from accuracy comparisons. No assumed 30 cm correction is applied. Moving before the measured-start trigger should exclude that displacement from recording, but the actual distance to a fixed finish can still change. Whether the shift preceded the trigger is unverified. Among the **four remaining reported measured attempts, only one returns a complete estimate**, the latest 3.24120 m result, which meets nominal tolerance. Only its foot references are explicitly confirmed.

Three estimates were withheld: estimated straight-path geometry mismatch at 21:54:16, finishing drift 0.84987 m at 22:02:40 and finishing drift 0.65624 m at 22:06:24. The mismatch has an estimated 0.52839 m maximum lateral deviation. These are estimator diagnostics, not proven physical deviations by the person. No resets occur in all five saved replays. Phone handling before Finished was not answered. These small same-person/same-phone counts do not estimate population performance.

Finishing-pause gyro mean norms in the two drift failures are 0.03599 and 0.02633 rad/s, compared with 0.02528 rad/s in the latest pass. Acceleration-norm standard deviations are 0.07269 and 0.04357 m/s², compared with 0.04871 m/s² in the pass. Raw quiet-tail motion is not dramatically different enough to establish phone handling as the cause. Translation is not independently measured by these IMU summaries. The distance pipeline remains **insufficiently reliable for routine use** despite the latest tolerance pass. Next engineering work should inspect estimator drift/initialization and boundary-to-camera agreement on retained evidence before requesting further repeated walks. Do not loosen rejection thresholds or fit scale to make these results pass.

Fresh assessments reproduce saved results without rerunning the estimator. Analysis, complete attempt inventory and user confirmation are saved in the existing notebook. A Windows missing-timezone-database failure is preserved alongside a retry using explicit current MYT UTC+08:00, followed by a separate five-trial review cell. Generated raw/results stay ignored under `android/dist/`. No software, calibration, APK, source push, OTA or model training occurred.

## First user-confirmed measured 3 m trial - 8 October 2026

The paired helper completed `distance-trial-1791464391571` automatically and estimated **3.27094 m** against a selected 3 m route. Complete measured-segment tracking passes integrity gates, with zero resets and 0.09783 m finishing standing drift. The user initially described an exactly measured walk but then clarified different foot references at the boundaries: toes at/pointing to the start and the back of the foot over the finish line. A toe-start/heel-finish mismatch can increase lower-back displacement beyond the floor-mark separation. Exact foot/posture offset is unknown. Consequently **the prior narrow accuracy pass is withdrawn**. The +0.27094 m / +9.0313% is an arithmetic comparison, not established measurement error. This trial's accuracy is not evaluable. No foot-length or scale correction is fitted. Both walks remain useful flow/tracking checks but not accuracy validation. Physical course crossings are detected by motion, not independently verified.

Camera saved 2,213 frames at 29.94 Hz, accelerometer/gyroscope recorded at 210.35 Hz, and magnetometer at 50.00 Hz. Sensor clocks are monotonic with finite values and zero reported rejected callbacks. The measured-motion interval is 22.4105 s followed by 4.2377 s finishing stillness. Camera maximum timestamp gap is 66.61 ms across the capture and initialized walking-state maximum gap is 33.65 ms. The actual measured phone-noise candidate and unchanged saved geometry/time were used. Local native CPU frontend plus CPU VINS processing stages total 35.66 s excluding upload/preparation. Fresh assessment of saved states reproduces the result without rerunning the estimator or fitting scale.

Notebook cell `gaittraceDistanceMeasured3M` preserves the initial analysis and `gaittraceDistanceFootreference` records the subsequent endpoint clarification and withdrawn accuracy verdict. Generated evidence remains ignored under `android/dist/distance-physical-review/distance-trial-1791464391571/`. Next, repeat the marked 3 m route using the same foot landmark and matching standing posture at both endpoints, without stepping beyond the finish. Record all trials. No code, profile, APK, source publication or OTA change occurred.

## First current-pipeline physical distance trial - 8 October 2026

Automatically uploaded `distance-trial-1791463790250` from build 23 finished as quiet-stop. Its reference identity, native pipeline and usual waist-bag optical setup match the saved calibration. The helper processed and returned **3.51512 m**, with complete measured-segment tracking and no estimator resets. The user confirms waiting for Finished and seeing the result on the phone. The recorded measured-motion interval is 10.4355 s, followed by 4.2906 s finishing stillness. Camera saved 2,372 frames at 29.90 Hz, accelerometer/gyroscope operated at 210.43 Hz, and magnetometer at 50.00 Hz. Native callback-drop counters are zero, sensor clocks are monotonic, and the largest camera timestamp gap is 66.83 ms. Standing horizontal drift is 0.03442 m. These support capture/tracking feasibility, not independent distance accuracy.

**Reference limitation:** the app selection was 3 m, but the user subsequently clarified that the actual walk exceeded that distance by an unknown amount. The displayed +0.51512 m / +17.1707% compares against a selection, not verified ground truth. It must not be interpreted as a failed or passed accuracy test. This trial's engineering accuracy result remains **not evaluable** and excluded from accuracy statistics. The subsequent user-confirmed measured trial is documented above. No new APK, board/noise calibration or manual export is needed while automatic transfer works.

The measured phone-noise profile was actually loaded in this replay. Computer import/features/estimator/export total about 48.36 s, excluding phone ZIP creation/upload and preparation. This run uses the selected native CPU frontend and CPU VINS, not GPU processing. A fresh review of its saved states reproduces the distance/integrity assessment without rerunning or tuning the estimator. The initial review assertion incorrectly compared a preliminary software-provenance record with the enriched final record; that failed analysis cell and its corrected retry are preserved in the existing notebook. User feedback is saved in a separate cell and corrects the ground-truth interpretation. All generated capture/review images/results remain ignored. No publication occurred.

## Actual stationary noise capture - 8 October 2026

Freshly reviewed physical `imu-noise-1791456301401.zip` with the production native-clock processor. ZIP CRC, finite values and increasing timestamps pass. There are 63,075 accelerometer samples and 63,072 gyroscope samples over approximately 300 seconds at **210.22 Hz**, plus 15,000 magnetometer samples at **50.00 Hz**. Accelerometer/gyroscope maximum interval is 4.941 ms, with approximately 0.845% interval coefficient of variation. No resampling, trimming or clock correction was used.

Stationary and short-term white-noise gates pass: accelerometer Allan slopes are -0.514, -0.550 and -0.465, and gyroscope slopes are -0.451, -0.488 and -0.481. Production status is **white-noise-candidate**, not full calibration or validated distance. Long-term bias random walk, repeatability and camera tracking accuracy remain unvalidated. Magnetometer coverage passes, but this analysis does not calibrate magnetic heading.

Read-only verification confirms that the paired helper already completed this exact upload and registered the matching installation/device/pipeline profile. Its result equals the freshly rerun report. The actual distance noise adapter accepts maximum-axis per-sample standard deviations of **0.0268003 m/s²** for acceleration and **0.000691093 rad/s** for angular rate. Random-walk defaults remain provisional. Phone-side receipt was not inspected. Executable analysis and outputs are saved in `notebooks/phone_camera_imu_calibration.ipynb`, with generated reports ignored under `android/dist/imu-noise-review/`. No new APK, software change or publication occurred. Next physical evidence is a complete marked 3 m straight trial, including practice/return, first-motion start and automatic quiet finish.

## Checklist navigation correction - 8 October 2026

The build-23 checklist previously omitted Home's **Import, research tools and app information** expansion. **Research tools** is a heading inside that section, not a menu button. Actual noise navigation is Home → expansion → Phone calibration → scroll main content → Research capture tools → Sensor noise (already selected) → Measure sensor noise (5 min). The release marker is below Storage in the same expanded Home section, not in Settings. Browser preview deliberately has no Android research controls.

Corrected `android/research/DISTANCE_PHONE_CHECKS.md`, including actual EN/MS/ZH labels and explicit Connect computer steps. Two added navigation checks render the actual Home, phone-calibration and noise screens with injected native dependencies; the saved-reference branch reaches the selected noise tab, while web omits Android tools. These are component checks, not physical phone interaction. No app code/native/binary changed, so the correction requires no replacement APK or OTA. Existing build 23 remains the target. Publication remains pending scope review.

**Verified APK - 8 October 2026:** 0.3.11/build 23 finished successfully (`d64795ab-4667-455a-b6dd-113fb99759f1`). ZIP integrity, compiled version/package, runtime, new native practice/end-boundary API, bundled EN/MS/ZH guidance and cryptographic Android signature pass. Certificate matches build 20, supporting an in-place update. [Download build 23](https://expo.dev/artifacts/eas/L8EFVUNHKT1E4voE2EAAORAoVj3Z_mfykV_a0HqcaA0.apk). Local file: `android/dist/apk/GaitTrace-0.3.11-build23.apk` (233,387,998 bytes). SHA-256: `dc09ab82650aef3817cfff4ad6304cf0c136aa2e6cf606529b4ed9583008abf5`. Runtime: `9bc3827992f3c583d878767addc04dae0f3d3081`. Organized local release evidence: `android/dist/releases/0.3.11-build23/`. Physical checks remain; no source push or OTA publication.


## Distance trial readiness and physical handoff - 8 October 2026

The separate local-computer research trial now has native placement → complete practice speech → practice movement/return/stillness → complete measured speech → first fresh motion → quiet-stop boundaries. Practice is not proof of VIO initialization; the person must return to the marked start. Standing cannot complete practice or start the measured walk. A no-walk timeout retains raw data without submitting a false zero-distance result. The finishing pause is recorded for integrity review but excluded from distance.

The pinned VINS estimator keeps saved camera/IMU rotation, translation and time offset fixed during these short trials. Straight distance uses horizontal endpoint displacement rather than summing pelvis sway. A separately selected turns route uses 350 ms smoothed horizontal trajectory length, with corner-shortening explicitly unvalidated. Resets, late initialization, gaps, excessive speed/bias, standing drift or route mismatch withhold complete-route estimates. Marked length is a comparison label, never fitted estimator scale. Motion boundaries are not verified clinical course crossings.

Five-minute stationary capture automatically uploads to the paired helper, runs native-clock Allan/white-noise review and returns a phone-bound result. Only matching phone/device/pipeline candidates can provide per-sample maximum-axis measurement standard deviations; continuous-time density is not blindly substituted as sample sigma. Random walk remains provisional. Real phone filtering, temperature and repeatability still require physical review.

Fresh verification: **206 app tests**, TypeScript, **71 research tests**, Android Metro export, actual-JVM boundary checks and live HTTP/ZIP/actual-TypeScript integration pass. Rebuilt VINS maintains **559 initialized analytic-control poses**, rigid-only RMSE **0.0003602 m**, without fitted scale. Generated noise is labelled synthetic. Blank footage returns not-initialized with no metres and survives actual TypeScript import. The first control exposed a no-features exit misclassified as processing failure; strict recovered-output checks fix this. Failed attempts remain in the notebook.

Three retained physical ZIPs were freshly replayed with fixed geometry/timing. The formerly resetting last trial maintains tracking diagnostically; the first still fails integrity. All three lack legacy holder/pipeline identity needed to validate newer calibration. Outputs remain diagnostics, not accepted measured 3 m results. Subsequently, matching stationary noise passed candidate checks, the initial current-pipeline over-walk tracked completely but lacked a known actual length, and the next walk tracked completely but its subsequent foot-reference clarification invalidated the initial accuracy interpretation. Neither walk currently establishes known body displacement. Independent distance accuracy remains unvalidated, as detailed above.

Experiments/provenance remain in `notebooks/phone_camera_imu_calibration.ipynb`; raw ZIPs, builds, logs, dependencies and generated results stay ignored. The [physical checklist](../../android/research/DISTANCE_PHONE_CHECKS.md) covers mounted noise, speech/first-motion/quiet-stop, marked routes, turns, interruption, transfer recovery and cleanup. New native **0.3.11/build 23** is required. Source/OTA publication remains pending review; no clinical distance, rehabilitation or model completion is claimed.

**Current work - 8 October 2026: 0.3.11 / build 23.** Native practice and motion boundaries, fixed-reference replay, standing-drift rejection and automatic short-term noise review are implemented. Software controls pass; physical accuracy remains unvalidated. See [[#Distance trial readiness and physical handoff - 8 October 2026]] and the linked phone checklist. Publication remains pending user scope review.

**Historical calibration build - 8 October 2026**

Version **0.3.9 / build 19** finished successfully on 7 October at 23:46 MYT
(EAS `6748383e-9927-4e24-9ce6-e9e9599c3f11`). The signed APK was downloaded and verified on 8 October:
ZIP integrity, manifest version/package, native calibration code, bundled round
guidance, runtime fingerprint and Android apksigner verification all pass. Its
signing certificate matches build 16, allowing an update over the existing app.

[Download the build-19 APK](https://expo.dev/artifacts/eas/AZLeoHa2b78I0i_e7aD1bv7xEh1CmBTHnxhvC3Lp1FM.apk). Local copy:
`android/dist/apk/GaitTrace-0.3.9-build19.apk` (233,380,614 bytes).
SHA-256: `fc72d019f2641762b76cf226ac825c72bb201d7a136bb74f2442488eab1c13c0`.
Runtime: `8e22ae58794f79ee93bc2e4838ac5c29f2893513`.

Build 18 failed before native compilation because source-byte changes overlapped
archive preparation. Build 19 used frozen native source, with all 14 module/plugin
files checked against the upload archive; the runtime compatibility guard remained
enabled. Install build 19 over the existing app and restart
`android/Start phone calibration.cmd` for the updated computer guide.
At that release, physical calibration and independent distance validation were
pending. The subsequent iKalibr reference candidate was solved and saved for
review; independent distance validation is still incomplete.
Source changes and generated artifacts remain local pending publication review.


This page tracks what the local GaitTrace phone app can capture and what still requires observer, course or clinical validation. It is an implementation record, not evidence that the app is a validated rehabilitation instrument.

## GPU calibration experiment - 8 October 2026

Built a separate CUDA-capable Ceres 2.2/iKalibr environment and actually executed
two CPU and two CUDA final solves against the same retained real capture and
fixed measured SfM. The same rebuilt executable, Ceres library and two-thread
configuration were used for both backends. Median final-solver time is
**355.09 s CPU versus 139.07 s CUDA**, a **60.8% reduction**.
All seven solver reports converge in each run. CUDA GPU activity is recorded;
this is a real calibration comparison, distinct from synthetic capability checks.
The timing excludes raw import, image preparation and SfM reconstruction.
One upstream initialization report has zero residuals and `Iterations: -2` in
all four runs. It is retained as an empty stage, not independent proof of
successful geometry calibration. Final weighted costs are about 492-495, but
those internal fits do not establish accuracy against measured physical geometry.

The strict numeric parity check fails. First-pair camera/IMU translation differs
5.02 mm, rotation 0.0701 degrees, time offset 0.353 ms and readout 0.127 ms.
Initialization also varies across replays. The executed notebook stores the
within-backend repeatability and cross-backend parameter/cost review, so these
differences are not attributed solely to GPU precision or called clinical error.
Translation varies **6.04 mm between CPU repeats** and **2.66 mm between CUDA
repeats**; paired cross-backend differences are 5.02 mm and 3.58 mm. Two repeats
on one development capture are insufficient to establish accuracy/equivalence.
At this solver-only checkpoint the production default/profile were preserved.
The subsequent complete-pipeline validation below supersedes the pending
processing check; independent physical accuracy remains unvalidated.
No independent distance validation was done.

The CTraj/veta repository URLs are unavailable, but the authors' distributed
Docker image retains the matching source in an earlier layer. Recovery verifies
the layer digest, exact source/dependency commits and unchanged raw tracked files.
The experimental non-unity build needs explicit includes and out-of-line accessor
declarations; function bodies, thresholds and iteration limits are preserved.
The build and CUDA controls passed through incremental/resumed compilation.
The consolidated Docker recipe has not had a separate cold-build run.

Source recipe and research worker: `android/research/calibration-cuda/`.
Fresh executions and saved-output analysis are in the existing
`notebooks/phone_camera_imu_calibration.ipynb`. Raw capture, recovered upstream
source/dependency trees, Docker images, build logs and benchmark products stay
local/ignored. This experiment does not change the helper's CPU default or the
Android APK. No new APK, phone capture, Git push or OTA is required/performed.
All 64 existing research unit checks pass. The four real calibration runs and
the separate synthetic CUDA controls are recorded distinctly in the notebook.

## Measured optimization follow-up - 8 October 2026

The fastest measured short-trial configuration is now the default: native CPU
tracking, a persistent worker, Linux storage, one archive for frame import and
one result-recovery call including Linux-written solver logs. Optional CUDA
tracking remains available. Calibration COLMAP extraction/matching still uses GPU.

The existing camera/IMU notebook freshly executed three alternating repetitions
of the previous and revised CPU orchestration on the same retained 353-frame
development capture. Median replay wall time fell from **10.74 s to
8.06 s**, a **24.9% reduction**. Import fell from
2.03 s to 0.43 s,
and export from 1.19 s to
0.20 s. Feature CSV hashes match and all 353
computed state rows are identical across all six runs, excluding processing-time
measurements. The solver itself stayed around 5.3 s, already a Release/-O3 build.
No frames, timestamps, iterations, convergence tolerances or integrity gates were
removed. These timings cover replay orchestration, not upload, raw capture
conversion, one-time worker startup or the longer calibration pipeline.

Two fresh final-calibration solves reused the same measured capture, bag and
fixed SfM reconstruction. Two versus four threads gave main-optimization times
**277.52 s versus 246.05 s**
(11.3% less), with final-solver
wall times 355.52 s versus 319.43 s. Both runs
converged, but the strict numerical parity gate failed. Camera translation
differed by 2.037 mm,
rotation by 0.0393 degrees,
time offset by 0.187 ms and
readout by 0.958 ms. Initialization
costs differed before the main optimization, so the difference cannot be isolated
to threading or called reduced clinical accuracy. Keep the existing **two-thread
default**. Four threads are experimental pending repeatability checks, selectable
with `GAITTRACE_REFERENCE_THREADS=4`; the actual affinity-capped count is recorded
in new calibration provenance. The saved phone calibration was not replaced.

The failed parity assertion and subsequent saved-output review are both retained
in the notebook. This is a measured improvement, not a claim of maximal or
universal optimization. Distance accuracy remains unvalidated; the retained
development walk still resets and does not admit a complete metric distance.
64 research tests and 11 real GPU-container checks pass. Desktop changes require
only restarting the helper, with no new APK after build 20 and no repeat phone
calibration. Source, wiki and weekly progress remain local for publication review.

## Local GPU processing - 8 October 2026

The RTX 5060 Laptop GPU is verified through real CUDA corner and forward/backward
LK kernels, not driver detection alone. An isolated, digest/commit-pinned OpenCV
4.12.0 / CUDA 12.9 image retains a worker context and compilation cache. Replay
files stay on native Linux storage; startup health and result exports disclose
backend, kernel counts, source/image hashes and timings. These desktop changes
require a helper restart, with no further APK beyond build 20. Source is local
pending the updated 51-file publication review.

The saved notebook freshly replays retained development frames, not a new physical
walk or independent evaluation. Same-build, alternating three-repetition timings
on 353 frames are **CPU 1.4587 s**, **CUDA 2.2742 s**: GPU is about **56% slower**
for this 150-feature workload. Full GPU replay executes 704 LK and 230 corner
calls (observed GPU memory 116 MiB). A startup HTTP health check and known
two-pixel-motion/irregular-clock CUDA check pass. Native CPU mode is available
for the measured faster path and is now the default. CUDA remains an explicit
research option after the user requested the fastest measured method.

GPU feature-stage wall time is 2.03 s, CPU 1.48 s; their respective VINS stages
are 7.01 s and 5.35 s. The diagnostic frontends produce different feature tracks,
so solver work is not identical. Both retained-capture replays reset and finish
uninitialized, admitting no complete metric distance. All 353 frames and native
timestamps are retained. Results remain research-only with clinical readiness
false. **64 research tests and 11 actual GPU-container checks pass.**

GPU-only is neither implemented nor recommended. Calibration COLMAP extraction /
matching and optional distance corner/LK tracking use CUDA. File handling, JPEG
decoding, geometric RANSAC, mapping and unchanged iKalibr/VINS solvers remain CPU.
Enabling CUDA is not evidence of speedup or more accurate gait/distance measures.

## Current camera processing investigation

### Current physical failure and local repair - 7 October 2026

Two actual build-16 ZIPs now establish the cause of the repeated 47-view stop:
the UI lagged the final native count of 48, and a hard memory cap ended collection
before missing angle coverage could be completed. Neither attempt stalled:
camera metadata remained about 29.7 Hz, saved lens images about 3.7 Hz, and
capture-queue drops and sensor rejections were zero. The latest attempt passed
side-angle coverage (0.2224) but high/low coverage reached 0.1119, below 0.12.
No fit was attempted by build 16. All three actual sensor streams were finite
and monotonic (accelerometer/gyroscope about 210.5 Hz, magnetometer 50 Hz).

Local 0.3.9/build 19 removes that count-based termination. After initial framing,
view admission follows the first unfinished angle/position round; unrelated
translations/zoom no longer inflate its count. Completed coverage is preserved.
The retained pool stays bounded at 48 with useful-view replacement; count alone
never admits a lens. Temporary board loss preserves collected views. The five-
minute capture limit and camera-stall/quality checks remain. EN/MS/ZH round labels,
brief action cues, spoken completion feedback and a computer movement example
guide side angles, high/low angles, image positions and final view diversity.
Speech finishes before the next cue; only the latest pending instruction is kept.

Fresh desktop JNI replay of the latest actual ZIP selects 24 views and passes
the unchanged fit/coverage checks: held-out p90 0.2530 px, training RMS
0.1715 px. This is an artifact replay, not a new phone calibration or metric
distance validation. It is saved with source/ZIP hashes in
`notebooks/phone_camera_imu_calibration.ipynb`; raw images/ZIP remain local.
192 app checks, TypeScript, Android export, 43 Python research checks and real
OpenCV JNI fixtures pass. The known-answer lens p90 remains 0.1593 px. Headless
browser checks with simulated progress verify round switching and no overflow
at 1366x768; they do not validate physical camera/audio behavior.

Build 17 (0.3.8, EAS 28c14a15-e0ef-4248-b40e-d594e6437af1) was canceled before
completion because it lacked the final staged collector. Build 19 requires a
replacement APK; build 16 cannot receive native collection changes via OTA.
Build 18 failed; build 19 is the frozen-source retry (see current build status below). Source publication
awaits user review. Reference calibration and independent distance validation
remain separate, incomplete requirements.



Local Android compilation verification (7 October): the frozen calibration-module
Kotlin and Java sources compile successfully against Android SDK 35 and JDK 17.
Gradle completed 39 actionable tasks in 6m18s. A Windows Kotlin daemon cross-drive
path error recovered through its fallback compiler; the final process exited 0
with BUILD SUCCESSFUL. This is actual Android compilation, distinct from the
desktop JNI fixtures. The signed cloud build 19 has since finished and passed APK verification
(8 October); physical phone calibration remains unverified.

### Published calibration and reduced setup burden - 7 October 2026

The user accepted one-time local computer processing. The local 0.3.6 candidate
now integrates guided Zhang/OpenCV lens calibration and private-LAN transfer to
the iKalibr authors' targetless reference executable. Scan the computer code,
watch the stationary computer board and its live framing diagram while moving
the bagged phone for lens-only fitting, then move the phone in a stationary room
for separate camera/IMU alignment. No tablet is required; a moving-tablet mode
remains explicitly optional. EN/MS/ZH prompts match the selected handling mode.
The computer displays native accepted-view count and the current prompt. Actual
phone JPEGs are processed transiently on the private LAN; only detected corners/
outline reach the page, avoiding a second coded target. They are not saved or
used to admit calibration. Brief target loss keeps accepted views; partial ChArUco views may qualify
under unchanged corner/coverage gates. [Zhang](https://www.microsoft.com/en-us/research/publication/a-flexible-new-technique-for-camera-calibration/)
permits either object to move; [OpenCV](https://docs.opencv.org/4.x/da/d13/tutorial_aruco_calibration.html)
supports partial target visibility. Source `2cce693` and the first functional
preview update `01a115df-b6e0-7bf6-9760-2c02061813e8` were published on 7 October.
All three GitHub workflows passed. Expo's actual client response matches the
build-15 runtime, allowing a compatible update. Physical receipt/usability is
not yet verified. Later documentation-only updates may have newer IDs.
The app automatically selects clear varied views, saves a successful lens profile,
stops the alignment capture and transfers/retrieves the reference result. No print,
ruler or manual ZIP exchange is required. Digital board shape/flatness still matter.

Actual native OpenCV known-answer checks recover lens parameters with 0.1593 px
held-out p90 residual. Replaying the existing calibration ZIP admits only 17
views, insufficient for the new coverage gate. These are numerical and retained
artifact tests, not physical phone/clinical validation. The new view-selection
limits are provisional engineering checks. The reference stage uses pinned
[iKalibr](https://github.com/Unsigned-Long/iKalibr) and standard COLMAP. Local CUDA
extraction/matching have an explicit CPU fallback; final calibration remains CPU
because the reference Ceres build lacks CUDA. Both software identities are saved;
old custom geometry fits are preserved as historical prototypes, never fallback
substitutes. All three raw sensors remain exported, although iKalibr uses only
camera/accelerometer/gyroscope. Optional factory fields are audited, not certified.

Both published-reference controls completed: the CPU final run reused earlier
image preparation, while a separate fresh CUDA SfM run registered 199 images.
The GPU-assisted numerical control gives 6.46 mm translation, 0.033-degree
rotation and 0.161 ms clock-offset error against known synthetic inputs.
Extraction/matching took 24/19 seconds; total fresh processing took 15.6 minutes
because final optimization stays CPU. Different COLMAP versions and preparation
prevent a controlled overall speed comparison. These results and the observed
RTX 5060 activity are stored in notebook executions 51–52. Forty research checks
pass, including disclosed fallback and stopping only the timed-out job container.
The computer-only follow-up passes 188 app/43 research checks and Android export.
An actual companion/browser check verifies drawn framing, progress/completion,
computer board/panel fit and optional tablet layout using a synthetic image and
simulated native counts. Whole/partial/absent targets exercise real OpenCV detection;
it is not a physical phone capture. A job-saving race is corrected so completion
is published only after its durable file is closed. Physical phone,
complete noise and clinical distance validation remain incomplete.

Profiles are device/camera/pipeline/optics-bound and separate from each patient's
standing baseline. A returned reference result remains review-required and grants
no full calibration, validated metres or clinical stopping. Complete noise,
geometry conventions, repeatability/residuals and independent routes remain
unverified. The existing Android tracker is still a prototype rather than a native
VINS/OpenVINS integration. New native calls require a replacement APK.
See the [current implementation and primary sources](../../docs/REHAB_ASSESSMENT_PRODUCT_SPEC.md#published-calibration-integration---7-october-2026)
and [local computer setup](../../android/research/CALIBRATION_SETUP.md).


Release verification: 0.3.6/build 15 completed on 7 October 2026 as EAS
c1617cf1-c1bb-4e83-86ab-95018b9e07b9. Local install file:
`android/dist/apk/GaitTrace-0.3.6-build15.apk` (233,356,422 bytes).
SHA-256: 592d865a76bc8e47f5ba747b25f4ffd3475cbfdda035655d2dd1b1d4d9951bb1.
Runtime e1383287be615da4c75a7a9ce08b9260cfd2cfb3 matches local fingerprint,
EAS and APK asset. Package/version, compiled guided-lens/alignment APIs, Camera
permission, absence of microphone permission, private-LAN HTTP capability, four
OpenCV ABIs, license assets and ZIP integrity pass. All 13 native source/license
files preserve Git clean-filter bytes. Build 14 failed Java checked JSON exception
compilation and has no installable APK. No physical-device pass is claimed.
The actual local processor starts successfully, its QR payload decodes, token
health access works and uploaded board state becomes available for display.
That is a local CLI/HTTP smoke check, not physical phone/Wi-Fi pairing validation.
At that initial verification, source/OTA publication was pending. Its scope is listed in the
ignored local publication-review page.

### Prior build-13 native acquisition preparation - 7 October 2026

The local 0.3.5/build 13 candidate separates acquisition callbacks from serialized
JPEG/storage/tracking work. The former 65 ms artificial image throttle is removed.
A bounded four-frame queue reports dropped image callbacks; a 5,000-event sensor
backlog stops with an integrity error rather than silently discarding IMU. FIFO
shutdown drains accepted work before ZIP creation. Camera capture-result/saved
rates, queue peaks and timing delays are exported. Acquire-latest driver losses
are not all attributed to the queue counter; compare metadata and saved counts.
Image callback latency is only comparable for a real-time camera hardware clock.
30 Hz remains a request, not a measured or guaranteed device rate; raw hardware
samples are preserved, separately from normalized 50 Hz clinical exports.

Phone calibration now offers **Camera board** and **Sensor noise**. The board can
be shown digitally on a fixed tablet/monitor, at the previously verified physical
square size. Record whether capture is through the usual waist-bag window or a
clear lens. New processed profiles bind capture-pipeline and optical-setup fields;
this is a user declaration, not automated proof of a clear lens or body location.
A separate five-minute, camera-free stationary capture saves all three sensors
under `camera-imu-noise/`; exporting it cannot overwrite the board capture.
Start awaits completed speech, cancellation/backgrounding prevents a late start,
and finish speech keeps the screen busy until completion. New cues are EN/MS/ZH.

`imu_noise.py` fits overlapping Allan deviation only to completed device-bound
stationary captures with valid SI values and sufficiently regular clocks. It
rejects movement, gaps and short records. A slope near -1/2 supports a short-term
white-noise candidate. Five minutes does **not** establish bias random walk;
stationary acceleration includes gravity and is not an accelerometer bias.
Longer stationary recording and review will be needed for the complete noise
model. The old walking ZIPs are correctly rejected as noise-calibration inputs.

`vio_readiness.py` defines a future-estimator engineering contract: full measured
geometry/noise and device/optics binding, two seconds of continuous initialized
tracking, no reset in that window, sufficient features, plausible complete vector
states and stable extrinsics/time offset. These provisional limits require tuning
and independent validation. Existing scalar-only replay telemetry is insufficient.
The current Android tracker has **not** been replaced by VINS/OpenVINS; new native
exports explicitly block metric readiness and the UI withholds old metre fields.
No clinical stopping criterion, full calibration or independent accuracy is granted.

Executed validation: TypeScript, 177 app checks, 35 Python research checks, actual
JVM bounded-queue/concurrency/hardware-clock checks and 10 browser flows pass.
The themed notebook records execution and source hashes in the same batch. The
browser/renderer checks do not establish physical audio, Camera2 or phone speed.
New native calls require a new APK; build 11 cannot acquire them via OTA. EAS
0.3.5/build 13 is submitted as 478fc333-8bae-48b2-9666-47fa55196b74; build and downloaded APK verification now pass. Physical performance remains
pending. Build 12 failed a Kotlin JSON-map type check; the explicit-cast
correction is verified in build 13. No Git push or
OTA publication. Research outputs, ZIPs, dependency/toolchain files and APK stay
local/ignored. Exact source scope must be reviewed before publication.

### Prior offline decision: VIO replay complete, calibration and capture next

New offline execution compiles pinned VINS-Mono estimator sources with Ceres 1.14
and a reusable ROS-free wrapper. Diagnostic Python feature tracking preserves five
lens coefficients and raw image rows; it is not the original VINS frontend. All
three retained phone ZIPs replay with real clocks and disclosed reference noise/
zero-translation starting assumptions. The corrected static-storage harness passes
an analytic non-gait known-geometry control (559 initialized states, 0.0003602 m
rigid-only position RMSE without scale fitting). All 26 Python research checks pass.
OpenVINS also compiles as a desktop library with a Boost 1.90 build-only patch;
its phone replay/front-camera Android integration/rolling-shutter suitability
remain untested. Third-party source/binaries stay out of source commits.

First two recordings retain 154/161 initialized states after the app motion trigger
and no resets; provisional IMU-position path lengths are 3.122/3.982 m. Only the
first route was reported as 3 m, and neither is independent accuracy evidence.
Third recording has 99 post-trigger initialized states, diverges to 23.13 m/s,
resets and ends uninitialized: no route distance is admitted. Full input includes
setup; JPEG replay differs from native luma/live scheduling. First original device
capture lacked a profile; matching retained geometry is applied offline only.

Startup sensor separation estimates briefly reach impossible 8.107/0.659 m before
later settling to phone-scale values; all runs refine rotation by about 26 degrees.
First two refine the -29.73 ms initial offset to approximately -3.63/-4.29 ms.
These adjustments expose unverified calibration/readiness, not an isolated cause.
A state labelled initialized cannot automatically start a clinical measurement.

[Full executed comparison and next contract](../../docs/REHAB_ASSESSMENT_PRODUCT_SPEC.md#executed-established-vio-feasibility---7-october-2026).
Next: modernize capture and establish full calibration/noise plus stable-start
readiness, then assess native integration and independent marked routes. Preserve
20-30 Hz actual frame-input ambition separately from 50 Hz gait exports, digital
stationary-tablet calibration and patient standing baselines. Do not ask for another
walk on unchanged build 11 or fit scale to the known route length. No clinical
metric, new APK, runtime, OTA or Git publication; distance/full-calibration/
independent-validation flags remain false. Prior source-only review is historical.

### Better-placement physical trial - 7 October 2026

User reports a slip during the preceding setup and better mounting in the new
trial distance-trial-1791349358636. Source SHA-256:
b47807a3ccfc7f0d1ac57830268b88c0d137b7883b0297a0803aea1490bb1642.
Profile is present and release remains 0.3.4/build 11. Native tracking improves
from one to six poses, with 25 renewed map points and one candidate keyframe.
Failure occurs 0.721 s after the movement trigger instead of 0.230 s. Both runs
reject reprojection-error: 1.5537 px here, previously 1.6478 px, versus the same
1.5 px engineering gate. No accepted scale, metre estimate or route error.
This is modest tracking improvement, not a successful distance result.

Full capture lasts 28.478 s; visual tracking begins around the movement trigger
13.677 s after capture starts. Setup duration alone does not enter the visual
trajectory; early IMU rows are stored but scale interpolation would use pose
segment times. There is appreciable movement in the two seconds preceding the
trigger. The records do not identify an exact slip time or prove that motion
was placement rather than walking, and do not validate first-step timing.
The operator report makes a placement effect plausible, not an isolated causal
finding. Failure with better placement shows handling is not the whole problem.

Acquisition remains healthy: 353 frames at 12.686 Hz, all matched to camera
metadata, max gap 103.6 ms. Accel/gyro 5,938 each at 210.407 Hz with max gap
4.89 ms, magnetometer 1,411 at 50 Hz with max gap 20.0 ms. All finite/monotonic.
JPEG artifact replay using the included profile and actual first native frame
rejects after one pose (1.7598 px). JPEG/native luma and RANSAC differences mean
it is not bit-identical and cannot overwrite the actual six-pose device result.
Sampled images still show holder obstruction and walking blur. No isolated cause
or validated distance error can be inferred. Route length was not restated.

Both profile-loaded physical captures remain available to validate a more robust
bootstrap rather than fitting only the first walk. The current next step is the established-VIO feasibility benchmark above,
including initialization, camera-motion/occlusion handling and start-cue timing
before metric consistency. Do not relax the gate just to accept the near-threshold
sample. Executed audit/replay outputs are in the existing notebook. Raw/private
artifacts stay ignored. No app change, new APK, OTA or source publication in this
review, and the existing publication scope has not been approved.

### Latest physical retry - build 11, profile present

Reviewed distance-trial-1791349028491 (SHA-256
e53a543aa1211aeb5042c2fc5d76355f6f1a3f466f842a11ee2398a304068899).
Actual 0.3.4/build 11 native capture contains the matching research profile.
On-device tracking obtains one pose, then rejects reprojection-error 0.230 s
after the movement trigger: coordinate reprojection RMS 1.6478 px exceeds the
unchanged 1.5 px engineering gate. It adds zero landmarks and zero keyframes.
The map-renewal stage therefore never becomes useful on this live trial. No
metric estimate, distance error, gait speed or independent validation is available.
Route length was not restated, so it is not assumed to be 3 m here.

Acquisition is healthy: 367 camera frames at 12.64 Hz, all with capture-result
metadata, max frame gap 133.2 ms. Acceleration 6,179 and gyro 6,178 samples at
210.37 Hz, max gaps 4.92 ms, magnetic 1,469 at 50 Hz, max gap 20 ms. All sensor
values finite and times strictly monotonic. Automatic quiet-stop completed the
29.65 s capture, 12.98 s after the movement trigger. Finish includes quiet time,
so this duration is not walking speed or a measured-course timing result.

Explicit JPEG replay, supplied the profile stored in this ZIP, also produces one
pose and rejects reprojection-error (1.6152 px). Its feature count differs from
native luma, so it is not a bit-identical live replay. The reusable desktop
replayer now starts at the actual first tracking-log camera timestamp instead
of dropping frames just before the wall/motion trigger. First native frame is
2.97 ms before that trigger in this capture. Earlier replay outputs are retained
with their original cutoff semantics and are not relabelled as device results.
All IMU samples are available before images offline, so live latency is untested.

Sampled images show holder obstruction, walking blur and textured room features.
Their individual causal contributions have not been isolated. Current evidence
supports a fragile visual-map initialization, not missing profile or sensor data.
Next work should validate initialization over multiple views and investigate
holder-feature rejection/rolling-readout and blur handling. Do not relax the
1.5 px gate or request repeated walks as if profile import solved odometry.
The earlier retained walk's 151-pose replay did not demonstrate general live
robustness, and its scale also remained rejected. Raw ZIP/profile/images and
outputs stay ignored. Actual audit/replay code and results are in the existing
notebook. No Android source change, APK, OTA or Git push in this review.

### Camera-distance retry implementation - 0.3.4 / build 11

Start is now unavailable until a matching phone research profile has been
imported. Missing profiles are also rejected by the native capture API. EN/MS/ZH
prompts present import as the required first action. The saved profile persists
when installing the APK over the existing application. Export of older trials
remains available.

The Java tracker now renews scene landmarks from accepted world-camera poses,
with forward/backward flow, positive depth, parallax, reprojection and spacing
checks. It preserves the existing map scale and never stitches independently
initialized maps. PnP, timing, IMU and physical-fit rejection limits are unchanged.
Method identifier is native-growing-map-scale-v2. On the retained development
3 m artifact, explicit profile replay improves from 20 poses/1.50 s to 151
poses/11.823 s, adding 318 points across eight candidate keyframes. No tracking
loss occurs in that replay. Metric scale still fails physical checks, including
implausible fitted bias. No accepted distance or route error is claimed. All IMU
is available before frames in replay, so live callback latency remains untested.

Validation: TypeScript, 173 app checks, 21 Python numerical/rejection checks,
six actual desktop JNI checks, 10 browser flow tests and web export pass. The new JNI check confirms
renewed landmarks preserve known map coordinates and scale. Executed source
hash/results are retained in the existing notebook. Native changes require a
new 0.3.4/build 11 APK, runtime 36ef802b5c8463d2c0a172abd85bb56d75f0ea0e.
Final 0.3.4/build 11 completed successfully on 7 October 2026 (EAS
784326fd-4a29-4477-a61b-58f93000b00f). Downloaded APK:
`android/dist/apk/GaitTrace-0.3.4-build11.apk`, 233,322,494 bytes, SHA-256
93c94fa267bd4ecea6083c374e2d1f69a2829a92725c3401ff51cbc3335081fa.
Compiled package/version, ZIP integrity, revised growing-map method/profile
prerequisite, four OpenCV ABIs and license assets verified. Runtime remains
36ef802b5c8463d2c0a172abd85bb56d75f0ea0e. Install over the existing app,
open Research tools > Camera distance trial, import the same phone research
profile once if absent, then Start and follow the cue. Walk the measured short
route, stand still until finish and export the diagnostic ZIP. Physical retry
and metric accuracy remain pending. No Git push or new OTA has been made.
Clinical boundaries and distanceReady remain false. Exact-scope publication
review is required before source push.

### First physical 3 m trial reviewed ? 7 October 2026

The supplied distance-trial-1791347211905 ZIP (SHA-256
0636e70d9e720042081a1dac6bae75adf585c99fab21945e5a385d1a83d6b588)
confirms 0.3.3/build 10 physical capture and automatic quiet-stop. User reports
3 m, not independently measured here. Camera saved 270 matched frames at 12.82
Hz, maximum gap 133.2 ms. Accel/gyro each have 4,510 samples at 210.40 Hz,
maximum gap 4.90 ms, and magnetometer 1,072 samples at 50 Hz, maximum gap 20 ms.
All values finite and sensor times strictly monotonic. Capture 21.59 s, motion
trigger at 9.23 s, finish 12.37 s later including the final still interval.
Substantial movement precedes the trigger, so exact first-step timing is not
established. No speech-completion behavior is independently confirmed by this ZIP.

The profile was absent in the on-device ZIP: needs-profile, zero tracked poses,
no distance. Applying the existing bound rotation-only profile in an explicit
offline replay obtains 20 poses over 1.50 s, then rejects inconsistent-map-pose
1.84 s after the movement trigger. Features fall from 413 to 30. All IMU samples
are available before images in this replay, so it cannot validate live latency.
No metric distance, route error or gait speed is accepted. Sampled images show
holder obstruction and motion blur alongside textured room features. The causal
contribution of these image conditions has not been isolated.

This is a useful real capture and a failed distance-estimation trial, not successful
3 m validation. Next gap: clearly enforce the profile prerequisite for metric
trials, improve fixed-map continuity/map renewal and test against this saved
walk before requesting another repeat. Investigate pre-trigger movement/cue
alignment. Import alone is insufficient, and thresholds must not be loosened to
force a 3 m answer. Notebook stores actual audit/replay code, outputs and processor
hash. Raw ZIP/images/profile/generated reports remain local and ignored.

**7 October app integration:** local 0.3.3 now includes a separate Android
Camera distance trial with native Camera2 capture and Java/OpenCV fixed-map
tracking/scale calculation. Patient-paced placement and fresh stillness precede
a fully completed voice cue; motion starts tracking and sustained quiet ends
the trial. Profile import is separate from accepted full calibration. Estimates
are withheld on missing profile, map loss, clock/IMU gaps, unobservable scale or
failed consistency gates. A single ZIP retains images, all three IMU streams,
frame results, profile, tracking diagnostics and app release identifiers.
Normal clinical tests and observer-form requirements are unchanged.

172 app tests, TypeScript and Android bundle pass. Five desktop checks execute
the actual Java algorithm with real OpenCV JNI (synthetic scale 2.7301 versus
known 2.7000); this is not Android capture/physical validation. Actual replay of
the second bench capture processes 443 post-five-second frames, produces one
map pose and rejects tracking (inconsistent-map-pose). All IMU samples are
available before frames in that replay; it cannot validate live callback latency.
Final native 0.3.3/build 10 completed successfully and its downloaded APK was
verified (package/version, ZIP, native tracker, four OpenCV ABIs and licenses).
Runtime is 037f976718a2d2ef78c79b8705adeb04596f072c. Build includes release
provenance and dependency-license assets. Install over the existing app, import
the separate rotation-only phone research profile in Camera distance trial,
walk a measured short route after the cue and stand still for automatic finish,
then export its ZIP with the independent route length/turn notes. No entered
route length supplies scale. The new APK is local under android/dist/apk.
Installed-device trial and
independent measured-route validation remain pending. Research camera path is
a tracked interior segment, not proven whole-route distance. No Git push/new OTA.

The 6 October local processor now uses each detected corner's exposure/readout
time rather than a single frame instant. On calibration-1791298033545, joint
camera/gyro fitting passes internal rotation/timing gates: held-out coordinate
RMS 1.1594 px, p90 1.6068 px, candidate offset -29.73 ms. The confirmed
moving-tablet first capture fails the same pixel model (6.9382 px RMS).
Mean-row correction alone still fails the original angular-rate gate
(0.08162 rad/s); no existing threshold was relaxed.

This is a rotation/timing candidate, not an importable full profile. Translation
screening finds 218 usable poses but no sufficiently long contiguous segment;
the largest accepted-pose gap is 2.136 s. Fixed-map visual tracking also loses
tracking on the second bench capture. Neither capture establishes walking
distance accuracy, and second-capture target stationarity is not operator-confirmed.

New reusable Python prototypes preserve one visual map scale and fit metric
scale/bias/gravity/lever arm from SI IMU data. Known-answer synthetic recovery,
pure rotation, absent excitation, inconsistent motion and tracking-gap checks
pass. A separate Android research implementation is now available as described
above. Rolling-shutter visual tracking, map expansion/continuous inertial fusion
and independent measured-route validation remain unfinished. Existing clinical
capture/stopping is unchanged; the new research native functions require a
replacement APK. Camera distanceReady remains false.
Executed analysis is in the [calibration notebook](../../notebooks/phone_camera_imu_calibration.ipynb).
Raw images/ZIPs/generated reports remain ignored/local. No source push or new OTA.

## Calibration ZIP persistence repair

User screenshot identifies a build-8 persistence bug: native File.toURI and Expo documentDirectory refer to the same ZIP but spell the URI differently, so copyAsync attempts a self-copy. Local repair skips same-path copying, validates the nonempty ZIP, and reconstructs missing latest.json from the newest valid native manifest/ZIP. Interrupted capture status is preserved. Existing source files stay unchanged; this does not validate geometry or distance. Four regressions, 165 app tests, TypeScript and Android bundle pass. Published by explicit user approval on 6 October 2026: Android preview OTA 01a11195-6294-7fba-93b2-b6eb1f075a52 (group 00541cb9-c847-468e-9f68-5ab0c2942d5c), runtime 0894d523161346acbefbbe6ac62b46e3a244f31f, compatible with 0.3.2/build 8. Server-side update and active preview-channel mapping verified. Installed device receipt and recovery remain to be checked. Source Git publication remains unapproved/pending; no Git push made. Preserve installed app data to retain the original capture.

## Researcher phone calibration acquisition and processing

Local 0.3.2 adds Research tools > Phone calibration, a 40-second native front-camera
ChArUco-board capture. First five seconds are still; subsequent multi-axis tilts
and translations establish geometry/timing observability. Actual frames, hardware
timestamps, exposure/skew metadata and three raw native IMU streams are retained
in a private export ZIP. Same holder optics must be used; displayed or printed 20 mm square
scale must be checked. Calibration is per physical phone/camera configuration,
shared by all participants; each participant's standing baseline stays separate.

[Calibration notebook](../../notebooks/phone_camera_imu_calibration.ipynb) records
executed numerical/admission tests and processes a supplied capture. Accepted
geometry reports can be imported only on the originating installation/configuration.
Wrong phones/pipelines, incomplete captures and false distanceReady claims fail.
The first real ZIP has now been processed; acquisition/lens fit is supported but full camera/IMU alignment remains rejected (see actual-capture review below). Seven Python recovery/rejection
checks, 161 app checks, TypeScript and Android Metro export pass; native APK build
8 finished successfully; downloaded APK integrity/package/version/native module and camera-only permissions pass. Physical capture validation remains pending. No source push/OTA published.

Geometry remains candidate, distanceReady=false. No odometry estimator or validated
automatic distance endpoint is implemented. Older Expo MP4 uses different camera
pixels/clocks and cannot directly reuse these intrinsics. Internal held-out frames
are not independent route validation; full IMU-noise and magnetic calibration are
not measured. Local artifacts and dependencies remain ignored.

## Simultaneous mounted-camera research trial

Local version 0.3.1 adds Android Research tools > Camera + IMU trial. It captures real front-camera video alongside accelerometer, gyroscope and magnetometer while retaining horizontal lower-back screen-out mounting. Camera permission is in-app; video is muted and uncropped, microphone permission blocked. One tap starts acquisition, followed by completed placement speech, five settled seconds and a complete walking instruction. Fresh movement starts the chosen 15/30/60-second walking window; rests are allowed and capture stops automatically. Placement is participant-paced, bounded only by a ten-minute/150 MB capture safety cap.

Matching-ID MP4 and JSON export from the trial or saved recording. JSON retains native IMU timestamps and monotonic events, but actual camera frame/start times, calibrated clock offset and synchronization error are unavailable; vioReady is false. Concurrent capture is implemented; metric camera distance and calibrated VIO are not. JSON imports do not include video bytes. Engineering trials remain outside G.A.I.T. requirements and clinical trends. Mounted room footage does not replace full-body observer video.

153 automated controller/storage/UI tests, 10 web workflow checks, TypeScript and Android Metro export pass. The initially supplied JSON was a separate failed 0.154-second attempt. The corrected user-confirmed counterpart (09:20:48 UTC, ID ending 5084d08e) contains 41.288 seconds, a saved video reference and three continuous streams, consistent in duration with the 41.13-second MP4. Whole-capture native rates are 81.05/80.79/37.08 Hz, with no native gaps above 100 ms. The strict movement-to-stop window is 33.741-41.288 seconds (7.547 seconds), ended by a user-stopped action. Earlier motion around 23-39 seconds overlaps the walking instruction and is retained separately as exploratory evidence. Precise frame alignment and gait/distance accuracy remain unvalidated. Version 0.3.1 requires a new camera-enabled APK. EAS build 7 completed successfully; source publication awaits review. See [capture specification](../../docs/REHAB_ASSESSMENT_PRODUCT_SPEC.md#simultaneous-front-camera-and-imu-trial-6-october) and [corrected sample review](../../docs/classification/WEEKLY_PROGRESS_2026-10-05.md#corrected-export-actual-concurrent-capture-and-window-selection).

## Local participant workflow

Current camera-trial flow is simplified locally: no long briefing or default duration picker. Tap Start, mount/stand still, follow one short walking cue, then stand still at the finish. Four fresh quiet seconds after movement end capture hands-free; 60 seconds is the default fallback. A pause can also end this engineering trial, so quiet-stop is not proof of a measured boundary. Clinical tests and their rest handling are unchanged. Technical settings/result details are collapsed, exports visible. EN/MS/ZH, 157 tests and Android export pass; publication remains pending, compatible with build 7.

Current 6 October worker flow: all real non-practice gait recordings require observer G.A.I.T. review, with unfinished records first in history and participant dashboards. Raw capture saves independently. A dedicated English-only clinical wizard has one assessor-details page, individual item cards, phase/criterion explanations, branch selection, pinned navigation, saved drafts and a paper-order overview. Patient UI/speech remain English/Malay/Chinese under the agreed policy. Drafts resume at the first unresolved item and navigation saves edits before leaving. Unobserved criteria remain missing, never zero. Practice and Google provider experiments remain outside labelled analysis.

JSON and feature CSV identify pending/complete review and observer-label readiness explicitly; these are not clinical-validation or sensor-quality flags. Complete G.A.I.T. labels are required for dashboard measured-speed trends alongside existing measured-course/protocol/aid rules. Raw exports and descriptive signal checks remain available. The 6 October batch is local pending publication review. See [current weekly progress](../../docs/classification/WEEKLY_PROGRESS_2026-10-05.md).

Reviewed the user's 9.57-second front-camera bag clip locally: room visibility is demonstrated, with upper-edge obstruction, blur and large angle changes. Follow-up comparison of 12 frames suggests roughly the upper 10-20% of image height is obscured in several frames; the boundary varies. This visual estimate supports testing a conservative tracking mask, not a validated distance-accuracy acceptance threshold. There is no synchronized IMU/calibration or measured route reference, so distance and tracking error were not estimated. Front-camera odometry is still unimplemented/unvalidated. The mounted outward view does not replace full-body observer video for G.A.I.T. See [sample review and next measurement requirements](../../docs/REHAB_ASSESSMENT_PRODUCT_SPEC.md#front-camera-sample-review-6-october).

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


## Dedicated short Google distance experiment - 2 October 2026

User requested a separate experiment because setting up a 12 m course is impractical for initial API testing. Local Android source now exposes Home > Import, research tools and app information > Research tools > Google distance trial, with measured 2/3/5 m routes (default 3 m). No clinical-test chooser is required. Participant linkage, permission-before-mounting, five-second standing reference and movement/fit checks are retained. The spoken cue asks the user to return to the start after setup, wait for Begin, then walk to the mark and stand still. Raw IMU starts after first-step detection; four seconds of continuous quiet automatically ends the trial, with a 60-second safety limit. Google querying begins at the audible cue (first-step fallback), retains a fixed stop boundary, and allows delayed post-stop reads for up to 30 seconds of waiting plus request time. The rest tail is part of the Google query interval; its mean speed is not moving-only speed.

The result asks whether the finish was reached before offering a direct full-JSON export. Reference route, completion and endpoint survive JSON and raw CSV review. Google records remain distinct from measured reference and raw IMU; no missing data is fabricated or replaced by a height estimate. A rest can terminate this engineering experiment early; the user can report that explicitly. Trials have versioned metadata and practice tagging, remain linked to participants/history, and are excluded from clinical speed trends and personal distance calibration. Normal clinical flows are unchanged. EN/MS/ZH text added.

Verification: TypeScript, 123 automated tests and Android/web Metro exports passed. These are software/contract checks, not native compilation, physical validation or measured accuracy. Google short-route availability and latency must be assessed on the actual holder; a new APK containing the Google module remains required and has not been built. This follow-up is local pending publication review. No model training or new dataset acquisition.


Build/publication result (2 October 2026): commit `54fb0f4` was pushed to main and all three GitHub workflows passed. EAS preview build `d3529b4c-e5f5-443c-9a15-01e4f7286bc8` completed successfully as GaitTrace **0.3.0 / Android build 6**, using the existing application/signing identity. Native Google module compilation passed. Runtime `a48c2ed43ddd2142beaa39b7f8031b8fff327407` matches the published Android preview update group `8e92c2d5-ef7f-499d-b5ad-470471c488b2`. [Direct APK](https://expo.dev/artifacts/eas/5sYVRhaXoeMJQDYTPrjgfXq7aSLe2wTlboCAzbZFoqU.apk). Local download target: `android/dist/apk/GaitTrace-0.3.0-build6.apk` (ignored). Physical installation and Google distance accuracy/latency remain unvalidated. Build-result documentation is retained locally for review; generated APK/log/metadata are not source commits.


### Actual 3 m trial evidence - 2 October 2026

Inspected export `gait-2026-10-02T09-41-45-834Z-18c37e2e.json` from build 6: 7.465 s of raw accelerometer/gyroscope/magnetometer at 82.15/81.77/36.61 Hz, finite samples and monotonic native timestamps with maximum gaps below 41 ms. Google returned no records across 10 successful reads including a final read 30.457 s after capture end; distance/steps/speed remain unavailable. No API errors or application boundary exclusions occurred. This is an availability failure for this trial, not measured Google distance error or proof of the underlying cause. User confirmed tapping Stop immediately at the finish, so automatic quiet-stop was not tested. The separate height-based estimate was 4.94361 m against the entered 3 m reference (conditionally +64.79%); it is not validated distance. Seven candidate peaks/70.59 steps per minute remain unverified, and clinical symmetry is undetermined. Raw data may support engineering analysis; this short trial does not validate gait outcomes or training labels.

Local audit: `android/dist/verification-google/trial-18c37e2e-review.md` and `.json` (ignored); original export remains outside source. Concrete next gap: separate broader-context/aggregate provider diagnostics while subscribed, preserving original test-window provenance and not attributing setup movement to the 3 m trial. Provider batching/availability/query behavior is unresolved. No implementation fix, model training, new dataset acquisition or push in this review.


### Connected-phone diagnostics (no new walk) - 2 October 2026

User chose diagnostics only. ADB confirmed installed 0.3.0/build 6 on Redmi Note 10 Pro / Android 11, granted activity recognition for both GaitTrace and Play services, Play services 26.36.33 and exposed hardware step-counter/detector sensors. Historical sensorservice entries show Google's Fitness LocalSensorAdapter requested 60,000,000 microseconds sampling/batching on a step counter (17:38:58 registration, 17:42:16 removal). Earlier JSON final empty read was about 17:42:16, 30.457 seconds after capture stop. This makes observation latency a plausible unresolved issue, not a proven root cause or new successful distance query. Narrow provider query behavior remains unresolved. Release APK private storage is unavailable through run-as; no bypass attempted.

Ignored diagnostic report: `android/dist/verification-google/connected-phone-diagnostics-2026-10-02.md`. Next implementation candidate is diagnostic-only broader-context queries plus a longer bounded read window while preserving fixed trial timing and separate context totals. No new walk, recording, app-data reset, code change, APK install, permission change, model training or push.


### Stationary Google API access check - live result, 2 October 2026

User clarified that basic API-access testing should not require walking or long waits, and requested a fresh call while connected by cable. Added a dedicated Research tools quick-check screen: availability/permission, subscription, 60-second and 600-second context reads, then unsubscribe. No participant, placement, countdown or gait recording. Explicit API-success versus records-available states prevent interpreting empty responses as failed connectivity or zero walking. Context counts are not trial distance; waving is not gait validation. Four-second request timeouts, failure cleanup and late-subscription cleanup included, with translated EN/MS/ZH UI and structured technical logs.

TypeScript, all 126 automated tests and Android Metro export passed. Native runtime fingerprint is unchanged and matches installed 0.3.0/build 6 (`a48c2ed43ddd2142beaa39b7f8031b8fff327407`), so no new APK was required. Approved commit `3ccb972` was pushed and the Android preview OTA workflow passed. The installed phone loaded the new screen. A fresh live check at 10:23:07 UTC on 2 October 2026 completed in 299 ms: availability, subscription, 60-second read, 600-second read and cleanup all passed; both windows returned zero records and no errors. The result card was fully visible on the phone. This verifies provider API access, not walking distance production or accuracy; gentle waving is not a gait validation. The earlier 3 m missing-distance result remains unresolved. No 90-second wait or normal clinical timing change was implemented.

The native parser was checked against the Recording API contract. It requests detailed distance/step delta datasets and reads their typed fields; it does not use Google Maps Routes or Directions, so Maps field masks and JSON route paths cannot explain the missing output. The quick check's immediate subscribe/read/unsubscribe sequence provides no meaningful opportunity to generate walking records and cannot access records before the subscription. The earlier 3 m trial subscribed before walking but still returned no records; the provider's actual availability/latency on short lower-back walks remains unresolved.

Local diagnostic refinement: the final delayed read in the dedicated short trial now also queries a broader post-finish context interval in parallel. Its records and poll timing are preserved in JSON as `contextObservations`/`contextPolls` and never enter trial distance, steps, speed or the stop rule. Android's mobile Recording API specifies activity recognition permission, which the app obtains before subscription; its documentation does not establish a blanket background-location requirement for this data type. Neither Health Connect nor Maps routing supplies automatic 3 m lumbar-walk distance for this app. Software checks passed; the phone is disconnected, so provider-data availability remains physically unvalidated.

The separate Google distance experiment now has a **10 m total out-and-back** option: measure 5 m to a turn mark, walk there and return to the start. It has distinct spoken and written instructions, an eight-second quiet finish and a 90-second fallback. The measured route and `5m-out-and-back` pattern are exported in JSON/CSV, and the trial remains practice-only. A comfortable turn is allowed, but the app cannot confirm the turnaround crossing or guarantee Google will emit records. This is not the clinical 10MWT, which uses a straight marked course and a timed zone. Approved commit `8e553c3` was pushed on 2 October 2026 and all GitHub workflows, including compatible Android preview OTA, passed. Physical validation remains pending.

## Profile entry parity and protocol sources - 4 October 2026

Verified source already contains age/sex/height/weight, walking aid, stroke type/location, hemisphere/body side, chronicity, history source and pre-existing gait/orthopaedic notes. Clinical tests already require explicit hemisphere/body side/chronicity/source, allowing unknown; optional clinical information must not be guessed. The gap was test-created profiles: setup lacked weight, stroke type/location and baseline-history inputs. Added those to the existing details/history panels, made stroke-history review discoverable for research walks too, and retained prefill and reset when selecting/changing participant. The resolver preserves omitted existing fields and validates entered weight. Both saved profiles and recording snapshots now receive these inputs; JSON retains full context and feature CSV additionally exports baseline gait/orthopaedic notes with CSV escaping.

Clinical tutorial worker notes now link each 10MWT/TUG/2MWT/6MWT to its specific Shirley Ryan AbilityLab RehabMeasures source. Source availability does not validate automatic phone endpoints. Existing 12 m/central-10 m variant, trial timing and clinical limitations are unchanged. New prompts have English/Malay/Chinese coverage. TypeScript, 134 tests (including rendered setup-to-snapshot and clinical export checks) and Android Metro export passed. Generated bundle stays ignored/local. No physical-device or clinical validation was performed; no native/dependency changes, so a compatible OTA can deliver this after publication. Changes remain local for user review.

## Assessment form discoverability - 4 October 2026

Audited the user's earlier assessment-form request. ResultScreen already stores a per-recording test-outcome form (completion, observed timing/distance/laps/rests, exertion, symptoms, notes and optional observed scale/score), but its entry was misleadingly labelled Add measured reference (optional). Renamed the entry to Gait assessment form, placed a clearly labelled entry near the top of results, and added an entry/status to saved-recording summaries. Saved details navigate directly to the expanded form. At this earlier audit the form was observer-entered but not item-by-item; that gap is completed in the subsequent Complete observer G.A.I.T. section below. Google engineering trials stay excluded. English/Malay/Chinese prompts, TypeScript and 134 tests pass. No physical-device review or publication occurred.

## Complete observer G.A.I.T. and sensor-free flow testing - 4 October 2026

Completed the user-supplied Appendix A digital form: 31 observer-rated items, maximum 62, source SHA-256 recorded in gaitRubric.ts. Preserves all 129 scoring choices, including equal-score alternatives and A/B/C/D branches; directional qualifiers, item notes, assessor, date, assessed limb, diagnosis, device/orthosis/assistance and observation/video reference. Missing items are never zero. Full totals require all ratings, necessary qualifiers and core assessor metadata. No sensor-derived G.A.I.T. scoring or clinical improvement claim is made. Original detailed rubric remains English; English/Malay/Chinese interface labels are not claimed as validated instrument translations.

The form is saved with each recording and participant snapshot, reopened from recording details, validated on JSON import, exported as per-item option/score/notes/qualifiers in feature CSV, and displayed as an observer total in dashboard session summaries. This supersedes the earlier incomplete-form status in this batch. No new clinical recordings or assessment validation were acquired.

Added a development-only browser Flow Lab and Playwright phone-viewport tests. Fixtures are clearly marked, contain no sensor samples, are practice-only and memory-only, and cannot enter native/release capture. Existing React Native tests inject sensor events/speech callbacks for acquisition logic. Browser tests cover saved full form, profile/tutorial navigation and actual shared preview start/finish components for 10MWT, TUG, 2MWT and 6MWT; long timers use a controlled test clock. This is not an Android emulator or physical-sensor/audio validation.

Validation: TypeScript, 138 unit/flow tests, six browser E2E tests and Android Metro export pass; generated screenshot inspected. Test outputs and source-PDF render stay ignored/local. Playwright is a development dependency only. Standalone test launch scripts retain the installed build-6 Android runtime fingerprint a48c2ed43ddd2142beaa39b7f8031b8fff327407. Run node scripts/start-flow-lab.cjs and npx.cmd playwright test from android; see FLOW_TESTING.md. All changes remain local for publication review.

## Approved publication result - 4 October 2026

User explicitly requested publication to perform phone checks. Pushed the reviewed 36-file source/documentation batch as 4d268d3. Repository hygiene, results portal and compatible Android update workflows all succeeded (Android run 37211898197). Expo preview group d8ba7fc1-ad1f-4443-b02b-363760392299 contains Android update 01a10777-32e3-787a-b168-cbfae2e54e84, with runtime a48c2ed43ddd2142beaa39b7f8031b8fff327407 matching installed build 6. App information should show update 01a10777 after download and relaunch; native version/build remain 0.3.0/build 6. Publication is verified; receipt and physical-device checks on the user's phone remain pending. Dependencies, generated bundles/screenshots/PDF renders and test reports were excluded from source commits.

## Actual calibration capture reviewed - 6 October 2026

Processed user ZIP calibration-1791297358282 (SHA-256 18ca43aa7ab2bc876399958668f16f96dafc2db006f1b7f11a3bcc1ea4bfc4ec). Completed 40.212 seconds, 499 front-camera 640x480 frames, all 499 native timestamp/capture-result matches, saved-frame rate 12.66 Hz. Raw accelerometer/gyroscope 8416/8415 samples at 210.40 Hz, maximum native gaps 4.94 ms; magnetometer 2000 samples, 50 Hz, 20 ms gap. All finite/monotonic. These rates belong to the calibration recorder, not the separate gait recorder.

Detected board corners in 397 frames; 277 supply at least 16. Corrected lens training RMS 0.1673 pixels and held-out point-coordinate RMS p90 0.1547 pixels support a provisional native-pipeline lens fit. Found and fixed an offline checker bug: Nx1x2 projected points broadcast against Nx2 observations, falsely creating NxNx2 residuals. Flatten corresponding points before subtraction; explicit regression passes. Eight Python tests pass; notebook stores actual capture results separately from synthetic checks. Earlier apparent lens rejection was a processor error, not user capture failure.

Full profile remains rejected: held-out camera/gyro coordinate RMS 0.09780 rad/s exceeds the existing 0.08 engineering gate. User confirmed the tablet target was also held/moved; static-reference prerequisite is unmet, independent of residual threshold. User verified displayed 20 mm squares (operator reported). No accepted clock/extrinsic/lever-arm calibration or walking distance. Keep this capture for acquisition/lens work; for alignment, place tablet fixed on a table/stand and move only the recording phone. Previous digital instructions omitted that crucial requirement; they are clarified rather than blaming the user.

Images, ZIP and generated reports/contact sheet remain local/ignored. Source notebook/reusable checker and current docs updated locally; no new app OTA or Git publication in this review.

## Second calibration capture - calibration-1791298033545

Executed the same corrected gates on the second user ZIP (SHA-256 df8a30cbc16ff40d21e8b3096e3f370ac87094b3ad375679998d56cbe8db6314), preserving first-capture outputs. Completed 40.241 seconds; 500 640x480 front-camera images, all with matching native capture results, saved-frame rate 12.664 Hz, maximum image gap 233.1 ms. Accelerometer/gyroscope each 8417 samples at 210.338 Hz, maximum gaps 4.893 ms; magnetometer 2001 samples, 50 Hz, 20 ms maximum gap. Finite, strictly monotonic native data. No save/copy failure.

Board corners detected in 333 frames, 226 with at least 16. Provisional lens training RMS 0.12265 pixels, held-out coordinate RMS p90 0.11681 pixels (previous 0.15472). Camera/gyro held-out coordinate RMS improves from 0.09780 to 0.080378 rad/s; existing gate remains 0.0800, so full profile stays rejected, distanceReady=false. The exceedance is only 0.000378 rad/s (0.47%); this is a borderline engineering fit, not evidence of clinically meaningful sensor failure. Threshold is not relaxed to admit the sample. Clock offset estimate -31.02 ms remains a failed-fit diagnostic, not accepted calibration.

Timing diagnostics: exposure 30-33.33 ms, rolling readout 32.203 ms; capture uses an approximate frame midpoint model. Native clocks are retained; median image callback arrival lag 75.0 ms must not be substituted for hardware time. These approximations/visual pose noise are plausible contributors, not an established cause. Early motion settles from gyro coordinate RMS 0.4305 in second 0 to 0.01614 in second 4; the nominal initial five seconds are not entirely still.

Visual contact sheet shows the tablet resting against furniture/support rather than visibly being held; target stationarity cannot be independently guaranteed from sampled images. Earlier operator-verified 20 mm display scale is contextual, not remeasured by this processor. Keep this useful capture for processing/intrinsics; no repeat requested solely for this near-threshold residual. Full rotation/timing/lever-arm validation and independent walking distance remain incomplete. Raw ZIP/images/generated reports remain local, notebook contains executed outputs and interpretations. No source push/OTA.

Final release verification: 0.3.5/build 13 completed successfully on 7 October
2026, EAS 478fc333-8bae-48b2-9666-47fa55196b74. Local APK:
`android/dist/apk/GaitTrace-0.3.5-build13.apk`, 233,341,562 bytes;
SHA-256 375704840cb52698c1efadc8fc8f522491d44e450b38e2cb07675b5633ea77c4.
Runtime fe7b72f4a02c458b1a9ae99f0a00abc90b7d73dc matches the local fingerprint,
EAS record and APK fingerprint asset. ZIP/compiled package/version, new native
noise/optics/queue methods, Camera permission, no microphone permission, four
OpenCV ABIs and license assets verified. Native Kotlin/Java compilation passed;
all 12 native source/license files preserve Git clean-filter bytes. Build 12 was
a failed compiler attempt and has no usable APK. Build 13 is the install target.

Physical test: install over the existing app; Research tools > Phone calibration.
Choose Sensor noise, tap Measure sensor noise, leave the phone untouched on a
firm table with the app open until the finish voice, then export its ZIP. Choose
Camera board, keep the digital board fixed and its square size verified, capture
through the usual waist-bag window and export that separate ZIP. Send both for
processing; no patient-specific repeat or new walking-distance claim. Full noise/
geometry and native VIO remain incomplete; a longer stationary noise record may
be needed. Do not enable clinical auto-stopping. Git/OTA publication still awaits
review; dependencies, demo assets, APKs and generated reports remain local.


### 8 October - actual build-19 capture passed; reference processing timed out

Retained job `c5edc4c934fc313c4e2a1e7b` is a completed actual phone capture:
1,960 saved images at 29.963 Hz, all three IMU streams, and zero reported image
drops or rejected sensor callbacks. Its on-device lens calibration passed,
with held-out p90 error 0.2793 pixels. Upstream reference initialization recovered
camera rotation, then timed out at 900 seconds while preparing image pairs.
There are 1,947 exported images and 2,428,611 written pairs
(63,143,886 bytes), but no upstream image-info file, completed
SfM or reference result. The bridge's bounded ~200-image selection happens after
this stage, so it did not protect initialization from the export workload.

Verified outcome: capture and lens ready, full camera–IMU calibration and distance
not ready. A saved artifact audit is in the existing phone calibration notebook.
Windows bind-mount overhead is a possible contributing factor, not measured proof.
The saved-capture recovery below supersedes that pending processing task.
The original failed attempt and its measurements remain historical evidence.


### 8 October - reference processing recovered from the saved capture

The unchanged published iKalibr executable was rerun against the actual retained
build-19 ZIP using a fresh Linux Docker volume for working files. The Windows
host boundary is crossed only when importing the original ZIP and exporting
outputs, including failure evidence. SHA-256 is unchanged:
`c5edc4c934fc313c4e2a1e7bc821daa741ecc4336556f4d53eb4143ffec12fa8`.
No raw frames or IMU streams were removed or generated. The existing bounded
SfM selection remains 195 measured keyframes. No solver or quality gate was weakened.

The previous image-pair timeout is resolved: 3,458,346 upstream pairs were written
in 32.948 seconds. CUDA COLMAP registered 169/195 images; feature extraction
took 7.834 seconds, matching 5.227 and CPU mapping 74.860. The full reference
job completed in 573.172 seconds (9m33s), including CPU camera–IMU optimization
and output transfer. Both main optimization passes report convergence.

Returned camera-to-reference-IMU separation is 36.35 mm, temporal offset
-2.587 ms in upstream convention, and readout 30.480 ms versus median camera
metadata 32.203 ms. The 16,704 in-sample reprojection errors have median
0.400 px, p90 1.313 px and RMS 0.916 px. These are fitting residuals, not held-out
accuracy or independent distance validation. Noise-model completeness,
repeatability, parameter-convention review and measured walking distance remain
unvalidated. `fullCalibrationReady` and `distanceReady` remain false.

The result was attached to the original job with capture/hash/optics checks.
The prior failed job record and logs are retained. The actual result passes the
installed app's TypeScript import contract; physical phone retrieval is still
pending. Restart the computer launcher, reconnect its new pairing code, then
tap **Resume calibration processing**. This retrieves the recovered result
without repeating capture or installing another APK.

47 Python research checks pass. New checks cover raw-copy integrity, preserved
failure evidence, GPU fallback, named-container timeout cleanup, durable result
recovery and rejection of distance-ready/mismatched recovered results.
Experiments and numeric outputs are saved in the existing phone calibration
notebook. All raw/processed captures, dependency images and proof remain local.
Source publication still requires review.


### 8 October - saved reference no longer prompts another alignment

The user confirmed the recovered reference was imported on the actual phone,
but its primary button still requested alignment. Source inspection confirmed
the action ignored `referenceSaved`, and the idle help also incorrectly said
sensor alignment was still needed. This was a UI-state defect, not processing
failure or an instruction to recapture.

The local fix makes **Back to home** the primary completed-state action, hides
capture/framing instructions and explicitly states that alignment need not be
repeated. **Repeat calibration** reveals deliberate repeat actions without
starting capture. Both immediate completion and loading an existing saved
reference use the same state. Pending newer processing retains precedence.
New labels/help have English, Malay and Chinese translations. Reference saving
still does not set `distanceReady` or admit metric tracking.

193 app tests and TypeScript pass. Component tests cover successful alignment,
resume, reopening, one exit action, no stale setup wording and repeat options
that do not launch another capture. This is component-flow verification, not
a physical run of the patched phone screen. The installed build-19 UI is not
updated yet; the user can leave with **Back to home** now. This JavaScript UI
change requires publication of a compatible update, not another APK. Source
publication remains pending review, and generated artifacts stay local.


### 8 October - distance validation and permanent recording cleanup

The reference-to-trial handoff is now implemented locally in release **0.3.10**.
The user accepted computer processing for this separate research trial. The
phone uses its saved, device-bound iKalibr reference; it no longer imports the
obsolete custom-fit profile. A separate native capture path saves camera frames,
hardware-clock accelerometer/gyroscope/magnetometer readings and the exact
reference JSON without running the old custom distance tracker. This native
change requires a replacement APK; build 19 cannot receive it through OTA alone.

Research tools now contains **Phone calibration** and **Distance validation**.
The obsolete Google API probe, Google distance trial and duplicate Camera + IMU
trial are removed from production navigation; historical readers and research
fixtures are preserved. Choose a **2, 3 or 5 m straight marked route**. Start the
computer helper, connect its setup code in Distance validation, then tap Start.
Place the phone at the lower back, screen outward, stand still, and wait for the
complete spoken walking cue. Walk to the mark, then stand still until Finished.
No screen interaction is needed while walking. Transfer and processing happen
automatically afterward on the paired computer; saved/pending jobs can resume.
The computer must run the updated helper and the existing pinned VINS executable.
Its availability is checked before the walk. Reference length is stored across
reopening and supplied only to the comparison report, never to estimator scale.

The computer adapter uses camera-to-reference-IMU quaternion/translation and
midpoint temporal/readout parameters directly from iKalibr. The pinned upstream
VINS-Mono estimator remains unchanged; the feature frontend is diagnostic Python
LK, not the original VINS frontend. Noise remains explicitly provisional. Results
suppress full-route comparison after late initialization, gaps, resets or failed
state bounds. A complete experimental estimate can be compared with the marked
route. **distanceReady**, **fullCalibrationReady** and independent clinical
validation remain false. No clinical automatic-distance stopping is enabled.
Export the raw trial ZIP and the separate result JSON for review. The new notebook
control actually executed the pinned solver: 559 initialized analytic poses,
0.0003602 m rigid-only position RMSE, no fitted scale. This is a non-gait harness
control, not phone accuracy. Actual saved-reference parameter conversion was also
executed. No new physical walking trial has been performed by the developer.

**My recordings** supports permanent deletion of selected walks and attached
videos. **Storage > Delete all recorded data** additionally clears unindexed raw
recordings, native research frame directories, their ZIP duplicates, camera/noise
captures, pending/recovery indices, export CSV/JSON copies and app camera/import
caches. Modern file/index and legacy AsyncStorage history are removed. No trash
or app backup is created. Participant profiles and compact saved calibration /
computer pairing are preserved. Downloads, external apps and desktop copies must
be deleted separately there. Errors are surfaced rather than claiming complete
deletion. EN/MS/ZH cover all new patient-facing controls and speech.

Verification: 200 app tests, TypeScript, 52 Python research checks, and Android
Metro export pass. Native build and physical first-step/quiet-stop/transfer checks
must be recorded separately from these injected-hardware UI tests. Publication
still requires review; raw captures, APKs, generated bundles and demo material
remain local/ignored.


**Current install target - 8 October 2026: 0.3.10 / build 20**

Build `0a0e43bf-ec5c-4726-ba0c-23dc7048d70b` finished successfully. Downloaded APK
passes ZIP integrity, compiled package/version, new reference-capture method,
bundled distance/deletion controls, runtime and Android apksigner verification.
The signing certificate matches existing build 16/19, supporting an in-place
update that preserves app data. Install the new APK once; build 19 cannot receive
the added native capture API through OTA alone.

[Download build 20](https://expo.dev/artifacts/eas/JaX9B4vKjCd0TlP9GugV-bbmB_zyu-vYQetz0jIdm0c.apk). Local file:
`android/dist/apk/GaitTrace-0.3.10-build20.apk` (233,384,142 bytes).
SHA-256: `a24a0e831e712e01c4333962e69460c56ec09e3598a86b25296b9be8f15a8053`.
Runtime: `f4e32256af4ee4d49a052ca0fb23beef337a0648`.

Restart `android/Start phone calibration.cmd`, reconnect its setup code in
**Research tools > Distance validation**, and use your saved calibration. Choose
3 m, tap Start, wait for the complete walking cue, walk to the marked finish and
stand still until Finished. Transfer/result return is automatic with the paired
computer available. Export trial ZIP and result JSON. An unavailable/partial
result is not a full-distance measurement. Actual device distance accuracy,
audio/automatic stop and permanent deletion still need physical acceptance checks.
Source remains local for scope review; no Git push or new OTA has been published.

## Complete calibration pipeline validation - 8 October 2026

Fresh all-CPU and GPU-assisted processing both passed on the same retained real
development ZIP. Each started in an empty Linux volume: unchanged capture
conversion, rebuilt upstream image preparation, new COLMAP feature extraction,
matching and reconstruction, final iKalibr solve, output export and result checks.
No old bag, reconstruction or calibrated parameter output was reused. Same
experimental executable/library, two threads and original algorithm limits.

| Stage / wall seconds | All-CPU control | GPU-assisted |
| --- | ---: | ---: |
| Raw import, conversion and preparation | 79.86 | 81.07 |
| Fresh reconstruction | 92.70 | 63.22 |
| Final solve and result generation | 394.32 | 148.92 |
| Complete processing | 566.89 | 293.21 |
| Including result export | 600.68 | 326.94 |

Including export, GPU assistance takes **45.6% less time**.
This is one complete run per backend on one capture. The current production
helper already uses GPU COLMAP when available; this all-CPU control is not a
measurement of the existing mixed production default. Conversion, mapping and
residual/Jacobian work are not all on GPU. Actual final-solver GPU activity is
confirmed (100% peak, engine PID present); the CPU control records 0%.

Both reconstructed one coherent model, registering 185/195 and
176/195 measured keyframes. All seven final-solver reports converge
in each run, including one empty initialization report that is not geometry
evidence. Camera/lens binding, unchanged raw ZIP digest, finite reprojection
residuals, rotation matrices and existing research geometry/timing bounds pass.
Fitted reprojection P90 is **1.382 pixels CPU / 1.369 pixels GPU**;
these are in-sample residuals, not held-out accuracy. Different CPU/GPU SfM
constraints explain why this is not a fixed-input numerical-equivalence test.
Paired extrinsics differ 4.08 mm / 0.1106 degrees,
time offset 0.338 ms and readout 0.345 ms.
No claim of clinical equivalence or improved distance accuracy is made.

The first fresh attempt exposed ROS Python-path initialization and was fixed.
Failure evidence remains in the notebook. Saved-output review then completed;
plotting dependency failures were preserved and resolved using the existing
plotting environment, without rerunning calibration or installing dependencies.

Actual loopback HTTP upload/job delivery plus the app's TypeScript poll/import/
save/reload logic pass for both actual outputs, with simulated phone storage.
Forged readiness, device binding and binary identity are rejected. The import
contract now explicitly recognizes this exact experimental image/binary as a
review candidate and retains original author-image support. This is not a
physical Android network/storage test. No installed app or saved phone profile
was changed. All 201 app tests, TypeScript and 64 research tests pass.

The complete processing path is now validated on this capture. Production
defaults remain unchanged; all candidate/full/distance readiness flags remain
false. Independent walking-distance validation, measured phone noise and
physical camera/IMU geometry remain separate unresolved research checks.
Fresh executions, retained failures, tables and analysis are saved in
`notebooks/phone_camera_imu_calibration.ipynb`. Raw/generated files stay local
under `android/dist/calibration-cuda-benchmark/full-pipeline-retry/`.
No new APK, cold-image rebuild, Git push or OTA publication was performed.


## Result integrity and expert walkthrough - 11 October 2026

Current software validation: 276 component tests, TypeScript, 1,090 native assertions and ten browser checks. Modified/unfinished 10MWT no longer produces a nominal 10 m measured speed. TUG has time only; full endurance outcomes require the standard 120/360-second interval, with one-second timer-resolution tolerance. Partial observations stay saved and are excluded from measured-speed trends. JSON retains original metadata plus a derived workerOutcome; feature CSV and dashboard use the corrected outcome contract. Raw sensor streams are unchanged.

Patient results now lead with a short saved/review status and movement observations; experimental timing is an explicit worker action. Opening worker notes moves the form ahead of patient content. The initial Android screenshot review revealed oversized repeated status cards and an unreachable worker selection after five scrolls; both were addressed and failed attempts retained. See ../../tools/mobile/APP_ACCEPTANCE.md for the detailed user/designer walkthrough and exact replay procedure, and local android/dist/acceptance/usability-summary.json for current-build native scenario verification.

This supports a supervised collector, not a clinically validated autonomous rehabilitation assessor. Full native clock captures for all five recording routes are historical evidence; the latest complete recording handoffs are controlled software replays. Real audibility, anatomical placement, measured distance, chair contact, older-adult comprehension and OEM background behaviour remain separate evidence gaps. No push or OTA publication in this batch.


Native follow-up completed for this batch: four current-APK scenarios pass, 80 control steps, with screenshots/XML/replies and failures retained. Stored modified 10MWT verified directly from the emulator: 12 s retained, completed=false, no nominal distance/speed and identical raw streams. Current APK embedded ID cbab29ca is emulator-only, not a phone release. Acceptance manifest passes. No push or OTA.


## Current collector scope and deferred rehabilitation workflow - 11 October 2026

User confirmed the current milestone is a polished collector for standard walking tests, retaining simple voice-led use, participant profiles, required assessment, signals and export. Daily practice prescriptions, check-ins, scheduled rehabilitation plans and adaptive coaching are future work. The complete proposed rehabilitation workflow is retained in ../../docs/REHAB_ASSESSMENT_PRODUCT_SPEC.md, under Future rehabilitation companion. The supported-phone/local-only requirements and outstanding measurement-validation needs remain applicable. No application code, test protocols or G.A.I.T. requirements changed in this planning clarification.

## Collector UI hierarchy and fixed review navigation - 11 October 2026

Implemented the current collector direction: Home prioritises starting a walk, recordings and participants. Dashboard/tutorials/import/setup/storage live under Tools and help, with computer diagnostics still collapsed separately. Main test cards explain purpose and route for 10MWT, TUG and 2MWT; 6MWT and research walk remain secondary. New selection/menu text has Malay and Chinese translations.

Recording detail tabs remain fixed while content scrolls; the actual emulator worker-save return reaches Notes directly without the previous four upward swipes. Raw capture, test boundaries, required G.A.I.T. forms and participant linkage are unchanged. Future rehabilitation plans/check-ins/adaptive coaching remain deferred.

Reproducible actions and local screenshots are documented in tools/mobile/APP_ACCEPTANCE.md. Software suite and native replay evidence are separate from heard TTS, camera distance and clinical/older-adult validation. Changes are local, not published.

Final collector UI evidence: five current-build emulator scenarios pass (104 controls), installed APK smoke and aggregate acceptance manifest pass. Sandbox: 276 components, TypeScript, 1,090 native assertions and ten browser checks. Actual saved modified-test outcome and raw-stream preservation pass. Failed attempts are retained; real-distance/audible-TTS/clinical evidence remains separate. No publication.

## Direct test selection and assessment access - 11 October 2026

Implemented explicit test choice for new sessions (no silent Research walk selection); retry-provided protocol choices remain preserved. Recording review puts assessment actions first and emphasises pending required assessments. Tools and help is a separate full-screen panel with Done and immediately visible import. Tool/import destinations close the panel correctly. New patient prompt is translated into Malay and Chinese; the English clinical-form policy is unchanged.

Final isolated software suite: 277 component tests, TypeScript, 1,090 native assertions and ten browser checks. Five current-build UI scenarios pass with 102 controls; native Continue is disabled before a test choice. Import and assessment access need zero scrolls in the revised replays. Actual saved modified-test outcome/raw-stream preservation and aggregate acceptance manifest pass. Older native captures are historical; this UI batch did not repeat their full real-duration walking captures.

Remaining UX refinements: persistent input labels/units, visible participant context during review, grouping long worker fields, and reducing the height occupied by fixed export controls. Evidence and reproducible steps are in tools/mobile/APP_ACCEPTANCE.md. Failed attempts remain local. No Git/OTA publication, physical distance, audible TTS or clinical validation claim.

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

Publication verification (20 October): GitHub Pages run 39358907549 deployed fbf0adf successfully. Android update run 39358907596 rejected a native fingerprint mismatch before publication. Reproduced exactly by converting the build-31 .gitignore to Linux LF: source b49e165ece8fc1b743f2891148f3d24dfdb45d65 versus recorded 7b8003b238a19ac35c4387219076cdd97cf27172. Added an exact-content SHA1 contract to the existing installed-config restoration script. Simulated LF .gitignore/eas.json -> restore -> fresh fingerprint passes and restores both files byte-for-byte. The runtime check is retained; no runtime override or APK rebuild.
