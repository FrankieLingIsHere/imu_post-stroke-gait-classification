# Offline VIO reference harness

Execution, tables and interpretation are in the existing
[camera/IMU notebook](../../../notebooks/phone_camera_imu_calibration.ipynb).
This folder is reusable build/integration code, not a standalone experiment runner.
The Android application does not load this harness. No native app/version change
or new APK is implied by a successful desktop build.

## Source and scope

- VINS-Mono: `90dabb5ec79946ae42fd2e1e91d4e69aabe1e25d`, repository
  <https://github.com/HKUST-Aerial-Robotics/VINS-Mono>.
- Ceres 1.14.0: `facb199f3eda902360f9e1d5271372b7e54febe1`, repository
  <https://github.com/ceres-solver/ceres-solver>.
- OpenVINS feasibility library: `69488123ed9362dd44b6f28e7f4680abbff1442b`,
  <https://github.com/rpng/open_vins>.

CMake enforces the VINS source identity. The upstream estimator, factors,
initialization, feature manager and marginalization sources are compiled unchanged.
ROS transport/visualization and loop closure are excluded. Small local header
shims supply logging and timestamp/header types. The estimator has static storage,
matching the zero-initialization contract of the upstream ROS executable.

`vio_reference.py` uses a **diagnostic Python frontend**, not the original VINS
feature tracker. It keeps raw pixel rows, all five lens distortion coefficients,
forward/backward LK consistency and calibrated epipolar rejection. An offline
comparison using this wrapper is not a benchmark of the complete unchanged ROS
application. Estimated states must not be labelled clinically validated metres.

Third-party source checkouts, Linux toolchains, libraries and raw/generated files
stay outside source commits. Upstream VINS/OpenVINS are GPL-3.0 projects. A future
distributed binary/application requires compatible licensing and source/notices;
this local research build is not an app-distribution decision.

## Reproduce the local build

The executed environment is Ubuntu 26.04 WSL2, GCC 15.2, OpenCV 4.10, Eigen 3.4,
Boost 1.90 and separately built Ceres 1.14.0. Current system Ceres 2.2 cannot build
the original VINS local-parameterization API unchanged.

Install build dependencies in the isolated Linux research environment:

```sh
apt-get install cmake build-essential libopencv-dev libeigen3-dev \
  libgoogle-glog-dev libboost-dev libboost-filesystem-dev \
  libboost-thread-dev libboost-date-time-dev
```

Use pinned source checkouts in a local dependency directory. Build Ceres with
tests/examples and optional sparse backends disabled; the forced `<limits>` include
is a GCC 15 compatibility setting, not a source modification:

```sh
cmake -S CERES_SOURCE -B CERES_BUILD \
  -DCMAKE_POLICY_VERSION_MINIMUM=3.5 -DBUILD_TESTING=OFF -DBUILD_EXAMPLES=OFF \
  -DMINIGLOG=OFF -DGFLAGS=OFF -DSUITESPARSE=OFF -DCXSPARSE=OFF -DLAPACK=OFF \
  '-DCMAKE_CXX_FLAGS=-include limits' -DCMAKE_INSTALL_PREFIX=CERES_INSTALL
cmake --build CERES_BUILD -j 3
cmake --install CERES_BUILD
cmake -S HARNESS_DIRECTORY -B HARNESS_BUILD \
  -DVINS_SOURCE=VINS_SOURCE -DCeres_DIR=CERES_INSTALL/lib/cmake/Ceres \
  -DCMAKE_BUILD_TYPE=Release
cmake --build HARNESS_BUILD -j 2
```

Replace the capitalized path placeholders with absolute local directories.
The notebook exports inputs and invokes `vins_reference INPUT_DIRECTORY [PREFIX]`.
The optional prefix preserves previous output artifacts. Noise and translation
assumptions are written alongside each input, never silently promoted to calibration.
Native hardware clocks, acceleration including gravity (m/s2), and gyro (rad/s)
are required. No camera upsampling, height-derived distance or route-length scale
fitting is performed. Magnetometer remains in the source ZIP; VINS does not use it.

The optional OpenVINS library uses upstream ROS-disabled CMake. On Boost 1.90,
`boost_system` is header-only and its standalone CMake component is absent. Apply
`openvins-boost190.patch` with `git apply --unidiff-zero` to the isolated checkout,
then configure `ov_msckf` with `ENABLE_ROS=OFF`, `ENABLE_ARUCO_TAGS=OFF` and the same
Ceres path. Build target `ov_msckf_lib`. This build-only compatibility patch is
recorded separately. Successful compilation does not establish rolling-shutter
support, Android integration or physical accuracy; OpenVINS has not replayed these
phone recordings in this batch.

## Verification contract

### Integrated helper selection

`Start phone calibration.cmd` explicitly selects `GAITTRACE_DISTANCE_PIPELINE=fixed-time-rows-quiet-v1`.
`distance_pipeline.py` builds `/root/gaittrace-vio/distance-build-v3` and runs CTest;
the old `reference-build` binary is preserved. Direct Python invocation defaults
to `fixed-time-v2` for historical controls. Corrected configuration sets
`fixed_time_row_correction: 1` and string-valued `replay_start_ns` from a continuous
two-second native-IMU quiet interval before measured motion. Original images/IMU
are retained. Features are extracted from the full capture; the wrapper excludes
the prefix only at estimator input. No frame/IMU clock rescaling or marked-distance
scale fitting. Absence of a qualifying baseline fails and retains the capture.

`/api/distance-health` requires correction/window capabilities in corrected mode.
Reports disclose source/backend/mode revision, binary hash and initialization.
Job keys additionally bind the selected noise-profile bytes. An older completed
report cannot silently substitute for new processing or noise settings.

Fresh full-service executions and actual app TypeScript import/save/reload pass
for five retained physical captures, using simulated phone storage. The altered
start is excluded from accuracy; three of four remaining reported measured trials
return estimates, latest confirmed 3 m at 3.15688 m (+5.23%). Blank synthetic
footage withholds distance. 83 research checks pass. The normal local helper is
active with the exact tested method. Prospective phone accuracy remains pending.


### Fixed-time rolling-shutter investigation - 8 October 2026

Historical isolated-candidate investigation. Integration above supersedes its pending helper work.

The pinned estimator chooses `ProjectionFactor` when `estimate_td: 0`.
That branch omits the row-time correction in upstream `ProjectionTdFactor`,
even when a nonzero readout is loaded. Our original fixed-time distance replay
therefore did **not** apply that row correction. The saved calibration itself
has not been changed.

Experimental YAML `fixed_time_row_correction: 1` corrects normalized image
coordinates before they enter that fixed-time branch, using raw pixel rows,
saved readout and normalized feature velocity. The default remains **0**.
Online time-offset estimation with this option is rejected to prevent double
correction. This implements the upstream first-order row model, not a complete
motion-blur or exposure model. The upstream estimator remains unchanged.

`ctest --test-dir HARNESS_BUILD --output-on-failure` runs 250 analytic cases
against the actual pinned upstream factors. A separate fresh zero-readout
analytic replay has identical states with the flag off/on and 559 initialized
poses, rigid-only RMSE 0.00001035 m. These are synthetic consistency checks.

Fresh isolated replays of five retained phone captures, followed by saved-state
reassessment under the added pose-continuity guard, are recorded in the existing
notebook. The latest confirmed 3 m walk changes from 3.24120 m to 3.15688 m.
Two earlier rejected trials return complete candidate estimates. One still
fails. The altered-start trial remains excluded from accuracy comparisons.
No route-label scale fit, threshold relaxation or saved-result replacement.

A separate notebook experiment excludes initial placement motion using the
first two-second quiet interval before measured motion. It keeps the quiet
baseline and practice, and does not prove anatomical placement. That selection
rule is not yet a production adapter. The opt-in executable was built separately
under `row-investigation-build`; the live helper executable is unchanged.
Before further accuracy testing, integrate explicit opt-in/provenance into the
helper and verify the same saved captures through its complete service path.
Neither replay recovery nor a prospective trial is clinical validation.

`test_vio_reference.py` checks clock convention, acceleration bracketing, profile
identity, units and rotation direction. `vio_reference_fixture.py` supplies an
analytic, non-gait, known-geometry control. It permits rigid gauge alignment only,
not similarity/scale fitting. Its error tolerance verifies harness consistency,
not a clinical accuracy threshold. Real-file diagnostic results and calibration
integrity remain separate, with `distanceReady=false` throughout.
