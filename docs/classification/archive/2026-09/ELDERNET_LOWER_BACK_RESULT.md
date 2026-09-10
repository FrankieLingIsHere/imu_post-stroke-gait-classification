# ElderNet lower-back frozen-encoder transfer: corrected result

> Follow-up: [partial adaptation](ELDERNET_PARTIAL_RESULT.md) is now complete.
> It improved AUROC over its matched frozen control but failed advancement gates.
> This report preserves the earlier frozen logistic-head comparison.

Executed 2026-09-09 under the [locked protocol](../../ELDERNET_LOWER_BACK_PROTOCOL.md).
The pretrained encoder did not improve specificity relative to the identical
randomly initialized frozen encoder. Both prospective comparison gates failed.
Keep the existing stroke models. No checkpoint promoted.

## Corrected results

| Scope / encoder | Participants | AUROC | Stroke detected | Healthy FP | Neurological FP | All other FP |
|---|---:|---:|---:|---:|---:|---:|
| Available / random | 146 | 0.703 | 38/44 | 3/12 | 42/71 | 45/90 |
| Available / pretrained | 146 | 0.553 | 39/44 | 6/12 | 58/71 | 74/90 |
| Matched available / random | 105 | 0.568 | 41/44 | 3/4 | 50/57 | 50/57 |
| Matched available / pretrained | 105 | 0.569 | 42/44 | 3/4 | 54/57 | 54/57 |

Thresholds use only each outer training set's inner stroke OOF scores, targeting
90% sensitivity. Actual held-out sensitivity can differ. Forty-eight head fits
completed, encoders ran on CUDA. All required pretrained encoder keys loaded
strictly; the speed regressor was discarded. Frozen batch-normalization state
was not updated on test data. Each trial's windows were averaged before averaging
trials within a person. No demographic or diagnosis predictor was supplied.

## Coverage and limits

1,785 complete ten-second straight-walking windows were available. Of 259 people,
146 contributed at least one window: healthy 12/72, stroke 44/49, ACL 3/11,
CIPN 11/19, HOA 6/15, KOA 10/18, PD 18/24, RIL 42/51. All people remain in the
coverage ledger. Missing people have no predictions and are not counted negative.
No short bouts were stretched, padded or joined across turns.

The duration requirement strongly changes the cohort composition and may favor
slower walkers. Only four healthy participants remain in the matched subset.
One outer training split has two healthy people, so some inner validation folds
contain no healthy people; all inner training folds retain all three target
groups. Those small counts make healthy-specificity estimates unstable.

This tests **head-only adaptation of frozen features**, using one random seed.
It does not compare fully trained random and pretrained neural networks. It is
not end-to-end fine-tuning, autonomous walking detection, cross-source validation,
or an exhaustive rejection of gait pretraining. Event annotations select walking
segments. Pretraining provenance is upstream-reported; TVS is not an independent
test because it supplied ElderNet fine-tuning data.

Before an end-to-end experiment, address this ten-second input's severe coverage
loss. Do not lower the window duration silently: it changes the pretrained model's
temporal contract. A shorter-window-compatible pretrained model or a separately
specified sequence adapter would need its own controlled evaluation.

## Verification and invalid first attempt

The first attempted run omitted native m/s²-to-g conversion. Its results and the
initial chat numbers are **invalid**, preserved explicitly under
`data/processed/eldernet_lower_back_units_error_v1/INVALID_RESULT.txt`.
No model was selected from that run. Both arms were rerun with division by
9.80665 before polyphase resampling, as required by the input contract.
Two regression tests now verify physical scale, channel identity, shape and
rejection of short/nonfinite windows. Both passed. The corrected numerical
results above supersede all earlier numbers for this experiment.

Valid artifacts: `data/processed/eldernet_lower_back_v1/` contains source hashes,
window and participant coverage, embeddings, inner/outer predictions, thresholds,
metrics, per-pathology counts, paired calls and gate decision. Historical phase+HR
predictions on the same available participant IDs are saved separately as context;
they used different inputs and broader training cohorts and are not a matched
architecture comparator.

No new raw data or model downloads. Existing signals were preprocessed for this
new input, encoding and nested head evaluation completed. Independent validation
and end-to-end fine-tuning remain unexecuted.
