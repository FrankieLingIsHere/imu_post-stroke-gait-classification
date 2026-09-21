# Browser acquisition and horizontal belt protocol

Updated 2026-09-21. Implementation is local pending publication review.

## Access and consent

The in-app dialog authorizes a three-second live check. Starting each supported Generic Sensor invokes the browser's access checks. This does not guarantee a browser permission prompt. Missing constructors cannot be enabled through consent or the Permissions API. All three actual streams remain required. No magnetic field is inferred from orientation angles.

Chromium documents a 60 Hz cap for most sensors: https://chromium.googlesource.com/chromium/src/+/refs/heads/main/services/device/generic_sensor/README.md . Chrome documents the restricted Magnetometer API: https://developer.chrome.com/docs/capabilities/web-apis/generic-sensor . A PWA has the same restrictions as its browser.

Browser requests are now 60/60/50 Hz for accelerometer/gyroscope/magnetometer. Native requests remain 100/100/50 Hz. Requested rates are not observed rates. JSON comparisonSignals.sampling reports observed timing and gaps, and the existing raw streams preserve original timestamps and values.

## Horizontal belt

Position the pouch at the centre of the lower back, screen outward, long phone edge horizontal. Either end may point left. The static gate expects gravity along either sign of device X within the existing provisional 20-degree window. It rejects portrait and flat placement. This tests phone orientation only, not anatomical location, face contact, fit, or the patient's posture. A helper should check the initial placement. The three-second settling and movement-then-settling steps remain automatic. Direction reminders use rotation projected onto measured gravity rather than device Y. Sustained orientation change still flags review and may represent posture rather than belt slip.

English, Malay and Chinese instructions reflect horizontal mounting. The old portrait placement illustration is suppressed until a matching illustration is available.

## Comparison and normalization

Raw device coordinates and units remain unchanged. New recordings identify lower-back-landscape-screen-out. Old portrait exports remain readable. JSON adds experimental stationary-gravity projections: signed vertical and unsigned horizontal magnitude, independently for each sensor at its own timestamps. Acceleration retains gravity. Missing baseline or a flagged placement shift suppresses these projections. This removes a constant coordinate rotation from these particular descriptors, but does not reconstruct anatomical forward/lateral axes or compensate time-varying body tilt. Horizontal magnitude loses direction and must not be used as a lateral asymmetry channel.

Lower rates can affect peak timing, spectral features and models trained at 100 Hz. At 50 Hz the sample interval is 20 ms, versus 10 ms at 100 Hz. Interpolation to 100 Hz cannot restore lost information. We have not measured model degradation on paired phone/reference recordings.

Recommended research protocol, not yet executed: retain raw files, audit native timestamps and gaps, choose a common rate supported by the slowest accepted stream (25 Hz is a candidate for the reported 46 Hz gyro), low-pass all source datasets below the target Nyquist frequency before resampling, and split or reject gaps. A candidate 8 Hz passband needs task-specific evaluation and an adequate transition band below 12.5 Hz. Do not use this representation for high-frequency wobble analysis. Keep higher-rate raw fit data for that purpose. Recompute features and train/evaluate on the same preprocessing using subject-separated splits and independent phone/reference evidence. Do not scale amplitude or z-score each walk merely to resemble healthy data: that can erase clinically relevant differences.

No dataset has been transformed, no model has been retrained, and no clinical equivalence has been established in this batch. Automated tests cover landscape gating, rotation-invariant projections, missing-baseline/shift suppression, and consent-before-check flow. Physical browser permission, belt placement and sensor/reference validation remain pending.
