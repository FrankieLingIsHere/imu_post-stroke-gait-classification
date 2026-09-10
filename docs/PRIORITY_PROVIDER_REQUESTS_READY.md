# Priority schema requests — prepared, not sent

These replace the generic first-wave wording. Contact details and study sources
were verified in `VERIFIED_PROVIDER_ROUTES_2026-09-08.md`. Sender name and
institution must be added before sending. No archive is requested at this stage.

## 1. Paolo Brasiliano: primary paired lower-back evaluation

To: paolobrasilianores@gmail.com

Subject: Raw lower-back gait schema request — independent research evaluation

Dear Dr Brasiliano,

I am working on participant-level research classification of healthy and
post-stroke walking from lower-back acceleration. I would like to ask whether
the data underlying your paper, “Identifying key gait features in stroke patients
using wearable inertial sensors and supervised and unsupervised machine learning”
(doi:10.1038/s41598-026-43666-7), could support an independent evaluation.

Our first request is only for a de-identified export example or data dictionary:

- Are native L4–L5 accelerometer axes available before gravity removal, filtering
  and stride normalization? What are the export units, channel order and timestamps?
- Are walking bounds available, and do trials contain uninterrupted walking spans
  of at least five seconds after excluding standing and transition periods?
- Can participant/trial IDs link signals to diagnosis, age, sex, severity,
  chronicity, walking speed and aid use, with missing fields identified?
- Does the cohort overlap with any other released dataset or related Santa Lucia
  study? What are the conditions for external evaluation and reporting results?

Our primary model requires only the lower-back channel; foot channels are not
needed for this evaluation. A healthy-versus-stroke evaluation would be reported
separately from non-stroke differential specificity. The current model has
substantial non-stroke false positives, and we are not claiming diagnostic readiness.
We would lock the evaluation protocol before accessing any supplied test signals.

Thank you for considering this schema-level inquiry.

## 2. Santa Lucia: independent clinical non-stroke specificity

To: m.tramontano@hsantalucia.it

Subject: Lower-back gait schema inquiry for clinical specificity evaluation

Dear Dr Tramontano,

I am investigating whether a healthy-versus-stroke wearable gait research model
incorrectly assigns positive scores to people with other neurological conditions.
The study registered as NCT04691102 appears relevant to this differential-specificity
question. Could your team provide a de-identified schema example or dictionary,
or direct me to the appropriate data custodian?

The immediate questions are:

- Are native, gravity-retaining lower-back/lumbar acceleration recordings available
  for healthy and clinically identified non-stroke groups? Please specify exact
  placement, device, native units, sampling rate, channel order and timestamps.
- Which walking tasks and annotations allow five-second straight-walking segments
  to be separated from turns, standing and transitions?
- What usable participant counts and metadata are available by diagnosis, including
  age, sex, walking speed and aids? Are clinical labels and missingness documented?
- Does this cohort overlap with the Brasiliano et al. 2026 gait-feature study or
  other datasets? What access and publication conditions apply?

We need only a schema discussion initially, not a full archive. This cohort
would assess non-stroke positive-call rates; it would not by itself establish
stroke sensitivity. We would preserve participant independence and freeze the
evaluation protocol before test-signal access.

Thank you for your guidance.
