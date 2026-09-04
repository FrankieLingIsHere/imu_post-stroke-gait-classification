---
type: staged
status: unresolved
reason: "full text blocked (MDPI 403 on both the article page and its htm variant, preprints.org 403 on the preprint version) — screening below is built from WebSearch snippets only, not a fetched primary source, so it does not meet this project's citation-verification bar and cannot be decided either way yet"
---

Pinheiro, C., Abreu, L., Figueiredo, J., Cruz, C., Cerqueira, J., & Santos, C. P. (2026). *Sensor-Based Classification of Post-Stroke Motor Impairment Using Fugl-Meyer Lower Extremity Scores*. *Sensors*, 26(14), 4458. https://www.mdpi.com/1424-8220/26/14/4458 (preprint version also found at preprints.org, also 403-blocked).

Surfaced via the 2026-07-28 search for new RQ3 evidence (query: "post-stroke gait classification wearable sensor machine learning new study 2026"). Full text could not be retrieved via any route attempted: MDPI article page (403), MDPI `/htm` variant (403), the preprints.org non-peer-reviewed preprint version (403), and a Semantic Scholar API lookup (429 rate-limited). Every fact below comes from WebSearch result summaries only and is explicitly **unverified against a primary source** — per this project's citation-verification discipline, none of it should be treated as confirmed or used in the manuscript without a real fetch first.

## What search snippets suggest (unverified)

- Combines the open-source "ARRA" dataset with data collected at Hospital of Braga: 32 post-stroke individuals, FMA-LE motor score 24±3.
- Best-performing feature set is described as "correlated sEMG features combined with age, paretic side, and body mass" plus noise-based data augmentation, reaching a validation Matthews Correlation Coefficient of 0.85. A decision tree classifier is mentioned; no deep learning method is mentioned in any snippet.
- One snippet describes the ARRA dataset's own spatiotemporal parameters as "derived from kinematic and ground reaction force data" — this phrasing, if accurate, would suggest the underlying motion-capture modality behind at least part of the feature set is optical/force-plate based rather than wearable-IMU based, which would raise an [[eligibility-criteria|EC1]] concern (non-wearable modality). This could not be confirmed against the actual methods section.

## Why this is staged rather than decided

Two separate open questions block a decision, and both require the actual full text: (1) whether any wearable IMU (accelerometer/gyroscope) component exists in this study's sensor inputs at all, given the snippets describe sEMG plus what sounds like optical-kinematic/force-plate spatiotemporal features rather than IMU-derived ones, and (2) the population size (32) and single-cohort, no-healthy-comparison design, which would place it on the IC4 pathway if it clears the modality question. Needs a resolved full-text fetch (try again later, or via institutional access) before either an Ingest or an exclusion is warranted.
