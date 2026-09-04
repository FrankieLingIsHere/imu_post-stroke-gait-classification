"""Download a predeclared NONAN participant partition with checksum validation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PARTITIONS_PATH = PROJECT_ROOT / "data" / "interim" / "nonan_gaitprint" / "participant_partitions.csv"
MANIFEST_ROOT = PROJECT_ROOT / "data" / "interim" / "nonan_gaitprint"
DOWNLOAD_ROOT = PROJECT_ROOT / "data" / "raw" / "nonan_gaitprint" / "source_packages"
FIGSHARE_API = "https://api.figshare.com/v2"
CHUNK_BYTES = 8 * 1024 * 1024
REPORT_EVERY_BYTES = 128 * 1024 * 1024


def api_get(url: str) -> dict | list:
    with urlopen(Request(url, headers={"User-Agent": "MR-ICT-NONAN-audit/1.0"}), timeout=60) as response:
        return json.load(response)


def md5_file(path: Path) -> str:
    digest = hashlib.md5()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(CHUNK_BYTES), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_files(participants: list[dict]) -> list[dict]:
    young_records = api_get(f"{FIGSHARE_API}/collections/6415061/articles?page_size=100")
    young_articles = {record["title"].removesuffix(".zip"): record["id"] for record in young_records}
    middle = api_get(f"{FIGSHARE_API}/articles/29371796")
    older = api_get(f"{FIGSHARE_API}/articles/27815034")
    middle_files = {record["name"].removesuffix(".zip"): record for record in middle["files"]}
    older_files = {record["name"].removesuffix(".zip"): record for record in older["files"]}

    result: list[dict] = []
    for participant in participants:
        participant_id = participant["participant_id"]
        cohort = participant["cohort"]
        if cohort == "young":
            article_id = young_articles[participant_id]
            article = api_get(f"{FIGSHARE_API}/articles/{article_id}")
            record = next(item for item in article["files"] if item["name"] == f"{participant_id}.zip")
        elif cohort == "middle":
            record = middle_files[participant_id]
        elif cohort == "older":
            record = older_files[participant_id]
        else:
            raise RuntimeError(f"Unknown cohort {cohort!r} for {participant_id}")
        expected_md5 = record.get("computed_md5") or record.get("supplied_md5")
        if not expected_md5:
            raise RuntimeError(f"Publisher metadata has no MD5 for {record['name']}")
        result.append(
            {
                "participant_id": participant_id,
                "cohort": cohort,
                "filename": record["name"],
                "url": record["download_url"],
                "expected_md5": expected_md5,
                "bytes": record["size"],
            }
        )
    return result


def download_file(record: dict, output_dir: Path, retries: int = 5) -> dict:
    destination = output_dir / record["filename"]
    partial = output_dir / f"{record['filename']}.part"
    if destination.exists() and md5_file(destination) == record["expected_md5"]:
        print(f"SKIP verified {record['filename']}", flush=True)
        return {**record, "status": "verified_existing", "path": str(destination)}

    if partial.exists() and partial.stat().st_size == record["bytes"]:
        observed = md5_file(partial)
        if observed != record["expected_md5"]:
            raise RuntimeError(f"MD5 mismatch for complete partial {record['filename']}: {observed} != {record['expected_md5']}")
        partial.replace(destination)
        print(f"PROMOTE verified partial {record['filename']}", flush=True)
        return {**record, "status": "downloaded_verified", "path": str(destination)}

    output_dir.mkdir(parents=True, exist_ok=True)
    offset = partial.stat().st_size if partial.exists() else 0
    headers = {"User-Agent": "MR-ICT-NONAN-audit/1.0"}
    if offset:
        headers["Range"] = f"bytes={offset}-"
    request = Request(record["url"], headers=headers)
    response = None
    for attempt in range(1, retries + 1):
        try:
            response = urlopen(request, timeout=120)
            break
        except (HTTPError, URLError) as exc:
            if attempt == retries:
                raise
            wait_seconds = 15 * attempt
            print(
                f"RETRY {record['filename']} after {type(exc).__name__} "
                f"({getattr(exc, 'code', 'network')}); waiting {wait_seconds}s "
                f"[{attempt}/{retries}]",
                flush=True,
            )
            time.sleep(wait_seconds)
    assert response is not None
    with response:
        append = response.status == 206 and offset > 0
        if not append:
            offset = 0
        mode = "ab" if append else "wb"
        written = offset
        next_report = ((written // REPORT_EVERY_BYTES) + 1) * REPORT_EVERY_BYTES
        print(f"START {record['filename']} ({record['bytes'] / 1e9:.2f} GB)", flush=True)
        with partial.open(mode) as handle:
            while True:
                chunk = response.read(CHUNK_BYTES)
                if not chunk:
                    break
                handle.write(chunk)
                written += len(chunk)
                if written >= next_report:
                    print(f"PROGRESS {record['filename']} {written / record['bytes']:.1%}", flush=True)
                    next_report += REPORT_EVERY_BYTES

    if partial.stat().st_size != record["bytes"]:
        raise RuntimeError(f"Incomplete {record['filename']}: {partial.stat().st_size} of {record['bytes']} bytes")
    observed = md5_file(partial)
    if observed != record["expected_md5"]:
        raise RuntimeError(f"MD5 mismatch for {record['filename']}: {observed} != {record['expected_md5']}")
    partial.replace(destination)
    print(f"DONE {record['filename']}", flush=True)
    return {**record, "status": "downloaded_verified", "path": str(destination)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--partition", default="frozen_healthy_specificity")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    import pandas as pd

    participants = pd.read_csv(PARTITIONS_PATH)
    selected = participants.loc[participants["partition"].eq(args.partition), ["participant_id", "cohort"]].sort_values("participant_id")
    if selected.empty:
        raise RuntimeError(f"No participants found for partition {args.partition!r}")
    records = source_files(selected.to_dict(orient="records"))
    total_bytes = sum(record["bytes"] for record in records)
    print(f"Partition {args.partition}: {len(records)} participants, {total_bytes / 1e9:.2f} GB compressed", flush=True)
    if args.dry_run:
        for record in records:
            print(f"PLAN {record['participant_id']} {record['cohort']} {record['filename']} {record['bytes'] / 1e9:.2f} GB")
        return

    output_dir = DOWNLOAD_ROOT / args.partition
    manifest_path = MANIFEST_ROOT / f"download_manifest_{args.partition}.json"
    existing = {}
    if manifest_path.exists():
        existing = {
            item["participant_id"]: item
            for item in json.loads(manifest_path.read_text(encoding="utf-8"))
            if item.get("status") in {"downloaded_verified", "verified_existing"}
        }
    results = []
    for record in records:
        result = download_file(record, output_dir)
        results.append(result)
        existing[record["participant_id"]] = result
        ordered = [existing[item["participant_id"]] for item in records if item["participant_id"] in existing]
        manifest_path.write_text(json.dumps(ordered, indent=2), encoding="utf-8")
    print(f"Wrote {manifest_path}", flush=True)


if __name__ == "__main__":
    main()
