# Sensor-free flow testing

Completed recording acceptance, native control sequences and saved-result checks:
[reproducible app acceptance](../tools/mobile/APP_ACCEPTANCE.md). The integrated
software scenarios use actual RecordScreen/ClinicalCapture/store handoffs; the
Android scenarios additionally exercise virtual sensors and native file sharing.

For actual APK/Android OS interaction tests without a phone, use the reusable
[workspace emulator/Appium lab](../tools/mobile/README.md). Browser previews and
native contract controls complement that lab; they are separate evidence layers.

## Run the complete local software check — 10 October 2026

From `android/`, run `npm run test:sandbox`. No phone, USB connection or APK
installation is used. This runs the app/component tests, TypeScript, production
Java transport/admission/timer/posture checks, and Playwright against the actual
Expo web UI. The browser suite exercises all four clinical previews, enrollment,
and the complete observer assessment including draft/save/reopen and language policy.
Clocks and hardware boundaries are controlled test inputs, not patient recordings.
Browser previews do not exercise Android Camera2 or establish walking distance.

The runner requires the existing local Python/JDK/org.json tools and Playwright
browser. Override `GAIT_PYTHON`, `JAVA_HOME` and `GAIT_JSON_JAR` if necessary.
Missing native prerequisites fail the run rather than silently skipping checks.
Logs and a machine-readable pass/fail report stay ignored under
`dist/sandbox-checks/`; the browser HTML report is `dist/flow-lab/report/index.html`.
These tests do not access or delete your phone's recordings.

Audible speech, Android camera/sensor scheduling, thermal performance and independently
measured distance still need hardware evidence. A browser sandbox cannot certify
them. The default development check is now phone-free; hardware checks should target
these remaining questions after software regressions pass.

## Current setup reliability checks - 9 October 2026

The actual PhoneSetup screen is rendered with substituted hardware and TTS
boundaries. Tests hold completion callbacks and verify that failed initial or
movement speech cannot advance capture or save a profile. Background/cancel
waits for native stop; late permission/capture completion cannot change the next
attempt. Failed stop disables another capture. Matching profiles can be reused.
The real audio wrapper also verifies cancellation clears its watchdog without
cutting the retry or reporting the cancelled utterance as completed.

The first connected build-25 setup exposed a real Android permission-activity
pause that the screen incorrectly treated as cancellation. Regression checks
now cover permission completion before activity resume, safe waiting without
background capture, cancellation during that wait, and stopping when an actual
capture leaves the foreground. Existing camera grants are read before requesting
permission again. The fresh suite passes 241/241; physical retesting is pending.

Physical retesting verifies active update 03e822a3 and the permission fix. Cold
Android TTS returned an empty voice list before service binding finished; a warm
retry completed the first utterance, then native capture failed during startup.
The prepared JS correction polls only empty voice lists for up to eight seconds,
without delaying an already-ready engine. New checks verify delayed readiness,
cancellation before readiness, bounded failure and a genuinely missing language.
The fresh suite passes 244/244 and TypeScript. Native capture failure diagnostics
are now logged without media or participant identifiers; delivery is pending.

Browser flow checks exercise draft retention, all 31 G.A.I.T. ratings, the English
clinical form under Malay/Chinese patient languages, protocol previews and
profile/tutorial navigation. Controlled preview clocks and injected hardware are
software verification only; they cannot prove audible Android TTS completion,
mounted distance accuracy or phone performance. Local check output is retained
in `dist/settlement-tests.txt` and `dist/settlement-flows.txt`.

## Quick enrollment 0.3.12

The rendered React flow test executes the actual enrollment screen with injected
hardware, holds the speech completion callback, and proves motion starts only
after the utterance completes. Capture -> completed speech -> upload -> review
-> explicit profile selection is exercised; result binding, failed replacement,
cancel/resume, prior-profile retention and EN/MS/ZH copy are checked separately.
Python checks reject unsupported capture/units/motion cues, view disagreement,
unbound neural weights, incorrect geometry and corrupted training bundles.
Actual GeoCalib CUDA inference and a full iKalibr replay use retained physical
measurements with explicitly adapted enrollment metadata. Synthetic GPU MAML
tests verify execution/checkpointing only and cannot enter physical training.
See the executed calibration notebook and [phone handoff](research/DISTANCE_PHONE_CHECKS.md).

## Main camera distance 0.3.12: software checks and physical handoff

Native code 24 adds the Android VINS library and external capture boundaries,
requiring a new signed APK. Main processing is phone-only. Tests cover normal
Go/end flow, timed rests, assessment retention, no-network processing, result
binding, restart recovery, worker edits, deletion and exports. The exact Java input
adapter and C++ frontend/core replay retained physical data on the host; synthetic
controls exercise gyro adaptation and 1 + 10 + 1 timing. These are software checks,
not physical Android performance or clinical validation. See the existing notebook
and [mounted-phone checklist](research/DISTANCE_PHONE_CHECKS.md).


## Distance trial 0.3.11: physical handoff

See [remaining phone checks](research/DISTANCE_PHONE_CHECKS.md). Practice, complete speech, first-motion, finishing-pause exclusion and no-walk are exercised using actual native Java and rendered React with injected hardware. Live helper/ZIP/TypeScript integration uses labelled synthetic noise/blank footage; actual VINS analytic control passes without fitted scale. These controls do not establish mounted-phone performance or clinical accuracy. Native build 23 is required; saved calibration remains reusable.

**Current build status - 8 October 2026**

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
New physical calibration and independent distance validation are still pending.
Source changes and generated artifacts remain local pending publication review.


Local 0.3.7/build-16 calibration repair: regression checks cover lens-only
sampling before conversion/storage, unchanged continuous-capture selection,
duplicate-view reasons, fitting callback before optimization, phone fitting/
saving display, failed-attempt recovery/export and EN/MS/ZH error translations.
Desktop JNI uses actual OpenCV and the native solver. Physical checks still need
the replacement APK: verify the preview updates during repositioning, optimizer
and ZIP pauses show their actual state, final failure names its missing gate,
and Export calibration attempt produces the corresponding ZIP after reopening.
Verify a genuine camera-image interruption yields camera-stalled instead of
claiming that the operator supplied insufficient views. This is not yet a
physical-device pass. Walking/alignment captures must retain their raw pipeline.

Camera research numerical checks are separate from this UI lab. From the
repository root, run:

```powershell
C:/Users/frank/.venv/Scripts/python.exe -m unittest discover -s android/research -p "test_*.py" -v
```

The 35 checks cover synthetic calibration/scale recovery and rejection of clock
gaps, pure rotation, unobservable scale and inconsistent motion. Actual two-ZIP
processing and failed visual tracking are retained in
`notebooks/phone_camera_imu_calibration.ipynb`. These are not physical walking
validation, and do not enable camera distance or automatic clinical endpoints.

The new native **Camera distance trial** has React screen-level checks in
`tests/cameraDistanceTrial.test.cjs` with explicitly mocked hardware/speech.
They verify full-speech gating, duplicate-cue suppression, background cancellation,
profile binding, persistence/recovery and withholding rejected metric output.
These mocks do not establish physical camera or voice performance.

The calibration notebook also executes the actual application Java algorithm
against the matching desktop OpenCV JNI library. Six known-answer checks cover
map scale, pure rotation, metric scale and unobservable distance. A desktop-only
loader adapter loads the real OpenCV DLL; Android permission/capture paths are
not executed. Native source compiles in EAS; installed-phone testing remains
required. Research-only estimates must not become clinical stop criteria.

Run from `android/` after `npm install`:

```powershell
node scripts/start-flow-lab.cjs
```

Open http://localhost:8092 on this computer. The phone-sized interface runs the
actual shared app screens. A permanent FLOW LAB banner identifies the session.
The demonstration participant and practice recording are browser-memory fixtures
with no sensor measurements. They disappear on refresh and cannot enter native
patient storage or be imported as device recordings.

Use **Open demo assessment** to enter the dedicated worker G.A.I.T. wizard,
including assessor details, item cards, draft save/resume and paper-order overview.
Use **Start a walk > Preview hands-free flow**
to exercise each protocol's explanation, preparation and start/finish screens
without passing a sensor check. The preview finish control represents an endpoint;
it is not evidence that the phone detects a course boundary or chair contact.

## Automated checks

```powershell
npx.cmd playwright install chromium
npx.cmd playwright test
npm.cmd test
npm.cmd run ts:check
```

Playwright opens the real Expo web UI at a phone viewport. It checks all 31
observer ratings, save/reopen, profile setup, every clinical tutorial and the
10MWT/TUG/2MWT/6MWT preview flows. Its controlled clock advances the two- and
six-minute preview timers without waiting in real time. Reports, screenshots and
failure traces are local under `dist/flow-lab/` and ignored by Git.

The existing React Native renderer tests inject sensor events and speech callbacks
to verify first-step gating, stillness, interruptions, start/finish clocks and
persistence failures. These are deterministic software tests, not hardware trials.

This browser harness is not an Android emulator. It covers shared UI/logic but
cannot verify native permissions, installed speech engines, real audio completion,
camera tracking or physical IMU accuracy. Those need a final real-device check.
No Android emulator/AVD was found in the inspected local setup.

## Observer G.A.I.T. version

The digital rubric uses the user's supplied Appendix A PDF, 31 items and a maximum
of **62**, identified by a source SHA-256 in `src/gaitRubric.ts`. The original paper's
abstract states 64; do not mix the abstract's maximum with this supplied form.
All option branches, including options sharing a numeric score, retain unique IDs.
Directions/positions and item notes are retained separately. Unobserved items are
missing, never zero. No full total is shown until all ratings, required directional
details, assessor, valid date, limb and observation source are complete.

Scores are entered by a trained observer, never computed from phone signals.
Language policy agreed on 6 October: patient screens remain English/Malay/Chinese;
the entire worker G.A.I.T. screen, controls and original criteria use English.
Save using **Save draft**, **Save & close**, or **Finish assessment**. The form
is linked to the recording/participant, reopened from recording details, included
in JSON, and exported as per-item option/score/notes/direction columns in feature CSV.

Every real, non-practice gait recording requires this observer review. History and
participant dashboards sort pending records first on entry. Practice and the
separate Google provider experiment are excluded from labelled analysis. JSON and
feature CSV carry `gaitReview` / `gait_review_status` and
`gait_labelled_analysis_ready`; these describe observer-label completeness, not
sensor quality, clinical validity or model-training admission. Raw exports and
signal quality review stay available while an assessment is pending. Dashboard
measured-speed trends require complete G.A.I.T. labels as well as their existing
measured-course/protocol/aid rules. Never fill an unobservable item with zero.
The dashboard displays complete observer totals without interpreting improvement.

Reference: [Daly et al. updated form and administration discussion](https://www.mdpi.com/2076-3425/12/8/1104).

## Paired front-camera/IMU hardware check (0.3.1)

Install the camera-enabled APK; installed build 6 lacks the native camera module.
Open Home > Import, research tools and app information > Camera + IMU trial.
Allow the camera in-app, select 15/30/60 seconds, and optionally enter a separately
measured short route length. Clear a safe route, tap Start paired capture, mount
the phone horizontally at the lower back with the screen outward, and stand still.
Wait for the complete walking instruction, then walk comfortably. Fresh movement
starts the walking timer; capture ends automatically. Do not use this as a clinical
distance endpoint. Permission denial, background interruption and explicit Stop
should produce clear status and preserve partial sensor data.

After saving, export **Export paired camera video** and **Export paired IMU and
timing JSON**. Keep the matching session ID in both files and send both for review.
Check that the MP4 opens, shows the actual mounted view, and has no microphone
audio; check all three raw streams for real readings, observed rates and gaps.
Repeat once after leaving/reopening the saved recording to verify persistence.
The upper obstruction may remain; footage is deliberately uncropped for evaluation.

Automated native-screen tests exercise the real controller with injected hardware;
they cannot validate camera throughput, mount quality or simultaneous sensor rates.
Event timestamps provide coarse stage alignment only: actual camera start/frame
times and calibrated camera/IMU offset are unavailable, so vioReady remains false.
Precise synchronization/calibration must be added and validated before VIO distance
tracking. This engineering trial is separate from observer-labelled clinical tests.

## Historical researcher phone calibration (0.3.2; superseded below)

This is per physical phone/camera configuration, shared by all participants. Print
the board generated by `notebooks/phone_camera_imu_calibration.ipynb`, at actual
size, and check a square measures 20 mm. Use the same optical holder window. Open
Research tools > Phone calibration and tap Capture calibration. Follow the short
still/move cues while holding the phone so the board remains visible. Keep the board/tablet fixed on a stable support. Move/tilt only the recording phone in
several directions. Capture ends automatically after 40 seconds; export its ZIP.

Confirm live frame previews, all three real sensor streams and native timestamps
in the ZIP. Check cancellation/backgrounding/error is never status completed.
Process the ZIP in the notebook; import its accepted calibration-report.json on
the same phone. Rejected/wrong-phone reports must fail import. Even an accepted
geometry report says walking-distance validation remains needed. Reinstallation,
changed phone/camera/pixel pipeline or changed holder optics requires rechecking.
The native calibration pipeline differs from existing Expo MP4; do not apply its
intrinsics directly to those videos. Patient standing baseline remains separate.

Seven Python tests exercise board detection, rotation/time/bias recovery,
acceleration/lever-arm recovery and unobservable/unsafe/incomplete rejection.
Three app tests check binding and prevent false distance readiness. These are
numerical/contract tests, not physical camera throughput or route accuracy.

## Camera-distance retry checks (0.3.4)

The camera-distance screen test now verifies that missing profiles present Import
and no Start button, speech or native capture. Native API rejects a missing
profile too. Eight dedicated screen/storage checks and all 173 app checks pass.
Six actual Java/OpenCV JNI numerical checks include map renewal in the original
coordinate frame/scale. Retained 3 m artifact replay tracks 151 poses but rejects
physical scale. This is development replay, not a validated metre result.


## Native capture-v2 checks

`CaptureQueueBudgetCheck.java` executes the actual queue class on the JVM, including
bounded capacity, eight-thread concurrent drain, observed hardware-clock rates,
processing delays and nonmonotonic clock rejection. It is not Camera2 throughput
validation. The native noise UI renderer test verifies completed speech before
start, no camera permission for noise, 300-second native elapsed-time display and
separate ZIP export. Processing tests cover white-noise recovery, movement/gap
rejection and the complete-state readiness contract. All 177 app/35 research and
10 browser checks pass; real phone noise/camera capture still must be checked.

## Guided published calibration (0.3.6)

Renderer tests exercise the actual screen with injected hardware: completed
instruction before lens capture, real progress-count display, saved lens before
alignment, single movement cue, native movement timer only after its speech
completes, finished capture before upload and review-required results. Canceling
an unfinished start instruction prevents any later capture. Static catalog checks
cover new EN/MS/ZH prompts. The local service tests use a real HTTP server for
token authentication and incomplete-upload rejection, and injected engines for
persistence/deduplication/failure behavior. Those service tests do not verify
reference calibration mathematics. Native JNI tests exercise real OpenCV and the
app's solver with known projections, duplicate/blur/invalid geometry and retained
phone images. See notebook outputs for actual upstream processing evidence.

Physical checks after installing build 15 and receiving the published compatible
guidance update: scan a computer pairing code on private Wi-Fi, verify the board
and live framing diagram on the computer, move the bagged phone while watching
the computer, verify accepted-view feedback and translated spoken instructions,
confirm quality-gated lens save, follow alignment and automatic stop/upload,
then retrieve the result. Check cancellation/backgrounding/reconnection and
profile reuse. Compare actual image/IMU rates, clocks and optical metadata before
admitting any profile. No phone or clinical distance pass is claimed here.

The lens screen maps every current native hint to computer-only guidance or the
explicit optional tablet mode. A lost
board view preserves the accumulated views; partial views can qualify under the
unchanged native corner/coverage gates. Renderer checks verify the new preparation
speech completes before capture. Feedback transport coalesces updates, allows one
request in flight and cancels late sends; it cannot block the native lens fit.
Real HTTP checks verify the tablet capability exposes only the board, cannot read
jobs, and strips unrelated progress fields. Actual phone JPEGs travel over the
private LAN to display-only OpenCV detection. Neither companion disk nor page receives
the JPEG; the page draws corner/outline coordinates without a duplicate target.
Whole/partial/absent synthetic boards exercise the detector; bad frames never
invent coordinates or change native acceptance. 188 app/43 research checks pass.
Actual headless-browser companion checks use synthetic frames and simulated
native counts to verify drawn framing, count/completion and computer board/panel
fit, plus optional tablet fit in portrait/landscape. Android export passes. Screenshots
and evidence remain local under `dist/native-distance-tools/`. These checks are
software UX/transport evidence, not a physical phone trial.


## Staged calibration regression checks - 7 October

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
Build submission/result is recorded locally after final checks. Source publication
awaits user review. Reference calibration and independent distance validation
remain separate, incomplete requirements.

Physical retry: restart the computer launcher, install build 19 once its APK is
verified, reconnect the computer, and follow one round at a time. Confirm each
completed check remains checked, voice instructions finish, and no stop occurs
at 47/48 views. Verify fitting/saving and export if rejected. No need to repeat
old build-16 attempts. Calibration remains researcher preparation for the phone.


Local Android compilation verification (7 October): the frozen calibration-module
Kotlin and Java sources compile successfully against Android SDK 35 and JDK 17.
Gradle completed 39 actionable tasks in 6m18s. A Windows Kotlin daemon cross-drive
path error recovered through its fallback compiler; the final process exited 0
with BUILD SUCCESSFUL. This is actual Android compilation, distinct from the
desktop JNI fixtures. The signed cloud build 19 has since finished and passed APK verification
(8 October); physical phone calibration remains unverified.


## Computer reference-processing repair - 8 October 2026 (local)

Working files now use a fresh Linux Docker volume rather than a Windows bind
mount. The original ZIP is hash-checked before and after processing. All solver
outputs, including failures, are copied back before the temporary volume is
removed; if output transfer fails, its volume identity is retained for recovery.
The published solver, raw measurements and quality checks are unchanged.
The actual failed capture now completes in 9m33s, with GPU COLMAP registering
169/195 measured images. 47 research checks pass. This is a computer-only
change; installed app 0.3.9/build 19 does not need another APK.

For the existing failed attempt: close the old computer processor window, reopen
`android/Start phone calibration.cmd`, reconnect the new code on the phone, and
tap **Resume calibration processing**. No new capture or ZIP export is needed.
Expect **Reference parameters saved. Research review is still needed.**
The result is saved for review, not validated metric tracking. Complete noise,
repeatability and measured walking-distance checks are still pending. See the
executed phone calibration notebook for actual timings/parameters and provenance.


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


### 8 October - distance validation and storage acceptance

Local 0.3.10 adds the native reference capture, requiring a new APK. Component
flows verify prep/cue/finish audio completion before capture/start/upload, no
duplicate cue on repeated native progress, cancellation before capture and saved
reference setup without a legacy import. Storage tests verify selected/all modern
and legacy removal, orphan files/ZIPs/video/export copies, preserved unrelated
files and explicit failure. Route-length reopening and result-binding checks pass.
Research checks verify camera-to-IMU geometry, timing, nonidentity rejection,
partial/reset/gap suppression and separate idempotent distance-job dispatch.

Phone checklist after installing the new APK:

1. Existing profiles, recordings and saved lens/reference must survive update.
2. Research menu contains just calibration and distance validation.
3. Restart computer helper, reconnect code, select a measured straight 3 m route.
4. Start, place phone, wait for complete Begin walking cue; walk to mark and stand
   still until Finished. Finish voice must complete before transfer begins.
5. Confirm automatic computer transfer and result return. Missing/partial tracking
   must display unavailable, not zero/full distance. Repeat three times; also 2/5 m.
6. Export raw trial ZIP and result JSON. If disconnected after capture, retry or
   resume must reuse the saved capture/route without recapturing.
7. With disposable recordings, cancel deletion first (nothing removed), then
   confirm selected deletion (other recordings intact). Confirm all-data cleanup
   returns zero owned recording-file bytes and empty history/dashboard, while
   profiles/calibration remain. Reopen app to check no legacy records reappear.
8. Repeat controls in English, Malay and Chinese. Check small screen and large
   font. External Downloads/computer copies remain outside app deletion.

No researcher should report these component/synthetic checks as physical-device
validation or accepted patient distance accuracy.


## IMU startup transport regression - 10 October 2026

Run `python -m unittest android/research/test_vio_bootstrap.py -v` from repository
root using the local Python interpreter. Requires JDK 17 and org.json jar (local
ignored tool paths or JAVA_HOME/GAIT_JSON_JAR). Executes production Java buffering,
interpolation, timing coverage and state-file writing with an injected solver
boundary: 49 assertions. Re-runs the existing 617 admission/boundary assertions.
Also executes 26 guided capture-clock assertions: delayed speech preserves the
full movement interval, failed estimator transitions do not start the timer, and
duplicate/early/expired starts are rejected. The production native wiring is
compiled into build 27; actual Android scheduling still needs a physical scan.
Proves genuine early samples are replayed, initial uncovered images are withheld
within bounds, saved offsets apply, and later gaps/sparse streams still fail.
It does not simulate Android hardware or validate physical distance. Native
Kotlin/Java compilation, DEX class presence, unchanged shared-library byte checks,
fresh fingerprint, APK signature and update identity are checked separately.
