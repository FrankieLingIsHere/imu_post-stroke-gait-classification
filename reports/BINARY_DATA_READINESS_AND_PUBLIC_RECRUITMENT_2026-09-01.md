# Binary classifier data-readiness and public-data recruitment decision

## Decision

The current data are **sufficient for a research prototype**, including participant-disjoint development, source-aware pooling, controlled robustness experiments, and a pre-specified confidence/abstention feasibility analysis. They are **not sufficient for a clinical-ready binary stroke classifier**.

This distinction is evidence-based rather than a generic sample-size warning:

| Requirement | Current evidence | Decision |
|---|---|---|
| Binary model development | 314 real development participants: 126 healthy and 188 stroke across Felius, Voisard, and Sint | Sufficient for prototype work |
| Participant-disjoint internal testing | Five-fold OOF, 314 participants; AUROC 0.948, Brier 0.097 | Feasible, but not independent validation |
| High-specificity operating rule | OOF threshold 0.78 gives 96.8% pooled specificity but only 63.8% sensitivity; no uniform automatic healthy-clearance rule is supported | Insufficient for a final clinical rule |
| Independent external healthy/stroke evidence | RevalExo: 17 people, only 7 healthy | Insufficient; confidence intervals are too wide |
| Differential specificity | 138 same-protocol non-stroke hard negatives reveal 52.2% stroke calls at 0.50 | Insufficient; clinically abnormal gait is not stroke-specific |
| Age/sex/subgroup assurance | Incomplete cross-source demographic linkage and no independent powered strata | Insufficient |

For orientation, estimating a sensitivity or specificity near 90% with a conventional approximate 95% margin of +/-5 percentage points requires about **139 independent people per class**. The seven external healthy participants are therefore a stress test, not an adequate specificity-validation cohort. This is a planning illustration, not a claim that a single numerical threshold confers clinical readiness.

## Public-source screening rule

A candidate can enter the final three-channel binary training pool only if it has independently identified healthy and stroke participants, raw walking IMU signals, a defensible lower-back plus bilateral-foot mapping, and sufficient metadata to prevent participant overlap. Other sources remain valuable, but only in the role stated below.

| Priority | Source | Evidence and access | Compatible role | Why it is not pooled directly today |
|---|---|---|---|---|
| 1 | Soangra/John passive ADL stroke-vs-healthy | Study reports 14 stroke + 14 healthy older adults; locally observed release has 13 CK stroke + 19 SUP healthy recordings; **100 Hz Dynaport 6-axis IMU** at L5/S1 for 3 days; CC-BY | Activity-domain context or pretraining feasibility only after a validated decoder; **not a gait external test** | Single L5/S1 IMU, no bilateral feet; free-living ADL and author code has group-labelled movement windows rather than verified gait labels |
| 2 | WearGait-PD | 85 age-matched healthy controls + 100 Parkinson's participants; raw 100 Hz full-body IMUs include L4/L5 and bilateral lower-limb sensors; Synapse access | **External healthy and non-stroke hard-negative specificity test**; possible representation-pretraining study | No stroke group; access workflow required; never a direct binary stroke-label expansion |
| 3 | 6MWT lower-back normative dataset | 60 healthy adults, age-balanced 20--79, 50% female; raw 100 Hz lower-trunk accelerometer/gyroscope; Figshare CC-BY | **Independent lower-back healthy normative/external specificity analysis** | Healthy-only and single lower-back sensor; different 6-minute protocol |
| 4 | BLISS | 21 healthy/impaired people including stroke-related dorsiflexor weakness; lower-limb IMU/EMG; CC-BY | Foot/impairment stress test, not final model training | No lower-back sensor and mixed impairment labels |
| Existing | Zhou rehabilitation | 10 stroke participants, raw IMU, longitudinal clinical metadata | Stroke-only auxiliary/OOD or severity analysis | No matched healthy cohort |

### Acquisition recommendation

1. **Soangra/John audit complete — do not download HDF5 derivatives for gait modelling.** The raw release has a directly relevant L5/S1 sensor but no verified gait labels or controlled walking protocol. Preserve it as activity-domain context; do not merge it into the three-channel model or call it a gait external test.
2. **Request/access WearGait-PD next** for the external healthy and clinical hard-negative evaluation that the current project lacks. Its L4/L5 and lower-limb IMUs make a 3-channel adapter technically possible, but its no-stroke composition means it remains evaluation/pretraining-only unless a separate design is approved.
3. **Use the 6MWT normative data only for the lower-back research track.** It is particularly useful to expose age-related healthy variation that the current binary healthy cohort does not adequately cover.

## What should not happen

- Do not download a large healthy-only dataset and call it a binary-training solution.
- Do not label Parkinson's, orthopedic, or neuropathy participants as healthy merely because they are non-stroke.
- Do not tune the binary operating threshold on RevalExo after acquiring new data.
- Do not claim that the 314-person development pool has externally validated age/sex fairness.

## Primary sources

- Soangra/John data release: https://doi.org/10.36837/chapman.000334
- Soangra/John study (confirms the 100 Hz Dynaport 6-axis IMU): https://doi.org/10.3390/s22020598
- WearGait-PD data record: https://www.synapse.org/Synapse:syn52540892/wiki/623751
- WearGait-PD descriptor: https://pmc.ncbi.nlm.nih.gov/articles/PMC13009270/
- 6MWT lower-back dataset: https://doi.org/10.6084/m9.figshare.c.7954157
- 6MWT descriptor: https://doi.org/10.1038/s41597-025-06506-3
- BLISS data record: https://doi.org/10.15125/BATH-01425

## Acquisition status (updated 2026-09-01)

The raw OMX releases and code bundle were downloaded interactively, verified, and normalised under `data/raw/soangra_john_2022/`. The ZIP downloads were removed after inventory verification. The observed raw layout contains 32 DynaPort OMX recordings: 13 CK stroke and 19 SUP healthy. Each header reports 100 Hz accelerometer and gyroscope acquisition.

The code bundle expects optional HDF5 derivatives, while the acquired OMX files need a validated DynaPort decoder. More importantly, the public record and supplied code establish a three-day naturalistic-activity design rather than a gait-labelled dataset. Optional HDF5 downloads are therefore not justified for the current gait-classification question.

Official record: https://digitalcommons.chapman.edu/pt_data/3/

### Carpinella 6MWT acquisition (completed 2026-09-01)

The Figshare `6MWT_IMU_Dataset.zip` download was acquired, matched the
published MD5 (`a23fb3753fc33648624725c33ec9d57e`), and was normalised into
`data/raw/carpinella_2026/`. It contains 60 healthy participants with raw
100 Hz lower-back acceleration and gyroscope arrays, straight-walking/turn
segments, gait events, and participant metadata. The release is a credible
participant-disjoint healthy gait cohort for a lower-back specificity/age
robustness audit; it cannot create bilateral foot channels or a stroke class.
Five documented timestamp-to-signal length mismatches require an explicit
future adapter rule. The verified ZIP was removed after extraction.

The frozen lower-back-only source-balanced baseline was then evaluated on the
author-provided straight-walking paths only. It made 0 stroke predictions among
60 healthy participants at the unchanged 0.50 decision reference (6,109
five-second windows; one-sided practical uncertainty remains: 95% Wilson upper
bound for the false-positive rate is 6.0%). This is a useful healthy
specificity result, but not a replacement for a paired external stroke/healthy
test and not evidence that the three-channel prototype is validated.

### Separate Zenodo stroke-sensitivity component audit (completed 2026-09-01)

The existing 10-participant Zenodo stroke-rehabilitation release was kept fully
separate from the Carpinella cohort and the frozen checkpoints' training data.
At the unchanged 0.50 decision reference, the three-channel baseline detected
9/10 stroke participants (90.0%; 95% Wilson CI 59.6–98.2%) and the lower-back
baseline detected 10/10 (100%; 95% Wilson CI 72.2–100%). No AUROC, balanced
accuracy, or combined sensitivity/specificity has been reported because Zenodo
and Carpinella are different external cohorts with different devices and
protocols. The results are component-wise robustness evidence only.
