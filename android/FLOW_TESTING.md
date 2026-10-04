# Sensor-free flow testing

Run from `android/` after `npm install`:

```powershell
node scripts/start-flow-lab.cjs
```

Open http://localhost:8092 on this computer. The phone-sized interface runs the
actual shared app screens. A permanent FLOW LAB banner identifies the session.
The demonstration participant and practice recording are browser-memory fixtures
with no sensor measurements. They disappear on refresh and cannot enter native
patient storage or be imported as device recordings.

Use **Open demo assessment** to enter the outcome form and the complete
item-by-item observer G.A.I.T. form. Use **Start a walk > Preview hands-free flow**
to exercise each protocol's explanation, preparation and start/finish screens
without passing a sensor check. The preview finish control represents an endpoint;
it is not evidence that the phone detects a course boundary or chair contact.

## Automated checks

```powershell
npx.cmd playwright install chromium
npx.cmd playwright test
npm.cmd test
npm.cmd run ts:check
```

Playwright opens the real Expo web UI at a phone viewport. It checks all 31
observer ratings, save/reopen, profile setup, every clinical tutorial and the
10MWT/TUG/2MWT/6MWT preview flows. Its controlled clock advances the two- and
six-minute preview timers without waiting in real time. Reports, screenshots and
failure traces are local under `dist/flow-lab/` and ignored by Git.

The existing React Native renderer tests inject sensor events and speech callbacks
to verify first-step gating, stillness, interruptions, start/finish clocks and
persistence failures. These are deterministic software tests, not hardware trials.

This browser harness is not an Android emulator. It covers shared UI/logic but
cannot verify native permissions, installed speech engines, real audio completion,
camera tracking or physical IMU accuracy. Those need a final real-device check.
No Android emulator/AVD was found in the inspected local setup.

## Observer G.A.I.T. version

The digital rubric uses the user's supplied Appendix A PDF, 31 items and a maximum
of **62**, identified by a source SHA-256 in `src/gaitRubric.ts`. The original paper's
abstract states 64; do not mix the abstract's maximum with this supplied form.
All option branches, including options sharing a numeric score, retain unique IDs.
Directions/positions and item notes are retained separately. Unobserved items are
missing, never zero. No full total is shown until all ratings, required directional
details, assessor, valid date, limb and observation source are complete.

Scores are entered by a trained observer, never computed from phone signals.
English, Malay and Chinese interface labels are available. Original detailed
scoring criteria remain English; interface translations are not validated clinical
instrument translations. Save using **Save assessment to this phone**. The form
is linked to the recording/participant, reopened from recording details, included
in JSON, and exported as per-item option/score/notes/direction columns in feature CSV.
The dashboard displays complete observer totals without interpreting improvement.

Reference: [Daly et al. updated form and administration discussion](https://www.mdpi.com/2076-3425/12/8/1104).
