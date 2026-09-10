# TVS raw-IMU acquisition: completed sample check

Two laboratory recordings were downloaded from the version-pinned Mobilise-D
TVS release (Zenodo 15861907), using resumable byte ranges rather than downloading
the 58.36 GB collection. All six selected files passed ZIP CRC and length checks;
SHA-256 hashes are saved in the local manifest.

| Schema-development sample | MAT bytes | Trials | Lower-back samples | Result |
|---|---:|---:|---:|---|
| Healthy: `HA/4109/Laboratory/data.mat` | 18,408,703 | 13 | 28,371 | All 13 trials passed |
| Parkinson's: `PD/4020/Laboratory/data.mat` | 31,207,433 | 12 | 39,566 | All 12 trials passed |

Verified in both files: `SU.LowerBack.Acc` and `Gyr` are matching N-by-3 numeric
arrays, declared rates are 100 Hz, values are finite, and per-trial timestamps
are finite and strictly increasing. Counts above include calibration and other
tasks; they are **not** counts of eligible walking observations. The official
mobgap loader converts native Acc from g to m/s²; this project's magnitude
model expects g, so that conversion must not be applied twice.

This completes the previously blocked download-and-parse step. It does not
establish model accuracy, fix false positives, or supply a stroke cohort.
These two participants were selected by smallest laboratory file size and are
reserved for schema development. Do not call them an untouched test cohort.

## Reproduce

```powershell
& C:/Users/frank/.venv-cu130/Scripts/python.exe scripts/acquire_tvs_schema_samples.py
& C:/Users/frank/.venv-cu130/Scripts/python.exe scripts/inspect_tvs_schema_samples.py
```

Local artifacts: `data/interim/public_imu_screen_2026-09-08/HA_sample/`,
`PD_sample/`, `sample_manifest.json`, `tvs_schema_results.json`, and
`unit_evidence.json`. The downloader reuses its range cache and verifies CRCs
after decompression. The inspector verifies sample SHA-256 hashes before parsing.
No classifier inference or retraining was performed.

## Existing-download and storage check

A recursive hidden/ignored-file-inclusive search of `C:/Users/frank` covered
Downloads, Documents, OneDrive, project archives and caches. No older file paths
matching TVS/WearGait names, cohort ZIP names, release IDs or TVS MAT filenames
were found. This is a filename-based search, not proof against renamed or nested
archives. The reported access-denied directory was `AppData/Local/Temp/WinSAT`.
Only C: was mounted. Details are in `local_download_inventory.json`.

Existing logical file sizes explain substantial retained project data: archived
raw cohorts 86.845 GB, NONAN 39.807 GB, RevalExo 19.988 GB, and Mobilise-D CVS
4.874 GB. These are current file totals, not measurements of a historical change
in free space. No files were deleted. CVS is processed outcome data and does not
replace these TVS raw laboratory recordings.

## Next unresolved implementation

Map reference walking intervals and quality exclusions to the raw lower-back
samples, then verify the fixed five-second preprocessing on these development
samples. Resolve the release's participant metadata before defining the untouched
specificity subset. Do not restart dataset discovery or report sample acquisition
as model-performance improvement.
