# Why the frozen model calls TVS participants positive

## Current conclusion

The strongest supported explanation is **learned motion-pattern sensitivity
that transfers poorly to this new task/device domain**, rather than a simple
unit conversion, channel mix-up, class-count prior or one faulty ensemble member.
The exact biological or acquisition cause of these four people's errors remains
unidentified. The experiments below identify model behaviour, not stroke causality.

The model can learn features associated with stroke in its development sources
without those features being specific to stroke. Its binary training labels do
not force it to distinguish stroke from every other source of unusual movement.
The healthy TVS failures show that attributing everything to PD pathology is
also insufficient. The ongoing cohort extension measures the extent of failure;
it cannot, by itself, isolate the mechanism.

## What was ruled out or narrowed

| Explanation | Evidence | Conclusion |
|---|---|---|
| Wrong TVS units, magnitude, rate or normalization | Independent raw reconstruction error below 2.5e-7 g; native 100 Hz; official stored-g evidence; all 15 training normalization constants reproduced exactly | No mismatch in these tested paths. Broader measurement/task differences remain possible |
| Stroke outnumbers healthy, so training simply learns the majority | Actual sampler draw contains 32 healthy and 32 stroke windows from each of three sources | Effective minibatch class counts are balanced. Within-class participant exposure can still differ |
| Healthy/stroke labels inverted | Training maps `label == 'stroke'` to 1 and uses sigmoid/BCE; selected development controls discriminate in the expected direction | No label inversion found |
| Foot/axis features accidentally mixed | Deployment consumes one lower-back magnitude channel; saved TVS input matches raw Euclidean magnitude | No accidental multi-sensor mixing found. Magnitude deliberately discards directional information; its causal contribution to errors is untested |
| One ensemble member drives healthy failures | All 15 independently call HA/1091 and HA/1092 positive; each of the three five-seed method means is above 0.92 | Shared failure, not one outlier |
| Large positive final-layer intercept | Mean head bias is 0.101981 logit; mean learned feature contributions are 3.517607 and 4.522057 for the two healthy people | Final-layer intercept alone does not explain their high scores. Earlier convolution/normalization biases are part of the learned feature path |
| Model is positive on every input | Selected development controls: 3/12 healthy and 10/12 stroke positive; shuffled inputs become predominantly negative | No global constant-positive collapse. These controls are resubstitution diagnostics, not accuracy estimates |

The implementation hashes for training/sampling, the architecture and inference
match the frozen release manifest. Prior normalization and nuisance-augmentation
experiments already exist in [the normalization benchmark](NORMALIZATION_VARIANT_BENCHMARK.md);
this work did not repeat training or reopen those rejected candidates.

## Controlled probes

The [diagnostic runner](../scripts/diagnose_tvs_positive_calls.py) fixed nine
conditions before inference. It uses only the four already inspected TVS people
and 24 deterministic development controls (four people per source/class, up to
three evenly spaced windows each). It does not open the 30 new cohort participants.
Predictions, weights and original input files are unchanged; transformed copies
are mechanism probes, not candidate preprocessing chosen for deployment.

| Probe | HA/1091 score | HA/1092 score | What it establishes |
|---|---:|---:|---|
| Original | 0.9622 | 0.9781 | Reproduces the saved failure |
| Move window mean to 1 g | 0.9841 | 0.9824 | Small DC/mean correction does not resolve these calls |
| Halve dynamic amplitude, preserve mean | 0.9408 | 0.9609 | Their failure persists after amplitude reduction |
| Double dynamic amplitude, preserve mean | 0.9860 | 0.9922 | Increasing amplitude also fails to resolve the healthy calls |
| Retain frequencies through 5 Hz | 0.6051 | 0.8856 | Higher-frequency content contributes to scores, but both remain positive |
| Retain frequencies through 10 Hz | 0.7070 | 0.8976 | A simple filter is not an observed healthy-specificity fix |
| Reverse sample order | 0.9734 | 0.9690 | High healthy scores persist under time reversal |
| Shuffle sample order, preserve exact values | approximately 0 | 0.000000862 | Temporal arrangement matters; marginal amplitude distribution alone is insufficient |
| Replace movement by constant window mean | 0.9765 | 0.9313 | This classifier can output strong positives even without gait dynamics |

The development controls help interpret these changes: halving dynamic amplitude
increased healthy positive calls from 3/12 to 8/12, while constant-mean inputs
made all 12 healthy and all 12 stroke controls positive. This is evidence of a
low-dynamics/non-walking failure mode. It is not proof that the actual TVS healthy
signals were low amplitude: their dynamic standard deviations were about 0.371
and 0.280 g, and changing amplitude did not rescue them.

Temporal shuffling preserves every sample value but destroys ordering and changes
the spectrum. Its effect does not isolate cadence, asymmetry, smoothness or one
frequency band. FFT truncation assumes periodic boundaries and can introduce
edge effects. Constant, shuffled and doubled signals can lie outside realistic
gait distributions. These limitations prevent calling a particular clinical
feature the proven cause. No threshold or transform was selected from the probes.

## Consequence

The model has no reliable notion of "this is not valid stroke-discriminating
gait" in these probes; it always returns a binary score. That is a demonstrated
weakness. A non-walking input guard could address constant signals, but would
not fix the observed healthy hallway errors and was not added to the frozen
cohort run. Arbitrary amplitude normalization, filtering or threshold increases
would hide symptoms without establishing stroke specificity.

Complete the fixed cohort evaluation before choosing the next development
experiment. Any proposed intervention must preserve stroke detection on separate
development validation while reducing independent non-stroke calls; no model
change can be accepted solely because it lowers these four inspected scores.

Artifacts: `data/interim/public_imu_screen_2026-09-08/positive_call_diagnosis_v1/`
contains the protocol, per-participant probe results, per-member original scores,
head/feature logit decomposition and group summary. Three transform tests passed
for preserved values under order changes, mean-preserving dynamic gain and
known-frequency removal. Original hallway predictions reproduced within 1e-6.
