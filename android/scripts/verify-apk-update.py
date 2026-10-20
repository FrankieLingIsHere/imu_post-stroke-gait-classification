"""Check packaged JS/update identity before an in-place APK update.

This complements signature/version and fresh-source fingerprint verification.
It does not validate physical tracking or clinical accuracy.
"""
import argparse
import hashlib
import json
import uuid
import zipfile
from pathlib import Path


def inspect_apk(apk: Path) -> dict:
    with zipfile.ZipFile(apk) as archive:
        corrupt = archive.testzip()
        if corrupt:
            raise ValueError(f"Corrupt APK member: {corrupt}")
        manifest = json.loads(archive.read("assets/app.manifest"))
        update_id = str(uuid.UUID(manifest["id"]))
        bundle_sha = hashlib.sha256(archive.read("assets/index.android.bundle")).hexdigest()
        runtime = archive.read("assets/fingerprint").decode().strip()
    return {"embeddedUpdateId": update_id, "bundleSha256": bundle_sha,
            "runtimeVersion": runtime, "apkSha256": hashlib.sha256(apk.read_bytes()).hexdigest()}


def verify_update(candidate: dict, previous: dict) -> None:
    if not previous.get("embeddedUpdateId") or not previous.get("bundleSha256"):
        raise ValueError("Previous release needs its actual embedded update ID and bundle SHA-256.")
    if (candidate["bundleSha256"] != previous["bundleSha256"]
            and candidate["embeddedUpdateId"] == previous["embeddedUpdateId"]):
        raise ValueError("Changed JavaScript reused the embedded update ID. Regenerate "
                         ":app:createReleaseUpdatesResources --rerun-tasks, then assemble and sign again.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("apk", type=Path)
    parser.add_argument("--previous-record", type=Path, required=True)
    args = parser.parse_args()
    candidate = inspect_apk(args.apk)
    previous = json.loads(args.previous_record.read_text(encoding="utf-8-sig"))
    verify_update(candidate, previous)
    print(json.dumps(candidate, indent=2))


if __name__ == "__main__":
    main()
