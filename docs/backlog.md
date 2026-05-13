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
- [x] `routers/chat.py` — `/api/chat` POST endpoint: accepts question + chart context + optional history, queries ChromaDB, calls Gemini, streams response; chunk metadata included in prompt for citations; system prompt hardened; true async streaming via queue bridge
- [x] `services/analytics.py` — analytics tool layer: get_top_characters, get_character_mentions, get_sentiment_extremes, get_relationships; keyword classifier in chat.py injects structured data for quantitative questions
- [x] `.env` loading with `python-dotenv`
- [x] Basic error handling on all routes

---

## Phase 4 — Frontend

- [x] Scaffold React app with Vite
- [x] Set up Tailwind CSS
- [x] `/src/api/` module — typed fetch wrappers for all backend routes
- [x] Layout — two-panel: dashboard on left, chat sidebar on right
- [x] `StoryArc/` — sentiment line chart (x = chapter, y = compound score, coloured by book)
- [x] `StoryArc/` — death timeline — `DeathTimeline.jsx` scatter chart built; X axis = sequential chapter index across series; 13 verified death events in `events.json`; `/api/story/deaths` route serves `chapter_seq_index` for correct positioning
- [x] `StoryArc/` — word count bar chart per book
- [x] `CharacterIntel/` — character mention frequency line chart (filterable by character)
- [x] `CharacterIntel/` — relationship graph — force-directed graph via react-force-graph-2d; co-occurrence edges from top-30 characters
- [x] Overview page — OverviewPage.jsx with 7 KPI cards (total chapters, total words, longest book, top character, most positive/negative chapter, most connected); independent per-card loading and error states
- [x] Character heatmap — CharacterHeatmap.jsx; top 15 chars × 7 books; avg mentions_per_1k_words per cell; lerp color scale; responds to global FilterContext
- [x] Tab navigation — TabBar in App.jsx; Overview / Story Arc / Character Intel; no router library; chat panel always visible
- [ ] `CharacterIntel/` — allegiance shift timeline — **BLOCKED**: see Technical Debt
- [x] `ChatPanel/` — chat UI with message history
- [x] `ChatPanel/` — chart context serialisation: on each message, capture current chart type + visible data + active filters and include in request payload
- [x] Streaming response rendering in chat panel
- [x] `ChatPanel/` — conversation history: last 6 turns sent as `history` array with each request; captured in component state via `messages.slice(-6)` before the current user message is appended
- [x] `ChatPanel/` — suggested prompt chips: 6 pre-written questions above the input; clicking populates the input (does not auto-send)
- [x] `ChatPanel/` — source cards: backend emits `__SOURCES__:<json>\n` header before streaming; frontend parses and renders `SourceCards.jsx` (book + chapter pills) below each AI answer
- [x] `ChatPanel/` — filter indicator: violet pill below header shows active book filter ("Filtering: Book 1, 3, 5"); hidden when all books selected; reads FilterContext directly
- [x] `ChatPanel/` — copy button: copies last AI answer to clipboard; disabled when no answer
- [x] `ChatPanel/` — clear button: resets full conversation history; disabled when no messages

---

## Phase 5 — Polish

- [x] Loading states on all charts
- [x] Error states on all charts and chat
- [x] Empty state for chat panel on first load
- [x] Per-chart book filter: sentiment chart had a multi-select book dropdown (removed in Session 12 — replaced by global filter)
- [x] Book filter that syncs across all charts — global FilterBar + FilterContext wired to all 5 chart components; SentimentChart local filter removed
- [ ] Chapter range filter (deferred — book filter only in Session 12)
- [ ] Character filter (deferred — later session)
- [x] Dark mode — theme.js palette + Tailwind warm/gold + Recharts explicit props; warm off-white text; #0f1117 background

---

## Technical Debt

- Dialogue attribution (who says what) is unresolved — current NER approach will find character names but not tag dialogue speakers. May need a custom heuristic or a separate model.
- ~~**Relationship graph** — blocked on: library decision; relationships.json missing; empty route.~~ **Resolved in session 7**: `react-force-graph-2d` chosen; `relationships.py` written and run; route now has Pydantic model; frontend component complete.
- ~~**COLORS duplication** — COLORS array was duplicated between MentionsChart and RelationshipGraph.~~ **Resolved in session 7**: extracted to `src/utils/colors.js`.
- **Allegiance shift timeline** — no data source; would require a preprocessing script designed from scratch. Moved here from Phase 4 as indefinitely deferred.
- Embedding model confirmed: `sentence-transformers/all-MiniLM-L6-v2`. Gemini Embedding API not used.
- ~~**Single-token unresolved aliases (Ron, Lupin, McGonagall, etc.)**~~ **Resolved in session 10**: `character_aliases.manual.json` created with 37 manual aliases; merge priority manual > Gemini now applied in `ner_mentions.py`.
- **mentions_per_1k_words frontend toggle** — field now in characters.json and served by `/api/characters/mentions`; raw vs normalized toggle in MentionsChart deferred.
- **deaths.json now superseded by events.json** — `deaths.json` is an empty `[]` leftover; `/api/story/deaths` now loads from `events.json` filtered by `event_type=="death"`; `deaths.json` can be deleted in a cleanup pass.
- **MentionsChart chapter titles** — mentions API (`/api/characters/mentions`) does not expose `chapter_title`; tooltip shows full book title (via BOOK_TITLES map) but chapter number only. Fix: load chapters.json in characters.py and add `chapter_title` to MentionRecord.
- **hero.png in src/assets/** — not imported anywhere; safe to delete in a cleanup pass.
- **MentionsChart character selection not reset on book filter change** — when selectedBooks changes, the character toggle (`selected` Set) is not reset to the new top-10. Characters selected from "all books" view persist even if they don't appear in the filtered view — they silently disappear from the chart. Acceptable for now; could be improved by resetting selected to new top-10 when selectedBooks changes.
- **WordCountChart has a local BOOK_TITLES copy** — `WordCountChart.jsx` defines its own `BOOK_TITLES` object instead of importing from `src/utils/theme.js`. Harmless but inconsistent; fix in a cleanup pass.
- **Source cards show all 5 RAG chunks regardless of relevance** — SourceCards.jsx renders all sources the backend returns (up to 5 deduplicated chunks). No relevance filtering. Acceptable for now; could rank or limit to 3 in a future pass.
- **RelationshipGraph edges not filtered by book** — edges are aggregate co-occurrence across all 7 books; when filtering to a subset of books, visible edges are those connecting visible nodes, but edge weights still reflect all-book co-occurrence, not just the selected books. Would require per-book edge storage in relationships.json to fix properly.
- CORS port was hardcoded to `3000` instead of `5173` (Vite default) — fixed in session 6, but Vite default port should be verified at setup in future projects.
