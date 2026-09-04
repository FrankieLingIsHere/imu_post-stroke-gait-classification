# Weekly Progress Report — Week 1

**Reporting date:** 27 August 2026  
**Project:** Deep learning classification of post-stroke gait from wearable IMU data

## 1. Executive summary

This week established a reproducible healthy-versus-post-stroke gait baseline using the Felius and Voisard datasets, audited an additional stroke-rehabilitation dataset from Zenodo, and tested whether multi-source/domain-adversarial learning improves generalization. The source-balanced baseline remains the selected model. It achieved strong internal participant-level discrimination and promising frozen external performance, but the evidence is not yet sufficient for age-general or clinical-ready claims.

## 2. Main findings

### Primary baseline

- Development data: Felius + Voisard.
- 284 participants and 18,511 validated five-second windows.
- Input: three acceleration magnitudes in lower-back, left-foot, right-foot order.
- Validation: participant-disjoint folds, fold-fitted normalization, source-by-label weighting.
- Internal pooled AUROC: approximately 0.957.
- Frozen RevalExo external AUROC: 0.871 across 17 participants.
- RevalExo was excluded from training, normalization, calibration, threshold selection, and model selection.

### Zenodo stroke-rehabilitation dataset

- 10 stroke participants, ages 37–88, approximately 120 Hz.
- 1,465 materialized windows using `SA→LB`, `LF→LF`, and `RF→RF`.
- Masked reconstruction and temporal contrastive pretraining did not improve downstream binary transfer.
- Domain-adversarial training slightly improved internal AUROC (0.961 versus 0.957) but reduced RevalExo AUROC to 0.593.
- Decision: do not include Zenodo in the primary probability. Retain its models as negative-transfer/domain/OOD research artifacts.

### Age and subgroup coverage

- Healthy age coverage is wider than stroke age coverage.
- The linked age audit contains healthy Voisard ages but no age-labelled stroke participants in the same table.
- Existing exploratory age-stratified results are not definitive because subgroup sizes are small.
- RevalExo does not provide individual ages; only cohort-level age summaries are available.
- DUO-Gait has 16 exact-age healthy participants aged 21–35.
- OxWalk has 39 healthy participants in coarse age bands but only hip/wrist accelerometers.
- Neither DUO-Gait nor OxWalk matches the primary bilateral-foot/lower-back input contract.

## 3. Requirement status

**Fulfilled:** participant-level labels, common preprocessing contract, participant-disjoint validation, source-balanced training, internal evaluation, frozen external evaluation, simpler-model comparison, and leakage controls.

**Partial:** calibration, healthy older-adult specificity, explainability, and cross-protocol robustness.

**Not fulfilled:** age-specific stroke validation, broad clinical-severity generalization, and evidence for clinical deployment.

## 4. Work completed this week

- Completed Zenodo full-release audit and extraction.
- Resolved Zenodo sensor aliasing and produced 18-channel and three-magnitude representations.
- Tested masked reconstruction, temporal contrastive pretraining, auxiliary loss, source-specific heads, and domain-adversarial learning.
- Rejected domain-adversarial training for the primary model after frozen external evaluation.
- Added leakage audit and baseline requirement audit.
- Audited healthy-only age sources and sensor compatibility.
- Updated the Obsidian wiki and project log with decisions and limitations.

## 5. Safe work to complete before Thursday

1. Run a final frozen-baseline metrics table covering internal source-specific performance, RevalExo performance, sensitivity, specificity, calibration, and confidence intervals.
2. Add a concise model limitations and intended-use section to the wiki.
3. Create a dataset coverage table showing participant counts, age availability, sensor placement, labels, and permitted role.
4. Package the selected baseline checkpoint and inference configuration without changing the model.
5. Prepare one figure showing the data flow: development sources → frozen baseline → external RevalExo test.
6. Prepare a short decision slide: “research prototype validated; clinical-ready status not yet supported.”

## 5a. Completed report-package actions

Before the report deadline, the following artifacts were added:

- [Frozen baseline metrics table](BASELINE_METRICS_TABLE.md)
- [Dataset coverage table](DATASET_COVERAGE_TABLE.md)
- [Baseline data-flow figure](BASELINE_DATA_FLOW.md)
- [Baseline model configuration](BASELINE_MODEL_CONFIG.md)

There is deliberately no deployment checkpoint yet: the intended threshold and calibration protocol are not clinically specified, so exporting one as a production artifact would overstate readiness.

## 6. Current conclusion for reporting

The project has progressed from exploratory data analysis to a reproducible, externally tested research prototype. The baseline is technically credible for further research, but the current participant diversity and age/clinical metadata are insufficient for a clinical-ready claim. Further progress should prioritize representative subject coverage and pre-specified subgroup validation rather than additional architecture complexity or synthetic patient generation.

## 7. Files supporting this report

- [Baseline requirements audit](../docs/BASELINE_REQUIREMENTS_AUDIT.md)
- [Online data expansion strategy](../wiki/datasets/online-data-expansion.md)
- [Frozen RevalExo metrics](../data/processed/revalexo_external_metrics.csv)
- [Baseline subgroup coverage audit](../data/processed/baseline_subgroup_coverage_audit.csv)
- [Project log](../wiki/log.md)
