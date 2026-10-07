# Week of 5 October 2026: collector assessment usability

## 6 October local implementation

Completed required observer-review tracking for real gait sessions. Pending records sort first in history and participant dashboards; result/details link directly to a dedicated G.A.I.T. worker screen. The wizard collects assessor metadata once, presents one original-rubric item at a time, splits scoring branches, keeps navigation visible and provides a paper-order overview. Drafts resume at the first unresolved item. Navigation saves pending edits and preserves raw recordings if saving fails. Unobservable items stay missing, and no total is prorated or guessed.

Agreed language policy: patient screens/speech remain English, Malay and Chinese; the entire clinical worker form is consistently English until clinical translations are reviewed. JSON and feature CSV expose observer-review completeness/readiness separately from raw-signal quality. Complete forms are required for measured dashboard trend inclusion; raw capture, signal inspection and exports remain available while labels are pending. Practice and Google provider experiments remain separate.

Inspected the supplied front-camera waist-bag clip: 284 frames, about 9.57 s, 720 x 1280, nominal 29.69 fps. Room visibility is established, but blur, upper-edge obstruction and large view changes limit the clip. A follow-up 12-frame visual comparison estimates upper-edge obstruction around 10-20% of image height in several frames, with a varying boundary; masked tracking is a feasibility proposal, not validated acceptance. No synchronized IMU, calibration or measured trajectory was supplied; distance accuracy was not computed. Front-camera visual-inertial tracking is still a feasibility route, not an implemented or validated distance service. The outward-looking camera cannot supply all full-body G.A.I.T. observations.

Validation: 140 deterministic tests and TypeScript passed; 10 actual Expo web worker/protocol tests and the Android Metro bundle passed. Screenshots were inspected, and long scoring criteria no longer overlap. Browser tests cover navigation saving, first-missing-item resume, branch selection, complete save/reopen, both non-English patient settings and all four clinical protocol previews. No new participant collection, clinical validation, synthesis training or classification experiments. Metadata/UI implementation is complete for this batch; physical sensor/camera and clinician-label validation remain incomplete.

### Simultaneous camera/IMU implementation

Added a separate Android research trial with real front-camera video and accelerometer/gyroscope/magnetometer streams. One tap begins capture, followed by complete spoken placement guidance, five settled seconds, a complete walking cue and fresh-movement start for a 15/30/60-second walking window. Rests are allowed. Automatic ending, partial-stop/background handling, raw-first persistence and matching-ID MP4/JSON exports are included. Footage remains uncropped and muted; microphone permission is blocked. Optional measured distance is a reference, not an estimator. EN/MS/ZH prompts and speech are present.

Native IMU timestamps and monotonic stage events are retained; actual camera start/frame times and calibrated clock offset are unavailable. VIO readiness is false. Distance tracking, calibrated synchronization and physical concurrent throughput remain unvalidated. Camera trials stay outside observer-label requirements and clinical trends. Validation now passes 153 controller/storage/UI tests, TypeScript, 10 actual Expo web workflow checks and Android Metro export. Native-screen tests use injected hardware, not a real-device run. Native configuration declares CAMERA and removes RECORD_AUDIO. No training or clinical validation was performed.

Downloaded APK integrity and compiled manifest are verified: com.gaitsteps.app, version 0.3.1, Android build 7, CAMERA permission present and RECORD_AUDIO absent. Local APK is android/dist/apk/GaitTrace-0.3.1-build7.apk. The first supplied files do not establish successful paired physical capture; see the review below.

Publication: source changes remain local for scope review; generated video, screenshots, bundles and APKs remain ignored. Version 0.3.1 adds expo-camera, superseding the earlier UI-only build-6 compatibility status. EAS assigned build 7 (c1bee024-4f46-40e3-b060-06a3a0e3524e), runtime 33936923bf8f867ab7acf5673f6214eab56383c9; native build completed successfully on 6 October 2026. A new APK is required before camera-runtime OTA updates can apply. No source push or new OTA publication occurred.

### Initial camera-trial JSON mismatch (resolved by corrected export below)

Session 2026-10-06T09-19-25-370Z-410c6bc3 from installed build 7 contains only 0.154 seconds, 5 accelerometer/5 gyroscope/2 magnetometer samples, interrupted stop and camera failure "Unknown error". Its events have camera request, stop and video resolution only: no placement-completion, walking-cue or movement timestamp. No walking IMU segment, rate assessment or gait/distance estimate is justified.

The accompanying MP4 lasts 41.13 seconds: 1234 nominal 30 fps frames, 720 x 1280, no audio stream. Sampled frames show a largely stable room early and changed views in the later approximately 25-41 seconds, with persistent upper obstruction. These are visual observations, not verified walking boundaries. Embedded creation fields around 09:21:49/09:22:18 UTC are not calibrated capture timestamps. The user subsequently provided the corrected JSON below; the earlier failed attempt remains separate evidence, with its native-error cause undiagnosed. Local contact sheet and provenance report remain ignored.

### Corrected export: actual concurrent capture and window selection

User supplied session 2026-10-06T09-20-48-772Z-5084d08e as the intended counterpart. JSON contains 41.288 seconds and a saved matching-ID video reference: 3345 accelerometer, 3332 gyroscope and 1528 magnetometer samples. Its duration is consistent with the 41.13-second video, although precise frame/IMU alignment remains unavailable. Native timestamps increase throughout, with no intersample gaps above 100 ms. Whole-capture observed native rates are 81.05/80.79/37.08 Hz respectively; requested rates were 100/100/50 Hz. This establishes real three-stream continuity for this trial, not validated gait accuracy or universal device throughput.

Placement speech ends at 15.320 seconds, walking speech at 33.245 seconds, movement gate at 33.741 seconds, and stop at 41.288 seconds. The strict movement-gate-to-stop interval is only 7.547 seconds because the app records a user-stopped endpoint, not completion of the selected 15-second window. That interval retains 604/608/279 readings at 80.09/80.50/37.02 Hz; maximum native gaps are 38.00/45.13/50.00 ms. Exported a local unresampled walking-only CSV with unchanged axes and original timestamps, plus relative selected-window time.

The saved descriptive motion summary identifies motion approximately 23-39 seconds, partly during the long walking cue. Exported this separately as exploratory phone motion, not verified steps or an official protocol window; its existence flags an instruction/timing usability concern and does not prove the cause. The first approximately 23 seconds are largely quiet. Retain the full original and measured 3 m reference; neither the path distance nor clinical symmetry/speed is validated. Video creation metadata is not substituted for missing frame-clock calibration. Artifacts and provenance remain ignored/local.

### Image-trackability screen and camera-trial guidance correction

User clarified that reaching the intended distance and uncertainty about automatic stopping caused the early Stop action. This is a trial explanation problem, not evidence of walking inability. Revised local flow gives complete time/route/finish instructions before recording/mounting, explicitly identifies time rather than distance stopping, and asks the person to stand still at the marked finish until the stop message. Final walking instruction is short with Begin walking now last. Stop speech fires at acquisition end without waiting for file saving; intentional cancellation does not become a false speech failure. EN/MS/ZH dynamic time and distance prompts are tested. 156 tests, TypeScript and Android export pass. Native fingerprint remains build-7-compatible; no new APK is required for these JS changes, but no OTA has been published yet.

Image-only feasibility screen: upper 21.6% excluded, resized 360 x 640, sampled video 22-40 seconds at 5 fps. Across 89 adjacent pairs, median corners 199, median tracked count 173, median forward/backward-consistent tracked fraction 92.5%, minimum 65.2%. This supports testing visual tracking in the remaining view; it is not a metric pose, depth, calibration result or distance-accuracy score. Local screening JSON includes exact method/provenance; no ground-truth 3 m value was used to manufacture an estimate. Camera intrinsics, camera/IMU geometry and timing, an estimator and independent route validation remain needed.

### Camera-trial simplification supersedes long-briefing approach

User rejected the instruction-heavy solution. Removed its long preflight speech and default duration choices, keeping one short cue per stage. Trial now auto-finishes after four consecutive quiet seconds following fresh movement, with sensor coverage required and timer reset on renewed motion/stale streams. Default 60-second fallback and optional reference/limit controls remain under Trial settings. Technical result text is collapsed; exports remain direct. Quiet-stop is metadata, not verified distance completion; a long pause can end this research trial. Clinical tests retain existing rest behavior. EN/MS/ZH cues, real-controller native UI flow and completion/cancellation tests pass (157 tests), TypeScript and Android export pass. No source push or OTA publication yet; build-7 compatible. Prior long-briefing notes above are superseded by this implementation.

### Researcher phone calibration - 6 October

Added local 0.3.2 researcher-only native Camera2/SensorManager calibration acquisition: 40-second bench routine, native frame/exposure/skew timestamps, fixed/off requested optics and three raw IMU streams, private ZIP export and explicit incomplete captures. Same-holder optical window and physically verified 20 mm ChArUco squares are required. Calibration is per physical phone/configuration, shared across participants; personal standing baseline is separate.

Reusable Python fitting/load gates and the calibration notebook screen lens geometry, camera/gyro rotation and residual offset, lever arm/acceleration consistency. Seven executed synthetic recovery/admission tests pass; they do not establish real-phone or walking accuracy. Processed geometry imports bind installation/camera/pixel pipeline, reject incomplete/wrong-device reports and retain distanceReady=false. 161 app tests, TypeScript and Android Metro export pass. Camera odometry, independent measured-route validation, full IMU noise and magnetic calibration remain incomplete. No real calibration capture has been processed and the older Expo MP4 pipeline cannot directly reuse these intrinsics.

EAS native build 32cf3ae5-0e74-4e38-a043-61d6e38ace08 submitted, 0.3.2/build 8/runtime 0894d523161346acbefbbe6ac62b46e3a244f31f. APK build finished and downloaded locally; ZIP integrity, compiled package/version and native calibration class verified, CAMERA present and microphone permission absent. Physical capture remains pending; no source push or OTA. This supersedes the earlier acquisition-missing status for calibration while preserving the distance-validation limitation. Wiki, current specification, release history and local publication review updated in the same batch; generated boards/ZIPs/APKs remain local/ignored.

### Calibration ZIP self-copy fix

Diagnosed supplied screenshot: native and Expo ZIP paths resolve to the same file, causing copyAsync rejection and no index/export controls. Fixed URI alias comparison, direct indexing of native durable ZIPs, nonempty validation, and recovery of unindexed captures from native manifests on page load. Recovery preserves interrupted/error status and raw bytes. Four regressions added; TypeScript, 165 app tests, Android Metro export and unchanged build-8 fingerprint pass. A compatible OTA can deliver the repair without reinstalling; source/OTA publication remains pending review. No physical calibration or distance result claimed.

### Calibration repair OTA publication

Published by explicit user approval on 6 October 2026: Android preview OTA 01a11195-6294-7fba-93b2-b6eb1f075a52 (group 00541cb9-c847-468e-9f68-5ab0c2942d5c), runtime 0894d523161346acbefbbe6ac62b46e3a244f31f, compatible with 0.3.2/build 8. Server-side update and active preview-channel mapping verified. Installed device receipt and recovery remain to be checked. Source Git publication remains unapproved/pending; no Git push made. User should open online to download, fully close and reopen, verify update marker 01a11195, then reopen Phone calibration and export the recovered ZIP. No new APK needed; app data must be retained.

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

## Row-timed calibration and distance prototype investigation - 6 October 2026

Implemented per-corner exposure/readout timing, joint gyro-driven image fitting and contiguous translation screening. Mean-row timestamp correction alone still fails the original angular-rate gate (0.08162 rad/s); no gate was relaxed. The second actual ZIP passes new internal rotation/timing checks (held-out coordinate RMS 1.1594 px, p90 1.6068 px, candidate offset -29.73 ms). The confirmed moving-tablet first ZIP fails the same model (RMS 6.9382 px). These are development fits, not independent accuracy validation or a full importable calibration.

Translation screening finds 218 usable second-capture poses, but no sufficiently long continuous segment; largest pose gap 2.136 s. Added local fixed-map visual tracking and metric scale/bias/gravity/lever-arm initialization, plus a route connector using real SI IMU and consistent map poses without entered route length. The frontend loses tracking on the second bench capture; failure is preserved, not replaced by estimated steps or invented movement. Rolling-shutter visual correction, map expansion/continuous inertial fusion, native walking integration and unseen measured-route validation remain incomplete. No working clinical camera distance/stop is claimed.

21 Python numerical/rejection checks pass, including known-scale/clock recovery, pure rotation, constant-speed scale degeneracy, inconsistent motion and frame-gap rejection. Actual code execution and outputs are retained in the existing calibration notebook; raw images/ZIPs/generated reports stay local/ignored. Updated current specification, research README, release history, flow-testing instructions, wiki concept/index/log and local publication scope. No app/native version change, APK requirement, new OTA, Git commit or push in this batch. Previous unrelated working changes remain preserved.

## In-app camera distance research trial - 7 October 2026

Integrated the local prototype into a separate 0.3.3 Android research screen: native Camera2 frames/results and three raw IMU streams, phone-bound research profile import, patient-paced placement/stillness, complete speech cue before arming, motion start, sustained-quiet stop and safety limits. No paid service or entered route length supplies scale. Missing calibration/tracking/clock/scale integrity withholds the estimate while saving a single diagnostic ZIP. Clinical protocol/rest/observer form rules are unchanged. Research camera travel is a tracked interior segment with initialization/boundary loss and possible sway, not a validated full clinical route or 10MWT endpoint.

172 app checks, TypeScript and Android bundle pass. New screen tests use mocked speech/hardware and verify callback-complete gating, duplicate-cue prevention, background cancellation, profile binding and self-copy-safe recovery. Actual application Java/OpenCV JNI code passes five desktop synthetic known-answer checks: metric scale 2.7301 versus known 2.7000, map scale preserved, pure rotation and unobservable scale rejected. The desktop adapter executes no Android capture/permission path. Replaying the second real bench ZIP processes 443 post-five-second frames, obtains one map pose then rejects inconsistent-map-pose. All IMU data is available before frames in that replay; no live-latency or walking accuracy result is claimed.

Exported a separate rotation-only research profile from the second capture; full geometry/independentDistanceValidation/distanceReady stay false. Profile and raw artifacts remain local/ignored. Native build 9 succeeded as an intermediate package; final build 10 adds bundled license/notice assets and release/build/runtime/update provenance in the exported manifest. Both use 0.3.3; only final build is intended for physical testing. New OpenCV/native methods cannot reach build 8 by OTA. Local docs/wiki/notebook/weekly pages and publication scope updated together; no Git push or new OTA authorized/published. Physical marked-route validation remains pending.


## 7 October ? Final native research APK verified

Final 0.3.3/build 10 (EAS e2cfa528-ebff-4062-ada1-c8591516d09c, runtime 037f976718a2d2ef78c79b8705adeb04596f072c) completed and downloaded to ignored android/dist/apk/GaitTrace-0.3.3-build10.apk. Verified compiled package/version, ZIP integrity, tracker class, all four OpenCV ABI libraries and four license assets. APK is 233,322,474 bytes, SHA-256 2cc0ff8d10f96c2644ee483e0865ac209d3b2deb7204b4a28189762c3f5b248c. Final 172 app checks and TypeScript pass, with five actual desktop OpenCV JNI known-answer checks already recorded in the notebook. These are implementation checks, not Android capture or physical distance accuracy. Updated current specification, workflow, index, release history, notebook registry and weekly page together. Research profile/raw artifacts/tools remain local and ignored. No Git push or new OTA. Physical trial instructions: install over existing app, import phone research profile in Research tools ? Camera distance trial, walk a measured short route after the complete cue, stand still until finish and export diagnostic ZIP with measured length/turn notes.


## 7 October ? First uploaded 3 m camera-distance trial audited

Audited user ZIP distance-trial-1791347211905 with intact ZIP and source SHA-256 0636e70d9e720042081a1dac6bae75adf585c99fab21945e5a385d1a83d6b588. Physical build-10 acquisition confirmed: 270 matched camera frames at 12.82 Hz, accelerometer/gyro 4,510 each at 210.40 Hz, magnetometer 1,072 at 50 Hz, finite/monotonic streams, automatic quiet-stop. No imported profile, hence needs-profile and no on-device distance. Actual offline replay with existing matching rotation-only profile produces 20 poses over 1.50 s and rejects inconsistent-map-pose 1.84 s after trigger. All IMU available before frames in replay; live latency untested. User-reported 3 m is not independently verified here and no metric distance/error/speed accepted. Pre-trigger motion and holder obstruction/blur retained as observations, not established first-step time or isolated failure causes. Saved executed audit/replay and source identity in themed notebook. Updated current specification/workflow/index/notebook guide/weekly page in this batch. Next gap is explicit profile readiness and map continuity before requesting a repeat; no app code change, OTA or Git push. Private raw data and generated reports remain local/ignored.

## 7 October - Camera-distance retry

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
EAS build 784326fd-4a29-4477-a61b-58f93000b00f is submitted. Completion and
physical retry remain pending. Clinical boundaries and distanceReady remain
false. No Git push or OTA has been made, pending exact-scope publication review.

## 7 October - Retry browser checks and native-byte compatibility

All 10 Playwright phone-viewport flow checks pass. Added scoped .gitattributes rule preserving exact bytes under android/modules/gait-camera-calibration, avoiding Windows/Linux newline changes to native runtime inputs. All 11 native-module file Git-filter hashes match raw hashes. The final local fingerprint remains 36ef802b5c8463d2c0a172abd85bb56d75f0ea0e, matching submitted build 11. These are repository/runtime checks, not physical distance validation. Scope remains local for required publication review.

## 7 October - Retry APK ready

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

Current source checks remain 173 app, 21 Python, six native JNI and 10 browser flow checks, plus TypeScript and web export. Retained walk replay now tracks 151 poses but rejects physical scale. Updated current wiki/specification/release/weekly pages together. Complete 73-file proposed source scope includes prior unpublished observer-form/camera/calibration support and native-byte Git attributes. Private trials, profile, generated tools/media/reports/APKs remain local and ignored. Source approval still awaits exact-scope review.

## 7 October - Actual build-11 retry

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

## 7 October - Better-placement trial compared

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
bootstrap rather than fitting only the first walk. Next work remains multi-view
initialization, camera-motion/occlusion handling and start-cue timing, followed
by metric consistency. Do not relax the gate just to accept the near-threshold
sample. Executed audit/replay outputs are in the existing notebook. Raw/private
artifacts stay ignored. No app change, new APK, OTA or source publication in this
review, and the existing publication scope has not been approved.


## 7 October - Distance architecture review and revised next step

User requested deeper external comparison after two profile-loaded live failures.
Reviewed primary OpenVINS/mobile, VINS-Mono/Mobile, Aalto Android tester, PIVO,
ADVIO and Kalibr material against current source and prior acquisition/feasibility
notes. OpenVINS mobile default branch is restructure and resolves to the same
previously inspected f0c465695c67c0eac786f4edf83a68109a6a58a9; rear-camera preference
is not a new finding. No clinical accuracy for the exact front-camera waist-bag
setup was established.

The custom engine is visual tracking with late differentiated-position scale
regression, not continuous VIO. Identified 65 ms tracking/capture throttle
(~12.7 Hz), shared callback/storage/estimator handler, midpoint-only live rolling
shutter timing, missing accepted full translation/bias/noise calibration and
partial interior camera-path versus full walking-distance mismatch. Potential
blur/occlusion/scheduling causes remain hypotheses rather than isolated results.

Revised action: pause threshold/map-only APK retries; establish a pinned
VINS-Mono rolling-shutter offline reference and assess OpenVINS native integration
before changing capture/calibration again. Reuse retained development ZIPs for
frontend diagnostics with true clocks; low camera rate/incomplete calibration
limit metric interpretation. Plan independent queues/actual 20-30 Hz estimator
input, complete device calibration using the fixed digital tablet and measured
route validation before any clinical auto-stop. No patient print requirement or
per-participant optical calibration. Updated specification, research README,
wiki concept/index/log in the same local batch. No model/engine execution,
dataset download, new distance result, APK, OTA or source push in this review.


## 7 October - Established VIO reference built and replayed

**Current status:** the offline comparison phase is complete. Do not request a
repeat on the unchanged APK or enable clinical distance stopping. Next work is
capture/calibration modernization and a startup convergence/readiness contract,
then native integration feasibility and independent physical validation.

Built pinned VINS-Mono estimator sources unchanged at
`90dabb5ec79946ae42fd2e1e91d4e69aabe1e25d`, with Ceres 1.14.0 at
`facb199f3eda902360f9e1d5271372b7e54febe1`, in Ubuntu 26.04 WSL2.
The reusable offline wrapper excludes ROS transport/visualization/loop closure,
uses static estimator storage matching upstream, and adds logging/header shims.
Its diagnostic Python LK/forward-backward/calibrated-epipolar frontend is not the
original VINS frontend. Five lens coefficients and native pixel rows are retained.
Hardware frame clocks include exposure/readout midpoint; the measured clock offset
is applied once by VINS. Acceleration is interpolated only at real gyro timestamps
between valid bracketing samples. No camera samples, steps or distance are invented.

Also compiled OpenVINS's ROS-disabled library at
`69488123ed9362dd44b6f28e7f4680abbff1442b`, with a documented build-only patch for
Boost 1.90's header-only system component. This is desktop build feasibility, not
Android/front-camera integration, rolling-shutter acceptance or a phone replay.
Dependency source and generated binaries remain local outside source commits.

The corrected harness passes an analytic non-gait camera/IMU control: 559 initialized
frames, rigid-only position RMSE 0.0003602 m. No similarity/scale alignment was fitted.
This verifies basic harness consistency under known geometry, not physical accuracy.
All 26 Python research checks pass, including five new timestamp/unit/profile/axis/reset
adapter checks. Themed notebook execution counts 36-40 retain inputs, preliminary
and corrected replay evidence, source/binary hashes and explicit assumptions.

| Actual retained capture | Initialized states after app movement trigger | Final state / resets | Diagnostic trajectory |
| --- | ---: | --- | --- |
| `1791347211905` | 154 | Initialized / 0 resets | Provisional IMU-position path 3.122 m, endpoint displacement 2.795 m; user originally reported a 3 m route. Not independent accuracy validation. |
| `1791349028491` | 161 | Initialized / 0 resets | Provisional IMU-position path 3.982 m, displacement 3.666 m; route length not restated, so no route error calculated. |
| `1791349358636` | 99 | Lost / 1 reset | Diverges to 23.13 m/s in an initialized state. No route distance admitted or stitched across reset. |

All inputs include setup and lack accepted full calibration. Replay uses JPEGs,
not live native luma/scheduling. First capture uses the separately retained matching
profile offline; its original device run had no profile. Reference noise parameters
are disclosed EuRoC-example placeholders, and camera/IMU translation begins at zero
with online refinement. No measured route length was used to fit scale.

**Critical new evidence:** "initialized" is not sufficient readiness. Estimated
camera/IMU separation briefly reaches 8.107 m in the first recording and 0.659 m in
the second during startup. After the app movement trigger, those maxima are 0.129 m
and 0.139 m, but that later plausibility does not validate their calibration. All
three runs change the initial rotation by about 26 degrees; stable first/second
runs change the time offset from -29.73 ms to about -3.63/-4.29 ms. These consistent
adjustments flag the imported rotation/timing candidate for investigation, not
proof of a uniquely identified calibration fault. The third run retains an
implausible ~0.35 m lever arm during walking and loses tracking.

No new app code, runtime, APK, OTA or Git publication accompanies this execution.
`distanceReady`, `fullCalibrationReady` and `independentDistanceValidation` remain
false. Continuous fusion is supported as a development direction, but the failure
and unstable startup calibration prevent adoption as a clinical stopping rule.
Do not select the pleasing 3.122 m value as success while ignoring the failed run.
Use the fixed digital-tablet calibration workflow, measured IMU noise, actual
20-30 Hz input where supported, and readiness based on stable geometry/tracking
before another independent route evaluation. A blanket 20-30 Hz target is engineering
guidance, not a proven universal minimum: the first two low-rate replays do initialize.

## Native acquisition preparation - 7 October 2026

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

Available physical capture procedure (before the calibration-method review below): install over the existing app; Research tools > Phone calibration.
Choose Sensor noise, tap Measure sensor noise, leave the phone untouched on a
firm table with the app open until the finish voice, then export its ZIP. Choose
Camera board, keep the digital board fixed and its square size verified, capture
through the usual waist-bag window and export that separate ZIP. Send both for
processing; no patient-specific repeat or new walking-distance claim. Full noise/
geometry and native VIO remain incomplete; a longer stationary noise record may
be needed. Do not enable clinical auto-stopping. Git/OTA publication still awaits
review; dependencies, demo assets, APKs and generated reports remain local.

### 7 October published calibration implementation

The user approved one-time local computer processing. Implemented guided native
Zhang/OpenCV lens calibration, automatic clear/diverse-view selection, held-out
reprojection/subset/radial checks and atomic device/camera/pipeline/optics-bound
lens saving. The digital board needs no ruler or physical print for lens intrinsics.
Optional factory metadata is exported, never automatically certified. Prior
custom geometry fitting remains historical research code.

Implemented the local computer launcher, QR pairing and automatic board display,
voice-completion-gated sensor-alignment capture, 50-second automatic stop and
private-LAN upload/result retrieval. The processor converts actual hardware/SI
measurements to the pinned iKalibr authors' reference executable and standard COLMAP.
All three raw sensors remain available; magnetometer is not an iKalibr input.
Equal provisional IMU weights are disclosed. No custom solver is substituted on
failure. Reference results stay review-required and never grant full calibration,
validated distance or clinical auto-stopping. Patient standing baselines remain
separate. The existing Android distance tracker is not a native VINS/OpenVINS port.

Actual JNI lens control: 24 diverse views, six held-out views, 0.1104 px training
RMS and 0.1593 px held-out p90. Repeated still views, blur and invalid parameters
are rejected. Retained calibration replay accepts 17 views with insufficient
coverage; this is artifact replay, not a new physical capture. 185 app, 40 research
and 10 browser checks pass. Renderer tests verify speech completion, no repeated
movement cue, automatic transfer and cancellation before a late start. These do
not establish physical Camera2/audio behavior or patient/route accuracy.

The free WSL/Linux Docker reference environment is installed locally. Initial
actual integration runs exposed ROS environment-hook and intrinsic-archive-format
issues, both corrected. A synthetic 6DOF image/IMU control exercises the unchanged
reference executable; reference and SfM processing evidence is saved in the themed
notebook. It is neither phone accuracy nor model training. Build 14 exposed
Android checked JSON exceptions missed by the desktop JSON jar; corrected native
declarations pass JNI, and replacement 0.3.6/build 15 completed and is verified.

Complete noise, geometry conventions, residual/repeatability review and independent
marked-route accuracy remain pending. New native features require the replacement
APK. Git publication still requires exact file-scope review. Dependencies, raw
ZIPs, Docker/toolchain artifacts, videos/demo assets and APK remain local/ignored.

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
No source push or OTA publication. Exact pending source scope is listed in the
ignored local publication-review page.

### 7 October reference control and local GPU configuration

The recorded CPU reference control completed with 199 measured SfM keyframes in
582.2 seconds, reusing upstream image preparation from earlier recorded attempts.
Analysis against its known synthetic geometry gives 5.68 mm translation error,
0.0165-degree rotation error, 9.90-microsecond clock offset error and
34.0-microsecond readout error. These are numerical integration checks, not
physical phone or clinical distance validation. Executions 44–50 preserve earlier
failures, the completed reference run, its analysis and build-15 verification.

Verified the RTX 5060 in Windows/WSL. The authors' COLMAP and Ceres libraries lack
CUDA. Installed NVIDIA Container Toolkit 1.20.1 and configured the free WSL
Docker runtime after the active CPU control finished. A separate official CUDA
COLMAP 4.2.1 image is pinned by digest and includes only a Python wrapper addition.
Actual extractor/matcher logs bind GPU device 0; active GPU usage was observed.
The local companion automatically selects this worker, retains diagnostics and
records CPU fallback on a GPU failure. Final published calibration stays CPU;
neither GPU availability nor successful SfM grants metric readiness. The fresh
CUDA SfM/reference control and its analysis are recorded separately in the themed
notebook, without overwriting the CPU control or original uploaded data.

The fresh GPU-assisted reference control completed in 938.9 seconds with all
199 measured SfM images registered. Extraction took 23.9 seconds, matching 19.0,
reconstruction 43.5 and conversion 1.0. Known synthetic geometry checks passed:
6.46 mm translation, 0.033-degree rotation, 0.161 ms clock-offset error and zero
readout error. Different COLMAP versions and cold/reused preparation prevent a
controlled overall speed comparison; no whole-job speedup is claimed. Executions
51–52 retain the actual run, parameter analysis, GPU logs/runtime evidence,
software identities, 40 passing research checks and unchanged build-15 Android
fingerprint. This is not physical phone/clinical distance validation. The verified
calibration APK remains 0.3.6/build 15; the computer-side GPU changes need no newer
APK. Exact source scope remains local for review.

### 7 October front-camera calibration ergonomics correction

The user identified the uncomfortable handling assumption: moving a front-facing
phone while trying to keep its board visible and read its screen. For lens-only
Zhang calibration, either object may move. Changed the default to a securely
supported, bagged phone and a moving/tilting tablet board. This does not apply to
the separate targetless camera/IMU alignment, which moves the phone in a static
textured room. Digital perspective distortion is not a substitute for real poses.
Partial ChArUco views can qualify; temporary board loss retains accepted views.
The existing 20-corner, 24-view, coverage and numerical-fit checks are unchanged.

Updated live speech and visible guidance in EN/MS/ZH; sharing the board remains
available after computer pairing. The local processor now supplies a session-
limited board-only tablet QR/link and a computer panel with actual accepted-view
count/prompt. It streams no camera images, grants no distance readiness and cannot
affect fitting. Feedback requests are throttled, coalesced and cancellation-safe.
The tablet capability cannot access captures/jobs. Progress exists only in memory.

187 app checks, TypeScript and 41 research checks pass. A real local service and
headless browser verify progress/completion rendering and board fit in portrait
and landscape using explicitly simulated progress. Screenshots/proof stay ignored
under `android/dist/native-distance-tools/`. Physical phone handling and accuracy
have not been tested. Runtime remains e1383287be615da4c75a7a9ce08b9260cfd2cfb3;
this follow-up can update build 15 compatibly, but is not in the existing APK and
has not been published. Setup/specification/wiki updated in the same local batch.

Sources: [Zhang](https://www.microsoft.com/en-us/research/publication/a-flexible-new-technique-for-camera-calibration/),
[OpenCV ChArUco partial views](https://docs.opencv.org/4.x/da/d13/tutorial_aruco_calibration.html).

### 7 October computer-only calibration flow and publication preparation

Corrected the extra-device assumption: the default uses the stationary computer
board, while the operator moves the phone in its usual bag and watches a live
framing diagram beside the board. The tablet method is explicitly optional,
selected before capture. All active prompts are EN/MS/ZH; saved profiles expose
Repeat lens check. Temporary target loss preserves views. Camera/IMU alignment
still moves the phone in a stationary textured room. Neither route weakens the
native Zhang/OpenCV fit, coverage or review-required metric flags.

At most one actual phone JPEG per second is transferred over the private LAN to
display-only ChArUco detection, then discarded. The page gets only corner/outline
coordinates, avoiding a duplicate coded target/video image. No preview is stored
on the companion; original native capture data remain on the phone as before.
Requests coalesce, time out and cancel without affecting fitting. Missing/bad/
stale frames display waiting or paused feedback. Added dependency checks to the
local launcher; existing compatible OpenCV is reused. Fixed the result-save race
exposed by tests: job completion follows atomic durable save.

188 app checks, TypeScript, 43 research checks and Android export pass. Actual
headless-browser/HTTP checks use a synthetic JPEG and simulated native counts
to verify real OpenCV detections, drawn framing, count/completion, simultaneous
computer board/panel fit and optional tablet portrait/landscape fit. Whole,
partially clipped and absent boards exercise actual detection; corrupt/oversized
frames yield no invented geometry. These are software checks, not a physical
phone trial. Runtime stays e1383287be615da4c75a7a9ce08b9260cfd2cfb3, compatible with
the verified 0.3.6/build 15. The existing APK lacks this follow-up. Source publication
requires exact scope review under AGENTS.md; push/OTA have not occurred. Setup,
testing guide, release notes, product spec and wiki updated in the same batch.
