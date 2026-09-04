"""Leakage-safe MiniROCKET rescue for the lower-back development model.

The module uses only Felius, Voisard, and Sint development arrays. It combines
new out-of-source MiniROCKET probabilities with the already matched deep
ensemble predictions from notebook 29. RevalExo and NONAN are never loaded.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sktime.transformations.panel.rocket import MiniRocketMultivariate

from src.models.evidence_gated_domain_generalization import (
    bootstrap_paired_delta,
    load_development_data,
    metric_row,
)


SEEDS = (42, 137, 202, 314, 515)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def participant_source_class_weights(meta: pd.DataFrame, indices: np.ndarray) -> np.ndarray:
    """Give each source/class cell equal mass and each participant equal mass within it."""
    frame = meta.iloc[indices][["source", "y", "group"]].copy()
    group_windows = frame.groupby(["source", "y", "group"])["group"].transform("size")
    cell_groups = frame.groupby(["source", "y"])["group"].transform("nunique")
    weights = 1.0 / (group_windows.to_numpy() * cell_groups.to_numpy())
    weights = weights / weights.mean()
    return weights.astype("float64")


def balanced_bias_indices(
    meta: pd.DataFrame,
    train_mask: np.ndarray,
    seed: int,
    per_cell: int = 2000,
) -> np.ndarray:
    """Sample source/class-balanced windows with participant-balanced draws."""
    rng = np.random.default_rng(seed)
    chosen: list[int] = []
    train = meta.loc[train_mask]
    for (_, _), cell in train.groupby(["source", "y"], sort=True):
        groups = np.asarray(sorted(cell["group"].unique()))
        group_draws = rng.choice(groups, size=per_cell, replace=True)
        for group in group_draws:
            candidates = cell.index[cell["group"].eq(group)].to_numpy()
            chosen.append(int(rng.choice(candidates)))
    rng.shuffle(chosen)
    return np.asarray(chosen, dtype=int)


def panel(
    x: np.ndarray,
    indices: np.ndarray,
    mean: float,
    std: float,
) -> np.ndarray:
    values = ((x[indices, :, 0] - mean) / std).astype("float32", copy=False)
    return np.ascontiguousarray(values[:, None, :])


def participant_probabilities(
    meta: pd.DataFrame,
    indices: np.ndarray,
    probabilities: np.ndarray,
) -> pd.DataFrame:
    frame = meta.iloc[indices][["source", "group", "y"]].copy()
    frame["probability"] = probabilities
    return frame.groupby(["source", "group", "y"], as_index=False)["probability"].mean()


def run_minirocket(project_root: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    processed = project_root / "data" / "processed"
    x, meta = load_development_data(processed)
    metric_rows: list[dict] = []
    prediction_rows: list[pd.DataFrame] = []
    for held_out_source in sorted(meta["source"].unique()):
        train_mask = meta["source"].ne(held_out_source).to_numpy()
        train_index = np.flatnonzero(train_mask)
        test_index = np.flatnonzero(~train_mask)
        if set(meta.iloc[train_index]["group"]).intersection(meta.iloc[test_index]["group"]):
            raise AssertionError("Participant leakage in source holdout")
        train_values = x[train_index, :, 0]
        mean = float(train_values.mean())
        std = float(max(train_values.std(), 1e-4))
        weights = participant_source_class_weights(meta, train_index)
        for seed in SEEDS:
            bias_index = balanced_bias_indices(meta, train_mask, seed)
            rocket = MiniRocketMultivariate(
                num_kernels=2000,
                max_dilations_per_kernel=16,
                n_jobs=1,
                random_state=seed,
            )
            rocket.fit(panel(x, bias_index, mean, std))
            train_features = np.asarray(rocket.transform(panel(x, train_index, mean, std)), dtype="float32")
            classifier = LogisticRegression(
                C=1.0,
                solver="liblinear",
                max_iter=2000,
                random_state=seed,
            )
            classifier.fit(train_features, meta.iloc[train_index]["y"].to_numpy(), sample_weight=weights)
            del train_features
            test_features = np.asarray(rocket.transform(panel(x, test_index, mean, std)), dtype="float32")
            window_probability = classifier.predict_proba(test_features)[:, 1]
            people = participant_probabilities(meta, test_index, window_probability)
            result = metric_row(people)
            metric_rows.append(
                {
                    "method": "minirocket_logistic",
                    "held_out_source": held_out_source,
                    "evaluation_source": held_out_source,
                    "seed": seed,
                    **result,
                }
            )
            people = people.assign(
                method="minirocket_logistic",
                held_out_source=held_out_source,
                seed=seed,
            )
            prediction_rows.append(people)
            print(
                f"MiniROCKET complete: {held_out_source} seed={seed} "
                f"BA={result['balanced_accuracy']:.3f} FP={result['false_positives']} "
                f"FN={result['false_negatives']}"
            )
    metrics = pd.DataFrame(metric_rows)
    predictions = pd.concat(prediction_rows, ignore_index=True)
    metrics.to_csv(processed / "lower_back_minirocket_rescue_metrics.csv", index=False)
    predictions.to_csv(processed / "lower_back_minirocket_rescue_predictions.csv", index=False)
    return metrics, predictions


def add_deep_and_heterogeneous(
    project_root: Path,
    rocket_metrics: pd.DataFrame,
    rocket_predictions: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    processed = project_root / "data" / "processed"
    deep = pd.read_csv(processed / "evidence_gated_lower_back_dg_participant_predictions.csv")
    deep = deep.loc[deep["method"].eq("ensemble_all"), [
        "held_out_source", "seed", "source", "group", "y", "probability"
    ]].copy()
    deep["method"] = "deep_ensemble"
    rocket = rocket_predictions[["held_out_source", "seed", "source", "group", "y", "probability", "method"]].copy()
    keys = ["held_out_source", "seed", "source", "group", "y"]
    merged = deep.merge(rocket, on=keys, suffixes=("_deep", "_rocket"), validate="one_to_one")
    heterogeneous = merged[keys].copy()
    heterogeneous["probability"] = (
        merged["probability_deep"] + merged["probability_rocket"]
    ) / 2.0
    heterogeneous["method"] = "heterogeneous_equal"
    prediction_frame = pd.concat([deep, rocket, heterogeneous], ignore_index=True)

    rows: list[dict] = []
    for (method, held_out, seed), frame in prediction_frame.groupby(
        ["method", "held_out_source", "seed"], sort=True
    ):
        rows.append(
            {
                "method": method,
                "held_out_source": held_out,
                "evaluation_source": held_out,
                "seed": seed,
                **metric_row(frame),
            }
        )
    metrics = pd.DataFrame(rows)
    metrics.to_csv(processed / "lower_back_heterogeneous_rescue_metrics.csv", index=False)
    prediction_frame.to_csv(processed / "lower_back_heterogeneous_rescue_predictions.csv", index=False)
    return metrics, prediction_frame


def decision(metrics: pd.DataFrame) -> dict:
    baseline = metrics.loc[metrics["method"].eq("deep_ensemble")]
    candidate = metrics.loc[metrics["method"].eq("heterogeneous_equal")]
    merged = baseline.merge(
        candidate,
        on=["held_out_source", "evaluation_source", "seed"],
        suffixes=("_baseline", "_candidate"),
        validate="one_to_one",
    )
    intervals = {}
    for metric in (
        "balanced_accuracy",
        "specificity",
        "sensitivity",
        "auroc",
        "brier",
        "false_positives",
        "false_negatives",
    ):
        mean, low, high = bootstrap_paired_delta(
            merged.rename(
                columns={
                    f"{metric}_baseline": f"{metric}_erm",
                    f"{metric}_candidate": f"{metric}_candidate",
                }
            ),
            metric,
        )
        intervals[metric] = {"mean_delta": mean, "ci_low": low, "ci_high": high}

    summary = metrics.groupby(["method", "held_out_source"], as_index=False).agg(
        auroc=("auroc", "mean"),
        brier=("brier", "mean"),
        balanced_accuracy=("balanced_accuracy", "mean"),
        specificity=("specificity", "mean"),
        sensitivity=("sensitivity", "mean"),
        false_positives=("false_positives", "mean"),
        false_negatives=("false_negatives", "mean"),
    )
    b = summary.loc[summary["method"].eq("deep_ensemble")]
    c = summary.loc[summary["method"].eq("heterogeneous_equal")]
    worst = {
        "balanced_accuracy_delta": float(c["balanced_accuracy"].min() - b["balanced_accuracy"].min()),
        "specificity_delta": float(c["specificity"].min() - b["specificity"].min()),
        "sensitivity_delta": float(c["sensitivity"].min() - b["sensitivity"].min()),
        "auroc_delta": float(c["auroc"].min() - b["auroc"].min()),
        "mean_brier_delta": float(c["brier"].mean() - b["brier"].mean()),
    }
    noninferior = (
        worst["balanced_accuracy_delta"] >= -0.005
        and worst["specificity_delta"] >= -0.02
        and worst["sensitivity_delta"] >= -0.02
        and worst["auroc_delta"] >= -0.01
        and worst["mean_brier_delta"] <= 0.01
        and intervals["balanced_accuracy"]["ci_low"] >= -0.02
        and intervals["specificity"]["ci_low"] >= -0.05
        and intervals["sensitivity"]["ci_low"] >= -0.05
        and intervals["brier"]["ci_high"] <= 0.02
    )
    error_safe = (
        intervals["false_positives"]["mean_delta"] <= 0
        and intervals["false_negatives"]["mean_delta"] <= 0
    )
    baseline_errors = float((baseline["false_positives"] + baseline["false_negatives"]).mean())
    candidate_errors = float((candidate["false_positives"] + candidate["false_negatives"]).mean())
    error_reduction = (baseline_errors - candidate_errors) / baseline_errors
    material = error_reduction >= 0.10
    result = {
        "accepted": bool(noninferior and error_safe and material),
        "noninferior": bool(noninferior),
        "fp_and_fn_nonincreasing": bool(error_safe),
        "material_total_error_reduction": bool(material),
        "mean_total_errors_baseline": baseline_errors,
        "mean_total_errors_candidate": candidate_errors,
        "relative_total_error_reduction": float(error_reduction),
        "worst_source_deltas": worst,
        "paired_bootstrap": intervals,
        "selection_scope": "development-only repeated leave-one-source-out",
        "frozen_cohorts_loaded": False,
    }
    summary.to_csv(
        Path(metrics.attrs.get("processed", ".")) / "lower_back_heterogeneous_rescue_summary.csv",
        index=False,
    )
    return result


def run(project_root: Path) -> dict:
    processed = project_root / "data" / "processed"
    rocket_metrics, rocket_predictions = run_minirocket(project_root)
    metrics, predictions = add_deep_and_heterogeneous(
        project_root, rocket_metrics, rocket_predictions
    )
    metrics.attrs["processed"] = str(processed)
    result = decision(metrics)
    result["config"] = {
        "representation": "lower_back_acceleration_magnitude",
        "window_samples": 500,
        "minirocket_kernels_requested": 2000,
        "minirocket_bias_windows_per_source_class": 2000,
        "classifier": "participant/source/class-weighted logistic regression C=1",
        "fusion": "equal probability average",
        "threshold": 0.5,
        "seeds": list(SEEDS),
    }
    result["input_sha256"] = {
        "primary": sha256(processed / "validated_acceleration_magnitude_windows_float32.npy"),
        "sint": sha256(processed / "sint_maartenskliniek_external_windows_float32.npy"),
        "deep_predictions": sha256(processed / "evidence_gated_lower_back_dg_participant_predictions.csv"),
    }
    (processed / "lower_back_heterogeneous_rescue_decision.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )
    print(json.dumps(result, indent=2))
    return {"metrics": metrics, "predictions": predictions, "decision": result}


if __name__ == "__main__":
    run(Path.cwd().resolve())
