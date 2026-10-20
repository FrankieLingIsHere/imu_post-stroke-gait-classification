#pragma once
#include <Eigen/Core>

// Fixed-td equivalent of the pinned ProjectionTdFactor row-velocity model.
// Observation order: normalized x/y/z, original pixel u/v, normalized vx/vy.
// Correct to the frame midpoint once; preserve original pixel rows and velocity.
inline void correctFixedTimeObservation(Eigen::Matrix<double,7,1>& f,
                                        double readout, double rows) {
    const double rowOffset = readout * (f[4] / rows - 0.5);
    f[0] -= rowOffset * f[5];
    f[1] -= rowOffset * f[6];
}
