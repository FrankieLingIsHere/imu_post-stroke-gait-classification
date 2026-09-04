---
type: concept
---

# Age and stroke gait

Age is both a biological source of gait variation and a possible confounder of stroke classification. This page keeps the age question separate from the primary healthy-versus-CVA model. The evidence comes from the supplied review source, the Voisard metadata, and the project's executed model-development notebooks.

## What the review and current data show

- In Voisard, healthy participants average about 39.7 years and CVA participants about 59.0 years. Age correlates with several gait features, including lower-back, foot and head RMS, cadence, stride time and stride-time variability. Most feature effects remain in the expected stroke direction after participant-level age adjustment. Source: [Ling et al. review document](C:/Users/frank/Downloads/Ling_et_al_WIREs_Data_Mining_Post-Stroke_Gait_Classification.docx), [[voisard-2025]] and [[discriminative-features]].
- Age is available for all 122 primary Voisard participants. The public Felius release has 132 stroke and 34 healthy participants after the S001P duplicate exclusion, but no participant-level age or sex metadata. Age cannot therefore be used as a complete pooled input without creating source-dependent missingness. See [[felius-dataset]].
- The provisional Voisard age bands are 18--39, 40--59 and 60+. They contain 43, 42 and 37 participants across both labels. The youngest band contains 43 healthy participants and no CVA participants, so it cannot support an age-matched stroke-versus-healthy test.
- The complete local Voisard release provides wider coverage than the primary binary subset: 259 participants have valid ages from 18 to 90 years across healthy, neurological and orthopedic cohorts. One participant has an invalid or missing age value and is excluded from age analyses. The additional neurological and orthopedic participants widen coverage, but they must not be relabeled as stroke.
- The primary healthy/CVA subset spans 18--87 years. The healthy group contributes ages from 18 onward, while the CVA group begins at age 41. Therefore wider age coverage does not currently solve the missing young-stroke overlap problem.

## Does age act differently in healthy and stroke gait?

The participant-level interaction model tests `feature ~ age + stroke + age x stroke`. A significant interaction would mean that the age slope differs between healthy and stroke participants.

- Head RMS interaction p = 0.039 and lower-back RMS interaction p = 0.049 were nominally positive findings.
- After Benjamini--Hochberg correction across the six tested features, both q = 0.148. Foot RMS, cadence, mean stride time and stride-time variability were not reliable interaction findings.
- The current sample therefore suggests that group-specific age effects are possible for some RMS features, but it does not establish a stable age-dependent stroke signature. This is an interaction result, not evidence that age should be fed into the classifier.

## Gait-model performance across age overlap

The repeated pooled model was checked only in age bands containing both labels. Raw participant-level AUROC averaged 0.953 in the 40--59 band and 0.913 in the 60+ band. Raw balanced accuracy averaged 0.891 and 0.816 respectively. Each estimate comes from small fold-level strata, with about 8.4 and 7.4 participants per stratum per outer fold on average, so these values are for robustness reporting and recruitment design rather than definitive age-specific validation.

## Modelling decision

Maintain two parallel directions:

1. The primary model is a pooled healthy-versus-CVA gait classifier that does not use age as an input or a first-stage gate.
2. The secondary model predicts age from gait. Continuous age regression should be the main age endpoint. Three-class age classification remains exploratory because the healthy-only feasibility model reached AUROC 0.726, balanced accuracy 0.451 and macro-F1 0.342 across five folds and three seeds. See [10_age_classifier_feasibility](../../notebooks/10_age_classifier_feasibility.ipynb).

Do not build an age-to-stroke cascade or shared age-and-stroke multi-task model yet. First collect age-complete, age- and sex-matched external data, compare age-adjusted and unadjusted baselines, and repeat the interaction analysis in an independent cohort. The executed interaction analysis is [legacy_20_age_group_interaction_analysis](../../notebooks/archive/legacy_20_age_group_interaction_analysis.ipynb). Related pages: [[classification-methods]], [[future-directions]], [[voisard-2025]] and [[felius-dataset]].

## Continuous age regression result

The executed [legacy_21_continuous_age_regression](../../notebooks/archive/legacy_21_continuous_age_regression.ipynb) experiment used 72 healthy Voisard participants with 1,039 usable windows and repeated five-fold participant-level validation across three seeds. The engineered-feature Ridge baseline reached mean MAE 12.86 years, RMSE 15.46 years, R² 0.310 and Spearman rho 0.643. Random forest was slightly weaker. The GPU Inception-style regression model reached MAE 13.42 years, RMSE 16.48 years, R² 0.243 and Spearman rho 0.580. This supports age-related signal structure but is not accurate or stable enough to justify a staged classifier or a multi-task stroke model. Continuous regression should remain a descriptive secondary endpoint until a larger age-balanced cohort is available.

## Age-adjusted stroke baseline

The executed [legacy_22_age_adjusted_gait_baseline](../../notebooks/archive/legacy_22_age_adjusted_gait_baseline.ipynb) compared four participant-level models across 15 repeated folds. Raw engineered gait features reached mean AUROC 0.973 and balanced accuracy 0.921. Adding age reached AUROC 0.968 and balanced accuracy 0.923, so age did not improve discrimination. Age alone reached AUROC 0.803, confirming that age is a strong shortcut in this imbalanced subset. Age-residualized gait features fell to AUROC 0.882 and balanced accuracy 0.786, showing that simple residualization can remove signal that is useful for the current CVA-versus-healthy task. This result does not prove age is irrelevant, but it supports keeping age out of the primary model until age-matched external validation is available.

The current external-cohort screen found no public dataset that simultaneously provides compatible raw IMU gait signals and complete participant-level age metadata. [[external-validation-cohort]] records RevalExo as the best near-term protocol stress test, while a new age-complete age- and sex-matched cohort remains necessary for the age question.
