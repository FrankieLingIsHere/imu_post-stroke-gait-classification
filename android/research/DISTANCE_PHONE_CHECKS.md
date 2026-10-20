# Remaining physical phone checks

## Local investigation replaces repeated phone checks — 10 October 2026

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

The following hardware lists are **deferred acceptance criteria and historical notes**,
not a request to reconnect, reinstall or repeat a scan. An accepted local end-to-end
new-phone setup is needed before any further physical acceptance is proposed.

## Checks for the release candidate

1. **First phone setup:** open a fresh installation with no imported calibration
   and no connected computer. Choose Start test; if setup is missing, the app
   opens **Set up this phone** automatically. Alternatively use Home > Import,
   research tools and app information > **Set up this phone**.
2. Tap **Start phone setup** while holding the phone in its usual bag. Face its
   front camera towards a bright furnished room. Hold still until the voice
   tells you to move. Then gently move it in small loops and tilt left/right/
   up/down. Listen until **Phone setup saved**. No board, measured walking
   distance, pairing or transfer is involved. This happens once per phone/window,
   not once per participant. An unsuccessful fit must preserve the old setup.
3. Choose a participant and **10MWT**, leaving **Phone distance** on. Secure the
   phone horizontally at the lower back, screen/camera facing out. Follow the
   voice through placement and fit checks. Wait for Go, then walk the straight
   marked **0 / 1 / 11 / 12 m** course. Stop safely at the finish and keep the
   phone mounted until Finished. Estimated tracking triggers capture completion;
   floor marks independently test whether it occurs at the right place/time.
4. Check Result > **Phone distance**, recording signal plots, participant history
   and the required G.A.I.T. form. Check raw JSON/CSV and camera/IMU ZIP if a
   tester needs to report a fault. Ordinary use requires no export or computer.
5. Also check a standing/rest interval, obscured/blank camera view, poor lighting,
   backgrounding, denied permissions and restarting. These must not invent
   distance or a successful clinical endpoint. Repeat on other supported phones.
6. Measure error, successful and rejected trial counts, start/finish timing,
   processing latency, battery/heat and EN/MS/ZH guidance. Numerical setup alone
   is not anatomical placement verification or independent accuracy validation.
7. Check TUG and 2MWT duration/flow separately. TUG chair contact is still
   provisional. Resting must not pause endurance clocks. Check deletion of
   selected/all records and research captures; the reusable setup should remain.

Clinical acceptance tolerances must be agreed before calling the app clinically
ready. Do not treat the earlier 3 m / 30 cm pilot as that release threshold.
See [the implemented method and limitations](ON_DEVICE_DISTANCE.md).

## Historical board-free developer checks (local build 24)

This needs the forthcoming **release-signed 0.3.12/native code 24 APK**.
The locally packaged test-key APK cannot update the existing release app. Do
not uninstall your current app just to try it; that would remove saved data.

1. On this computer run **android/Start phone calibration.cmd**. It prepares the
   pinned learned camera model, executes a GPU readiness check when available,
   and opens the local pairing page. Both devices must share the same Wi-Fi.
2. On the phone: **Home > Import, research tools and app information > Phone
   calibration > Quick phone setup (experimental)**. Tap **Connect computer**
   and scan its pairing code. Keep **Capture through the usual waist-bag window**
   selected, using the actual holder/window throughout setup and later walking.
3. Tap **Capture scene and sensors**. Hold the bagged phone still facing a
   furnished room. After the voice finishes, move it gently in small loops and
   tilt left/right/up/down for the guided scan. No target, square measurement,
   printing, walking distance entry or screen tap during capture is needed.
   Keep furniture in view; a blank wall/dark room is unsuitable. Allow about
   one minute of capture. The retained full-chain replay took about **20 minutes**
   of desktop processing; timing varies. A stand-in front-camera recording or changing bag optics is not valid.
4. The computer display must switch to **Board-free scene enrollment**, without
   asking for coded squares. Its texture diagram is only a display hint. The
   profile is checked after capture; this is not a live calibrated-angle counter.
5. A passing result offers **Use experimental profile**. Select it deliberately.
   Failures should keep the existing profile and expose **Retry saved capture**
   or a specific recapture hint. Try leaving/reopening during processing, then
   **Resume quick processing**. Voice instructions must complete before motion.
6. Tap **Export enrollment bundle**. Send the ZIP unchanged: it contains
   `input.zip` (real frames/IMU), `result.json`, and `training-example.json`.
   A raw-only failed capture is still useful for debugging but is not a labelled
   training example. The helper also retains the upload/result on the computer.
7. Turn the computer off and test the ordinary **Camera distance (experimental)**
   recording path. Keep the mounted phone untouched until Finished. A short
   measured 3 m research walk can test processing; use the actual 12 m course
   for 10MWT (0/1/11/12 m marks). A distance-validation helper trial alone does
   not prove on-phone processing. Export gait JSON and camera/IMU ZIP as well.
8. Note phone model, app/native code, scan success/rejection, desktop processing
   time, phone processing time, heat, tracking success, and independently measured
   route length. Use the **same lower-back/phone reference position at both marks**;
   do not compare a toe at start to a heel at finish. Include failed runs, not
   only successful estimates. The model must not use the measured length as scale.
9. Repeat setup once on each phone to provide a second physical enrollment,
   then compare its measured walks. Different users reuse a phone profile.
   Different phone/camera/window/installation requires its own profile. Raw
   research cleanup must retain the reusable profile but remove capture copies.

The future focal-head trainer requires at least **five different hardware models,
two physical enrollments per model**, with three training/one validation/one test
model. This is an engineering admission minimum, not a clinical validation sample.
It never counts frame splits, copied archives or metadata replays as new phones.
Current app enrollment uses the frozen pretrained model and physical refinement;
it does not yet use our own cross-device-trained few-shot network. Accuracy,
compatibility and reliability remain experimental until these trials are reviewed.

## Historical main-pipeline developer checks - 0.3.12 / native code 24

A new **signed APK** is required; the build-23 link below does not contain this
engine. Full local APK packaging passes with a test signing key; no release-signed
build-24 APK has been published. Do not install the debug-signed verification APK
over the existing release app.
Existing saved calibration/noise are reusable. Extra 3 m repeatability trials
remain deferred for the prototype; clinical accuracy is not established.

1. Install the forthcoming 0.3.12 APK over the current app, preserving its data.
   Confirm the version/native code in expanded Home app information.
2. **Leave the computer off.** Do not repeat board/alignment/noise calibration.
   A new participant on this phone uses the same saved device calibration.
3. Choose ordinary **Start test**, participant and test, then enable **Camera
   distance (experimental)** on **Choose your test**. Grant camera permission.
4. Mount horizontally at the lower back with the front-camera window exposed.
   Follow the usual stillness/fit voice checks. The short sensor-baseline model
   runs automatically; no extra calibration action is needed.
5. For **10MWT**, use marks at 0, 1, 11 and 12 m: 1 m to build pace, 10 m measured
   section, 1 m to slow down. Wait for Go, walk to the final mark, stop and remain
   still until the finish voice. No phone tap is needed to finish recording.
6. Open Result/Details. **This phone is calculating distance** should appear.
   Keep the app open. The result must arrive without Wi-Fi/helper access. Phone
   processing duration is not yet benchmarked. The single rule remains complete
   tracking plus integrity checks, otherwise distance unavailable. Estimated
   central-zone timing is experimental and is not a live distance stop.
7. Check TUG chair-to-chair boundaries and timed-test rests. Recording must retain
   IMU if camera storage/tracking fails. Observe phone heat and battery usage;
   no all-phone or six-minute runtime guarantee is claimed yet.
8. Retry a saved calculation using **Calculate saved distance** or **Resume distance
   processing** without rewalking. Check relaunch recovery and correct participant,
   worker notes and mandatory G.A.I.T. linkage. Export JSON, features CSV and the
   camera/IMU ZIP if a check fails; include the displayed message.
9. Delete a selected recording (or all recorded data). Its camera ZIP, raw frames
   and generated phone-processing files should disappear. Saved calibration and
   participant profiles should remain.

Remaining physical checks: actual Android JNI execution, camera/three-sensor
concurrency, complete audio and native start/end timing, processing duration,
thermal/memory/storage limits, sharing and relaunch. Host replay is not an
Android benchmark. See [method and calibration limits](ON_DEVICE_DISTANCE.md).

## Historical separate-trial checklist (build 23)


[Download verified build 23](https://expo.dev/artifacts/eas/L8EFVUNHKT1E4voE2EAAORAoVj3Z_mfykV_a0HqcaA0.apk). Local APK: `android/dist/apk/GaitTrace-0.3.11-build23.apk`. Build/signature/guidance verification is complete.

The software pipeline is prepared for a research trial. Distance accuracy is **not yet validated**. This is separate from clinical 10MWT/TUG and does not automatically stop those tests at a measured distance. The computer calculates this research result after capture.

## Prepare once

These are the labels in the installed **Android APK**, not the browser preview. **Research tools is a heading, not a separate menu button.**

1. On **Home**, tap **Import, research tools and app information**. Scroll the page if needed. This expands the **Research tools** section containing **Phone calibration** and **Distance validation**. The small selectable **GaitTrace v… · build …** marker is also inside this expanded section, below **Storage**; it is not in Settings. Confirm **v0.3.11 · build 23**. If necessary, install the linked APK over the existing app without uninstalling or clearing data.
2. Restart `android/Start phone calibration.cmd`. Keep computer and phone on the same private Wi-Fi. In the expanded Home section, tap **Distance validation**, then **Connect computer**, and scan the setup code on the computer. Return to Home. Existing saved calibration should load; do not repeat the board capture unless the camera, holder/window or optical setup changed.
3. In the expanded Home section, tap **Phone calibration**. Scroll down its main content to the text button **Research capture tools**, then tap it. **Sensor noise** is already selected in build 23; tap that tab if needed. Tap **Measure sensor noise (5 min)**. Leave the phone untouched on a firm table, app visible and screen awake. It saves automatically, speaks completion and sends the capture to the paired helper. If sending fails, use **Check saved sensor noise**, without recording again.

If your app language differs, look for these actual translated labels:

| English | 中文 | Bahasa Melayu |
| --- | --- | --- |
| Import, research tools and app information | 导入、研究工具和应用信息 | Import, alat penyelidikan dan maklumat aplikasi |
| Research tools (heading) | 研究工具 | Alat penyelidikan |
| Phone calibration | 手机校准 | Penentukuran telefon |
| Research capture tools | 研究采集工具 | Alat rakaman penyelidikan |
| Sensor noise | 传感器噪声 | Hingar sensor |
| Measure sensor noise (5 min) | 测量传感器噪声（5分钟） | Ukur hingar sensor (5 min) |
| Distance validation | 距离验证 | Semakan jarak |

If these controls are absent after expanding Home, check the build marker there before repeating any calibration. This checklist targets build 23.

Noise pass: a matching completed capture is returned and displayed as a short-term noise candidate. A rejected/review-required report must remain visible as such. This five-minute test does not establish long-term bias random walk, camera accuracy or clinical validity. If your actual phone filtering prevents a white-noise fit, export that capture for review; do not change noise values manually.

## Earlier proposed three-trial repeatability check (deferred for prototype)

**Software handoff complete (8 October).** The corrected local helper is active.
Complete service replays and the actual app import code pass, but measured
distance is not yet prospectively validated. The latest confirmed saved 3 m
walk gives **3.15688 m (+5.23%)**; one retained trial still fails. The altered-start
trial is excluded. Do not count these development replays as new repeatability tests.

**Keep build 23 and the existing calibration.** No new APK, board capture or
five-minute noise measurement. The supplied noise capture is already registered.
Open the computer's pairing page and reconnect through **Distance validation >
Connect computer** if needed. The standard `Start phone calibration.cmd` now
enables the correction and quiet initialization automatically. Exported result
JSON should contain `software.processing.mode: fixed-time-rows-quiet-v1` and
`noise.initialization`; a successful estimate does not make `distanceReady` true.

Mark a straight **3 m** path. Align the **same foot landmark**, for example toes,
at both lines with the same facing direction and similar standing posture. After
practice, return to that exact start. Perform the following flow three times,
keeping the phone in the same bag position and keeping every result, including
Unavailable. When transfer works, reports are already on the computer; no manual
export is needed. Tell the reviewer the route length and any overshoot, movement
of the starting point, early handling or interrupted guidance.

From **Home > Import, research tools and app information > Distance validation**, choose **3 m / Straight route**, then tap **Start distance trial**.

1. Secure the phone horizontally at the lower back, screen/front camera outward, in the usual bag window. Stand still; follow the spoken practice cue.
2. Practice a few comfortable steps, turn and return to the **start mark**, then stand still. Practice is excluded from the measured walk. Returning to the correct mark requires the person; the app cannot recognize that mark.
3. Wait for the **complete measured-walk instruction**, ending with **Begin walking now**. Only then walk to the finish mark. The measured boundary starts on fresh motion, not on the countdown or while standing.
4. Stand still at the finish until **Finished**. The phone ends capture automatically after a quiet interval; do not tap Stop or remove the bag early. A pause of roughly four seconds will also end this short research trial.
5. Let the paired computer process the capture. Check the result returns automatically and survives reopening the page. **Unavailable** is a legitimate failed trial, not a zero-metre measurement.

Record each displayed estimate/error and whether the cue/first-motion/quiet-stop behavior matched what happened. Export **distance trial ZIP** and **result JSON** for each attempt; the capture IDs must match. The paired helper also retains uploads/results in ignored `android/dist/calibration-processor/` job folders, so there is no need to manually tune or transfer parameters.

If the three 3 m trials track completely, try three **2 m** and three **5 m** straight trials. Then try a separate **Route with turns** trial: 1.5 m outward plus 1.5 m back = **3 m total**. Turns assess path tracking only; they are not a standardized straight 10MWT. Keep the camera window/holder unchanged.

Predeclared *engineering feasibility* target for this small pilot: every straight trial has complete tracking and absolute error no greater than `max(0.20 m, 10% of marked length)`. Report all failures; never select only successful trials or tune scale against these route labels. Passing nine trials would justify broader validation, not a clinical accuracy claim. Turns require separate review because trajectory smoothing can shorten corners.

## Flow and recovery checks

- **No walking:** finish practice and its return, then remain still after the measured cue. After about 25 seconds, hear no-walk feedback. The capture must be saved without a distance estimate.
- **Voice/languages:** try EN/MS/ZH. Each preparation/practice/measured/finished instruction completes, is not repeated, and matches the displayed stage. The phone can remain at the lower back after tapping Start.
- **Camera/throughput:** the bag's obstruction, room lighting, actual camera timestamps, dropped frames, sensor rates and moving-image feature coverage must be inspected in the exported physical captures. A clear-looking preview alone does not pass these checks.
- **Interrupted capture:** background/lock or intentionally stop one trial. It must retain an interrupted capture and withhold a complete-route estimate. Keep the app visible/awake during normal tests.
- **Network/processor interruption:** disconnect Wi-Fi after saving, or stop the helper while processing. Restore it and use Resume/Retry. The same ZIP should be reused without repeating the walk; no conflicting route length/shape should appear after reopening.
- **Storage cleanup:** after copying test files you wish to retain, delete selected recordings and then clear all recorded data. Reopen the app and check files/recordings are gone, other selections were preserved where appropriate, and participant profiles plus compact saved calibration remain. Externally shared Downloads/computer copies require separate deletion.

## What is already checked without phone hardware

The actual native Java boundary class runs on the JVM for placement, audio barriers, practice movement/stillness, first-motion start, finishing-pause exclusion, no-walk timeout, stale sensors and time limit. Actual React screens and TypeScript contracts are exercised with injected hardware/storage; the live local HTTP service, ZIP parsing, noise analysis, actual VINS executable and actual TypeScript upload/poll/import code are exercised with labelled synthetic controls. Retained physical ZIPs were also freshly replayed diagnostically; their missing legacy holder/pipeline identity prevents treating them as validation of the newer saved calibration. None of these replaces the physical checks above.
