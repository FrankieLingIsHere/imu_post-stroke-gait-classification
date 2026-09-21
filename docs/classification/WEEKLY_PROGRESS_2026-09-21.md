# Week of 21 September 2026

App acquisition update prepared locally: explicit browser sensor-check consent, realistic 60/60/50 Hz web requests, horizontal lower-back belt gating, gravity-projected direction reminders, and optional baseline-relative comparison signals in JSON while retaining raw data. See [sampling and placement protocol](../../android/SAMPLING_AND_PLACEMENT.md). Dataset resampling and model evaluation remain proposed, not executed. Physical validation and publication are pending.


## [2026-09-21] Sampling audit executed and native distribution selected

New notebook 39 executed a paired rate-reduction audit on existing local development data: 161 included Voisard participants and 166 Felius participants. The coverage ledger retains 96 Voisard packet-gap exclusions and two short/invalid-bout exclusions. No new raw data acquisition, classifier training, synthesis or clinical evaluation. Median 8 Hz-band waveform error was 5.30/8.82% at 25 Hz and 1.31/2.31% at 50 Hz for Voisard/Felius respectively. Preserve higher acquisition rates; 25 Hz is not universally validated. The app adds experimental candidate interval alternation, never a neurological or verified bilateral symmetry verdict. The user selected a standalone native Android APK after the PWA restriction was explained. EAS profile linked to the signed-in personal account. APK built successfully; physical validation pending. See [audit](PHONE_SAMPLING_AND_ASYMMETRY.md).


## [2026-09-21] Standalone Android build started

Expo account verified and project linked to @frankielingishere/gait-steps (3db4ae90-2d4d-41f9-9689-f70f656ac581). Cloud signing key generated and the current /android source uploaded (19.9 MB). Internal preview APK build e3466fa0-35f7-4f16-8c85-a240fa757573 has now finished successfully. No Git push or clinical validation. This supersedes the earlier account-login blocker; build completion is confirmed below.


## [2026-09-21] Standalone Android APK completed

EAS build e3466fa0-35f7-4f16-8c85-a240fa757573 finished successfully. Package com.gaitsteps.app, version 0.1.0 (1), SDK 52, internal preview release with developmentClient disabled. [Download APK](https://expo.dev/artifacts/eas/xAT-b9nZQhbSiJ3grrY6aKqeXL2JnqRIOFU2x94rP-0.apk). [Build details](https://expo.dev/accounts/frankielingishere/projects/gait-steps/builds/e3466fa0-35f7-4f16-8c85-a240fa757573). The app runs without Metro or the developer computer. Installation and physical three-sensor tests remain pending. No Git push was performed; automatic over-the-air updates are not configured.


## [2026-09-21] GaitTrace branding, updates and versioning

Display name changed to GaitTrace, with a rendered two-shoe teal/cream launcher icon and matching PWA branding. Stable Expo slug and Android package are preserved. Version 0.2.0, remote auto-incremented Android build 2. Fingerprint runtime and preview update channel configured. Initial OTA group 9a909628-c9e5-4804-a76c-0f7d1d19a98e published with Android update ID 01a0c240-c412-7c6f-b19b-d40607a329b3. Runtime ead45ff05f56ff8de69ce960cb9af9126a4cc015 matches replacement APK build 44f1af5a-436e-4613-82a0-66dd7f9bc99b. APK compilation completed successfully; current download below. Home/footer and recording JSON carry release identifiers. No forced reload during recording. GitHub OTA workflow prepared locally; needs publication and EXPO_TOKEN repository secret. Physical validation checklist is android/PHYSICAL_DEVICE_VALIDATION.md. Automated TypeScript and 73 tests pass; physical update adoption remains pending.


## [2026-09-21] GaitTrace 0.2.0 build 2 ready

Replacement APK build 44f1af5a-436e-4613-82a0-66dd7f9bc99b completed successfully. [Install GaitTrace 0.2.0 (2)](https://expo.dev/artifacts/eas/L7skC5kknzsTjhhW1TFZiX2pHnAfzgDiBMRO0UDHJWo.apk). This supersedes the earlier 0.1.0 download for sharing. Update server returned HTTP 200 with the expected update ID on the matching runtime. Physical install/update and sensor validation are still pending. Source/workflow publication and GitHub EXPO_TOKEN configuration remain outstanding; initial OTA was published directly through the authenticated Expo account.


## [2026-09-21] Publication authorized

User approved pushing the GaitTrace app, update workflow, sampling audit and associated documentation batch to main. APK and initial compatible OTA are already built/published. GitHub automation requires the EXPO_TOKEN repository secret; its presence has not yet been verified. No generated datasets, dependency folders, APKs or credentials belong in this source commit.
