# Phone-only distance and short setup

## Retained-capture regression results — 10 October 2026

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

## Historical implementation description (not physical acceptance)

## Phone-only setup and live distance - 9 October 2026

Local 0.3.12/native code 24 now implements first setup and walking tracking on
Android, without a computer, pairing, target board, upload or paid API. The new
**Set up this phone** screen also opens automatically if ordinary test setup
finds no matching profile. Completed quiet/movement voice instructions gate real
native capture. A failed or interrupted attempt preserves the previous profile.
EN/MS/ZH text and speech are included. Setup belongs to the phone/camera/window,
not each participant. Approximately ten seconds quiet and fifty seconds guided
motion are captured, with checks afterwards. A guaranteed few-second scan is
not claimed.

The pinned OpenVINS core estimates eight camera parameters, camera/IMU alignment
and time offset from actual front-camera/accelerometer/gyroscope measurements.
Factory camera metadata supplies only a prior. Three-axis magnetometer capture
is retained but not invented or fed into the visual-inertial solver. Admission
requires real-time hardware clocks, all-axis excitation, bounded uncertainty,
plausible geometry and a stable five-second tail. Poor scenes, missing data or
unsettled fits cannot supply a profile. No route length is used to fit scale.

Main recording runs tracking continuously. A tracked 10MWT uses 1 m approach,
10 m timed zone and 1 m finish, with automatic estimated 12 m stopping. Quiet
rests cannot replace that distance boundary. Camera-to-IMU time offset is
accounted for, and boundary interpolation only uses adjacent accepted poses.
Stale tracking, gaps, jumps, excessive uncertainty and route mismatch withhold
complete distance. Saved live poses supply the final calculation rather than a
second scaled estimator. TUG chair contact remains provisional and endurance
stops remain duration-based. Existing profiles, assessment linkage, real sensor
exports, old recording compatibility and permanent capture cleanup are retained.

Executed evidence: 231 app tests and 617 native contract assertions pass.
Actual host execution of the same core rejects blank footage and insufficient
calibration excitation. A 45-second textured-scene/all-axis control converges,
and the actual Java admission code accepts its stable tail. A perturbed-prior
control also converges. A known-geometry 3 m control returns 2.98457 m. Reusing
the newly admitted profile in a separate 3 m control and the actual app result
validator returns **2.88629 m** (-0.11371 m, -3.79%), without scale fitting.
These are newly executed synthetic software controls, not phone recordings,
clinical validation, cross-device evidence or model training. The notebook saves
results and provenance; generated frames, profiles and binaries remain local.

The native port includes explicit serial initialization, recoverable invariant
failures and a motion-cue handoff that prevents zero-motion updates from
suppressing slow walking. Rotational rolling-shutter compensation uses measured
readout timing and gyro data. Translation during readout is not modeled.
Noise densities/bias random walk remain provisional. Numerical covariance and
repeatability are not independent accuracy. Weaker-motion controls were rejected;
this is a real observability/first-use usability limitation, not a reason to
relax acceptance checks. No real cross-device few-shot network is trained.

A release-signed ARM64 APK is now ready locally: **GaitTrace 0.3.12 / build 24**.
Its certificate matches installed build 23, so it supports an in-place update
without uninstalling. Packaged native libraries, licenses, version, EN/MS/ZH
strings, preview request headers and fingerprint runtime are verified. The
read-only update endpoint check returned 204 for this runtime: no compatible
OTA is currently published. After installing this native binary, compatible
JavaScript/asset updates can use preview; native changes still require an APK.
Physical fresh-phone setup, mounted accuracy/failure-rate, audio and runtime
acceptance remain. Production/clinical readiness is **not** claimed. No push,
OTA or public release publication has occurred. The [phone checklist](DISTANCE_PHONE_CHECKS.md)
sets out the remaining checks.

## Historical desktop board-free enrollment - 9 October 2026

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
loading/deduplication, model-level train/validation/test separation, matching phone/camera/window support-query tasks, labelled
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

## What the small adaptive model does

`ShortBaselineModel` is a Bayesian gyro-bias model. Ten 0.2-second stationary
blocks update a zero-mean bias prior. It reports posterior uncertainty, rejects
moving/sparse/nonfinite observations, and seeds VINS only when uncertainty and
bias bounds pass. An uncertain fit leaves the ordinary VINS bias initialization
in place. The raw IMU and saved camera calibration are never overwritten.

This is automatic short-observation statistical adaptation, **not a trained
cross-device few-shot neural network**. It cannot learn lens distortion,
camera-to-IMU geometry or metric scale from a few unlabeled steps. No clinical
gait classifier or participant-specific diagnosis was trained in this work.
Its bounds are engineering choices requiring phone evaluation, not a published
clinical accuracy guarantee. The current retained capture's posterior is too
uncertain to apply; withholding that adjustment is the intended behavior.

## How others reduce setup

- [HKUST VINS-Mobile](https://github.com/HKUST-Aerial-Robotics/VINS-Mobile)
  demonstrates visual-inertial estimation on compatible iOS phones. It supports
  the feasibility of mobile computation, not arbitrary-phone/front-window accuracy.
- [VINS-Mobile-Android](https://github.com/jannismoeller/VINS-Mobile-Android)
  provides an Android port example. We compile the already pinned VINS-Mono core
  instead of substituting that port's old camera transport or device parameters.
- [OpenVINS sensor calibration guidance](https://docs.openvins.com/gs-calibration.html)
  and [Yang et al., online self-calibration and degeneracy](https://arxiv.org/abs/2201.09170)
  explain online refinement and motion observability. Full parameter calibration
  requires sufficiently excited motion; simple planar motion can leave parameters
  ambiguous. A short ordinary walk is not a universal replacement for calibration.
- Android [CameraCharacteristics](https://developer.android.com/reference/android/hardware/camera2/CameraCharacteristics)
  can expose factory intrinsics and poses, subject to camera support and coordinate
  conventions. The retained Redmi front-camera capture exposes no factory lens
  intrinsics. Do not substitute a focal-length guess and call it factory calibration.

## New participant versus new phone

A new participant on an already calibrated phone needs the ordinary posture,
stillness and fit checks, not another board/alignment/noise session. The baseline
model runs automatically on the stored quiet interval. It belongs to the device
and recording, not the participant's stroke profile.

An unfamiliar phone still needs a verified device/optical profile. A future
cross-device learner needs a labeled multi-phone calibration collection and
held-out-phone validation, including different lens windows and timing pipelines.
We have not acquired such a collection or trained that learner. The next sensible
step is manufacturer-supported calibration plus observable online refinement,
with an explicit unsupported-device result when the necessary information is absent.
The app must not claim that an arbitrary room scan establishes metric accuracy.

## Few-shot request: audited training feasibility (9 October)

The intended experience is rapid enrollment: a new phone observes a few views
and brief motion, stores its profile, and reuses it for every participant. The
current Bayesian bias adjustment does not implement that learned enrollment.

A fresh manifest audit covers local research ZIPs and the user's supplied
Downloads captures. It finds 52 manifest-bearing archives but only 25 distinct
capture IDs: **17 physical captures on one Xiaomi M2101K6G installation**
(6 calibration, 10 distance, 1 noise), plus 4 synthetic controls and 4 adapted
historical main-flow replays. All 16 physical camera captures contain an IMU
stream. Duplicate archive copies and replay adapters do not create new training
tasks. This audit is limited to available manifest-bearing ZIPs, not a claim that
all gait exports or potential research material have been inventoried.

The existing recordings are useful for a same-phone pilot and comparison against
the saved candidate calibration. They do not support a held-out-phone test. A
random split of neighboring video frames would leak the same phone, lens and
scene into training and evaluation. Saved solver estimates are proxy labels;
the reported route lengths provide endpoint checks, not full reference
trajectories. Self-supervised learning can use unlabelled sequences, but this
does not establish transfer or remove the need for independent physical checks.
No calibration network was trained in this audit.

### Proposed learned enrollment experiment

1. Start from a broadly pretrained camera model. [GeoCalib (ECCV 2024)](https://github.com/cvg/GeoCalib)
   estimates intrinsics/gravity from images and supports shared intrinsics over
   multiple images. Its default principal point is fixed at the image center;
   its distortion models do not directly replace our five-coefficient Brown
   calibration. It supplies an initialization candidate, not camera/IMU timing,
   sensor extrinsics, or metric-distance validation.
2. Benchmark zero-shot and few-view estimates on whole held-out captures from
   this phone against the saved candidate profile. Report errors, uncertainty,
   failures and window occlusion; fitting to the existing profile is a
   same-device transfer experiment, not independent calibration validation.
3. Obtain additional device/optical profiles with reference calibration and
   measured walking checks. Train a small calibration residual/uncertainty head
   across device tasks while freezing most of the pretrained encoder. Keep
   support views separate from query clips; hold out entire phones and routes.
   Compare against the pretrained model, saved-profile reuse and ordinary
   geometric refinement before claiming a benefit from few-shot learning.
4. Adapt supported parameters from a short capture using visual/IMU residuals
   and motion-observability checks. Request only the missing motion/view when
   evidence is insufficient. Store an accepted profile; do not repeat enrollment
   for a different participant. Clip duration and required views must be measured,
   not advertised as a guaranteed few seconds in advance.

This hybrid is a plausible engineering direction, not an implemented model or
accuracy promise. [Visual-inertial self-calibration research](https://arxiv.org/abs/2201.09170)
shows why insufficient motion can leave parameters unobservable. A learned prior
can assist initialization; it cannot create absent physical information.

The Face ID analogy concerns enrollment experience. Apple's system uses a
TrueDepth depth map and infrared data, with neural processing; it is not learning
an arbitrary phone's metric camera/IMU calibration from a few RGB pictures.
See [Apple's technology explanation](https://support.apple.com/en-us/102381).

Executed inventory and GPU checks are saved in the existing calibration notebook.
GeoCalib source commit `97b8968e7798a66bf04fcf791fb535624241bda7` and its released
`distorted` pretrained checkpoint were obtained locally (ignored dependencies).
A fresh CUDA experiment used five evenly spaced measured-motion frames from each
of three retained walking captures, without feeding the saved calibration into
the model. Shared-image estimates were compared afterwards with the saved
candidate's mean focal length of 494.6972 pixels:

| Retained capture suffix | Estimated mean focal (px) | Difference from candidate | Desktop GPU calculation |
| --- | ---: | ---: | ---: |
| 1791468615419 | 490.8471 | -0.778% | 1.752 s |
| 1791468384841 | 494.2123 | -0.098% | 0.784 s |
| 1791468160915 | 483.7885 | -2.205% | 0.812 s |

These are same-phone candidate-parameter comparisons, not distance errors,
independent truth, held-out-device accuracy or Android latency. GeoCalib performs
shared-intrinsics geometric refinement over learned image predictions. Its neural
weights were frozen: this is pretrained few-view inference, **not training a
few-shot model on our recordings**. The scene/window setup and prior development
use of these recordings preclude calling them a pristine final test. The simplified
distortion and centered principal point cannot simply overwrite our full lens
profile. Its reported internal uncertainty is not empirically calibrated here.

The first Windows PyTorch import reported an Application Control error; a normal
retry loaded CUDA and the experiment completed on the RTX 5060 Laptop GPU. No
policy was disabled. Missing inference dependencies were installed only inside
ignored `android/dist/few-shot-feasibility/inference-deps`. An intermediate
notebook assertion assuming that the import would fail is retained with the
successful subsequent experiment; it is not a model failure. No application
behavior, native APK, OTA or source publication changed for this experiment.

## Reproduce the enrollment/training pipeline

Launch `android/Start phone calibration.cmd` on the paired computer. The launcher
prepares local GeoCalib dependencies/checkpoint and runs actual inference kernels
before advertising quick-enrollment availability. It prefers the existing
`C:/Users/frank/.venv-cu130/Scripts/python.exe`; an alternative compatible PyTorch
interpreter can be selected with `GAITTRACE_LEARNED_PYTHON`. A new computer needs
PyTorch/torchvision compatible with its GPU plus the existing Docker/WSL iKalibr
setup. This is not a zero-dependency cloud service. Model/runtime/source pins are
checked; downloads and captures remain ignored, never committed. GeoCalib source
and license are retained with the downloaded checkout (Apache-2.0).

Reusable implementations: `rapid_calibration.py` (capture contract/orchestration),
`rapid_calibration_worker.py` (real frame selection/GPU prior/quality),
`few_shot_calibration.py` (dataset tasks, first-order MAML focal head, training,
candidate-label inference), and `src/rapidCalibration.ts` (app transfer/import).
Orchestrate training in `notebooks/phone_camera_imu_calibration.ipynb`: call
`load_examples` on enrollment bundles or helper `training-example.json` files,
choose validation/test **hardware models before training**, call `task_partition`,
then `train`. Generated weights/reports stay under a versioned local `android/dist/`
directory. A trained focal-head artifact cannot replace a camera/IMU profile.
Labelled support adaptation still requires a solver-derived support label;
unlabelled scene views do not supply timing, lever arm or independent metric truth.

Method foundations: [GeoCalib, ECCV 2024](https://github.com/cvg/GeoCalib),
[iKalibr, IEEE T-RO 2025](https://github.com/Unsigned-Long/iKalibr), and
[MAML, ICML 2017](https://proceedings.mlr.press/v70/finn17a.html).
The implemented focal head is a limited experimental first-order adaptation of
the MAML approach; neither its gait-distance accuracy nor its cross-phone
performance is established by those publications.

## Existing phone-engine build and evidence

The module's Gradle build enables OpenCV Prefab and CMake. CMake fetches pinned
VINS-Mono, Ceres 1.14 and Eigen sources into ignored build directories; the source
tree must include `research/vio-reference` shims/wrapper. See the module's
`THIRD_PARTY.md` for licensing and corresponding-source requirements before release.

The complete local 0.3.12/build-24 APK packages successfully, including the JNI
engine, OpenCV and embedded JavaScript. This verification package uses an Android
debug certificate; it cannot update the installed release app. A release-signed
APK remains pending. 224 app tests, 94 research tests, TypeScript and web export
pass. Saved noise calibration is also verified after raw-report removal.

ARM64 library/AAR compilation, actual JVM input preparation and a host execution
of the exact Android C++ frontend/runner are software checks. The latter replays
retained data; it is not a phone speed, temperature or prospective accuracy test.
The executed notebook is `notebooks/phone_camera_imu_calibration.ipynb`. Local
artifacts are in `android/dist/phone-vio-native/` and `android/dist/gait-main-native/`.
An updated native APK is required; OTA cannot add this library. Main-camera
throughput, actual JNI execution, processing time, thermal behavior and phone
storage/relaunch behavior still require the installed APK on a physical device.
# 10MWT boundary unification — 10 October 2026

Build 28 saves `ten-metre-boundaries-v1` from the production live monitor:
the Go origin, initial route direction and interpolated 1/11/12 m timestamps.
Saved processing verifies these against accepted poses and uses the saved times
for `10 / (t11 - t1)`. It no longer substitutes an endpoint-derived direction.
Missing/altered evidence withholds timed-zone speed. Older offline processing
remains identifiable and unchanged. The initial pose must precede Go by no more
than 0.2 s; it is a sampled origin, not an exact interpolated pose at Go.

Java-to-TypeScript replay uses a controlled trajectory with small lateral drift,
which would previously produce different endpoint and initial directions.
All crossings agree; five corrupted/missing-evidence controls reject the timed
zone. This is software validation, not measured floor-crossing accuracy.

