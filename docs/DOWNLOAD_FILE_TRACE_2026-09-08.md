# Direct downloadable-file trace

## User download constraint confirmed

The user requested paired healthy/stroke data with matching sensors, rather than
the offered healthy-only Kiel archives. Do not start those large downloads for
this task. Local directories already contain Felius, Voisard, Sint and RevalExo,
and their processed development/external tensors are present. This presence check
does not certify every source archive is complete. No new matching paired archive
was established by the follow-up search, so no large download was started.

This pass inspected API file manifests, downloaded small files and opened their
contents. No full participant signal archive was acquired and no model was run.
Local evidence: `data/interim/download_trace_2026-09-08/`.

| Route | Actual files checked | Finding for the frozen model |
|---|---|---|
| Brasiliano supplementary material | Supplements 2 and 4 downloaded as genuine binary XLS. Supplement 2 has RUN 1–10 analysis sheets; supplement 4 contains gait-feature group statistics. Original endpoints for 1, 3 and 5 returned HTML instead of XLS. | Verified files are not raw lower-back recordings. Do not infer raw access from supplementary download links. |
| Inui uneven-gait GitHub | Recursive Git tree, README and 25,111-byte `sample.csv` downloaded. Tree contains README, requirements, example CSV and notebook. CSV columns are RMS, harmonic ratio, entropy, recurrence and Lyapunov features. | Downloadable feature example, not 500-sample acceleration windows. README's positional class assumption is not an independently verified clinical label manifest. |
| Kiel Figshare 20238006 | API lists seven RAR archives (about 15.25 GB total) and `demographics_scores_extern.xlsx` (37,690 bytes). Workbook downloaded and XML inspected: 21 participant rows in `Mobility_Dataset_Healthy`. | Public healthy data exist. The descriptor states remaining participants require author contact and an agreement. Not a new public paired stroke cohort. Archive payloads were not downloaded or validated. |

## Direct endpoints

- [Kiel API file manifest](https://api.figshare.com/v2/articles/20238006)
- [Kiel demographics workbook](https://ndownloader.figshare.com/files/37208827)
- [Kiel first raw archive, 1–3, approximately 2.67 GB](https://ndownloader.figshare.com/files/36191226)
- [Kiel descriptor documenting restricted remaining cohorts](https://jahrbib.sulb.uni-saarland.de/bitstream/20.500.11880/34147/1/data-07-00136.pdf)
- [Inui repository](https://github.com/Yasuhiro-Inui/stroke-vs-healthy-uneven-gait-ML)
- [Inui directly downloadable feature sample](https://raw.githubusercontent.com/Yasuhiro-Inui/stroke-vs-healthy-uneven-gait-ML/main/stroke-vs-healthy--uneven-gait-ML/sample.csv)
- [Brasiliano supplementary file 2](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41598-026-43666-7/MediaObjects/41598_2026_43666_MOESM2_ESM.xls)
- [Brasiliano supplementary file 4](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41598-026-43666-7/MediaObjects/41598_2026_43666_MOESM4_ESM.xls)

## Corrections and limits

The older local Kiel audit covers ten healthy records. It must not be generalized
to all downloadable Kiel data: this separate official record lists 21 healthy
participants. Conversely, its 167-person description must not be interpreted as
167 publicly downloadable participants. The apparent neurological-download lead
was ruled out by the workbook and explicit access statement.

Queries also checked author-name DataCite records and searched Zenodo/Figshare/
Mendeley routes. These returned unrelated namesakes or already-known/nonmatching
datasets; the DataCite name query alone was not an exhaustive author search.
No new compatible public paired raw release was established in this bounded pass.
That is not proof that none exists anywhere.

No user action is needed for the public files verified here. Provider involvement
is needed only if pursuing the unavailable raw Brasiliano recordings or Kiel's
restricted clinical participants. Do not download healthy archives expecting
them to contain the missing stroke group.
