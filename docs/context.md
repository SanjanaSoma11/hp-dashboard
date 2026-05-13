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
| Frontend | React, Recharts · `localhost:5173` |
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
│   │   ├── run_all.py          ← orchestrator; run this instead of scripts individually
│   │   ├── chapter_splitter.py
│   │   ├── alias_resolver.py   ← Gemini alias map; run before ner_mentions.py pass 2
│   │   ├── ner_mentions.py
│   │   ├── relationships.py
│   │   ├── sentiment.py
│   │   └── chunker.py
│   ├── data/
│   │   ├── chapters.json
│   │   ├── sentiment.json
│   │   ├── aliases.json                    ← Gemini alias map (gitignored)
│   │   ├── aliases_raw.json                ← Gemini response cache (gitignored)
│   │   ├── character_aliases.manual.json   ← hand-curated alias map; safe to commit (name mappings only, no book text)
│   │   ├── characters.json
│   │   ├── relationships.json
│   │   └── events.json                     ← manually curated events (deaths only); no book text; safe to commit
│   ├── chroma_db/          ← ChromaDB persisted store
│   ├── routers/
│   │   ├── story.py
│   │   ├── characters.py
│   │   └── chat.py
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   ├── config.js       ← API_BASE (reads VITE_API_BASE env var, defaults to localhost:8000)
│   │   │   ├── story.js
│   │   │   ├── characters.js
│   │   │   └── chat.js
│   │   ├── context/
│   │   │   └── FilterContext.jsx   ← selectedBooks: number[]; FilterProvider wraps App; useFilter() hook
│   │   ├── components/
│   │   │   ├── Card.jsx            ← reusable card wrapper (title, subtitle props); bg-neutral-900
│   │   │   ├── FilterBar.jsx       ← global book filter bar (Books 1–7 toggles + All/Clear)
│   │   │   ├── StoryArc/
│   │   │   ├── CharacterIntel/
│   │   │   └── ChatPanel/
│   │   │       ├── ChatPanel.jsx   ← chat UI; suggested chips; filter indicator; copy/clear buttons; source card streaming
│   │   │       └── SourceCards.jsx ← source pill cards rendered below each AI answer
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
| NER entity normalisation | Possessives stripped before counting; structural phrase fragments blocked via blocklist; two-tier alias resolution: manual dictionary + Gemini-based alias resolution via alias_resolver.py | alias_resolver.py sends top-200 entities to Gemini, gets back alias→canonical map validated against input list, writes aliases.json; ner_mentions.py loads both character_aliases.manual.json (37 manual aliases) and aliases.json (Gemini aliases), merges them with manual taking priority for any overlap, applies merged map in Pass 2; 52 aliases applied in pass 2; manual aliases resolve single-token names missing from Gemini (Ron, Lupin, McGonagall, Hagrid, Neville, Ginny, Cedric, Sirius, Moody, Tonks, all Weasley first names, Voldemort aliases); ambiguous surnames (Weasley alone, Potter alone) intentionally excluded from both maps |
| Relationship graph library | react-force-graph-2d | Force-directed layout, canvas-based, simple API, maintained; D3 rejected as too low-level for this scope |
| Relationship edge construction | Chapter co-occurrence, top-30 characters only | Co-occurrence is computable from existing characters.json; interaction-based approach would need dialogue attribution (unresolved) |
| Relationship graph centrality | networkx degree, weighted_degree, betweenness, pagerank per node | Computed in relationships.py and stored in relationships.json nodes; used to size nodes in the frontend (pagerank → radius 3–10px); nodes also carry a books field listing which books each character appears in |
| Global filter state | React Context (FilterContext) — selectedBooks: number[] | Wraps the entire app from App.jsx; all filtering is client-side via useMemo in each component; no backend filter params needed since all data is loaded in full; book filter only — character and chapter range filters deferred |
| Sentiment | VADER | Lightweight, no model download, works well on narrative text |
| Chunking | LangChain | Standard RAG tooling; chunk metadata includes book_title, chapter_title, word_count, characters_mentioned (top-30 characters, comma-separated string) |
| Embedding model | `sentence-transformers/all-MiniLM-L6-v2` | Confirmed over Gemini Embedding API — fully local, no API cost, runs on MPS |
| AI model | Gemini 3.1 Flash Lite via Vertex AI (google-genai SDK, ADC auth) | Switched from API key auth — uses GCP project hpdashboard, requires gcloud auth application-default login on local machine |
| Chat stream protocol | `__SOURCES__:<json>\n` header line before AI tokens | Backend emits deduplicated `[{book_title, chapter_title}]` from ChromaDB metadatas as first line; frontend buffers until `\n`, parses header, then streams remaining bytes as message text; frontend renders `SourceCards` from parsed sources |
| Deployment | None — localhost only | Book text is copyrighted, keeping everything local |
| Book text in git | No — gitignored | Copyright compliance |
| Preprocessing data in git | No — gitignored | Derived from copyrighted text |

---

## Hard Constraints

- Book text is **never committed to git** — added to `.gitignore`
- All preprocessing outputs (JSON/CSV/ChromaDB) are also **gitignored**
- The only external network call is to the **Gemini API**
- No deployment — runs entirely on `localhost`
- Gemini access uses Vertex AI ADC auth (`gcloud auth application-default login`) — no API key; GCP project `hpdashboard`; optional overrides `GCP_PROJECT` and `GCP_LOCATION` in `/backend/.env`
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

- Preprocessing scripts run **once** via `backend/preprocessing/run_all.py`, outputs saved to `/backend/data/`
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
- Gemini: Vertex AI ADC auth; `gcloud auth application-default login` required; GCP project defaults to `hpdashboard`

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
| All books | Alias resolution — two-tier approach, ambiguous surnames unresolved by design | Gemini alias map (aliases.json) resolved 29 aliases including core names. Manual dictionary (character_aliases.manual.json) added 37 more, covering single-token names Gemini couldn't resolve (Ron, Lupin, McGonagall, Hagrid, Neville, Ginny, Cedric, Sirius, Moody, Tonks, all Weasley first names) plus Voldemort aliases. 52 of 55 merged aliases were applied in pass 2. "Weasley" (bare surname, 1360 mentions) and "Potter" (bare surname, 640 mentions) intentionally excluded from both maps — they are genuinely ambiguous across multiple characters. |

---

## Open Questions

- How to handle dialogue attribution (who says what) — spaCy alone won't solve this cleanly
