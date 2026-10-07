# GaitTrace release history

## 0.3.6 - guided published calibration and local reference processor

Published 7 October 2026 as source commit `2cce693`. Repository hygiene, web
publication and compatible Android update workflows all passed. First functional
update: `01a115df-b6e0-7bf6-9760-2c02061813e8`, group
`f8b8e064-3577-4ad3-af1e-ceac9ade2d97`, channel `preview`, runtime
`e1383287be615da4c75a7a9ce08b9260cfd2cfb3`. The actual client manifest is verified.
This is compatible with build 15; earlier native builds need its replacement APK.
Subsequent documentation-only updates can change the displayed update ID while
retaining the same app code/runtime. APKs, captures and generated/demo assets
remain local/ignored. Physical usability and distance validation are unverified.

Local follow-up: computer-only lens calibration is the default. The computer
displays the stationary board and a mirrored live framing diagram derived from
real phone frames, so the operator can move the bagged phone while watching the
computer. Native accepted-view count and voice prompts appear alongside it;
EN/MS/ZH speech follows the selected mode. Temporary board loss retains views.
The supported-phone/moving-tablet method remains explicitly optional. A saved
profile offers Repeat lens check. Preview JPEGs are processed transiently over
the private LAN; the companion never saves a preview or returns its JPEG to the browser. Framing cannot
admit calibration. Fixed a worker race so job completion follows durable save.
188 app and 43 research checks pass; actual companion/browser checks verify
computer framing/board layout and optional tablet layout using a synthetic image
and simulated counts. Android export passes. The Android
fingerprint remains build-15-compatible. This follow-up arrives through the
published compatible update; it is not in the original APK bundle. Physical
usability is unverified.

Phone calibration now selects clear, diverse ChArUco views and runs the published
Zhang method through native OpenCV 4.12. Successful lens parameters save
atomically and match the device/camera/pipeline/optics. Failed captures preserve
the previous profile. A generated digital board needs no print or ruler for
this lens-only phase. Optional Android factory fields are exported for audit,
never certified as a full camera/IMU calibration.

The new computer launcher supports QR pairing, automatic board display,
50-second voice-guided sensor alignment, local ZIP upload and automatic retrieval
from the pinned iKalibr authors' reference executable plus standard COLMAP. Inputs
use actual Camera2/SI IMU clocks. All three raw sensors remain retained, though
iKalibr does not use magnetometer data. Reference results are research-review
candidates, not admitted to metric distance or clinical auto-stopping. The
complete noise model and physical accuracy remain unverified.

The local companion selects a pinned official CUDA COLMAP worker for feature
extraction/matching when NVIDIA Docker support is installed. GPU failures retain
diagnostics and explicitly fall back to CPU. The published iKalibr executable
and its final calibration solver remain unchanged and CPU-only. Frankie's WSL
runtime now exposes the RTX 5060; actual feature/matcher logs show GPU execution.

185 app checks (including spoken-phase completion, cancellation and translated
prompts), 40 research checks and 10 browser flows pass. Actual native lens JNI
controls pass; retained calibration replay correctly fails coverage. These are
software/development checks, not new participant or clinical validation. Build
14 failed Android's checked JSON-exception compilation; explicit declarations
correct the issue. Replacement build 15 completed and its APK is verified. Native changes require a
build-15 APK; this native verification preceded the publication recorded above.


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

## 0.3.5 - native acquisition and sensor-noise preparation (local)

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


## 0.3.4 - profile readiness and native map renewal (local)

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

Scoped Git attributes preserve native-module bytes across Windows builds and
Linux OTA jobs. Post-change local fingerprint matches the build-11 runtime.

## 0.3.3 - in-app camera distance research trial (local)

Adds a separate native research screen and Java/OpenCV fixed-map tracker/metric
scale calculation. One-time phone research-profile import, unhurried placement,
fresh sensor stillness, completed spoken start cue, motion start and quiet stop.
Rejected tracking/scale retains raw images and all three sensors. ZIP includes
capture-result times, per-frame diagnostics, research profile and app release
identifiers. Estimates remain experimental camera-path segments, not clinical
whole-course distance/speed or a 10MWT stopping criterion. Full calibration and
independent physical validation remain pending.

172 app checks, TypeScript, Android bundle, native Java compilation and five
desktop OpenCV JNI known-answer checks pass. Second real bench-capture replay
rejects tracking after one map pose; no successful real walking result claimed.
Native OpenCV/Commons Math dependencies require a new APK; licenses/notices are
included as assets. Build 9 was an intermediate compilation check; final build
10 includes release provenance and notices. Final build 10 completed successfully
on 7 October 2026 (EAS e2cfa528-ebff-4062-ada1-c8591516d09c), runtime
037f976718a2d2ef78c79b8705adeb04596f072c. Downloaded APK is verified as
com.gaitsteps.app 0.3.3/versionCode 10, with intact ZIP, native tracker, four
OpenCV ABIs and bundled licenses. Local artifact:
`dist/apk/GaitTrace-0.3.3-build10.apk` (233,322,474 bytes), SHA-256
`2cc0ff8d10f96c2644ee483e0865ac209d3b2deb7204b4a28189762c3f5b248c`.
No source Git push or new OTA. Install over the existing app to preserve the
phone installation identifier and calibration/profile binding.

This file records source releases and installation requirements. `app.json` declares the application version; EAS assigns the Android build number. Actual installed release/runtime/update identifiers come from `src/releaseInfo.ts` and are included in recordings. Do not infer an APK build number from the application version or promise an APK before its build succeeds.

## Local research processor update - 6 October 2026

No app version/runtime change or OTA: added per-corner rolling-readout camera/gyro
fitting, contiguous translation screening, fixed-map visual tracking and metric
scale initialization with explicit rejection conditions. Second real capture
passes only internal rotation/timing gates (1.1594 px held-out RMS); first
moving-tablet capture fails. Full translation calibration remains unavailable,
and the visual prototype loses tracking on the second bench capture. Android
distance/stopping behavior is unchanged; camera distanceReady remains false.
Executed research outputs and synthetic checks are recorded in the existing
calibration notebook; raw captures/generated reports remain local.

## 0.3.2 build-8-compatible calibration ZIP save fix (published OTA)

Fixed native/expo URI aliases (file:/ versus file:///) causing copyAsync to copy a ZIP onto itself in the same durable document directory. Nonempty native ZIPs are indexed directly; separate cache files are copied and checked. Page loading recovers unindexed ZIPs from native manifests, preferring the newest valid capture and preserving interrupted/error status. No raw images/IMU/ZIP contents are changed and no distance calibration is invented. Four regression tests reproduce self-copy, cache persistence, missing/empty files and orphan recovery. TypeScript, 165 app tests and Android Metro export pass. Native runtime remains 0894d523161346acbefbbe6ac62b46e3a244f31f (build 8); OTA can deliver the fix without a new APK. Published by explicit user approval on 6 October 2026: Android preview OTA 01a11195-6294-7fba-93b2-b6eb1f075a52 (group 00541cb9-c847-468e-9f68-5ab0c2942d5c), runtime 0894d523161346acbefbbe6ac62b46e3a244f31f, compatible with 0.3.2/build 8. Server-side update and active preview-channel mapping verified. Installed device receipt and recovery remain to be checked. Source Git publication remains unapproved/pending; no Git push made.

## 0.3.2 / Android build 8 - researcher phone calibration

Local implementation, source/OTA publication pending user review. New Camera2/SensorManager module requires a new APK. EAS build 32cf3ae5-0e74-4e38-a043-61d6e38ace08 submitted with versionCode 8 and runtime 0894d523161346acbefbbe6ac62b46e3a244f31f; native compilation finished successfully on 6 October. APK: [GaitTrace 0.3.2 build 8](https://expo.dev/artifacts/eas/yvJNaow1lQ2JkAVjAl0kDUy_oCW74eO9yW-Ukkj1WUA.apk). Local copy: android/dist/apk/GaitTrace-0.3.2-build8.apk. ZIP integrity, compiled version/package, native calibration class and CAMERA without RECORD_AUDIO permissions verified (95,595,245 bytes). Physical calibration remains pending.

- Research tools > Phone calibration: one 40-second researcher board capture, actual frame previews, native frame/exposure/skew timestamps and raw three-axis accelerometer/gyroscope/magnetometer in SI units. Cancellation preserves an incomplete ZIP. No participant creation or clinical recording.
- Export ZIP; process locally using notebooks/phone_camera_imu_calibration.ipynb; import an accepted geometry report on the originating phone/configuration. Reuse per phone, not per patient. Individual standing/postural reference remains separate.
- Geometry fitting screens lens, camera/gyro rotation and timing, lever arm/accelerometer consistency. Invalid captures, inadequate excitation, missing timing, wrong phone/pipeline and claimed distance readiness are rejected. Passing geometry never means validated distance; no VIO estimator or automatic distance stop added.
- Includes simplified camera trial and required worker assessment from the pending build-7 source batch. English/Malay/Chinese researcher prompts. TypeScript, 161 app tests, seven Python numerical/admission checks and Android Metro export pass; real calibration/holder distance validation remains pending.

## 0.3.1 / Android build 7 - simultaneous front-camera/IMU trial

Local simplification, not yet published: removed the long briefing and default duration choices. One tap starts placement, followed by a short walking cue. Four fresh quiet seconds after movement automatically finish the camera trial; 60 seconds is the default fallback limit. Clinical rest rules are unchanged. Technical result text/settings are collapsed, exports stay visible, and EN/MS/ZH cues are short. 157 tests, TypeScript and Android export pass. Build-7 native runtime is unchanged; publication is pending.

Local 6 October implementation, source publication pending review. Adds native expo-camera 16.0.18; a new APK is required for installed build 6. EAS build c1bee024-4f46-40e3-b060-06a3a0e3524e was submitted, with runtime 33936923bf8f867ab7acf5673f6214eab56383c9. Native build succeeded on 6 October 2026. APK: [GaitTrace 0.3.1 build 7](https://expo.dev/artifacts/eas/90IBQ9OxX_SCTnJWkkC53P_LVX1pruOhiQMFVQoqDlM.apk).

- Separate Android Research tools > Camera + IMU trial. One tap records real front-camera video and all three native IMU streams; full placement guidance, five settled seconds and a completed walking instruction precede fresh-movement start for a 15/30/60-second walking window. Rests are included; capture stops automatically. No fixed 20-second placement deadline. Backgrounding, camera failure and early stopping retain partial sensor data.
- Muted, uncropped video in private phone storage; in-app camera permission and blocked microphone permission. Matching-ID MP4 and JSON exports include native IMU timestamps and monotonic stage events. Actual camera start/frame timestamps and calibrated clock offset remain unavailable; vioReady is false. No camera distance estimator or paid API is added.
- English/Malay/Chinese patient prompts and speech. Camera trials are practice experiments, excluded from clinical review requirements and rehabilitation trends. Includes the required English G.A.I.T. worker wizard below.
- 153 deterministic/controller/UI tests, 10 browser workflow checks, TypeScript and Android Metro export pass. Hardware responses in automated tests are injected; physical concurrent capture/timing remains unverified.
- Downloaded APK ZIP integrity and compiled manifest were verified: com.gaitsteps.app, version 0.3.1, versionCode 7, CAMERA present and RECORD_AUDIO absent. Local artifact: android/dist/apk/GaitTrace-0.3.1-build7.apk (95,571,477 bytes). Generated APK and verification reports remain ignored.

## 0.3.0 preview updates - October 2026

- Local 6 October: required G.A.I.T. observer review for real gait recordings, unfinished-first queues, dedicated item-card wizard with paper-order overview, draft/resume/navigation-save and explicit JSON/feature CSV readiness. Patient UI remains multilingual; the entire clinical worker form uses English by user agreement. Original scoring choices and missingness are preserved. No native/dependency change; installed build-6 runtime compatibility verified. Publication pending scope review.

- Local 4 October complete observer G.A.I.T.: supplied 31-item/62-point form with assessor/limb/context, all scoring branches, qualifiers and item notes; JSON import/export, feature CSV and dashboard totals. Development-only Flow Lab and Playwright UI checks; 138 unit/flow tests, six browser checks, TypeScript and Android export pass. Runtime fingerprint remains build-6 compatible. Original scoring criteria remained English; interface translations were not clinically validated. Published in source 4d268d3 with Android preview OTA 01a10777 on the build-6 runtime; worker language policy is updated above.

- Local 4 October intake parity: setup now captures weight, stroke type/location and pre-existing gait/orthopaedic notes in participant snapshots; feature CSV includes both baseline-note fields. Three-language prompts and per-test clinical source links. TypeScript, 134 tests and Android Metro export pass. Compatible JavaScript change, published with source 4d268d3 and OTA 01a10777.

- Separate Research tools > Quick Google API check; no participant, placement, countdown, gait recording or deliberate post-stop wait.
- Checks native availability/permission, subscription, detailed reads over recent 60-second and 600-second context windows, and cleanup. Empty successful replies pass API access while records remain unavailable. Context counts are never walking distance. Four-second request timeouts and late-subscription cleanup are included.
- EN/MS/ZH messages and structured technical logging (`GaitGoogleApiCheck`) for connected-device inspection. Waving is not a walking accuracy test.
- TypeScript, 126 tests and Android Metro export pass. Native runtime matches build 6: `a48c2ed43ddd2142beaa39b7f8031b8fff327407`. No native or dependency changes; compatible OTA `3ccb972` was published and loaded on the installed build-6 phone. Existing clinical and short-trial capture timing is unchanged.
- Live Redmi Note 10 Pro check on 2 October 2026: availability, subscription, 60-second read, 600-second read and cleanup all passed in about 0.3 seconds; both reads returned zero records. This verifies API access, not walking distance or step accuracy. The result was visible on the phone without scrolling.
- Short-trial diagnostic: the final delayed read also queries a wider post-finish context window in parallel. Its raw points and polling outcome are exported as diagnostics only; no context value enters trial distance, steps, speed or stopping. This cannot force Google to produce records, and physical validation is still required.
- Separate Google trial option: measured 5 m out and 5 m back (10 m total) with one comfortable turn, spoken three-language guidance, eight-second quiet finish and 90-second fallback. The route pattern survives JSON/CSV export and import; it remains a practice distance experiment, not a clinical 10MWT. Published in `8e553c3`; Android preview OTA workflow passed on 2 October 2026. Physical Google-distance response is still untested.

## 0.3.0 / Android build 6 - short Google distance trial

- Separate Android research-tool entry for tape-measured 2, 3 or 5 m routes, default 3 m; no clinical test selection or 12 m course required.
- Existing participant, permission and phone-fit checks are retained. After the spoken Begin cue, raw recording starts at the first detected step and finishes after four consecutive seconds of stillness. A 60-second limit is a safety fallback, not a distance endpoint.
- Google queries start at the audible Begin callback (first-step fallback) and retain a fixed end boundary. Delayed reads observe for up to 30 seconds plus request time after walking; missing records remain unavailable.
- Result confirmation distinguishes reaching the measured finish from an early stop. Dedicated JSON export and labelled CSV metadata preserve reference length, completion and stop reason. Practice tagging excludes these experiments from rehabilitation trends; no participant distance calibration is overwritten.
- English, Malay and Chinese trial instructions. TypeScript, all 123 tests and Android/web Metro exports passed. Published source commit `54fb0f4`; EAS build `d3529b4c-e5f5-443c-9a15-01e4f7286bc8` succeeded on 2 October 2026. APK: [GaitTrace 0.3.0 build 6](https://expo.dev/artifacts/eas/5sYVRhaXoeMJQDYTPrjgfXq7aSLe2wTlboCAzbZFoqU.apk). Runtime `a48c2ed43ddd2142beaa39b7f8031b8fff327407` matches the published preview update. Actual-holder accuracy and installation trials remain pending.

## 0.3.0 — 2 October 2026

**APK status: built successfully, Android build 6.** EAS build `d3529b4c-e5f5-443c-9a15-01e4f7286bc8` contains the Google native module. This is the same `com.gaitsteps.app` application, not a separate test app. The new native Google module requires a new APK; JavaScript updates cannot add it to build 5 or Expo Go. Retain the existing signing identity when building an update to preserve the installed application and its local data. Fingerprint runtime policy separates incompatible native versions.

### Changes

- Opt-in Google on-device Recording API distance/step comparison using Play services Fitness 21.3.0, with activity permission requested before mounting. No Google account, Fit OAuth or paid service was added.
- Provider record intervals, first-seen and poll timing, missing/partial/error results and subscription-cleanup diagnostics. Google data stays separate from raw IMU, clinical reference outcomes and stopping logic. JSON retains detailed evidence; raw and feature CSV include Google comparison columns.
- Explicit clinical history for clinical-test setup, participant linkage and saved profile snapshots; unknown history is not fabricated.
- Five-second standing baseline, participant-paced setup and hands-free clinical capture. Timed endurance tests finish automatically; 10MWT/TUG movement-then-quiet stopping remains provisional and cannot verify course crossings or chair contact.
- Protocol-aware experimental phone speed, including timed rests, and separate optional measured-reference entry. Whole-walk estimates are not central-zone 10MWT speed.
- English, Malay and Chinese instructions, experiment controls and result messages.

### Verification and limits

TypeScript and 117 automated tests passed. Android/web Metro exports, native-module autolinking, SDK API-symbol checks and whitespace checks passed. Native compilation subsequently passed in EAS build 6; physical-device validation remains pending. Google distance accuracy, short-test availability and reporting delay require actual-holder trials. No clinical accuracy claim or automatic Google-distance endpoint is enabled.

Build/use/validation instructions: [Google Recording API experiment](modules/gait-google-recording/README.md).

## Previous source version: 0.2.0

The app configuration preceding this release declared 0.2.0. Earlier implementation history is retained in [README.md](README.md) and Git history. No verified historical version-to-APK-build mapping is recorded here; check the installed app or EAS build record for its actual build number.

## File organization

- `CHANGELOG.md`: maintained release history and native-install requirements.
- `app.json`: application/native configuration and fingerprint update policy.
- `package.json` and `package-lock.json`: matching package version and reproducible dependencies.
- `eas.json`: remote build numbering, signing/build profile and update channel.
- `src/releaseInfo.ts`: installed native and Expo update provenance.
- `dist/`: ignored publication reviews, exports and verification output. A publication review is not the release history.

Keep APKs, local dependencies, SDK binaries, demo video assets and generated review artifacts outside source commits.

Local 4 October form navigation: explicit Gait assessment form entries in results and saved summaries; direct expansion on review, three-language labels. Existing observer outcome form is not a complete standardized G.A.I.T. instrument. TypeScript and 134 tests pass; unpublished.

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
