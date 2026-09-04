"""Verify MAREA access; manual browser download is required.

The CAISR/Halmstad wiki has no verified public download API for this project.
Manual steps:
1. Open https://mw.hh.se/caisr/index.php/Gait_database in a browser.
2. Follow the MAREA gait-database download instructions and accept any terms.
3. Save/extract the supplied files under data/raw/marea_2017/data/,
   preserving the repository-provided directory and file names.
"""

from __future__ import annotations

from urllib.request import Request, urlopen


URL = "https://mw.hh.se/caisr/index.php/Gait_database"


def main() -> None:
    request = Request(URL, headers={"User-Agent": "post-stroke-gait-project/0.1"})
    with urlopen(request, timeout=60) as response:
        print(f"HTTP {response.status}: {response.geturl()}")


if __name__ == "__main__":
    main()
