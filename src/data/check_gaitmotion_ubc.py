"""Verify GaitMotion access; manual browser download is required.

No public data-download API was verified for the UBC Open Collections record.
Manual steps:
1. Open https://open.library.ubc.ca/collections/researchdata/items/1.0435087.
2. Use the record's download controls to obtain every data file and README.
3. Save/extract them under data/raw/gaitmotion_2025/ without renaming files,
   then run normalize_dataset_layout.py so archives and extracted files are
   sorted into archives/ and data/.
"""

from __future__ import annotations

from urllib.request import Request, urlopen


URL = "https://open.library.ubc.ca/collections/researchdata/items/1.0435087"


def main() -> None:
    request = Request(URL, headers={"User-Agent": "post-stroke-gait-project/0.1"})
    with urlopen(request, timeout=60) as response:
        print(f"HTTP {response.status}: {response.geturl()}")


if __name__ == "__main__":
    main()
