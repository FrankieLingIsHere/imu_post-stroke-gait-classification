# One-time phone calibration

**Superseded user setup: 9 October 2026.** The current product must enroll every
supported future phone without a computer. The desktop workflow below is retained
for developer reference only. Local 0.3.12/native code 24 now has an independent on-phone setup path.
The release-signed ARM64 APK is ready locally; prospective production acceptance remains. Do not repeat desktop setup as the proposed solution.
See [current requirement and gaps](ON_DEVICE_DISTANCE.md) and
[handoff status](DISTANCE_PHONE_CHECKS.md). Existing files/profiles are preserved.


**Verified APK - 8 October 2026:** 0.3.11/build 23 finished successfully (`d64795ab-4667-455a-b6dd-113fb99759f1`). ZIP integrity, compiled version/package, runtime, new native practice/end-boundary API, bundled EN/MS/ZH guidance and cryptographic Android signature pass. Certificate matches build 20, supporting an in-place update. [Download build 23](https://expo.dev/artifacts/eas/L8EFVUNHKT1E4voE2EAAORAoVj3Z_mfykV_a0HqcaA0.apk). Local file: `android/dist/apk/GaitTrace-0.3.11-build23.apk` (233,387,998 bytes). SHA-256: `dc09ab82650aef3817cfff4ad6304cf0c136aa2e6cf606529b4ed9583008abf5`. Runtime: `9bc3827992f3c583d878767addc04dae0f3d3081`. Organized local release evidence: `android/dist/releases/0.3.11-build23/`. Physical checks remain; no source push or OTA publication.


**Current native trial: GaitTrace 0.3.11 / build 23.** A new APK is needed for practice and first-motion/quiet-stop boundaries. Existing saved phone calibration is retained. Follow [the remaining physical checks](DISTANCE_PHONE_CHECKS.md). Source remains local pending review.


## Local compute backend

Restart **Start phone calibration.cmd** after desktop-source updates. Short
distance trials now default to CPU, the faster measured frontend on this computer.
The installed OpenCV 4.12 image runs a persistent native CPU worker. If that image
is absent, the helper explicitly discloses its Windows OpenCV fallback. Calibration
COLMAP extraction/matching still uses CUDA when available. These desktop changes
alone do not require a new APK or repeated calibration. The newer native boundary flow requires build 23.

Optional `GAITTRACE_VIO_BACKEND=cuda` starts the isolated CUDA image and verifies
actual corner/LK kernels before advertising GPU readiness. A persistent worker and
named compilation cache avoid per-job cold starts. Phone health checks return the
actual startup preflight and its age. Close the helper to stop its owned worker.
The first optional GPU build compiles dependencies for this computer's RTX 5060
(SM 12.0). Other GPU architectures need a separately checked build.

Distance jobs keep working images/state files on Linux storage and transfer at
stage boundaries. Result JSON records image identity, feature-source hash,
actual CUDA call counts, CPU stages and per-stage wall time. GPU failure fails the
attempt and keeps the capture; it never silently claims GPU execution.

GPU stages: calibration COLMAP features/matching; distance-trial Shi-Tomasi corner
selection and pyramidal LK. CPU stages: JPEG decoding, calibrated RANSAC, file
handling, COLMAP mapping, iKalibr and the unchanged pinned VINS/Ceres 1.14 solver.
GPU acceleration changes compute performance, not clinical distance readiness.
The CUDA frontend is diagnostic and not bit-identical to CPU LK: fixed 30
iterations versus CPU epsilon stopping, and device corner-selection differences.
See the executed notebook for benchmark evidence and integrity limits.

**Measured performance, 8 October:** the same-build warm-worker comparison on
353 retained development frames gives median CPU **1.4587 s**, CUDA **2.2742 s**
over three alternating repetitions. CUDA was about **56% slower** for this small
150-feature workload. Actual GPU execution is confirmed (704 LK calls, 230 corner
calls; observed GPU memory 116 MiB), not a speedup claim. The complete CUDA replay
has a 2.03 s feature stage and 7.01 s CPU estimator stage. The native CPU path has
a 1.48 s feature stage and 5.35 s estimator stage. Estimator inputs differ between
the diagnostic frontends, so these are not identical solver workloads. Both reset
and finish uninitialized, so neither admits a complete distance measurement.
GPU mode remains explicitly available. The default for these short trials is
now the measured faster native CPU path. GPU-only processing is
not recommended. The hardware/kernel checks also pass the known two-pixel-motion
and irregular-frame-clock test. Raw captures and estimator settings are preserved.

The default CPU frontend reuses the installed
OpenCV 4.12 image as a persistent CPU worker; its calculations are labelled CPU,
with zero CUDA calls. On a computer without that image it uses Windows OpenCV as
an explicitly disclosed fallback. Calibration feature matching continues to use
CUDA when available. Set `GAITTRACE_VIO_BACKEND=cuda` only for a deliberate GPU
comparison; no manual backend selection is needed for normal use.

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

OpenCV documents the [CUDA LK implementation](https://docs.opencv.org/4.12.0/d7/d05/classcv_1_1cuda_1_1SparsePyrLKOpticalFlow.html)
and [CUDA corner detector](https://docs.opencv.org/4.12.0/dc/d6d/group__cudaimgproc__feature.html).

**Previous verified install - 8 October 2026: 0.3.10 / build 20**

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


**Previous verified build - 0.3.9/build 19**

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


This is researcher preparation for a particular phone, native camera pipeline
and optical setup. Patients do not repeat it before their walking tests.

**Current calibration repair (7 October):**

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

1. On this computer, double-click `android/Start phone calibration.cmd`. Keep the
   page and processor open. The free WSL/Linux Docker reference environment is
   installed on Frankie's computer. Other computers need that environment first.
2. Use the same private Wi-Fi. On the new Android app, open **Research tools →
   Phone calibration → Connect calibration computer** and scan the code. The
   computer switches to the board and a live framing diagram. **No tablet is
   needed.** Keep that computer board still.
3. Tap **Calibrate camera lens**. Hold the phone in its usual bag, front camera
   toward the computer. Watch the outline/dots beside the board on the computer
   while slowly moving/tilting the phone. Follow the voice and pause between
   positions. Briefly losing the board does not reset saved views. No ruler,
   physical print or manual ZIP transfer is needed. A saved profile also offers
   **Repeat lens check**, preserving the prior profile if the new attempt fails.
4. Tap **Align camera and sensors**. Hold the phone in its bag, front camera
   facing a textured room. Follow the stillness and gentle loops/tilts prompts.
   After the movement cue finishes, the phone records 50 seconds and stops
   automatically. Keep the lens unobstructed and the room lighting stable.
   This is research-team handling of the device, not an exercise for a patient.
5. The app uploads the capture locally and retrieves the reference result. Keep
   the computer running while it processes. **Leave processing** does not delete
   the computer job; **Resume calibration processing** retrieves its result.
   Restarting the processor creates a new pairing code: reconnect first.

Published on 7 October 2026 from commit `2cce693`. GitHub's three publication
workflows passed. The first functional Android update is
`01a115df-b6e0-7bf6-9760-2c02061813e8` on channel `preview`, runtime
`e1383287be615da4c75a7a9ce08b9260cfd2cfb3`. Expo's client endpoint serves that
manifest for build 15. Later documentation-only updates may have a newer ID.
If build 15 is installed, open the app online, let the update download, then
fully close and reopen it. Older builds need the build-15 APK for the new native
APIs. Restart the computer launcher so it runs the current companion source.

The computer shows a mirrored framing diagram detected from actual phone JPEGs,
not another coded board/video image. That prevents a duplicate target appearing
in the same camera view. Up to one frame/second is sent to this computer over
private Wi-Fi, decoded in memory and discarded. Only outline/corner coordinates
and native accepted-view count reach the computer page; no camera preview is
saved or sent to a cloud service. Framing is optional display feedback and cannot
admit a calibration or change raw pixels. Failed/absent/stale frames show waiting
or paused feedback. The native phone solver still controls quality and lens save.

**Use a tablet instead** remains an explicit optional mode: the computer gives a
board-only tablet link, the phone stays supported and the tablet moves. Switch
modes before starting. The default always uses the computer board. The target
display must remain flat with unchanged proportions; digital perspective warping
does not replace physical relative viewpoints.

The transfer uses a session token over private-LAN HTTP. It is not encrypted.
The QR code grants access to this temporary calibration service. No cloud
camera upload or paid distance service is used. If Windows shows a firewall
prompt for this Python processor, allow the private home/research network.
Public/guest Wi-Fi and networks that isolate devices will not work.

The app deliberately distinguishes **lens saved**, **reference result saved**
and **validated metric tracking**. A reference result is retained for review,
not automatically admitted to the live distance tracker. Parameter conventions,
physical bounds, residuals, repeatability, complete IMU noise and independent
distance accuracy still need review. Ordinary waist walking does not supply all
the movement required for full calibration. Changing phone, camera dimensions,
capture pipeline or bag-window optics invalidates reuse. An app reinstall that
clears device storage also loses this binding.

## Methods and provenance

- Lens: Zhang's published planar calibration, through OpenCV 4.12
  `calibrateCamera`, with ChArUco detections. Uniform board-size scale is irrelevant
  for lens intrinsics; the pattern must remain planar and retain its aspect ratio.
  Automatic view selection, held-out reprojection, subset stability and radial
  mapping checks are provisional engineering admission gates, not clinical limits.
  Zhang allows either the camera or the target to move. ChArUco permits partial
  views; the app still needs at least 20 detected corners per accepted frame and
  its existing 24-view/coverage gates. Repositioning frames are skipped, not a
  reason to restart. Moving the board is valid for **lens-only** fitting. The
  separate camera/IMU alignment requires the phone to move in a stationary room.
- Camera/IMU: the iKalibr authors' IEEE T-RO 2025 reference executable, pinned
  Docker base image, rolling-shutter midpoint model and standard COLMAP SfM. No custom
  rotation/translation solver is substituted on failure. Original ZIPs, raw
  hardware timestamps, sensor units, factory metadata, upstream parameters and
  software identities stay available under ignored local storage.
- Magnetometer: all three raw sensors are retained. iKalibr itself uses camera,
  accelerometer and gyroscope; it does not calibrate magnetic heading.
- Equal provisional IMU weights are disclosed in the processor provenance. They
  are not a measured noise model. The separate stationary-noise research tool
  remains available under **Research capture tools**.

Sources: [Zhang, 2000](https://www.microsoft.com/en-us/research/publication/a-flexible-new-technique-for-camera-calibration/),
[OpenCV partial-view ChArUco calibration](https://docs.opencv.org/4.x/da/d13/tutorial_aruco_calibration.html),
[iKalibr authors](https://github.com/Unsigned-Long/iKalibr).

## Local GPU processing

The companion automatically selects the installed CUDA COLMAP worker when Docker
has an NVIDIA runtime. Frankie's RTX 5060 and WSL Docker runtime are now configured.
The official CUDA COLMAP snapshot is pinned by digest; its version and executable
hash are recorded separately from the unchanged iKalibr executable. Feature
extraction and matching request CUDA. Reconstruction and the reference calibration
solver remain on CPU; the authors' installed Ceres library has no CUDA component.
If GPU processing fails, its logs are kept, the fallback is recorded and the CPU
path is tried. GPU acceleration changes processing time, not clinical readiness.

The actual GPU-assisted synthetic control completed with 199 registered images:
24 seconds for extraction, 19 for matching, 43 for reconstruction and about
15.6 minutes overall including fresh image preparation and CPU calibration.
Known geometry/timing checks passed (6.46 mm translation, 0.033-degree rotation,
0.161 ms clock error). This is not a controlled whole-job speed comparison with
the earlier CPU run, which reused preparation and used a different COLMAP version.
It is also not a physical phone accuracy result. All distance readiness remains
false; GPU processing does not itself validate metric walking distance.

For another NVIDIA computer, configure the free
[NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
before launching the companion. On WSL, keep the Windows NVIDIA driver; do not
install a Linux display driver. The launcher builds the small Python wrapper on
the official CUDA image automatically. The first GPU image download is about
3.37 GB; it stays outside Git and is reused. Non-NVIDIA computers retain CPU
processing. No paid GPU service is involved.


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
