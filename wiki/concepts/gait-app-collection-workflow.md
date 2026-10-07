---
type: concept
---

# Gait app collection workflow

This page tracks what the local GaitTrace phone app can capture and what still requires observer, course or clinical validation. It is an implementation record, not evidence that the app is a validated rehabilitation instrument.

## Current camera processing investigation

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
supports partial target visibility. This ergonomic follow-up remains local and
has not reached the installed build-15 APK; its Android runtime is unchanged.
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
No source push or OTA publication. Exact pending file scope is listed in the
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
