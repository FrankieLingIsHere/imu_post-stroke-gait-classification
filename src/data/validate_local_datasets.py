"""Validate local dataset readiness before EDA or modeling.

This script checks the generated dataset catalog, confirms required paths, and
tests any remaining zip files.
"""

from __future__ import annotations

import json
from pathlib import Path
from zipfile import BadZipFile, ZipFile


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_ROOT = PROJECT_ROOT / "data" / "raw"
CATALOG_PATH = PROJECT_ROOT / "data" / "interim" / "dataset_catalog.json"


def test_zip(path: Path) -> str:
    try:
        with ZipFile(path) as archive:
            bad_member = archive.testzip()
    except BadZipFile as exc:
        return f"BAD ZIP: {exc}"
    if bad_member is not None:
        return f"BAD MEMBER: {bad_member}"
    return "OK"


def main() -> None:
    if not CATALOG_PATH.exists():
        raise FileNotFoundError("Run build_dataset_catalog.py first.")

    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    failures: list[str] = []

    for manifest in catalog:
        dataset_id = manifest["dataset_id"]
        if not manifest["complete"]:
            failures.append(f"{dataset_id}: manifest is not complete")
        missing = [
            item["path"]
            for item in manifest["required_paths"]
            if not (PROJECT_ROOT / item["path"]).exists()
        ]
        if missing:
            failures.append(f"{dataset_id}: missing required paths {missing}")
        print(
            f"{dataset_id}: complete={manifest['complete']} "
            f"files={manifest['summary']['file_count']}"
        )

    partials = sorted(RAW_ROOT.rglob("*.part"))
    if partials:
        failures.append(
            "Incomplete partial downloads remain: "
            + ", ".join(str(path.relative_to(PROJECT_ROOT)) for path in partials)
        )

    for archive in sorted(RAW_ROOT.rglob("*.zip")):
        result = test_zip(archive)
        print(f"{archive.relative_to(PROJECT_ROOT)}: {result}")
        if result != "OK":
            failures.append(f"{archive.relative_to(PROJECT_ROOT)}: {result}")

    if failures:
        print("\nValidation failed:")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)

    print("\nValidation passed: all cataloged datasets are complete.")


if __name__ == "__main__":
    main()
