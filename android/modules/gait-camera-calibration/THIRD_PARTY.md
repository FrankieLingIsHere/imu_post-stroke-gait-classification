# Native visual-inertial estimator

On-device setup and live tracking compile OpenVINS commit
`69488123ed9362dd44b6f28e7f4680abbff1442b` from
https://github.com/rpng/open_vins (GPL-3.0-or-later). ROS transport, simulations
and executables are excluded. The Android adapter sets runtime options directly,
uses measured Camera2 midpoint timestamps and applies a local rotational
rolling-shutter compensation. That compensation is a local extension, not a
claim that unchanged OpenVINS supports a full rolling-shutter sensor model.
Boost 1.84.0 headers/filesystem use the Boost Software License 1.0:
https://www.boost.org/LICENSE_1_0.txt. The release archive SHA-256 is pinned in CMake.

The phone distance engine compiles VINS-Mono commit
`90dabb5ec79946ae42fd2e1e91d4e69aabe1e25d` from
https://github.com/HKUST-Aerial-Robotics/VINS-Mono (GPL-3.0).
The Android wrapper and linked derivative must be distributed consistently with
GPL-3.0, with corresponding source and build instructions. This local build is
not publication approval. Upstream estimator sources are fetched unchanged.

Ceres Solver 1.14.0 (`facb199f3eda902360f9e1d5271372b7e54febe1`), BSD-3-Clause:
https://github.com/ceres-solver/ceres-solver

Eigen 3.3.7 (`36b95962756c1fce8e29b1f8bc45967f30773c00`), MPL-2.0:
https://github.com/eigenteam/eigen-git-mirror

OpenCV 4.12.0, Apache-2.0: https://github.com/opencv/opencv

Sources and their license files are retained in the generated CMake dependency
directory. Generated dependencies and binaries do not belong in Git source commits.
The app needs a newly built native APK; JavaScript updates cannot add this engine.
