# Provider schema intake

Current role contract: [evaluation-role decision](RECRUITMENT_ROLE_DECISION_2026-09-08.md).
Set `evaluation_profile` explicitly. The bilateral-foot/all-group requirements
described below apply to `full_comparison`, not every single-channel evaluation.

Implemented 2026-09-08. This replaces the informal screening step with a
repeatable evidence checklist. It does not verify whether provider statements
are true, calculate statistical power, inspect raw archives, or certify clinical
validity. A reviewer must examine the referenced sample/dictionary first.

1. Copy [provider_schema.json](templates/provider_schema.json) to local
   `data/interim/` with a candidate-specific filename.
2. Record native sensor values and clinically identified participant counts.
3. Set each evidence status to `confirmed`, `unknown`, or `not_met`. Only
   `confirmed` with a traceable document/section reference clears a requirement.
   Put missingness, restrictions and protocol deviations in the supplied notes.
4. Run:

```powershell
& C:/Users/frank/.venv-cu130/Scripts/python.exe scripts/check_recruitment_schema.py data/interim/provider_candidate.json --output data/processed/provider_candidate_gate_v1.json
```

Exit 0 means schema-ready for metadata intake; exit 2 means hold with explicit
blockers; invalid input exits 1. Existing decisions are protected from overwrite.
Output includes the exact input SHA-256. Keep provider documents and participant
information in ignored local data directories.

The gate retains the current plan's bilateral-foot requirement, even though the
primary classifier needs only lower back. It also requires non-stroke comparison
groups for the planned specificity endpoint. A lower-back-only or paired-only
cohort may still be scientifically useful, but requires a separately documented
role/protocol decision rather than quietly weakening this gate.

A different positive sampling rate is allowed at schema screening. It does not
prove that resampling or the adapter meets the frozen 100-Hz contract. Native
units must be explicit; unsupported units remain on hold for adapter review.

The precision-plan evidence must describe endpoint-specific sample-size targets
and adequacy of available groups. Positive counts alone do not establish power.
Clinical metadata evidence should cover age, sex, stroke severity/chronicity,
side, walking speed, aid, footwear and task conditions, with missingness reasons.
The overlap evidence must address existing development, tuning, calibration and
inspected cohorts, including aliases and related releases. This screening does
not replace identifier-level overlap validation on the received manifest.

After schema readiness, data-use terms and the frozen evaluation protocol still
control acquisition and access. The first archive operation must validate
metadata/schema before extraction or inference. This tool downloads nothing and
never opens a final test.

## Verification and immediate outcome

Six gate tests passed (15 repository tests total). They cover complete synthetic
intake, every absent requirement, assertions without evidence, known sources,
invalid rates/populations, and malformed nested fields. The actual CLI ran on
the blank template and correctly returned hold. No real provider was accepted.

Use [the prepared requests](PROVIDER_SCHEMA_REQUEST_DRAFTS.md) to obtain the
missing evidence. These drafts have not been sent. Further generic classifier
audits will not supply the absent provider data.
