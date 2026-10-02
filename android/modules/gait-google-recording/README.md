# Google on-device Recording API experiment

Local Expo module for GaitTrace. Uses Google Play services Fitness **21.3.0**, `FitnessLocal` and `LocalRecordingClient`, not legacy Fit OAuth or the Fit REST API. No API key, Google account, cloud upload, trial subscription or paid service was added. Google calls the on-device data registration a *subscription*; this is not a billing subscription.

## Build and use

Expo SDK 52 autolinking discovers this package in `android/modules/`. The library manifest and app configuration declare `ACTIVITY_RECOGNITION`. A **new native Android APK** must contain the module: Expo Go and previously installed APKs cannot obtain it through JavaScript updates. App version is 0.3.0; EAS uses the existing remote build-number configuration and fingerprint runtime policy. Do not publish the new JavaScript bundle against the older native runtime.

Build with the project's existing Android build workflow and signing identity. Java and the Android SDK are required for a local build. No new cloud build or paid account is initiated by this change. A successful native compile and physical-device run are still required before calling the integration device-tested.

In **Set up your walk → Language and audio settings**, enable **Google distance test · experimental**. Start Test checks full distance-capable Play services availability and requests Android physical-activity permission while the phone is accessible. No Fit app installation or Google sign-in is required. Missing native module, unavailable services or denied permission explains how to continue with the option disabled.

## Capture contract

- Register distance and steps during preparation, before recording starts. Query only from the research-walk capture start or the clinical audible Go to actual capture finish; setup movements remain outside that query window.
- Read detailed records every two seconds and twice after stopping, with a two-second delay before the last read. Each request has a four-second timeout. This is a bounded observation window, not a guarantee Google has finished batching.
- Preserve provider record intervals, first observation times, query request/return times, counts and errors in JSON. A missing record is `null`, not zero. An explicit provider zero is preserved. Returning record intervals do not establish sample-level latency.
- Deduplicate identical records. Exclude invalid values, boundary-straddling intervals and overlapping intervals from sums; retain original observations for audit. Do not prorate a coarse interval into invented per-second distance. Coverage is the duration of accepted distance intervals divided by the test window; it describes returned intervals, not validated walking coverage.
- Withhold whole-window speed for incomplete interval coverage (below 95%), rejected intervals or API errors. This 95% software gate is an experimental completeness rule, not an accuracy threshold. Any available speed remains an OS estimate over the capture window, not verified central-zone 10MWT speed.
- Release both registrations after final reads or cancellation. Record cleanup failure; do not claim background collection stopped when cleanup fails. A late subscription resolving after cancellation triggers cleanup again. Google registrations can survive process death, so a force-kill may interrupt cleanup; permission revocation/system settings may be necessary if that happens.
- API failure does not stop the IMU test. Google outputs never control boundaries, overwrite raw axes or replace measured reference outcomes. Google summaries are exported in raw/feature CSV; detailed records and arrival evidence are in JSON.

## Physical validation on the actual holder

1. Install the newly built APK. Record its app/build/runtime versions and phone/Play services versions. Verify grant, deny and module-unavailable behavior; never report readiness based only on hardware presence.
2. Keep the agreed horizontal lower-back, screen-out arrangement. Use a tape-measured straight course and independent video/observer timing as the **research validation reference**. The app still obtains Google distance automatically; no patient distance entry is needed.
3. Compare repeated trials at comfortable and slow pace, pauses, cane use where applicable and turns. Include a standing-only control to check false distance. Evaluate post-stroke trials separately from healthy development checks.
4. Export JSON and CSV. Examine whether Google supplied distance at all, accepted interval coverage, excluded boundary intervals and first-seen delays. Short tests may end before records arrive; do not turn that into a clinical zero or quietly use the height heuristic.
5. Compare available distance with the measured route using bias, absolute/relative error and repeatability. Validate timing/endpoints separately. Agree acceptance limits with the supervisor before using Google distance to end a test. Raw IMU, OS distance and reference distance must remain separate.

Sources: [Google integration guide](https://developer.android.com/health-and-fitness/recording-api), [LocalRecordingClient](https://developers.google.com/android/reference/com/google/android/gms/fitness/LocalRecordingClient), [detailed read request](https://developers.google.com/android/reference/com/google/android/gms/fitness/request/LocalDataReadRequest.Builder).
