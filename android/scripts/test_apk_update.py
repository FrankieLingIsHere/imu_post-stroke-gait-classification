"""Release regression controls, using synthetic ZIPs rather than real APKs."""
import importlib.util
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

spec = importlib.util.spec_from_file_location("apk_update", Path(__file__).with_name("verify-apk-update.py"))
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


class EmbeddedUpdateCheck(unittest.TestCase):
    def candidate(self, directory, name, update_id, bundle):
        apk = Path(directory) / name
        with zipfile.ZipFile(apk, "w") as archive:
            archive.writestr("assets/app.manifest", json.dumps({"id": update_id}))
            archive.writestr("assets/index.android.bundle", bundle)
            archive.writestr("assets/fingerprint", "a" * 40)
        return guard.inspect_apk(apk)

    def test_changed_bundle_requires_a_new_embedded_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            old = self.candidate(directory, "old.zip", "00000000-0000-4000-8000-000000000001", b"old JS")
            stale = self.candidate(directory, "stale.zip", old["embeddedUpdateId"], b"fixed JS")
            with self.assertRaisesRegex(ValueError, "reused the embedded update ID"):
                guard.verify_update(stale, old)
            fresh = self.candidate(directory, "fresh.zip", "00000000-0000-4000-8000-000000000002", b"fixed JS")
            guard.verify_update(fresh, old)
            guard.verify_update(old, old)

    def test_missing_previous_identity_is_not_a_verified_update(self):
        with self.assertRaisesRegex(ValueError, "Previous release needs"):
            guard.verify_update({}, {"runtimeVersion": "a" * 40})


if __name__ == "__main__":
    unittest.main()
