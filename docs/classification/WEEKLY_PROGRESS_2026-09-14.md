# Week 4 progress: phone gait collection app

## Browser sensor follow-up

Implemented a three-second real-stream check for browser accelerometer, gyroscope and magnetometer, per-sensor rates/status, separate consent and fresh recheck before shared hands-free setup. All streams must meet 25 Hz coverage/freshness requirements; missing channels are never synthesized. Browser exports identify acquisition API, timing origin, unit conversion and platform. Capture is foreground-only, with interrupted saving on sensor loss or tab hiding. Tab-memory recordings must be exported before refresh/close. Native/browser equivalence is not established. 67 tests and TypeScript pass; web/Android bundles build. Actual-phone permissions, speech and sensor checks remain pending. Publication approved on 2026-09-17, with no new clinical acquisition or model evaluation. The earlier weekly snapshot below describes the deployed preview.

Week beginning **14 September 2026**, recorded through **17 September**. This week's focus is developing and checking the phone collection workflow, building on the earlier app prototype. Earlier model-development results remain in the Week 3 report; no new model training or clinical validation is claimed here.

## Main outcome

Prepared a single-codebase Android collection prototype and a phone-layout browser preview for remote supervisor review. The app records real three-axis accelerometer, gyroscope and magnetometer streams, offers guided setup and local review, and exports raw data plus experimental timing features. The browser preview is built from the same `/android` source and does not record or simulate IMU data. Deployment is prepared but not live.

## Work completed and current capabilities

| Workstream | Result | Interpretation |
|---|---|---|
| Patient experience | Consistent theme, large controls, fixed primary actions, paged guides, realistic illustrations, English/Malay/Simplified Chinese text and speech | Small screens and enlarged text retain necessary scrolling; voice availability depends on installed voices. |
| Setup and hands-free flow | Consolidated settings, optional short sound preview, mounting time, fresh-stream checks and measured stationary baseline, movement/settling check, automatic countdown | Retry preserves completed fit checks but acquires a fresh baseline. Sensors cannot verify anatomical lower-back contact or belt tightness. |
| Recording and assistance | Independent nine-axis streams, native and receipt timestamps, gentle audio/haptic cues, rest-aware checks, interruption capture | Quiet rest is allowed. Direction/placement cues are phone-motion heuristics, not clinical balance assessment. |
| Review and export | Recording details, time-labelled plots, sensor rates and capture notes; JSON, raw CSV and feature CSV | Raw readings are preserved. Browser JSON review stays in tab memory and does not upload files. |
| Experimental gait timing | Candidate step events, within-bout cadence and step-interval statistics, with version and exclusions in exports | Peak estimates are not validated foot contacts or total observed steps. No patient classification or normality score is included. |
| Remote presentation | Expo web build from `/android`, centred phone frame on laptops and full viewport on phones; shared screens and calculations | Platform adapters handle browser imports/downloads and Android sensors/storage. No second app codebase. |

## Current patient flow

Language and settings → optional voice sample → Start → mounting guidance/time → live sensor checks and measured baseline → comfortable movement/settling check → automatic countdown → timed recording, with pauses allowed → local review and export.

The browser substitutes an explicitly labelled explanatory walkthrough for native acquisition. It never reports a fabricated sensor-ready result. Screen guidance alone is insufficient when mounted at the lower back; native audio/haptics and physical audibility checks remain important.

## What the supplied recording established

One user-described healthy practice recording was audited. The user confirmed the phone was **not at the intended lower-back location**, so this is an engineering trace, not an eligible lower-back training or validation sample.

- Captured duration: **10.100 s**; all **2,017** CSV sensor rows match the JSON export.
- Accelerometer: **827 samples, 81.746 Hz**; gyroscope: **820 samples, 81.110 Hz**; magnetometer: **370 samples, 36.607 Hz**.
- All nine axes are finite and vary. Requested rates of 100/100/50 Hz were not achieved. The current repeat flag is explained by magnetometer rate below its 40 Hz threshold.
- Experimental replay produced **9 candidate peaks**, **65.395 candidate intervals/min**, over **7.34 s** of retained candidate-bout duration. These are algorithm outputs, not observed step-count or cadence accuracy.
- There was no independently observed step/contact reference. This sample cannot establish gait normality, sensor calibration or training suitability.

## Verification and evidence status

| Area | Status |
|---|---|
| App software checks | 58 tests and TypeScript pass; web and Android bundles produced locally. |
| Layout verification | Automated phone-frame geometry checks pass; interactive browser checks remain pending because no connected browser is available. |
| Research-history review | 109 tests across 33 changed research test files pass after a test-only fixed-seed/precision correction; no model retraining. |
| Acquisition | One supplied device trace inspected; no new clinical cohort acquired. |
| Processing | Native-time acquisition QA and experimental feature replay completed for that trace. |
| Clinical evaluation | Not completed; no independent step/contact accuracy or representative patient usability study. |
| Deployment | Source/configuration prepared; Git repaired to 2.55.0.windows.5 and remote fetch verified; publication authorized and in progress. |
| Android distribution | APK not built; Expo account or local native build environment still needed. |

## Decisions and next steps

1. Use the browser build for supervisor walkthrough and review of locally selected exports. Keep real sensor collection in Android.
2. Retain research history in the repository after scope review. Exclude `.expo`, `node_modules`, generated bundles, raw data and model weights; retain lockfiles and source assets.
3. Git repair and remote refresh are complete. Publish the reviewed scope and verify the Pages deployment.
4. Test mounting, audio, interruption/retry, import/download and accessibility on physical devices. Adjust absolute-upright gating to accommodate habitual lean before unsupervised patient use.
5. Validate candidate steps and timing against synchronized observations; test pauses, turns, slow/asymmetric walking and handling separately. Signal completeness alone does not validate a gait feature.

The grant objective remains clinically parameterized healthy-to-stroke-like synthesis. This week's collection and measurement work supports that objective; it does not complete clinical synthesis or establish a diagnostic app.

## Reading links

- [App source and method](../../android/README.md)
- [Publication scope and Git blocker](../../android/DEPLOYMENT_REVIEW.md)
- Phone recording audit: retained locally for separate research review.
- App wiki: retained locally for separate research review.
- [Week 3 model-development history](WEEKLY_PROGRESS_2026-09-07.md)
- [Supervisor-facing Week 4 page](../../reports/WEEK_04_PROGRESS.html)


## Settings explanation update

Settings clarity update (2026-09-17): labelled 10/20/30 seconds as recording duration after the countdown, excluding setup time and allowing pauses/early stopping. Added accessible 48-pixel info buttons for Recording duration, Voice guidance, Direction reminders and Practice walk, with one expandable explanation at a time. The duration label remains visible; its explanation is hidden until tapped. Text supports English, Malay and Simplified Chinese. TypeScript and all 58 existing app tests pass. This change is authorized for publication; recording logic is unchanged.


### Default settings shortcut

Added Use default settings: restores the existing 20-second configuration with voice and direction reminders on and practice off, cancels a playing voice sample, closes help and confirms the selected values. It does not start recording, change language or select consent. All four setting explanations use info buttons; English, Malay and Chinese supported. TypeScript and 58 tests pass. Publication authorized by the user on 2026-09-17.
