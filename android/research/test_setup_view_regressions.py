"""Actual desktop OpenCV/production solver regressions; not Android capture proof."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

APP = Path(__file__).resolve().parents[1]
TOOLS = APP / "dist/native-distance-tools"
NATIVE = APP / "modules/gait-camera-calibration/android/src/main/java/expo/modules/gaitcalibration"


class SetupViewRegressions(unittest.TestCase):
    def test_missing_views_blur_recovery_and_bounded_capture_queue(self):
        compiler = TOOLS / "jdk-17.0.20.1+1/bin/javac.exe"
        java = compiler.with_name("java.exe")
        dll = TOOLS / "windows-opencv/opencv_java4120.dll"
        fixture = TOOLS / "lens-fixture.json"
        jars = [TOOLS / "opencv.jar", TOOLS / "json.jar"]
        for item in [compiler, java, dll, fixture, *jars]:
            self.assertTrue(item.exists(), f"Missing local regression prerequisite: {item}")
        sources = [NATIVE / "GuidedLensCalibration.java", NATIVE / "CaptureQueueBudget.java"]
        sources += [APP / f"research/native-tests/{name}.java" for name in
                    ["GuidedLensCalibrationCheck", "CaptureQueueBudgetCheck"]]
        with tempfile.TemporaryDirectory(prefix="gait-setup-views-") as classes:
            cp = os.pathsep.join(map(str, jars))
            result = subprocess.run([str(compiler), "-cp", cp, "-d", classes, *map(str, sources)],
                                    capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(result.returncode, 0, result.stderr)
            for name, args in [("GuidedLensCalibrationCheck", [str(dll), str(fixture)]),
                               ("CaptureQueueBudgetCheck", [])]:
                result = subprocess.run([str(java), "-cp", classes + os.pathsep + cp, name, *args],
                                        capture_output=True, text=True, encoding="utf-8", timeout=180)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                print(result.stdout.strip())


if __name__ == "__main__":
    unittest.main()
