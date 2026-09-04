# Score overlap and heterogeneous rescue

Date: 2026-09-03

## Threshold feasibility

The selected lower-back deep ensemble cannot reach near-zero FP and FN by
changing its threshold. Across one cross-seed consensus prediction for each of
314 out-of-source development participants:

- the minimum total error is 58 participants;
- the most balanced error-rate threshold still produces 26 FP and 37 FN;
- zero FP requires 157 FN;
- zero FN requires 87 FP;
- the maximum healthy probability is 0.9718; and
- the minimum stroke probability is 0.1010.

The score distributions overlap substantially. Threshold optimization can only
exchange FP for FN and must not be presented as a model improvement.

## Heterogeneous rescue experiment

Notebook 31 fitted a lower-back MiniROCKET transform plus weighted logistic
classifier under the same three complete source holdouts and five seeds used by
the deep ensemble. Transformer bias windows and classifier weights were
balanced by source, class, and participant. The only tested fusion was a fixed
50:50 probability average with the accepted deep ensemble. RevalExo and NONAN
were not loaded.

The heterogeneous fusion failed every admission requirement:

| Gate result | Value |
|---|---:|
| Mean total errors, deep ensemble | 21.73 per source/seed |
| Mean total errors, heterogeneous fusion | 25.87 per source/seed |
| Relative error change | **+19.0% worse** |
| Mean FP delta | +0.73 |
| Mean FN delta | +3.40 |
| Balanced-accuracy delta | -0.0245 (95% paired bootstrap -0.0397 to -0.0089) |
| AUROC delta | -0.0047 (-0.0097 to -0.0003) |
| Brier delta | +0.0164 (+0.0107 to +0.0224) |

MiniROCKET alone and the equal fusion are rejected. The accepted lower-back
deep ensemble from notebook 29 remains the development model.

## What the failure means

This result does not show that heterogeneous time-series ensembles are invalid.
It shows that this fixed MiniROCKET/logistic representation does not add useful
three-source lower-back information to the current deep ensemble. Reweighting
the same predictions after inspecting these results would be post-hoc tuning
and is not allowed.

The more fundamental mismatch is label granularity: a participant diagnosis is
copied onto every five-second gait window, although a stroke participant can
produce near-normal windows and a healthy participant can produce atypical
windows. Mean probability pooling cannot learn which windows are diagnostically
reliable.

## Next model gate

The next candidate is participant-level multiple-instance learning (MIL):

1. Treat each participant/trial as a bag of real lower-back windows.
2. Reuse an Inception-style window encoder.
3. Learn gated-attention pooling over window embeddings.
4. Apply the binary healthy/stroke loss once per participant, not once per
   window.
5. Use source/class-balanced participant batches and sample a fixed number of
   windows per bag during training.
6. Tune only inside the two outer training sources and repeat complete-source
   holdout across five seeds.
7. Require FP and FN to be non-increasing, at least 10% total-error reduction,
   and the existing worst-source discrimination/calibration safeguards.

If MIL fails, the limiting factor should be recorded as cohort/label overlap,
not addressed through repeated threshold or ensemble searches. Near-zero
binary errors would then require new representative paired participants. A
confidence/referral zone could reduce errors among automated decisions but
would no longer classify every participant automatically.

