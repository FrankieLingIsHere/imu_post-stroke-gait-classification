"""Inspect the local Voisard et al. (2025) dataset structure.

Run after downloading, extracting, and organizing the Figshare data. This
reports the actual hierarchy under data/raw/voisard_2025/data
and checks the manuscript expectation that each trial folder contains seven
files. It intentionally does not infer sensor channels beyond
repository-provided file names.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

from dataset_download_utils import RAW_ROOT


DATA_ROOT = RAW_ROOT / "voisard_2025" / "data"


def main() -> None:
    if not DATA_ROOT.exists():
        raise FileNotFoundError(
            f"{DATA_ROOT} is missing. Extract the Voisard archive and run "
            "normalize_dataset_layout.py first."
        )

    files = [path for path in DATA_ROOT.rglob("*") if path.is_file()]
    print(f"Data root: {DATA_ROOT}")
    print(f"Files: {len(files)}")
    print(
        "Extensions:",
        dict(Counter(path.suffix.lower() or "<none>" for path in files)),
    )

    cohorts: dict[tuple[str, str], set[str]] = defaultdict(set)
    trial_file_counts: Counter[Path] = Counter()
    raw_sensor_codes: Counter[str] = Counter()

    for path in files:
        relative_parts = path.relative_to(DATA_ROOT).parts
        if len(relative_parts) != 5:
            continue
        domain, cohort, participant, trial, file_name = relative_parts
        cohorts[(domain, cohort)].add(participant)
        trial_file_counts[path.parent] += 1
        marker = "_raw_data_"
        if marker in file_name:
            raw_sensor_codes[file_name.rsplit(marker, 1)[1].split(".", 1)[0]] += 1

    print("\nCohorts and participant counts:")
    for (domain, cohort), participants in sorted(cohorts.items()):
        print(f"- {domain}/{cohort}: {len(participants)} participants")

    print("\nTrial folder file-count distribution:")
    for file_count, folder_count in sorted(Counter(trial_file_counts.values()).items()):
        print(f"- {folder_count} trial folders contain {file_count} files")

    print("\nRaw sensor file-name codes:")
    for sensor_code, count in sorted(raw_sensor_codes.items()):
        print(f"- {sensor_code}: {count} files")

    print("\nSample trial folders:")
    for trial_folder in sorted(trial_file_counts)[:10]:
        print(f"- {trial_folder.relative_to(DATA_ROOT)}")


if __name__ == "__main__":
    main()
