"""Predeclare NONAN healthy-domain partitions before further signal acquisition.

The resulting CSV is a participant-level governance record, not a model split.
It isolates structural-audit participants and mobility-relevant health flags,
then reserves an age- and sex-stratified healthy-only specificity set.  The
remaining eligible people are the only candidates for a future separately
reported source-balanced healthy-enrichment experiment.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
METADATA_ROOT = PROJECT_ROOT / "data" / "raw" / "nonan_gaitprint" / "staged_audit" / "metadata"
OUTPUT_ROOT = PROJECT_ROOT / "data" / "interim" / "nonan_gaitprint"
SEED = 20260902
AUDIT_IDS = {"S030", "S048", "S103"}
FROZEN_FRACTION = 0.25

# Headache/migraine alone is retained: it is reported in the source screening
# table but does not by itself identify a mobility disorder. All listed fields
# below can plausibly affect gait or safety and are excluded from the strict
# healthy reference definition before any signal-level decision is made.
MOBILITY_RELEVANT_FLAGS = [
    "neuropathy",
    "myopathy",
    "vertigo",
    "diabetes",
    "rheumatoid_arthritis",
    "scoliosis",
    "cardiovascular_disease",
    "pulmonary_disease",
    "stroke_cardiac_arrest",
    "major_surgery",
    "seizures",
    "unexplained_falls",
    "joint_replacements",
    "acute_illness",
    "gait_injury",
]


def load_metadata() -> pd.DataFrame:
    sources = [
        ("young", METADATA_ROOT / "young_subject_characteristics.xlsx", "age (years)"),
        (
            "middle",
            METADATA_ROOT / "middle" / "subject_trial_characteristics" / "Gaitprint_subject_characteristics.csv",
            "age",
        ),
        (
            "older",
            METADATA_ROOT / "older" / "subject_trial_characteristics" / "Gaitprint_subject_characteristics.csv",
            "age",
        ),
    ]
    frames: list[pd.DataFrame] = []
    for cohort, path, age_column in sources:
        frame = pd.read_excel(path) if path.suffix == ".xlsx" else pd.read_csv(path)
        frame = frame.copy()
        frame["cohort"] = cohort
        frame["age_years"] = pd.to_numeric(frame[age_column])
        frame["participant_id"] = frame["id"].astype(str).str.replace("S", "", regex=False).astype(int).map("S{:03d}".format)
        frame["gender"] = frame["gender"].astype(str).str.strip().str.lower()
        frames.append(frame)

    data = pd.concat(frames, ignore_index=True)
    for flag in MOBILITY_RELEVANT_FLAGS:
        data[flag] = data[flag].astype(str).str.strip().str.lower().eq("yes")
    data["mobility_flag_count"] = data[MOBILITY_RELEVANT_FLAGS].sum(axis=1)
    return data


def select_frozen_subset(candidates: pd.DataFrame) -> set[str]:
    """Pick ceil(25%) within each age cohort, approximately sex-stratified."""
    rng = np.random.default_rng(SEED)
    selected: set[str] = set()
    for cohort, cohort_data in candidates.groupby("cohort", sort=True):
        target = int(np.ceil(len(cohort_data) * FROZEN_FRACTION))
        by_gender = list(cohort_data.groupby("gender", sort=True))
        quotas = {
            gender: int(np.floor(target * len(group) / len(cohort_data)))
            for gender, group in by_gender
        }
        remainder = target - sum(quotas.values())
        ordered_genders = sorted(
            ((target * len(group) / len(cohort_data) - quotas[gender], gender) for gender, group in by_gender),
            reverse=True,
        )
        for _, gender in ordered_genders[:remainder]:
            quotas[gender] += 1

        chosen_for_cohort: list[str] = []
        for gender, group in by_gender:
            ids = np.asarray(sorted(group["participant_id"].tolist()))
            chosen_for_cohort.extend(rng.choice(ids, size=quotas[gender], replace=False).tolist())
        if len(chosen_for_cohort) != target:
            raise RuntimeError(f"{cohort}: selected {len(chosen_for_cohort)} instead of {target}")
        selected.update(chosen_for_cohort)
    return selected


def main() -> None:
    data = load_metadata()
    data["partition"] = "candidate_healthy_enrichment"
    data.loc[data["mobility_flag_count"] > 0, "partition"] = "excluded_mobility_screen"
    data.loc[data["participant_id"].isin(AUDIT_IDS), "partition"] = "structural_audit_only"

    eligible = data.loc[data["partition"].eq("candidate_healthy_enrichment")].copy()
    frozen_ids = select_frozen_subset(eligible)
    data.loc[data["participant_id"].isin(frozen_ids), "partition"] = "frozen_healthy_specificity"

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    columns = [
        "participant_id",
        "cohort",
        "age_years",
        "gender",
        "mobility_flag_count",
        *MOBILITY_RELEVANT_FLAGS,
        "partition",
    ]
    output_csv = OUTPUT_ROOT / "participant_partitions.csv"
    data.loc[:, columns].sort_values(["partition", "cohort", "participant_id"]).to_csv(output_csv, index=False, quoting=csv.QUOTE_MINIMAL)

    partition_counts = data.groupby(["partition", "cohort"]).size().rename("n").reset_index()
    output_json = OUTPUT_ROOT / "participant_partitions.json"
    output_json.write_text(
        json.dumps(
            {
                "seed": SEED,
                "frozen_fraction_per_cohort": FROZEN_FRACTION,
                "structural_audit_ids": sorted(AUDIT_IDS),
                "mobility_relevant_flags": MOBILITY_RELEVANT_FLAGS,
                "counts": partition_counts.to_dict(orient="records"),
                "frozen_healthy_specificity_ids": sorted(frozen_ids),
                "governance": [
                    "Structural-audit people are excluded from all later test and training roles.",
                    "Frozen healthy-specificity people must not affect preprocessing, adapter fitting, training, calibration, threshold selection, or model selection.",
                    "Candidate healthy-enrichment people remain unavailable until source-contract and frozen-specificity gates pass.",
                    "RevalExo remains the untouched paired external benchmark.",
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Wrote {output_csv}")
    print(f"Wrote {output_json}")
    print(partition_counts.to_string(index=False))


if __name__ == "__main__":
    main()
