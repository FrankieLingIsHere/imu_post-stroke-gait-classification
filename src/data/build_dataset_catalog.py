"""Build local dataset manifests for EDA and data-mining notebooks.

The manifests describe what is present locally and where the usable raw roots
are. They do not normalize columns, infer sensor channels, or merge datasets.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_ROOT = PROJECT_ROOT / "data" / "raw"
ARCHIVE_RAW_ROOT = PROJECT_ROOT / "data" / "archive" / "raw"
INTERIM_ROOT = PROJECT_ROOT / "data" / "interim"


DATASETS: dict[str, dict[str, Any]] = {
    "nonan_gaitprint": {
        "display_name": "NONAN GaitPrint healthy reference series (staged audit)",
        "repository": "Springer Nature Figshare",
        "access_link": "https://doi.org/10.6084/m9.figshare.c.6415061.v1",
        "status": "staged_contract_audit",
        "role": "healthy-domain contract audit; not training, calibration, threshold selection, or paired external evaluation",
        "usable_roots": ["staged_audit"],
        "required_paths": [
            "staged_audit/metadata/young_subject_characteristics.xlsx",
            "staged_audit/metadata/middle/subject_trial_characteristics/Gaitprint_subject_characteristics.csv",
            "staged_audit/metadata/older/subject_trial_characteristics/Gaitprint_subject_characteristics.csv",
            "staged_audit/source_packages/S030.zip",
            "staged_audit/source_packages/S048.zip",
            "staged_audit/source_packages/S103.zip",
        ],
        "notes": [
            "Three median-age audit participants (24, 45, and 63 years) are locally retained and reserved for structural audit only.",
            "Each verified archive has 18 raw 200-Hz Noraxon CSV trials with explicit mG acceleration fields for lower spine, left foot, and right foot.",
            "Lower spine is documented lower-thoracic/L1-T12 rather than L5; it is a named LB proxy, never an L5 relabeling.",
            "Before additional download or training, create participant-disjoint frozen healthy-specificity and potential-enrichment partitions.",
        ],
    },
    "gaitex_2026": {
        "display_name": "GAITEX (2026) multimodal treadmill gait dataset",
        "repository": "Zenodo / Science Data",
        "access_link": "https://zenodo.org/records/15729056",
        "status": "audited_synthesis_candidate",
        "storage": "archive",
        "role": "physics-grounded virtual-IMU healthy synthesis and self-supervised representation research only",
        "usable_roots": ["data"],
        "required_paths": [
            "data/austra/ng/qualisys_marker_data_austra_ng.csv",
            "data/austra/ng/xsens_imu_data_austra_ng.csv",
            "data/austra/ng/ik_imus/models/scaled_model_austra_ng.osim",
        ],
        "notes": [
            "The original Zenodo ZIP passed its published MD5 check before removal; the verified extracted release is retained under data/archive/raw/gaitex_2026.",
            "The verified 17.66-GB release contains 19 healthy participants; 18 have complete normal-gait assets, with 17 fully clearing target-cluster QC and one retained for marker-complete segment selection.",
            "It provides synchronized 100-Hz markers, orientation quaternions, and OpenSim models, but no released raw accelerations.",
            "Its recorded trunk sensor is pelvis, not a documented lower-back/L5 placement: do not pool or directly score it with the LB/LF/RF classifier.",
            "A virtual L5 placement and marker-derived acceleration must be defined and validated before any synthesis/pretraining experiment.",
        ],
    },
    "kiel_validation_dataset": {
        "display_name": "Kiel Validation Dataset public healthy subset",
        "repository": "GitHub / Neurogeriatrics Kiel",
        "access_link": "https://github.com/neurogeriatricskiel/Validation-dataset",
        "status": "audited_ineligible",
        "storage": "archive",
        "role": "healthy multi-sensor reference; not compatible with the current lower-back/left-foot/right-foot inference contract",
        "usable_roots": ["preferred_walking"],
        "required_paths": [
            "preferred_walking/pp001_imu_walk_preferred.mat",
            "preferred_walking/pp010_imu_walk_preferred.mat",
        ],
        "notes": [
            "Public release contains ten healthy people only; five younger and five older adults.",
            "The selected preferred-walking subset has raw g-unit acceleration, bilateral foot sensors, and a pelvis sensor.",
            "Do not map pelvis to lower back, resample, pool, or score it with the LB/LF/RF classifier; patient data require a separate request.",
        ],
    },
    "carpinella_2026": {
        "display_name": "Carpinella et al. (2026) 6MWT IMU dataset",
        "repository": "Figshare",
        "access_link": "https://doi.org/10.6084/m9.figshare.29665850.v1",
        "status": "ready",
        "storage": "archive",
        "role": "external healthy lower-back gait specificity and age-robustness cohort",
        "usable_roots": ["data"],
        "required_paths": [
            "data/Subject 1/Data.mat",
            "data/Subject 60/Data.mat",
            "metadata/Data_Summary.xls",
            "metadata/LOCAL_AUDIT.md",
        ],
        "notes": [
            "60 healthy adults completed a controlled 6MWT with a single lower-back/pelvis IMU.",
            "Raw acceleration and gyroscope signals are sampled at 100 Hz; walking segments and gait events are supplied.",
            "Healthy-only and lower-back-only: do not directly pool with the three-channel binary training set.",
        ],
    },
    "voisard_2025": {
        "display_name": "Voisard et al. (2025)",
        "repository": "Figshare",
        "access_link": "https://doi.org/10.6084/m9.figshare.28806086",
        "status": "ready",
        "role": "primary stroke-vs-healthy baseline dataset",
        "usable_roots": ["data"],
        "required_paths": [
            "data/healthy/HS",
            "data/neuro/CVA",
            "data/neuro/PD",
            "data/neuro/CIPN",
            "data/neuro/RIL",
            "data/ortho/ACL",
            "data/ortho/HOA",
            "data/ortho/KOA",
        ],
        "notes": [
            "Actual public archive uses dataset/data/healthy, dataset/data/neuro, and dataset/data/ortho.",
            "Trial folders contain four raw sensor text files, one processed text file, one metadata JSON, and one PNG plot.",
        ],
    },
    "duogait_2023": {
        "display_name": "Zhou et al., DUO-GAIT (2023)",
        "repository": "Zenodo",
        "access_link": "https://doi.org/10.5281/zenodo.7415758",
        "status": "ready",
        "storage": "archive",
        "role": "healthy reference dataset for dual-task/fatigue comparisons",
        "usable_roots": ["data"],
        "required_paths": [
            "data/repository_raw",
            "data/repository_interim",
            "data/repository_processed",
        ],
        "notes": [
            "Zenodo exposes raw.zip, interim.zip, and processed.zip; local copy is extracted into matching folders.",
        ],
    },
    "camargo_2021": {
        "display_name": "Camargo et al. (2021)",
        "repository": "Mendeley Data",
        "access_link": "https://data.mendeley.com/datasets/fcgm3chfff/1",
        "status": "ready",
        "storage": "archive",
        "role": "healthy reference dataset for locomotion and placement exploration",
        "usable_roots": ["data"],
        "required_paths": ["data/README.txt", "data/SubjectInfo.mat"],
        "notes": [
            "Manual browser download required by repository; local folder is expanded with AB subject directories.",
        ],
    },
    "oxwalk_2022": {
        "display_name": "Small et al., OxWalk (2022)",
        "repository": "Oxford University Research Archive",
        "access_link": "https://ora.ox.ac.uk/objects/uuid:19d3cb34-e2b3-4177-91b6-1bad0e0163e7",
        "status": "ready",
        "storage": "archive",
        "role": "healthy free-living wrist/hip reference dataset",
        "usable_roots": ["data"],
        "required_paths": [
            "data/metadata.csv",
            "data/Hip_100Hz",
            "data/Hip_25Hz",
            "data/Wrist_100Hz",
            "data/Wrist_25Hz",
        ],
        "notes": [
            "Manual browser download required by ORA; local folder is expanded with hip/wrist CSV files.",
        ],
    },
    "felius_2024": {
        "display_name": "Felius et al. (2024)",
        "repository": "Zenodo",
        "access_link": "https://doi.org/10.5281/zenodo.11045239",
        "status": "ready",
        "role": "stroke and healthy control comparison dataset/code archive",
        "usable_roots": ["data"],
        "required_paths": [
            "data/Raw_data/Data_Healthy",
            "data/Raw_data/Data_Stroke",
        ],
        "notes": [
            "Zenodo archive is expanded locally; inspect Raw_data before deriving feature assumptions.",
        ],
    },
    "gaitmotion_2025": {
        "display_name": "Zhang et al., GaitMotion (2024)",
        "repository": "UBC Library Open Collections",
        "access_link": "https://open.library.ubc.ca/collections/researchdata/items/1.0435087",
        "status": "ready",
        "storage": "archive",
        "role": "simulated stroke/Parkinsonian gait comparison (healthy volunteers, not patients)",
        "usable_roots": ["data"],
        "required_paths": [
            "data/Normal",
            "data/Shuffle",
            "data/Stroke",
        ],
        "notes": [
            "Manual browser download required by UBC; Normal, Shuffle, and Stroke zip files are extracted locally.",
        ],
    },
    "marea_2017": {
        "display_name": "Khandelwal and Wickstrom, MAREA (2017)",
        "repository": "CAISR/ISLAB, Halmstad University",
        "access_link": "https://mw.hh.se/caisr/index.php/Gait_database",
        "status": "ready",
        "storage": "archive",
        "role": "healthy real-world robustness reference (indoor/outdoor/treadmill, waist/wrist/ankle placement)",
        "usable_roots": ["data"],
        "required_paths": [
            "data/Subject Data_txt format",
            "data/Subject Data_mat format",
            "data/Activity Timings",
            "data/GroundTruth.mat",
        ],
        "notes": [
            "20 healthy adults, 128 Hz Shimmer3 accelerometers at waist/wrist/left ankle/right ankle.",
            "Subjects 1-11 have indoor+treadmill timings, subjects 12-20 have outdoor timings.",
        ],
    },
    "soangra_john_2022": {
        "display_name": "Soangra & John (2022)",
        "repository": "Chapman University Digital Commons",
        "access_link": "https://digitalcommons.chapman.edu/pt_data/3/",
        "status": "ready",
        "storage": "archive",
        "role": "paired lower-back IMU naturalistic-activity cohort; not gait-labelled and therefore context/pretraining only",
        "usable_roots": ["data"],
        "required_paths": [
            "data/stroke",
            "data/healthy",
            "metadata/manifest.csv",
            "metadata/README.md",
        ],
        "notes": [
            "Observed local release: 13 CK stroke and 19 SUP healthy DynaPort OMX recordings.",
            "Native headers specify 100 Hz accelerometer and gyroscope acquisition at the lower back.",
            "The release contains three-day naturalistic activity data, not verified gait labels; raw OMX also requires a validated DynaPort decoder.",
        ],
    },
}


def summarize_folder(path: Path) -> dict[str, Any]:
    files = [item for item in path.rglob("*") if item.is_file()] if path.exists() else []
    dirs = [item for item in path.rglob("*") if item.is_dir()] if path.exists() else []
    return {
        "exists": path.exists(),
        "file_count": len(files),
        "directory_count": len(dirs),
        "bytes": sum(item.stat().st_size for item in files),
    }


def build_manifest(dataset_id: str, config: dict[str, Any]) -> dict[str, Any]:
    raw_root = (ARCHIVE_RAW_ROOT if config.get("storage") == "archive" else RAW_ROOT) / dataset_id
    required = [
        {
            "path": str((raw_root / relative).relative_to(PROJECT_ROOT)),
            "exists": (raw_root / relative).exists(),
        }
        for relative in config["required_paths"]
    ]
    usable_roots = [
        str((raw_root / relative).resolve().relative_to(PROJECT_ROOT))
        for relative in config["usable_roots"]
        if (raw_root / relative).exists()
    ]
    summary = summarize_folder(raw_root)
    complete = (
        config["status"] == "ready"
        and summary["exists"]
        and summary["file_count"] > 0
        and all(item["exists"] for item in required)
    )
    if config["status"] != "ready":
        complete = False
    return {
        "dataset_id": dataset_id,
        "display_name": config["display_name"],
        "repository": config["repository"],
        "access_link": config["access_link"],
        "status": "ready" if complete else config["status"],
        "complete": complete,
        "role": config["role"],
        "raw_root": str(raw_root.resolve().relative_to(PROJECT_ROOT)),
        "usable_roots": usable_roots,
        "required_paths": required,
        "summary": summary,
        "notes": config["notes"],
    }


def main() -> None:
    INTERIM_ROOT.mkdir(parents=True, exist_ok=True)
    catalog = []
    for dataset_id, config in DATASETS.items():
        manifest = build_manifest(dataset_id, config)
        dataset_interim = INTERIM_ROOT / dataset_id
        dataset_interim.mkdir(parents=True, exist_ok=True)
        (dataset_interim / "manifest.json").write_text(
            json.dumps(manifest, indent=2), encoding="utf-8"
        )
        catalog.append(manifest)

    (INTERIM_ROOT / "dataset_catalog.json").write_text(
        json.dumps(catalog, indent=2), encoding="utf-8"
    )
    print(f"Wrote {len(catalog)} dataset manifests under {INTERIM_ROOT}")
    for manifest in catalog:
        status = "READY" if manifest["complete"] else manifest["status"].upper()
        print(
            f"{manifest['dataset_id']}: {status}, "
            f"{manifest['summary']['file_count']} files, "
            f"{manifest['summary']['bytes'] / (1024 ** 3):.3f} GiB"
        )


if __name__ == "__main__":
    main()
