# Voisard non-stroke hard-negative evaluation

## Purpose and leakage boundary

This is a **differential-specificity evaluation**, not an additional training set. The current full-expanded source/class-balanced magnitude prototype was trained only on the existing healthy/CVA Voisard subset plus Felius and Sint. It was then applied without retraining, calibration, or threshold tuning to the otherwise-unused non-CVA Voisard participants.

The cohort is participant-disjoint from the healthy/CVA subset and shares the published Voisard acquisition protocol: 100 Hz lower-back, left-foot, and right-foot accelerometers. Windows use exactly the primary contract: acceleration magnitude in LB/LF/RF order, 5-second straight-walking windows, and 2.5-second hop, with supplied gait-event bounds excluding the U-turn. It is **not** an independent-site test because it uses the same device/protocol family as Voisard.

The evaluated population is therefore appropriate for the question: *does a stroke-vs-healthy classifier mistake other clinically abnormal gait for stroke?* It must never be relabelled as stroke or silently pooled into binary training.

## Coverage

| Cohort | Participants | Included windows | Mean age (years) | Meaning in this audit |
|---|---:|---:|---:|---|
| ACL | 11 | 166 | 36.7 | orthopedic hard negative |
| CIPN | 19 | 548 | 63.4 | neurological hard negative |
| HOA | 15 | 363 | 69.7 | orthopedic hard negative |
| KOA | 18 | 348 | 69.7 | orthopedic hard negative |
| PD | 24 | 876 | 74.3 | neurological hard negative |
| RIL | 51 | 3,039 | 59.8 | neurological hard negative |
| **Total** | **138** | **5,340** | — | **non-stroke only** |

Two ACL trials did not contain a qualifying 5-second straight-walking span; no signals were fabricated or padded. One participant lacks age metadata.

## Results from the saved full-expanded prototype

Here, “false positive” means a non-stroke participant classified as stroke. It does **not** mean the person is healthy.

| Cohort | Mean stroke probability | FP rate at 0.50 | FP rate at locked 0.78 |
|---|---:|---:|---:|
| ACL | 0.309 | 36.4% (4/11) | 0.0% (0/11) |
| CIPN | 0.494 | 52.6% (10/19) | 26.3% (5/19) |
| HOA | 0.303 | 26.7% (4/15) | 13.3% (2/15) |
| KOA | 0.342 | 38.9% (7/18) | 16.7% (3/18) |
| PD | 0.568 | 62.5% (15/24) | 33.3% (8/24) |
| RIL | 0.615 | 62.7% (32/51) | 49.0% (25/51) |
| **Pooled** | — | **52.2% (72/138)** | **31.2% (43/138)** |

## Interpretation and decision

This baseline is capable of separating the project’s labelled healthy and CVA/stroke cohorts, but it is **not a stroke-specific differential classifier**. Parkinson’s disease, radiation-induced leukoencephalopathy, and chemotherapy-induced peripheral neuropathy frequently receive stroke-like scores. Raising the locked threshold reduces these errors but does not remove them, while the prior RevalExo check showed that higher thresholds also reduce stroke sensitivity.

Do not use these cohorts to claim improvement, train a generic “stroke” label, or alter the frozen RevalExo result. Their correct immediate roles are:

1. Report them as a same-protocol clinical hard-negative stress test.
2. Use their pathology labels later only for a separately specified **open-set/uncertainty or differential-gait** experiment, with every participant isolated from all model-selection folds.
3. Prioritize an independent-site, age-overlapping healthy-plus-stroke cohort for final external validation. The locally available hard negatives expose an important failure mode but cannot fix it by themselves.

## Reproducibility

- Evaluator: `scripts/evaluate_voisard_nonstroke_hard_negatives.py`
- Participant probabilities: `data/processed/voisard_nonstroke_hard_negative_participant_predictions.csv`
- Summary: `data/processed/voisard_nonstroke_hard_negative_summary.csv`
- Trial/window audit: `data/processed/voisard_nonstroke_hard_negative_trial_audit.csv`
- Source release: https://doi.org/10.6084/m9.figshare.28806086

## Binary hard-negative exposure experiment (final output remains binary)

We tested a binary alternative to a three-class model. The network still emits only `P(stroke)`. During training, selected non-CVA windows receive a temporary negative *hard-negative exposure* target; they are **not renamed healthy**, and the original binary baseline remains intact. Each result below holds out one whole pathology cohort (ACL, CIPN, HOA, KOA, PD, or RIL) from exposure training, then scores that unseen cohort. RevalExo was not loaded.

This experiment has two required gates:

1. **Primary-task safety:** in five participant-disjoint healthy/CVA development folds, AUROC, Brier, and balanced accuracy must each be within 0.01 of the source/class-balanced binary baseline.
2. **Unseen-pathology usefulness:** across the 138 held-out hard-negative participants, the 0.50 false-positive rate must decrease by at least 0.10 without any pathology cohort worsening. This minimum prevents selecting a complex mechanism for a trivial shift in one cohort.

| Binary exposure dose | Primary OOF AUROC | Primary OOF Brier | Primary OOF BA | Primary healthy FP/fold | Unseen non-stroke FP at 0.50 | Decision |
|---|---:|---:|---:|---:|---:|---|
| None (baseline) | 0.9544 | 0.0904 | 0.8941 | 2.6 | 52.2% (72/138) | Reference |
| 25% batch exposure | 0.9578 | 0.1404 | 0.8236 | 1.0 | 31.2% (43/138) | Reject: primary calibration and BA fail |
| 7.7% batch exposure | 0.9585 | 0.0838 | 0.8901 | 2.0 | 46.4% (64/138) | Reject: hard-negative gain is only 5.8 points |

The lower dose is encouraging technically: it preserves the primary binary task and does not worsen any held-out pathology cohort. However, its benefit is insufficient for admission, especially for the key residual groups: PD remains 62.5% false positive at 0.50 and RIL remains 60.8%. The larger dose demonstrates the opposite trade-off: it reduces hard-negative errors but damages primary calibration and balanced accuracy. Therefore **neither exposure configuration replaces the binary baseline**.

The useful conclusion is not that a binary final product is impossible. It is that the current public data cannot yet support a binary classifier that is both stroke-sensitive and reliably stroke-specific across other neurological gaits. The final product should retain a binary stroke score, with hard-negative data used only in future, independently replicated outlier-exposure or abstention research after an independent healthy/stroke cohort is secured.

### Reproducibility

- Leave-one-pathology binary exposure: `scripts/benchmark_binary_hard_negative_exposure_loco.py`
- Primary safety gate: `scripts/benchmark_hard_negative_exposure_primary_oof.py`
- 25% results: `data/processed/binary_hard_negative_exposure_loco_metrics.csv` and `binary_hard_negative_exposure_primary_oof_metrics.csv`
- 7.7% results: `data/processed/binary_hard_negative_exposure_loco_metrics_h2.csv` and `binary_hard_negative_exposure_primary_oof_metrics_h2.csv`
