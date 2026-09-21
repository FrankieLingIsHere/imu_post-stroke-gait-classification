# GaitTrace physical-device validation

Run these checks with a researcher/helper before patient use. Record phone model, Android version, GaitTrace version/build/update ID (home-screen footer), date, language, test ID, belt position and observations. Keep the JSON and CSV exports from each trial. Mark each check PASS / FAIL / NOT TESTED. Automated tests and APK compilation do not replace these checks.

## 1. Install and standalone operation

Install the new 0.2.0 APK over the earlier version using the same signing identity. Confirm the GaitTrace name and two-shoe icon. Existing recordings must still open. Turn off the computer and disconnect Wi-Fi/mobile data. Cold-launch the app and open existing recordings. Try English, Malay and Chinese; offline speech requires the respective Android voice installed. Test large system text and a small phone screen: main actions must remain reachable.

## 2. Raw three-sensor checks (researcher holding phone)

Make short labelled engineering captures; these are not gait trials. On a stationary nonmetal table, acceleration magnitude should be around 1 g, gyro near zero, and magnetometer should produce finite readings in microtesla. Numerical plausibility alone does not prove calibration. Gently change orientation: gravity should move between acceleration axes, gyro should respond during rotation, and magnetic components should change. Never bring a strong magnet near a participant or device to perform this check. Sensor readings must not appear before real events arrive. If hardware is unavailable or access denied, recording must not pass readiness. Use a separate test device for permission-denial tests rather than changing a participant's phone settings.

Inspect exported JSON: three independent streams, x/y/z in each, monotonic sensor timestamps, actual counts/rates, no NaN/Infinity, no repeated frozen stream. Native requests are 100/100/50 Hz for accel/gyro/magnetometer. Assess observed rates, not requested values. A stable slower rate is not a missing sensor. For this first engineering review, flag <80/80/40 Hz or any gap >250 ms for review; these are requested-rate tolerance checks, not clinically validated acceptance limits. A 50 Hz gyro may still be useful, but cannot be claimed equivalent to 100 Hz. Measure jitter and timing separately for each stream.

## 3. Belt baseline and hands-free flow

Place the pouch at the centre of the lower back, long edge horizontal, screen outward. Have a helper visually verify it. Test both ends pointing left. A stable landscape phone should pass after a continuous baseline. Portrait or flat placement should not pass the new angle gate. Moving during the baseline should reset settling. Do not ask a patient to straighten their body to satisfy a phone check: adjust the pouch if comfortable, otherwise record the failed gate for review.

After Start, verify the spoken placement period, movement/fit check, stopping, baseline and countdown proceed without further taps. Repeat after a failed step: completed steps should not all restart. Confirm voice is audible while the phone is behind the user. Test the stop action and accidental touches with a helper. The app cannot verify anatomical location, strap tightness or safety to walk from orientation alone.

## 4. Controlled walking and interruptions

With a healthy volunteer and clear route, collect three 20-second straight trials, then a walk-pause-walk trial. Pauses must be retained, not diagnosed as poor gait. Compare experimental peak counts with a helper's independent count/video if consented; record discrepancies rather than adjusting thresholds to fit. A manual count cannot validate side-specific timing or neurological cause.

Separately test a deliberate comfortable turn and a belt-position change with a researcher. Direction cues are approximate and may be withheld without a usable baseline. A sustained tilt change should flag review; it may reflect posture or belt movement. Do not deliberately destabilize a patient. Phone handling can mimic steps, so a missed handling warning is a limitation to record, not proof of valid gait.

Background or lock the phone during a test, then reopen it. The recording should be interrupted/saved, not silently presented as complete. Check an incoming-call interruption too. Raw capture must not bridge missing intervals as if measured. Verify the saved stop reason, duration and gaps.

## 5. Export and provenance

Export JSON, raw CSV and feature CSV. Confirm all three sensor names/units, placement instruction, separate timestamps, and the expected number of raw rows. JSON must contain appRelease with actual installed version/build and embedded or OTA update ID. Derived projections and alternating timing must be labelled experimental. They must not replace raw axes or assert stroke, verified left/right identity, or alcohol/fatigue exclusion. Reopen saved recordings after app restart and test sharing to the intended researcher destination.

## 6. Automatic update and rollback readiness

The first APK had no updater: install the NEW 0.2.0 APK first. With internet, cold-launch the new APK and leave it open long enough to download. Fully close it from recents and reopen. The footer should show the published update-ID prefix instead of bundled. Record both IDs and export a new test recording. The currently published initial OTA carries the same functionality as the embedded build, so use the ID to verify delivery rather than expecting screen changes.

During an active recording, an update must never force a reload. Close/reopen offline afterward and confirm the cached app still works. Keep a previous known-good compatible update/build identified before future releases; EAS can republish an earlier compatible update. This release configures automatic loading, but physical update adoption and recovery remain untested until these steps pass. A new native runtime requires a new APK, not an OTA. Existing recording compatibility must be tested after each change to export/storage contracts.

## What this validates

This checklist validates installation, acquisition and workflow behavior on the tested phone only. Accurate step timing/asymmetry requires simultaneous independent bilateral foot-contact reference (e.g. validated instrumented system) and predeclared error analysis across relevant users and devices. Neurological attribution requires clinician-labelled cohorts and explicit confounder evaluation. Do not induce alcohol exposure, sleep deprivation or unsafe walking for an app smoke test.

Test log template:

| Test ID | Phone / Android | App/build/update | Condition / orientation | Sensor rates and largest gaps | Expected / observed | Export filenames | PASS/FAIL/NOT TESTED |
|---|---|---|---|---|---|---|---|
| | | | | | | | |
