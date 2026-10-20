# GaitTrace release history

## 0.3.19 / Android build 31 (local first-use and setup feedback correction)

- Generate pseudonymous study IDs in walking setup and participant creation; retain optional worker overrides and returning-person selection.
- Preserve an explicit motion-only alternative without measured camera distance; reset test-selection panels to the top.
- Check for compatible phone setup before participant entry for automatic distance, return to the draft after calibration, and retain inputs after a late missing-profile check.
- Consolidate participant details behind a named action, show an automatic ID without a manual input on the main page, tint secondary buttons and keep action icons readable.
- Announce movement directions once; explain measured optical/alignment/timing uncertainty, native capture duration, stale/slow frames and changing fits. Preserve all admission thresholds and the open-ended capture.
- Suppress obsolete queued guidance after native completion, preserve speech completion and prevent a final-complete display before the native movement clock finishes.
- Signed ARM64 package, matching certificate/runtime and embedded versions verified locally. No Git push or OTA publication; actual phone convergence, distance and novice/elderly usability are not established by software tests.

## 0.3.18 / Android build 30 (local collector package)

- Package compact recording/assessment navigation and the current multilingual setup guidance.
- Show a front-camera framing/voice check before capture; acknowledge measured movement directions and let slow users continue without the normal 120-second cutoff.
- Correct display-axis guidance and Camera2 crop/pixel-centre optical priors.
- Restore upstream visual outlier rejection (chi-square multiplier 1); keep FEJ, pixel noise and readiness bounds unchanged. Controlled bias is reduced, not eliminated.
- Sign with the existing release certificate and bump app/native version consistently. New native runtime requires one APK installation; compatible subsequent OTA updates remain supported.
- Existing records and saved calibration are not recomputed by installation. Physical ARM64 launch, audibility, distance, OEM and elderly usability remain unverified. Local only; no Git/OTA publication.

## 0.3.17 / Android build 29 (local collector package)

- Package the latest collector workflow: explicit test selection, returning-participant confirmation, required assessment-first review and separate Tools panel.
- Add persistent field labels, stronger input outlines, pinned participant identity and compact export format selection. Language choices wrap on narrow displays.
- Group worker measurements and optional observations; restore unfinished drafts and keep users on the screen after a save failure. Raw sensor streams remain unchanged.
- Include whole-recording signal overview, import cancellation/progress and provisional-stop warning/resume behaviour from the latest local UI batch.
- Signed ARM64 package and fresh runtime/bundle identity verified. Software checks pass; physical launch, audio and distance evidence remain separate. No publication.

## 0.3.16 / Android build 28 (local candidate)

- Unify 10MWT automatic stopping and saved speed around one native origin,
  walking direction and interpolated 1 m, 11 m and 12 m crossing record.
- Verify saved crossing evidence against continuous accepted poses; withhold
  timed-zone speed if evidence is missing or inconsistent. Historical offline
  results retain their original processing path.
- Include the pending quiet-first setup, tracker lifecycle and personal standing
  reference repairs. Stable natural lean is accepted; raw IMU axes remain intact.
- Software tests do not establish physical distance accuracy or clinical validity.
  Native changes require a new APK; no publication is implied by local packaging.

## 0.3.15 / Android build 27 (local candidate)

- Restore the actual estimator movement-start transition after completed guidance.
- Give guided setup its full 50-second movement interval, replacing the premature
  generic 40-second cutoff; incomplete guidance fails at the separate safety limit.
- Log capture completion clocks and genuine sample counts for physical diagnosis.
- Add production clock and estimator-handoff controls. Physical setup and distance
  acceptance remain pending; no new OTA or publication.


## 0.3.14 - real IMU startup handoff (build 26)

Fixes the physically observed rolling-shutter coverage failure at camera startup.
Early accelerometer/gyroscope samples are replayed after actual camera metadata
constructs tracking. Only initially uncovered images may be withheld (bounded
one second/20 frames), preserving raw observations and recording diagnostics.
Later coverage failures still stop tracking. Saved timing offsets apply from
startup. Native Java/Kotlin change requires one in-place APK update. Signed local
APK, fresh fingerprint, update identity and existing certificate verified; 244
app tests, TypeScript, 47 transport and 617 contract assertions pass. Installation
and successful physical setup/distance acceptance remain pending. No publication.

The approved build-25 OTA 01a12167 is physically active; its initial speech
completion callback was verified before capture. It cannot deliver this native fix.

## 0.3.13 - setup reliability and corrected native runtime (build 25)

Includes completed-utterance gating, safe cancellation/retry, saved phone setup
reuse and the clearly labelled computer-reference section described below.
Home's app title now consistently says GaitTrace. The native tracking method,
camera orientation and saved calibration binding are unchanged.

Physical setup follow-up: the first scan stopped when Android's permission
activity briefly paused the app. The compatible JS fix now waits for permission
and foreground return before speaking/capturing, reuses existing camera grants,
and preserves cancellation during active capture. All 241 app tests and
TypeScript pass. The original installed build-25 bundle does not contain this
follow-up until the corrected local package or an approved OTA is installed.
No native version change is required for this fix. The first incremental package
reused its embedded update ID and Expo loaded cached JavaScript. Regenerated
update resources with fresh ID `03e822a3...` and added an APK identity guard.
The real stale-ID package is rejected and the fresh package passes. Verify the
active update ID before physical retesting. The Redmi now shows 03e822a3 with its
exact installed APK verified. A cold speech-engine race stopped the first cue;
a warm retry completed the cue but native capture failed during startup. Added
bounded empty-voice readiness polling and native error diagnostics in JS.
TypeScript and 244 app tests pass. These latest compatible changes remain local;
successful setup and walking acceptance are still pending.

Approved compatible preview OTA **01a12167...** now delivers the cold-voice
readiness fix and native capture-error diagnostics to runtime `89e68fa8...`.
Published `2026-10-09T16:03:40.034Z` from the verified Android export; no new assets,
native code or raw captures uploaded. Active OTA and capture remain pending.
No Git push was performed. This does not establish calibration/distance accuracy.

Build 24's cached fingerprint did not match a fresh calculation from its source.
Rebuilt update resources and packaged a signed build 25 with runtime
`89e68fa8d1cbc1bfcd7133a318d7f10da6a42364`. Its actual APK fingerprint matches
fresh source computation; manifest, signature, channel, bundled fixes and ZIP
integrity pass. The certificate matches builds 23/24. A corrected installation
is required once, preserving local records and profiles. OTA publication now
checks the source against `releases/current-native.json` before sending an update.

TypeScript, all 238 app tests and all 10 browser flow tests pass. Native ARM64
assembly succeeds. Connected Redmi inspection confirms build 24 launches and
Android exposes all three IMU sensors. Build 25 is now installed and launches on
that Redmi. Its pulled APK digest and runtime match the verified local package;
Android retains the original installation date. Full voice and measured walking
acceptance remain pending. No push or OTA publication.

## 0.3.12 - local phone-only camera distance (native code 24)

### Local setup reliability follow-up - 9 October 2026

Setup now requires the speech engine's completed-utterance callback before
starting capture, beginning movement or enabling Continue. Failed voice cues
stop the attempt. Cancellation waits for native capture to stop; stale permission,
speech and capture completions cannot advance a retry. If native stop fails,
another capture is blocked with a restart instruction. Cancelling speech clears
its completion watchdog so an old timeout cannot interrupt a new prompt.

A matching saved profile offers **Use saved phone setup**. Home distinguishes
phone-only setup from **Advanced research tools (computer required)**. New text
is translated in English, Malay and Chinese. These JavaScript changes keep
0.3.12/native code 24 and require publication before an installed app receives
them. No new APK, OTA or Git push was issued for this follow-up.

Verification: TypeScript, all 238 app tests, all 10 Playwright browser flows and
Android Hermes bundle export pass. Speech completion is tested at callback
boundaries, not by listening on a physical phone. Build 24 installation is
user-confirmed; mounted distance and physical performance remain unchecked.

### Local phone-only implementation - 9 October 2026

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
OTA or public release publication has occurred. The [phone checklist](research/DISTANCE_PHONE_CHECKS.md)
sets out the remaining checks.


## 0.3.11 - distance trial practice, boundaries and noise review

- Integrated corrected computer processing: normal launcher explicitly selects fixed-time row compensation and a continuous native quiet initialization window, with a separate built/tested engine. Version/source/backend plus noise-profile digest identify jobs and preserve old reports. Fresh full-service replays and actual TypeScript import/save/reopen pass; blank synthetic footage withholds distance. 83 research tests and 250 factor cases pass. Existing build 23/calibration unchanged; no new APK or prospective/clinical accuracy claim.

- Desktop investigation: fixed-time VINS branch was skipping row-timing correction. Added an explicit opt-in wrapper correction and 250-case regression against the pinned upstream factors; default/live executable remain unchanged. Fresh saved-capture candidates improve the latest measured 3 m result from 3.24120 m to 3.15688 m, but one of four reported measured attempts still fails. Added pose-discontinuity rejection using the existing 3 m/s plausibility bound. Placement-prefix exclusion is a notebook experiment, not an active helper feature. 74 research tests, actual CTest and fresh analytic control pass. No clinical validation, new APK, push or OTA.

- Documentation/navigation-check follow-up: the checklist now starts with Home's **Import, research tools and app information**, identifies Research tools as a heading, explains scrolling to Research capture tools and lists EN/MS/ZH labels. Version/build marker is in expanded Home below Storage, not Settings. Two actual-component navigation checks pass. No app-code/native change or replacement APK for this correction.

- Native research trial separates placement, fully spoken practice cue, practice movement/return to start, fully spoken measured cue, first-motion start and automatic quiet-stop. No walking produces a retained no-walk capture, never a zero-distance result. Sensor arrival order cannot falsely invalidate a fresh gyro/magnetometer sample.
- Saved geometry/time stay fixed in the pinned VINS replay. Finishing standing time is excluded from distance; excessive standing drift, resets, gaps, partial tracking and incompatible route geometry withhold the full estimate. Straight routes use horizontal endpoint displacement; turns use a separately labelled smoothed horizontal path. These are research measures, not clinically validated distance or automatic clinical-test boundaries.
- Five-minute stationary sensor capture transfers to the paired computer for short-term noise review. Only matching phone/device/pipeline candidates can supply per-sample measurement noise; long-term bias random walk remains provisional. Existing saved calibration is preserved.
- EN/MS/ZH practice, route choices, no-walk and noise-feedback wording. Raw ZIP plus result JSON remain exportable; failed processing can retry the saved ZIP.
- Fresh full HTTP/ZIP/estimator/actual-TypeScript negative control passes: blank footage returns not-initialized, not zero distance. The freshly executed non-gait analytic VINS control maintains 559 initialized poses, rigid-only position RMSE 0.0003602 m, no fitted scale. Synthetic controls do not establish physical accuracy.

**Current native target: 0.3.11 / build 23.** Build 22 was superseded before release by the final translation and sensor-order fix. Build 21 was an unused remote version reservation. Build 23 is compiled and verified; artifact details follow. A new APK is required for the native boundary API. No source push or OTA publication has occurred.

Physical acceptance checklist: [research/DISTANCE_PHONE_CHECKS.md](research/DISTANCE_PHONE_CHECKS.md).

**Verified APK - 8 October 2026:** 0.3.11/build 23 finished successfully (`d64795ab-4667-455a-b6dd-113fb99759f1`). ZIP integrity, compiled version/package, runtime, new native practice/end-boundary API, bundled EN/MS/ZH guidance and cryptographic Android signature pass. Certificate matches build 20, supporting an in-place update. [Download build 23](https://expo.dev/artifacts/eas/L8EFVUNHKT1E4voE2EAAORAoVj3Z_mfykV_a0HqcaA0.apk). Local file: `android/dist/apk/GaitTrace-0.3.11-build23.apk` (233,387,998 bytes). SHA-256: `dc09ab82650aef3817cfff4ad6304cf0c136aa2e6cf606529b4ed9583008abf5`. Runtime: `9bc3827992f3c583d878767addc04dae0f3d3081`. Organized local release evidence: `android/dist/releases/0.3.11-build23/`. Physical checks remain; no source push or OTA publication.


## 0.3.10 - local distance validation / permanent storage cleanup

- Complete fresh camera/IMU processing validation: CPU 600.68 s / GPU-assisted 326.94 s including export on one retained capture. Exact experimental build import support added; all readiness flags remain false. Saved phone calibration and production defaults unchanged.
- Desktop-only experimental CUDA Ceres/iKalibr build and two-per-backend real-capture comparison: median final solve 355.09 s -> 139.07 s, all stages converge. Numerical parity fails, so existing CPU defaults/profile are preserved; repeatability is recorded. No new APK or clinical distance claim.
- Desktop-only fastest measured CPU default, archive import and batched Linux log/result transfer (353-frame replay 10.74 s -> 8.06 s, identical computed states). Four-thread calibration benchmark is faster but fails strict parity, so the two-thread default is retained.
- Desktop-only CUDA corner/LK worker, verified startup kernels, persistent context/cache, Linux replay storage and per-stage provenance. No further APK needed after build 20. Measured warm CPU tracking remains faster than CUDA for the retained 353-frame/150-feature capture; VINS/iKalibr remain CPU. GPU support is not a claimed universal speedup.

- Saved iKalibr reference -> separate native raw trial -> paired-computer pinned VINS processing, with result JSON and partial/reset rejection. New APK required.
- Research tools reduced to Phone calibration and Distance validation; retired experimental screens removed from navigation.
- Selectively delete recordings/videos, or clear all recorded data and large research/export/import files without an app backup. Profiles and compact calibration remain.
- EN/MS/ZH interface coverage; reference-length persistence and resume/retry processing.
- 200 app tests, TypeScript, 64 research checks and Android export pass; actual non-gait VINS control executed. Physical distance accuracy remains unvalidated.

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


## 0.3.9 - guided calibration rounds (local, unpublished)

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

## 0.3.8 - superseded build

Build 17 was canceled. Do not install it for the staged calibration fix.


## 0.3.7 - calibration stall diagnostics (local, unpublished)

Build 16 completed successfully on 7 October 2026 (EAS
25ba329b-f230-4886-822d-e92b4c4e5ee8). Downloaded and verified local APK
`android/dist/apk/GaitTrace-0.3.7-build16.apk`: 233,377,958 bytes, SHA-256
4dac96ebed6f72daf1f65f61e8ca591c6333bfce534f5f5ced68f2affd21e562.
Native compilation, APK ZIP integrity, package/version, new sampling/stall/fitting/
saving/diagnostic code markers, camera permission, absence of microphone
permission, four OpenCV ABIs, licences and fingerprint
963b7871e24e5231cb07b5ade36c7ac3676be518 verified. A replacement APK is required.
No physical freeze-resolution or clinical accuracy pass is claimed. Source
publication remains pending review; the APK and generated proof stay local.


Prepared replacement build 16 after the operator reported both previews freezing
and repeated clear-view failure. Lens-only image selection now happens before
YUV conversion/JPEG/storage at a maximum of 4 Hz, matching the existing detector
interval. Intentional omissions are counted separately from queue drops. Walking
and camera/IMU alignment retain their original acquisition path.

Fitting and saving have explicit phone/computer states. A 15-second absence of
camera images stops lens capture with a camera-stalled error. Timeout errors name
missing view count, angle/position coverage, failed fit or unfinished fitting.
The capture retains corner counts, coverage spans and fit rejection diagnostics;
Export calibration attempt includes failed attempts after reopening. All new
phone wording has Malay and Chinese translations. Existing lens admission gates
and previous-profile preservation remain unchanged.

190 app checks, TypeScript, Android export, 43 research checks and desktop Java/
OpenCV checks pass. The lens known-answer residual remains 0.1593 px held-out p90.
These are software checks. No physical freeze resolution or metric accuracy is
claimed. Native runtime changes require a replacement APK; build 15 cannot receive
the full repair by OTA. Git publication awaits review of this new scope.

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
