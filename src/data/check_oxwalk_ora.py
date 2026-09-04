"""Verify OxWalk access; manual browser download is required.

Oxford ORA provides a public dataset landing page, but no verified simple
download API is used here. Manual steps:
1. Open https://ora.ox.ac.uk/objects/uuid:19d3cb34-e2b3-4177-91b6-1bad0e0163e7
   in a browser.
2. Confirm the title is "OxWalk: Wrist and hip-based activity tracker dataset
   for free-living step detection and gait recognition".
3. Use the ORA file/download controls on that record to obtain every available
   data file and documentation file.
4. Place/extract the files under data/raw/oxwalk_2022/, then run
   normalize_dataset_layout.py so usable files land under
   data/raw/oxwalk_2022/data/.
"""

from __future__ import annotations

from urllib.request import Request, urlopen


URL = "https://ora.ox.ac.uk/objects/uuid:19d3cb34-e2b3-4177-91b6-1bad0e0163e7"


def main() -> None:
    request = Request(URL, headers={"User-Agent": "post-stroke-gait-project/0.1"})
    with urlopen(request, timeout=60) as response:
        print(f"HTTP {response.status}: {response.geturl()}")


if __name__ == "__main__":
    main()
