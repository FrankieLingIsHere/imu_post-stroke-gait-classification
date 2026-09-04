# Data storage retention audit

Date: 2026-09-03

## Decision

The local `data/` tree occupies approximately **268.681 GiB**. Most of this is
not required by the current Felius + Voisard + Sint classifier. A conservative
cleanup can recover approximately **114.752 GiB** while retaining the active
training sources, frozen paired evaluation source, processed arrays, metrics,
manifests, and executed-notebook evidence.

No files were deleted during this audit.

## Tier A execution completed

Tier A was executed after exact-path and retained-artifact checks. The removed
files totalled **114.753 GiB**, reducing `data/` from 268.681 GiB to
**153.928 GiB**.

The following protected resources were verified after deletion: Felius,
Voisard, extracted Sint, RevalExo, all of `data/processed/`, the NONAN interim
directory, and the candidate/frozen NONAN materialized tensors. The deleted
NONAN archives and redundant ZIP packages are not locally recoverable; they
must be downloaded again from their providers if raw rematerialization is
required. Tier B has not been executed.

## Tier A: safe immediate cleanup

These files do not contribute to the active classifier. Their processed
derivatives, metadata, checksums, and experiment results already exist.

| Path | Size (GiB) | Reason it can be removed | What remains |
|---|---:|---|---|
| `data/raw/nonan_gaitprint/source_packages/candidate_healthy_enrichment/` | 107.319 | Candidate NONAN enrichment failed repeated participant-level admission gates and is not in final training | Two materialized candidate tensors, window metadata, partitions, manifests, compatibility results, and executed notebooks |
| `data/raw/nonan_gaitprint/staged_audit/source_packages/` | 4.073 | Three structural-audit archives have already been materialized and documented | Staged tensors, metadata, manifests, and wiki audit |
| `data/raw/sint_maartenskliniek/IMU_GaitAnalysis-1.1.0.zip` | 2.413 | Redundant compressed copy; the verified 4.695-GiB extraction is the active source | Complete extracted Sint release and processed three-channel/6-DoF tensors |
| Compressed ZIP copies under `data/raw/mobilise_d_cvs/` | 0.947 | The corresponding clinical, main, dictionary, and walking-bout folders are extracted | Extracted files and saved cohort benchmark outputs |

**Tier A recovery: approximately 114.752 GiB.** The resulting `data/` tree
would be approximately 153.929 GiB.

Deleting the NONAN source archives prevents offline rematerialization, but all
source files are publicly reacquirable and the local download manifests retain
participant IDs and checksums. The current model results remain reproducible
from the retained processed tensors.

## Tier B: completed/rejected sources suitable for off-drive storage or deletion

These datasets are not used by the current final classifier. They should be
kept only if near-term follow-up research is planned. Deleting them preserves
the reports and executed results but means the associated raw-data notebook
cannot be rerun until the source is downloaded again.

| Dataset/path | Size (GiB) | Current evidence status | Recommendation |
|---|---:|---|---|
| NONAN frozen source archives | 37.073 | One-sided healthy specificity already scored; cannot be used for model selection | Move off-drive or delete after retaining the 270.8-MiB raw/repaired processed tensors and manifests |
| `data/archive/raw/camargo_2021/data/` | 23.081 | Healthy placement/context source only; no direct binary training role | Delete if no immediate feature-replication rerun is planned; the local `scripts.zip` is not a copy of these data |
| `data/archive/raw/soangra_john_2022/data/` | 17.526 | Naturalistic ADL, not gait-labelled; decoder unresolved; no classifier contribution | Strong deletion/offload candidate |
| `data/archive/raw/duogait_2023/data/` | 17.254 | Healthy-only enrichment and synthesis routes did not improve the final model | Delete/offload; retain processed 500x3 windows, gait cycles, metadata, and negative-result reports |
| `data/archive/raw/gaitex_2026/data/` | 16.445 | Physics-derived direct pooling and matched SSL transfer were rejected | Delete/offload unless future calibrated virtual-sensor work is specifically planned |
| `data/raw/mobilise_d_cvs/walking_bout_dmo/` | 4.364 | Processed DMO data, not raw bilateral IMU; not poolable with classifier | Delete/offload after retaining main clinical tables and saved benchmark outputs |

**Tier B recovery: approximately 115.743 GiB.** Applying Tier A and Tier B
would reduce the whole `data/` tree to approximately **38.186 GiB**.

## Keep locally

| Dataset/artifact | Why it must remain |
|---|---|
| `data/raw/felius_2024/` (0.981 GiB) | Active paired stroke/healthy training source and raw reconstruction reference |
| `data/raw/voisard_2025/` (4.674 GiB) | Active paired training source, demographics, and non-stroke hard negatives |
| `data/raw/sint_maartenskliniek/extracted/` (4.695 GiB) | Active third paired development source and verified lower-back 6-DoF adapter |
| `data/raw/revalexo/` (18.615 GiB) | Paired external reference with restricted/authorised-access considerations; do not discard without a verified institutional backup |
| `data/processed/` | Compact model-ready tensors, predictions, metrics, checkpoints, and audit evidence |
| `data/interim/nonan_gaitprint/` (1.069 GiB) | Compact processed NONAN evidence replacing roughly 148 GiB of source archives for current analyses |
| Dataset manifests, checksums, metadata, reports, wiki, and executed notebooks | Required provenance and interpretation |

## Important qualification

"Removable" means not needed for the current classifier and already represented
by saved evidence. It does not mean scientifically worthless. GAITEX, DUO-GAIT,
NONAN, and Mobilise-D remain legitimate sources for different future research
questions, but retaining hundreds of gigabytes locally is not justified when
their present classifier routes are rejected or complete.
