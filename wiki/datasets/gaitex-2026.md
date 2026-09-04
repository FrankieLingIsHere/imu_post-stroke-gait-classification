# GAITEX (2026): virtual-IMU synthesis candidate

## Local status

The full GAITEX release is retained in the completed-source archive at
`data/archive/raw/gaitex_2026/`. Its publisher archive was checksum-verified
before extraction (`cc69aa2b8d1317430012252e5a58d2b5`) and then removed as a
redundant 16.45-GiB copy; the extracted source data and all audit artefacts are
preserved.

The 2026-09-02 local audit found 19 participant directories. Eighteen contain
the complete normal-gait asset set: three annotated treadmill-speed intervals,
100-Hz Qualisys marker trajectories, Xsens orientation quaternions, metadata,
and a participant-specific OpenSim model. `hans` does not have a complete
normal-gait asset set. Seventeen participants fully clear the target rigid
cluster criterion (at least three valid markers in every pelvis/left-foot/right-foot
cluster). `gregers` has local left-foot marker loss, but every normal-gait
segment still has at least one uninterrupted five-second marker-complete run;
it is retained only through marker-complete window selection. Initial warnings
for `austra` and `elodie` came from a faulty rule that interpreted a single zero
coordinate as a missing XYZ marker; the audit now correctly treats only an
all-zero XYZ triplet as missing.

## Contract and permitted role

GAITEX is healthy only. It publishes orientation data, markers, and OpenSim
models; it does **not** publish raw accelerometer signals. The documented trunk
sensor is pelvis, not the project's lower-back/L5 placement. Consequently it
must not be directly pooled with Felius/Voisard/Sint, passed to the LB/LF/RF
prototype, or used in any frozen external test.

It is a candidate for physics-grounded virtual healthy IMU generation and
self-supervised representation research. The next feasibility gate is an
explicit, reproducible virtual attachment model for L5, left foot, and right
foot, followed by marker-derived tri-axial acceleration generation for normal
gait only. Any generated data must pass held-out-person realism and downstream
utility checks before it can influence training, and it will never be described
as additional independently recruited participants.

## Virtual-sensor feasibility result (2026-09-02)

`scripts/probe_gaitex_virtual_sensor_feasibility.py` assessed the recorded
pelvis, left-foot, and right-foot marker clusters only; it does not generate
training data. Across 18 people and 55 annotated normal-gait segments, marker
and orientation time bases align to within 2 ms for at least 99% of frames, and
every foot segment retains an uninterrupted run of at least five seconds under
the three-of-four marker criterion. Median diagnostic ground-frame centroid
acceleration p99 is 3.48 m/s² for the recorded pelvis cluster, 20.45 m/s² for
the left foot, and 20.75 m/s² for the right foot. These values show that the
motion source is technically usable for a virtual-sensor experiment; they are
not sensor-output validation and must not be passed to the classifier.

The unresolved scientific gate is not data availability: it is the definition
of an explicit lower-back/L5 virtual attachment. The OpenSim models include
pelvis and lumbar degrees of freedom, but GAITEX documents a pelvis sensor,
not an L5 attachment. The next implementation must specify the attachment in
the model frame, derive virtual **proper** acceleration and orientation, then
validate it against the recorded foot/pelvis orientation/cluster geometry
before any self-supervised pretraining or augmentation utility test.

## Physics-derived magnitude sensitivity and target-contract audit

The validated plate centres were smoothed and differentiated twice to produce
gravity-inclusive *proper-acceleration magnitudes* for three normal-gait
channels: `pelvis_proxy_not_l5`, left foot, and right foot. This produced 293
non-overlapping five-second windows from all 18 people. Three differentiation
settings were retained rather than selecting a visually smooth output: 110 ms,
210 ms, and 310 ms Savitzky--Golay windows. Foot p99 magnitude decreases from
3.27/3.33 g (left/right) at 110 ms to 2.05/2.15 g at 310 ms, showing why a
stronger smoothing choice would erase impact dynamics.

The unadapted source was then compared with **real healthy Felius/Voisard only**
(3,960 windows, 106 participants); RevalExo, Sint, stroke samples, and any
classifier fitting were excluded. The 110-ms setting is the least divergent,
but a participant-disjoint source classifier still separates virtual GAITEX
from real healthy windows at AUROC 0.994 (feature energy distance 3.91). The
210-ms and 310-ms variants are still more separable (AUROC 1.000 and 1.000,
respectively). Therefore none is eligible for direct pooling. This does not
invalidate the virtual motion; it shows that a source-aware adapter or
self-supervised pretraining test is required, with any fitting performed only
inside a development fold.

## Adapter and self-supervised transfer results

A transparent per-channel median/IQR affine adapter was evaluated over 20
repeated participant-held-out splits. Its source and target statistics were
fitted only on the corresponding training participants. It reduced median
feature energy distance from 4.35 to 2.52, but the held-out source AUROC stayed
at 0.999 (empirical 95% range 0.990--1.000). Therefore the residual mismatch is
not merely gravity offset or amplitude scale; direct adapted pooling is
rejected. The adapter preserved waveform ordering and non-DC spectral shape by
construction, so the result is evidence of deeper device/protocol dynamics,
not an artefact of a destructive remapping.

The remaining safe use, an architecture-matched GPU self-supervised ablation,
also did not improve real-label classification. A contrastive Inception encoder
was pretrained only on 110-ms GAITEX virtual windows (no binary labels), then
fully fine-tuned on real Felius/Voisard/Sint labels. In matched five-fold
participant-disjoint internal evaluation it reached AUROC 0.9632, Brier 0.0753,
and balanced accuracy 0.8987, versus scratch AUROC 0.9646, Brier 0.0733, and
balanced accuracy 0.9043. RevalExo was never loaded. GAITEX virtual data is
therefore **not adopted** for the current binary prototype, direct pooling, or
pretraining. It remains a useful validated physics source for future work only
if a new target task or a real paired virtual-sensor calibration set becomes
available.
