# Classification methodology review — 2026-09-09

Decision: retain the frozen model as a research comparator. Its current evidence
does not justify a transferable stroke-specific interpretation. Prioritize
measurement validity and conditional discrimination before another architecture
or threshold experiment. This review changes the implementation direction, not
the manuscript's study inclusion or findings.

## What actually produces a positive score

The frozen v0.2.0 consumes lower-back acceleration magnitude
`sqrt(ax² + ay² + az²)` in g, 500 samples at 100 Hz. Training-derived scalar
normalization precedes two multiscale convolution blocks. Each member produces a
sigmoid score; 15 member scores are averaged, then windows are averaged per
participant and compared with 0.50. This is a learned class score, not an
established probability of stroke. If displayed as `1 - stroke_score`, a healthy
score is only its binary complement; it does not establish healthy gait or exclude
another disease.

The input contains movement amplitude, local waveform and temporal structure.
It has no explicit paretic side, foot-contact events, stance/swing durations,
bilateral timing, clinical severity or lesion information. Magnitude discards
direction: distinct three-axis trajectories can produce identical inputs.
These losses cannot be recovered by choosing a more powerful classifier.

**New code finding, executed in the existing Python environment:** the maximum
local receptive field before global averaging is 74 samples (approximately
0.74 seconds). The longest path is kernel 25 → pool 2 → kernel 25:
`1 + 24 + 1 + 24*2 = 74`. An evaluation-mode autograd check on an interior feature
position found support at samples 214–287 inclusive, exactly 74 samples.
See [architecture](../models/lower_back_ensemble.py) and
[blocks](../models/stroke_gait_inception.py).
Global averaging includes evidence from all five seconds, but does not explicitly
model ordered relationships between distant local events. This is a limitation
of temporal representation, not proof that the receptive field caused the
observed false positives. Training batch normalization is distinct from this
evaluation-mode receptive-field statement.

## What the evidence does and does not establish

| Finding | Methodological implication |
|---|---|
| TVS: 17/18 healthy and 16/16 PD called positive | Severe specificity/transfer failure. TVS contains no stroke sensitivity evidence. |
| Voisard: frozen model calls 89/138 non-stroke positive | Binary healthy-versus-stroke training does not establish distinction from other gait disorders. |
| Three-class experiment: sensitivity 87.76% → 68.71%, other-pathology FPR 53.38% → 40.58% | Explicit differential labels alone failed under the tested representation and recipe; reduced FP is not sufficient success. |
| Verified units, sampling and normalization; shared errors across members | No tested simple adapter bug explains the failure. Ensemble agreement does not establish validity. |
| Constant-input positives and sensitivity to temporal shuffling | Model accepts non-informative inputs and uses temporal structure. Synthetic probes do not identify a unique clinical cause. |

Sources: [evidence map](../docs/CLASSIFICATION_EVIDENCE_MAP.md),
[mechanism probes](TVS_POSITIVE_CALL_MECHANISM_2026-09-08.md),
[differential experiment](DIFFERENTIAL_GAIT_IMPLEMENTATION_2026-09-09.md).
The new validity wrapper rejects exact constant/nonfinite windows only; it is
opt-in and does not repair moving-gait specificity.

Our prior feature analysis already found healthy-versus-stroke differences in
RMS and cadence. Those are useful descriptions of the studied groups, but neither
an individual diagnosis nor proof of cross-pathology specificity. The existing
[feature page](../wiki/concepts/discriminative-features.md) also documents a real
device effect on lower-back RMS and a device-matched feature sensitivity analysis.
That analysis supports those group effects; it does **not** show the CNN ignores
hardware. Do not rebrand this existing finding as a newly discovered confound.
Voisard's shared protocol does not imply identical devices across all classes.

Participant/source separation protects against particular leakage routes. It
does not eliminate correlations between label and age, speed, severity, task or
device. Domain alignment likewise does not prove absence of shortcuts. The current
evidence is consistent with shared impairment cues plus recording/task shift;
their individual causal contributions remain unresolved. Speed is also part of
the impairment pathway, so report both total discrimination and speed-conditional
discrimination rather than mechanically removing it and calling that truth.

## Available frameworks and the relevant role

| Framework or approach | Verified role and compatibility | Decision for this project |
|---|---|---|
| [Mobilise-D mobgap](https://github.com/mobilise-d/mobgap) | Open Python lower-back IMU gait-measurement pipeline; gait bouts and mobility outcomes. Specific pipelines have validation and use conditions. | Best starting point for a lower-back measurement adapter. Verify algorithm-specific axes, units, metadata and impaired-gait coverage. Not a pretrained stroke diagnostic model. |
| [gaitmap](https://github.com/mad-lab-fau/gaitmap) | Open movement-analysis toolbox focused on foot IMUs, including stride segmentation and parameter extraction. | Relevant if bilateral foot signals are available. Foot algorithms cannot simply be applied to lower-back magnitude. |
| [APDM Mobility Lab](https://support.apdm.com/hc/en-us/articles/360000177066-How-are-Mobility-Lab-s-algorithms-validated) | Commercial gait/balance measurement system with algorithm validation against measurement references. | A measurement-system alternative, not evidence of a compatible stroke-versus-other classifier. Procurement is not the next step. |
| [Physilog/Gait Up stroke validation](https://pubmed.ncbi.nlm.nih.gov/31352347/) | Two foot sensors compared with Vicon in 25 subacute stroke survivors. Several parameters were valid/reliable, with limitations for severe foot dragging and paretic stance/swing. | Shows why parameter-specific clinical validation matters; not validation of stroke diagnosis. |
| [Brasiliano et al. 2026](https://www.nature.com/articles/s41598-026-43666-7) | Existing included study: five IMUs, interpretable gait features and conventional classifiers; healthy-versus-stroke discrimination. | Relevant feature-design reference, not a drop-in lower-back architecture or proof of independent differential diagnosis. Already in our wiki. |

No compatible, independently validated, off-the-shelf stroke-versus-other gait
classifier was verified in this review. This is a bounded search conclusion, not
a claim that none exists. No dataset or package was downloaded or installed during
this review. Framework availability must not be confused with public stroke data.

## Concrete next implementation and its stopping rule

The unanswered question is whether measurable gait characteristics add stroke
discrimination beyond known recording and population differences. Existing feature
extraction, device sensitivity analyses and classifier benchmarks must be reused.

1. Build a participant-level contract joining existing features, predictions,
   device, age, task, walking speed/cadence where available, and pathology labels.
   Preserve missing metadata and exclusions. First check joint label/device/task
   overlap: no statistical adjustment can manufacture a missing comparison group.
2. Reuse corrected gait-interval extraction and validate a lower-back measurement
   adapter against available event references before adding new features. Keep
   directional data where supported; only estimate bilateral or paretic features
   where the sensor/event contract supports them. Report extraction failures by
   diagnosis instead of selecting only easy walkers.
3. Compare nuisance-only, interpretable gait-feature, and combined baselines on
   identical participant/source/pathology splits, with all fitting and selection
   inside training folds. Evaluate incremental sensitivity/specificity, calibration,
   coverage and participant-level uncertainty. Use existing inspected cohorts for
   development only; an untouched compatible cohort remains necessary for final
   validation.

These are the next implementation targets, not completed experiments. Do not
start another broad CNN/Transformer sweep. If overlap is inadequate, document the
identifiability limit. If gait features cannot separate stroke from other disorders
under matched conditions, narrow the output to gait impairment assessment rather
than conceal the limitation with a threshold or a confident stroke label.
