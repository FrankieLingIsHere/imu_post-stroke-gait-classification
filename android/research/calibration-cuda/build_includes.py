"""Explicit declarations supplied implicitly by upstream's unity build.

Only fixes declarations in isolated experimental sources. No executable
algorithm statements, thresholds, iteration limits or calibration data change.
"""
from pathlib import Path
import sys

INCLUDES = {
    "src/solver/calib_solver_init_prep_ei_align_circle_based_impl.cpp": [
        "<opencv2/highgui.hpp>"],
    "src/solver/calib_solver_init_prep_ei_align_impl.cpp": [
        "<opencv2/highgui.hpp>", '"factor/data_correspondence.h"',
        '"core/optical_flow_trace.h"', '"core/rotation_estimator.h"'],
    "src/solver/calib_solver_init_prep_ei_align_line_based_impl.cpp": [
        "<opencv2/highgui.hpp>", '"core/event_preprocessing.h"',
        '"factor/data_correspondence.h"'],
    "src/sensor/event_data_loader.cpp": ['"util/status.hpp"'],
    "src/viewer/visual_colorized_cloud_map.cpp": ['"core/visual_distortion.h"'],
    "src/core/optical_flow_trace.cpp": ['"core/visual_distortion.h"'],
    "src/viewer/visual_gravity.cpp": ['"core/visual_distortion.h"'],
    "src/viewer/visual_lin_vel_drawer.cpp": ['"core/visual_distortion.h"'],
    "src/viewer/visual_ang_vel_drawer.cpp": ['"core/visual_distortion.h"'],
    "src/core/visual_distortion.cpp": [
        '"util/status.hpp"', "<opencv2/calib3d.hpp>",
        '"veta/camera/pinhole_brown.h"', '"veta/camera/pinhole_fisheye.h"'],
}
LINKAGE_EDITS = {
    "include/core/feature_tracking.h": [
        ("inline Eigen::Vector2f Raw() const;", "Eigen::Vector2f Raw() const;"),
        ("inline Eigen::Vector2f Undistorted() const;", "Eigen::Vector2f Undistorted() const;"),
    ],
}


def patch_content(name, content):
    prefix = "".join(f"#include {header}\n" for header in INCLUDES.get(name, [])
                     if f"#include {header}" not in content)
    for before, after in LINKAGE_EDITS.get(name, []):
        if before in content:
            if content.count(before) != 1:
                raise ValueError("Unexpected upstream declaration")
            content = content.replace(before, after)
        elif after not in content:
            raise ValueError("Upstream declaration is missing")
    return prefix + content


def apply(root):
    for name in set(INCLUDES) | set(LINKAGE_EDITS):
        path = root / name
        content = path.read_text()
        patched = patch_content(name, content)
        if patched != content:
            path.write_text(patched)


if __name__ == "__main__":
    apply(Path(sys.argv[1]))
