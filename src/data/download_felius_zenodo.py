"""Download Felius et al. (2024) from the public Zenodo REST API.

The registry's search-only entry was resolved against the paper and Zenodo to
record 11045239 (DOI 10.5281/zenodo.11045239). Files are retained unchanged
under data/raw/felius_2024/ before local sorting. Run
normalize_dataset_layout.py after extraction so usable files land under
data/raw/felius_2024/data/. Do not infer CSV columns or sensor labels until
the archive has been opened and inspected.
"""

from __future__ import annotations

import argparse

from dataset_download_utils import RAW_ROOT, download_files, get_json, print_tree


RECORD_ID = 11045239
API_URL = f"https://zenodo.org/api/records/{RECORD_ID}"
DESTINATION = RAW_ROOT / "felius_2024"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata-only", action="store_true")
    args = parser.parse_args()
    record = get_json(API_URL)
    files = [
        {
            "name": item["key"],
            "download_url": item["links"].get("content") or item["links"]["self"],
            "size": item.get("size"),
        }
        for item in record["files"]
    ]
    print(f"Zenodo title: {record['metadata']['title']}")
    print(f"Repository files: {[item['name'] for item in files]}")
    if not args.metadata_only:
        download_files(files, DESTINATION)
        print_tree(DESTINATION)


if __name__ == "__main__":
    main()
