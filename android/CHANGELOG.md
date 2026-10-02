# GaitTrace release history

This file records source releases and installation requirements. `app.json` declares the application version; EAS assigns the Android build number. Actual installed release/runtime/update identifiers come from `src/releaseInfo.ts` and are included in recordings. Do not infer an APK build number from the application version or promise an APK before its build succeeds.

## 0.3.0 — 2 October 2026

**APK status: not built yet.** The Android build number is pending EAS assignment. This is the same `com.gaitsteps.app` application, not a separate test app. The new native Google module requires a new APK; JavaScript updates cannot add it to build 5 or Expo Go. Retain the existing signing identity when building an update to preserve the installed application and its local data. Fingerprint runtime policy separates incompatible native versions.

### Changes

- Opt-in Google on-device Recording API distance/step comparison using Play services Fitness 21.3.0, with activity permission requested before mounting. No Google account, Fit OAuth or paid service was added.
- Provider record intervals, first-seen and poll timing, missing/partial/error results and subscription-cleanup diagnostics. Google data stays separate from raw IMU, clinical reference outcomes and stopping logic. JSON retains detailed evidence; raw and feature CSV include Google comparison columns.
- Explicit clinical history for clinical-test setup, participant linkage and saved profile snapshots; unknown history is not fabricated.
- Five-second standing baseline, participant-paced setup and hands-free clinical capture. Timed endurance tests finish automatically; 10MWT/TUG movement-then-quiet stopping remains provisional and cannot verify course crossings or chair contact.
- Protocol-aware experimental phone speed, including timed rests, and separate optional measured-reference entry. Whole-walk estimates are not central-zone 10MWT speed.
- English, Malay and Chinese instructions, experiment controls and result messages.

### Verification and limits

TypeScript and 117 automated tests passed. Android/web Metro exports, native-module autolinking, SDK API-symbol checks and whitespace checks passed. These do not constitute native compilation or physical-device validation. Google distance accuracy, short-test availability and reporting delay require actual-holder trials. No clinical accuracy claim or automatic Google-distance endpoint is enabled.

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
