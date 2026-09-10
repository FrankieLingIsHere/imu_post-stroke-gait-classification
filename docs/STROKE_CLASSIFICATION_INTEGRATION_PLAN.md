# Post-Stroke Gait Classification: Integration and Next-Stage Plan

Current implementation: [workspace guide](classification/README.md) and [weekly progress](classification/WEEKLY_PROGRESS_2026-09-07.md). Completed public results are in Week 3 commit `b462795`; remaining local files include both completed work and active research.

> Current user-authorized direction: working research prototypes may use lower
> gates, with historical validation failures preserved. See
> [prototype policy and dataset roles](RESEARCH_PROTOTYPE_POLICY_2026-09-09.md).
> TVS contact-laterality prototype is packaged and CLI verified; it is not a stroke model.
> Stroke phase+HR prototype is now [packaged and CLI verified](classification/README.md).
> [Feature audit and held-out benchmark](classification/BENCHMARK.md) completed.
> Full-development threshold remains exploratory; no new independent validation.

Status: current implementation handoff, updated 2026-09-09.
Use [the evidence map](CLASSIFICATION_EVIDENCE_MAP.md) and
[wiki handoff](../wiki/concepts/classification-project-status.md) before new work.

## Current methodological direction

[Packet correction executed](../reports/PACKET_ALIGNMENT_CORRECTION_2026-09-09.md):
versioned native loader verified against provider processing on 1,348 trials;
259-person feature comparison rerun. Frozen v0.2.0 gives 89/138 non-stroke
positives both before and after correction on identical 5,340 windows; zero
participant calls change. Other-pathology FPR in the combined feature model also
stays 50.7%. Alignment is corrected but stroke specificity remains unresolved.
Use src/data/voisard_aligned.py for new native extraction; historical artifacts
remain preserved. This experiment is closed, not a pending rerun. No replacement
model or threshold is admitted. Independent diagnostic and measurement validation
remain open; broader input migration must be versioned explicitly.

## Bilateral phase experiment completed

[Executed phase comparison](../reports/BILATERAL_PHASE_COMPARISON_2026-09-09.md):
all 259 selected participants retained across the existing folds, 1,348 trials,
1,345 complete trial feature sets and no missing participant feature sets.
Adding phase features to nuisance+cadence reduces other false positives 73 to 64/138,
but stroke detections fall 43 to 41/49. Matched comparison: other FP 35 to 26/76,
stroke detections 34 to 30/49. Both fail the pre-fit sensitivity-preserving gate.
Secondary combined+phase matched result: other FP 43 to 31/76 with detections
unchanged at 31/49. No promotion. Baseline reproduction and four unit tests passed.
This is completed annotation-assisted development evidence, not sensor-only or
independent validation. No downloads or release changes. Do not rerun this test.
The follow-up [nested threshold experiment](../reports/PHASE_NESTED_THRESHOLD_2026-09-09.md)
is now completed: 72 inner fits, training-only 90% sensitivity thresholds, both
primary gates failed. Primary full: 41/49 stroke detected, 59/138 other FP, versus
baseline 44/49 and 61/138. Matched: 42/49 and 61/76 versus 44/49 and 69/76.
Secondary matched combined+phase detects 45/49 but calls 62/76 other and 13/19
healthy positive. Stop threshold sweeps on this representation. No model admitted.
The completed phase/threshold experiments remain closed. The subsequent
stance-variability feasibility result and current measurement priority are below. Neither stroke diagnosis nor a renamed abnormality score
is validated by these results. Independent cohort and measurement evidence remain
required. Acquisition unchanged, phase preprocessing reused, evaluation complete.

## Current checkpoint

| Work | Verified current result |
|---|---|
| Frozen v0.2.0 | 15-member lower-back magnitude model unchanged; not clinically validated |
| Voisard exact-weight stress | 89/138 non-stroke positive; pooling still leaves 87/138 |
| TVS metadata | 40/40 acquired |
| TVS raw signals | 36 participants acquired; four metadata-excluded raw files not acquired |
| TVS preprocessing/evaluation | Complete: 34 participants, 117 windows; six explicit exclusions |
| TVS positive calls | 17/18 healthy, 16/16 PD; inspected/new strata recorded separately |
| Input-transfer and mechanism checks | Complete; no tested units/normalization bug, exact root cause unproven |
| Differential objective implementation | 27 GPU fits completed; three-class candidate failed all three seed gates |
| Input validity | Optional API/CLI rejects constant/nonfinite windows with no score; valid inputs unchanged |

## Latest implementation decision

[Executed implementation and results](../reports/DIFFERENTIAL_GAIT_IMPLEMENTATION_2026-09-09.md): on 259 same-protocol
Voisard participants, compare primary binary, matched binary exposure and explicit
three-class objectives using the same backbone, three disjoint folds and three
seeds. Whole pathology groups are held out. Three-class mean stroke sensitivity
fell from 87.76% to 68.71%, despite other-pathology FPR falling from 53.38% to
40.58%. Matched binary exposure achieved 35.99% FPR at the same mean sensitivity.
Reject promotion; do not rerun this candidate or tune a favourable threshold.
These are controlled single-member development comparisons, not frozen-ensemble
or independent-site performance estimates. TVS was not used for this training.

`models/input_validity.py` is an implemented, opt-in research inference wrapper.
Constant/nonfinite windows return null scores and explicit rejections, never
healthy predictions. It is not a gait detector and does not fix moving healthy
TVS false positives. The frozen API/weights and prior results remain unchanged.
Six focused tests plus real API/CLI smoke verification passed. No process remains
running and no model replacement has passed validation.

The next training intervention is not yet selected. It must target a different,
explicitly justified mechanism and preserve stroke sensitivity on disjoint
validation. Acquisition, threshold, pooling, architecture, mechanism audits and
this three-class experiment are completed work, not a pending queue. Public-data
preference persists; no outreach was sent. Historical design sections below are
context and must not override this current decision.

Evidence: [TVS cohort result](../reports/TVS_COHORT_RESULT_2026-09-09.md),
[mechanism diagnosis](../reports/TVS_POSITIVE_CALL_MECHANISM_2026-09-08.md),
[freeze](../reports/LOWER_BACK_RELEASE_FREEZE_2026-09-08.md),
[historical exposure](../reports/VOISARD_NONSTROKE_HARD_NEGATIVE_EVALUATION_2026-09-01.md).

## 1. Executive decision

The project should stop treating another architecture search on the current 314 development participants as the default next step. The strongest current result is a **research incumbent**, not a clinical stroke classifier:

- participant-level binary task: healthy versus stroke
- primary input: one lower-back acceleration-magnitude channel
- development sources: Felius, Voisard, and Sint Maartenskliniek
- outer validation: complete-source leave-one-source-out
- selection: five fixed seeds, participant-disjoint inner validation, source/class-balanced training, training-only normalization
- incumbent: equal-probability ensemble of compact ERM, HAROOD-style CORAL, and ERM++-style optimization members
- evidence status: suitable for development comparison, not for clinical generalization or diagnosis

The next defensible stage is a **locked evaluation on a new, paired, clinically described cohort**. The paired role requires healthy and stroke participants. The separate specificity role requires healthy and clinical non-stroke participants. Both need the documented lower-back sensor contract; the full-comparison role additionally requires bilateral feet. See the role decision in `RECRUITMENT_ROLE_DECISION_2026-09-08.md`. The model, preprocessing, threshold, calibration, exclusions, and abstention policy must be frozen before the cohort is opened.

The immediate engineering task is therefore integration and auditability, not model novelty.

## 1.1 Cohort decision after the full local scan

There is currently **no completely matching, untouched public cohort** available in the repository or in the screened candidate list. A cohort counts as completely matching only if it satisfies all of these conditions:

1. clinically identified stroke and healthy participants in the same release
2. gait-labelled or controlled walking recordings, not free-living activity windows
3. raw or losslessly reconstructable IMU signals
4. documented lower-back or lumbar placement plus bilateral foot placements
5. verified sampling rate and acceleration units
6. participant-level metadata sufficient for age, sex, and clinical subgroup accounting
7. no participant overlap with Felius, Voisard, Sint, RevalExo, or any tuning source
8. large enough to support an independent test rather than another descriptive stress test

### Go/no-go matrix

| Cohort | Matching status | Decision |
|---|---|---|
| Sint Maartenskliniek | Closest match: 10 stroke + 20 healthy, raw 100 Hz Xsens, lumbar + bilateral feet, controlled gait. Already used in development and sensitivity work. | **Do not reuse as final test.** Keep its historical external examination separate from later training. |
| RevalExo | Paired raw IMU cohort with a working adapter. Only 17 participants, 7 healthy and 10 stroke, and repeatedly inspected. | **Frozen stress test only.** Not a sufficiently powered or pristine final cohort. |
| Felius and Voisard | Matching paired development sources. Already used for training and model selection. | **Development only.** Cannot provide independent validation. |
| Soangra/John | Paired L5/S1 raw IMU, but naturalistic ADL and no verified gait labels or controlled walking task. No bilateral feet. | **Reject for gait validation.** Do not download derivative files for this purpose. |
| WearGait-PD | Raw 100 Hz full-body IMUs with useful lumbar and lower-limb sensors, but no stroke group. | **Hard-negative specificity only.** Never relabel as healthy controls for binary training. |
| Carpinella 6MWT | 60 healthy participants, raw 100 Hz lower-back IMU, age metadata, controlled walking. No stroke group and no bilateral feet. | **Healthy specificity and age audit only.** Already acquired and evaluated. |
| Mobilise-D CVS | Large clinical non-stroke cohorts with metadata, but processed back-sensor mobility outcomes rather than matching raw LB/LF/RF windows. | **Clinical hard-negative/OOD benchmark only.** Do not fabricate bilateral channels. |
| Zhou rehabilitation | Stroke-only raw IMU with longitudinal metadata. | **Stroke-only severity/OOD analysis.** Cannot form a paired test. |
| Kiel validation dataset | Public release contains only 10 healthy participants. The stroke/neurological extension is not publicly available. Pelvis is not documented lower back. | **Reject as a public paired cohort.** Do not pursue private data without a new access decision. |
| Wang et al. release | Small historical paired study, but archive availability is unresolved and the representation is cycle-level lower-limb angular velocity, not the frozen acceleration contract. | **Reject as a direct external test.** |
| DUO-GAIT, OxWalk, MAREA, Camargo, GaitMotion, triaxial healthy set, NONAN | Healthy-only or non-equivalent placement/protocol. | **Independent healthy/domain checks only.** Never turn them into stroke labels. |

### Practical consequence

Do not install another large dataset for the current binary classifier. That would add storage and adapter risk without solving the missing paired independent cohort. The project should either:

- stop at the current research evidence and report the absence of a suitable final cohort, or
- obtain a genuinely new cohort through a study collaborator or prospective collection under the acceptance checklist in `data/interim/recruitment_acceptance_checklist.md`.

Before any new download, require a small provider-level schema sample or data dictionary proving the eight conditions above. A full archive may be acquired only after the sample passes. The first operation on the full archive must be metadata/schema validation, not bulk extraction or model training.

Current public specificity acquisition is **TVS**, with WearGait-PD as a separate account-required candidate, but only for non-stroke specificity and representation stress testing. It does not answer the paired stroke-versus-healthy validation question. Treating it as the missing cohort would be a category error.

## 1.2 Online search result: no new paired cohort cleared

An online search was performed on 2026-09-08 using Europe PMC, Crossref/DataCite, OpenAlex, Zenodo, Figshare, Synapse, and primary dataset pages. The search was screened at the record level rather than from search snippets alone.

The apparent new lead from the search was not new:

- Felius's Zenodo records `10.5281/zenodo.11045239`, `10.5281/zenodo.11044903`, and related parent/version records describe the already-used Felius cohort. The official metadata confirm the excellent technical match: healthy and stroke labels, lower-back plus bilateral-foot sensors, raw CSV, 104 Hz sampling, and a 2-minute walk test. These records strengthen the provenance of the existing source but cannot create an untouched cohort.
- Zhou's Zenodo rehabilitation record `10.5281/zenodo.10534055` is stroke-only with ten participants and two visits. It cannot provide a paired test.
- The newer related study records found in the search either describe stroke-only rehabilitation, severity, gait-feature extraction, validation against optical motion capture, or datasets already screened in the project. They do not provide a new paired raw lower-back plus bilateral-foot cohort.
- BLISS is public and contains healthy and impaired participants, including stroke-related impairment, but its documented wearable sensors are lower-limb EMG/IMU units rather than the required lower-back plus bilateral-foot acceleration contract. It is not a drop-in binary cohort.
- WearGait-PD remains a useful public hard-negative source with healthy and Parkinson disease participants, but it contains no stroke group and must not be relabelled as healthy for binary training.

Search conclusion: **no newly identified public cohort qualifies for download as an untouched paired validation set**. This does not prohibit the separate TVS non-stroke specificity acquisition. Author-request recruitment is parked under the current public-only preference, and no outreach has been sent.

## 1.3 Contact-based recruitment shortlist

The first outreach wave is recorded in [`docs/CONTACT_RECRUITMENT_SHORTLIST_2026-09-08.md`](CONTACT_RECRUITMENT_SHORTLIST_2026-09-08.md). The strongest initial contacts are the Shirley Ryan AbilityLab wearable-sensor program and the Santa Lucia IRCCS multimodal gait cohort because their registry records explicitly identify paired or multi-condition populations and wearable gait measurements. University of Rzeszów, CHU Dijon, Istanbul University-Cerrahpasa, and the Strathclyde recovery program are secondary routes for either completed-cohort access or prospective protocol collaboration.

These are contact leads, not accepted datasets. Registry evidence does not establish raw-signal access, the frozen lower-back plus bilateral-foot placement, channel order, or data-use permission. The first request must be for a provider-level schema sample or data dictionary. No archive acquisition or model adaptation is authorized until the recruitment acceptance checklist passes.

## 2. Strict critique of the current approach

### 2.1 What is genuinely strong

The current work has several properties that are better than most small wearable-gait studies:

1. The statistical unit is the participant, not the thousands of overlapping windows.
2. Complete-source holdout tests transport across acquisition domains instead of only random window splits.
3. Inner validation is participant-disjoint and normalization is fitted on training data.
4. Five seeds and source-specific FP/FN reporting expose instability that a single AUROC would hide.
5. RevalExo and NONAN are protected from model selection in the current development benchmarks.
6. Architecture and method names were corrected when local implementations did not match canonical upstream methods.
7. Rejected methods are recorded as bounded negative results instead of being silently discarded.

### 2.2 The main scientific flaw

The binary label is narrower than the phrase "stroke classifier" suggests. The current supervised task is healthy versus stroke under the available source definitions. It does not establish stroke specificity. The hard-negative analysis reports substantial positive calls for non-stroke neurological and orthopedic cohorts. Therefore the model may be detecting abnormal or neurologically atypical gait, source composition, device/protocol differences, or age-related gait variation rather than a stroke-specific signature.

This is not a reason to discard the model. It is a reason to rename the claim, redesign the next cohort, and make specificity against clinically relevant non-stroke groups a primary endpoint.

### 2.3 Package identity and remaining limits

The selected lower-back v0.2.0 ensemble is packaged in `models/predict_lower_back.py`.
`models/predict.py` is the historical three-channel comparator. Model documentation
now distinguishes them. Earlier planning reports may still describe historical
contracts; do not rerun the completed package audit or freeze on that basis.
RevalExo is repeatedly inspected research evidence, not a pristine final test.

## 3. What to combine from other work

Do not combine incompatible studies by averaging headline accuracy. Combine their transferable design principles.

### 3.1 Stroke-gait literature principles

The project review and verified primary records show recurring patterns:

- Classical gait features such as cadence, stride time, variability, RMS, and asymmetry remain useful diagnostic baselines and error probes.
- Raw-signal CNNs can learn useful representations, but their scores are not comparable to feature models unless the participant split, task, sensor placement, and label definition match.
- Subject-level validation is essential because repeated trials and gait cycles are correlated.
- Stroke severity, chronicity, walking speed, aids, age, sex, and non-stroke gait disorders affect the interpretation of a healthy-versus-stroke result.
- A model that performs well on a single clean cohort can fail under device, protocol, or population shift.

### 3.2 General time-series methods

The following methods are useful reference points, not automatic upgrades:

- **InceptionTime**: verified primary method and official implementation use a six-module multi-scale CNN ensemble for general time-series classification. The project's compact two-block CNN is not a reproduction.
- **MiniROCKET**: the official implementation uses random convolutional features and a linear classifier, with 10,000 features as the standard reference and `RidgeClassifierCV` over logarithmic alphas. Earlier reduced local variants do not reject canonical MiniROCKET.
- **GroupDRO**: the official work defines explicit groups and emphasizes regularization and worst-group generalization. The project's source-by-class sampler is not equivalent to source-domain GroupDRO.
- **CORAL**: the tested mean-plus-covariance alignment is a reasonable domain-generalization member, but one backbone and one fixed weight do not establish universal superiority.
- **MIL**: participant-level bags are conceptually appropriate for window-to-person labels. The current mean and gated-attention experiments reject only the tested adaptations on the current cohort.

Primary references checked for this plan:

- InceptionTime: https://doi.org/10.1007/s10618-020-00710-y and https://github.com/hfawaz/InceptionTime
- MiniROCKET: https://doi.org/10.1145/3447548.3467231 and https://github.com/angus924/minirocket
- GroupDRO: https://arxiv.org/abs/1911.08731 and https://github.com/kohpangwei/group_DRO
- Systematic review of automatic post-stroke gait classification systems: https://doi.org/10.1016/j.gaitpost.2024.02.011
- Current local primary-study and dataset records: `wiki/studies/`, `wiki/datasets/`, and `data/processed/prior_method_upstream_commits.csv`

## 4. Target system definition

### 4.1 Claims the system may make now

Allowed:

- "research model for distinguishing the available healthy and stroke cohorts"
- "participant-level transport benchmark across three development sources"
- "lower-back acceleration-magnitude research baseline"

Not allowed:

- clinical diagnosis
- stroke-specific detection in an arbitrary population
- age-general performance
- clinical calibration
- superiority over all deep-learning or classical methods
- external validation based only on the 17-person RevalExo cohort

### 4.2 Endpoints

Keep these as separate endpoints. Do not force them into one multiclass label without a new clinical design.

1. Primary research endpoint: healthy versus clinically diagnosed stroke.
2. Primary specificity endpoint: healthy versus non-stroke neurological and orthopedic gait disorders.
3. Secondary endpoint: stroke severity or functional impairment, only when a source supplies a validated and harmonized label.
4. Secondary engineering endpoint: source/device transport.
5. Exploratory endpoint: abstention or referral-zone performance.

### 4.3 Prediction unit

The participant is the statistical unit. A trial is a nested repeated measurement. A five-second window is an input instance only. Every participant, visit, and trial must remain in exactly one split.

## 5. Frozen input contract

The primary contract is deliberately minimal:

```text
shape: (n_windows, 500, 1)
sampling rate: 100 Hz
duration: 5 seconds
signal: lower-back acceleration magnitude
units: canonical g after source adapter conversion
channel meaning: documented lower-back or explicitly flagged adapter-equivalent
normalization: training-fold mean and standard deviation only
window overlap: allowed for training, forbidden across evaluation boundaries
participant aggregation: mean probability for the incumbent, fixed before test access
```

The three-channel LB/LF/RF magnitude input remains a secondary comparator. It must not silently replace the primary lower-back result.

Every source adapter must record:

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class SensorContract:
    dataset_id: str
    participant_key: str
    trial_key: str
    label: str
    source_site: str | None
    placement: str
    accelerometer_unit: str
    sampling_rate_hz: float
    lower_back_provenance: str
    walking_mask_provenance: str
    quality_status: str
```

`lower_back_provenance` must distinguish `native_documented`, `adapter_equivalent`, and `not_supported`. Felius must not be presented as native lower-back evidence unless its source documentation proves that mapping.

## 6. Required code architecture

The next implementation should centralize the contract instead of adding another notebook-specific loader.

### 6.1 New reusable modules

Create these modules only after checking whether an equivalent local module already exists:

```text
src/stroke_gait/
  contracts.py          # dataclasses and schema validation
  adapters.py           # source-specific loading and unit conversion
  manifests.py          # immutable participant/trial/window manifests
  splits.py             # participant/site/source grouped split generation
  preprocessing.py      # walking mask, resampling, magnitude, normalization
  baselines.py          # engineered feature and linear baselines
  aggregation.py        # window -> trial -> participant prediction
  evaluation.py         # metrics, confidence intervals, subgroup tables
  decision.py           # frozen threshold and abstention policy
```

If the repository's current `src/data` and `src/features` modules already own one of these responsibilities, extend them rather than duplicating them. The principle is one owner per contract.

### 6.2 Manifest schema

Materialize one row per participant/trial, not one row per window only:

```python
MANIFEST_COLUMNS = [
    "dataset_id", "site_id", "device_id", "participant_key", "trial_key",
    "label", "clinical_group", "age_years", "sex", "stroke_side",
    "stroke_severity", "stroke_chronicity_months", "walking_speed_m_s",
    "walking_aid", "placement", "sampling_rate_hz", "n_samples",
    "quality_status", "exclusion_reason", "split_role", "split_id",
]
```

Missingness is data, not a reason to silently impute clinical fields. Every missing field gets an explicit reason such as `not_collected`, `not_released`, or `not_applicable`.

### 6.3 Split generation

The controlling code should look like this:

```python
def assert_group_disjoint(train, valid, test):
    groups = [set(frame["participant_key"]) for frame in (train, valid, test)]
    assert not groups[0] & groups[1]
    assert not groups[0] & groups[2]
    assert not groups[1] & groups[2]

def make_outer_splits(manifest, holdout_source):
    test = manifest[manifest["dataset_id"] == holdout_source]
    development = manifest[manifest["dataset_id"] != holdout_source]
    train, valid = participant_stratified_split(
        development,
        stratify=["dataset_id", "label"],
        group="participant_key",
        seed=20260908,
    )
    assert_group_disjoint(train, valid, test)
    return train, valid, test
```

No split helper may accept a window table without a participant key. If a future site-held-out split is possible, site is a second grouping constraint and must be held out jointly with participants.

### 6.4 Preprocessing

The preprocessing function must be pure with respect to the fit state:

```python
def fit_preprocessor(train_windows):
    finite = np.isfinite(train_windows)
    if not finite.all():
        raise ValueError("non-finite training signal")
    mean = train_windows.mean(axis=(0, 1), keepdims=True)
    std = train_windows.std(axis=(0, 1), keepdims=True)
    if np.any(std < 1e-6):
        raise ValueError("near-constant training channel")
    return mean.astype("float32"), std.astype("float32")

def apply_preprocessor(windows, state):
    mean, std = state
    if not np.isfinite(windows).all():
        raise ValueError("non-finite evaluation signal")
    return ((windows - mean) / std).astype("float32")
```

Do not fit normalization, imputation, feature selection, calibration, threshold, or window-selection rules on a held-out source.

### 6.5 Participant aggregation

Use one explicit aggregation owner:

```python
def aggregate_participant_probability(window_frame):
    return (
        window_frame.groupby(["participant_key", "label"], as_index=False)
        .agg(probability=("window_probability", "mean"), n_windows=("window_probability", "size"))
    )
```

The test report must include `n_windows` as a descriptive quantity but must never use it as a weight in participant-level confidence intervals.

## 7. Model stack to implement

The system should have three layers, in this order.

### Layer A: interpretable baseline

Fit logistic regression and a linear SVM on a predeclared feature set:

- lower-back acceleration RMS
- cadence
- mean stride time
- stride-time variability
- foot RMS only where placement is valid
- asymmetry features only where bilateral signals are documented

This baseline is not optional. If the raw model does not beat it under transport evaluation, the project should report the simpler model rather than hide it behind an ensemble.

### Layer B: frozen incumbent

Package the exact notebook-29 lower-back ensemble. Do not rename it as canonical InceptionTime or full ERM++.

Required artefacts:

```text
models/checkpoints/stroke-gait-lower-back-ensemble-v0.2.0.pt
models/lower_back_ensemble.py
models/predict.py
models/MODEL_CARD.md
data/processed/lower_back_ensemble_manifest.json
data/processed/lower_back_ensemble_normalization.json
```

The package must contain the member architecture/configuration, seed list, source list, normalization values, channel semantics, training commit, checksum, and the exact aggregation rule. The current three-channel model package must be relabelled historical or secondary until it is no longer ambiguous.

### Layer C: locked future challengers

Do not start these on the current development data unless a preregistered exception is approved:

- canonical InceptionTime
- canonical MiniROCKET with official feature count and classifier contract
- source-domain GroupDRO
- a calibrated participant-level MIL model

These are valid future methods, but the current evidence says the bottleneck is cohort design. A challenger can be run only as one bounded benchmark on new evidence, not as an open-ended rotation.

## 8. Hard-negative and specificity design

The next paired cohort must intentionally include:

- healthy controls spanning the stroke cohort's age range
- clinically diagnosed stroke participants with severity and chronicity fields
- non-stroke neurological gait disorders
- orthopedic gait disorders
- walking-aid and slow-walking subgroups where clinically relevant

The primary specificity table must report each clinical group separately. Do not pool all non-stroke groups into one number if group labels are available.

The model output should support a referral/indeterminate zone:

```text
probability < lower_threshold: research negative
lower_threshold <= probability <= upper_threshold: indeterminate / referral
probability > upper_threshold: research positive
```

Thresholds must be chosen on a calibration cohort or inner validation only. The final test must not be used to choose them. If a referral zone is used, report coverage and error rates among covered participants. Do not call it a classifier that classifies every participant.

## 9. Locked evaluation protocol

Before opening the new cohort, create and checksum a JSON lock file containing:

```json
{
  "model_version": "stroke-gait-lower-back-ensemble-v0.2.0",
  "input": {"sampling_rate_hz": 100, "window_samples": 500, "channels": ["LB_accel_magnitude"]},
  "normalization": "checkpoint-fixed",
  "aggregation": "participant_mean_window_probability",
  "threshold": "predeclared_or_calibration_locked",
  "abstention": "predeclared_or_disabled",
  "excluded_sources": ["RevalExo", "NONAN"],
  "opened_at": null,
  "selection_allowed_after_open": false
}
```

The final report must include:

Apply the following full metric list only to a cohort with the required classes.
TVS supplies no stroke-positive class: report healthy and clinical non-stroke
positive-call rates, participant accounting and uncertainty, not stroke
sensitivity, diagnostic AUROC, balanced accuracy or calibration claims.

- participant accounting: included, excluded, failed, indeterminate
- TN, FP, FN, TP counts and fractions
- AUROC and AUPRC with participant-level confidence intervals
- sensitivity, specificity, balanced accuracy, F1
- Brier score and calibration plot or calibration table
- site, device, age, sex, severity, chronicity, walking-speed, and aid subgroups where available
- non-stroke neurological and orthopedic specificity
- failure examples with signal-quality and provenance fields
- exact software version, checkpoint checksum, and manifest checksum

## 10. Acceptance and stop rules

### Admit a future model only if all are true

1. It uses the frozen participant/site split contract.
2. It beats the engineered baseline by a predeclared practical margin.
3. It is non-inferior on AUROC, calibration, sensitivity, and specificity across held-out sources.
4. It does not worsen non-stroke specificity beyond the predeclared margin.
5. It reduces both FP and FN, or the trade-off is explicitly justified by the intended operating cost.
6. The result survives the untouched paired-cohort test.
7. The gain is not confined to one source, device, age band, or label subgroup.

### Stop model development and collect data if any are true

- repeated model changes only exchange FP and FN
- the challenger loses to the engineered baseline
- non-stroke false positives remain high
- age, speed, severity, or device coverage is missing enough to block interpretation
- performance is source-specific or calibration collapses externally
- the candidate requires threshold tuning on the test set

The current records already satisfy enough of these stop conditions to justify freezing the incumbent and prioritizing cohort acquisition.

## 11. Agent execution order

1. Read the current checkpoint, wiki handoff and evidence map. Verify local files before acquisition.
2. Resume common-task TVS pilot selection and clinical-quality protocol. Do not repeat completed model, metadata or adapter work.
3. Acquire only selected additional laboratory signals with the resumable downloader. Record failures and exclusions separately.
4. Validate duration, reference intervals, timebase, units, aids and quality before inference.
5. Apply the unchanged model with a predeclared participant-level evaluation protocol. TVS cannot estimate stroke sensitivity.
6. Update reports, current handoff, affected wiki pages, index and append-only log in the same change batch.

## 12. Files that must be reconciled

Treat these as a documentation repair set before release:

- `README.md`
- `models/README.md`
- `models/MODEL_CARD.md`
- `models/predict.py`
- `src/models/freeze_lower_back_ensemble.py`
- `docs/DEEP_LEARNING_DEVELOPMENT_PLAN.md`
- `docs/BASELINE_REQUIREMENTS_AUDIT.md`
- `reports/MODEL_IMPROVEMENT_GATE_2026-09-03.md`
- `reports/CANONICAL_CORRECTIVE_BENCHMARK_2026-09-03.md`
- `reports/TEST_SET_CREDIBILITY_AUDIT_2026-09-03.md`
- `reports/PRIOR_METHOD_CODE_ALIGNMENT_AUDIT_2026-09-03.md`

Historical reports should remain available for provenance, but their headers must clearly state that they are historical and must not be used as the current model contract.

## 13. Falsification checks

The following cheap checks can disconfirm the plan's assumptions:

1. Verify the selected checkpoint accepts one lower-back channel and produces the same participant-level predictions as the notebook-29 decision artefact.
2. Verify Felius lower-back provenance from its own source documentation. If it is not native, split the result into native and adapter-equivalent evidence.
3. Verify that every final-test participant has no row in any training, tuning, normalization, calibration, or threshold-selection manifest.
4. Recompute hard-negative specificity from participant predictions, not window counts.
5. Compare the engineered baseline and frozen incumbent under identical held-out participants.
6. Search all active documents for conflicting values of model version, input shape, source list, and external AUROC before release.

If any check fails, stop integration and repair the contract. Do not compensate with another model.

## 14. Bottom line for the next agent

The current project has done enough architecture exploration to justify a pause. The next useful contribution is not a cleverer network. It is a single coherent, reproducible, clinically honest system contract that makes it impossible to confuse the lower-back incumbent with the older three-channel prototype, impossible to call healthy-versus-stroke evidence stroke-specific, and difficult to obtain an impressive result by counting correlated windows or tuning against a recycled external cohort.

The incumbent and sample integration are complete. Resume the TVS common-task pilot while retaining the unresolved independent healthy/stroke validation need.

## Roadmap priority 1 completed: stance variability coverage

[Executed feasibility](../reports/STANCE_VARIABILITY_FEASIBILITY_2026-09-09.md):
1,259/1,348 trials have within-side/bout CV, but participant coverage fails the
locked 95% per-group gate: healthy 68/72, ACL 9/11, HOA 13/15. All 49 stroke have
coverage. All participants retained in the ledger, no model fitted. Eight tests
passed across the new CV and existing phase extractor. Do not relax the gate or
rerun this estimator as an untested proposal. Acquisition unchanged, preprocessing
complete, classifier evaluation not run. Latest model results unchanged.
The subsequent directional-axis audit below resolves the nominal mapping.
All 1,348 raw headers have accelerometer/gyro/magnetometer XYZ.
Then consider gyro-assisted measurement validation; OOD remains lower priority.

## Nominal directional axes resolved

[Executed axis audit](../reports/DIRECTIONAL_AXIS_AUDIT_2026-09-09.md): provider
Figure 2 supports lower-back X vertical, Y ML and Z AP. Of 1,294 comparable
raw/processed trials, 750 TechnoConcept flip X/Y signs, 37 retain identity, and
507 XSens retain identity. Filtered signed mappings match to numerical precision.
54 XSens comparisons remain unsupported. Initial-second gravity is X-dominant in
1,347/1,348 trials; CVA_18_2 is Z-dominant. This is a screening flag, not a clinical
exclusion or validated stationary interval. Per-trial anatomical calibration is
not established. The nominal-Y harmonic-ratio experiment is now completed below. Sign inversion does not change HR
amplitudes. No new classifier result. Acquisition unchanged, axis audit complete,
directional HR preprocessing/evaluation completed below. Gyro laterality remains separate.

## Directional harmonic ratio completed

[Executed HR comparison](../reports/ML_HARMONIC_RATIO_2026-09-09.md): all 259
participants have main features, 1,345 usable trials. 72 inner and 24 outer fits,
three tests passed. Primary matched phase+HR: 44/49 stroke, 5/19 healthy FP,
47/76 other FP versus phase baseline 42/49, 13/19, 61/76. Full: 45/49, 6/72,
56/138 versus 41/49, 11/72, 59/138. Useful gains, both locked gates fail: matched
sensitivity below 90%, full other-FPR reduction below 5pp. Quality-screened primary
matched result 42/49, 6/19, 48/76. No promotion or threshold sweep. Acquisition
unchanged, HR preprocessing/evaluation complete. The following conditional gyro experiment is now completed; no specificity fix
is established.

## Conditional gyro laterality completed

[Executed result](../reports/GYRO_LATERALITY_2026-09-09.md): six fresh linear SVC
fits on six gyro feature types, participant/pathology held out, known contact times.
48,131/48,257 contacts usable. Matched participant-macro accuracy: healthy 97.8%,
stroke 89.6%, CIPN 95.9%, PD 96.6%, RIL 88.1%. Full stroke 71.4%, healthy 54.0%.
Gate failed. No event-adapter integration, no post-hoc label flips. Two tests passed.
This is annotation-conditioned agreement, not independent or autonomous measurement
validation. The signed gyro raw/processed check is now complete below; it does not
justify corrective fitting. Device and cohort effects remain entangled. Acquisition unchanged,
gyro preprocessing/conditional evaluation complete, release unchanged.

## Gyro transformation audit complete

[Executed audit](../reports/GYRO_AXIS_TRANSFER_AUDIT_2026-09-09.md): 1,294/1,348
trials comparable. All gyro mappings agree with acceleration mappings. Scale 1,
constant offsets fully explain residuals (max corrected RMSE 2.1e-14), consistent
with documented provider offset subtraction. 54 comparisons unresolved. No new
input correction or retraining justified. Two tests passed, all trial rows retained.
Ten participants with both devices show saved OOF side accuracy 25.9% XSens vs
78.9% TechnoConcept; exploratory transfer evidence, not isolated device causality.
Close this mapping audit. Any new sign/calibration intervention needs independent
frame evidence. OOD remains separately scoped against prior abstention work.
Acquisition unchanged, audit complete, model results unchanged, no running job.

## Physical calibration evidence checks completed

[Executed physical checks](../reports/GYRO_CALIBRATION_EVIDENCE_2026-09-09.md):
all 1,348 trials. Median gravity-projected U-turn integral XSens 3.075,
TechnoConcept 3.068 supports common radians/s scale, not degrees/radians mismatch.
Processed static bias is near zero; 450/507 comparable XSens and all 787
TechnoConcept offsets agree with native first-200-row subtraction. Head/back turn
signs agree in all 1,343 jointly usable trials. These are consistency checks, not
independent absolute heading calibration. All ten paired-device participants use
different sessions; their accuracy gap does not isolate hardware. No rescaling,
label flipping or retraining. Existing physical checks closed. Next prerequisite
is independent known-direction or event-reference availability; do not claim
absolute handedness or reference correctness from these signals alone. Acquisition
unchanged, physical checks complete, independent calibration unresolved.

## Local optical reference intake and exploratory classifier

[Executed TVS intake](../reports/TVS_OPTICAL_REFERENCE_AND_CLASSIFIER_2026-09-09.md):
32 existing participants (17 healthy/15 PD), 225 trial records. Optical event-side
fields and raw markers verified. 163 trials usable, 45 absent optical contacts,
17 partial/invalid. Optical/INDIP agree on side in all 1,584 matched contacts.
Corrected coverage 823/952 healthy, 822/962 PD fails 95% gate. Initial denominator
bug permitted three exploratory laterality fits (87.46% HA, 87.34% PD); preserved
and explicitly not admitted. Fixed accounting, reran intake, no additional fits.
No stroke cohort or new stroke classifier. Acquisition unchanged. Next measurement
task is a separately specified per-contact optical quality policy, retaining
unknown intervals and participant coverage. Voisard calibration remains unresolved.

Historical DUO-GAIT inventory is superseded by the completed magnitude test linked above; directional transfer remains pending.
