# Native calibration acquisition

Local Expo module, Android Camera2/SensorManager only; no paid service or remote
backend. SDK 52 autolinks the module from `android/modules`. A new native APK is
required; Expo Go and older installed APKs cannot receive it through JavaScript OTA.

`capture()` obtains native frames/capture-result timestamps and all three IMU
streams, automatically stops after 40 seconds, and returns a private ZIP plus
manifest. `progress` exposes actual saved frame previews and native elapsed time;
`stop()` preserves an explicitly incomplete capture. Captures are not gait records
and do not create participants, assessment forms, trends or metric distance.

See [research processing](../../research/README.md) for the board, units, admission
checks, phone/configuration binding and independent distance-validation boundary.

Capture-v2 adds `captureWithOptics("waist-bag-window" | "clear-lens")` and
`captureNoise()`: the latter runs camera-free for five minutes on a stationary
table, writes all three IMU streams, and exports a separate device-bound ZIP.
This short capture supports white-noise characterization, not a complete bias
random-walk model. New calls require the 0.3.5 native APK.

Callbacks copy native data to one serialized storage/tracking handler. Frame work
is bounded to four jobs and rejected callbacks are counted; sensor overflow stops
capture explicitly. Accepted jobs drain before files close. No camera rate is
invented: the 30 Hz request, actual capture/saved rates and processing delays are
separate manifest fields. Acquire-latest driver frame loss is not identical to
the queue-drop counter. Callback clock latency needs a real-time camera clock.
Current distance research exports remain metric-blocked until full calibration
and a continuous native estimator are integrated and validated.
