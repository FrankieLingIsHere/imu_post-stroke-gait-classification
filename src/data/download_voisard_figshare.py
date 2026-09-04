"""Download Voisard et al. (2025) from the public Figshare REST API.

Source record: https://doi.org/10.6084/m9.figshare.28806086
Destination before local sorting: data/raw/voisard_2025/

This script preserves the files exactly as Figshare provides them. Run it
before writing feature code, then run normalize_dataset_layout.py after
extraction so usable files land under data/raw/voisard_2025/data/. Inspect
the local inventory rather than assuming cohort folders, trial folders, file
count, or channel names.
"""

from __future__ import annotations

import argparse

from dataset_download_utils import RAW_ROOT, download_files, get_json, print_tree


ARTICLE_ID = 28806086
API_URL = f"https://api.figshare.com/v2/articles/{ARTICLE_ID}"
DESTINATION = RAW_ROOT / "voisard_2025"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata-only", action="store_true")
    args = parser.parse_args()
    record = get_json(API_URL)
    files = [
        {"name": item["name"], "download_url": item["download_url"], "size": item.get("size")}
        for item in record["files"]
    ]
    print(f"Figshare title: {record['title']}")
    print(f"Repository files: {[item['name'] for item in files]}")
    if not args.metadata_only:
        download_files(files, DESTINATION)
        print_tree(DESTINATION)


if __name__ == "__main__":
    main()
