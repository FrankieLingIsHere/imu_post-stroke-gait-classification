# Presentation source

This directory contains two independent Slidev presentations:

- `slides.md` — established three-channel benchmark and clinical-readiness evidence.
- `experiments-2026-08-27-to-present.md` — experiments and decisions from 27 August 2026 onward.

```powershell
npm install
npm run dev
npm run dev:experiments
```

Build both decks with `npm run build:all`. Export them separately with `npm run export` and `npm run export:experiments`.

Generated dependencies and build output are excluded from version control. `package-lock.json` is retained to make the JavaScript environment reproducible. Claims and numerical results in both decks must be traceable to an executed notebook or a report in `../reports/`.
