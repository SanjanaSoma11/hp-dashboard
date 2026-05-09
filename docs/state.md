# State

Current project state. Read this at the start of every session before doing anything.

---

## Current Phase

**Phase 2 — Preprocessing** (in progress)

**Last updated:** 2026-05-07

---

## What Was Just Completed

- `backend/.venv` created with Python 3.12 (`/opt/homebrew/bin/python3.12`); all requirements installed; `en_core_web_sm` downloaded
- `chapter_splitter.py` written and executed — `backend/data/chapters.json` produced (198 chapters across 7 books)
- `ner_mentions.py` written and validated — possessive normalisation confirmed, blocklist expanded; `characters.json` produced (8,931 records, 7 books)
- `sentiment.py` written and validated — 198 records; per-book averages align with series arc (Book 1 brightest at 0.6354, Book 7 darkest at -0.2945)

### Chapter counts (from last run)

| Book | Detected | Expected | Status |
|---|---|---|---|
| 1 | 17 | 17 | ✅ |
| 2 | 18 | 18 | ✅ — apostrophe fix confirmed DOBBY'S REWARD |
| 3 | 22 | 22 | ✅ |
| 4 | 35 | 37 | ⚠ 2 short — OCR artifact, accepted |
| 5 | 39 | 38 | ⚠ 1 extra — possible false-positive heading, accepted |
| 6 | 30 | 30 | ✅ |
| 7 | 37 | 37 | ✅ |

---

## What's Next

1. `chunker.py` — LangChain RecursiveCharacterTextSplitter (~500 tokens, 50 overlap), embed with `sentence-transformers/all-MiniLM-L6-v2`, store in ChromaDB collection `hp_books`
2. Validate all preprocessing outputs manually before moving to Phase 3

---

## Pending Decisions

- Embedding model: `sentence-transformers/all-MiniLM-L6-v2` vs Gemini Embedding API
- Relationship graph library: D3 vs `react-force-graph`

---

## Session Log

| Session | What was done |
|---|---|
| Session 1 | Project scoped, tech stack decided, architecture designed, all docs created |
| Session 2 | Phase 1 complete: .gitignore, backend/requirements.txt, backend/main.py, frontend Vite+React scaffold |
| Session 3 | Python 3.12 venv at backend/.venv; chapter_splitter.py, ner_mentions.py, sentiment.py written and validated; chapters.json, characters.json, sentiment.json produced |
