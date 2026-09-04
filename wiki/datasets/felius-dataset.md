---
type: dataset
population: "Real stroke and healthy controls, same protocol, incl. a longitudinal subset"
sensors: "bilateral foot, lower back, ~100 Hz (inferred)"
role: primary
---

Felius et al. (2024)'s underlying signal data, independently re-mined as this review's **second real, paired stroke-and-healthy dataset**. Distinct from [[felius-2024]], which covers what the *published paper itself* reports (its own VAE feature-extraction results) — this page covers what *this review's own hands-on mining* of the same raw signal found.

## Sensor-configuration discrepancy (flagged 2026-07-29, resolved)

A `journal-critic` adversarial review flagged that this page's "bilateral foot, lower back" sensor list contradicts [[felius-2024]]'s own frontmatter ("2 IMUs: bilateral foot") and the manuscript's Table 3. Checked directly against the published paper's own Methods section via a fresh fetch: Felius et al. (2024) states explicitly, "Data were collected using two unsynchronized Inertial Measurement Units (IMUs) positioned on the left and right foot" — no lower-back sensor in the paper's own description. A separate fresh check of the Zenodo record's file-naming convention, however, references a lower-back-coded file location alongside both feet, consistent with this review's own notebook (`01_post_stroke_gait_baseline.ipynb`), which explicitly flags the lower-back channel as "inferred from the authors' own filter defaults, not stated directly in the repository" rather than confirmed documentation. The manuscript's Section 2.3 previously stated "three inertial units" as flat fact, understating that uncertainty — corrected to state the published paper's own two-foot-IMU description plus the review's own inferred third channel, hedged the same way the notebook itself already hedges it. Table 3 (about the published paper) and Table 5 (about this review's own re-mining, already saying "inferred") did not need changing.

## Participant-count reconciliation (added 2026-07-29, third journal-critic pass; figures below superseded 2026-08-01 by the S001P exclusion in "Key findings" above — 133/35 became 132/34)

A third journal-critic review flagged that the manuscript's "182 stroke participants" figure (49 Voisard + 133 Felius) did not visibly reconcile against Table 3's stated Felius total of 107, when read from the manuscript text alone. This was already disclosed here but not clearly enough in the manuscript itself. Fixed by adding an explicit reconciliation to Section 2.3 and Section 4.2.6, and by filling in Table 5's previously-empty Felius population cell with both figures side by side (133 stroke / 35 healthy actually re-mined vs. the published paper's 107 stroke / 37 healthy). Table 5's Access Link cell was also fixed from a non-functional search instruction to the real citable DOI, https://doi.org/10.5281/zenodo.11045239, and its sampling-rate cell corrected from "~100 Hz, inferred" to "104 Hz, per the Zenodo record's own description" — the record's own text states this directly ("sampled at 104 Hz"), confirmed via a fresh fetch, so this was never actually an inference.

## Data-loading pipeline gap (found and fixed 2026-07-29)

A second, independent `journal-critic` adversarial re-review caught that this review's own participant count (previously reported as 34 unique Felius stroke subjects) could not be reconciled with the 107 stroke participants Felius et al. (2024) itself reports (77 longitudinal + 30 test-retest). Checked directly against the raw downloaded data rather than assumed: `src/features/felius.py`'s `list_trials()` function read only the `Data_Stroke` folder (the 30-participant test-retest reliability subset, matching the 34-subject/64-trial count previously reported) and never the separate `Data_long` folder, which contains the 77-participant longitudinal cohort as its own distinct set of raw files. Fixed by adding `Data_long` to `FOLDER_LABELS` in `felius.py`. The corrected pipeline finds **133 unique stroke subjects across 320 trials** — more than the paper's own reported 107, a discrepancy between the public data release and the published demographics that is disclosed here rather than forced to match. Healthy participants are unaffected (35 unique subjects, `Data_Healthy` was already read correctly).

## Key findings (this review's own re-mining, corrected 2026-08-05 — S001P duplicate exclusion)

- **S001P duplicate found and excluded, round 19 (2026-08-01), not previously recorded on this page**: subject `S001P`'s files exist, byte-identical, in both the `Data_Healthy` and `Data_Stroke` folders of Felius's own public release (same trial_key, same feature values in each copy) — a genuine data-integrity issue in the dataset's own release, not this project's code. `felius.py`'s `list_trials()` now excludes any subject ID spanning more than one folder-derived label rather than guessing which folder is correct. This changed every Felius-derived number on this page, all now corrected below.
- **318 stroke trials from 132 unique subjects, 59 healthy trials from 34 unique subjects** (corrected from 320/133 and 61/35 pre-S001P-exclusion; confirmed directly against `felius.build_feature_table()`'s current output, 166 total unique participants = 132+34). No participant-level demographic or clinical data accompanies the public release, so the age/gender confound checks run on [[voisard-2025]] cannot be repeated here. **Verified directly, 2026-07-22**: this isn't just an absence, the original authors' own analysis code reads `Data/Characteristics/ontslagen.xlsx` ("ontslagen" = Dutch for "discharged"), proving a participant-characteristics file existed for their own analysis — publicly viewable at https://github.com/RichardFel/VAE/blob/V1.0.6/Functions/Progression.py. That file itself was never included in the public data release, https://doi.org/10.5281/zenodo.11045239.
- Felius has no public participant-level age metadata for either label. It can remain in the pooled primary gait model, but it cannot currently support age adjustment, an age classifier, or a complete age-input model without recovering the missing characteristics file or recruiting age-labeled participants. See [[age-and-stroke-gait]].
- Stride-frequency detection fails for 17.6% of Stroke trials vs. 0% of Healthy trials (round 19: was 17.5%, negligible shift from the S001P exclusion) — impaired gait is still less periodic than healthy gait, breaking the single-dominant-frequency assumption autocorrelation-based detection requires.
- Corroborates [[voisard-2025]]'s age-adjusted direction for mean stride time, stride-time CV, and lower-back RMS (rank-biserial r = -0.66, -0.80, 0.61 — round 19: was -0.63, -0.77, 0.59 pre-S001P-exclusion; direction and significance both hold, every effect size got slightly stronger once the duplicate was removed, consistent with its identical values sitting in both groups diluting the true group difference).
- Raw cadence effect (r = 0.66, round 19: was 0.63) could not be checked for an age confound — no demographic data available. This asymmetry (Voisard checkable, Felius not) is a specifically flagged limitation. Mean stride time and raw cadence are not independent corroborations here: Felius derives both from one shared autocorrelation frequency estimate, so they are the same measurement with the sign flipped.
- Sample entropy and Poincare SD1 disagree in **direction** with [[voisard-2025]] — a genuine, unresolved cross-dataset discrepancy, not smoothed over. Three explanations are on the table, none rulable in or out with the evidence available: different sensor hardware/mounting/protocol, the orientation-invariant magnitude-based computation used here rather than a calibrated axis, or a real clinical difference between the two stroke cohorts (severity, chronicity) that can't be tested given the missing characteristics file noted above. See `synthesis.md`.

## Links

See [[felius-2024]] for the published paper's own findings (unsupervised VAE feature extraction, no classification task). Paired against [[voisard-2025]] throughout [[discriminative-features]] and [[sensor-placement]].
## Raw-release and linkage audit (2026-09-01)

The official data and processing release is available through [Zenodo DOI 10.5281/zenodo.11044903](https://doi.org/10.5281/zenodo.11044903) and the authors' [Reliability-of-Gait repository](https://github.com/RichardFel/Reliability-of-Gait). The repository confirms the intended three-file contract: left foot, right foot, and low back; each file contains timestamp, three accelerometer axes, and three gyroscope axes.

The local raw files follow this structure. The remaining obstacle is not missing data but identifier linkage: the processed window table uses a shortened trial key that does not directly equal the raw filename. Reconstruction must therefore use the official folder-aware trial listing and exact subject/triplet matching. No signed-axis tensor has been admitted yet.

## Released-code fidelity audit (2026-09-02)

The executed `19_felius_source_faithful_segmentation_audit.ipynb` compared the
project's periodic-window rule with the authors' released
`Reliability-of-Gait` procedure. The released code trims acquisition edges,
uses acceleration *and* gyroscope magnitude to find the two-minute walking
interval, then processes synchronized lower-back and foot 6-DoF signals. The
project magnitude-only materialisation does not reproduce that contract.

The current periodic rule retained 98.2% of healthy candidate windows but only
78.4% of stroke candidate windows. This is a label-asymmetric selection effect
and makes earlier direct-pooling evidence incomplete. A literal source-
procedure reproduction did not solve it: common synchronized walking intervals
were found for 53/59 healthy trials and 258/318 stroke trials, so it excluded
an even larger fraction of irregular stroke trials. The next representation
must preserve source-faithful walking semantics without treating the original
feature-extraction algorithm's failure mode as a reason to remove impaired gait.

## Lower-back gyroscope representation pilot (2026-09-02)

`25_lower_back_accel_gyro_source_transport_pilot.ipynb` used the existing
source-aligned Felius/Voisard 6-DoF windows to compare lower-back acceleration
magnitude with lower-back acceleration-plus-gyroscope magnitude. It is a
lower-back-first, source-transport test rather than a replacement for the
three-channel prototype. Adding gyroscope magnitude improved Felius-to-Voisard
mean AUROC from 0.7357 to 0.8234 and healthy specificity from 0.3519 to 0.4537.
The reverse Voisard-to-Felius direction did not improve (AUROC 0.7825 to
0.7829; balanced accuracy 0.6978 to 0.6210). This asymmetric result is direct
evidence that gyroscope dynamics contain useful gait information, but also that
axis/filter/task alignment remains unresolved. A source-faithful Sint 6-DoF
adapter is required before a three-source lower-back model is evaluated.
