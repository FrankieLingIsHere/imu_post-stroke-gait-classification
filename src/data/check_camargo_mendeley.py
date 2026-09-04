"""Verify Camargo et al. (2021) access; manual browser download is required.

Mendeley Data does not expose a verified public download API for this project.
Manual steps:
1. Open https://data.mendeley.com/datasets/fcgm3chfff/1 in a browser.
2. Select the version shown by the registry and choose Download All (or each
   listed data file).
3. Save the downloads in data/raw/camargo_2021/, extract them, then run
   normalize_dataset_layout.py so usable files land under
   data/raw/camargo_2021/data/.
4. Run this script again to record the resolved access URL and HTTP status.
"""

from __future__ import annotations

from urllib.request import Request, urlopen


URL = "https://data.mendeley.com/datasets/fcgm3chfff/1"


def main() -> None:
    request = Request(URL, headers={"User-Agent": "post-stroke-gait-project/0.1"})
    with urlopen(request, timeout=60) as response:
        print(f"HTTP {response.status}: {response.geturl()}")


if __name__ == "__main__":
    main()
