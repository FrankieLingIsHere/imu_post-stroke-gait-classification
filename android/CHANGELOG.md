# GaitTrace release history

This file records source releases and installation requirements. `app.json` declares the application version; EAS assigns the Android build number. Actual installed release/runtime/update identifiers come from `src/releaseInfo.ts` and are included in recordings. Do not infer an APK build number from the application version or promise an APK before its build succeeds.

## Unreleased - quick stationary Google API check

- Separate Research tools > Quick Google API check; no participant, placement, countdown, gait recording or deliberate post-stop wait.
- Checks native availability/permission, subscription, detailed reads over recent 60-second and 600-second context windows, and cleanup. Empty successful replies pass API access while records remain unavailable. Context counts are never walking distance. Four-second request timeouts and late-subscription cleanup are included.
- EN/MS/ZH messages and structured technical logging (`GaitGoogleApiCheck`) for connected-device inspection. Waving is not a walking accuracy test.
- TypeScript, 126 tests and Android Metro export pass. Native runtime matches build 6: `a48c2ed43ddd2142beaa39b7f8031b8fff327407`. No native or dependency changes; compatible OTA `3ccb972` was published and loaded on the installed build-6 phone. Existing clinical and short-trial capture timing is unchanged.
- Live Redmi Note 10 Pro check on 2 October 2026: availability, subscription, 60-second read, 600-second read and cleanup all passed in about 0.3 seconds; both reads returned zero records. This verifies API access, not walking distance or step accuracy. The result was visible on the phone without scrolling.
- Local follow-up for short Google trials: the final delayed read also queries a wider post-finish context window in parallel. Its raw points and polling outcome are exported as diagnostics only; no context value enters trial distance, steps, speed or stopping. This cannot force Google to produce records, and physical validation is still required.
- Local separate Google trial option: measured 5 m out and 5 m back (10 m total) with one comfortable turn, spoken three-language guidance, eight-second quiet finish and 90-second fallback. The route pattern survives JSON/CSV export and import; it remains a practice distance experiment, not a clinical 10MWT.

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
