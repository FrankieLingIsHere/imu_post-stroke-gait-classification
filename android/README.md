# Gait Steps

A single-role Android prototype for guided movement recording. After cloning, run `cd android` and `npm ci` (or `npm install`), then `npm run android`, using an Expo SDK 52-compatible client or development build. The local `npm run web` build supports preview and capability-gated browser capture; see the browser contract below. Browser capture publication authorized on 2026-09-17; physical-device verification remains pending.

## What changed

- Shared teal/cream theme, readable text, 56 dp buttons, system font scaling and safe-area handling. Primary actions remain outside content scrolling. Guides and history use explicit pages. Small screens and enlarged text retain overflow scrolling instead of clipping content.
- Four realistic, locally bundled guide illustrations: clear path, secure lower-back placement, comfortable walking and seated review. They are generated illustrations, not photographs of enrolled participants.
- After the final Start action and 20-second mounting countdown, the app automatically checks live sensors, phone orientation and settling. Three continuous steady seconds establish a stationary reference. Baseline samples and axis means are saved separately in JSON. A failed check stops without starting a walk. This does not verify anatomical placement or calibrate hardware accuracy.
- Real X/Y/Z accelerometer, gyroscope and magnetometer streams replace simulated recording. All three must be available and sending events before the walk begins. No simulator fallback.
- Every history item opens a descriptive movement summary, signal plots with explicit five-second time navigation, sensor information, observed sampling rates and capture notes. CSV and JSON export through the native file share sheet.
- Setup includes an optional brief voice sample with immediate Stop and a skip/start option after two seconds. There is no separate sound-check page or audibility confirmation. Voice-off mode explains that a helper must signal timing. Countdown, voice cues, visible Stop and save, Android back handling, interruption capture and retryable saves follow. Practice walks remain explicitly marked.
- Optional gentle direction reminders, on by default. The arrow is a static path reminder, never a navigation command or verified straightness indicator.

## Sensor and export contract

| Stream | X/Y/Z units | Requested rate | Meaning |
|---|---|---|---|
| Accelerometer | g | 100 Hz | Acceleration including gravity |
| Gyroscope | rad/s | 100 Hz | Angular velocity about each device axis |
| Magnetometer | microtesla (uT) | 50 Hz | OS-calibrated magnetic field |

Axes are the phone's axes, not clinically aligned body axes: X across the screen, Y toward the top, Z outward. Placement instructions specify upright, screen outward, in a firm centre lower-back pouch. Placement is instructed, not detected or verified.

Each event retains unrounded SDK X/Y/Z and native event timestamp in seconds, plus monotonic JavaScript receipt elapsed milliseconds and wall-clock receipt time. Native timestamps are not Unix time. Missing timestamps stay null. Streams remain independent; rates can differ. No interpolation, nine-axis row alignment, bias correction, gravity removal or resampling is silently applied. Partial final recordings are retained. Non-finite events are ignored; this prototype does not yet count rejected events.

CSV is long format: one sensor event per row, with source, units, timing, session ID, practice flag, placement, planned/captured duration and stop reason. JSON is the complete record and includes requested rates, platform/OS, calibration description, voice/reminder settings, reminder events, the separate measured baseline and a versioned summary computed from saved signals. Use JSON when full provenance is needed. Chart reduction preserves bucket extrema for display only; exported values are not reduced.

Observed rates prefer monotonic native event timing and otherwise use receipt timing. Notes flag missing streams, gaps over 250 ms, native-timing problems, rates below 80% of requested, and early stops. These are transparent engineering heuristics, not clinical quality gates or model-admission criteria. Captured seconds can include standing and pauses; no walking-period detector is implemented.

The native SDK 52 implementation was inspected: Android accelerometer divides the OS signal by gravity, while gyro and magnetometer preserve their OS axes/values, and all expose native seconds. See [Expo accelerometer](https://docs.expo.dev/versions/v52.0.0/sdk/accelerometer/), [gyroscope](https://docs.expo.dev/versions/v52.0.0/sdk/gyroscope/) and [magnetometer](https://docs.expo.dev/versions/v52.0.0/sdk/magnetometer/). Hardware accuracy, calibration and actual rates remain device dependent.

## Baseline, motion alerts and clinical scope

See [clinical scope and engineering rules](CLINICAL_SCOPE.md) for the reviewed G.A.I.T. Appendix A mapping, stationary-baseline conditions, combined acceleration/rotation checks and descriptive-summary formulas. Quiet pauses are accepted, saved and excluded from moving-period trend comparisons. The timer continues during rest; resuming is optional. Sustained possible handling gets a gentle reminder, while large smooth combined motion alone does not. These provisional checks cannot establish forward travel or distinguish every tremor from handling. The app does not automatically score G.A.I.T. or diagnose gait impairment.

## Direction reminders

The experimental estimate integrates upright phone Y-axis angular velocity after a stationary preparation baseline. A rolling 2.5 second calibration requires at least 1.8 seconds of samples and low gyro variation. It is disabled when the phone tilts or events become stale. A relative rotation above 25 degrees sustained for 2 seconds can trigger a soft cue, at most once every 12 seconds. Magnetometer readings are saved for research but do not drive direction cues, avoiding an unvalidated magnetic-heading claim.

This is relative phone rotation, not lateral drift, straight-line tracking, obstacle avoidance, fall detection or a validated gait measure. Phone slip and gyro drift remain confounders. No corrective left/right steering is given. Voice guidance matters when the phone is secured behind the patient; visual controls are for setup or a helper. Voice-off setup instructs the person to use a helper for timing. The patient can simply stop walking without reaching for the phone; the timed recording then ends automatically. Vibration supplements speech but does not replace it. Playing or skipping the optional voice sample does not prove audibility from the pouch or under changing noise/Bluetooth conditions.

## Storage and compatibility

Raw v2 sessions live in the app document directory, one JSON file per session, with a small AsyncStorage index. Save retries reuse the same ID. Old `gaitsteps:sessions` records remain readable and are explicitly labelled `legacy-simulation` in details and exports. Their original simulator only stored complete 500-sample acceleration windows; discarded tails and absent gyro/magnetometer cannot be recovered.

Recordings stay local until the user invokes the share sheet. Export copies use the app cache, which the OS may clear. Active acquisition is held in memory: abrupt process death or force-stop can lose an unfinished recording. Backgrounding is handled as an interrupted recording, but OS process termination is not a guaranteed save. No backend, participant identity, diagnosis or clinical labels are collected. Device hardware model/firmware and verified placement/calibration are not captured yet. These are future protocol needs, not evidence that synthesis or clinical validation is complete.

## Validation and review

Run `npm test`, `npm run ts:check`, `npx expo install --check`, and `npx expo export --platform android --output-dir dist/android`. All 43 tests passed, along with TypeScript, Expo dependency compatibility and the Android Hermes bundle export including all four illustrations. Tests inject synthetic hardware/speech callbacks; they are not real patient recordings or physical device trials.

Before participant use, perform the native device review:
1. Check 360×640, 390×844 and larger phones, gesture/button navigation insets, and enlarged system text with TalkBack. Main actions should stay reachable. Confirm guide images match the text and lower-back phone orientation.
2. Deny permission or use a device without a magnetometer: recording must not start. Confirm all nine axes respond on a device with the three sensors.
3. Record 10/20/30 seconds, including practice, quiet standing and walking. Inspect rates, native timestamps, units and all axes in the exported JSON and CSV.
4. Stop early, press Android back, background during setup/walking, retry a failed save and reopen after restart. Verify a completed session appears once.
5. Test export using Files and the intended recipient app. Confirm cancellation does not claim a transfer occurred.
6. Check voice audibility with the phone in its pouch. Verify the final baseline lasts at least three continuous steady seconds, then starts hands-free. Phone movement or stale events must restart settling. A failed check must announce that no walk started. Inspect the separate raw baseline in JSON.
7. Check strong phone motion, walk?rest?walk, direction calibration, phone tilt and turns with a helper in a controlled trial. Rest should produce no handling/direction cue or capture-quality penalty, and all samples should remain exported. Do not ask patients to shake the device. Reminder thresholds are unvalidated. Check that stillness and periodic handling do not become a gait diagnosis.

The in-app browser was unavailable in this workspace session. Responsive design and device sensors therefore still need visual/native verification. Existing SDK 52 dependencies report npm advisories; a framework upgrade requires a separate compatibility review.

Design references: [Aufait UX elder-friendly interface guidance](https://www.aufaitux.com/blog/designing-elder-friendly-ui-interfaces/) informed clear labels, contrast, larger targets and simpler navigation. No content or artwork was copied from that article.

## Local review scope

Review app source/configuration, dependency lockfile, guide assets, tests, this README, the gait-collection wiki handoff and weekly progress updates together. Dependencies, Expo caches and exported bundles are excluded by the existing workspace ignore rules. No commit or push was made. The pre-existing unrelated `.gitignore` edit is preserved.



## Pre-flight fit flow (2026-09-15)

From the single setup page, one Start test tap starts: 20 seconds to mount in a snug lower-back pouch (screen out), three continuous steady upright seconds, a spoken request for three comfortable steps and a stop, a movement-then-settling check whose final steady readings establish the baseline, then a spoken 3-2-1 countdown. The countdown rechecks fresh data and stability and returns to baseline checking if needed. The fit stage allows 45 seconds including rest; incomplete checks stop without starting a test, rather than inventing a pass. Steps are instructed, not counted. Three seconds of stillness are retained rather than reducing the existing baseline to two.

The fit stage needs one second of combined movement followed by three steady upright seconds. Missing data resets it. Sustained possible handling (1.5 seconds) stops setup with a gentle possible-pouch-motion message and haptic warning; it does not assert a loose belt or abnormal gait. No automatic repeated walking trial is forced. Successful raw fit streams are saved separately in JSON with timing and explicit unverified-contact/tightness/step-count metadata. Unsuccessful setup currently is not persisted as a session.

A first-order 10 Hz high-pass acceleration-vector RMS is saved as an engineering descriptor only. It requires monotonic native timestamps, intervals no greater than 25 ms, at least 50 samples, and at least 0.5 seconds after discarding the first 20 filter outputs. Otherwise it is null. It covers the fit stage including settling, not verified individual steps. No validated tightness threshold exists here. Human walking can contain high-frequency impact components: [heel-strike study](https://pubmed.ncbi.nlm.nih.gov/3964043/). A universal 1-4 Hz-only snug-fit rule is therefore not assumed.

The installed expo-sensors API has no proximity reader ([Expo sensor API](https://docs.expo.dev/versions/latest/sdk/sensors/)). Contact is explicitly unavailable, not a fabricated zero. Screen-out mounting remains consistent with the existing illustrations and exports. Proximity would require native integration and would still not prove anatomical placement. No OS screen lock is used because backgrounding interrupts acquisition. In-app stop/back buttons require a second confirmation within five seconds; Android Back remains available. Speech uses volume 1.0 but cannot override system media volume; the optional voice preview is available before mounting, and voice-off mode instructs the person to use a helper.

During capture, compare a two-second mean acceleration vector with the saved stationary gravity reference. Require sufficient continuous coverage and plausible gravity magnitude, and flag angles above 15 degrees sustained for two seconds. Store one possible-placement-shift event per run in JSON, include placement_review_required in every walking CSV row, expose a recording review note and withhold overall trend/rhythm, preserving all raw samples. Posture change or sustained acceleration can also contribute; yaw rotation about gravity is invisible to this monitor. Rest is still accepted. No asymmetry metrics or model admission pipeline exist in this app, and these flags must not be treated as clinical validation.

Validation: 43 injected-event software tests, TypeScript and Android bundle checks. Device audibility, touch usability, filter performance and threshold validation remain pending. All changes remain local.


## Setup and language update (2026-09-17)

Setup now uses one page with an optional voice sample. The sample can be stopped immediately or skipped after two seconds without disabling guidance. Retry this check stays on the recording page, preserves settings and a completed fit stage, and allows eight seconds to replace the phone before requiring a fresh baseline. Successful fit settling supplies the baseline without a duplicate wait. English, Bahasa Melayu and Simplified Chinese cover active screen text and spoken guidance, with a remembered language preference and explicit missing-voice errors. Raw export keys and values remain unchanged apart from optional setup language/retry metadata. All 43 software tests, TypeScript, Expo dependency compatibility and Android bundle export pass. Native pronunciation, audibility, accessibility and layout checks remain pending. No new clinical acquisition, validated preprocessing, training or evaluation occurred. Changes remain local.

On a native device, check each language with enlarged text and TalkBack, verify installed and missing language voices, and retry failures both before and after a completed fit stage. Confirm that retry never starts without fresh steady sensor readings.


## Patient-readable observations - 2026-09-17

The result and detail screens now share a patient-facing interpretation with compact Pauses, Rhythm and Changes tabs. It explains possible rests, visible repetition and beginning-to-end movement changes in English, Malay and Simplified Chinese, without exposing frequencies on the summary. Placement-shift flags, incomplete coverage and possible handling take priority and withhold interpretation. Rest does not imply poor gait. Motion amplitude is not labelled speed, fatigue, balance, step symmetry or recovery. The next-review prompt asks the person to share context such as rests, turns, discomfort and assistance with the recording. Existing signal algorithms and raw exports are unchanged. Forty-five software tests pass. Native layout and patient comprehension remain unverified. No clinical evaluation or model training was performed.


## Research feature exports

JSON export schema 3 adds `researchFeatures` (`phone-research-features-v2`) alongside unchanged saved raw data. The raw-event CSV remains unchanged. **Export features CSV** creates a separate tidy file with one row per feature, units, definition, availability reason, aggregation, placement verification and capture notes. JSON is the complete provenance record, including observed stream coverage and motion-context intervals.

Nine signal descriptors are computed: magnitude mean, sample magnitude SD (n−1), and vector RMS for each of accelerometer, gyroscope and magnetometer. They use all saved samples, including pauses/turns/handling, without filtering, resampling or gravity removal. They are sample-weighted engineering descriptors, not gait-quality measures. Steps, cadence and step timing now have explicitly experimental estimates from candidate peaks, with per-bout provenance. Full walking duration, speed, stride CV and stride-time asymmetry remain unavailable. No simulated legacy data receives device features.

There is no reference-comparison tab, classification or scoring in the app. The separate [executed research notebook](../notebooks/healthy_reference_comparison.ipynb) contains the 19-person annotation-assisted reference. Phone signal features are not interchangeable with those annotated gait features. Keep raw JSON for future reprocessing. Exporting an older real recording computes features on demand without modifying its saved raw session.

Validation: 53 app tests and five reference-module tests passed, with TypeScript and Android export checks. Native sharing/layout verification remains pending.


## Experimental exported step timing

`phone-research-features-v2` includes `phone-step-peaks-v1`. Only exports compute this estimator; patient summaries and live guidance do not use it. JSON retains candidate timestamps, within-bout intervals, exclusions, settings and method limitations. Feature CSV includes estimator version and distinguishes sample-wide descriptors from candidate-bout aggregation. The raw CSV and saved sessions remain unchanged.

Input: finite acceleration and gyro with strictly increasing native timestamps and observed rates >=25 Hz. Native timing is mapped to elapsed time using the first accelerometer event, not JS callback intervals. Linear interpolation to 50 Hz never crosses native gaps >100 ms. Complete one-second windows must satisfy the existing combined-movement heuristic. Quiet, uncertain, handling and missing windows split bouts. A placement-shift flag withholds timing for the recording. This can miss low-amplitude or slow pathological steps and does not establish walking or straightness.

Processing: acceleration magnitude minus a 0.3 Hz bidirectionally exponentially smoothed baseline, followed by bidirectional 3 Hz exponential smoothing. Those are nominal parameters, not Butterworth cutoffs. Local maxima need prominence >=max(0.025 g, 0.35 filtered SD) within 250 ms on each side. Peaks closer than 300 ms compete by height; intervals >2 s split bouts. Each bout needs >=4 candidate peaks. Exclude 300 ms at supported-run edges and partial final one-second windows. No side or toe-off estimator is implemented. Periodic handling, harmonics and missed peaks can bias timing.

Exported count is the number of retained candidates, **not a total verified session step count**. Cadence = 60 × sum(N_bout−1) / sum(last_time−first_time), excluding between-bout pauses. Step-time mean, sample SD and CV use within-bout adjacent-candidate intervals; changes of pace contribute to variability. `candidate_bout_duration` is the sum of those first-to-last spans, not total walking duration. No accepted bout yields null, not a claim of zero steps. Stance, swing, stride laterality, asymmetry and speed are not inferred.

Validation: 53 app contract tests include 60/90/120/150 steps/min synthetic oscillations at 50/81.7/100 Hz, native-time invariance to batched JS delivery, pauses, gaps, stillness, handling, clock failures and placement-shift gating. Synthetic oscillations are not patient validation. The [executed phone audit notebook](../notebooks/phone_gait_recording_audit.ipynb) replays the actual TypeScript export against the supplied non-lower-back trace: 9 candidates, 65.395 candidate intervals/min, 7.34 s retained first-to-last duration. There is no observed step reference and no accuracy claim. Parameters were not tuned to this trace.

The prior [event adapter failed admission](../reports/LOWER_BACK_EVENT_VALIDATION_2026-09-09.md); this new simple peak estimator is not a validated replacement or a port of mobgap. Literature distinguishes step-count estimation from contact-event measurement: [smartphone step counting](https://cancer.jmir.org/2023/1/e47646) and [lumbar gait-event estimation](https://www.jmir.org/2025/1/e72831/). Their validation does not transfer to this implementation. Independent synchronized step/contact observations are the next measurement-validation need.


## Browser capture

This update adds **Check this phone's sensors** to setup. Under HTTPS, the browser must expose real Accelerometer, Gyroscope and Magnetometer XYZ streams through the Generic Sensor API. Hardware presence alone is insufficient; unsupported browsers retain the walkthrough. No compass-angle substitution, synthetic data or partial-sensor recording fallback is used.

The check takes three seconds. Every sensor needs finite XYZ and increasing timestamps, at least 1.5 seconds of measured coverage, at least 25 Hz, no sensor-time gap over 250 ms and a reading within the last 500 ms. These are engineering readiness rules, not calibration or clinical quality validation. Start rechecks streams before the existing mounting/baseline/fit/countdown flow and requires separate consent. Existing requested-rate capture notes remain unchanged, so a browser can pass readiness but still have rate notes against the 100/100/50 Hz requests.

Device-relative acceleration including gravity is converted from m/s2 to g using 9.80665; gyro stays rad/s and magnetometer stays uT. Sensor.timestamp milliseconds become seconds, without substituting receipt time. JSON identifies platform=web, API, timing origin, conversion, user agent and unverified calibration. Raw and feature CSV append platform, sensor_api and timestamp_basis. Experimental timing metadata distinguishes browser from native time. This is not evidence of native/browser measurement equivalence.

Keep the page foregrounded and the phone unlocked. Missing streams or a hidden tab interrupt and save an active walk. Browser capture and review are held only in tab memory: **export before refreshing or closing**. No uploads or persistent browser storage. Speech, vibration and wake lock depend on browser support and need actual-phone testing. Native local-file storage is unchanged.

67 automated tests and TypeScript pass; web and Android bundles build. Tests inject events and check missing/denied/slow/stale/invalid streams, conversion, cleanup, provenance, consent and interrupted saving. Physical browser-device and audio trials remain pending.

References: [Sensor timestamps](https://developer.mozilla.org/en-US/docs/Web/API/Sensor/timestamp), [Accelerometer device frame](https://developer.mozilla.org/en-US/docs/Web/API/Accelerometer/Accelerometer), [Gyroscope](https://developer.mozilla.org/en-US/docs/Web/API/Gyroscope), [Magnetometer support](https://developer.mozilla.org/en-US/docs/Web/API/Magnetometer/Magnetometer).

## Browser layout and review

The browser build uses a centred phone frame (430 px outer width) on wider screens and the full viewport on phones. It reuses the app screens, gives an explanatory hands-free walkthrough when its three-sensor check cannot pass, and never simulates a successful reading. Local JSON imports are bounded and validated, held in tab memory only, never uploaded, and cleared on refresh. Browser exports download files instead of using native sharing.

Deployment review and exact proposed source scope: [DEPLOYMENT_REVIEW.md](DEPLOYMENT_REVIEW.md). The existing Pages workflow builds a separate `/gait-app/` entry. Browser interaction cannot be verified here because no connected browser is available.


## Installable web app (PWA)

The web export is a single-page progressive web app. On a supported phone browser, open the hosted app, then use **Install on this phone** or the browser's **Add to Home screen** menu. It opens in its own phone-shaped app window and caches the app shell for offline reopening. A connection is still required to load the latest deployment and browser sensor permissions/availability still apply. In particular, installing the PWA cannot expose a magnetometer that the browser has withheld.

The PWA is rebuilt from this same `/android` source on every Pages deployment. The service worker uses network-first navigation and cached static assets as an offline fallback; versioned JavaScript files update with a new deployment. Browser recordings remain tab-memory only and must be exported before refresh, closing, or browser storage eviction.

## Horizontal belt and sampling update (2026-09-21)

See [sampling and placement protocol](SAMPLING_AND_PLACEMENT.md) for the new landscape belt orientation, browser consent limitations, measured rates and experimental JSON comparison projections. Raw capture remains unchanged.

## GaitTrace release and device validation

The installed app is named GaitTrace. See [distribution and versioning](NATIVE_DISTRIBUTION.md) and [physical-device validation checklist](PHYSICAL_DEVICE_VALIDATION.md). The original 0.1.0 APK must be replaced with the update-enabled 0.2.0 APK.
