# Public raw-IMU screening

Date: 2026-09-08. Scope: repository and file access screening, not a model-performance experiment.

Subsequent acquisition succeeded: see [actual TVS sample checks](../reports/TVS_SAMPLE_ACQUISITION_2026-09-08.md).
Healthy and PD laboratory MAT samples now exist locally and passed schema
inspection. The failed-transfer outcome below records the earlier attempt only.

## Correction: existing recommendations, limited new evidence

TVS and WearGait-PD were already documented before this screening:

- [Existing public-source review](../reports/DATA_SUFFICIENCY_AND_PUBLIC_SOURCE_REVIEW.html)
  already prioritizes TVS for clinical specificity; its source is
  `scripts/render_data_sufficiency_and_sources_html.py`, line 18.
- [September 1 recruitment decision](../reports/BINARY_DATA_READINESS_AND_PUBLIC_RECRUITMENT_2026-09-01.md)
  already recommends WearGait-PD, documents its sensor contract and access
  workflow, and excludes it from paired stroke validation.

The preceding response overstated progress by presenting these existing
recommendations as the screening outcome. The added evidence is limited to
endpoint checks, the HA ZIP inventory, a smart-belt signal prefix and failed
TVS sample-transfer attempts. No new compatible cohort was acquired, no TVS
signal schema was verified locally, and no model improvement was demonstrated.
Resume the unresolved acquisition/schema step; do not repeat source discovery
or the already documented specificity recommendation.

## Decision

Prioritize **Mobilise-D Technical Validation Study (TVS)** for a public lower-back
non-stroke specificity study. It was previously identified conceptually; this
screening advances it to actual archive inspection. Do not confuse it with the
processed Mobilise-D CVS release already downloaded locally.

No new independent, healthy-plus-stroke, lower-back raw-IMU cohort was verified
in this bounded search. This does not establish that none exists. Existing
Felius, Voisard and RevalExo data remain existing evidence, not new holdouts.
Author-request cohorts remain parked under the user's public-data-only decision.

## Screened routes

| Dataset / primary source | Access and signal evidence | Suitability / decision |
|---|---|---|
| [Mobilise-D TVS, v1.0.2](https://zenodo.org/records/15861907) | Anonymous API and HTTP byte-range access verified. Six actual cohort ZIP archives. Repository specifies raw McRoberts MM+ lower-back IMU, laboratory walking and free-living recordings, 108 released participants. HA archive central directory contains laboratory `data.mat`, `infoForAlgo.mat`, and `test_list.json`. | Highest-priority **specificity** candidate: healthy, PD, MS, proximal femoral fracture, COPD, CHF; no stroke. Verify sample signals, units, exclusions and cohort metadata before acceptance. |
| [WearGait-PD](https://www.synapse.org/Synapse:syn52540892/wiki/623752) | Repository API accessible. Access instructions explicitly require Synapse registration before file downloads. Schema documents 100 Hz, raw acceleration in m/s², gyroscope in rad/s, task annotations, plus separate gravity-removed acceleration fields. | Strong secondary specificity candidate; 100 PD + 85 controls. **Account required, not anonymous direct download.** No stroke. Confirm exact lumbar placement and use raw acceleration, not FreeAcc. |
| [Stroke case – Smart Belt Dataset](https://zenodo.org/records/10785201) | Two listed CSVs: 228.8 MB and approximately 1.4 GB. Anonymous byte-range download of first 8,192 bytes succeeded. Actual columns include `Belt,PA_ID,Millis,Ax,Ay,Az,Gx,Gy,Gz`; numeric sensor readings verified. Repository specifies 100 Hz, waist/left/right/middle hip sensors. | Hold: stroke only; no verified healthy cohort, walking labels, subject mapping, units or exact lower-back sensor mapping. `PA_ID` increments alongside time in the inspected prefix; do **not** interpret it as a participant identifier. Prefix is an incomplete file, not a usable cohort download. |
| [Stroke walking bracelet dataset](https://zenodo.org/records/10782580) | Repository lists a 30.7 MB accelerometer CSV with patient IDs and walking-task labels from 11 stroke participants. Sensor is on either wrist. File content not downloaded this pass. | Exclude from lower-back classifier input: wrong placement and no healthy group. |
| [Jeonju University IMU (JU-IMU)](https://github.com/youngminoh7/JU-IMU) | Official README downloaded. 29 non-disabled and 15 stroke participants; 45 accelerometer/gyroscope/magnetometer columns; Google Drive download links. Actual Drive payload access not tested. | Exclude for this task: upper-limb range-of-motion and daily-living activities, not the required walking protocol. Paired populations alone are insufficient. |
| [Subacute Stroke Gait biomechanics data](https://data.mendeley.com/datasets/szmfkhyjpd/1) | Repository describes IMU-derived gait reports, joint angles, EMG and gait-cycle summaries. Local API/page requests returned HTTP 403; browser search tool could read description but not a file inventory. | Unverified raw-data release. Cannot count as downloadable raw acceleration merely because IMUs were used. |
| [Biofeedback Stroke Stance Phase and Single Support Phase](https://data.mendeley.com/datasets/8f4mpm9w2z/1) | Repository describes sacrum/lower-limb sensors and gait-cycle/joint-angle outcomes; no raw file schema verified. | Hold outside accepted shortlist: original accelerometer/gyroscope time series not established. |
| [NTU stroke-gait papers](https://www.mdpi.com/1424-8220/23/15/6793) | Both published routes, `http://140.112.14.7/~sic/PaperMaterial/IMU_LPD_Data.zip` and `http://140.112.14.7/~sic/PaperMaterial/Dataset.zip`, returned HTTP 404 in this session. | Broken published download endpoints. Do not present as currently downloadable. Mirrors and sensor compatibility remain unverified. |
| [PhysioNet multimodal gait in young adults](https://physionet.org/content/multimodal-gait-dataset/1.0.0/) | Public file inventory and anonymous download instructions exist. Title and population identify young adults; references to stroke are not evidence of stroke participants. | Not a paired stroke cohort or clinical non-stroke specificity cohort. No bulk download. |

## TVS contract and remaining checks

The repository specifies comfortable, slow and fast straight walking, hallway
walking, turns and simulated daily activities. Tests 1–3 are calibration;
exclude them from gait analysis. Prefer the last trial where repeated trials
represent technical/performance retries. Do not treat free-living calibration
recordings as walking. Sensor-missing recordings are possible.

The published loader documentation describes 115 collected participants while
this release describes 108. Use version-pinned archive and participant metadata
for analysis counts, not a paper-level total. The release lists six ZIPs totaling
58,355,733,475 bytes. A separate participant workbook is described but is not
listed as a standalone file in the v1.0.2 API inventory; metadata completeness
must be resolved before subgroup claims.

The stated license is CC BY-NC-ND 4.0. The authors frame TVS as algorithm
validation rather than deriving clinical insights from its small disease groups.
Use a preregistered technical false-positive stress evaluation; do not claim
diagnostic validation or tune the frozen model against its test labels.

Before model inference, lock signal selection, units, sampling conversion,
walking-task selection, missingness handling, subject grouping and reporting.
Keep any format-inspection participants separate from an untouched evaluation
subset. No threshold, model weights or accuracy claims change in this screening.

## Reproducibility

Evidence is stored under `data/interim/public_imu_screen_2026-09-08/`:
Zenodo metadata, Synapse access/schema pages, archive inventories and an explicitly
partial smart-belt CSV prefix. These local evidence files are ignored by Git.
`fetch_tvs_samples.py` uses bounded HTTP ranges, validates range responses and
verifies uncompressed length and ZIP CRC before saving selected laboratory members.
It selects the smallest laboratory recording in each of HA and PD for schema
inspection, not a representative sample for outcome estimation.

Transfer outcome: the initial HA archive-tail request returned HTTP 206 and
yielded 181 ZIP members. The selected HA laboratory member is
`HA/4109/Laboratory/data.mat` (18,408,703 uncompressed bytes). Subsequent sample
retrieval did not complete; the first attempt was stopped after no progress,
and the alternate `/records/.../files/HA.zip` route timed out awaiting its
response. **No TVS MAT sample has been downloaded or parsed successfully.**
PD archive contents and raw sample units/rate remain to be checked. The
verified raw numeric sample in this session is the smart-belt prefix only.
TVS is an acquisition candidate, not an accepted or evaluated cohort.

Search families included stroke/raw IMU/lumbar/gait in Zenodo and Mendeley,
GitHub releases, institutional ZIP links, Synapse and PhysioNet. Known Kiel,
Brasiliano and Inui restrictions remain recorded in
[the preceding file trace](DOWNLOAD_FILE_TRACE_2026-09-08.md); they were not
reclassified as new public raw cohorts.
