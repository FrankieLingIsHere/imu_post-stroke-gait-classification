---
type: concept
status: active
updated: 2026-09-09
---

# Classification project: current handoff

Current implementation: [workspace guide](../../docs/classification/README.md) and [weekly progress](../../docs/classification/WEEKLY_PROGRESS_2026-09-07.md). Completed public results are in Week 3 commit `b462795`; remaining local files include both completed work and active research.

Current objective: clinically parameterized healthy-to-stroke-like synthesis. The tested cycle contract and six-channel virtual-IMU component are complete: 18 healthy GAITEX participants, 55 windows, eleven tests passed. This does not establish stroke synthesis or L5 validity. Clinical bounds, coherent motion transformation, measurement/phenotype validation and a clean final cohort remain open. RevalExo is historical only. Previously inspected data remain development data.

Metadata and existing raw signals were reused. Pilot preprocessing and engineering verification are complete; no new clinical evaluation or classifier improvement occurred. GAITEX pilot roles include 14 available development-build and four development-holdout parents. See the workspace guide for the completed experiment archive; do not restart old proposals.

Current engineering decision: user authorizes lower research-prototype gates.
[Policy, dataset roles and CLI](../../docs/RESEARCH_PROTOTYPE_POLICY_2026-09-09.md).
TVS laterality prototype packaged on 32 participants/1,645 contacts under 85%
accuracy and 85% coverage gates. Earlier CV: HA 87.46%, PD 87.34%, corrected coverage
86.45%/85.45%. This is post-result prototype acceptance, not revised validation.
Original failed gates remain historical evidence. Frozen stroke model unchanged.
Acquisition unchanged, prototype fitting/packaging and real CLI smoke check complete.
Inputs require native TVS-frame gyro and supplied contact indices. No stroke output.

Use [[evidence-gated-model-improvement]], [[mobilise-d-tvs]] and the
[evidence map](../../docs/CLASSIFICATION_EVIDENCE_MAP.md). Historical logs and
reports are not instructions to rerun completed work.

## Current implementation

Current executable stroke feature prototype: [stroke-phase-hr-v0.1.0](../../models/prototypes/stroke-phase-hr-v0.1.0/README.md).
[Workspace guide](../../docs/classification/README.md) and [prototype registry](../../models/prototypes/README.md) are the active entry points.
Both TVS laterality and stroke phase+HR feature prototypes are packaged.
Acquisition unchanged, existing HR preprocessing/evaluation complete; independent validation open.
The following sections preserve prior implementation results.

Historical: [packet alignment correction](../../reports/PACKET_ALIGNMENT_CORRECTION_2026-09-09.md)
is complete. Metadata/raw files reused; aligned preprocessing and feature evaluation
complete on 1,348 trials/259 people. Frozen paired evaluation complete on 5,340
windows/138 non-stroke people: 89 positive before, 89 after, zero changed calls.
Four alignment tests and provider-signal verification passed. No clinical data
acquisition, retraining of frozen weights or model promotion. No job is running.

Previous: [lower-back event validation](../../reports/LOWER_BACK_EVENT_VALIDATION_2026-09-09.md)
completed on all 260 local people/1,356 trials. Metadata accounted; local provider
processed lower-back acceleration reused; 2,712 trial/mode evaluations completed.
No data download or classifier fitting. Pinned mobgap 1.2.0 installed in existing
environment. Autonomous stroke F1 .811, count-cadence MAE 17.51 steps/min; admission
failed. Four tests passed; three invalid references remain explicitly accounted.

Historical: [conditional gait comparison](../../reports/CONDITIONAL_GAIT_COMPARISON_2026-09-09.md)
is complete: metadata census 260 people/1,356 trials; existing evaluation scope
259 people/1,348 trials; local lower-back raw signals reused, four reference-assisted
gait features complete, 36 logistic fits evaluated. No raw acquisition. One
missing age retained. Matched scope 144 (19 healthy/49 stroke/76 other).
RMS AUROC .801 stroke-versus-healthy but .449 stroke-versus-other; combined features
failed to improve on covariates plus cadence. Three tests passed. No promotion.

The [differential-gait experiment](../../reports/DIFFERENTIAL_GAIT_IMPLEMENTATION_2026-09-09.md) is implemented and
complete: 259 Voisard participants, 7,485 windows, three participant-disjoint
folds with whole pathology groups held out, three seeds and three matched arms
(27 GPU fits). This is the new one-channel objective comparison, distinct from
historical three-channel negative exposure. It uses no TVS or RevalExo data.

Three-class versus primary-binary means: other-pathology FPR 40.58% versus
53.38%, but stroke sensitivity 68.71% versus 87.76%. Matched binary exposure
achieved 35.99% FPR with the same mean sensitivity. All seed gates failed;
no candidate weights replace frozen v0.2.0. Do not repeat this experiment or
retune its threshold to claim success. These are development-control results,
not estimates for the full frozen ensemble or independent-site validation.

[Input-validity API and CLI](../../models/input_validity.py) are available as an
opt-in wrapper. Constant and nonfinite windows return null scores with explicit
reasons. Valid inputs pass unchanged. Rejections must not be counted as healthy
negatives. This is not a gait detector and does not resolve moving healthy TVS
errors. Six focused tests and real API/CLI smoke verification passed.

## Data and evaluation ledger

| Layer | Verified completed state |
|---|---|
| Frozen model | v0.2.0, 15 members, lower-back magnitude in g, 100 Hz, 500 samples, unchanged |
| Development | 314 people across Felius, Voisard and Sint; current differential experiment uses only Voisard |
| TVS metadata | All 40 HA/PD participants |
| TVS raw signals | 36 participants; four metadata-excluded raw files not acquired |
| TVS preprocessing and evaluation | 34 participants, 117 windows; five metadata and one short-bout exclusion |
| TVS calls | 17/18 healthy, 16/16 PD positive; newly opened stratum 14/15 healthy and 14/14 PD |
| Voisard exact-weight stress | 89/138 non-stroke positive; pooling still gives 87/138 |

[Full TVS result](../../reports/TVS_COHORT_RESULT_2026-09-09.md).
No download, training or evaluation job remains running. TVS has no stroke group;
reference turns are unavailable and all opened people are now inspected evidence.
No stroke sensitivity or clinical generalization claim follows from TVS.

## Methodology direction, 2026-09-09

See [[classification-methodology]]. Native packet alignment is corrected in a
versioned loader and the affected feature comparison has been rerun. False
positives persist; the packet-correction experiment is closed. New extraction
should use src/data/voisard_aligned.py. Historical helpers/tensors remain for
reproduction. Broader migration and manuscript impact assessment are separate
from this implementation result. No further diagnostic candidate is admitted;
independent measurement truth and cross-source validation remain absent.

## Root-cause status and next decision

[Mechanism probes](../../reports/TVS_POSITIVE_CALL_MECHANISM_2026-09-08.md)
found shared temporal-pattern sensitivity, high scores on constant inputs and
no tested magnitude/rate/units/normalization mismatch. They did not establish a
unique clinical cause. The three-class result now shows that this particular
label-objective change is insufficient under its locked recipe.

No next training candidate is admitted. A new proposal must identify what differs
from completed exposure, normalization, threshold, pooling, architecture and
three-class experiments, and retain stroke sensitivity on disjoint validation.
Do not mistake the implemented input guard for a fix to actual gait specificity.

## Persistent collaboration decisions

- Read the integration plan and evidence map before proposing repeat work.
- Public accessible raw IMU is preferred; author-request leads are parked and
  outreach requires explicit authorization. Search local archives before download.
- Use `C:/Users/frank/.venv-cu130/Scripts/python.exe`; no new environment is needed.
- Keep this page, affected wiki pages, index and append-only log synchronized.
- Preserve frozen artifacts, old results and unrelated changes; state hypotheses
  separately from verified findings. No manuscript findings were changed.

## Bilateral phase experiment completed, 2026-09-09

[Executed comparison](../../reports/BILATERAL_PHASE_COMPARISON_2026-09-09.md):
259 participants, 1,348 trials, 1,345 complete trial phase sets. Every participant
retained with complete aggregated features. Existing folds and corrected baselines
reproduced. Four unit tests passed and 24 logistic fits completed.
Primary phase addition: other FP 73 to 64/138, stroke detections 43 to 41/49.
Matched subset: other FP 35 to 26/76, stroke detections 34 to 30/49. Both fail the
locked sensitivity-preserving gate. Secondary combined+phase matched other FP
43 to 31/76 with stroke detections unchanged at 31/49. Useful development signal,
not a proven root cause or admitted replacement. Frozen model remains unchanged.
Metadata/raw acquisition unchanged. Phase preprocessing and evaluation complete.
No download or running job.

## Nested sensitivity threshold experiment completed

[Executed result](../../reports/PHASE_NESTED_THRESHOLD_2026-09-09.md): 72 inner
fits with thresholds selected only from inner OOF stroke scores at a 90% target.
Both primary gates failed. Full phase arm detects 41/49 stroke with 59/138 other
FP, baseline 44/49 and 61/138. Matched phase arm detects 42/49 with 61/76 other FP,
baseline 44/49 and 69/76. Secondary matched combined+phase detects 45/49, but
62/76 other and 13/19 healthy are positive. Three threshold unit tests passed.
All participants retained, no release changes. Metadata/raw acquisition unchanged,
phase preprocessing reused and nested evaluation complete. Stop threshold sweeps.
Current roadmap priority is the directional measurement prerequisite described below.
Do not relabel stroke scores as validated gait-abnormality scores. Sensor-only phase
recovery and diagnostic specificity remain unvalidated. OOD is a separate question.

## Stance variability feasibility completed, 2026-09-09

[Executed CV coverage check](../../reports/STANCE_VARIABILITY_FEASIBILITY_2026-09-09.md):
1,259/1,348 usable trial CVs. Healthy 68/72, ACL 9/11 and HOA 13/15 fail the locked
95% group coverage gate; stroke 49/49. No participants dropped, no model fitted,
no new accuracy result. Eight CV/phase tests passed. Metadata/raw acquisition
unchanged, CV preprocessing complete and classifier evaluation not run.
All selected raw headers contain Acc/Gyr/Mag XYZ; the subsequent audit below
resolves nominal axes, without per-trial calibration. Next is provider device-axis convention verification for directional
harmonic ratio, followed conditionally by gyro measurement validation. Existing
magnitude HR is not ML HR. OOD stays lower priority. No release changes or running job.

## Directional-axis audit completed

[Provider/file verification](../../reports/DIRECTIONAL_AXIS_AUDIT_2026-09-09.md)
establishes nominal LB X vertical, Y ML, Z AP. It supersedes the earlier metadata-only
uncertainty. Raw/processed mappings: 750 TechnoConcept flip X/Y, 37 identity,
507 XSens identity, 54 unsupported comparisons. All comparable filtered mappings
match to numerical precision. CVA_18_2 has Z-dominant initial gravity; retain as a
quality flag, not a diagnosis-based exclusion. Per-trial anatomy remains unvalidated.
Nominal-Y harmonic ratio with coverage/orientation sensitivity is completed below. Sign inversion is irrelevant to Fourier amplitudes but
relevant to gyro laterality. Acquisition unchanged, axis audit complete, HR
extraction/evaluation completed below. No new diagnostic score or release change.

## Directional HR experiment complete

[Executed results](../../reports/ML_HARMONIC_RATIO_2026-09-09.md): primary matched
phase+HR detects 44/49 stroke with 5/19 healthy and 47/76 other FP, versus 42/49,
13/19 and 61/76 without HR. Full HR: 45/49, 6/72 and 56/138. Both primary gates
fail (matched sensitivity below 90%, full FPR improvement below 5pp). All 259
participants retained; main HR coverage complete, quality-screened HR available
245/259 with train-only imputation. Three tests and 96 fits complete. Improvements
not uniformly robust to quality screening. No model promotion. Metadata/raw
acquisition unchanged, HR preprocessing/evaluation complete. Conditional gyro laterality is completed below. OOD remains separate.

## Conditional gyro laterality completed

[Executed result](../../reports/GYRO_LATERALITY_2026-09-09.md): reference-time side
assignment gate failed. Matched healthy 97.8%, stroke 89.6%, CIPN 95.9%, PD 96.6%,
RIL 88.1% participant-macro accuracy. Full stroke 71.4%, healthy 54.0%. Six fresh
fits and two tests complete, 48,131/48,257 contacts usable. No pretrained pickle
or environment downgrade used. No automatic label flipping or adapter promotion.
The signed gyro audit is completed below; scope dependence is not proof of device causality. Acquisition unchanged, conditional
preprocessing/evaluation complete. Autonomous and independent measurement validation
remain unfulfilled. Stroke-classifier results unchanged. No running job.

## Gyro mapping audit complete

[Executed mapping audit](../../reports/GYRO_AXIS_TRANSFER_AUDIT_2026-09-09.md):
1,294 comparable trials, all gyro/acceleration sign permutations agree. Scale 1,
constant offset correction reconstructs processed gyro to max RMSE 2.1e-14.
54 comparisons unsupported. No input bug found that justifies retraining.
Ten participants with both devices have saved side accuracy 25.9% XSens vs 78.9%
TechnoConcept; sessions/mounting/protocol remain possible contributors. No label
flips or independent anatomical validation. Two tests passed. Acquisition unchanged,
audit complete, model results unchanged. Close this audit. New calibration needs
independent frame evidence; OOD must consult prior abstention decisions first.

## Physical calibration hypotheses checked

[Executed checks](../../reports/GYRO_CALIBRATION_EVIDENCE_2026-09-09.md): U-turn
integrals 3.075 XSens/3.068 TechnoConcept support common radians/s scale. Processed
initial bias near zero, head/back turn signs agree 1,343/1,343 usable trials.
These do not prove absolute handedness. All ten paired-device participants use
different sessions; prior device accuracy gap is confounded by visit/mounting,
with one distance-protocol difference. No guessed correction or new model fit.
Acquisition unchanged, physical checks complete, independent calibration unresolved.
Next prerequisite: independent known-direction/event references, not repeat unit,
bias or raw/processed mapping checks. Model results unchanged.

## Optical event-reference intake completed

[TVS intake and exploratory classifier](../../reports/TVS_OPTICAL_REFERENCE_AND_CLASSIFIER_2026-09-09.md):
32 local participants, 17 HA/15 PD. Raw optical markers and explicit event sides
verified. Optical/INDIP side agreement 1,584/1,584 matched contacts. Corrected
contact coverage 86.4% HA/85.4% PD fails gate. Initial denominator bug allowed
three exploratory fits, 87.46%/87.34% accuracy; saved as exploratory, not admitted.
Corrected intake rerun, no further fits. 163/225 trials usable; 45 missing optical,
17 partial/invalid. No stroke group, no stroke model promotion. Acquisition
unchanged, reference extraction complete, corrected model eligibility failed.
Next is explicit per-contact reference-quality handling, not dropped bad trials.
Independent calibration of Voisard is not established by TVS references.

## Stroke feature prototype packaged

[Executable package and input contract](../../models/prototypes/stroke-phase-hr-v0.1.0/README.md):
full fit on 259 Voisard participants, ten covariate/phase/HR features. Threshold
0.3953767333929809 from inspected development OOF scores, not independent validation.
Three contract tests, serialization parity, example CLI and full 259-row smoke
passed. Invalid rows produce unknown, only age may be imputed. Requires annotated
phase features, not autonomous raw input. Historical nested metrics unchanged.
Acquisition unchanged, feature preprocessing reused, packaging complete, independent
evaluation open. Files use versioned package/examples and processed batch folders.

## Stroke feature benchmark verified

[Executed benchmark](../../docs/classification/BENCHMARK.md): all ten predictors
reconstructed from 1,348 trials for 259 people, only one missing age. Twelve
held-out refits reproduce saved scores; candidate API matches fold predictions.
Ten contract/phase/HR tests passed. Full AUROC 0.897, TP 45/49, healthy FP 6/72,
other FP 56/138. Matched AUROC 0.835, TP 44/49, healthy FP 5/19, other FP 47/76.
Full orthopedic FP 0/44, neurological controls remain difficult, CIPN worsens
versus baseline. Thresholds from inner OOF training only for these metrics;
full-package threshold is not independently evaluated. Acquisition unchanged,
feature reconstruction/benchmark complete, sensor-only and independent validation open.

Historical DUO-GAIT inventory is superseded by the completed magnitude test linked above; directional transfer remains pending.


Experiment records now use notebooks with saved outputs. Notebook 35 contains the
virtual-IMU pilot code, artifact replay tables and embedded plot; its duplicate
runner was removed. Reusable physics modules/tests remain Python. This migration
does not rerun generation or change any clinical/model result.


Local Git organization (2026-09-10): pending work is preserved on the local
`work/classification-local-2026-09-10` review branch in commits grouped by purpose.
A clean working tree does not mean all research is complete or published.
Experiment-notebook migration remains partial. Published main stays at b462795;
review each group before any future publication.


Notebook restructuring (2026-09-10): notebooks 36 and 37 consolidate phase/measurement
and VGA reports with saved artifact-replay outputs. Six standalone report scripts
removed after dependency checks; original source-byte hashes verified against
notebook audit cells. Shared experiment helpers and utilities remain Python.
No new model run, dataset acquisition or clinical evaluation. See the notebook
guide for the current reading path.


Full script inventory (2026-09-10), notebook 38: 139 scripts checked structurally,
27 with Python consumers, 20 utility candidates and 92 notebook-migration
candidates. Eight missing-path flags, six with archive counterparts and two
Mobilise-D paths unresolved. No deletion approval or experiment completion is
implied by these counts. Source/data/evaluation states are unchanged.


## App settings explanation - 2026-09-17

Settings clarity update (2026-09-17): labelled 10/20/30 seconds as recording duration after the countdown, excluding setup time and allowing pauses/early stopping. Added accessible 48-pixel info buttons for Recording duration, Voice guidance, Direction reminders and Practice walk, with one expandable explanation at a time. The duration label remains visible; its explanation is hidden until tapped. Text supports English, Malay and Simplified Chinese. TypeScript and all 58 existing app tests pass. This change is authorized for publication; recording logic is unchanged. No acquisition, preprocessing or clinical evaluation changed.


### Default settings shortcut

Added Use default settings: restores the existing 20-second configuration with voice and direction reminders on and practice off, cancels a playing voice sample, closes help and confirms the selected values. It does not start recording, change language or select consent. All four setting explanations use info buttons; English, Malay and Chinese supported. TypeScript and 58 tests pass. Publication authorized by the user on 2026-09-17.


## [2026-09-17] Browser capture implementation

Browser capture implemented locally: all three Generic Sensor API streams must pass a measured three-second check before shared setup and separate consent. Exports identify browser timing, conversion and platform. Tab-memory recordings require export before refresh/close; sensor loss or hiding interrupts the walk. 67 tests and TypeScript pass; web/Android bundles build. Physical-phone testing and publication remain pending. No clinical acquisition or evaluation.


## [2026-09-17] PWA delivery preparation

At the user's request, the uncommitted Android automatic-update preparation was removed. The shared web build now has manifest, install prompt, icon and offline service worker through the existing Pages deployment. PWA installation does not expand browser sensor access, so the magnetometer remains browser-dependent. Recording remains in tab memory and must be exported before close. Automated checks pass; physical installation/offline testing remains outstanding. No clinical evaluation.


## [2026-09-21] Browser consent and horizontal belt acquisition

Prepared locally: sensor-check consent dialog, browser requests at 60/60/50 Hz, landscape lower-back gate and gravity-projected turn guidance. Raw values remain unchanged. JSON adds experimental stationary-gravity projections and measured sampling diagnostics. See [protocol](../../android/SAMPLING_AND_PLACEMENT.md). Common-rate dataset preprocessing is proposed, not executed. No new data acquisition, training or clinical evaluation. Physical validation and publication pending.


## [2026-09-21] Sampling audit executed and native distribution selected

New notebook 39 executed a paired rate-reduction audit on existing local development data: 161 included Voisard participants and 166 Felius participants. The coverage ledger retains 96 Voisard packet-gap exclusions and two short/invalid-bout exclusions. No new raw data acquisition, classifier training, synthesis or clinical evaluation. Median 8 Hz-band waveform error was 5.30/8.82% at 25 Hz and 1.31/2.31% at 50 Hz for Voisard/Felius respectively. Preserve higher acquisition rates; 25 Hz is not universally validated. The app adds experimental candidate interval alternation, never a neurological or verified bilateral symmetry verdict. The user selected a standalone native Android APK after the PWA restriction was explained. EAS profile linked to the signed-in personal account. APK built successfully; physical validation pending. See [audit](../../docs/classification/PHONE_SAMPLING_AND_ASYMMETRY.md).


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


## [2026-09-21] GitHub update workflow runtime repair

User configured EXPO_TOKEN and the workflow credential-presence check passed. The Expo action then failed installing current EAS CLI because @oclif/plugin-autocomplete requires Node >=22 while the workflow used Node 20. Updated the Android update workflow to Node 22 within the authorized publication scope. No app binary or runtime change. Publishing verification remains in progress.


## [2026-09-21] Build 2 OTA compatibility repair

GitHub token authentication and tests passed, but first CI update fingerprint differed from installed build 2. EAS fingerprint comparison isolated exactly .gitignore and eas.json byte hashes: Git LF normalization differed from the Windows build files. Added a content-hash-gated script restoring the exact known build-2 line endings before CI publication. Modified configs are not rewritten and no runtime hash is overridden. This preserves native-change protection. CI delivery recheck pending.


## [2026-09-21] Automatic Android updates verified

## [2026-09-21] Hands-free setup cues and native review import

Android setup now schedules the spoken five-second cue early enough to account for text-to-speech startup and gives first-time users explicit horizontal lower-back placement instructions. The native review control accepts the app's JSON export and raw long-format CSV through the Android document picker and stores the validated recording locally; files are not uploaded. TypeScript checks and 73 automated tests pass. Current asymmetry remains an experimental alternating candidate-interval descriptor with unknown foot identity and no clinical threshold.

Native build c7aa3b2d-0be1-42fd-84a3-1d0f905033ca finished successfully as Android preview build 3. [APK](https://expo.dev/artifacts/eas/Dc2u_B5IwAcQqQ8orWvaVqB_fm0yAHyTzYSqGTb0NrA.apk)

The walk transition now gives an explicit no-walking countdown, announces the start, and arms capture until movement is detected. The saved duration begins at detected movement to reduce idle lead-in time. All 73 tests pass; publication remains pending review.

History now offers a combined raw CSV export for all saved sessions, retaining session ID, participant metadata, sensor identity, asynchronous timestamps, units and raw axes.

Signal charts retain five-second pages for readability and display performance; each X/Y/Z legend can now be tapped or hovered to highlight that axis, with multilingual explanations.

GitHub Actions run 35563700262 completed successfully after authentication, checks and publication. The update endpoint returned HTTP 200 and Android update 01a0c261-f5cf-761a-b117-fcd21738811e for installed build 2 runtime ead45ff05f56ff8de69ce960cb9af9126a4cc015. EXPO_TOKEN and CI publication are now verified. No replacement APK is needed. Physical cold-launch adoption remains a device check.
