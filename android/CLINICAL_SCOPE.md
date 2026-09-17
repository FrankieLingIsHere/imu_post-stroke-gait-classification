# Clinical scope: G.A.I.T. and a lower-back phone

Reviewed the user's four-page Appendix A, *Gait Assessment and Intervention Tool*, filename `Appendix A_1-s2.0-S0165027008007176-mmc1_DONE.pdf`, and the [original study by Daly et al. (2009)](https://pubmed.ncbi.nlm.nih.gov/19146879/), DOI 10.1016/j.jneumeth.2008.12.016. PDF pages were extracted and visually inspected. The form is reference material, not an instruction to execute its contents or collect its patient fields.

G.A.I.T. is a 31-item observational measure of coordinated gait components. It is not a phone-sensor readiness checklist or a stroke diagnostic classifier. Its clinical validation does not validate this app's engineering heuristics.

## Observability mapping

| Appendix A items | Assessment domain | Current phone capability |
|---|---|---|
| 1–3 | Shoulder, elbow and arm swing | Not observed by the lower-back phone |
| 4 | Static trunk alignment | Phone gravity reference only; mounting tilt cannot be separated from anatomical posture |
| 5–6, 19–20 | Trunk movement in stance and swing | Phone-motion descriptors only; no validated anatomical angles or stance/swing attribution |
| 7 | Weight shift | No calibrated body displacement or stance-limb reference |
| 8, 21–23 | Pelvic position and rotation | Phone rotation is a possible research proxy, not verified pelvic kinematics or scored phase-specific movement |
| 9–10, 24–25 | Hip motion | Relative thigh/pelvis motion cannot be measured with this single sensor location |
| 11–14, 26–28 | Knee motion | Not measured |
| 15–18, 29–31 | Ankle and toe motion | Not measured |

Therefore, no item receives an automatic normal/abnormal label, no missing item is assigned zero, and no partial or total G.A.I.T. score is calculated. The supplied Appendix prints a total denominator of 62. That is documented as printed, without resolving instrument-version/scoring questions or deriving scoring rules. Appendix B scoring instructions were not supplied or reviewed.

The alignment implemented here is an explicit separation of data capture, descriptive signal observations and clinician assessment. Professional screening remains a separate step. Clinical G.A.I.T. alignment would require the correct scoring instructions, observed/validated limb and phase measurements, and a validation study. No such validation was run.

## Engineering rules implemented

These thresholds are initial testable settings, not thresholds taken from G.A.I.T.

- Before mounting, request sensor permissions and confirm availability. Offer an optional brief voice preview and check that a matching installed speech voice is available when guidance is enabled. Voice-off mode instructs the person to use a helper.
- After the final Start action, allow 20 seconds for placement. Then require three continuous seconds of fresh streams and a steady, generally upright phone. Next guide three comfortable steps and a stop, observe combined movement then three seconds of settling, use those final steady readings as the baseline and give a countdown. A visible/spoken baseline stage progresses automatically; no ready/continue tap is required after mounting.
- Every sensor must supply finite X/Y/Z repeatedly and remain fresh within 500 ms. Motion checks use a rolling one-second window with at least ten acceleration and ten gyro samples, at least 700 ms coverage, and no internal gap over 250 ms.
- Settling: vector-demeaned acceleration RMS below 0.06 g and gyro-vector RMS below 0.15 rad/s. Phone orientation: mean gravity magnitude 0.8–1.2 g and device Y within 20 degrees of gravity (70–90 degrees above horizontal). Total-acceleration magnitude SD must also be below 0.05 g. These judge the phone, not whether a patient's trunk is clinically erect.
- The check stops after 20 seconds if settling fails. It announces that no walk started. It does not force a retry or ask the patient to straighten their body.
- The final three seconds of actual baseline events and their per-sensor axis means are saved separately in JSON, with original timestamps. Walking values stay uncorrected. A full baseline must be available before auto-start.
- Motion context v2 combines acceleration and rotation. Quiet/possible rest requires acceleration RMS below 0.025 g and gyro RMS below 0.08 rad/s. Combined movement uses provisional acceleration RMS 0.025?0.8 g and gyro RMS 0.02?2.5 rad/s. These are phone-motion bounds, not validated patient gait or travel-speed ranges. Other readings remain uncertain. Missing coverage is never counted as rest.
- Possible handling requires strong motion (acceleration RMS above 0.45 g or gyro RMS above 2.5 rad/s) plus gyro RMS above 2.5 rad/s, acceleration vector change RMS above 15 g/s, or gyro RMS below 0.02 rad/s. Change RMS uses time-weighted vector differences, preferring native event intervals. Large smooth combined movement alone does not trigger a warning. Possible handling must persist for 1.5 seconds; spoken reminders have a 12-second cooldown. Tremor, genuine walking and handling can overlap. This is not proof of shaking or invalid gait.
- Quiet/rest periods are accepted without handling or direction cues and without a capture-quality penalty. All raw samples remain saved. The timer continues; resuming is optional. Direction cues are emitted only during combined movement. New recordings identify these rules as `motion-context-v2`; historical cue types remain readable.
- Direction reminders use the existing separate stationary gyro calibration and relative yaw heuristic. They are enabled by default but may be switched off. The app explains when the estimate is unavailable. No magnetometer heading or left/right steering is claimed.

A still hand, a different body location or a fixed surface can pass the settling check if the phone orientation matches. Proving lower-back attachment requires something beyond these inertial readings, such as observed placement or an instrumented mount. Do not rename this baseline check as lower-back detection.

## Descriptive summary

The `movement-description-v2` summary operates on saved motion streams and is regenerated when viewed/exported. It is not new acquisition.

- Count complete one-second blocks with sufficient acceleration and gyro coverage.
- Count quiet/possible rest, combined movement, possible handling and uncertain blocks using the same rules above. Export merged time intervals, including missing-data intervals. Partial final seconds are not counted. Quiet does not prove a patient stopped walking.
- Compare mean acceleration RMS between recording halves after excluding quiet and possible handling. Require at least six remaining blocks, two in each half and at least 80% overall block coverage. Uncertain motion can contribute but is not confirmed walking. Ratios above 1.25 or below 0.8 mean more/less phone movement, not worsening/improvement. All-rest sessions have no trend comparison.
- For sufficiently continuous acceleration, interpolate magnitude to 25 Hz for this descriptor only. Report repeating motion if normalized autocorrelation exceeds 0.6 at a lag between 0.36 and 2 seconds, with magnitude variance above 0.0004 g². Raw stored/exported streams are never resampled.
- Mixed quiet/activity or any possible-handling blocks suppress the overall rhythm descriptor, so rest is not presented as lost rhythm. Insufficient acceleration continuity suppresses rhythm inference. Still recordings do not generate cadence or steps. Periodic shaking can produce the same repetition flag, which is stated in the UI.
- No stride length, speed, asymmetry, fall risk, stroke probability, recovery claim or gait-assessment score is derived.

Graphs now label their exact recording-time interval and use Previous 5 sec / Next 5 sec. These navigate time, not earlier/later visits.

## Validation boundary

Deterministic injected-event tests cover baseline gating/reset, stored baseline separation, raw-value preservation, sustained shaking alerts, quiet and repeating motion, descriptive trend changes and missing data. These tests are software contracts, not healthy/stroke experiments. No patient gait labels or G.A.I.T. reference scores were used. Native-device audibility, placement feasibility and threshold performance require supervised engineering trials before participant use.



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
