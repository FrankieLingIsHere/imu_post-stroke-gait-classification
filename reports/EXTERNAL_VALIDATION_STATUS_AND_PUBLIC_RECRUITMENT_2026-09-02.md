# External-validation status and public-cohort screen

## Bottom line

The three-channel Felius+Voisard+Sint prototype is a research prototype, not a
clinically validated classifier. Sint was valid as a frozen external evaluation
only before it entered the separately labelled expansion experiment. It cannot
also test the expanded model. The expanded model's only paired untouched
external score is RevalExo, with 17 people; this is too small for a clinical
performance claim.

## Verified current prototype result

The saved `full_expanded_inception_prototype_seed_42.pt` checkpoint was
re-executed on CUDA on 2026-09-02 against the untouched RevalExo tensor. This
reproduced the reported result exactly enough for display:

| Item | Result |
|---|---:|
| Participants | 17 (7 healthy, 10 stroke) |
| Participant AUROC | 0.9143 |
| Brier score | 0.1611 |
| Balanced accuracy at existing 0.50 reference | 0.7143 |
| Stroke detection | 10/10; Wilson 95% interval 72.2%–100.0% |
| Healthy specificity | 3/7; Wilson 95% interval 15.8%–75.0% |

These intervals are deliberately wide. They describe this small cohort only;
they do not establish stable sensitivity or specificity in a clinical
population.

### Artifact provenance correction

The files named `full_expanded_prototype_revalexo_*` had been overwritten on
2026-09-01 by a later experiment without identifying its checkpoint. The
benchmark now records the checkpoint name and accepts `OUTPUT_PREFIX`, so
future probes cannot overwrite the canonical result. The re-executed canonical
artifacts are:

- `data/processed/full_expanded_prototype_revalexo_metrics.csv`
- `data/processed/full_expanded_prototype_revalexo_participant_predictions.csv`
- `data/processed/full_expanded_repro_check_2026_09_02_revalexo_metrics.csv`

## Second paired public-cohort screen

| Candidate | What is genuinely available | Decision |
|---|---|---|
| Sint Maartenskliniek | 20 healthy + 10 stroke; lower back + both feet; already used first as a frozen external cohort, then in the expanded training sensitivity stream | Not available as a final-model test after expansion; retain its correctly separated historical role |
| Kiel Validation Dataset | Public repository has only 10 healthy participants. It documents a future protocol with neurological/stroke participants, but states that further data are available on request | Not a public paired external cohort; do not request private data in this online-only project without new authority |
| Wang et al. 2021 gait release | Publication reports 8 stroke + 7 healthy people and a historical direct archive URL. The archive timed out on 2026-09-02. The reported representation is cycle-level lower-limb angular velocity, not a documented LB/LF/RF acceleration contract | Do not acquire or pool; even if recovered, it is a separately adapted lower-limb study, not a direct three-channel external test |
| Mannini/Trojaniello 2016 | Published paired elderly/post-stroke gait study with waist and shank IMUs | No reproducible public raw-data release identified in this screen |
| Soangra/John | Public paired L5/S1 IMU data | Naturalistic ADL, not verified gait-labelled data; unsuitable for this gait validation role |

The Kiel public repository itself confirms that the released ten participants
are healthy only and that additional data require contact. Wang et al. report
the small paired cohort and the now-unreachable archive, while also explaining
the gait-cycle angular-velocity representation. Sources: [Kiel repository](https://github.com/neurogeriatricskiel/Validation-dataset), [Wang et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC7962128/), [Mannini et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC4732167/), and [Soangra/John data page](https://digitalcommons.chapman.edu/pt_data/3/).

## Decision and next authorised work

No newly screened public dataset is cleared for download, training, or final
external evaluation. The evidence-based priority is to locate a second
fully-public, paired stroke--healthy **gait** IMU cohort with raw or
reconstructable acceleration and a defensible lower-back/bilateral-foot mapping.

Until such a cohort exists, do not claim clinical readiness, retune against
RevalExo, reuse Sint as a final-model test, fabricate channels, or use
synthetic data as a substitute for independent participants.

