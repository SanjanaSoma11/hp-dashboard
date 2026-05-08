# Backlog

Remaining tasks, upcoming features, and known issues. Move items to `restart.md` when in progress, delete when done.

---

## Phase 1 — Project Setup

- [ ] Initialise git repo with `.gitignore`
- [ ] Create `/backend/` with `requirements.txt` and `main.py`
- [ ] Create `/frontend/` with Vite + React scaffold
- [ ] Set up `.env` with Gemini API key
- [ ] Move `docs/` into project root

---

## Phase 2 — Preprocessing

- [ ] `chapter_splitter.py` — parse ALL CAPS headings, strip page markers, output `chapters.json` (book → chapter → text)
- [ ] `ner_mentions.py` — run spaCy `en_core_web_sm` on each chapter, extract character mentions, output `characters.json` (character × book × chapter frequency)
- [ ] `sentiment.py` — run VADER on each chapter, output `sentiment.json` (book → chapter → compound/pos/neg scores)
- [ ] `chunker.py` — chunk text with LangChain RecursiveCharacterTextSplitter (~500 tokens, 50 overlap), embed with `sentence-transformers/all-MiniLM-L6-v2`, store in ChromaDB collection `hp_books`
- [ ] Validate all outputs — spot check a few characters and chapters manually

---

## Phase 3 — Backend

- [ ] `main.py` — FastAPI app with CORS enabled for `localhost:3000`
- [ ] `routers/story.py` — `/api/story/sentiment`, `/api/story/deaths`, `/api/story/wordcount`
- [ ] `routers/characters.py` — `/api/characters/mentions`, `/api/characters/relationships`
- [ ] `routers/chat.py` — `/api/chat` POST endpoint: accepts question + chart context, queries ChromaDB, calls Gemini, streams response
- [ ] `.env` loading with `python-dotenv`
- [ ] Basic error handling on all routes

---

## Phase 4 — Frontend

- [ ] Scaffold React app with Vite
- [ ] Set up Tailwind CSS
- [ ] `/src/api/` module — typed fetch wrappers for all backend routes
- [ ] Layout — two-panel: dashboard on left, chat sidebar on right
- [ ] `StoryArc/` — sentiment line chart (x = chapter, y = compound score, coloured by book)
- [ ] `StoryArc/` — death timeline (scatter or bar)
- [ ] `StoryArc/` — word count bar chart per book
- [ ] `CharacterIntel/` — character mention frequency line chart (filterable by character)
- [ ] `CharacterIntel/` — relationship graph (consider D3 force graph or `react-force-graph`)
- [ ] `CharacterIntel/` — allegiance shift timeline
- [ ] `ChatPanel/` — chat UI with message history
- [ ] `ChatPanel/` — chart context serialisation: on each message, capture current chart type + visible data + active filters and include in request payload
- [ ] Streaming response rendering in chat panel

---

## Phase 5 — Polish

- [ ] Loading states on all charts
- [ ] Error states on all charts and chat
- [ ] Empty state for chat panel on first load
- [ ] Book/chapter filter that syncs across all charts
- [ ] Dark mode (optional)

---

## Technical Debt

- Dialogue attribution (who says what) is unresolved — current NER approach will find character names but not tag dialogue speakers. May need a custom heuristic or a separate model.
- Relationship graph library choice not finalised — Recharts can't do graph layouts. Need D3 or `react-force-graph`.
- Embedding model not confirmed — `all-MiniLM-L6-v2` is a sensible default but Gemini's embedding API could be used instead for consistency.
