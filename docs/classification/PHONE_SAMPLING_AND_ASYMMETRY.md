# Phone sampling and movement alternation: executed feasibility audit

2026-09-21. New execution in [notebook 39](../../notebooks/39_phone_sampling_feasibility.ipynb), with raw-source hashes and results under `data/processed/phone_sampling_v1/`. This is a signal-fidelity study on previously inspected development data, not a final test, a clinical validation, or a classifier rerun. RevalExo was excluded.

## Scope and accounting

Selected one lexicographically first trial per eligible participant, without selecting on outcomes. Voisard: 259 selected, 161 included, 96 rejected for any native packet gap, two without finite straight bouts of at least six seconds. Existing common-packet-origin loader was used, but trials with packet gaps were rejected rather than admitted using its interpolation. Supplied event/turn annotations delimit straight bouts only and are not independent laboratory truth. Felius: 166 participants included via the existing loader and duplicate-subject exclusion, using the first 20 seconds without event segmentation. Felius's assumed 100 Hz follows the existing provider-pipeline convention and is not a verified device clock. These differences prevent treating the datasets as an identical walking protocol.

Polyphase anti-aliasing resampling compared 25, 50 and 60 Hz against the original rate. Waveform NRMSE is calculated in a common 8 Hz low-pass band after trimming one second at both ends, normalized to dynamic signal RMS. Participant means aggregate bouts before population summaries. Candidate peaks use a fixed 0.3–3 Hz magnitude detector, not the app estimator or confirmed heel strikes. No diagnostic threshold was selected.

| Dataset | Rate | Median waveform NRMSE | Median peak shift, matched peaks | Median candidate-peak F1 |
|---|---:|---:|---:|---:|
| Voisard | 25 Hz | 5.30% | 10.08 ms | 1.000 |
| Voisard | 50 Hz | 1.31% | 5.20 ms | 1.000 |
| Voisard | 60 Hz | 0.90% | 4.91 ms | 1.000 |
| Felius | 25 Hz | 8.82% | 10.00 ms | 0.975 |
| Felius | 50 Hz | 2.31% | 5.00 ms | 0.977 |
| Felius | 60 Hz | 1.58% | 4.84 ms | 0.980 |

At 25 Hz, median dynamic acceleration energy above the new Nyquist limit was 0.26% in Voisard and 3.48% in Felius. At 50 Hz it was 0.024% and 0.394%. These are acceleration-only findings and do not validate gyro/magnetometer bandwidth. Matched-peak errors exclude unmatched peaks, so F1 and count changes must be considered alongside them. At 25 Hz the 95th percentile participant count-based cadence change was 8.49/min in Voisard and 42.52/min in the unsegmented Felius windows, an important counterexample to blanket acceptance. Higher rates also retain Felius outliers. Results do not measure the clinical accuracy of any detector.

## Decision

Do not adopt 25 Hz as a universal raw-acquisition target. Preserve every native sample and timestamp, request 100/100/50 Hz in the native app, and measure delivery. For browser recordings retain the realistic 60/60/50 request and measured delivery if used. A 25 Hz derived representation may support some low-bandwidth research features but is not cleared for asymmetry or high-frequency jitter. Retain 50–60 Hz or better when available. Do not upsample 46 Hz to 50 or 100 Hz and claim equivalent information. Irregular sampling, dropped packets, phone attachment and the exact app estimator remain unvalidated. No common-rate preprocessing is applied to production training data by this audit.

## Asymmetry versus cause

Existing phase and harmonic-ratio studies already failed specificity gates: see [bilateral phase](../../reports/BILATERAL_PHASE_COMPARISON_2026-09-09.md) and [harmonic ratio](../../reports/ML_HARMONIC_RATIO_2026-09-09.md). Do not relaunch those as new findings. The phone peak detector cannot label feet or toe-off. The app now offers an explicitly experimental alternation descriptor: paired odd/even candidate intervals within uninterrupted bouts, with at least five pairs per bout, 200*abs(mean A - mean B)/(mean A + mean B), aggregated by pair count. This is not established left/right symmetry, stance/swing symmetry, step-length asymmetry or a neurological verdict. Gaps/handling/placement problems are subject to the existing estimator gates, but missed/double peaks and turns can still mislead. No normal/abnormal threshold is added.

For anatomical axis analysis, retain the raw nine axes and baseline. Gravity gives a vertical reference but leaves heading unresolved. Trunk lateral motion is not identical to bilateral limb timing. A validated anatomical calibration and independently labelled contacts are needed before naming left/right or affected side. The practical next measurement study is simultaneous phone/belt capture and bilateral contact reference, comparing raw and reduced rates with predeclared event, timing and asymmetry error bounds. Repeated recordings should capture self-reported sleep, alcohol, medication, pain, support and task conditions; these are covariates, not evidence that confounding has been excluded. No alcohol/sleep-labelled validation cohort was used here.

Primary evidence for overlap: [sleep deprivation and gait control](https://www.nature.com/articles/s41598-021-00705-9) and [phone gait features during drinking episodes](https://arxiv.org/abs/1711.03410). Neither supplies a validated differential diagnosis rule for this app.

## Delivery decision

The user ultimately selected native Android capture on 2026-09-21 after reviewing the browser restriction. The same Expo source builds an internal-distribution APK with `developmentClient:false`. It runs without the developer's computer. See [distribution instructions](../../android/NATIVE_DISTRIBUTION.md). A PWA cannot programmatically expose a missing Magnetometer API. No compass-derived magnetic-field values are substituted. No APK success or physical validation is claimed until an actual build and phone check complete.
