---
type: synthesis
---

# Synthesis — Autonomous Wearable-based Post-Stroke Gait Classifications

The top-level narrative page. Mirrors the manuscript's Discussion and Conclusion, but as a living, linkable document. Start here, then follow links out to whatever's relevant.

## The core contribution

No existing review connects three threads at once: which features discriminate post-stroke gait ([[discriminative-features]]), which classification methods exploit them and how well ([[classification-methods]]), and how placement practicality affects real-world deployability ([[sensor-placement]], [[placement-vs-practicality]]). [[jiao-2024]], [[da-silva-2024]], [[prisco-2024]], [[boukhennoufa-2022]], and [[jourdan-2021]] each cover pieces of this. None combines them within a stroke-specific scope.

This review closes that gap through two strands, kept evidentially distinct throughout: a PRISMA-guided synthesis of 17 included studies ([[eligibility-criteria]]), and original hands-on data mining directly on 7 open gait datasets ([[voisard-2025]], [[felius-dataset]], [[gaitmotion]], [[duo-gait]], [[oxwalk]], [[marea]], [[camargo-2021]]).

## The headline findings

1. **Trunk/lower-back placement is the most consistent, age-independent discriminator**, corroborated across five independent studies and both real hands-on-mined datasets. See [[sensor-placement]].
2. **A real demographic-confound discovery**: [[voisard-2025]]'s raw cadence effect reverses direction entirely once age is controlled for — a finding neither [[jiao-2024]] nor the measurement-validity reviews report, because it required re-mining real signal data, not just synthesizing published results. A second, independent gender confound was found the same way. See [[discriminative-features]].
3. **A real signal-processing failure caught and fixed**: naive Fourier-domain peak-picking on [[marea]] produced a physiologically impossible cadence by locking onto the wrong harmonic; autocorrelation-based detection fixed it, and the same fix revealed a placement-dependent step-vs-stride periodicity confusion.
4. **A genuine deployment tension, not just an evidence gap**: trunk placement wins on accuracy, pocket placement wins on practicality, and no single study tests both in a systematic multi-placement comparison against the same stroke cohort. See [[placement-vs-practicality]].
5. **Quality assessment, applied for real**: [[quality-assessment]] surfaces two concrete methodological red flags — [[sun-2025]]'s apparent lack of any train/test split, and [[obrien-2022]]'s self-disclosed partial leakage — plus systemic weaknesses in control-group matching and code availability across the field.

## Current project model-development layer

The review evidence and the new deep-learning development experiments must remain separate. The current executed model work supports pooled Voisard plus Felius training with global fold normalization and equal source-by-label participant-cell weighting. Repeated outer validation gives mean AUROC 0.944 overall, 0.920 on Felius and 0.973 on Voisard. Calibration improves Brier score from 0.102 to 0.091 and ECE-10 from 0.141 to 0.112, but validation-derived thresholds range from 0.339 to 0.859, so no clinical threshold is fixed. See [[classification-methods]].

Age is being developed as a parallel secondary direction, not as an automatic input to the stroke model. The age interaction audit found nominal head and lower-back RMS interactions, but neither survives six-feature Benjamini--Hochberg correction. Only the middle and older Voisard bands contain both labels. The full decision and limitations are recorded in [[age-and-stroke-gait]].

The complete local Voisard release has valid ages from 18 to 90 across 259 participants, but the added coverage includes neurological and orthopedic cohorts rather than additional young CVA controls. Continuous age regression on the healthy subset is modest: engineered-feature Ridge reaches MAE 12.86 years and R² 0.310, while the Inception-style regressor reaches MAE 13.42 years and R² 0.243. This does not justify an age gate or age input in the stroke model.

The fold-fitted age-adjustment baseline reinforces that decision. Raw gait features reached AUROC 0.973, gait plus age reached 0.968, and age alone reached 0.803. Age did not add discrimination to gait, while residualizing gait features against age reduced performance. The current interpretation is that age is a shortcut risk and a biological audit variable, not a required classifier input.

## What's still genuinely open

- The [[hsu-2018]] shank-leading vs. [[voisard-2025]]/[[felius-dataset]] lower-back-leading disagreement — different classification targets, never tested head-to-head on the same placements.
- The sample-entropy direction disagreement between [[voisard-2025]] and [[felius-dataset]] — reported as unresolved, not smoothed over.
- No study yet combines systematic multi-placement comparison with pocket-carried validation in one stroke cohort. See [[future-directions]].
- **Narrowed 2026-07-28**: [[rojek-2025]], found via a fresh literature search, is the first study found applying both classical (SVM, Random Forest, k-NN) and deep learning (CNN) classifiers to the identical task and population — CNN highest at 91.88%, SVM close behind at 89.91%. It doesn't fully close this question, since it never states which sensor stream produced its classifier inputs and doesn't report a full performance breakdown for its three classical models, but it is genuine, real progress on a gap this review previously described as entirely open. See [[classification-methods]].

## How to navigate from here

- Want the raw study-level data? Go to `studies/`.
- Want the dataset-level detail? Go to `datasets/`.
- Want the cross-cutting arguments? Everything above links to a `concepts/` page.
- Want prior-review context? Go to `reviews/`.
- Want the maintenance history of this wiki itself? See `log.md`.
