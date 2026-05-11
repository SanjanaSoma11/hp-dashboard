# Context

## Project Identity

- **Name:** HP Dashboard
- **Type:** Personal fun project, non-commercial, not deployed
- **Developer:** Solo, local machine only
- **Purpose:** Harry Potter analytics + AI Q&A for personal use

---

## Stack

| Layer | Technology |
|---|---|
| Preprocessing | Python, spaCy, VADER, LangChain, regex |
| Backend | FastAPI · `localhost:8000` |
| Vector store | ChromaDB · local |
| Processed data | JSON / CSV files |
| Frontend | React, Recharts · `localhost:3000` |
| AI Q&A | Gemini 2.0 Flash (free tier) |

---

## Data Flow

```
Book text (7 .txt files)
        │
        ▼
┌─────────────────────────────────────────────────┐
│            Preprocessing pipeline               │
│  Chapter split │ NER/mentions │ Sentiment │ Chunks │
└─────────────────────────────────────────────────┘
        │                          │
        ▼                          ▼
  Processed data            Vector store
  (JSON / CSV)               (ChromaDB)
        │                          │
        └──────────┬───────────────┘
                   ▼
           FastAPI backend ◄──► Gemini API
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
Analytics dashboard      Chat Q&A panel
(Story Arc +             (chart context
 Character Intel)         injection)
```

---

## Directory Structure

```
hp-dashboard/
├── backend/
│   ├── preprocessing/
│   │   ├── chapter_splitter.py
│   │   ├── alias_resolver.py   ← Gemini alias map; run before ner_mentions.py
│   │   ├── ner_mentions.py
│   │   ├── relationships.py
│   │   ├── sentiment.py
│   │   └── chunker.py
│   ├── data/
│   │   ├── chapters.json
│   │   ├── sentiment.json
│   │   ├── aliases.json        ← Gemini alias map (gitignored)
│   │   ├── aliases_raw.json    ← Gemini response cache (gitignored)
│   │   ├── characters.json
│   │   └── relationships.json
│   ├── chroma_db/          ← ChromaDB persisted store
│   ├── routers/
│   │   ├── story.py
│   │   ├── characters.py
│   │   └── chat.py
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── StoryArc/
│   │   │   ├── CharacterIntel/
│   │   │   └── ChatPanel/
│   │   ├── App.jsx
│   │   └── main.jsx
│   └── package.json
├── books/                  ← gitignored, local only
│   ├── Book1.txt
│   └── ...
└── docs/
    ├── context.md
    ├── state.md
    ├── backlog.md
    └── agents.md
```

---

## Key Decisions

| Decision | Choice | Reason |
|---|---|---|
| Scope | Story Arc + Character Intelligence dashboards + Chat Q&A | Best combination of coherent data and interesting interactivity |
| Frontend | React + Recharts | Standard, well-documented, good charting library |
| Backend | FastAPI (Python) | Fits Python-heavy preprocessing stack |
| Vector store | ChromaDB | Fully local, no external service needed |
| NER | spaCy | Best Python NER library for named entity extraction |
| NER entity normalisation | Possessives stripped before counting; structural phrase fragments blocked via blocklist; Gemini-based alias resolution via alias_resolver.py | alias_resolver.py sends top-200 entities to Gemini in one call, gets back a JSON alias→canonical map, validates every canonical value against the input list (prevents hallucination), writes aliases.json; ner_mentions.py loads aliases.json at startup and applies it in Pass 2; 22 validated aliases resolved including Harry→Harry Potter, Dumbledore→Albus Dumbledore, Hermione→Hermione Granger, Malfoy→Draco Malfoy; ambiguous surnames (Weasley, Ron) correctly omitted from map by Gemini |
| Relationship graph library | react-force-graph-2d | Force-directed layout, canvas-based, simple API, maintained; D3 rejected as too low-level for this scope |
| Relationship edge construction | Chapter co-occurrence, top-30 characters only | Co-occurrence is computable from existing characters.json; interaction-based approach would need dialogue attribution (unresolved) |
| Sentiment | VADER | Lightweight, no model download, works well on narrative text |
| Chunking | LangChain | Standard RAG tooling |
| Embedding model | `sentence-transformers/all-MiniLM-L6-v2` | Confirmed over Gemini Embedding API — fully local, no API cost, runs on MPS |
| AI model | Gemini 3.1 Flash Lite via Vertex AI (google-genai SDK, ADC auth) | Switched from API key auth — uses GCP project hpdashboard, requires gcloud auth application-default login on local machine |
| Deployment | None — localhost only | Book text is copyrighted, keeping everything local |
| Book text in git | No — gitignored | Copyright compliance |
| Preprocessing data in git | No — gitignored | Derived from copyrighted text |

---

## Hard Constraints

- Book text is **never committed to git** — added to `.gitignore`
- All preprocessing outputs (JSON/CSV/ChromaDB) are also **gitignored**
- The only external network call is to the **Gemini API**
- No deployment — runs entirely on `localhost`
- Gemini API key lives in `/backend/.env` as `GEMINI_API_KEY` — never hardcoded
- Do not suggest adding auth, user accounts, or sessions
- Do not add dependencies without a clear reason
- Do not use `print()` for logging in FastAPI — use Python `logging`

---

## Working Principles

- **Don't over-engineer.** This is a fun personal project, not production software. Prefer simple, readable solutions over clever abstractions.
- **Explain tradeoffs honestly.** If there is a better approach, say so even if it means changing a prior decision.
- **Push back on bad ideas.** Don't validate weak decisions to be agreeable.
- **Stay local-first.** All solutions should work entirely on localhost.

---

## Code Style

### Python
- Python 3.11+
- Type hints on all function signatures
- Docstrings on all public functions (one line is fine for simple ones)
- No unnecessary abstraction — flat is better than nested
- Use `pathlib.Path` over `os.path`
- Prefer f-strings
- Dependencies go in `requirements.txt`, pinned versions

### React / JavaScript
- Functional components only, no class components
- `useState` and `useEffect` for state management — no Redux, no Zustand unless complexity demands it
- Recharts for all charts
- Tailwind CSS for styling
- API calls go in a `/src/api/` module, not inline in components
- No `any` types if using TypeScript

---

## Architecture Rules

- Preprocessing scripts run **once**, outputs are saved to `/backend/data/`
- FastAPI routes are **read-only** — they serve pre-computed data, they do not re-run analysis
- The `/api/chat` route is the only route that calls Gemini
- Chart context passed to Gemini must be **serialised JSON**, not raw rendered HTML
- ChromaDB collection name: `hp_books`

---

## Environment

- Machine: MacBook Air M4, 16GB RAM, macOS
- Python environment: venv at `/backend/.venv` — activate with `source backend/.venv/bin/activate`
- Node: via nvm
- Books location: `/books/` (gitignored)
- Gemini API key: stored in `/backend/.env` as `GEMINI_API_KEY`

---

## Dataset

- Source: Kaggle (`rupanshukapoor/harry-potter-books`)
- Format: 7 plain `.txt` files, one per book
- Chapter detection: ALL CAPS lines (e.g. `THE BOY WHO LIVED`)
- Page markers present: `Page | N Harry Potter and the... - J.K. Rowling` — strip during preprocessing
- Dialogue: not tagged by speaker — needs NLP attribution
- License note: Kaggle dataset listed CC0, but uploader did not have rights to relicense — handle as copyrighted

---

## Known Data Quality Issues

| Book | Issue | Detail | Decision |
|---|---|---|---|
| Book 4 (Goblet of Fire) | 35 chapters detected vs 37 expected (2 short) | One or more chapter headings lost in OCR — text is present but headings are missing, causing the splitter to merge those chapters into the previous one | Accepted as OCR ceiling, not a code bug. Do not attempt to fix in `chapter_splitter.py`. |
| Book 5 | 39 chapters detected vs 38 expected (1 extra) | Possible false-positive ALL CAPS heading in source text | Accepted as OCR artifact. |
| All books | spaCy PERSON false positives | "the Order of" and possessive forms (e.g. "Harry's") were surfacing as separate entities. Fixed via normalise() and blocklist in ner_mentions.py. "Harry" vs "Harry Potter" left fragmented intentionally — alias resolution deferred to relationship graph phase. | — |
| All books | VADER compound saturation | VADER compound score saturated at ±0.9999 for long chapter texts due to sigmoid accumulation on full chapter strings. Fixed in session 6: `sentiment.py` now scores at sentence level via `nltk.sent_tokenize` and averages compound/pos/neg/neu per chapter. Compound range is now -0.2157 to +0.1340 with 0/198 chapters saturated. | Resolved |
| All books | Alias resolution — Gemini approach, ambiguous surnames unresolved by design | Replaced the heuristic frequency-inversion guard with a Gemini call (alias_resolver.py). Gemini correctly resolved Harry→Harry Potter, Dumbledore→Albus Dumbledore, Hermione→Hermione Granger, Malfoy→Draco Malfoy, and 18 others. Gemini correctly omitted ambiguous surnames (Weasley, Ron→Ron Weasley was discarded since "Ron Weasley" is not in top-200 entities) — these remain as unresolved nodes in the relationship graph. "Potter" (640 mentions, separate from "Harry Potter") is also unresolved — valid because "Potter" as a bare surname refers to Harry, James, and Lily in different contexts. Remaining limitation: single-token names that lack a matching full form in top-200 cannot be resolved (Ron, Lupin, McGonagall). |

---

## Open Questions

- How to handle dialogue attribution (who says what) — spaCy alone won't solve this cleanly
