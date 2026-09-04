# Notebook entry point

**Current as of 4 September 2026:** the Week 2 sprint report covers 18
leakage-safe experiments and 3 candidate external datasets. The repository has
34 active numbered notebooks, all executed through the current evidence stage.
The public presentation is available as the [Week 2 sprint report](../reports/Week2_Sprint_Report_Post-Stroke_Gait_IMU.pdf).

You do **not** need to read all 34 notebooks to understand the project. The
numbered notebooks preserve the full research and rejection history; the five
notebooks below are the shortest reliable route through the current evidence.

## Ten-minute reading path

1. [01 — Dataset and gait-pattern EDA](01_post_stroke_gait_baseline.ipynb)
   explains the original data and observed stroke-versus-healthy patterns.
2. [02 — ML-readiness audit](02_ml_readiness_audit.ipynb) establishes the
   participant/trial structure, label contract, and leakage-safe unit of split.
3. [29 — Selected lower-back model](29_evidence_gated_source_only_domain_generalization.ipynb)
   contains the current five-seed, leave-one-source-out model-selection result.
4. [30 — FP/FN and test credibility](30_fp_fn_and_test_set_credibility_audit.ipynb)
   shows where the model fails and why the evidence is not yet clinical-grade.
5. [34 — Canonical corrective benchmark](34_canonical_inceptiontime_minirocket_corrective_benchmark.ipynb)
   tests the final architecture corrections and records why model rotation now
   stops.

## Current decision in one paragraph

The primary research track is binary post-stroke-versus-healthy classification
from one lower-back acceleration-magnitude channel. The current development
incumbent is an equal-probability ensemble of compact Inception-style ERM,
HAROOD-style CORAL, and an ERM++-style optimization variant, selected using
participant-disjoint five-seed leave-one-source-out validation across Felius,
Voisard, and Sint. It is a research baseline, not a clinically ready model. The
final corrective benchmark found no reliable replacement: the closest fixed
incumbent/MiniROCKET fusion reduced false positives but increased false
negatives and did not transport safely across sources. Architecture selection
on these 314 participants is now closed. RevalExo and NONAN remain excluded
from model selection.

## Choose a path

| Reader goal | Open these notebooks |
|---|---|
| Understand the data | 01 → 02 → 03 → 05 |
| Reproduce the baseline | 05 → 06 → 07 → 08 → 09 |
| Inspect external evaluation | 11 → 12 → 13 → 30 |
| Understand healthy-data enrichment decisions | 14 → 15 → 17 → 20 → 21 |
| Understand the lower-back model decision | 25 → 28 → 29 → 30 |
| Review rejected rescue methods | 31 → 32 → 33 → 34 |
| Continue the research | Read 29, 30, and 34; freeze the incumbent and work on untouched paired-cohort evaluation |

For the complete phase-by-phase catalog and execution status, see
[notebooks/README.md](README.md). Files under `archive/` are historical and are
not part of the current workflow.
