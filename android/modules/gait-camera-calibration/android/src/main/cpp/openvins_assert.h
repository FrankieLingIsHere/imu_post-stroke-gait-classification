#pragma once
#include <stdexcept>
// Upstream invariant failures remain checks in release, but return through JNI.
inline void gait_openvins_check(bool condition) {
  if (!condition) throw std::runtime_error("OpenVINS estimator invariant failed");
}
