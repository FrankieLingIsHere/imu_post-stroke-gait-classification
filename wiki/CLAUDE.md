# Schema — MR-ICT Review Paper Wiki

This vault implements the pattern described in [[llm-wiki]] (Karpathy's LLM Wiki pattern), instantiated for one project: the systematic review *"Autonomous Wearable-based Post-Stroke Gait Classifications: A Systematic Review"* (retitled 2026-07-23, formerly *"Automatic Post-Stroke Gait Classification with Wearables"*). Read `llm-wiki.md` once for the philosophy; this file is the concrete schema for this specific vault, plus a Skill Map adapted from Nick Milo's "AIOS" video (*How I Use Obsidian + Claude Cowork to Run My Life*). When any of these disagree, this file wins — it's the domain-specific instantiation.

## Relationship to Claude Cowork (and why this file exists)

Nick Milo's video runs on **Claude Cowork**: a scheduled, always-on agent pulling from Gmail, Calendar, and ClickUp to generate an unattended 6am daily brief. **This project uses Claude Code instead**: an interactive, session-based CLI with no autonomous background execution by default. The two products solve different problems — Cowork automates a personal life; Claude Code executes precise, reviewable work inside a project directory.

The adaptation that matters: everything Cowork does *automatically on a timer*, Claude Code does *on request, inside a session, invoked by name*. The **Skill Map** below is the direct analog of Cowork's daily-brief system — a fixed menu of named workflows, each with a clear trigger and a clear procedure, so a new session can execute one reliably instead of improvising. If persistent automation is ever wanted (e.g. a nightly Sync + Lint pass), it can be layered on top later using Claude Code's own `/loop` or `schedule` skill — that is an explicit, opt-in decision the user makes, not something this schema sets up unilaterally.

**Every skill below except Query now also exists as a real, invokable Claude Code Skill** in `../.claude/skills/` (`wiki-ingest`, `wiki-sync`, `wiki-search-enrich`, `wiki-draft-assist`, `wiki-lint`, plus `journal-format-check` for WIREs submission-formatting compliance), so they can be triggered by name or automatically when a matching request comes in, not just followed as prose instructions. Read `../CLAUDE.md` (the project root, which auto-loads every session, unlike this file) for how those fit together with this project's global agents and skills in `~/.claude/`.

## Session start protocol

Paste this (or something like it) at the start of any session that will work on this wiki:

> Read `wiki/CLAUDE.md` and `wiki/index.md`. Confirm what you've read, then await instruction.

This is the direct analog of Nick Milo's "SSK" startup prompt — it exists to defeat model amnesia between sessions. A session that skips this and starts editing pages cold risks duplicating a page that already exists, breaking a link convention, or missing a fact that's already been resolved elsewhere in the vault.

## Three layers

**Raw sources** (immutable, outside this vault, in the parent project folder):
- `../docs/Review_Paper_Draft.docx` — the manuscript itself. Source of truth for all included-study facts, quality-assessment findings, and discussion synthesis.
- `../docs/Sources_Search_Log_and_Datasets.docx` — the search log and dataset access registry. Source of truth for screening/exclusion history.
- `../notebooks/01_post_stroke_gait_baseline.ipynb` — the hands-on data-mining notebook. Source of truth for every hands-on-mining number (age stats, cluster purity, SNR rankings, placement comparisons).
- `../docs/PRISMA_2020_flow_diagram_updated_SRs_v2.docx` — earlier PRISMA diagram draft, superseded by the one embedded in the manuscript.

Never edit these from inside the wiki. If a wiki page and a raw source disagree, the raw source is right and the wiki page needs fixing — flag it, don't silently pick one.

**The wiki** (this directory, LLM-maintained):
- `studies/` — one page per included study in Table 3 (currently 17). Filename: `lastname-year.md` (e.g. `mannini-2016.md`; `hsu-2018.md` and `hsu-2021.md` for the two distinct Hsu et al. studies). Template: `templates/study-template.md`.
- `datasets/` — one page per hands-on-mined dataset (currently 7: Voisard, Felius, GaitMotion, DUO-GAIT, OxWalk, MAREA, Camargo). Template: `templates/dataset-template.md`.
- `reviews/` — one page per prior review discussed in Section 2 (currently 5: Jiao, da Silva, Prisco, Boukhennoufa, Jourdan). Template: `templates/review-template.md`.
- `concepts/` — topic/synthesis pages that cut across studies: research questions, eligibility criteria, discriminative features, sensor placement, classification methods, quality assessment, the trunk-vs-pocket deployment tension, future directions. Template: `templates/concept-template.md`.
- `synthesis.md` — the top-level narrative page. Mirrors the manuscript's Discussion/Conclusion but as a living, linkable document rather than fixed prose.
- `index.md` — content-oriented catalog of every page in the wiki, grouped by folder, one line each. Read this first, every session.
- `log.md` — chronological, append-only record of every skill run (ingest, sync, search, draft-assist, query, lint).
- `numbers-registry.md` — every load-bearing manuscript number that is restated in more than one location, with every location listed, so a fix to one instance can be mechanically checked against all its siblings instead of relying on an ad hoc grep. Update it in the same edit batch as any change to one of its listed numbers.
- `raw/` — **not** a copy of the raw sources above. A staging inbox for candidate material the [[#3. Source Search & Enrichment|Source Search & Enrichment]] skill finds but hasn't yet been screened/filed. See `raw/README.md`.
- `templates/` — starter frontmatter + section skeleton for each page type, so new pages stay structurally consistent without re-deriving the convention from scratch each time.

**You (the human)** curate what gets ingested and ask the questions. The LLM does the filing, cross-referencing, and bookkeeping.

## Page conventions

Every page opens with YAML frontmatter. Minimum fields by type — see `templates/` for copy-paste starters:

**Study pages** (`studies/*.md`):
```yaml
---
type: study
year: 2016
pathway: IC1          # IC1, IC4, or IC5 — which eligibility pathway admitted it
population: "15 stroke vs 10 healthy elderly"
method: "HMM + SVM"
placement: "shank, waist"
---
```

**Dataset pages** (`datasets/*.md`):
```yaml
---
type: dataset
population: "260 participants: 73 HS, 143 neuro, 44 ortho"
sensors: "head, lower back, bilateral foot, 100 Hz"
role: primary   # primary (real paired stroke/healthy), simulated, or healthy-only-reference
---
```

**Concept and review pages**:
```yaml
---
type: concept   # or "review"
---
```

Body structure for study/dataset pages: a one-paragraph summary first (what it is, why it's here), then a `## Key findings` section, then a `## Links` section only if there are relational notes that don't fit naturally as inline `[[wikilinks]]` elsewhere in the page (most links should just be inline, in prose, where the connection is actually being made — an appendix link list is a fallback, not the default).

## Linking rules

- Link liberally, inline, at first mention per page: a study page discussing lower-back placement links `[[sensor-placement]]`; a concept page synthesizing across studies links every study it draws on.
- A link that doesn't resolve yet (page not created) is fine — Obsidian shows it as an unresolved link, which is itself a to-do signal, not an error. Don't invent a stub page just to make a link resolve; create it for real when there's real content, or leave it unresolved.
- No page should be an orphan (zero inbound links) once the initial build is done. If you write a page and nothing will naturally link to it, add it to `index.md` at minimum and reconsider whether it should be folded into an existing page instead.

## Numbers discipline (carried over from the manuscript's own standing rules)

- Never state a number, citation, or finding in a wiki page that isn't traceable to a raw source or to something already verified in the manuscript. This wiki is a restructuring of already-verified facts, not a place to introduce new unverified claims.
- If the manuscript itself has a known open question or unresolved discrepancy (e.g. the sample-entropy direction disagreement between Voisard and Felius), represent it as unresolved in the wiki too — don't quietly resolve it during restructuring.
- No semicolons, no parenthetical `(Section X)` cross-references — those were manuscript-prose constraints and don't apply here, since wikilinks replace that function entirely. Do keep the same "never fabricate, always verify" discipline.
- Any web search performed for [[#3. Source Search & Enrichment|Source Search & Enrichment]] must be verified against a real fetched source (PMC, publisher page, or equivalent) before a fact from it lands in any page, matching the standard the manuscript itself was held to all session.
- **Not carried over, but flagged here so it's found from this file too**: paragraph spacing and table design (borders, header shading, row banding, width, font size) drifted inconsistently across the manuscript over many sessions, since none of it is defined by the document's own Word styles, only ad-hoc per-paragraph and per-row direct formatting. Normalized document-wide 2026-07-23. The canonical values and the reason they must be set explicitly on any newly inserted paragraph or table row, rather than assumed inherited, live in the project-root `../CLAUDE.md`'s "Standing manuscript rules" section, not here, since this is a `.docx` production concern rather than a wiki-content concern. Read it before inserting a paragraph or table row directly into `Review_Paper_Draft.docx`.

## Skill Map

Six named workflows. Each has a trigger (when to run it) and a procedure (what to actually do). Invoke by name — "run Sync" or "do a Lint pass" — so the request is unambiguous. This is the vault's analog of Cowork's fixed daily-brief menu, adapted to run on request instead of on a timer.

### 1. Ingest
**Trigger**: a genuinely new study, dataset, or finding needs filing — the source already exists and is confirmed relevant, it just isn't in the wiki yet.
1. Read the raw source for the new fact.
2. Create or update the relevant `studies/` or `datasets/` page (use the matching template).
3. Update every `concepts/` page the new fact touches (a placement finding touches `concepts/sensor-placement.md` at minimum; check `concepts/discriminative-features.md` and `synthesis.md` too).
4. Update `index.md`.
5. Append an entry to `log.md`: `## [YYYY-MM-DD] ingest | <what>`.

### 2. Sync
**Trigger**: the raw sources changed — the manuscript was edited, the notebook was re-run, a new PRISMA count landed — and the wiki needs to catch up. This is what "keep observing the changes and apply changes" means in practice: on request, not continuously, since Claude Code has no background file-watcher running by default.
1. Compare the raw sources' current state against what `log.md`'s most recent `sync` or `ingest` entry assumed. A fast way in: check the manuscript's included-study count, table numbering, and any section the user says they just edited.
2. For each actual change found, treat it like an Ingest (steps 2–4 above) targeted at just the affected pages — don't re-walk the whole vault for a one-paragraph edit.
3. If a wiki page's claim turns out to be stale (the manuscript moved on and the page didn't), fix the page — don't leave two versions of the same fact disagreeing.
4. Append an entry to `log.md`: `## [YYYY-MM-DD] sync | <what changed, what was updated>`.

### 3. Source Search & Enrichment
**Trigger**: asked to look for new relevant literature, or a Lint pass flags a topic with thin coverage.
1. Use WebSearch/WebFetch to find candidate sources — real papers, not summaries of papers. Ground every claim in an actually-fetched source, per the numbers-discipline rule above.
2. Screen each candidate against `concepts/eligibility-criteria.md`'s IC1/IC4/IC5 and EC1/EC2 rules.
3. A candidate that's ambiguous or only partially verifiable (e.g. only a preprint mirror, not the final published text) goes into `raw/` as a staged, unresolved item — see `raw/README.md` — rather than being silently included or silently dropped.
4. A candidate that clearly qualifies gets a full Ingest (skill 1).
5. A candidate that clearly doesn't qualify gets logged as excluded, with the specific IC/EC reason, in the same `log.md` entry — don't just discard it silently, since "we already checked this and it doesn't qualify" is itself useful information for the next session.
6. Append an entry to `log.md`: `## [YYYY-MM-DD] search | <query, N candidates found, N included, N excluded, N staged>`.

### 4. Draft Assist
**Trigger**: asked to write or revise part of the actual manuscript (`../docs/Review_Paper_Draft.docx`) or another project deliverable, using the wiki as the knowledge source rather than re-deriving everything from scratch.
1. Read `index.md`, then the specific `concepts/`, `studies/`, or `datasets/` pages relevant to the section being drafted — this is faster and more consistent than re-reading the whole manuscript to remember what's already been established.
2. Draft or revise using what those pages already say. If the wiki and the manuscript disagree on a detail, that's a Sync gap — fix it via skill 2 before drafting, not by picking whichever version is convenient.
3. Apply this project's standing prose rules when writing manuscript text: no semicolons, no parenthetical `(Section X)` cross-references, short sentences with explicit connectors rather than long comma-spliced ones, and thematic synthesis rather than sequential "Author A did X, Author B did Y" summary where the section calls for it.
4. If the draft session surfaces a new synthesis, comparison, or connection that isn't yet in the wiki, file it back as a page update (per Ingest) rather than letting it live only in the drafted text.

### 5. Query
**Trigger**: a question about the project that the wiki should be able to answer directly.
1. Read `index.md` first to find candidate pages — don't grep the whole vault blind.
2. Read the candidate pages, follow links as needed.
3. Answer with citations to the specific wiki pages (and, through them, the underlying raw source).
4. If the answer produced something worth keeping (a comparison, a synthesis), offer to file it back as a new or updated page rather than letting it live only in chat.

### 6. Lint
**Trigger**: run periodically, or whenever the wiki feels like it might have drifted from the manuscript.
1. Check every page in `studies/`, `datasets/`, `reviews/`, `concepts/` is listed in `index.md`.
2. Check for orphan pages (no inbound links) via Obsidian's graph view or a grep for the page's own filename across the vault.
3. Check for contradictions: does any concept page state a number that a study/dataset page states differently?
4. Check for gaps: is there a study or dataset in `../docs/Review_Paper_Draft.docx`'s Table 3/5 that has no corresponding wiki page yet?
5. Check `raw/` for staged items that have been sitting unresolved for a while — surface them rather than letting them silently age out.
6. Log the lint pass in `log.md`.

## Model selection (adapted from the video's guidance)

Claude Code lets you switch models mid-session (`/model`). As a rough default for this vault: routine Ingest/Sync work (filing a known fact into a page) doesn't need the strongest model. Source Search & Enrichment, Draft Assist, and Lint benefit from a stronger model, since they require judgment calls (does this candidate really meet IC5? does this draft stay consistent with five other pages at once?) rather than mechanical filing. When delegating any of these to a background `Agent`, its `model` parameter can be set independently of the main session's model.

## Current state (as of the initial build)

17 included studies, 7 hands-on-mined datasets, 5 prior reviews, and the concept layer were built in one pass from the already-verified content of `../Review_Paper_Draft.docx` as it stood after this session's edits (17 included studies, Table 4 quality assessment applied, PRISMA diagram regenerated). The Skill Map, templates, and `raw/` staging area were added in a second pass, adapting Nick Milo's Obsidian + Claude Cowork "AIOS" video to Claude Code's session-based execution model. See `log.md` for the exact record of both passes.
