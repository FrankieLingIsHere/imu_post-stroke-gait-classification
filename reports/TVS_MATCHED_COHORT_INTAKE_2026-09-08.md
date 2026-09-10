# TVS matched-task intake checkpoint

Subsequent execution: the [locked pilot](TVS_LOCKED_PILOT_2026-09-08.md) acquired
four additional raw files and completed frozen scoring. Six raw participants
are now local; 34 remain unacquired. This report retains the earlier metadata
intake results. Use the pilot report for current raw-data and evaluation counts.


## Latest result: metadata intake completed

Replaying a previously successful uncached 30-byte ZIP-header request returned
HTTP 206 with both urllib and Requests. Replaying the exact previously failing
metadata range also returned HTTP 206. The resumed intake then completed:
**40/40 participants' metadata CRC-verified, zero pending transfers**. Earlier
504 errors below are historical, not the current acquisition state. The precise
network/gateway cause is not established; the observations support intermittent
availability rather than a persistent client incompatibility.

After excluding the two schema-development participants, metadata candidates
with the required sensor/reference availability and no task annotation are:

| Task | Healthy | Parkinson's |
|---|---:|---:|
| Comfortable straight walk (Test5) | 19 | 19 |
| Slow straight walk (Test6) | 19 | 19 |
| Fast straight walk (Test7) | 19 | 18 |
| Hallway (Test10) | 18 | 16 |

These are metadata candidates, not accepted five-second walking records. No
additional raw participant signals were downloaded and no larger-cohort model
evaluation was performed. Next: fix the common-task sampling/quality protocol,
then acquire selected laboratory members and check reference-bout durations.
The previous successful raw transfer used the same API content endpoints,
1 MiB range requests, disk cache and ZIP CRC checks; no alternative installation
or undisclosed dataset source was involved.

## Downloader repair

The acquisition path now uses `src/data/http_ranges.py`: persistent Requests
sessions, at most two active connections across nested workers, a 15-second
connection timeout and 45-second socket-inactivity timeout. There is no total
download deadline while data continue arriving. Transfers remain bounded to
1 MiB ranges; partial bytes are flushed to `.part` files and resumed from their
saved offset on retry or a subsequent invocation. Completed chunks retain the
existing cache keys, so the earlier downloads are reused.

Transient connection/HTTP failures receive three attempts with exponential
backoff; Retry-After is honored (delays above 60 seconds stop for a later resume).
Range/length, encoding and archive-validator mismatches fail closed. Servers
that ignore Range and return HTTP 200 are rejected before reading the archive
body. Completed ranges use SHA-256 sidecars and atomic publication; extracted
members still require ZIP CRC/length verification.

Four real local HTTP-server tests pass: interrupted-body resumption, resumption
in a later invocation, rejecting ignored Range, and detecting cache corruption.
Six existing TVS adapter/intake tests also pass. `requests` was already declared
in requirements.txt and has now been installed in the active CUDA venv.

The repaired transport was exercised on the pending metadata batch. These are
approximately 1–2 KB requests, so their failures cannot be attributed solely to
large-file transfer time. Current per-request errors are preserved in
`lab_metadata/intake_status.json`; unfinished transfers remain pending.

Live retry result: all four attempted metadata members returned **HTTP 504
Gateway Time-out** after the bounded retries. No new member completed; 38 remain
pending. This is a returned upstream/gateway error, not merely the old client's
15-second read timeout. Existing TVS range-cache reuse was also verified without
a network request. Increasing a local timeout cannot repair an HTTP 504 response.

Implemented `scripts/screen_tvs_lab_metadata.py` to inspect the laboratory
metadata for all 20 healthy and 20 Parkinson's participants listed in the two
verified archive inventories. It downloads only `test_list.json` and
`infoForAlgo.mat`, validates ZIP CRC/length, records SHA-256, and resumes from
local metadata. It reuses the two existing schema samples without downloads.

Per participant/timepoint/task it records the last trial, availability of the
SU lower-back sensor and Stereophoto reference, device type, walking-aid status
and task annotations. Last-trial metadata failures never trigger fallback to an
earlier trial. Availability does not establish a five-second usable bout; that
still requires the raw/reference parser after selection.

## Executed result and blocker

- Archive inventory: 40 laboratory participants (20 HA, 20 PD).
- Metadata successfully verified locally: two existing development participants.
- Pending transfers: 38; they are not clinical exclusions.
- Independent matched subset selected: **none**. Selection is explicitly not ready.
- Additional participant signals downloaded in this step: **none**.
- Six TVS tests pass, including corrupt-cache rejection, offline cache reuse and
  preventing fallback to a successful earlier trial after a failed final trial.

Zenodo requests timed out before a response, including its small record API,
archive byte ranges, alternate file routes and a separate curl request. GitHub
API access succeeded. A four-request metadata batch failed to complete; repeated
attempts were stopped. The resumable intake stops after a batch has no successful
transfers and writes pending statuses rather than selecting whichever subjects
happen to download first. No credentials or user action have been shown necessary.

The already-open PD development participant's metadata documents a rollator;
the HA development participant has no walking aid. This is an additional reason
not to interpret their previous smoke-test outputs as a controlled disease
comparison. Neither enters the independent-subset candidate counts.

## Resume without repeating discovery or downloading whole archives

```powershell
& C:/Users/frank/.venv-cu130/Scripts/python.exe scripts/screen_tvs_lab_metadata.py
```

Offline inspection (returns a pending status until all metadata are available):

```powershell
& C:/Users/frank/.venv-cu130/Scripts/python.exe scripts/screen_tvs_lab_metadata.py --offline
```

Local state: `data/interim/public_imu_screen_2026-09-08/lab_metadata/` contains
per-subject screens, `screening.json` and `intake_status.json`. Full demographic
and clinical quality metadata remain separate acceptance requirements. Do not
equate task matching with age/severity matching or verified clinical eligibility.
