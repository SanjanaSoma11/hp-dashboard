# State

Current project state. Read this at the start of every session before doing anything.

---

## Current Phase

**Phase 6 complete — Relationship graph shipped**

**Last updated:** 2026-05-11

---

## What Was Just Completed

- **SentimentChart dynamic axes**: Y axis now uses a computed domain from actual compound values in the visible selection (±0.05 padding, rounded to 2dp) instead of the static [-1, 1]; X axis reindexes from 0 when books are filtered so the axis matches the visible chapter count; tooltip still shows correct book/chapter via preserved data fields; both axes animate via Recharts default transitions
- **Gemini alias resolution**: replaced the heuristic `build_canonical_map` in ner_mentions.py with a Gemini-produced alias map; alias_resolver.py added; 22 validated aliases produced; Harry (17,039 raw) now resolves to Harry Potter (17,862 combined); characters.json and relationships.json regenerated; all relationship graph edges now reference canonical full names
- Previous session: relationships.py written, RelationshipGraph.jsx built, COLORS utility extracted, sentiment chart book filter added

---

## What's Next

No active blockers. Remaining backlog items:

- Book/chapter filter syncing across all charts (Phase 5 polish)
- Allegiance shift timeline (indefinitely deferred — no data source)
- Dialogue attribution (indefinitely deferred)

---

## Pending Decisions

None.

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
| Session 7 | Alias resolution added to ner_mentions.py; relationships.py written; relationship graph frontend built with react-force-graph-2d; sentiment chart book filter added; COLORS utility extracted |
| Session 8 | SentimentChart axes fixed (dynamic Y domain, reindexed X per visible selection); heuristic alias resolution replaced with Gemini call via alias_resolver.py (22 aliases, Harry → Harry Potter confirmed); characters.json + relationships.json regenerated |
