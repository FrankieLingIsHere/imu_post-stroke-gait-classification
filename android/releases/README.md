# Native release compatibility

Current local collector package: **GaitTrace 0.3.19 / build 31**, embedded update **8e25fd12**, runtime `7b8003b238a19ac35c4387219076cdd97cf27172`. Signed ARM64 APK: `dist/apk/GaitTrace-0.3.19-build31.apk` (75,014,786 bytes). Certificate matches build 30 for an in-place update without uninstalling. Android and embedded Expo versions, signature, ZIP, native libraries/licenses, current bundle, preview update channel and fresh source runtime are verified. Nothing has been pushed or published through OTA. The added native final-check diagnostics require this new APK once.

First use checks phone setup before participant entry for automatic camera distance. New participant study IDs are generated automatically; manual study labels remain available in worker details. Final-check speech identifies outstanding timing, uncertainty, slow/delayed frames and changing-fit requirements, with one movement-coverage announcement and no obsolete queued coaching after native completion. The software suite passes 296 app tests, TypeScript, native contracts and ten browser flows. Thirty-eight current-screen checks replay retained Android numerical traces; two fresh emulator interaction scenarios cover 39 controls. These are separate layers, not one physical end-to-end walking proof. Phone convergence, audible TTS, clinical distance and older-adult usability remain unverified. Older package notes below are historical.

Previous locally verified signed package was **0.3.16/build 28**, runtime
`e3b6276c02e6ea24b45cf61fbab2dad505152a37`, embedded update `8394c378`.
APK: `dist/apk/GaitTrace-0.3.16-build28-startup-fix.apk`. Native 10MWT boundary unification
and pending personal-posture/setup repairs are included. Certificate matches
build 27 and supports in-place installation. Original build 28 is installed;
Android blocked USB installation of the corrected package, now in Downloads for
manual in-place installation. Corrected launch and fresh-phone setup remain unverified.
Physical distance/clinical acceptance and publication
remain pending. The build-27 record is preserved in `native-0.3.15-build27.json`.

Previous local verified package was **0.3.15/build 27**, runtime
`dc4e096fdfc6970ea21354503969a693255b62e3`, embedded update `bcb3d899`.
Native timing/movement fixes require APK installation. Build-26 physical failure
is retained in `native-0.3.14-build26.json`. New package installation and active update bcb3d899 are physically verified; setup and
independent distance validation are pending; no new publication. Earlier release
sections describe their historical handoffs.


`current-native.json` records the locally verified signed native release.
It is provenance and an OTA compatibility contract, not an APK download or
evidence of clinical accuracy. APKs, build logs, credentials, complete packaging
proofs and publication review remain local under `../dist/releases/` and `../dist/apk/`.

Before publishing a compatible update, run from `android/`:

```powershell
node scripts/verify-native-runtime.cjs
```

This computes the current Android source fingerprint and checks its runtime and
version against the release record. The update workflow runs the same check.
Native/config changes require a freshly verified APK and release record; do not
replace the source fingerprint with an old runtime to make publication pass.

For a local native build, regenerate `:app:createReleaseUpdatesResources` with
`--rerun-tasks`, assemble and sign with the existing certificate, then compare
the actual APK fingerprint against a fresh source calculation. A cached Gradle
output alone is insufficient. Preserve current recordings by installing over
the existing application, never by uninstalling it.

Build 24 contained a stale fingerprint despite its working launch. Build 25
corrects that metadata and includes setup speech/retry/reuse fixes. A corrected
installation is needed once; subsequent compatible JavaScript updates can use
the recorded preview runtime after publication approval.

The first physical build-25 setup exposed a permission-dialog interruption bug.
Its compatible JavaScript correction is packaged locally with the same native
version, certificate and runtime; every native library is byte-identical to the
initial installed package. An incremental build also reused the old embedded
update ID, allowing Expo to load cached JavaScript despite changed APK contents.
Regenerated update resources and recorded the actual fresh embedded ID and
bundle SHA-256. Initial installation proof is retained separately; physical
launch of this corrected bundle is verified: the Redmi shows update 03e822a3 and
its pulled APK matches the package exactly. Setup remains unvalidated. Cold TTS
initialization failed once, then a warm retry completed the first spoken cue but
capture failed during startup. Compatible JS voice readiness/diagnostic fixes
were published after explicit user scope approval as compatible preview OTA
**01a12167...**, at `2026-10-09T16:03:40.034Z`. Native APK publication remains false;
the release record separately tracks the approved OTA. Active OTA and successful
capture still need phone verification. No Git push was performed.
An actual preview/runtime HTTP request verifies Expo serves this exact approved
update. The connected phone is not currently running GaitTrace, so active OTA
delivery cannot yet be checked.

For an in-place APK update, retain the previous release record and run:

```powershell
python scripts/verify-apk-update.py path/to/new.apk --previous-record path/to/previous-native.json
```

The prior record must contain the actual `embeddedUpdateId` and `bundleSha256`.
Changed JavaScript with a reused embedded ID fails verification even when its
native runtime is compatible. Always regenerate update resources for local
incremental APK packaging. Check the active update ID on the phone as well as
the APK digest before physical acceptance. Two synthetic ZIP regression controls
and the real stale/fresh APK check pass. These do not validate motion tracking.


Historical local release: **0.3.14/build 26**, runtime **4180b461...**, embedded update
**149962eb...**. The genuine startup-sample handoff changes native Java/Kotlin,
so build-25 OTA updates cannot apply it. Existing release signing is retained;
install over the app to keep recordings. Physical launch/setup acceptance is
pending. `native-0.3.13-build25.json` preserves the prior APK and the separately
approved, physically active OTA 01a12167. No new publication is approved.
