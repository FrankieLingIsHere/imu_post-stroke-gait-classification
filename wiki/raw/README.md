# raw/ — staging inbox, not a source-of-truth folder

This folder is **not** where the project's real raw sources live — those are the manuscript, the search log, and the notebook, all one level up in the parent project folder (see `../CLAUDE.md`'s "Three layers" section). Don't put copies of those here.

This folder exists for one purpose: **candidates the [[CLAUDE#3. Source Search & Enrichment|Source Search & Enrichment]] skill finds but can't yet fully resolve.** Concretely, that means:

- A paper that looks relevant but where only a preprint or an abstract could be verified, not the final published full text (see the manuscript's own handling of Sadeghsalehi 2026 for the precedent — excluded on verification-tier grounds, not content grounds, and logged as such rather than silently dropped).
- A candidate where eligibility is genuinely ambiguous and needs a second look before a real study page gets created for it.
- Any fetched abstract, citation, or note that should inform a future decision but isn't yet confirmed enough to become a real `studies/` page.

## Convention

One markdown file per staged candidate, named `lastname-year-staged.md`, with at minimum:

```yaml
---
type: staged
status: unresolved       # unresolved, or a note on why it's stuck
reason: ""                # what's blocking resolution — access, ambiguous fit, etc.
---
```

followed by whatever was actually found (citation, abstract text, source URL).

## Lifecycle

A staged item should not sit here indefinitely. The Lint skill checks this folder specifically and should surface anything staged for a while without resolution. Every staged item eventually becomes one of two things: a real page in `studies/` or `datasets/` (delete the staged file, it's done its job), or a logged exclusion in `log.md` (delete the staged file, the reason is preserved in the log).

This folder should normally be near-empty. A growing `raw/` is a signal the Source Search & Enrichment skill is finding more than it's resolving.
