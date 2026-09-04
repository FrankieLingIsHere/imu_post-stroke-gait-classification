---
type: index
---

# Index

Catalog of every page in this wiki. Read this first when answering a query — drill into specific pages from here rather than grepping the vault blind.

## Start here

- [[synthesis]] — top-level narrative, the review's headline findings and open questions.
- `CLAUDE.md` — the schema for this vault: page conventions, linking rules, session-start protocol, and the **Skill Map** (Ingest, Sync, Source Search & Enrichment, Draft Assist, Query, Lint). Read this every session before editing anything.
- `llm-wiki.md` — the underlying pattern this vault implements (Karpathy's LLM Wiki).
- `templates/` — starter frontmatter + section skeleton for each page type (study, dataset, concept, review).
- `raw/` — staging inbox for candidate sources not yet resolved into a real page. Should normally be near-empty; see `raw/README.md`.
- `numbers-registry.md` — every load-bearing number restated in more than one manuscript location, with all its locations listed. Check and update this in the same edit batch as any change to a Section 4.2 or Table 6 figure — this is the tool meant to stop the "fix landed in one paragraph, not its siblings" pattern that has been this project's single most common recurring bug across the `journal-critic` review-loop rounds (see `log.md`).

## Concepts (12)

- [[research-questions]] — the three RQs anchoring the review (RQ3 and RQ4 merged 2026-07-23).
- [[eligibility-criteria]] — IC1/IC4/IC5 pathways and EC1/EC2 exclusions; which studies qualify and why.
- [[discriminative-features]] — RQ1: what separates healthy from post-stroke gait, literature + this review's own re-mining.
- [[sensor-placement]] — RQ2: trunk-placement convergence, the raw-magnitude-vs-discriminative-value distinction, the one open disagreement.
- [[classification-methods]] — RQ3: classical-to-deep-learning evolution and the datasets behind it, the still-unresolved classical-vs-deep comparison.
- [[quality-assessment]] — Section 3.6's four criteria applied to all 22 eligible studies (corrected 2026-08-05 from a stale "14"); several concrete red flags found.
- [[placement-vs-practicality]] — the trunk-accuracy-vs-pocket-deployability tension, and a tiered-deployment reframe.
- [[future-directions]] — seven concrete next steps, each traced to a specific gap above.
- [[age-and-stroke-gait]] — age confounding, age-by-stroke interactions, age-overlap performance and the parallel age-model decision.
- [[external-validation-cohort]] — screening and ranking of candidate external cohorts for frozen model validation.
- [[concepts/evidence-gate-cross-dataset-imu]] — mandatory paper/code/task/split audit before any new pooling, normalization, domain-generalization, SSL, or synthesis experiment.
- [[concepts/evidence-gated-model-improvement]] — five-seed source-held-out result admitting a complementary-error lower-back ensemble and defining the final-test requirement.

**Stale count fixed 2026-08-05** (seven studies ingested across two passes; see `log.md`'s 2026-08-05 ingest entries): the manuscript's Table 3 caption reads "26 included studies," Table 4 (quality assessment) covers 22. **Six studies with unresolved status, found but not investigated**: the same source folder that supplied this pass's seven PDFs also contains six LeMoyne & Mastroianni papers (2018-2021) not mentioned anywhere in the current manuscript at all — unclear whether these were ever screened and excluded, or are a genuine unscreened gap. Flagged for the user to clarify before any further ingest.

## Included studies (26 with wiki pages — matches the manuscript's current Table 3 count exactly)

| Study | Pathway | Method |
|---|---|---|
| [[mannini-2016]] | IC1 | HMM + SVM |
| [[hsu-2018]] | IC1 | RF/AdaBoost/DT/NB/MLP |
| [[wang-2021]] | IC1 | Two-stage DNN |
| [[hsu-2021]] | IC1 | SVM (lower verification tier) |
| [[lee-2018]] | IC1 | Random Forest |
| [[pohl-2022]] | IC4 | SVM/LR/k-NN, nested CV |
| [[obrien-2022]] | IC4 | Balanced RF (self-disclosed leakage) |
| [[sun-2025]] | IC4 | Stepwise regression (no CV found) |
| [[brasiliano-2026]] | IC1 | k-NN/SVM/DT, SBS |
| [[inui-2026]] | IC1 | ML classification (clean sweep on quality assessment) |
| [[abdollahi-2024]] | IC4 | Random Forest |
| [[shin-2022]] | IC1 | CNN, pocket placement |
| [[lee-2025]] | IC1 | CNN-LSTM, smartphone pocket |
| [[avvenuti-2018]] | IC5 | Threshold-based, no stroke population |
| [[ensink-2023]] | IC5 | Threshold-based |
| [[felius-2024]] | IC5 | Variational autoencoder (dual role, see [[felius-dataset]]) |
| [[wu-2025]] | IC4 | 1D CNN + severity regression |
| [[obrien-2024]] | IC4 | L1-logistic regression, classical only (corrected 2026-08-05: confirmed in manuscript, not "not yet") |
| [[rojek-2025]] | IC4 | SVM/RF/kNN/CNN head-to-head (corrected 2026-08-05: confirmed in manuscript, not "not yet") |
| [[scheffer-2012]] | IC1 | Backpropagation ANN, 16-sensor full-body suit — added 2026-08-05 |
| [[iosa-2021]] | IC1 | Feedforward ANN vs. logistic regression, sacral IMU — added 2026-08-05 |
| [[shih-2021]] | IC1 | DNN, bilateral shank, cross-system/cross-dataset tested — added 2026-08-05 |
| [[tas-2024]] | IC1 | Wavelet decomposition + LogitBoost, Brunnstrom stage — added 2026-08-05 |
| [[orfanos-2026]] | IC1 | Random Forest, gyroscope-only shank features — added 2026-08-05 |
| [[yang-2026]] | IC4 | LDA, single shank IMU vs. MoCap — added 2026-08-05 |
| [[igarashi-2024]] | IC5 | Threshold/AUC analysis, no trained classifier — strongest external trunk-RMS corroboration, added 2026-08-05 |

## Datasets audited in hands-on mining (10)

| Dataset | Role |
|---|---|
| [[voisard-2025]] | primary — real paired stroke/healthy |
| [[carpinella-2026]] | external healthy controlled 6MWT lower-back IMU — 60 participants, acquired and validated |
| [[soangra-john-2022]] | paired lower-back naturalistic-activity IMU — raw release acquired; not gait-labelled; decoder pending |
| [[felius-dataset]] | primary — real paired stroke/healthy |
| [[sint-maartenskliniek]] | paired Xsens stroke/healthy; expanded-development source and verified lower-back 6-DoF adapter |
| [[gaitmotion]] | simulated — not real patients |
| [[duo-gait]] | healthy-only reference |
| [[oxwalk]] | healthy-only reference |
| [[marea]] | healthy-only reference |
| [[camargo-2021]] | healthy-only reference (unparseable format) |

## Prior reviews (5)

- [[jiao-2024]] — methodological quality in post-stroke gait classification.
- [[da-silva-2024]] — measurement reliability of wearable-derived post-stroke gait parameters.
- [[prisco-2024]] — general inertial-sensor validity across pathologies.
- [[boukhennoufa-2022]] — ML in post-stroke rehabilitation assessment broadly.
- [[jourdan-2021]] — ML validating commercial wearable gait sensors across populations generally.

## Raw sources (immutable, outside this vault)

- `../docs/Review_Paper_Draft.docx` — the manuscript.
- `../docs/Sources_Search_Log_and_Datasets.docx` — search log and dataset registry.
- `../notebooks/01_post_stroke_gait_baseline.ipynb` — hands-on data-mining notebook.
## Current next action

For repository navigation, start at
`../notebooks/00_READ_THIS_FIRST.md`. The complete notebook archive remains
available for audit, but the first-reader evidence path is 01 → 02 → 29 → 30 →
34. Notebook 33 supplies the implementation audit that authorized the final
corrective benchmark.

Notebook 34 completed the bounded canonical correction. No candidate passed:
InceptionTime canonical mechanics raised mean errors from 21.73 to 32.13,
canonical 10k MiniROCKET raised them to 23.27, and the closest
incumbent/MiniROCKET fusion reached 22.13. That fusion reduced FP but increased
FN and regressed Felius and Sint despite helping Voisard. RevalExo and NONAN
were not loaded. Keep the notebook-29 lower-back ERM + CORAL + ERM++-style
ensemble frozen, stop architecture rotation on these 314 participants, and
move to a new untouched paired-cohort evaluation. Three channels remain a
secondary comparator.

The subsequent score-frontier audit proved that no threshold can make both FP
and FN nearly zero. A five-seed MiniROCKET/deep heterogeneous fusion increased
total errors by 19.0% and was rejected. Participant-level multiple-instance
learning was then tested: mean pooling reduced total errors only 1.8% while
significantly lowering balanced accuracy and AUROC, and gated attention was
worse. Both were rejected. The current deep ensemble is frozen; the next
requirement is a new untouched paired cohort, not further post-hoc selection on
the same development participants.

The exact official-code audit corrected the interpretation of older local
variants and authorized notebook 34. The resulting test closes the outstanding
InceptionTime and MiniROCKET baseline gap under the project protocol; it does
not convert unrelated local DDPM, GroupDRO, or ERM++-style experiments into
exact reproductions. See [[concepts/prior-method-code-alignment]] and
`../reports/CANONICAL_CORRECTIVE_BENCHMARK_2026-09-03.md`.

The requirements in [[concepts/evidence-gate-cross-dataset-imu]] remain
mandatory before any later modeling change. The 2026-09-03 deep audit found that recent successful
work often addresses generic activity recognition, gait detection, or
target-aware adaptation rather than source-only stroke diagnosis. The next
experiment must therefore have a paper-and-code-traced protocol, matched ERM,
participant/source-disjoint validation, and no RevalExo/NONAN selection. See
`../reports/EVIDENCE_GATE_CROSS_DATASET_IMU_2026-09-03.md`.

Follow [[concepts/recruitment-protocol]] for age-overlapping healthy and post-stroke recruitment before attempting domain adaptation.

The 2026-09-01 pipeline comparison found the project stronger than common practice on participant-level splits, source-aware pooling, frozen external evaluation, and negative-result gates, but identified unresolved contract risks: 200-point event cycles versus 500-sample windows, magnitude-only inputs, source-specific event definitions, artificial synthetic parent IDs, and architecture mismatch in the pretraining probe. The next action is a locked preprocessing-contract and raw-axis-versus-magnitude ablation before further architecture changes. See `../reports/PIPELINE_RESEARCH_COMPARISON_AND_PROCESSING_AUDIT_2026-09-01.md`.

The contract check additionally confirmed that development raw tri-axial tensors are not currently available in `data/processed`; only 3-channel magnitude arrays are stored. RevalExo's 18-channel tensor is frozen external data and cannot train the missing raw-axis comparison. Recovering development raw channels from the immutable source releases is therefore a prerequisite, not an already-completed experiment.

The raw-source inventory completed 2026-09-01 found 1,356 Voisard raw text files and 1,148 Felius raw CSV files, making a primary-dataset raw-axis audit feasible. No directly usable Sint CSV raw files were found in the extracted release, so Sint remains magnitude-only until its format is adapted and verified. See `data/processed/development_raw_axis_inventory.csv` and [[../reports/PIPELINE_RESEARCH_COMPARISON_AND_PROCESSING_AUDIT_2026-09-01]].

The first linkage check found 16,366 Felius processed windows, but their stored trial IDs do not directly match the raw Felius filenames. Raw-axis reconstruction therefore requires a verified metadata-key join before any new tensor is generated; no raw-axis result should be reported yet.

This linkage was subsequently resolved. A verified signed-axis tensor now contains all 18,511 Voisard/Felius windows in `(18511, 500, 9)` format, with exact magnitude reproduction after unit harmonization (maximum error approximately 1e-6). It is ready for the raw-axis versus magnitude ablation; existing magnitude artifacts remain unchanged.

The corrected five-fold ablation found magnitude mean AUROC/Brier/balanced accuracy `0.9794/0.0660/0.9080` versus signed-axis `0.9741/0.0563/0.9274`. Signed axes improve calibration and balanced accuracy but not AUROC; frozen external evaluation and repeated seeds are still required before changing the official representation.

The frozen RevalExo signed-axis test resolved the uncertainty: signed axes achieved AUROC `0.457`, Brier `0.412`, balanced accuracy `0.500`, and `7/7` healthy false positives, versus the magnitude baseline `0.914/0.161/0.714` and `4/7` healthy false positives. Keep magnitude as the official representation; signed axes are internal-only until sensor-frame alignment is validated.

The specificity audit shows that zero false positives is incompatible with high sensitivity on the current RevalExo scores: the highest healthy score is `0.895`, while four of ten stroke scores are below that value. The recommended design is a specificity-first threshold with an indeterminate/confirmatory zone, followed by hard-negative healthy and non-stroke specificity testing. See `../reports/SPECIFICITY_FIRST_FALSE_POSITIVE_STRATEGY.md`.

The native-window synthesis candidate completed 2026-09-01. It generates directly in the classifier's `500 x 3` contract, avoiding the former 200-cycle-to-500-window mismatch. MAREA real/synthetic mean and SD are `1.431/0.880` vs `1.421/0.748`; DUO-GAIT `1.462/0.914` vs `1.449/0.800`. DUO-GAIT roughness is close to real, but mild under-dispersion remains. Keep it quarantined pending 5/10/20% utility tests. See `../reports/NATIVE_HEALTHY_WINDOW_SYNTHESIS_2026-09-01.md`.

Internal ratio selection rejected 10% and 20% synthetic healthy enrichment. Five percent increased mean participant balanced accuracy from `0.9112` to `0.9210`, but reduced AUROC from `0.9826` to `0.9747` and worsened Brier from `0.0655` to `0.0683`. It remains a cautious candidate pending repeated-seed confirmation; RevalExo has not been used to choose this ratio.

Repeated seeds 42–44 rejected the remaining 5% candidate: real-only versus 5% synthetic was AUROC `0.9777` vs `0.9731`, Brier `0.0712` vs `0.0715`, and balanced accuracy `0.9076` vs `0.9082`. The negligible balanced-accuracy difference is not stable or material; direct synthetic enrichment is not admitted, and RevalExo was not reused to tune it.

The next improvement direction is population robustness rather than further direct synthetic enrichment: worst-source/protocol validation, group-robust real-data training, physically constrained real-signal augmentation, specificity-first abstention, hard-negative clinical/older-healthy evaluation, and a second independent cohort. See `../reports/POPULATION_ROBUSTNESS_IMPROVEMENT_PLAN.md`.

The initial leave-one-source-out group-DRO test was not admitted as a global replacement. It improved held-out Sint AUROC/BA (`0.905/0.800` to `0.955/0.850`) but raised Sint healthy false positives from `0/20` to `4/20`; it also worsened Felius calibration and Voisard healthy false positives (`19/72` to `25/72`). Source-balanced ERM remains the safer baseline while targeted Voisard healthy hard-negative analysis proceeds.

The predeclared physical-augmentation test was also rejected on the fully held-out Voisard source. Training on Felius+Sint with small gain/noise/cadence perturbations produced AUROC/Brier/balanced accuracy `0.883/0.178/0.779` and `26` healthy false positives, versus unaugmented source-balanced ERM `0.897/0.131/0.807` and `16` false positives. RevalExo was untouched. The evidence points away from generic signal perturbation and toward a locked, participant-level out-of-fold specificity/abstention rule plus real hard-negative evaluation.

The development-only OOF specificity audit was completed on 314 real participants in five participant-disjoint folds. A positive threshold of `0.78` is the most sensitive rule with pooled healthy specificity `96.8%` (95% Wilson LCB `92.1%`) and >=90% observed healthy specificity in every source; its pooled sensitivity is only `63.8%` (worst source `60.0%`). No automatic-healthy threshold met both pooled and per-source sensitivity criteria. This is therefore a high-specificity referral candidate only, not a clinically safe two-sided triage rule. See `../reports/SPECIFICITY_FIRST_FALSE_POSITIVE_STRATEGY.md`; the threshold is locked for one descriptive external check without retuning.

The locked RevalExo check is complete: applying `0.78` to the saved full-expanded prototype yields 6/7 healthy true negatives and 7/10 stroke true positives (specificity `85.7%`, sensitivity `70.0%`, balanced accuracy `77.9%`), compared with 1/7 healthy true negatives and 10/10 stroke true positives at `0.50`. The cutoff was not adjusted afterwards. It reduces false positives but does not eliminate them or establish clinical performance because the external healthy sample is only seven people.

The unused non-CVA cohorts within the local Voisard release were evaluated as participant-disjoint, same-protocol **hard negatives**, never as training labels. Across 138 people (ACL, CIPN, HOA, KOA, PD, RIL) and 5,340 canonical LB/LF/RF magnitude windows, the saved full-expanded model predicts stroke for 72/138 (`52.2%`) at 0.50 and 43/138 (`31.2%`) at locked 0.78. RIL and PD have the highest rates (`62.7%` and `62.5%` at 0.50). The model is therefore not yet stroke-specific in a clinical differential setting; adding more generic healthy windows alone cannot establish that property. Full audit: `../reports/VOISARD_NONSTROKE_HARD_NEGATIVE_EVALUATION_2026-09-01.md`.

The requested binary-only hard-negative exposure experiment is complete. It retained a single stroke probability output and held out each non-CVA pathology cohort in turn. High exposure (25% of each batch) cut unseen non-stroke FPs from `52.2%` to `31.2%` but failed the independent primary-task safety gate (Brier `0.0904` to `0.1404`, BA `0.8941` to `0.8236`). Low exposure (7.7%) preserved primary OOF AUROC/Brier/BA (`0.9585/0.0838/0.8901`) but reduced hard-negative FPs only to `46.4%`; PD and RIL remained problematic. Neither is admitted to the final binary baseline. The real data limitation remains differential stroke specificity, rather than a lack of generic healthy windows.

Binary data readiness was reassessed after the specificity and hard-negative experiments. The 314-person real development pool is sufficient for a research prototype, but not for a clinical-ready binary decision rule: RevalExo contains only 7 external healthy people, the OOF high-specificity threshold loses substantial sensitivity, demographic linkage is incomplete, and non-stroke Voisard cohorts expose differential-specificity failure. No newly screened public release is a direct drop-in three-channel paired stroke/healthy expansion. Soangra/John's CC-BY paired 100-Hz DynaPort 6-axis L5/S1 release was acquired, but audit shows it is naturalistic ADL rather than gait-labelled and therefore cannot fill that gap; WearGait-PD is a large age-matched healthy/PD hard-negative IMU source; the 60-person 100-Hz 6MWT lower-back IMU release is age-balanced healthy normative data. Full decision and links: `../reports/BINARY_DATA_READINESS_AND_PUBLIC_RECRUITMENT_2026-09-01.md`.

The Soangra/John raw release was subsequently downloaded interactively and normalised into `data/raw/soangra_john_2022/`: 13 CK stroke and 19 SUP healthy lower-back DynaPort recordings, each with 100 Hz accelerometer and gyroscope header settings. The release is three-day naturalistic ADL data and its supplied code yields group-labelled movement windows, not verified gait labels. It is therefore a ready **raw activity-domain context source**, not a gait external-validation cohort. The vendor-specific OMX format still needs a validated decoder before any model input is produced; the three-channel gait baseline remains unchanged. See [[soangra-john-2022]].

The acquired Carpinella 6MWT cohort supplies the missing controlled, age-diverse healthy **gait** check for the lower-back track. A frozen lower-back-only baseline was evaluated on 60 fully external healthy participants (6,109 author-segmented straight-walking windows) and made 0 false-positive stroke calls at the unchanged 0.50 reference; the 95% Wilson upper bound is 6.0%. This is strong but one-sided healthy specificity evidence—not paired external stroke validation, not a basis for retuning, and not a reason to replace the three-channel prototype. See [[carpinella-2026]].

The separate Zenodo stroke-only component audit then found 9/10 three-channel and 10/10 lower-back frozen-model detections at the same 0.50 reference. Never combine that result with Carpinella's healthy result into a single binary metric: the two releases differ in device and protocol. That historical component audit did not settle the primary model. The later source-held-out development gate in [[concepts/evidence-gated-model-improvement]] makes lower back the primary research and deployment track, with three channels retained as a comparator.

Sint Maartenskliniek is the first independent paired public gait examination (20 healthy, 10 stroke; lower back and both feet). Its frozen external Inception result was AUROC 0.915, Brier 0.097, and balanced accuracy 0.850. It was only then assessed in a separately labelled source-balanced training sensitivity experiment; the expanded prototype's one-time untouched RevalExo result was AUROC 0.914, Brier 0.162, and balanced accuracy 0.714. A second independent paired cohort—not a first one—is now the outstanding transportability evidence gap. See `../reports/SINT_MAARTENS_PUBLIC_DATASET_DECISION.md` and `../reports/SINT_SENSITIVITY_TRAINING.md`.

Important governance consequence: because Sint was subsequently admitted to the expanded model's training stream, its earlier frozen result does **not** validate that expanded model. Re-testing on Sint would be in-sample evaluation. The expanded model has only the 17-person RevalExo paired external test, which is insufficient for a clinical-ready claim; a new untouched paired cohort is mandatory.

The current RevalExo checkpoint result was re-executed and provenance-locked on 2026-09-02: AUROC 0.9143, Brier 0.1611, BA 0.7143. Its threshold-dependent uncertainty is large (10/10 stroke detections, Wilson 72.2%–100.0%; 3/7 healthy true negatives, 15.8%–75.0%). No newly screened public source is cleared as the required second paired cohort. See `../reports/EXTERNAL_VALIDATION_STATUS_AND_PUBLIC_RECRUITMENT_2026-09-02.md`.

A second frozen lower-back healthy audit on the locally acquired Terrier/Piergiovanni older cohort (59 people aged 65–88) yielded 53/59 false positives. Its median lower-back magnitude is 0.578 g, far below the model contract (training mean 1.016 g), so this is an unresolvable data-representation mismatch rather than defensible evidence of age bias. It must not be pooled, rescaled by guesswork, or used for threshold selection. See [[datasets/triaxial-older-healthy]].

For an online-only project, follow [[datasets/online-data-expansion]] and assign each public dataset to binary training, pretraining, specificity testing, or context before downloading or pooling it.
