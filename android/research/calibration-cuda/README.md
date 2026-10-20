# Experimental GPU calibration benchmark

This builds a separate iKalibr/Ceres environment for a CPU/CUDA comparison. It
does not alter `gaittrace-ikalibr:reference-v1`, the desktop helper's default,
saved phone calibration or the Android app. CUDA accelerates supported linear
algebra; capture conversion, residual/Jacobian evaluation and other solver work
still use CPU. Building C++ software also uses CPU.

The authors' current CTraj/veta repository URLs returned 404 on 8 October 2026
([upstream issue](https://github.com/Unsigned-Long/iKalibr/issues/46)). Their
published Docker image retains the pinned source and dependency installs in an
earlier layer. `recover_sources.py` verifies that layer's SHA-256, the source
commits and unmodified tracked files. It extracts into a separate local context
with bounded paths and preserves upstream licenses. It does not modify the
working CPU image or substitute a different calibration algorithm.

Run inside WSL as root, using the existing downloaded authors' image blobs:

```sh
python3 /path/to/calibration-cuda/recover_sources.py /opt/gaittrace-calibration-build-context
cp /path/to/calibration-cuda/{Dockerfile,CMakeLists.txt,solver_probe.cpp,build_includes.py} /opt/gaittrace-calibration-build-context/
tar -C /opt/gaittrace-calibration-build-context -cf /opt/gaittrace-calibration-build-context/authors-source.tar home/iKalibr/src
docker build --target solver -t gaittrace-ikalibr:cuda-solver-v1 /opt/gaittrace-calibration-build-context
```

The Ceres source is the original installed 2.2.0 commit, rebuilt with `USE_CUDA`,
CUDA 12.9.1 and architecture 120 for the local RTX 5060. CTraj is rebuilt against
that shared Ceres library. iKalibr uses the recovered source with explicit
header includes and out-of-line declarations needed for non-unity compilation
(see `build_includes.py`). The function bodies are preserved without algorithm
edits, Release/-O3 and at most two compiler jobs to bound template-compilation memory.
The original binary/image remains available for baseline and recovery. This
hardware-specific recipe is experimental, not a portable app build dependency.

`solver_probe` is a synthetic known-answer capability check. Its runtime is not
an estimate of real calibration performance. `benchmark.py` runs the rebuilt
binary directly against a fresh copied real bag and fixed measured SfM, with two
threads and either `UseCudaInSolving=false` or `true`. It verifies dynamic Ceres
linkage, collects GPU samples, records exact executable/library/image/input
identities, checks all solver convergence reports and retains failure evidence.
It never imports or replaces a profile and always labels distance unvalidated.

`pipeline.py` validates preparation and finishing in a fresh volume. It reuses
the production capture converter, runs the rebuilt upstream initializer, exports
the same bounded measured-keyframe plan and finishes with `benchmark.run(prepared=True)`.
Run the unchanged `calibration-companion/sfm.py` between those stages, with the
pinned COLMAP image and an explicit CPU/CUDA selection. Export uses the existing
workspace hash checks. `review.py` checks saved outputs, actual convergence,
camera/lens binding, finite fitted reprojection residuals and the existing
camera/IMU geometry/timing bounds; it never certifies physical distance accuracy.

The executed full-pipeline cells in the existing notebook retain both failures
and successful retries. The app import contract recognizes only the exact
experimental image and binary identities as a review candidate. Original
author-image results remain supported. Loopback service delivery uses the actual
TypeScript poll/import/save code with simulated phone storage; physical Android
network delivery and saved phone state are separate from that software check.

Execute and save experiments in `notebooks/phone_camera_imu_calibration.ipynb`.
Use fresh disposable Linux volumes, a read-only saved capture at `/source`, and
an ignored local results folder at `/evidence`. Source/build trees, Docker images,
raw capture and benchmark logs remain local. Compare convergence, parameters and
timing before considering a production backend change. The experimental binary
was built successfully through an incremental/resumed compilation; this Dockerfile
consolidates the required fixes. A separate cold rebuild of the consolidated
recipe has not been performed.

## GPU calibration experiment - 8 October 2026

Built a separate CUDA-capable Ceres 2.2/iKalibr environment and actually executed
two CPU and two CUDA final solves against the same retained real capture and
fixed measured SfM. The same rebuilt executable, Ceres library and two-thread
configuration were used for both backends. Median final-solver time is
**355.09 s CPU versus 139.07 s CUDA**, a **60.8% reduction**.
All seven solver reports converge in each run. CUDA GPU activity is recorded;
this is a real calibration comparison, distinct from synthetic capability checks.
The timing excludes raw import, image preparation and SfM reconstruction.
One upstream initialization report has zero residuals and `Iterations: -2` in
all four runs. It is retained as an empty stage, not independent proof of
successful geometry calibration. Final weighted costs are about 492-495, but
those internal fits do not establish accuracy against measured physical geometry.

The strict numeric parity check fails. First-pair camera/IMU translation differs
5.02 mm, rotation 0.0701 degrees, time offset 0.353 ms and readout 0.127 ms.
Initialization also varies across replays. The executed notebook stores the
within-backend repeatability and cross-backend parameter/cost review, so these
differences are not attributed solely to GPU precision or called clinical error.
Translation varies **6.04 mm between CPU repeats** and **2.66 mm between CUDA
repeats**; paired cross-backend differences are 5.02 mm and 3.58 mm. Two repeats
on one development capture are insufficient to establish accuracy/equivalence.
At this solver-only checkpoint the production default/profile were preserved.
The subsequent complete-pipeline validation below supersedes the pending
processing check; independent physical accuracy remains unvalidated.
No independent distance validation was done.

The CTraj/veta repository URLs are unavailable, but the authors' distributed
Docker image retains the matching source in an earlier layer. Recovery verifies
the layer digest, exact source/dependency commits and unchanged raw tracked files.
The experimental non-unity build needs explicit includes and out-of-line accessor
declarations; function bodies, thresholds and iteration limits are preserved.
The build and CUDA controls passed through incremental/resumed compilation.
The consolidated Docker recipe has not had a separate cold-build run.

Source recipe and research worker: `android/research/calibration-cuda/`.
Fresh executions and saved-output analysis are in the existing
`notebooks/phone_camera_imu_calibration.ipynb`. Raw capture, recovered upstream
source/dependency trees, Docker images, build logs and benchmark products stay
local/ignored. This experiment does not change the helper's CPU default or the
Android APK. No new APK, phone capture, Git push or OTA is required/performed.
All 64 existing research unit checks pass. The four real calibration runs and
the separate synthetic CUDA controls are recorded distinctly in the notebook.

## Complete calibration pipeline validation - 8 October 2026

Fresh all-CPU and GPU-assisted processing both passed on the same retained real
development ZIP. Each started in an empty Linux volume: unchanged capture
conversion, rebuilt upstream image preparation, new COLMAP feature extraction,
matching and reconstruction, final iKalibr solve, output export and result checks.
No old bag, reconstruction or calibrated parameter output was reused. Same
experimental executable/library, two threads and original algorithm limits.

| Stage / wall seconds | All-CPU control | GPU-assisted |
| --- | ---: | ---: |
| Raw import, conversion and preparation | 79.86 | 81.07 |
| Fresh reconstruction | 92.70 | 63.22 |
| Final solve and result generation | 394.32 | 148.92 |
| Complete processing | 566.89 | 293.21 |
| Including result export | 600.68 | 326.94 |

Including export, GPU assistance takes **45.6% less time**.
This is one complete run per backend on one capture. The current production
helper already uses GPU COLMAP when available; this all-CPU control is not a
measurement of the existing mixed production default. Conversion, mapping and
residual/Jacobian work are not all on GPU. Actual final-solver GPU activity is
confirmed (100% peak, engine PID present); the CPU control records 0%.

Both reconstructed one coherent model, registering 185/195 and
176/195 measured keyframes. All seven final-solver reports converge
in each run, including one empty initialization report that is not geometry
evidence. Camera/lens binding, unchanged raw ZIP digest, finite reprojection
residuals, rotation matrices and existing research geometry/timing bounds pass.
Fitted reprojection P90 is **1.382 pixels CPU / 1.369 pixels GPU**;
these are in-sample residuals, not held-out accuracy. Different CPU/GPU SfM
constraints explain why this is not a fixed-input numerical-equivalence test.
Paired extrinsics differ 4.08 mm / 0.1106 degrees,
time offset 0.338 ms and readout 0.345 ms.
No claim of clinical equivalence or improved distance accuracy is made.

The first fresh attempt exposed ROS Python-path initialization and was fixed.
Failure evidence remains in the notebook. Saved-output review then completed;
plotting dependency failures were preserved and resolved using the existing
plotting environment, without rerunning calibration or installing dependencies.

Actual loopback HTTP upload/job delivery plus the app's TypeScript poll/import/
save/reload logic pass for both actual outputs, with simulated phone storage.
Forged readiness, device binding and binary identity are rejected. The import
contract now explicitly recognizes this exact experimental image/binary as a
review candidate and retains original author-image support. This is not a
physical Android network/storage test. No installed app or saved phone profile
was changed. All 201 app tests, TypeScript and 64 research tests pass.

The complete processing path is now validated on this capture. Production
defaults remain unchanged; all candidate/full/distance readiness flags remain
false. Independent walking-distance validation, measured phone noise and
physical camera/IMU geometry remain separate unresolved research checks.
Fresh executions, retained failures, tables and analysis are saved in
`notebooks/phone_camera_imu_calibration.ipynb`. Raw/generated files stay local
under `android/dist/calibration-cuda-benchmark/full-pipeline-retry/`.
No new APK, cold-image rebuild, Git push or OTA publication was performed.
