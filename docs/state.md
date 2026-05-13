# State

Current project state. Read this at the start of every session before doing anything.

---

## Current Phase

**Phase 7 — Stabilization / Complete**

**Last updated:** 2026-05-13 (Session 17)

---

## What Was Just Completed

- **Chat UX polish (Session 17)**:
  - Text color audit — no `text-black` or `color: black` found anywhere; all components already use appropriate warm/neutral light colors from `theme.js`
  - `backend/routers/chat.py` — `_stream_answer` now emits a `__SOURCES__:<json>\n` header line before any AI tokens; contains deduplicated `[{book_title, chapter_title}]` from the ChromaDB `metadatas` for the query
  - `frontend/src/components/ChatPanel/SourceCards.jsx` — new sub-component; receives `sources` array from message state; renders compact pill-cards (book title + chapter title) below each AI response
  - `frontend/src/components/ChatPanel/ChatPanel.jsx` — major update:
    - Streaming logic now buffers until the first `\n`, parses the `__SOURCES__:` header, stores sources on the message object, then continues streaming the remaining text normally
    - `MessageList` — each assistant message renders `<SourceCards sources={msg.sources} />` below its bubble
    - `FilterIndicator` sub-component — reads `selectedBooks` from `useFilter()` directly (no prop); renders a violet pill "Filtering: Book 1, 3, 5" below the header when fewer than all 7 books are selected; hidden otherwise
    - Suggested prompt chips — 6 pre-written question buttons rendered above the input row; clicking populates the input without auto-sending; questions cover: quantitative (Book 4 mentions), sentiment (most negative chapter), relationship (most connected to Harry), narrative (end of Book 6), comparative (Hermione across books), and event-based (most deaths)
    - Copy button in header — calls `navigator.clipboard.writeText` on the last assistant message; disabled when no answer yet
    - Clear button in header — resets `messages`, `input`, and `error` state; disabled when no messages

- **Visual polish and relationship graph upgrades (Session 16)**:
  - `RelationshipGraph.jsx` — node size now scales by total `mention_count` (was pagerank); edge weight threshold slider below the graph with default set to median weight (hides the hairball on load); clicking a node shows `NodeStatsPanel` (mention count, degree, pagerank, top 3 connections by co-occurrence weight); click again to dismiss
  - `NodeStatsPanel.jsx` — new sub-component in `CharacterIntel/`; receives full node record + all edges + visible node set; computes top-3 neighbors by filtered edge weight
  - `src/utils/theme.js` — central palette: `THEME.bg`, `THEME.border`, `THEME.text`, `THEME.accent` (violet/gold/emerald), `THEME.chart` (grid/tick/label/link); `BOOK_TITLES` map moved here; all chart components import from this file for Recharts explicit props
  - `tailwind.config.js` — extended with `warm` (100/200/400/600) and `gold` (400/500/600) color keys; emerald already built into Tailwind
  - `src/components/Card.jsx` — reusable card wrapper with `title` (required) and `subtitle` (optional) props; `bg-neutral-900 border border-neutral-800` styling; all charts and the overview KPI section are wrapped in it
  - `StoryArc.jsx`, `CharacterIntel.jsx`, `OverviewPage.jsx` — converted `h3` + bare `div` wrappers to `<Card>` with title/subtitle props; section headings now use `text-warm-100`
  - `SentimentChart.jsx` — tooltip shows `book_title` + `chapter_title` (from API); Y-axis labeled "Sentiment"; THEME constants for grid/tick/label
  - `WordCountChart.jsx` — Y-axis labeled "Words"; tooltip shows full book title (from BOOK_TITLES); THEME constants
  - `MentionsChart.jsx` — tooltip shows full book title via BOOK_TITLES; Y-axis labeled "Mentions"; THEME constants
  - `DeathTimeline.jsx` — tooltip shows `book_title` + `chapter_title` from API; THEME constants
  - `backend/routers/story.py` — `SentimentRecord` and `DeathEvent` Pydantic models gain `book_title: str` + `chapter_title: str`; built from `_chapter_meta` dict at startup using `(book, chapter) → {book_title, chapter_title}` lookup from `chapters.json`
  - `App.jsx` — background updated to `#0f1117` (warm charcoal, matches THEME.bg.page)
  - `OverviewPage.jsx` KpiCard — text updated to `text-warm-100` / `text-warm-400` for warm off-white consistency
  - Deleted: `src/App.css` (Vite boilerplate, never imported); `src/assets/react.svg`; `src/assets/vite.svg`

- **Overview page, character heatmap, tab navigation (Session 15)**:
  - `src/components/Overview/OverviewPage.jsx` — 7 KPI cards: Total Chapters, Total Words, Longest Book, Top Character, Most Positive Chapter, Most Negative Chapter, Most Connected; each card has independent loading/error state; 4 parallel fetches (wordcount, sentiment, mentions, relationships) using existing API functions; `KpiCard` sub-component with label/value/sub/loading/error props; book number → title map (`BOOK_TITLES`) hardcoded on frontend for display (e.g., "Order of the Phoenix, Ch. 28"); cards use `bg-neutral-900 border border-neutral-800` to be visually distinct from chart panels
  - `src/components/CharacterIntel/CharacterHeatmap.jsx` — top 15 characters (ranked by total mention_count across all books, stable ordering), 7 columns (books), cell value = avg `mentions_per_1k_words` per (character, book) pair across chapters; color scale interpolated from dark neutral `rgb(25,25,35)` to violet-600 `rgb(124,58,237)`; plain HTML table + inline RGB via `lerpColor()`; responds to global FilterContext (hides deselected book columns, recomputes maxVal over visible books only); no new charting library
  - `App.jsx` — `TabBar` component with Overview / Story Arc / Character Intel tabs; active tab = violet underline, inactive = neutral hover; `useState('overview')` default; FilterBar stays visible on all views; chat panel stays visible on all views; no router library
  - `src/components/CharacterIntel/CharacterIntel.jsx` — CharacterHeatmap added between MentionsChart and RelationshipGraph
  - `src/components/Overview/index.js`, `src/components/CharacterIntel/index.js` updated

- **Analytics tool layer for AI chat (Session 14)**:
  - `backend/services/analytics.py` created with four functions, each loading from pre-computed JSON in `backend/data/` — no recomputation, no DB calls: `get_top_characters(book, n)`, `get_character_mentions(character, book)`, `get_sentiment_extremes(n, direction)`, `get_relationships(character)`; all data files are `lru_cache`-loaded; `known_characters()` exported for classifier bootstrap
  - `_detect_analytics(question)` added to `backend/routers/chat.py` — keyword heuristics check for "most", "least", "how many", "compare", "which book", "top", "lowest", "highest", "ranked", "how often", "fewest", "count"; `_extract_book()` uses `\bbook N\b` digit pattern + word-form map with word boundaries; `_extract_character()` matches against the 30 known characters from relationships.json (full name first, then word-boundary token fallback)
  - Classifier routes to: `relationships` (character + connect/interact keywords), `sentiment_extremes` (sentiment + top/least), `character_mentions` (character + mention/appear/count), `top_characters` (top + character/who keywords); returns None for non-quantitative questions
  - `_build_prompt()` gains an optional `analytics: dict | None` parameter; when present, injects a clearly labelled "Structured analytics data" block before RAG passages
  - `_SYSTEM_PROMPT` updated with Rule 5: treat the analytics block as authoritative for quantitative answers, still cite book/chapter where applicable; all Session 13 hardening rules intact
  - `_init_known_characters()` called at module load (after `router = APIRouter()`) to populate `_KNOWN_CHARACTERS` from relationships.json

- **AI chat improvements (Session 13)**:
  - `_build_prompt()` now pulls `metadatas` from ChromaDB results and labels each passage with its `book_title` and `chapter_title`; Gemini is instructed to cite sources inline as `(Book X, Chapter Y: [title])`
  - `HistoryTurn` Pydantic model added; `ChatRequest` gains an optional `history: list[HistoryTurn] = []` field; last 6 conversation turns are included in the prompt between chart context and the question
  - `_SYSTEM_PROMPT` hardened: answer only from evidence, cite every claim, exact fallback phrase when evidence is thin, no invented quotes or chapter names; passed via `types.GenerateContentConfig(system_instruction=...)`
  - True async streaming: replaced collect-then-yield with an `asyncio.Queue` bridge — `_produce()` runs in a thread executor and pushes tokens via `call_soon_threadsafe`; `None` sentinel signals end-of-stream
  - `streamChat(question, chartContext, history)` updated in `chat.js`; `ChatPanel.jsx` captures `messages.slice(-6)` before state update and passes as history

- **Previous session**: Centrality metrics added to relationship graph: `relationships.py` now builds a networkx graph and computes `degree`, `weighted_degree`, `betweenness`, and `pagerank` per character; nodes also carry a `books: [int]` field listing which books they appear in; relationships.json schema changed from a flat edge list to `{nodes: [...], edges: [...]}`; `characters.py` router updated with `NodeRecord` and `RelationshipsResponse` Pydantic models; `networkx==3.4.2` added to requirements.txt
- **Global book filter bar**: `FilterContext` (React Context, `selectedBooks: number[]`) added and wraps the entire app; `FilterBar` component renders 7 toggle buttons (Book 1–7) with All/Clear controls, displayed at the top of the main panel above all sections; every chart component now reads from FilterContext and filters client-side
- **SentimentChart local filter removed**: `BookDropdown` component and local `selectedBooks` state deleted; chart now reads `selectedBooks` from FilterContext; dynamic Y-axis and X-axis reindexing behavior preserved
- **All 5 chart components wired to global filter**: SentimentChart, DeathTimeline, WordCountChart, MentionsChart, RelationshipGraph all filter on `selectedBooks` via `useMemo`; empty states shown when no books selected
- **RelationshipGraph upgraded**: uses new `{nodes, edges}` API response; nodes sized by PageRank (radius 3–10px); filters to characters whose `books` field intersects `selectedBooks`, then removes edges where either endpoint is hidden
- **Chat context updated**: `chartContext` now includes `globalFilters: { selectedBooks }` so the AI knows the active filter state

- Previous session: Chunk metadata enriched; events.json with 13 verified death events; death timeline scatter chart built

---

## What's Next

Project is feature-complete as of Session 17. Remaining items are all indefinitely deferred:
- Chapter range filter (deferred — book filter deemed sufficient)
- Character filter (deferred)
- Allegiance shift timeline (indefinitely deferred — no data source)
- Dialogue attribution (indefinitely deferred)
- mentions_per_1k_words raw vs normalized toggle in MentionsChart (deferred)

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
| Session 9 | deaths.json placeholder confirmed; README fixed (auth, model, port, preprocessing, docs ref); run_all.py orchestrator created; API_BASE centralized in frontend/src/api/config.js |
| Session 10 | Manual character dictionary (37 aliases, character_aliases.manual.json); alias merge priority (manual > Gemini, 55 total); mentions_per_1k_words added to characters.json and MentionRecord model; pipeline rerun validated |
| Session 11 | Chunk metadata enriched (book_title, chapter_title, word_count, characters_mentioned); events.json created with 13 verified death events; death timeline scatter chart built in frontend; /api/story/deaths route updated with Pydantic model and chapter_seq_index |
| Session 12 | Centrality metrics (degree, weighted_degree, betweenness, pagerank, books) added to relationship graph nodes via networkx; global book FilterBar + FilterContext added; all 5 chart components wired to global filter; SentimentChart local filter removed; RelationshipGraph upgraded to new API format with node sizing by PageRank; chat context includes globalFilters |
| Session 13 | AI chat improvements: chunk metadata (book_title, chapter_title) surfaced in _build_prompt() with inline citation instructions; HistoryTurn model + history field on ChatRequest; last 6 turns passed from ChatPanel; hardened system prompt (evidence-only, mandatory citations, no invention); true async streaming via asyncio.Queue bridge with thread executor |
| Session 14 | Analytics tool layer: backend/services/analytics.py with get_top_characters, get_character_mentions, get_sentiment_extremes, get_relationships (all load from JSON, lru_cache); keyword classifier _detect_analytics() in chat.py with book/character extraction; analytics block injected into prompt before RAG passages when question is quantitative; system prompt updated with Rule 5 (analytics block is authoritative for counts/rankings) |
| Session 15 | Overview page (7 KPI cards, independent per-card loading/error); CharacterHeatmap (top 15 chars × 7 books, avg mentions_per_1k_words, lerp color scale dark→violet, FilterContext-aware); App.jsx tab navigation (Overview/Story Arc/Character Intel, violet underline active state, no router library) |
| Session 16 | RelationshipGraph: node size by mention_count, edge threshold slider (default=median), node click stats panel (NodeStatsPanel.jsx); theme.js palette + Tailwind warm/gold colors; Card.jsx wrapper + all charts/overview wrapped; chart tooltip book+chapter titles (backend enriched SentimentRecord+DeathEvent with book_title/chapter_title); axis labels on all charts; dark theme: #0f1117 bg, warm-100/400 text, THEME constants in all Recharts props; deleted App.css + Vite SVGs |
| Session 17 | Chat UX polish: text color audit (clean); backend chat.py emits __SOURCES__ JSON header before streaming; SourceCards.jsx sub-component renders source pills below AI answers; ChatPanel: suggested prompt chips (6 questions), filter indicator (reads FilterContext directly), copy button (last answer to clipboard), clear button (resets history) |
