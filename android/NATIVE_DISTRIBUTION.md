# Installable Android app

## Current release configuration

GaitTrace 0.2.0 uses the existing application ID and signing key so it can upgrade the first APK. EAS owns the monotonically increasing Android build number. The local legacy versionCode is not the authoritative installed number; the UI uses expo-application. Fingerprint policy separates incompatible native runtimes. JSON appRelease records the actual native version/build, runtime, channel and OTA update ID at capture.

An initial update is already published to preview and its endpoint was checked: HTTP 200 and the expected update ID for the matching Android runtime. This verifies server delivery, not installation on a physical device. The first 0.1.0 APK cannot receive it because it did not bundle expo-updates.

### Enable publication from GitHub

The local workflow `.github/workflows/publish-android-update.yml` publishes compatible Android updates after checks on approved main-branch app changes. It is not active until committed/pushed and the secret is configured.

1. Create an Expo access token in the owning account's dashboard: https://expo.dev/settings/access-tokens . Do not paste it into chat or commit it.
2. In GitHub repository Settings > Secrets and variables > Actions, add a repository secret named `EXPO_TOKEN` with that token.
3. Review and publish the workflow/source batch. Subsequent main changes under android trigger it; workflow_dispatch can publish explicitly.
4. A change of native fingerprint needs a new APK built with `eas build --platform android --profile preview`. Publishing an unmatched update alone does not update older binaries.

Until CI is enabled, the logged-in maintainer can publish with `npx.cmd eas-cli@latest update --platform android --channel preview --environment preview --message "Describe the change" --non-interactive` from android. A Git push by itself does not publish an OTA without that workflow.

Physical checks: [PHYSICAL_DEVICE_VALIDATION.md](PHYSICAL_DEVICE_VALIDATION.md).

Use the same `/android` source for native collection and web review. The `preview` EAS profile explicitly disables the development client and builds an internal-distribution APK. The APK contains the JavaScript bundle and assets and runs without Metro, Expo Go, or the developer's computer. Each phone must have functioning accelerometer, gyroscope and magnetometer streams. Availability and actual rate are checked at runtime, not guaranteed by installation.

Maintainer commands from `/android`:

```powershell
npx.cmd eas-cli@latest login
npx.cmd eas-cli@latest init
npx.cmd eas-cli@latest build --platform android --profile preview
```

Login is interactive: do not put passwords or tokens in source. `init` links an actual project to the signed-in account, and its returned project ID must be retained in config. Review the generated signing credential and retain access to it for future upgrades. No project ID or signing key is invented here. Cloud build uploads the application source to Expo. The download link is available after a successful build. Share it with testers, who download/install the APK and may need to allow installation from their browser. The phone can then record offline, with locally available speech voices.

GaitTrace 0.2.0 enables EAS Update on preview with fingerprint runtime compatibility. Updates check on cold launch, download in the background, and apply on a later cold launch. No forced in-session reload is implemented. Native dependency/config changes need a new APK. Remote Android build numbers auto-increment; the human-readable app version is bumped deliberately for releases. Git pushes only publish updates after the new workflow is pushed and a repository EXPO_TOKEN secret is configured.

References: https://docs.expo.dev/build/internal-distribution/ and https://docs.expo.dev/build-reference/apk/ . A Metro bundle export verifies bundling only, not APK compilation or physical sensor performance.


## [2026-09-21] Standalone Android build started

Expo account verified and project linked to @frankielingishere/gait-steps (3db4ae90-2d4d-41f9-9689-f70f656ac581). Cloud signing key generated and the current /android source uploaded (19.9 MB). Internal preview APK build e3466fa0-35f7-4f16-8c85-a240fa757573 has now finished successfully. No Git push or clinical validation. This supersedes the earlier account-login blocker; build completion is confirmed below.


## [2026-09-21] Standalone Android APK completed

EAS build e3466fa0-35f7-4f16-8c85-a240fa757573 finished successfully. Package com.gaitsteps.app, version 0.1.0 (1), SDK 52, internal preview release with developmentClient disabled. [Download APK](https://expo.dev/artifacts/eas/xAT-b9nZQhbSiJ3grrY6aKqeXL2JnqRIOFU2x94rP-0.apk). [Build details](https://expo.dev/accounts/frankielingishere/projects/gait-steps/builds/e3466fa0-35f7-4f16-8c85-a240fa757573). The app runs without Metro or the developer computer. Installation and physical three-sensor tests remain pending. No Git push was performed; automatic over-the-air updates are not configured.


## [2026-09-21] GaitTrace branding, updates and versioning

Display name changed to GaitTrace, with a rendered two-shoe teal/cream launcher icon and matching PWA branding. Stable Expo slug and Android package are preserved. Version 0.2.0, remote auto-incremented Android build 2. Fingerprint runtime and preview update channel configured. Initial OTA group 9a909628-c9e5-4804-a76c-0f7d1d19a98e published with Android update ID 01a0c240-c412-7c6f-b19b-d40607a329b3. Runtime ead45ff05f56ff8de69ce960cb9af9126a4cc015 matches replacement APK build 44f1af5a-436e-4613-82a0-66dd7f9bc99b. APK compilation completed successfully; current download below. Home/footer and recording JSON carry release identifiers. No forced reload during recording. GitHub OTA workflow prepared locally; needs publication and EXPO_TOKEN repository secret. Physical validation checklist is android/PHYSICAL_DEVICE_VALIDATION.md. Automated TypeScript and 73 tests pass; physical update adoption remains pending.


## [2026-09-21] GaitTrace 0.2.0 build 2 ready

Replacement APK build 44f1af5a-436e-4613-82a0-66dd7f9bc99b completed successfully. [Install GaitTrace 0.2.0 (2)](https://expo.dev/artifacts/eas/L7skC5kknzsTjhhW1TFZiX2pHnAfzgDiBMRO0UDHJWo.apk). This supersedes the earlier 0.1.0 download for sharing. Update server returned HTTP 200 with the expected update ID on the matching runtime. Physical install/update and sensor validation are still pending. Source/workflow publication and GitHub EXPO_TOKEN configuration remain outstanding; initial OTA was published directly through the authenticated Expo account.
