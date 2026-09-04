"""Normalize ready dataset folders to one local data contract.

After this script runs, every ready dataset uses:

data/raw/<dataset_id>/
  data/       usable repository data for EDA and feature work
  archives/   original compressed downloads, when retained
  metadata/   readmes, manifests, figures, and other side files

"""

from __future__ import annotations

import shutil
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_ROOT = PROJECT_ROOT / "data" / "raw"
READY_DATASETS = [
    "voisard_2025",
    "duogait_2023",
    "camargo_2021",
    "oxwalk_2022",
    "felius_2024",
    "gaitmotion_2025",
    "marea_2017",
]


def move_path(source: Path, destination: Path) -> None:
    if not source.exists():
        return
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source), str(destination))
    print(f"{source.relative_to(PROJECT_ROOT)} -> {destination.relative_to(PROJECT_ROOT)}")


def move_contents(source_dir: Path, destination_dir: Path) -> None:
    if not source_dir.exists():
        return
    destination_dir.mkdir(parents=True, exist_ok=True)
    for child in source_dir.iterdir():
        move_path(child, destination_dir / child.name)


def remove_empty_dirs(root: Path) -> None:
    if not root.exists():
        return
    for path in sorted([p for p in root.rglob("*") if p.is_dir()], reverse=True):
        try:
            path.rmdir()
        except OSError:
            pass
    try:
        root.rmdir()
    except OSError:
        pass


def ensure_buckets(dataset_root: Path) -> None:
    for bucket in ("data", "archives", "metadata"):
        (dataset_root / bucket).mkdir(parents=True, exist_ok=True)


def normalize_voisard(root: Path) -> None:
    move_contents(root / "source" / "dataset" / "data", root / "data")
    move_path(root / "source" / "dataset" / "README.md", root / "metadata" / "README.md")
    move_path(root / "source" / "dataset" / "quick_start", root / "metadata" / "quick_start")


def normalize_duogait(root: Path) -> None:
    move_path(root / "source" / "raw", root / "data" / "repository_raw")
    move_path(root / "source" / "interim", root / "data" / "repository_interim")
    move_path(root / "source" / "processed", root / "data" / "repository_processed")
    shutil.rmtree(root / "source" / "__MACOSX", ignore_errors=True)
    shutil.rmtree(root / "metadata" / "__MACOSX", ignore_errors=True)


def normalize_camargo(root: Path) -> None:
    move_contents(root / "source", root / "data")
    move_path(root / "data" / "README.txt", root / "metadata" / "README.txt")


def normalize_oxwalk(root: Path) -> None:
    move_contents(root / "source" / "OxWalk_Dec2022", root / "data")
    move_path(root / "data" / "README.txt", root / "metadata" / "README.txt")


def normalize_felius(root: Path) -> None:
    move_contents(root / "source" / "RichardFel-VAE-8073887", root / "data")
    for name in (".gitattributes", ".gitignore", "CITATION.cff", "requirements.txt"):
        move_path(root / "data" / name, root / "metadata" / name)


def normalize_gaitmotion(root: Path) -> None:
    move_contents(root / "source" / "extracted", root / "data")
    move_path(root / "source" / "readme.md", root / "metadata" / "readme.md")
    move_path(root / "source" / "figure0.png", root / "metadata" / "figure0.png")
    move_path(root / "source" / "figure1.png", root / "metadata" / "figure1.png")


def normalize_marea(root: Path) -> None:
    move_contents(root / "MAREA_dataset", root / "data")
    move_path(root / "data" / "READ ME.txt", root / "metadata" / "READ ME.txt")
    move_path(root / "data" / "mainScript.m", root / "metadata" / "mainScript.m")


NORMALIZERS = {
    "voisard_2025": normalize_voisard,
    "duogait_2023": normalize_duogait,
    "camargo_2021": normalize_camargo,
    "oxwalk_2022": normalize_oxwalk,
    "felius_2024": normalize_felius,
    "gaitmotion_2025": normalize_gaitmotion,
    "marea_2017": normalize_marea,
}


def main() -> None:
    for dataset_id in READY_DATASETS:
        root = RAW_ROOT / dataset_id
        if not root.exists():
            print(f"{dataset_id}: missing, skipped")
            continue
        ensure_buckets(root)
        NORMALIZERS[dataset_id](root)
        remove_empty_dirs(root / "source")
        remove_empty_dirs(root / "MAREA_dataset")

    print("Normalized ready dataset layouts.")


if __name__ == "__main__":
    main()
