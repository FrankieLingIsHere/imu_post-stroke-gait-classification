# Review of the collaborator-supplied false-positive hypotheses

> Subsequent execution update: the proposals below are historical. The
> [phase experiment](BILATERAL_PHASE_COMPARISON_2026-09-09.md) and
> [nested threshold test](PHASE_NESTED_THRESHOLD_2026-09-09.md) are complete.
> Both failed their primary gates. Do not restart them from this review.


The supplied synthesis is useful as a hypothesis checklist, not a demonstrated
explanation of this model. Reviewed against the evidence map and the primary
sources behind references 3, 4, 5 and 7. This is not a full eight-reference audit.
No new training, acquisition or cohort evaluation occurred.

| Suggestion | Assessment for this project |
|---|---|
| Activity confusion | Relevant to deployment, but cannot alone explain non-stroke positives already observed in annotated straight walking. Our gait-bout adapter is already evaluated and failed admission. |
| Placement/orientation | Distinguish physical placement, attachment movement and sensor calibration from a pure coordinate rotation. The current norm is invariant under an orthogonal rotation: norm(Ra)=norm(a). Pure axis rotation is not a sufficient mechanism here; moving the sensor or changing its transfer characteristics can still matter. |
| Age/body size/pace | Plausible, partly tested by covariate/cadence comparisons. Correlation does not establish cause. Cadence is not speed; speed is partly an impairment outcome, so blanket residualization can remove useful information. |
| Participant/window leakage | Existing subject/source-disjoint splits address the proposed basic leakage route. Overlap within training is not itself train/test leakage. Correlated windows still affect weighting and uncertainty; a random-split comparison would not identify the cause of current external false positives. |

## Citation corrections and applicability

[Van Mierlo et al.](https://pubmed.ncbi.nlm.nih.gov/41553893/) investigate walking
detection, including stairs being mistaken for walking. That is not evidence that
stairs were classified as stroke. Their bilateral-foot measurement setup is also
not an interchangeable lower-back implementation.

[Mu et al., institutional abstract](https://www.imperial.ac.uk/patient-safety-research-collaboration/our-work/publications/research-publications/?id=1190093&noscript=noscript&respub-t4-action=citation.html)
supports investigating position transfer, not guaranteeing position independence
for our classifier. Moving between different body locations changes the task;
leave-one-location-out is not the priority for a fixed lower-back contract. Our
prior CORAL experiments are relevant completed evidence, although they do not
exhaust every possible adaptation method.

[Caramia et al.](https://iris.uniroma3.it/bitstream/11590/338740/1/Caramia_IEEE-JBHI.pdf)
study Parkinson's classification. The citation does not establish a speed-invariant
stroke marker recoverable from our single magnitude channel. Joint range of motion
would need an appropriate sensor/kinematic contract; it is not available simply by
changing feature selection.

[Hsu et al.](https://pubmed.ncbi.nlm.nih.gov/30314269/) is directly relevant to
healthy/stroke/other neurological discrimination, and is already in our wiki.
Its shank/multiple-sensor evidence is not a new lower-back external validation.

## A specific remaining feature gap

The conditional experiment's `stride_time_asymmetry` compares the left and right
mean same-foot cycle durations. It does not measure alternating step-time
asymmetry, swing-time asymmetry or stance-time asymmetry. For example, left contacts
at 0, 1, 2 seconds and right contacts at .3, 1.3, 2.3 seconds produce equal one-second
stride durations, despite alternating .3/.7-second steps. This is a mathematical
counterexample to interpreting that feature as comprehensive bilateral timing.
It is not a claim that all stroke gait is asymmetric or that asymmetry is specific
to stroke. Targeted searches of current implementation scripts found no executed
matched differential comparison using the proposed phase-resolved feature set.

**Recommended next experiment, not yet implemented:** reference-assisted bilateral
phase feature feasibility. Compute alternating heel-strike step-time differences,
swing/stance duration asymmetry and valid double-support fractions from existing
event annotations, with no intervals crossing turns and explicit malformed/missing
cycle coverage. No clinical-deficit-side flag or diagnosis-derived field may enter
the classifier. Use the same folds, cadence/covariate controls, held-out pathologies
and matched-device sensitivity analysis. Lock sensitivity-preserving admission
criteria before fitting; this is not another broad feature/architecture sweep.

This tests whether the missing phase information is useful before investing in
sensor-only extraction. Annotations are algorithm-derived, so even a positive
result would require independent replication and measurement validation. It would
not demonstrate that one lower-back sensor can recover the new features. If it
fails, do not infer that every conceivable gait representation is impossible;
restrict the supported output and stop promoting diagnostic claims without evidence.

Current verified result remains 89/138 non-stroke positives before and after packet
correction, zero changed calls. The new feature question is a justified direction,
not a known fix or a discovered unique root cause.


## Follow-up synthesis review

The second supplied synthesis retains the recommended phase-feature experiment,
but overstates causality. Demographic and physical-placement contributions have
not been excluded. Missing phase descriptors are a testable information gap, not
a proven explanation of the frozen model's errors. The handcrafted stride-asymmetry
feature is incomplete; this does not prove the raw CNN is blind to every bilateral
pattern. Stroke-versus-healthy feature utility is not stroke-versus-other specificity.

A verified new actionable source is [Ullrich et al.](https://pubmed.ncbi.nlm.nih.gov/34892475/):
left/right initial-contact classification uses lower-back gyroscope features.
This supports a possible later measurement route, not recovery from acceleration
magnitude alone or validation of final contacts/double support. Reference 4 in the
new synthesis names Schneider's smartphone thesis although its text attributes
that reference to Van Mierlo: the citation mapping is incorrect.

[GaitEncoder's official implementation](https://github.com/rdmagruder/GaitEncoder/blob/master/README.md)
uses full-body walking kinematics (32 joints, 24 stride-normalized time points),
not our raw lower-back IMU contract. [OpenOOD](https://zjysteven.github.io/OpenOOD/)
is principally an image-classification benchmark: methods may be adapted, but its
benchmarks do not validate clinical gait rejection. Neither is a drop-in solution.

Keep representation and rejection experiments separate. OOD detection does not
necessarily recognize an unseen diagnosis when its measured signal resembles a
known class; a new device can also make a genuine stroke case look unfamiliar.
Any rejection test needs fixed validation thresholds, held-out pathologies,
retained stroke sensitivity, rejected-stroke counts and coverage. Rejections are
unknown, not healthy. Prior abstention work must be consulted before proposing a
new implementation. The phase-feature experiment remains the first recommendation.
Do not silently exclude participants with invalid cycles: retain missingness and
coverage by diagnosis. No new training or full 26-reference audit occurred.
