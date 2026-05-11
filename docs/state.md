# State

Current project state. Read this at the start of every session before doing anything.

---

## Current Phase

**Relationship Graph — pending design and library decision**

**Last updated:** 2026-05-10

---

## What Was Just Completed

- Phase 3 backend complete: FastAPI app with all routers (`story.py`, `characters.py`, `chat.py`) wired into `main.py`
- Phase 4 frontend complete: Tailwind CSS configured, `/src/api/` fetch wrappers, two-panel layout, all chart components built
- Phase 5 polish complete: loading states, error states, empty state for chat panel
- All three charts confirmed rendering: sentiment line chart, character mentions frequency chart, word count bar chart
- Chat panel streaming confirmed working end-to-end
- Three bugs fixed:
  - CORS port was hardcoded to `3000` instead of `5173` (Vite default)
  - `mention_count` field mismatch between backend response and frontend expectation
  - Stale uvicorn process blocking port on restart

---

## What's Next

Relationship graph — blocked on three things:

1. **Library decision**: D3 vs `react-force-graph` — unresolved; pick before writing any component code
2. **Preprocessing**: `relationships.json` does not exist; needs a new script to extract character co-occurrence or interaction data from `characters.json` / `chapters.json`
3. **Backend route**: `/api/characters/relationships` currently returns an empty list — needs data before it can be implemented

---

## Pending Decisions

- Relationship graph library: D3 vs `react-force-graph`

---

## Session Log

| Session | What was done |
|---|---|
| Session 1 | Project scoped, tech stack decided, architecture designed, all docs created |
| Session 2 | Phase 1 complete: .gitignore, backend/requirements.txt, backend/main.py, frontend Vite+React scaffold |
| Session 3 | Python 3.12 venv at backend/.venv; chapter_splitter.py, ner_mentions.py, sentiment.py written and validated; chapters.json, characters.json, sentiment.json produced |
| Session 4 | chunker.py written and validated; all preprocessing complete; Phase 2 done |
| Session 5 | Phase 3 backend complete (all routers); Phase 4 frontend complete (Tailwind, API module, layout, all chart components, chat panel) |
| Session 6 | Phase 5 polish complete; three bugs fixed (CORS port, mention_count field mismatch, stale uvicorn process); all charts and chat streaming confirmed working |
