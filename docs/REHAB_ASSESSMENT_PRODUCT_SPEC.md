# Rehabilitation assessment product specification

Updated 2026-10-07. This specification expands the client brief from a research walk recorder into a rehabilitation assessment workflow. Native camera-distance research remains separate from clinical assessment.

## Camera distance research trial - 7 October 2026

### Published calibration integration - 7 October 2026

The user approved one-time local computer processing. The local 0.3.6 candidate
now provides guided on-phone Zhang/OpenCV lens calibration and an automatic
private-LAN bridge to the iKalibr authors' reference camera/IMU executable. Old
custom OpenCV/scipy geometry fits remain historical research tools. They are not
substituted when the reference engine fails.

The new flow is **open the computer launcher ? scan its code ? follow the lens
prompts ? follow the sensor-alignment prompts ? receive the result**. The
computer displays the stationary board and live framing feedback computed from
actual phone JPEGs. The bagged phone moves while the operator watches the
computer, following EN/MS/ZH speech; no tablet is required. The supported-phone/
moving-tablet mode is explicitly optional. Partial board views can qualify;
brief target loss keeps accepted views. The separate camera/IMU alignment moves
the phone in a stationary room. The diagram receives only detected coordinates,
preventing a duplicate coded target. Preview JPEGs are discarded after local
processing. Display feedback cannot admit calibration or relax numerical checks.
The ergonomic update is local, compatible with the
verified build-15 runtime, and has not been delivered to the installed APK. No
printing, ruler, manual ZIP transfer or patient-specific device calibration is
required. Digital board aspect ratio and flatness still matter. Native selection
requires 24 diverse clear views and checks held-out reprojection, subset stability,
finite/physically bounded parameters and radial mapping. These selection limits
are provisional engineering gates, not published clinical accuracy thresholds.
A failed/interrupted attempt preserves the previous valid lens profile.

[Zhang's published planar method](https://www.microsoft.com/en-us/research/publication/a-flexible-new-technique-for-camera-calibration/)
is implemented through OpenCV 4.12 `calibrateCamera`. Uniform board scale cancels
for lens intrinsics, so this phase needs no measured square size. This is not a
metric camera/IMU geometry or distance calibration. Actual native Java/OpenCV
known-answer checks recover the lens with 0.1593 px held-out p90 residual and
reject duplicate views, blur and nonfinite geometry. Replaying the retained
calibration-1791298033545 yields 17 accepted views and insufficient coverage,
without a ready profile. That replay is development evidence, not a new capture.

[iKalibr](https://github.com/Unsigned-Long/iKalibr), published in IEEE T-RO 2025,
is the selected targetless spatiotemporal reference. Unlike the previously
considered [Kalibr target workflow](https://github.com/ethz-asl/kalibr/wiki/camera-imu-calibration),
it avoids a measured alignment target, but still needs lens parameters, textured
visual surroundings and varied 3D motion. The guided native capture waits for
completed speech before the 50-second movement interval, then automatically stops,
retains all three IMU streams and transfers the ZIP. Its bag-window declaration
and device/camera/pipeline binding must match the saved lens profile.

The free local WSL/Linux Docker environment uses the authors' pinned image
`sha256:2de8ac994a86951b6255e4b8485eae9982ea3ed03bac33dd9d0ee254e383587c`.
The bridge assembles measured Camera2 timing and SI IMU data into a ROS bag,
uses the rolling-shutter midpoint model and automates standard COLMAP reconstruction.
CUDA feature extraction/matching are selected when the local NVIDIA Docker
runtime and pinned CUDA worker are available; CPU remains the disclosed fallback.
The authors' installed Ceres library lacks CUDA, so final calibration stays on CPU.
The standard sequential matcher and up to 200 measured SfM keyframes bound work;
all original images and continuous IMU remain retained. Raw measurements,
original upstream outputs and executable SHA remain available. The binary image
has no checked-out source commit, so it is not assigned the inspected repository's
commit identity. Equal provisional IMU weights are disclosed, not claimed as a
measured long-term noise model. The magnetometer is retained but not used by
this reference solver. Processing jobs and failed captures remain local.

The executed CPU reference control completed in 582.2 seconds with 199 measured
SfM keyframes, reusing upstream image preparation from the recorded earlier attempts.
Against the synthetic known geometry, translation error was
5.68 mm, rotation error 0.0165 degrees, clock offset error 9.90 microseconds and
readout error 34.0 microseconds. This establishes numerical integration on a
synthetic control, not phone accuracy or clinical distance validation. Failed
earlier runs and the completed result remain in the calibration notebook.

A separate fresh CUDA SfM/reference control also completed and passed its known
geometry/timing checks: 199 registered images, 6.46 mm translation error,
0.033-degree rotation error and 0.161 ms clock error. Extraction/matching took
24/19 seconds, but the whole cold-preparation/CPU-solver run took 938.9 seconds.
No overall speedup is claimed across different COLMAP versions/preparation states.
The companion selects the installed GPU worker automatically; 40 research checks
pass, including preserved uploads on fallback and cleanup of only the timed-out
worker. The Android build-15 runtime fingerprint remains unchanged.

Optional Android factory intrinsics/distortion, pose and reference fields are
now exported when available. None is automatically treated as a verified profile.
Camera-relative zero translation does not prove camera/IMU separation. Restricted
waist gait does not establish full calibration observability. Calibration belongs
to the research team and is reused only for matching camera/settings/optics,
separately from each patient's standing reference.

A received reference result is explicitly **review-required**. It does not set
camera/IMU candidate readiness, full calibration, validated distance or clinical
auto-stopping. Parameter conventions/bounds, residuals/repeatability, complete
noise and independent marked-route accuracy still need review. The existing
Android tracker has not been replaced by native VINS/OpenVINS. See
[local setup and method provenance](../android/research/CALIBRATION_SETUP.md).


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
No source push or OTA publication. Proposed scope is 28 modified and 81 new
files, listed in the ignored local publication-review page.

### Executed established-VIO feasibility - 7 October 2026

**Historical VIO/acquisition evidence:** offline comparison is complete. Local 0.3.5 acquisition and
noise-capture preparation plus a future-estimator readiness contract are now
implemented; see the latest acquisition section below. Build 13 and the downloaded APK are verified
after the corrected build-12 Kotlin map-type failure. Physical capture performance,
full calibration and native VIO integration remain pending. Do not repeat the
walking trial on build 11 or enable clinical distance stopping.

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

### Architecture review and revised next action - 7 October 2026

**Historical source-review decision (executed phase now recorded above):** pause
further threshold/map-only APK iterations. Benchmark an
established, tightly coupled visual-inertial estimator before another patient
walking request. Keep build 11 as an experimental collector. No replacement
engine was built, integrated or evaluated in this review, and no metric accuracy
is claimed. This decision supersedes the earlier next-action wording about
patching the custom bootstrap first; historical physical results remain intact.

OpenVINS and its Android port were already reviewed on 2 October. Reinspection
of the current default branch (`restructure`) resolves to the same pinned commit
`f0c465695c67c0eac786f4edf83a68109a6a58a9`, so the rear-camera selection is not a
new discovery. The new findings concern estimator architecture, capture rate,
rolling shutter, calibration completeness and whole-route measurement.

| Primary source | Verified capability | Relevance and unresolved constraint |
| --- | --- | --- |
| [OpenVINS Android](https://github.com/goldbattle/open_vins_mobile) / [camera source](https://github.com/goldbattle/open_vins_mobile/blob/f0c465695c67c0eac786f4edf83a68109a6a58a9/app/src/main/java/com/openvins/android/Camera2ResView.kt) | Android camera/JNI integration for OpenVINS; inspected source prefers the rear camera. | Native integration candidate, not a front-camera drop-in. Front-camera configuration/calibration and rolling-shutter suitability must be demonstrated. This review does not establish rolling-shutter support in OpenVINS. |
| [VINS-Mono](https://github.com/HKUST-Aerial-Robotics/VINS-Mono) | Sliding-window camera/IMU optimization, IMU preintegration with bias correction, initialization/recovery and explicit rolling-shutter configuration. | Preferred offline reference for the present rolling-shutter camera. Linux/ROS build and old dependencies require a feasibility check; Android integration is separate work. Its device guidance requests images above 20 Hz and IMU above 100 Hz, not a universal threshold for every estimator. |
| [VINS-Mobile](https://github.com/HKUST-Aerial-Robotics/VINS-Mobile) | Real-time single-phone visual-inertial localization demonstration with initialization and recovery. | Evidence that phone odometry is achievable; the published implementation is iOS, with historical iPhone testing. It does not validate a front-facing waist-bag mount or post-stroke clinical endpoints. |
| [Aalto Android VIO tester](https://github.com/AaltoML/android-viotester) | Android capture/calibration/comparison workflow, actual frame timestamps, recommended target 30 fps; calibration pattern can be displayed on a screen. | Useful capture/benchmark reference, not a ready clinical distance provider. Its calibration mode estimates camera parameters, not automatically the complete camera/IMU geometry. |
| [PIVO paper](https://arxiv.org/abs/1708.00894) | Smartphone camera/IMU fusion designed for robustness to visual occlusion. | Supports investigating inertial fusion during partial occlusion; does not establish indefinite metric accuracy through a blocked lens or provide a verified drop-in Android service here. |

These references demonstrate navigation capabilities, not independently verified
accuracy on this project's exact phone, pouch, short course or stroke population.
No raw benchmark dataset was downloaded or admitted in this source audit.
OpenVINS/VINS repositories carry GPL-3.0 licensing: no API subscription is needed,
but distribution requires a separate license/dependency review.

#### Overlooked engineering requirements

1. **Continuous fusion:** `ResearchDistanceTracker.java` currently derives camera
poses first and estimates metric scale afterward using differentiated visual
positions. Gyroscope consistency is checked later. This is not a full VIO state
estimator with inertial prediction, continuous bias estimation and uncertainty.
Differentiation amplifies visual noise; established fusion avoids relying solely
on that late regression for the motion state.
2. **Camera rate and scheduling:** the collector's 65 ms arrival-time throttle
limits both saved frames and tracking input; actual trials deliver 12.6-12.8 Hz.
Camera metadata indicates a higher native frame rate. Camera callbacks, IMU
callbacks, JPEG writing and tracking share a handler thread. Separate capture,
estimation and storage queues; instrument latency/drops and test actual 20-30 Hz
estimator input without inventing frames. This is a design gap, not proof that
thread contention caused the observed failures. Preserve high-rate native IMU
and hardware clocks; normalized 50 Hz gait exports remain a separate product.
3. **Rolling shutter and exposure:** actual captures have roughly 30-33 ms
exposure and 32 ms sensor readout. The live tracker uses a representative midpoint
time, not per-row correction. The offline row-timed calibration does not correct
live frames automatically. Blur and row distortion are plausible contributors,
not isolated causes. Improve illumination/exposure within device limits and use
an estimator that explicitly handles the relevant timing model.
4. **Full calibration:** the current profile is lens plus rotation/timing only.
Accepted camera/IMU translation, acceleration bias and IMU noise/random-walk
characterization remain missing. [OpenVINS calibration](https://docs.openvins.com/gs-calibration.html)
and [Kalibr requirements](https://github.com/ethz-asl/kalibr/wiki/camera-imu-calibration)
make these separate tasks. Validate the same lens/window, resolution and capture
settings. A small lens reprojection error alone does not validate metric scale.
5. **Initialization and loss:** two-view bootstrap and permanent failure after
one rejected pose are fragile. Multi-view initialization, robust outlier handling,
state uncertainty and explicit recovery are needed. Increasing the 1.5 px gate
until a trial passes would conceal the issue. Occluded pouch regions should be
masked for tracking only, preserving original frames and image coordinates.
6. **Distance definition:** the smoothed interior camera trajectory omits startup
and derivative edges; body sway can inflate accumulated camera travel. Complete
camera localization, walking progression and a clinical timed-zone boundary are
three different validations. Quiet auto-stop can also occur during a mid-route
rest. Do not equate any accepted partial trajectory with a 10MWT endpoint.

#### Concrete sequence and acceptance evidence

- First perform a local build/configuration feasibility check for a pinned
VINS-Mono reference and an OpenVINS Android integration candidate. Compare
rolling-shutter handling explicitly before choosing the app backend. Use the
existing themed notebook for executed benchmarks and reusable adapters in the
research module directory. Do not duplicate old experiments or call a proposed
benchmark an executed result.
- Convert retained ZIP streams using true frame/IMU timestamps, SI units and
explicit camera axes. These development recordings can expose frontend failures;
their low frame rate and incomplete calibration limit metric interpretation.
Never set scale using the user's reported route length and then claim to validate
that length. JPEG replay differs from live native luma and callback scheduling.
- Only after backend/capture requirements are known, update the research collector
for independent queues, actual frame-rate/latency diagnostics and a complete
phone-level calibration routine using the existing stationary digital tablet
board. Characterize IMU noise separately. No printing is required; patients do
not repeat the researcher calibration. Each run still needs automatic readiness.
- Then validate repeated independently measured short routes, longer routes,
turns and permitted pauses. Record full-route coverage, metric scale uncertainty,
distance bias/error, dropout, latency and false completion. Agree the clinical
endpoint/error requirement with the supervisor before enabling automatic clinical
stopping. Reserve new routes for evaluation rather than tuning on every attempt.
- If the present front-camera/window configuration cannot meet those requirements,
report that failure explicitly. A free external API cannot recover absent visual
information or substitute for validated short-course measurement. Keep the
collector presentable independently of the unvalidated distance research.

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
bootstrap rather than fitting only the first walk. The revised next action is the established-VIO feasibility benchmark above,
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

Local 0.3.3 integrates the Java/OpenCV prototype into a separate native Android
research screen. A phone-bound rotation/timing profile can be imported without
pretending that full acceleration calibration passed. Without it, acquisition
still saves diagnostic raw data but cannot calculate distance. Fresh stillness
and three receiving sensors trigger a complete spoken start cue; the native
walking state is armed only after speech completes. Motion starts tracking,
sustained quiet stops after a minimum capture interval, and placement/walking
safety limits preserve partial data. Cancellation/backgrounding reject metric
output. This engineering stopping rule does not change clinical rest handling.

The ZIP contains native camera images, actual frame/exposure/readout times,
accelerometer/gyro/magnetometer samples, tracking diagnostics, any supplied
profile and app/build/runtime/update identifiers. Missing metadata, map loss,
clock gaps, inconsistent visual/gyro motion, unobservable scale or physical-fit
failures explicitly withhold the estimate. No entered route length fits scale.
The experimental horizontal camera path is a tracked, smoothed interior segment;
initialization/boundary portions and residual sway make it unsuitable as a
whole-route clinical speed/distance result or automatic 10MWT stopping boundary.

172 app checks, TypeScript and Android bundle pass. Five real desktop OpenCV JNI
checks execute the application Java math/tracking implementation under known
synthetic conditions (scale 2.7301 versus 2.7000). These do not execute Android
capture or establish patient accuracy. The second native bench ZIP replay loses
its fixed map after one pose; the failure is retained. Physical marked-route
testing is now possible in the app and remains required. Build-8 cannot acquire
OpenCV/new native functions by OTA; 0.3.3 requires a replacement APK. Library
licenses are bundled; no remote subscription/service is used. Final 0.3.3/build
10 completed successfully, and the downloaded APK package/version, ZIP, tracker
class, four OpenCV ABIs and license assets were verified. Runtime:
037f976718a2d2ef78c79b8705adeb04596f072c. Physical accuracy remains untested.

## Researcher phone calibration - 6 October 2026

Current processing state: the new per-corner exposure/readout model passes
internal rotation/timing checks on the second native capture (held-out RMS
1.1594 px, p90 1.6068 px, candidate offset -29.73 ms), and rejects the confirmed
moving-tablet first capture (RMS 6.9382 px). This does not establish full geometry
or distance. Translation/accelerometer screening remains unavailable because
usable board poses have no sufficiently long uninterrupted segment; maximum
accepted-pose gap is 2.136 s. No complete profile can be imported yet.

Local reusable Python now includes a fixed-map visual tracking prototype and
a camera/IMU metric-scale initializer/route connector. Numerical tests cover
known-scale recovery, pure-rotation rejection, unobservable scale, tracking gaps
and inconsistent motion. The visual frontend loses tracking on the second bench
capture. This is not a successful real walking estimator: rolling-shutter-aware
visual tracking, map expansion/continuous fusion, native walking integration
and independent measured-route validation remain necessary for clinical use. Existing app
distance and stopping behavior are unchanged; camera distanceReady stays false.

Local 0.3.2 adds a researcher-only 40-second front-camera board capture with native
Camera2 frame/exposure/skew clocks and direct three-axis IMU timestamps. Calibration
is per physical phone/camera/optical configuration, shared across participants;
the individual standing midline baseline remains separate. Same-holder optical
window is used during bench capture. A fixed tablet display or printed ChArUco board provides known metric
geometry; its 20 mm square scale must be verified physically.

Export ZIP, process in notebooks/phone_camera_imu_calibration.ipynb, and import an
accepted report on the originating installation. Geometry candidates are withheld
on incomplete captures, insufficient excitation, gaps, changing optics or failed
internal fitting checks. Import enforces phone/camera/pixel-pipeline binding and
never turns geometry into distanceReady. Existing Expo MP4 cannot directly reuse
the native calibration intrinsics. Production camera odometry, independent measured-route
validation and clinical automatic distance endpoints are still unimplemented.
No external paid service, model training or patient-specific board routine is added.

## Current worker-assessment requirement and language policy

Every real non-practice gait recording requires the supplied observer G.A.I.T. assessment for labelled analysis. Raw recording saves first and remains reviewable/exportable; pending labels do not destroy data or become normal zeroes. Practice and the separate Google distance-provider engineering trial are not labelled clinical sessions. Missing legacy/imported forms become pending without inventing scores. Complete means all 31 ratings, required directions and assessor/date/limb/observation source are present. This is a completeness check, not clinical or sensor validation.

The dedicated worker screen shows assessor details once, then one item per card with gait-phase context and the exact original scoring explanations. Separate branch selection reduces long multi-branch lists. Previous/Next and draft controls remain outside the content scroll. A paper-order overview allows rapid review and editing. Drafts reopen at the first unresolved item and save before leaving through navigation; failures keep the screen open. Explicit draft saves are still needed before forcibly terminating the app. Unobservable items remain unresolved with notes. A clinician must determine whether the available observation covers the full instrument; the app must never coerce a guessed rating.

User-agreed policy on 6 October: patient-facing UI and speech remain English/Malay/Chinese. The entire G.A.I.T. worker screen and its navigation use English consistently, preserving the original instrument until clinical translations have been reviewed. Clinical source criteria are not rewritten into simplified diagnostic rules. Research capture/setup language is unchanged.

History and each participant's dashboard sort unfinished assessments first whenever loaded. Result/detail screens expose worker assessment directly, separately from test outcomes/notes. JSON and feature CSV export an explicit review status and observer-label readiness flag. These flags are only one requirement for future labelled analysis; they do not replace signal quality, consent, synchronized reference evidence or independent validation. Measured progress curves exclude unfinished G.A.I.T. sessions. Raw signal descriptors remain accessible for quality checks.

### Simultaneous front-camera and IMU trial, 6 October

Native Android Research tools > Camera + IMU trial captures the mounted outward front-camera view with real accelerometer, gyroscope and magnetometer streams. It requests camera permission inside the app, records muted 720p-requested video, and blocks microphone permission. The original image remains uncropped so the upper obstruction can be evaluated; no tracking mask is applied. Files remain in private on-device storage until exported.

The current local camera-trial flow removes the long pre-capture briefing. Default view shows a short marked-route prompt and Start; limit/reference controls are under Trial settings. One tap starts acquisition and the short placement cue. After all three streams and five settled seconds, the next cue is "Walk to the finish and stand still. Begin walking now." Fresh movement arms capture ending; four consecutive quiet seconds with fresh sensor coverage stop it automatically. Resumed motion or stale sensors reset that quiet timer. Default fallback is 60 seconds; optional 15/30/60 limits remain available. A mid-route pause can also end this engineering trial: quiet-stop records the mechanism, not proof of arriving at a distance boundary. Clinical tests and their rest rules remain unchanged. The final spoken cue is short and independent of file saving. Result exports remain visible; technical capture details are collapsed. These changes are local, not yet published to the phone, and require no new native module.

Corrected supplied trial confirms three continuous streams and a duration-consistent MP4. A local image-only feasibility screen masked the upper 21.6% of 360 x 640 frames and sampled 22-40 seconds at 5 fps. Across 89 adjacent frame pairs, median detected corners were 199 and median forward/backward-consistent tracked fraction was 92.5%, minimum 65.2%. This tests short-term 2D trackability only, not depth, calibrated scale, camera/IMU timing or distance accuracy. Original frames and IMU were unchanged; screen outputs stay local. Calibration and independent measured-route validation are still required, consistent with [OpenVINS sensor calibration](https://docs.openvins.com/gs-calibration.html).

Export both matching-ID MP4 and IMU JSON from the trial or its saved recording. JSON retains raw sensor axes, native sensor timestamps and monotonic camera-request, instruction-completion, movement and stop events. Expo Camera does not expose actual recording-start or per-frame timestamps here. Actual video start offset, timing uncertainty and camera/IMU clock calibration remain unavailable, and vioReady is false. This is concurrent acquisition for a feasibility review, not precisely synchronized VIO or metric distance. Importing JSON alone does not transfer video bytes.

Trials are engineering practice records outside G.A.I.T. requirements and clinical trends. The mounted room view cannot replace external full-body observer footage. Version 0.3.1 requires a new APK; build 6 cannot acquire its native camera module by OTA. Automated controller/storage/native-screen checks use injected hardware. Actual-holder image quality, real rates/gaps, camera calibration and native camera/IMU synchronization still require validation before odometry integration.

### Front-camera sample review, 6 October

Inspected the user-supplied mounted-camera clip locally: 284 decoded frames, approximately 9.57 seconds, 720 x 1280, nominal 29.69 frames/s. Sampled frames show an external room view, but also a dark upper-edge obstruction, blurred motion, bright-window exposure and substantial view changes between ceiling, room and floor; the ending includes handling/face imagery. The cause of the obstruction and whether every segment was in the final fixed mount are not established. Follow-up inspection of 12 time-spaced frames with image-height guides estimates the dark upper-edge obstruction at roughly 10-20% of image height in several frames, with a variable soft boundary. This is a visual estimate, not pixel segmentation or a validated acceptance threshold. The remaining image is sufficient to justify a masked-tracking feasibility experiment, not to approve metric distance accuracy. This is useful mounting-feasibility evidence, not a successful odometry trial.

No synchronized raw IMU, camera calibration, camera-to-IMU transform/time offset or independently measured travelled length accompanied this clip. Therefore no defensible metric distance or tracking error was calculated. Custom front-camera visual-inertial tracking remains unimplemented. [OpenVINS calibration documentation](https://docs.openvins.com/gs-calibration.html) explains how IMU fusion supplies monocular scale and why intrinsics, extrinsics and timing matter. Improve lens clearance/window cleanliness, secure the mount and use a continuously visible, well-lit textured scene; validate repeated measured short routes using synchronized camera/IMU capture before considering automatic distance stopping. Preserve the existing lower-back position. Mounted footage looks outward and cannot replace an external observer's full-body views for all G.A.I.T. items.

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

The lower-back IMU can record timestamped, asynchronous accelerometer, gyroscope, and magnetometer streams; identify recording start and stop; describe pauses, motion coverage, turns, placement shifts, and experimental timing features; and preserve a clinician-entered distance or event marker.

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

Placement resolved by the user on 2 October: **screen/selfie camera faces the room; rear camera faces the body**. The screen-out arrangement was the constraint at that time. On 4 October the user allowed camera use and consideration of a holder/orientation change to expose the rear camera, while retaining lower-back sensing. ARCore remains unsuitable for the front camera. Prefer a separate rear-camera ARCore feasibility trial if that mounting change is acceptable; retain a calibrated front-camera/IMU prototype as the higher-effort alternative. This is an engineering feasibility proposal, not verified front-camera support or calibrated distance. No cloud subscription, billing account or paid external service is proposed.

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


## Dedicated short Google distance experiment - 2 October 2026

User requested a separate experiment because setting up a 12 m course is impractical for initial API testing. Local Android source now exposes Home > Import, research tools and app information > Research tools > Google distance trial, with measured 2/3/5 m routes (default 3 m). No clinical-test chooser is required. Participant linkage, permission-before-mounting, five-second standing reference and movement/fit checks are retained. The spoken cue asks the user to return to the start after setup, wait for Begin, then walk to the mark and stand still. Raw IMU starts after first-step detection; four seconds of continuous quiet automatically ends the trial, with a 60-second safety limit. Google querying begins at the audible cue (first-step fallback), retains a fixed stop boundary, and allows delayed post-stop reads for up to 30 seconds of waiting plus request time. The rest tail is part of the Google query interval; its mean speed is not moving-only speed.

The result asks whether the finish was reached before offering a direct full-JSON export. Reference route, completion and endpoint survive JSON and raw CSV review. Google records remain distinct from measured reference and raw IMU; no missing data is fabricated or replaced by a height estimate. A rest can terminate this engineering experiment early; the user can report that explicitly. Trials have versioned metadata and practice tagging, remain linked to participants/history, and are excluded from clinical speed trends and personal distance calibration. Normal clinical flows are unchanged. EN/MS/ZH text added.

Verification: TypeScript, 123 automated tests and Android/web Metro exports passed. These are software/contract checks, not native compilation, physical validation or measured accuracy. Google short-route availability and latency must be assessed on the actual holder; a new APK containing the Google module remains required and has not been built. This follow-up is local pending publication review. No model training or new dataset acquisition.

## Profile entry parity and protocol sources - 4 October 2026

Verified source already contains age/sex/height/weight, walking aid, stroke type/location, hemisphere/body side, chronicity, history source and pre-existing gait/orthopaedic notes. Clinical tests already require explicit hemisphere/body side/chronicity/source, allowing unknown; optional clinical information must not be guessed. The gap was test-created profiles: setup lacked weight, stroke type/location and baseline-history inputs. Added those to the existing details/history panels, made stroke-history review discoverable for research walks too, and retained prefill and reset when selecting/changing participant. The resolver preserves omitted existing fields and validates entered weight. Both saved profiles and recording snapshots now receive these inputs; JSON retains full context and feature CSV additionally exports baseline gait/orthopaedic notes with CSV escaping.

Clinical tutorial worker notes now link each 10MWT/TUG/2MWT/6MWT to its specific Shirley Ryan AbilityLab RehabMeasures source. Source availability does not validate automatic phone endpoints. Existing 12 m/central-10 m variant, trial timing and clinical limitations are unchanged. New prompts have English/Malay/Chinese coverage. TypeScript, 134 tests (including rendered setup-to-snapshot and clinical export checks) and Android Metro export passed. Generated bundle stays ignored/local. No physical-device or clinical validation was performed; no native/dependency changes, so a compatible OTA can deliver this after publication. Changes remain local for user review.

## Complete observer G.A.I.T. and sensor-free flow testing - 4 October 2026

Completed the user-supplied Appendix A digital form: 31 observer-rated items, maximum 62, source SHA-256 recorded in gaitRubric.ts. Preserves all 129 scoring choices, including equal-score alternatives and A/B/C/D branches; directional qualifiers, item notes, assessor, date, assessed limb, diagnosis, device/orthosis/assistance and observation/video reference. Missing items are never zero. Full totals require all ratings, necessary qualifiers and core assessor metadata. No sensor-derived G.A.I.T. scoring or clinical improvement claim is made. At publication on 4 October, the original detailed rubric remained English with multilingual interface labels. The current 6 October agreement makes the entire worker screen consistently English, as specified above. No clinical translation validation is claimed.

The form is saved with each recording and participant snapshot, reopened from recording details, validated on JSON import, exported as per-item option/score/notes/qualifiers in feature CSV, and displayed as an observer total in dashboard session summaries. This supersedes the earlier incomplete-form status in this batch. No new clinical recordings or assessment validation were acquired.

Added a development-only browser Flow Lab and Playwright phone-viewport tests. Fixtures are clearly marked, contain no sensor samples, are practice-only and memory-only, and cannot enter native/release capture. Existing React Native tests inject sensor events/speech callbacks for acquisition logic. Browser tests cover saved full form, profile/tutorial navigation and actual shared preview start/finish components for 10MWT, TUG, 2MWT and 6MWT; long timers use a controlled test clock. This is not an Android emulator or physical-sensor/audio validation.

Validation: TypeScript, 138 unit/flow tests, six browser E2E tests and Android Metro export pass; generated screenshot inspected. Test outputs and source-PDF render stay ignored/local. Playwright is a development dependency only. Standalone test launch scripts retain the installed build-6 Android runtime fingerprint a48c2ed43ddd2142beaa39b7f8031b8fff327407. Run node scripts/start-flow-lab.cjs and npx.cmd playwright test from android; see FLOW_TESTING.md. All changes remain local for publication review.

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

Physical test: install over the existing app; Research tools > Phone calibration.
Choose Sensor noise, tap Measure sensor noise, leave the phone untouched on a
firm table with the app open until the finish voice, then export its ZIP. Choose
Camera board, keep the digital board fixed and its square size verified, capture
through the usual waist-bag window and export that separate ZIP. Send both for
processing; no patient-specific repeat or new walking-distance claim. Full noise/
geometry and native VIO remain incomplete; a longer stationary noise record may
be needed. Do not enable clinical auto-stopping. Git/OTA publication still awaits
review; dependencies, demo assets, APKs and generated reports remain local.
