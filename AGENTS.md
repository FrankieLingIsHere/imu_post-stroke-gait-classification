# Project collaboration

## Git publication review

Present the proposed new and modified files for user review before pushing.
Do not push further changes until the user has reviewed that scope and explicitly
approved publication. Keep local dependencies and generated research artifacts
out of source commits, and preserve unrelated working-tree changes.
After completing work, update the wiki and local weekly progress page in the same
batch. Keep those page changes local for the user's final review before pushing.

## Dataset access claims

Supervisor-aligned direction (2026-09-09): prioritize clinically parameterized
healthy-to-stroke-like gait synthesis as the grant deliverable. Healthy-only
generation and gait classification are supporting experiments, not completion of
that objective. RevalExo is historical evidence only: do not use it for further
selection, tuning or admission decisions. Previously inspected development data
cannot be relabeled as a pristine final test. See the supervisor-feedback section
of `docs/classification/WEEKLY_PROGRESS_2026-09-07.md` before new experiments.

Never describe a dataset as directly downloadable merely because its paper,
registry, code, feature tables or supplementary material is public. Before making
that claim, verify the actual file endpoint and distinguish raw signals from
derived features, available population groups, sensor placement, and access terms.
State precisely what was downloaded versus only listed or inferred. A healthy-only
release does not establish public stroke recordings. Author-request access is not
a public download. If no compatible raw download is verified, say so immediately;
do not repeatedly offer irrelevant downloads or imply permission is the obstacle.

Treat the user as a research collaborator who wants candid technical judgment.
Challenge proposals when evidence, statistical validity, or implementation quality
argues against them. Explain the reason and propose a concrete alternative.
Do not agree merely to encourage, and do not assume the user is always wrong.
Separate verified results, assumptions, and untested suggestions.

For classification continuation, read `docs/STROKE_CLASSIFICATION_INTEGRATION_PLAN.md`
and `docs/CONTACT_RECRUITMENT_SHORTLIST_2026-09-08.md`. Prioritize reproducible
contracts and independent cohort evidence over further architecture searches.
Contact leads are not accepted datasets. Sending outreach requires explicit user
authorization. Preserve existing unrelated changes.

Before proposing or rerunning classification audits, read
`docs/CLASSIFICATION_EVIDENCE_MAP.md`. Check existing reports, prediction files,
model identity and completed decisions first. Name the specific unanswered gap.
Do not treat historical "next experiment" sections as current instructions when
later notebooks already completed or rejected those experiments.

Before dataset searches, search existing docs, reports (including HTML), wiki,
scripts and local acquisition artifacts by dataset name, alias and DOI. Read
the prior acquisition decision. Report only the new evidence relative to that
decision; an existing candidate or recommendation is not a new screening result.
Resume its concrete unresolved step rather than reissuing the shortlist.

For classification work, keep the Obsidian vault in sync in the same change
batch: update `wiki/concepts/classification-project-status.md`, affected concept
or dataset pages, `wiki/index.md`, and append a dated entry to `wiki/log.md`.
Read `.claude/skills/wiki-sync/SKILL.md` and `wiki/CLAUDE.md` before vault edits.
Replace stale current-status instructions rather than stacking contradictory
updates. Preserve historical reports and append-only log entries. Always state
metadata, raw-signal, preprocessing and evaluation completion separately.

## Classification workspace organization

Keep the folder structure clean. Use `docs/classification/README.md` as the current
work entry point and `models/prototypes/README.md` as the executable prototype
registry. Put prototype examples in each versioned package's `examples/` folder.
Keep experiment outputs in versioned `data/processed/` directories. Prefer updating
current working documents over creating new dated planning reports. Preserve
historical evidence and existing imports/links when reorganizing files. Never
duplicate or redownload datasets merely to start another experiment.

## Local Python environment

Existing environments are `C:/Users/frank/.venv` and
`C:/Users/frank/.venv-cu130` (Python 3.11). Prefer the latter for PyTorch work,
using `C:/Users/frank/.venv-cu130/Scripts/python.exe` explicitly. These are
outside the workspace sandbox, so access failures can require escalation;
do not interpret a sandbox-hidden interpreter as an absent installation.

## Experiment notebooks

User-confirmed convention: experiment orchestration, analysis and saved outputs
belong in notebooks. Keep reusable loaders, model/feature code and tests as Python
modules. Prefer updating a themed notebook over adding a new one-off runner.
Save tables/plots and provenance in the notebook so results can be read without
rerunning. Label artifact replays explicitly; never present reloaded historical
results as a newly executed training run. Migrate old runners with dependency
checks before removing them; preserve historical source hashes and experiment
contracts. Publication still requires user review.
