---
type: concept
---

A study qualifies for inclusion by satisfying **at least one** of three inclusion pathways, with no conflict against either exclusion criterion — not the standard "all criteria must hold" PRISMA model.

## The pathways

- **IC1** — direct comparison or classification task between stroke participants and a comparison group, using a data-driven classification method. 9 studies: [[mannini-2016]], [[hsu-2018]], [[wang-2021]], [[hsu-2021]], [[lee-2018]], [[brasiliano-2026]], [[inui-2026]], [[shin-2022]], [[lee-2025]].
- **IC4** — stroke participants only, with a graded outcome (severity, function, or risk), using a data-driven classification method. 7 studies: [[pohl-2022]], [[obrien-2022]], [[sun-2025]], [[abdollahi-2024]], [[wu-2025]], [[obrien-2024]], [[rojek-2025]].
- **IC5** — wearable IMU-based gait methodology relevant to the three [[research-questions]] (feature extraction, sensor-placement comparison, or detection-method evaluation), **explicitly including studies conducted entirely in a healthy population**, without stroke participants or a data-driven classification method. 3 studies: [[avvenuti-2018]], [[ensink-2023]], [[felius-2024]].

## Two further requirements, not pathways

- **IC2** — a wearable IMU data-collection component, with body placement coded as a comparison variable wherever the source study reports it explicitly. **Amended 2026-07-29** (see note below): originally worded as an unconditional "placement reported explicitly" requirement, which [[rojek-2025]] does not strictly satisfy.
- **IC3** — peer-reviewed journal article, conference paper, or book chapter, written in English.

## The exclusions

- **EC1** — non-wearable sensing modality (video, optical mocap, pressure plates, electrostatic field sensing), no wearable IMU component.
- **EC2** — full text not available or inaccessible.

## IC2 amendment, 2026-07-29 (Rojek et al. 2025's placement gap)

A `journal-critic` adversarial review flagged that Section 3.3's original wording, "eligibility requires wearable inertial measurement unit data, with sensor placement reported explicitly," is a blanket rule stated before the three pathways are even introduced, and that [[rojek-2025]] fails it as written: its own full text (independently re-verified fresh, not just re-read from the earlier ingest) confirms a wearable IMU component was used but never states IMU count or body placement, since data collection combined IMU, pressure-sensor, and video streams without specifying which one produced each reported feature. This is a real gap in the source paper, not a stale or mistaken claim on this review's part, unlike the same review's [[hsu-2021]] finding.

Given the choice between excluding Rojek, amending the rule, or leaving it as a silently-inconsistent exception, the rule was amended: IC2 now requires a confirmed wearable IMU component, with placement coded as a comparison variable only wherever the source study states it explicitly, rather than requiring explicit placement unconditionally. Rojek stays included on IC4, with its placement-provenance gap disclosed on its own page and in the manuscript's Section 6 rather than glossed over. The manuscript's Section 3.3 and Table 1 were updated to match.

## History worth remembering

This IC5 pathway didn't exist from the start. It was added specifically because [[avvenuti-2018]] — a genuinely relevant trunk-vs-pocket placement study with no stroke population — was initially, wrongly excluded. The fix generalized into a real pathway rather than a one-off exception, which is why [[ensink-2023]] and [[felius-2024]] could later be added the same way.

## Links

Determines which of the 19 pages in `studies/` exist at all, all 19 now formally reflected in the manuscript's Table 3 as of 2026-07-28, when [[obrien-2024]] and [[rojek-2025]] were added via a second supplementary screening pass (Section 6). [[quality-assessment]]'s four criteria apply only to IC1/IC4 studies — IC5 studies are exempt by design.
