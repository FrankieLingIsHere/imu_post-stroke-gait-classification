# Sensor-free flow testing

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
