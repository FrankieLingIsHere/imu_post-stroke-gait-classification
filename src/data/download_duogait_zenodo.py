"""Download DUO-GAIT from the public Zenodo REST API.

Registry DOI/record: https://doi.org/10.5281/zenodo.7415758
Destination before local sorting: data/raw/duogait_2023/

The release contains multi-gigabyte archives. The script obtains each current
file URL from Zenodo metadata and preserves its archive name; extraction is
deliberately not automatic so the original archives remain auditable. After
extraction, run normalize_dataset_layout.py to sort repository folders under
data/raw/duogait_2023/data/.
"""

from __future__ import annotations

import argparse

from dataset_download_utils import RAW_ROOT, download_files, get_json, print_tree


RECORD_ID = 7415758
API_URL = f"https://zenodo.org/api/records/{RECORD_ID}"
DESTINATION = RAW_ROOT / "duogait_2023"


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
