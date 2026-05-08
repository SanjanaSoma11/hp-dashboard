# Architecture

## Overview

A local-only Harry Potter analytics dashboard combining two views — Story Arc and Character Intelligence — with a chart-aware AI Q&A panel powered by the Gemini API. All book text stays on-device. The only outbound call is to Gemini for Q&A completions.

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

## Component Breakdown

### Preprocessing (`/backend/preprocessing/`)
Runs once. Outputs are saved and never need to re-run during development.

- `chapter_splitter.py` — detects ALL CAPS chapter headings in raw `.txt` files, splits into per-chapter segments across all 7 books
- `ner_mentions.py` — runs spaCy NER to extract character mentions per chapter, outputs character × chapter frequency matrix
- `sentiment.py` — runs VADER on each chapter, outputs sentiment score (compound, positive, negative) per chapter per book
- `chunker.py` — splits text into ~500-token overlapping chunks using LangChain, embeds with sentence-transformers, stores in ChromaDB

### Backend (`/backend/`)
FastAPI app with three route groups:

- `/api/story` — serves story arc data (sentiment timeline, death timeline, word count per chapter)
- `/api/characters` — serves character data (mention counts, relationships, allegiance)
- `/api/chat` — receives user question + current chart context, retrieves relevant chunks from ChromaDB, calls Gemini API, streams response

### Frontend (`/frontend/`)
Two-panel React app:

- **Analytics dashboard** — Story Arc view (sentiment/timeline charts) + Character Intelligence view (mention charts, relationship graph). Built with Recharts.
- **Chat Q&A panel** — Sidebar chat interface. On every message, the frontend serialises the currently visible chart's data as JSON and injects it into the request payload as chart context.

### Chart-aware Q&A
When the user sends a message in the chat panel:
1. Frontend sends: `{ question, chart_context: { type, data, filters } }`
2. Backend retrieves top-k chunks from ChromaDB relevant to the question
3. Backend constructs a prompt: system context + chart context JSON + retrieved chunks + user question
4. Gemini API returns a completion, backend streams it back to the frontend

---

## Directory Structure

```
hp-dashboard/
├── backend/
│   ├── preprocessing/
│   │   ├── chapter_splitter.py
│   │   ├── ner_mentions.py
│   │   ├── sentiment.py
│   │   └── chunker.py
│   ├── data/
│   │   ├── chapters.json
│   │   ├── sentiment.json
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
    ├── architecture.md
    ├── claude.md
    ├── memory.md
    ├── backlog.md
    ├── restart.md
    └── agents.md
```

---

## Key Constraints

- Book text is **never committed to git** — added to `.gitignore`
- All preprocessing outputs (JSON/CSV/ChromaDB) are also **gitignored**
- The only external network call in the entire system is to the **Gemini API**
- No deployment — runs entirely on `localhost`
