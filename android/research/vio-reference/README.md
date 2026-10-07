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

`test_vio_reference.py` checks clock convention, acceleration bracketing, profile
identity, units and rotation direction. `vio_reference_fixture.py` supplies an
analytic, non-gait, known-geometry control. It permits rigid gauge alignment only,
not similarity/scale fitting. Its error tolerance verifies harness consistency,
not a clinical accuracy threshold. Real-file diagnostic results and calibration
integrity remain separate, with `distanceReady=false` throughout.
