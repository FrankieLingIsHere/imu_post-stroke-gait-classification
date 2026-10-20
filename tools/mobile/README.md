# Workspace Android interaction lab

Current first-use controls (20 October): study IDs are automatic; the smoke command validates required age rather than a missing ID. On an uncalibrated phone, use the explicitly labelled **Record motion only** path for SDK-only recording checks. This does not supply camera distance or bypass its quality gate. `first-use-setup.json` verifies the calibration entry; `research-recording.json` completes a synthetic practice recording and opens the saved signals. `type` values may include `{runId}` for a unique lab identifier; `set-switch` sets a declared true/false value instead of blindly toggling. Historical full-duration clinical scripts require their saved synthetic participant fixture and are not newly validated by these first-use checks.

For completed recordings, all walk types and exact reproducible controls, use
[APP_ACCEPTANCE.md](APP_ACCEPTANCE.md). The smoke command alone is not full-flow
acceptance. `clinical-scenarios.cjs` exercises native IMU recording routes;
`verify-recordings.cjs` checks their saved files. Controlled tracked-10MWT
software replay remains separate from physical camera distance validation.

The lab runs an actual Android 11 operating system and installed APK, controlled
through Appium 3.8.0 / UiAutomator2 8.7.0. It is available from the workspace root
without connecting a phone. The dedicated serial is **emulator-5560**; scripts
never select the first connected device. Appium listens only on localhost:4725.

## Start and reuse

Double-click **Start Android test lab.cmd**, or run from the workspace root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/mobile/mobile-lab.ps1 -Action Start
powershell -NoProfile -ExecutionPolicy Bypass -File tools/mobile/mobile-lab.ps1 -Action Status
powershell -NoProfile -ExecutionPolicy Bypass -File tools/mobile/mobile-lab.ps1 -Action Test
```

The Test action defaults to `android/dist/emulator-lab/GaitTrace-emulator-x86_64.apk`.
Use `-Apk <path>` for another compatible GaitTrace build. For other apps, use
`interact.cjs --package <package.name> --scenario <file>` with their own labels;
the smoke test's assertions are specific to GaitTrace. GaitTrace's ARM-only phone
APK installs on this image but its Hermes loader crashes under ARM translation;
use the x86_64 build rather than treating that crash as a Redmi failure.

After changing app code, rebuild the emulator package with:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/mobile/build-lab-apk.ps1
```

The build uses production source and an x86_64 ABI, reuses existing pinned native
dependency source, and places CMake intermediates at `%USERPROFILE%/.gait-mobile-native`
to avoid Windows path-length failures. It does not sign a phone release, update
release provenance, publish OTA, or install anything on a physical phone.

To open an interactive emulator window, Stop the headless emulator first, then
Start with `-ShowWindow`. Stop closes only this emulator; Appium remains available.
Status reports its actual Android ABI and Appium readiness. Setup reinstalls the
downloaded tools if missing, using the existing Android SDK command-line tools.
Environment variables apply to the script process, not your global Windows setup.

## Inspect replies and drive interactions

```powershell
node tools/mobile/interact.cjs source
node tools/mobile/interact.cjs tap --label "Start a walk"
node tools/mobile/interact.cjs type --label "Study ID or participant label" --value "EMU-DEMO"
node tools/mobile/interact.cjs back
node tools/mobile/interact.cjs home
node tools/mobile/interact.cjs resume
node tools/mobile/interact.cjs rotate --value LANDSCAPE
node tools/mobile/interact.cjs font --value 1.3
node tools/mobile/interact.cjs font --value 1
node tools/mobile/interact.cjs sensor --label acceleration --value "0:9.81:0"
node tools/mobile/interact.cjs sensor --label gyroscope --value "0:0:0"
node tools/mobile/interact.cjs sensor --label magnetic-field --value "25:0:-45"
```

Each command captures a screenshot, UI XML and reply JSON under ignored
`android/dist/emulator-lab/interactions/`. Labels must match the selected language.
The smoke test saves a per-step report, screens and logcat in `android/dist/emulator-lab/`.
Actions include `tap`, `type`, `back`, `home`, `resume`, `rotate`, `scroll`, `font`,
`sensor`, `assert` and `source`. To replay a workflow, save an array of these actions
as JSON and use `--scenario <file>`. Example:

```json
[
  {"action":"tap","label":"Start a walk"},
  {"action":"tap","label":"Continue"},
  {"action":"assert","label":"Enter an age from 1 to 120."},
  {"action":"back"}
]
```

## Evidence boundaries

### Verified scenarios and repeatable permission fixture

The initial native run passed 11 smoke checkpoints: installed ABI, Home,
recordings, participants, dashboard, preparation, required ID/age responses,
Android keyboard entry, background/resume, research navigation and virtual sensor
availability. The camera-permission scenario also passed denial, app error,
retry/grant and cancellation back to Home. Platform controls passed three sensor
set/readbacks and larger font. Landscape refusal is an explicitly expected
response because GaitTrace locks portrait, not a successful landscape transition.
These are the scenarios tested, not a claim that all recording/export flows pass.

Repeat the platform controls with:

```powershell
node tools/mobile/interact.cjs --scenario tools/mobile/scenarios/platform-controls.json
```

Permission denial counters persist in Android 11. The explicit fixture command
below **discards only GaitTrace's virtual installation/data**, reinstalls the lab
APK and runs the permission scenario. Use it for disposable emulator data only:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/mobile/mobile-lab.ps1 -Action PermissionTest -ResetVirtualApp
```

Ordinary Test and interaction actions retain the virtual app's data. Neither
fixture changes the physical phone or its recordings.

The emulator can exercise actual touch/keyboard UI, required fields, OS permission
dialogs, navigation, background/resume, rotation, font scaling, virtual sensor
inputs and camera API startup/failure. These are stronger platform checks than
browser previews, which remain available through `npm run test:sandbox` in android.
Existing production Java and component tests provide deterministic timing,
speech-completion and distance-boundary controls alongside the emulator.

No single tool simulates every phone faithfully. The emulated camera is not a
calibrated, synchronized visual walking trajectory; virtual IMU values are not
patient measurements. A successful emulator interaction does not establish
audible TTS, Redmi OEM behaviour, thermal performance, anatomical placement or
clinical distance accuracy. The initial smoke test is navigation/intake/lifecycle
coverage, not every recording/export scenario. Expand explicit scenarios as
features change and retain failed runs.

Official references: [Android console and virtual sensors](https://developer.android.com/studio/run/emulator-console),
[hardware acceleration](https://developer.android.com/studio/run/emulator-acceleration),
[Appium UiAutomator2](https://github.com/appium/appium-uiautomator2-driver).

Downloaded SDKs, driver dependencies, AVD user data, APKs, screenshots and logs
stay in ignored `android/dist/` or the local native cache. They are not source
commits. Tests use a separate virtual installation, not your phone's recordings.

## Recording-list and action-area layout review

The emulator-only build disables preview OTA loading, so UI checks use its embedded source bundle rather than a cached update. Phone release update configuration is unchanged. Build metadata records `previewOtaEnabled: false`; the build verifies the merged manifest.

From English Home, replay `node tools/mobile/interact.cjs --scenario tools/mobile/scenarios/list-layout-review.json`. It sets 720x1280 and font scale 1.3, checks content/action rectangles, opens recordings and the export/delete panel, selects/clears all, and checks preparation/audio settings before restoring the display. `assert-readable-layout` uses the first content and last action ScrollViews and records their rectangles. `assert-recording-visible` checks a visible recording entry; Android clips reported rectangles to the viewport, so it does not prove the entire card is visible.

Use `tap-scroll` for controls within long content. Reset font to 1 and display size before ordinary smoke checks; small-screen settings can legitimately move inline Home controls below the fold. Every operation targets emulator-5560, and failures/screenshots remain local.

`audio-control-layout.json` checks the TUG preparation sound/readiness page at the same constrained size: choose the saved synthetic participant, continue, choose TUG, continue, scroll to Play voice sample, stop the sample if still playing, then check the sample and Start test controls. This proves control reachability, not audible or complete TTS.

Interaction replies include the installed base APK SHA-256. `verify-usability.cjs` requires that hash, the current build time and the exact scenario controls, so an older installation cannot satisfy the current-package acceptance report.

The lab restores its temporary merged update manifest in `finally`, invalidating the altered Gradle output so future phone builds regenerate their normal enabled-update configuration. The restoration helper was exercised on the generated manifest and an idempotence fixture. For `tap-scroll`, bounded searches use a shorter implicit lookup and may add one positioning scroll when a control touches the content boundary. `scroll` accepts optional `percent` (0.1 to 1); the audio replay uses 0.2 after the sample label changes size. Reported Android element rectangles can be clipped; inspect the retained screenshots rather than treating bounds alone as full visibility.

## Phone calibration preflight

From English Home, run `node tools/mobile/interact.cjs --scenario tools/mobile/scenarios/setup-preview-startup.json`. It checks framing before calibration, actual voice sample completion, native capture startup and cancellation. Read captured logs and pending tracking states; it does not assert numerical calibration completion.

`setup-voice-unavailable.json` requires an explicit missing-TTS emulator fixture. Use the SDK adb with `-s emulator-5560` to `shell pm disable-user --user 0 com.google.android.tts`, force-stop/reopen GaitTrace, then replay the scenario. Always `shell pm enable com.google.android.tts` in finally, even after failure. Never apply this fixture to a physical phone. A failure from a still-working engine is an invalid absence fixture, not an app regression. APP_ACCEPTANCE.md records exact tested folders and remaining evidence limits.

## Android numerical calibration lab

Build the separate test package with `powershell -NoProfile -ExecutionPolicy Bypass -File tools/mobile/build-calibration-replay.ps1`. It compiles production Java sources and copies the unchanged x86_64 JNI libraries from the current app lab APK. It installs only as com.gaittrace.calibrationlab on emulator-5560; it is neither a patient APK nor a test-input hook in GaitTrace.

Run the Android JNI setup proof cells in notebooks/phone_camera_imu_calibration.ipynb with the existing gait-cu130 kernel. The reusable calibration_replay.py module renders synchronized analytic scenes through the existing OpenCV environment and captures actual Android JNI responses. It retains timestamped attempts, including failures. A shell exit code alone does not establish an instrumentation pass; the module reads the current instrumentation result and assertion. Normal completion, slow views, missing-axis recovery, optical distortion/occlusion, noise, camera-prior variation, permanently missing axes and blank-scene rejection are covered.

To replay saved native states through the production React setup component, from android/ set GAITTRACE_ANDROID_SETUP_PROOF to the final-proof evidence directory, run `node --test tests/onDeviceSetup.test.cjs`, then remove the variable. Hash-checked engine/profile values are captured results; speech/bridge callbacks are controlled. This is layered software evidence, not one live Camera2/TTS session or physical calibration accuracy. See APP_ACCEPTANCE.md for current outcomes, numerical bias and remaining evidence gaps.

## Calibration-bias investigation

The existing `notebooks/phone_camera_imu_calibration.ipynb` orchestrates `calibration_audit.py`: parameter-group host ablations, retained source/library hashes and separate frozen-profile motion checks. The oracle-alignment diagnostic cannot be deployed on an unknown phone. No route scale is fitted. Current audit found remaining bias; the automatic held-out admission stage is not implemented in GaitTrace. Read the latest acceptance section before claiming calibration success.

The Android numerical replay now checks emulator free space and removes only its own `/data/local/tmp/gait-setup-*` input copy after retaining outputs and input hashes on the computer. Prior ENOSPC logs remain saved. A partially completed suite cannot report success. Never clear the patient app to repair numerical-lab storage.
