Load this file only during review or planning — do not load every session.

# Backlog

Remaining tasks, upcoming features, and known issues. Move items to `state.md` when in progress, delete when done.

---

## Phase 1 — Project Setup

- [x] Initialise git repo with `.gitignore`
- [x] Create `/backend/` with `requirements.txt` and `main.py`
- [x] Create `/frontend/` with Vite + React scaffold
- [x] Set up `.env` with Gemini API key
- [x] Move `docs/` into project root

---

## Phase 2 — Preprocessing

- [x] `chapter_splitter.py` — parse ALL CAPS headings, strip page markers, output `chapters.json` (book → chapter → text)
- [x] `ner_mentions.py` — run spaCy `en_core_web_sm` on each chapter, extract character mentions, output `characters.json` (character × book × chapter frequency)
- [x] `sentiment.py` — run VADER on each chapter, output `sentiment.json` (book → chapter → compound/pos/neg scores)
- [x] `chunker.py` — chunk text with LangChain RecursiveCharacterTextSplitter (~500 tokens, 50 overlap), embed with `sentence-transformers/all-MiniLM-L6-v2`, store in ChromaDB collection `hp_books`
- [x] Validate all outputs — spot check a few characters and chapters manually

---

## Phase 3 — Backend

- [x] `main.py` — FastAPI app with CORS enabled
- [x] `routers/story.py` — `/api/story/sentiment`, `/api/story/deaths`, `/api/story/wordcount`
- [x] `routers/characters.py` — `/api/characters/mentions`, `/api/characters/relationships`
- [x] `routers/chat.py` — `/api/chat` POST endpoint: accepts question + chart context, queries ChromaDB, calls Gemini, streams response
- [x] `.env` loading with `python-dotenv`
- [x] Basic error handling on all routes

---

## Phase 4 — Frontend

- [x] Scaffold React app with Vite
- [x] Set up Tailwind CSS
- [x] `/src/api/` module — typed fetch wrappers for all backend routes
- [x] Layout — two-panel: dashboard on left, chat sidebar on right
- [x] `StoryArc/` — sentiment line chart (x = chapter, y = compound score, coloured by book)
- [x] `StoryArc/` — death timeline (scatter or bar)
- [x] `StoryArc/` — word count bar chart per book
- [x] `CharacterIntel/` — character mention frequency line chart (filterable by character)
- [ ] `CharacterIntel/` — relationship graph — **BLOCKED**: see Technical Debt
- [ ] `CharacterIntel/` — allegiance shift timeline — **BLOCKED**: see Technical Debt
- [x] `ChatPanel/` — chat UI with message history
- [x] `ChatPanel/` — chart context serialisation: on each message, capture current chart type + visible data + active filters and include in request payload
- [x] Streaming response rendering in chat panel

---

## Phase 5 — Polish

- [x] Loading states on all charts
- [x] Error states on all charts and chat
- [x] Empty state for chat panel on first load
- [ ] Book/chapter filter that syncs across all charts
- [ ] Dark mode (optional)

---

## Technical Debt

- Dialogue attribution (who says what) is unresolved — current NER approach will find character names but not tag dialogue speakers. May need a custom heuristic or a separate model.
- **Relationship graph** — blocked on two things: (a) library decision between D3 and `react-force-graph` is unresolved; (b) `relationships.json` does not exist and needs a new preprocessing script to extract character co-occurrence or interaction data; `/api/characters/relationships` currently returns an empty list.
- **Allegiance shift timeline** — no data source; would require a preprocessing script designed from scratch. Moved here from Phase 4 as indefinitely deferred.
- Embedding model confirmed: `sentence-transformers/all-MiniLM-L6-v2`. Gemini Embedding API not used.
- CORS port was hardcoded to `3000` instead of `5173` (Vite default) — fixed in session 6, but Vite default port should be verified at setup in future projects.
