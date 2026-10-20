"""Actual Java transport controls; injected solver boundary is not phone evidence."""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


APP = Path(__file__).resolve().parents[1]
NATIVE = APP / "modules/gait-camera-calibration/android/src/main/java/expo/modules/gaitcalibration"


class BootstrapTransportChecks(unittest.TestCase):
    def test_real_java_handoff_resampling_and_startup_coverage(self):
        java_home = Path(os.environ.get("JAVA_HOME") or APP / "dist/native-distance-tools/jdk-17.0.20.1+1")
        suffix = ".exe" if os.name == "nt" else ""
        compiler, java = [java_home / "bin" / (name + suffix) for name in ["javac", "java"]]
        jar = Path(os.environ.get("GAIT_JSON_JAR") or APP / "dist/phone-vio-native/json.jar")
        if not compiler.exists() or not java.exists() or not jar.exists():
            self.skipTest("Requires JDK 17 and org.json jar; set JAVA_HOME and GAIT_JSON_JAR")
        checks = ["VioBootstrapCheck", "OnDeviceFlowCheck", "GuidedCaptureClockCheck", "SetupBaselineGateCheck", "SetupFailureRecoveryCheck", "CameraOpticalPriorCheck"]
        sources = [NATIVE / (name + ".java") for name in ["VioBootstrap", "OnDeviceVio", "OnDeviceProfile", "ReferenceTrackingProfile", "LiveDistanceGate", "GuidedCaptureClock", "SetupBaselineGate", "SetupConvergenceGate", "CameraOpticalPrior"]]
        sources += [APP / "research/native-tests" / (name + ".java") for name in checks]
        with tempfile.TemporaryDirectory(prefix="gait-vio-bootstrap-") as classes:
            compiled = subprocess.run([str(compiler), "-cp", str(jar), "-d", classes, *map(str, sources)], capture_output=True, text=True)
            self.assertEqual(compiled.returncode, 0, compiled.stdout + compiled.stderr)
            for name in checks:
                result = subprocess.run([str(java), "-cp", classes + os.pathsep + str(jar), "expo.modules.gaitcalibration." + name], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("PASS:", result.stdout)
                print(result.stdout.strip())


if __name__ == "__main__":
    unittest.main()
