# Phone camera / IMU calibration

Current entry point: [local pipeline results and limitations](ON_DEVICE_DISTANCE.md).

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

The computer paths and delivery notes below are historical research evidence.

The earlier separate trial follows:

Current distance processing: [integrated research helper](#integrated-research-distance-helper---8-october-2026). The standard launcher now selects the corrected pipeline; build 23 and saved calibration stay compatible. Distance accuracy remains unvalidated.

**Earlier separate native trial: GaitTrace 0.3.11 / build 23.** Use build 23 for practice and first-motion/quiet-stop boundaries. If it is already installed, the corrected computer helper needs no replacement APK. Existing saved phone calibration is retained. Follow [the remaining physical checks](DISTANCE_PHONE_CHECKS.md). Source remains local pending review.


**Previous install: 0.3.10 / build 20.** See
[CALIBRATION_SETUP.md](CALIBRATION_SETUP.md) for the verified APK and new distance
trial. Desktop compute changes require restarting the helper, not another
APK for those desktop-only changes. The newer native practice/boundary flow requires build 23.

**Previous calibration build - 8 October 2026**

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


Historical status (7 October): local 0.3.9/build 19 repairs the verified 48-view
cap and guides stage-specific view collection. [Start here](CALIBRATION_SETUP.md).
A new native APK is required. Build 17 was canceled as superseded; source
publication awaits scope review. Latest actual ZIP passes unchanged lens gates
in desktop replay (24 views, held-out p90 0.2530 px), not a physical device pass
or metric-distance validation. Raw captures and generated proof stay local.

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
That initial native verification preceded source/OTA publication. The user later
approved the final 116-file scope, published as `2cce693`; see the current status
and setup guide above. The exact review page stays local/ignored.


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


## Distance validation integration (local 0.3.10)

`vio_compute.py` now selects the measured faster native CPU corner/LK frontend by default,
kernel-checks it during helper startup/health, and stages VINS replay on native
Linux storage. The pinned estimator and calibration solver remain CPU; no claim
of an entirely GPU pipeline is made. `vio-cuda/Dockerfile` pins CUDA by digest and
OpenCV/contrib by verified commits. Each result discloses actual GPU calls and
stage timings; raw captures and generated images stay local. See the compute
section in CALIBRATION_SETUP and the notebook's executed CPU/CUDA comparison.
The 353-frame controlled benchmark is CPU 1.46 s vs CUDA 2.27 s; GPU support
is verified but is slower for this workload. Default CPU mode uses the same
installed image/worker on this computer, with a Windows fallback if absent.

`distance_validation.py` binds the saved iKalibr candidate to a new raw native
trial and runs the pinned VINS replay with measured extrinsics/time/readout,
explicitly provisional noise and the diagnostic LK frontend. The local companion
adds authenticated `/api/distance-captures` and engine health, durable jobs, retries
and result delivery. No Google service, subscription or paid distance API is used.
The marked length is comparison-only. Partial/reset trajectories cannot become
full-route estimates. All clinical readiness remains false. See CALIBRATION_SETUP
and the executed camera/IMU notebook for the short phone flow and control result.

The obsolete raw Google and duplicate camera screens are not in production
navigation. Keep historical research modules/readers and fixtures for older
exports. App Storage can permanently remove raw frame trees, ZIPs and stale
indices while retaining compact saved device calibration and pairing.

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

Historical pre-integration checkpoint.

The isolated fixed-time rolling-shutter candidate improves retained phone trials:
three of four reported measured attempts produce complete candidates, latest
confirmed 3 m changes from 3.24120 to 3.15688 m. One still fails. Added pose-jump
integrity checks do not relax drift/geometry gates. Altered-start trial excluded
from accuracy; no fitted scale. 74 research checks, 250 actual pinned-factor cases
and fresh analytic controls pass. Candidate is not active in the live helper;
quiet-prefix selection is notebook-only. See [wrapper contract](vio-reference/README.md#fixed-time-rolling-shutter-investigation---8-october-2026)
and the existing camera/IMU notebook for executions and preserved failures.
Complete-service integration precedes prospective phone validation. No new APK,
calibration capture, source push or OTA.
