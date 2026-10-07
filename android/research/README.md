# Phone camera / IMU calibration

Current status (7 October): local 0.3.6 integrates native guided Zhang/OpenCV
lens calibration and QR-paired, one-time local iKalibr reference processing.
[Start here](CALIBRATION_SETUP.md). The computer displays the stationary board
and a live framing diagram from actual phone frames while the bagged phone moves.
No tablet is needed; a moving-tablet mode is explicitly optional. Brief loss of
the target retains accepted lens views. This ergonomic source revision has not
been delivered to the installed build-15 APK; its Android runtime is unchanged.
The app transfers/retrieves alignment captures automatically. No print, ruler,
manual export/import or patient-specific hardware calibration is required.

The native solver has actual OpenCV JNI known-answer and retained-artifact checks.
188 app checks, 43 Python research checks and 10 prior app browser flows pass. The latter
do not validate physical Camera2/audio or distance accuracy. Reference solver
results stay review-required, with all metric/full-calibration readiness false.
Complete noise, parameter/residual/repeatability review and independent marked
routes remain required. The Android distance tracker remains a prototype;
[offline VINS/OpenVINS](vio-reference/README.md) is not an Android estimator port.
The new native methods need the replacement 0.3.6 APK.

An actual local companion/browser check verifies computer board/framing fit,
drawn detections, progress/completion and optional tablet layout using a synthetic
JPEG and simulated native counts. Real OpenCV detection is exercised with whole,
partially clipped and absent targets. It does not establish physical usability or
calibration accuracy. JPEGs are processed transiently on the local computer; the
page receives no JPEG and display-only coordinates cannot admit calibration.

The pinned published executable has now completed its synthetic image/IMU control.
The final CPU run took 582.2 seconds, reusing upstream image preparation from the
recorded earlier attempts; recovered translation error was 5.68 mm and rotation
error 0.0165 degrees. This is numerical integration evidence, not physical phone
or clinical distance accuracy. The companion also supports an immutable official
CUDA COLMAP worker for feature extraction/matching, with retained failure logs and
a CPU fallback. Final iKalibr calibration stays CPU because its installed Ceres
library has no CUDA component. Both binaries have separate provenance.

Research orchestration and recorded verification live in
[the calibration notebook](../../notebooks/phone_camera_imu_calibration.ipynb).
`camera_calibration.py` supplies the reusable loader, printed ChArUco board,
geometry/timing fitting and rejection gates; `test_camera_calibration.py`
checks numerical recovery and invalid-input rejection.

`camera_imu_joint.py` adds row-specific exposure/readout times and joint
camera/gyro image fitting. Whole held-out views keep orientation, bias and clock
offset fixed; only translation is fitted on them. Its rotation/timing candidate
is not a full calibration report and must not be imported as one.

`visual_tracking.py` provides an experimental fixed monocular map, triangulation,
optical flow and PnP. Map loss terminates the segment; there is no scale-reset
fallback. `visual_inertial_scale.py` fits metric scale, accelerometer bias, gravity
and lever arm from consistent map accelerations and real SI IMU samples. Its
route connector reports experimental horizontal **camera** travel only when
observability, physical consistency and residual checks pass. Sway, drift,
rolling-shutter correction, map expansion and continuous inertial fusion remain
unresolved. The Python versions remain offline; the Java research
tracker/scale implementation is integrated into the Android **Camera distance
trial** screen. Local 0.3.4 adds conservative world-map landmark renewal using
accepted poses, without resetting map scale or adding relocalization/loop closure. It is not a clinical distance or test-stop feature.

The trial uses the native unrotated Camera2 pipeline, actual exposure/readout
metadata, three raw IMU streams and a phone-bound rotation-only research profile.
It waits for fresh stillness, completes the spoken start cue, begins tracking on
movement and ends after sustained quiet (or a safety limit). Missing calibration prevents starting the distance trial. During capture,
map loss, clock gaps, unobservable scale and failed physical checks withhold the
estimate while preserving the raw ZIP. The metric path covers the tracked,
smoothed interior camera segment; initialization and derivative edges are not
the full marked route. Residual body sway may affect its length. Do not treat it
as full-course distance or a 10MWT boundary.

`distance_research_profile.py` exports the separate research-only profile; it
does not turn a rotation candidate into accepted full geometry. The current
phone's generated profile stays local under its second-capture output directory.
The notebook records five executed Java/OpenCV JNI known-answer checks and an
explicit replay of the second capture. Desktop tests use a loader adapter with
the real matching OpenCV DLL; they do not execute Android camera/permissions or
confirm physical walking accuracy. The replay loses its fixed map after one
pose; this failure is retained. The native SDK test tools and reports stay ignored.

Native dependencies are the official [OpenCV Android AAR](https://opencv.org/opencv4android-usage-models/)
4.12.0 and [Commons Math linear algebra](https://commons.apache.org/proper/commons-math/userguide/linear.html)
3.6.1. Their Apache-2.0 licenses/notices are packaged as Android assets. No remote
distance service, account or subscription is used.

Use `C:/Users/frank/.venv/Scripts/python.exe` with OpenCV ArUco, NumPy and
SciPy. Portable dependencies are listed in `requirements.txt`. Actual captures,
printed-board artifacts, reports and APKs remain under ignored `android/dist/`.

The researcher displays the board on a stationary tablet, or prints a
180 x 140 mm board, verifies 20 mm squares with a ruler,
keeps the board/display fixed on a table or stand, and performs one 40-second capture using **Research tools > Phone calibration**.
The first five seconds are still; subsequent motion must cover all rotation axes
and several translations of only the recording phone, with the board visible and the same optical holder
window in front of the camera. Export the ZIP, process it in the notebook and
import an accepted `calibration-report.json` back into the same installation.
Patients do not perform this board routine. Their individual quiet-standing
midline reference remains separate.

Calibration capture is native Camera2 YUV -> JPEG, unrotated/unmirrored, with
hardware frame timestamps, exposure/skew metadata and direct SensorManager
accelerometer (m/s2), gyroscope (rad/s), magnetometer (uT) samples. Requests of
200/200/50 Hz and up to 15 stored frames/s are targets, not delivered-rate claims.
Camera focus and stabilization are requested fixed/off and reported when
available. No microphone, remote API, patient video or cloud service is required.

Accepted reports are **geometry candidates**, not validated odometry. They
retain `distanceReady=false` and cannot control a 10MWT stop. Fitting checks are
provisional engineering gates; interleaved held-out views are an internal check,
not independent walking validation. Magnetometer hard/soft-iron calibration and
IMU noise/random-walk characterization are not performed. Older Expo MP4 capture
has a different pixel/timestamp pipeline and cannot directly reuse these camera
intrinsics. No new physical calibration result is claimed until a real ZIP is
processed; no distance accuracy claim until the matching odometry pipeline is
implemented and evaluated on separate measured walking routes.

Actual 6 October investigation: row-specific camera/gyro fitting on the second
ZIP gives 1.1594-pixel held-out coordinate RMS, 1.6068-pixel p90 and a -29.73 ms
candidate clock offset. Its internal rotation/timing gates pass. The known
moving-tablet first capture fails (6.9382-pixel RMS). Mean-row timestamp correction
alone did not pass the old angular-rate gate (0.08162 rad/s); that gate was not
relaxed. Full calibration remains unavailable: 218 usable second-capture poses
have no sufficiently long contiguous translation segment (largest gap 2.136 s).
The fixed-map visual frontend also loses tracking on that bench capture. These
are actual failure results, not successful walking-distance validation.

The notebook retains both captures, processor identity, failed and candidate
reports, and executed synthetic tests. Neither ZIP is a held-out clinical route.

Sources: [OpenVINS calibration](https://docs.openvins.com/gs-calibration.html),
[Android Camera2 timestamp contract](https://developer.android.com/reference/android/hardware/camera2/CameraCharacteristics#SENSOR_INFO_TIMESTAMP_SOURCE_REALTIME),
[OpenCV calibration](https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html).

## Current retained-walk verification

The first user-reported 3 m build-10 ZIP captured all streams but had no profile.
Offline profile replay failed after 20 poses. With map renewal, the same retained
development walk yields 151 poses across 11.823 s, 318 added landmarks and no
tracking loss. Scale remains physically rejected; there is no accepted metre
estimate. Six real JNI numerical checks now include renewed world-coordinate
and map-scale preservation. This is not independent accuracy or live timing
validation. See executed notebook outputs and originating source hashes.

Latest actual build-11 trial includes a profile but rejects reprojection-error
after one pose, 0.23 s from movement trigger (1.6478 px versus 1.5 px gate).
JPEG replay also rejects after one pose. The replay loader now uses the first
native tracking-log frame timestamp where available, retaining original bench
cutoff behavior otherwise. Acquisition is healthy; bootstrap robustness and
metric scale remain unresolved. Retained-walk improvement is development evidence,
not a claim of reliable live distance. See notebook actual retry outputs.

## Native acquisition preparation ? 7 October 2026

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
