# NONAN GaitPrint healthy reference series

## Role and status

NONAN GaitPrint is the current **staged healthy-domain audit** source. It is
not in the binary training pool, calibration set, threshold-selection set, or
the frozen RevalExo benchmark. It comprises three CC-BY, protocol-consistent
healthy cohorts collected with Noraxon MyoMotion IMUs during self-paced walking
on a 200-m indoor track: 35 young adults (19--35 years), 50 middle-aged adults
(36--55 years), and 41 older adults (56+ years). This is 126 real,
age-labelled healthy participants, not synthesized data.

The staged local audit is stored at
`data/raw/nonan_gaitprint/staged_audit/`. It deliberately contains metadata and
only three predeclared representative participant archives:

| Cohort | Participant | Age | Local role |
|---|---:|---:|---|
| Young (G01) | S030 | 24 | Contract audit only |
| Middle-aged (G02) | S048 | 45 | Contract audit only |
| Older (G03) | S103 | 63 | Contract audit only |

The three people were selected as the median-age row of each cohort's released
participant table; none carries a source `notes` entry. They are permanently
reserved for structural auditing and cannot later be represented as an
independent healthy test cohort.

## Verified source contract (2026-09-02)

All three publisher archives pass their Figshare MD5 values. Each contains 18
CSV trials, 48,001 samples per four-minute trial (0.005-s time spacing), and
321 exported columns. The raw accelerometer signals are explicitly labelled in
**mG**, so conversion to g is division by 1,000; no guessed unit scaling is
needed.

The usable three-sensor map is:

| Project role | NONAN raw columns | Placement interpretation |
|---|---|---|
| LB proxy | `Lower spine Accel Sensor {X,Y,Z} (mG)` | Lower-thoracic/L1--T12 strap placement; **not documented L5** |
| LF | `Foot Accel Sensor {X,Y,Z} LT (mG)` | Left dorsal foot |
| RF | `Foot Accel Sensor {X,Y,Z} RT (mG)` | Right dorsal foot |

The same records also publish a `Pelvis` sensor, but it is not the selected LB
proxy. Neither pelvis nor lower spine may be silently renamed as L5. The
lower-spine channel is more relevant to the project's lower-back research
question, while its documented placement difference remains a required domain
adaptation variable.

Across all 54 sampled trials (2,592,054 time points), every selected raw
target channel was finite. Gravity-inclusive magnitude medians were 0.994--
1.096 g for lower spine, 1.162--1.314 g for left foot, and 1.145--1.353 g for
right foot. The corresponding p99 ranges were 1.625--2.317 g, 3.946--6.176 g,
and 4.226--6.053 g. These are physically plausible raw IMU ranges and clear
the initial scale/completeness gate.

One local quality event was found: S030 left foot had two samples above 16 g
(maximum 25.082 g) in `S030_G01_D01_B02_T02.csv` at 175.095 s; one other trial
had a single 9.431-g sample. This is an isolated-impact/sensor artifact
candidate, not evidence of sustained corruption. Any later materializer must
apply a predeclared, train-fitted artifact policy and report the affected sample
fraction; it must not silently clip the full source.

## Predeclared participant governance

The released screening tables were checked before further download. Fourteen
people reporting mobility-relevant conditions (vertigo, diabetes, joint
replacement, cardiovascular/pulmonary condition, or another listed gait-relevant
flag) are excluded from the strict healthy reference definition. Headache or
migraine alone is recorded but not treated as a gait exclusion. The resulting
partition was created with seed `20260902` by
`scripts/create_nonan_partitions.py` and stored in
`data/interim/nonan_gaitprint/participant_partitions.{csv,json}`:

| Partition | Young | Middle-aged | Older | Total | Permitted role |
|---|---:|---:|---:|---:|---|
| Structural audit only | 1 | 1 | 1 | 3 | Contract inspection only |
| Excluded mobility screen | 0 | 8 | 6 | 14 | Not a strict-healthy reference |
| Frozen healthy specificity | 9 | 11 | 9 | 29 | One-sided external specificity after materialization |
| Candidate healthy enrichment | 25 | 30 | 25 | 80 | Separate source-balanced sensitivity stream only after the frozen gate |

The frozen group is age- and sex-stratified within cohort at 25% (rounded up)
and cannot affect source adaptation, preprocessing, architecture choice,
calibration, threshold selection, or model selection. The 80 prospective
enrichment participants are not yet downloaded. RevalExo remains the only
paired external benchmark.

## Frozen healthy-specificity materialization (2026-09-02)

All 29 predeclared publisher archives have been downloaded and MD5-verified
(`39,806,805,051` bytes in total); their acquisition record is
`data/interim/nonan_gaitprint/download_manifest_frozen_healthy_specificity.json`.
They were materialized once under the same fixed contract as the structural
audit. The result is 23,657 finite, non-overlapping five-second windows with
shape `(23,657, 500, 3)` in each of:

- `frozen_healthy_specificity_magnitude_raw.npy` — primary, untouched
  representation;
- `frozen_healthy_specificity_magnitude_isolated_spike_repaired.npy` —
  predeclared sensitivity representation.

The participant/window coverage is 9/7,344 young, 11/9,072 middle-aged, and
9/7,241 older participants/windows. Metadata contain exactly the 29 frozen
participant IDs and no prospective-enrichment participant. The isolated-spike
policy repaired 167 raw samples. It reduces the materialized maximum from
68.012 g to 14.102 g without changing the separate raw representation.

No NONAN data have been used for fitting, normalization, adaptation,
calibration, threshold selection, or model selection. The one-time
participant-level score was completed on CUDA with fixed checkpoint
`full_expanded_inception_prototype_seed_42.pt` (development-only checkpoint
mean/std; 314 training participants and 22,506 training windows). At the
predeclared neutral 0.50 probability reference, the raw representation produced
2 false positives among 29 healthy participants: false-positive rate 6.9% and
specificity 93.1% (Wilson 95% CI 78.0--98.1%). The repaired sensitivity
representation produced the same two false positives (`S131`, probability
0.654; `S043`, probability 0.530); its largest participant-probability change
from raw was only 0.00179. This establishes that the result is not driven by
the isolated-spike policy. It does **not** establish AUROC, stroke sensitivity,
calibration, clinical deployment readiness, or a reason to tune on NONAN.

## Contract-preserving audit materialization

`scripts/materialize_nonan_staged_audit.py` converted the three structural-audit
archives exactly once into the project's established representation: raw mG was
converted to g, the three tri-axial channels were anti-aliased from 200 Hz to
100 Hz with `resample_poly`, then converted to gravity-inclusive vector
magnitude and divided into non-overlapping five-second windows. The result is
2,592 windows of shape `(500, 3)` in
`data/interim/nonan_gaitprint/staged_audit_magnitude_raw.npy`.

A transparent isolated-spike sensitivity output is stored alongside it. Only
the two contiguous >16-g left-foot samples were linearly interpolated before
resampling. This changes one of 2,592 windows, 20 output values, with a
dataset-wide mean absolute change of `2.51e-06 g`; the raw and repaired
representations therefore remain separate for the next source-shift test. No
NONAN output has been passed to a classifier.

## Preliminary source-shift pre-screen

Using only the three structural-audit people and healthy Felius/Voisard
reference windows, a compact magnitude-dynamics source classifier was close to
chance: AUROC 0.590 for raw windows and 0.597 after isolated-spike repair. The
corresponding standardized feature energy distances were 1.047 and 1.099. The
two-sample repair therefore has no material aggregate effect, and the source is
not rejected for an obvious scale or temporal mismatch. This is a pre-screen,
not an admission result: three people cannot establish transportability and no
classifier prediction, adaptation, or training decision was made from it.

The predeclared 29-person frozen healthy-specificity cohort has now passed
acquisition, materialization, and its one fixed-model score. The two false
positives require descriptive protocol/source review, but the small-sample
confidence interval does not support declaring a no-false-positive healthy
cohort. The separately held 80 candidate people may only be considered for a
predeclared source-balanced training sensitivity experiment that leaves
NONAN-frozen and RevalExo untouched.

### False-positive descriptive review (reporting-only)

The executed review in `notebooks/02_ml_readiness_audit.ipynb` uses only the
already saved fixed-model participant probabilities and raw window summaries.
Both false-positive participants have zero recorded mobility-relevant screening
flags and are female, but they do not have a common signal-amplitude pattern:

- `S043` (middle cohort, age 54; probability 0.530) is at the high end of the
  frozen cohort for lower-back and bilateral-foot variability/dynamics;
- `S131` (older cohort, age 56; probability 0.654) is near the low end of those
  same summaries.

The isolated-spike sensitivity representation leaves both calls unchanged.
Therefore age, a single magnitude scale correction, global clipping, or the
observed isolated spikes cannot be identified as a common causal explanation.
The derived reporting-only table is
`data/interim/nonan_gaitprint/frozen_healthy_specificity_descriptive_profile.csv`.
This finding does not justify any tuning on the frozen cohort.

## Next admission gate

The source has passed **structural feasibility only**. Before more participants
are acquired or any healthy labels influence training:

1. Predeclare participant-disjoint NONAN partitions: a healthy-only frozen
   specificity subset and a separate potential enrichment subset.
2. Materialize walking windows with source-local mG-to-g conversion and a
   documented isolated-artifact policy. Fit resampling, normalization, and any
   adapter only on the relevant development partition.
3. Quantify source separability against real healthy Felius/Voisard windows.
   A low source classifier score and acceptable frozen healthy specificity are
   required before considering source-balanced healthy enrichment.
4. Preserve RevalExo as untouched paired external evaluation. NONAN alone can
   measure healthy specificity/domain shift; it cannot create a paired
   stroke-vs-healthy external AUROC.

## Candidate healthy-enrichment materialization (2026-09-02)

The predeclared 80-person `candidate_healthy_enrichment` partition completed
MD5-verified acquisition (107.32 GiB across 80 source archives) and was
materialized in the executed
`notebooks/14_nonan_candidate_healthy_materialization.ipynb` notebook. The
notebook asserts exact archive/partition agreement and zero participant overlap
with the 29 frozen-specificity people, three structural-audit people, and 14
mobility-screen exclusions before reading signals.

Streaming conversion avoided a full ~245-GiB CSV extraction. It produced 68,398
finite non-overlapping five-second windows of shape `(500, 3)`, with channels
in `LB/LF/RF` magnitude order and `LB` explicitly recorded as the documented
L1/T12 lower-spine proxy. Both raw and isolated-spike-repaired representations
were retained; the repair affected 178 samples and reduced the repaired maximum
from 100.33 g to 15.74 g. This is a data-readiness artefact only: no candidate
data have yet influenced training, normalization, calibration, thresholds, or
model selection.

## Bounded enrichment ablation (2026-09-02)

The executed `notebooks/15_nonan_source_compatibility_gate.ipynb` found strong
participant-level source separability between candidate NONAN and the existing
healthy reference (AUROC 0.8926). Direct pooling is therefore not admissible.

`notebooks/16_bounded_nonan_enrichment_ablation.ipynb` then ran a three-fold,
participant-disjoint sensitivity experiment. It used a fixed 64-window cap per
candidate person and a 0.10 relative sampling cap for the NONAN source. Every
fold fitted normalization only on its training participants. It did not read,
score, calibrate on, or otherwise use the frozen 29-person NONAN cohort or
RevalExo.

Across folds, adding bounded NONAN healthy data kept original-source AUROC
essentially unchanged (mean 0.9549 baseline versus 0.9544 enriched), while
original-source balanced accuracy rose from 0.8157 to 0.8861 and held-out
candidate healthy specificity rose from 0.9107 to 0.9630. Candidate
specificity was heterogeneous: it fell in one fold and improved in one, so the
result is promising but not a final admission decision. The next gate is
repeated, paired seed/fold evaluation with uncertainty intervals; frozen
cohorts remain untouched until a predeclared final comparison.

## Repeated paired admission gate (2026-09-02)

The stronger five-repeat, three-fold paired test in executed
`notebooks/17_repeated_paired_nonan_enrichment_gate.ipynb` did **not** support
admitting candidate NONAN to final training. Its 15 paired resampling units
gave: original-source AUROC difference +0.0002 (bootstrap 95% CI -0.0039 to
+0.0049); original balanced-accuracy difference +0.0150 (CI -0.0115 to
+0.0381); original healthy-specificity difference -0.0166 (CI -0.0901 to
+0.0480); and held-out candidate healthy-specificity difference -0.0021 (CI
-0.0296 to +0.0283). These are repeated resampling units rather than
independent clinical cohorts.

The source-aware capped addition therefore remains a documented development
negative result. It neither demonstrates a durable benefit nor justifies
spending the frozen cohorts. The canonical Felius/Voisard/Sint model remains
unchanged while a class-aware adaptation or genuinely matched paired cohort is
investigated.

## Class-aware alignment pilot (2026-09-02)

The executed `notebooks/18_class_aware_nonan_alignment_pilot.ipynb` tested a
healthy-only CORAL-style embedding loss: it aligned candidate-NONAN healthy
embeddings with original-source healthy embeddings, while leaving stroke
examples out of that alignment term. The candidate source was still capped at
64 windows/person and its classification loss was downweighted to 0.10.

This theoretically motivated variant also failed its pilot gate. Candidate
held-out healthy specificity was unchanged (mean 0.9872 for both baseline and
alignment), whereas original-source mean balanced accuracy declined from 0.8857
to 0.8488 and healthy specificity declined from 0.8730 to 0.8095. It is
rejected without repeated tuning or frozen-cohort evaluation. The evidence
shows that the current problem is not solved merely by matching healthy feature
moments across these sources.

## Sampler-corrected re-audit (2026-09-02)

Code review found that the release-training script and the first candidate-NONAN
tests balanced source/label **windows**, not participants. A corrected pilot in
`20_participant_balanced_nonan_pooling_pilot.ipynb` initially looked favorable:
at a 10% candidate-source mass, candidate healthy specificity was 0.9872 versus
0.7873 and original healthy specificity was 0.9435 versus 0.7238. That was a
single split, not a final finding.

The executed repeated gate in notebook 21 corrected the earlier evidence
without hiding it. Across 15 seed-matched participant-disjoint units, candidate
enrichment still had no durable benefit: original AUROC delta -0.0041 (95%
bootstrap CI -0.0094 to +0.0012), original healthy-specificity delta -0.0343
(CI -0.0909 to +0.0253), and candidate healthy-specificity delta -0.0026
(CI -0.0176 to +0.0123). The cohort is therefore not admitted to this current
magnitude-model recipe, but it is not globally rejected as a dataset: the
representation/segmentation contract remains under audit.

## Sources

- [Young cohort Figshare collection](https://doi.org/10.6084/m9.figshare.c.6415061.v1)
- [Middle-aged cohort Figshare record](https://doi.org/10.6084/m9.figshare.29371796)
- [Older cohort Figshare record](https://springernature.figshare.com/articles/dataset/NONAN_GaitPrint_An_IMU_gait_database_of_healthy_older_adults/27815034)
