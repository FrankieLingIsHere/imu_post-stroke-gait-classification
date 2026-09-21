# Supervisor preview deployment review

**Approved publication update (2026-09-17):** browser capture is implemented and the user approved publishing the exact batch below. Earlier preview-only descriptions below document the previous release; see README.md for the current browser contract. This batch is being published; physical-device verification remains pending.

Proposed new files: android/src/browserSensors.ts and android/tests/browserSensors.test.cjs. Modified app files cover the recording adapter/contract, setup and result screens, platform banner/home/import text, transient browser storage, exports, timing provenance, translations and tests. App README and this review document, Week 4 Markdown/HTML, and wiki status/index/log accompany the change. Dependencies, generated bundles and previously stashed research work remain excluded.

Verification: 67 tests and TypeScript pass; web and Android bundles build. No actual browser-device sensor or audio validation has been completed. Browser capture remains dependent on all three Generic Sensor APIs; tab memory is lost on refresh/close and users must export first.

Publication authorized on 2026-09-17. Git repaired to 2.55.0.windows.5; remote fetch succeeds and origin/main is an ancestor of the reviewed branch. Publication is being executed; earlier blocker/review entries below are historical. This is a research prototype presentation, not a patient-service launch.

## Current patient flow

Choose language and settings → optional voice sample → Start → 20-second mounting time → live streams and baseline → comfortable movement/settling check → automatic countdown → timed recording with rest allowed → local review and raw/feature exports. A failed setup check can be retried while retaining completed fit checks and acquiring a fresh baseline.

Before unsupervised patient use: revise the absolute upright gate to accommodate habitual leaning, distinguish ambiguous phone/posture changes, and test mounting, audio, accessibility and event estimates on physical devices and representative users. Current peak estimates are experimental, not verified foot contacts. This preview does not imply those issues are solved.

## Browser presentation

- The actual Expo interface stays phone-sized: a centred 430 px outer frame on wider screens, full viewport on phones. Small content areas retain scrolling and fixed primary actions.
- A persistent browser-preview label states that sensors are not recorded.
- Setup leads to an explanatory walkthrough, never a fabricated sensor-ready state or generated patient recording.
- Review an Android JSON export by choosing a local file. It is kept only in tab memory, never uploaded or bundled. Refresh clears imported recordings. Download JSON, raw CSV or feature CSV locally.
- No default patient data, healthy reference distribution or classification model is included in the site. English, Malay and Simplified Chinese remain available. Browser voice availability depends on the device.

## Proposed publication scope

1. `android/`: app source, translations, configs, tests, lockfile, README/clinical/deployment documentation and four guide illustrations. Exclude dependencies, caches, build output, signing files and recordings using `android/.gitignore`.
2. Root `.gitignore`: include the six-line Android cache/build exclusion addition as defense in depth. `android/.gitignore` also excludes these paths independently.
3. `.github/workflows/publish-results.yml`: add verified Expo web export and copy its output into the existing Pages artifact at `gait-app/`. Existing portal assembly remains intact.
4. Keep weekly/wiki updates, research notebooks, generated analyses and unrelated local changes local for separate review. Publish from an isolated checkout of remote main, copying only the approved files. Do not push the current research branch and its unrelated commits.

Expected location after successful GitHub Pages publication: `https://frankielingishere.github.io/imu_post-stroke-gait-classification/gait-app/`. This is a target, not a verified live URL.

Build locally in `android/`: set `GAIT_WEB_BASE_PATH=/imu_post-stroke-gait-classification/gait-app`, then run `npx expo export --platform web --output-dir dist/web`. Clear that environment variable for a root-hosted local preview. The existing Pages workflow builds artifacts rather than committing generated bundles.

## Native Android distribution

`eas.json` includes an internal preview APK profile. An APK is required to distribute real sensor collection without a running Expo development server. No Expo account is currently signed in, and no Android SDK/Java build environment was found on PATH. An APK has not been built or uploaded. When an authorized Expo account is available, link the project and use `eas build --platform android --profile preview`; review the Android signing setup then. Do not invent an EAS project ID.

## Verification limits

Automated checks and bundle checks are recorded in the app README. No connected browser is available in this workspace, so interactive browser/layout verification is still pending. Native sensor and audibility checks also require a device. Publication requires review of the above scope under the root AGENTS.md rule.

## Exact app files proposed for first publication

- `android/.gitignore`
- `android/App.tsx`
- `android/CLINICAL_SCOPE.md`
- `android/DEPLOYMENT_REVIEW.md`
- `android/README.md`
- `android/app.config.js`
- `android/app.json`
- `android/assets/guides/path.png`
- `android/assets/guides/placement.png`
- `android/assets/guides/review.png`
- `android/assets/guides/walk.png`
- `android/babel.config.js`
- `android/eas.json`
- `android/package-lock.json`
- `android/package.json`
- `android/src/audio.ts`
- `android/src/components/BigButton.tsx`
- `android/src/components/PatientSummary.tsx`
- `android/src/components/PhoneFrame.tsx`
- `android/src/components/QualityBadge.tsx`
- `android/src/components/ReviewImport.tsx`
- `android/src/components/ReviewImport.web.tsx`
- `android/src/components/Screen.tsx`
- `android/src/components/SignalChart.tsx`
- `android/src/components/StepIndicator.tsx`
- `android/src/export.ts`
- `android/src/export.web.ts`
- `android/src/exportData.ts`
- `android/src/gaitTiming.ts`
- `android/src/i18n.tsx`
- `android/src/language.ts`
- `android/src/movement.ts`
- `android/src/patientSummary.ts`
- `android/src/placement.ts`
- `android/src/recording.ts`
- `android/src/researchFeatures.ts`
- `android/src/reviewRecording.ts`
- `android/src/screens/DetailsScreen.tsx`
- `android/src/screens/HistoryScreen.tsx`
- `android/src/screens/HomeScreen.tsx`
- `android/src/screens/OnboardingScreen.tsx`
- `android/src/screens/PrepareScreen.tsx`
- `android/src/screens/RecordScreen.tsx`
- `android/src/screens/ResultScreen.tsx`
- `android/src/screens/WalkthroughScreen.tsx`
- `android/src/sensorSim.ts`
- `android/src/sensors.ts`
- `android/src/store.ts`
- `android/src/store.web.ts`
- `android/src/theme.ts`
- `android/src/translations.ts`
- `android/tests/experience.test.cjs`
- `android/tests/recording.test.cjs`
- `android/tsconfig.json`

Modified tracked file: `.github/workflows/publish-results.yml`. No other tracked modifications are in the publication scope.

## Pending-change review - 2026-09-17

Recommendation: publish the 54 app files listed above, root `.gitignore` Android exclusions, and the Pages workflow as one isolated app deployment commit. The app candidate set is 8,864,212 bytes before this documentation update (about 8.9 MB); four guide PNGs account for about 8.1 MB. These are required source assets, not Expo caches.

Verified `.expo/`, `node_modules/`, `dist/` and Metro caches are ignored, with no tracked files under the first three directories. Keep `package.json`, `package-lock.json`, Expo app configuration and source assets. After cloning, run `cd android`, `npm ci` (or `npm install`), then `npm start`; CI uses `npm ci` for locked dependency installation. All lockfile dependency URLs use the public npm registry. A limited secret-pattern scan found no matches; this is not an exhaustive security audit.

Keep all other pending changes local for a separate research/documentation review: both notebooks, healthy-reference Python module/test, phone recording audit, thesis/reference/app wiki pages, wiki indexes/log, notebook/classification indexes, and weekly Markdown/HTML. The phone audit notebook contains saved plots and relies on a local Downloads recording; the healthy-reference notebook relies on ignored local research artifacts. They are not prerequisites for building the app and a fresh clone alone cannot replay their analyses. The weekly HTML contains relative links to research documents not copied by the Pages workflow; do not publish those additions in this app-only batch.

TypeScript and all 58 app tests passed again during this review. Interactive browser and physical-device checks remain pending. The current branch has eight commits ahead of the cached origin/main; do not push that branch wholesale. Refresh the remote and publish only reviewed scope from an isolated checkout after explicit approval. No staging, commit or push occurred during this review.

## Expanded research-history review - 2026-09-17

This supersedes the earlier recommendation to exclude all eight research commits solely because they are unrelated to app deployment: the user has requested their inclusion in repository publication review. Keeping the research history is appropriate, subject to the disclosed content and final scope review.

| Commit | Scope | Assessment |
|---|---|---|
| b6348b1 | Research modules, tests, experiment runners, model manifests and ignore rules | Include as source/evidence; weights and raw data remain local. |
| ec0f604 | Completed experimental reports and locked protocols | Include; preserve failures and development-only interpretation. |
| 8f15fac | Research specifications, data-access evidence and recruitment drafts | Include only with awareness that unsent outreach drafts and researcher contact addresses will become public; these are not private correspondence or acquired clinical records. |
| 690119d | Notebook evidence, wiki and project collaboration instructions | Include; local-artifact dependencies are documented. |
| 8c492be | Progress page and builder dependency cleanup | Include. |
| 1749386 | Removal of superseded experiment slide PDF | Include; original remains in prior Git history. |
| 652b9ad | Six report-runner migrations to saved-output notebooks | Include; historical source remains in Git history. |
| 9104dfb | Script dependency inventory and handoff updates | Include; structural inventory does not imply every experiment is reproducible from a bare clone. |

Compared with cached origin/main, the final tree changes 209 paths. Across all eight commits, 235 introduced blob versions total 5,928,610 uncompressed bytes; largest is about 549 KB. No introduced raw/processed dataset directory, model weight archive, node_modules or Expo cache was found. Limited credential-pattern scanning found no matches. Researcher emails occur in three contact/draft documents, with public-source citations; their current validity was not rechecked. All 101 changed Python files parse, five changed notebooks have no saved error outputs, and all existing Pages copy inputs exist in the committed tree. No training, dataset acquisition or clinical validation was rerun.

Pre-publication documentation corrections made locally: remove stale notebook-35 reservation now that 35-38 exist, and clarify in the prototype registry that local weights/examples are not included in a clone. These corrections should accompany publication. Other current app/research unstaged changes are separate from the eight historical commits and must not be swept in with `git add .`.

Remote refresh was attempted but Windows Application Control blocked Git's libcurl-4.dll; origin/main therefore remains cached and current remote divergence is not verified. No push was attempted. A deletion or later redaction would not remove content from earlier commits; if contact drafts are excluded, publish a curated history/snapshot rather than pushing all eight unchanged.

Final test result: 109 tests across 33 changed research test files pass. The initial GPU/NumPy parity failure (maximum absolute difference 5.66e-6) was corrected in the test only by fixing the seed and disabling cuDNN TF32 during that comparison. Include `tests/test_gait_cnn.py`, `models/prototypes/README.md` and the notebook-index correction with the reviewed history; no training behavior or saved results changed. Weekly/wiki review entries remain local pending final scope approval.

## Git network failure: confirmed root cause and required repair

On 2026-09-17, Windows CodeIntegrity event 3077 identifies `C:/Program Files/Git/mingw64/libexec/git-core/libzstd.dll`, loaded by `git-remote-https.exe`, as failing Enterprise signing requirements under policy `{0283ac0f-fff1-49ae-ada1-8a933130cad6}`. The console reports libcurl-4.dll because its dependency load fails. Installed Git is 2.55.0.windows.2. The blocked DLL reports NotSigned; SHA-256 is `B95C223A9548A9ECF51377C962E0BC8F0C51EB0C6F67A296DBC885996F0DD40D`.

The official Git for Windows release endpoint currently lists 2.55.0.windows.5. This establishes an available update, not that the update satisfies this machine's policy. A Windows administrator/policy owner must deploy an approved Git package or repair its approved installation. No policy, signature requirement, transport or DLL was modified to evade enforcement. Once repaired, run `git fetch origin` and recheck divergence before pushing. Git network access remains unresolved; no publication was attempted.

Sources: [Microsoft App Control troubleshooting](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/app-control-for-business/operations/appcontrol-debugging-and-troubleshooting), [official Git for Windows installation](https://git-scm.com/install/windows).

## Week 4 publication additions

User-requested current-week app progress is prepared in `docs/classification/WEEKLY_PROGRESS_2026-09-14.md` and `reports/WEEK_04_PROGRESS.html`. `site/index.html` now features Week 4 while retaining Week 3, and the Pages workflow copies the new report. The classification index and wiki handoff link the current week. These additional files remain local for final review; the report states deployment is pending and separates implementation, software tests, sample QA and uncompleted clinical evaluation.


## Exact browser-capture change batch

- android/DEPLOYMENT_REVIEW.md
- android/README.md
- android/src/browserSensors.ts
- android/src/components/PhoneFrame.tsx
- android/src/components/ReviewImport.web.tsx
- android/src/exportData.ts
- android/src/gaitTiming.ts
- android/src/recording.ts
- android/src/researchFeatures.ts
- android/src/screens/DetailsScreen.tsx
- android/src/screens/HomeScreen.tsx
- android/src/screens/PrepareScreen.tsx
- android/src/screens/RecordScreen.tsx
- android/src/screens/ResultScreen.tsx
- android/src/sensors.ts
- android/src/store.web.ts
- android/src/translations.ts
- android/tests/browserSensors.test.cjs
- android/tests/experience.test.cjs
- android/tests/recording.test.cjs
- docs/classification/WEEKLY_PROGRESS_2026-09-14.md
- reports/WEEK_04_PROGRESS.html
- wiki/concepts/classification-project-status.md
- wiki/index.md
- wiki/log.md

## PWA delivery change batch - 2026-09-17

The user requested a PWA instead of the uncommitted Expo Update/Android automatic-update preparation. That preparation was removed locally: no `expo-updates` dependency, Expo account linkage, Android update channel, automatic-update workflow, APK update metadata, or native update behavior remains in this batch.

The same `/android` app source now exports a PWA through the existing Pages workflow. New public files provide a standalone manifest, local app icon and scoped service worker; a post-export script adds manifest and service-worker registration to Expo's generated HTML. The Home screen uses the browser's standard installation prompt where available and gives Add-to-Home-screen guidance otherwise. The Pages deployment runs `npm run export:web`, so every approved main-branch change rebuilds the PWA from the same source; no generated deployment files are committed.

The PWA cache is an offline app-shell fallback. It uses network-first navigation to receive a new deployment and caches static same-origin files. It does not persist recordings, upload data or expand browser sensor permissions. Browser capture still requires the three exposed Generic Sensor APIs, including the currently unavailable magnetometer on the tested browser.

Verification: TypeScript and 70 tests pass. The PWA export includes the manifest, standalone metadata, service-worker registration, icon and worker files. Android bundle export still passes without altered native behavior. Physical PWA installation, browser permission and offline fallback testing remain pending.

## Proposed acquisition update ? 2026-09-21

Review scope: browserSensors.ts, movement.ts, recording.ts, sensors.ts, comparisonSignals.ts, exportData.ts; PrepareScreen.tsx, RecordScreen.tsx, OnboardingScreen.tsx, translations.ts; experience/recording tests; SAMPLING_AND_PLACEMENT.md, README.md, this review, Week 5 progress, wiki status/index/log. Adds app consent, realistic browser requests, landscape belt setup and derived gravity projections. No raw dataset replacement or model retraining. Physical validation and publication pending.

Additional scope (2026-09-21): eas.json and NATIVE_DISTRIBUTION.md; alternatingTiming.ts, PatientSummary.tsx and translations/export/tests; src/features/sampling_audit.py and tests/test_sampling_audit.py; executed notebook 39 and PHONE_SAMPLING_AND_ASYMMETRY.md; weekly and wiki updates. Local generated CSVs remain excluded. No model training. Expo account is now linked and the APK build completed successfully.


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
