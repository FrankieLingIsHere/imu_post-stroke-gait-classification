# Frozen lower-back audit: older healthy triaxial cohort

## Question and protection against leakage

Can the already-trained lower-back-only binary model recognise a second,
age-diverse healthy gait cohort as healthy? This is a healthy-only specificity
audit, not a binary evaluation. The cohort was never used for model training,
normalisation, calibration, or threshold selection. The three-channel
LB/LF/RF magnitude model remains the primary prototype.

## Cohort and preprocessing contract

The public [Terrier/Piergiovanni triaxial accelerometer dataset](https://doi.org/10.5281/zenodo.10148824)
contains walking recordings from older adults, with a lower-back accelerometer
and one foot accelerometer. It has no bilateral-foot pair, so it cannot be
scored by the three-channel model without fabricating a missing channel.

For this frozen lower-back audit, only author-segmented normal corridor walking
(`*_LB_N_O.csv` and `*_LB_N_R.csv`) was used. The source is documented as
256-Hz, g-unit triaxial acceleration. Each continuous recording was resampled
to the checkpoint's fixed 100-Hz contract using polyphase resampling
(`up=25`, `down=64`), converted to acceleration magnitude, and divided into
5-second windows with 2.5-second hop. Scores were aggregated by participant.

| Item | Value |
|---|---:|
| Healthy participants scored | 59 |
| Age coverage | 65–88 years |
| Windows | 7,955 |
| Model/device | Frozen lower-back model / CUDA |
| Decision reference | Existing 0.50 (not retuned) |

## Result

| Outcome | Result |
|---|---:|
| Healthy participants called stroke | 53/59 |
| False-positive rate | 89.8% |
| 95% Wilson interval | 79.5%–95.3% |
| Mean participant stroke probability | 0.610 |
| Median participant stroke probability | 0.644 |

This is a strong external-domain failure for this model/cohort pairing. It is
not an estimate of sensitivity, AUROC, or clinical utility because all
participants are healthy.

## Why this must not be treated as an age result

The input distribution is substantially different from both the checkpoint and
the successful Carpinella healthy audit:

| Magnitude characteristic | Older triaxial cohort | Carpinella healthy cohort |
|---|---:|---:|
| Median magnitude | 0.578 g | 1.021 g |
| Samples below 0.3 g | 32.7% | 1.0% |
| Samples in 0.5–1.5 g | 34.5% | 74.2% |
| Samples in 0.8–1.2 g | 11.1% | 31.0% |

The frozen model's fitted input mean is 1.016 g (SD 0.206 g). The older
cohort’s magnitude distribution is therefore far outside its observed input
domain. Although the public release documents g units, its lower-back signal
representation and/or sensor processing differs materially from the model’s
gravity-inclusive magnitude contract. Blindly multiplying, offsetting, or
adding gravity would manufacture an unvalidated signal and is prohibited.

Older age is also not the explanation that can be claimed from this result:
the participant probability increases with age within this out-of-domain
cohort (Spearman rho 0.468, p=0.00019), but this association is confounded by
the unverified sensor/representation shift. It cannot establish an age bias.

## Decision

1. **Do not pool** this release into binary training or use it to tune a
   threshold.
2. **Do not call it a failed older-healthy clinical test**; it fails the
   pre-inference data-contract check for the present gravity-inclusive
   lower-back magnitude model.
3. Retain it as documented evidence that the secondary lower-back track is
   not device/representation invariant.
4. The next valid lower-back evaluation must use a cohort whose raw signal
   semantics can be verified against the trained input contract, or a
   predeclared device-invariant representation must be developed and tested
   on held-out sources before it is presented as robust.

## Reproducibility artifacts

- Script: `scripts/evaluate_triaxial_older_healthy_lower_back_external.py`
- Summary: `data/processed/triaxial_older_healthy_lower_back_external_audit.csv`
- Participant scores: `data/processed/triaxial_older_healthy_lower_back_external_participant_predictions.csv`
- Window metadata and predictions: `data/processed/triaxial_older_healthy_lower_back_external_window_metadata.csv`, `data/processed/triaxial_older_healthy_lower_back_external_window_predictions.csv`

