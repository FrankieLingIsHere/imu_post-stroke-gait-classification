# DUO-GAIT follow-up and comparable differential-classification evidence

> Subsequent execution: [waveform-frame six-channel training and DUO-GAIT evaluation](GAIT_FRAME_RESULT.md) completed and failed its primary gate. Anatomical calibration remains unverified. Historical pending statements below do not mean that this waveform-frame experiment is still pending.
2026-09-09. Historical inventory. Subsequently, [frozen magnitude inference completed](DUOGAIT_GAIT_CNN_RESULT.md); directional transfer remains pending.

The gait_cnn 36-fit benchmark used Voisard only. Earlier project work used
DUO-GAIT, including full-cycle extraction. The old event audit is superseded by
`reports/DUOGAIT_FULL_CYCLE_EXTRACTION.md`, not a current reason to defer use.
The old extraction script points to a pre-archive path and extracts acceleration
magnitudes, not the new six/eighteen-channel representation. Its interval selection
does not explicitly check every outlier/turn/interruption flag, so its prose claim
of clean cycles must not substitute for checking those flags in a new adapter.

Local inventory verified today: `data/archive/raw/duogait_2023/data` contains
SA/LF/RF CSVs and left-foot core event tables for all 16 participants in each of
OG_st_control, OG_st_fatigue, OG_dt_control and OG_dt_fatigue. Example signal columns
include AccXYZ and GyrXYZ; event columns include ic_samples, fo_samples, is_outlier,
turning_step, turning_interval and interrupted. This is file/header verification,
not complete signal-quality or synchronization validation. No download is needed.

The [primary DUO-GAIT paper](https://www.nature.com/articles/s41597-023-02391-w)
describes 16 healthy adults, four walking conditions and synchronized 128 Hz
acceleration/angular velocity at nine placements. The upstream gait_cnn optional
DUO-GAIT configuration classifies single-task fatigue versus control. That task
does not train a stroke label. Its current default instead uses stroke visits.

The next useful external-negative test is frozen gait_cnn inference on the four
conditions, preserving training scalers and thresholds, matching axis conventions
and gyro units across sources, using physical-frequency filtering at 128 Hz and
the same 200-point phase representation. Inspect official exclusion flags and
timestamp correspondence before extraction. Report all seeds, participant-level
FP by condition, paired score changes and coverage. Healthy-only testing cannot
measure stroke sensitivity. Keep this set out of training for that test. Prior
project exposure means it is not a pristine never-inspected external dataset.

Comparable evidence:

- [Mannini et al. 2016](https://pmc.ncbi.nlm.nih.gov/articles/PMC4732167/) is already
  in the wiki: stroke, Huntington's disease and elderly controls, HMM/SVM with
  subject holdouts and participant voting. It motivates differential controls and
  sequence modeling, not a newly discovered raw dataset or a CNN checkpoint.
- [Zannat 2026, revision 2](https://arxiv.org/abs/2604.18372v2) is a newly checked
  preprint abstract: bilateral wrist IMUs on PADS, PD versus healthy and differential
  diagnoses. It reports sensitivity .994 for the former and .812 for the latter.
  This is an analogous specificity challenge, not evidence of our model's cause.
  Its wrist motor-assessment contract is not a lower-back gait replacement.
  Full-text methodology, code and weights have not been audited here.
- [Fischer's institutional thesis abstract](https://hpi.de/en/arnrich/teaching/fischer/)
  describes the directly related fatigue/dual-task gait CNN work and distinguishes
  within-person from unknown-person sensor findings. Reproducing its task is a
  separate implementation benchmark, not stroke-validation evidence.

Metadata and archived signal/event availability verified. New gait_cnn DUO-GAIT
preprocessing and evaluation remain unexecuted. Independent positive-cohort
validation remains open.
