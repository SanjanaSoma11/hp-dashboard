# Agents

Defines AI working modes for different tasks in this project. Tell Claude which mode to use at the start of a session.

---

## Mode: Preprocessor

**Use when:** Writing or debugging any file in `/backend/preprocessing/`

**Behaviour:**
- Think about data quality first — what could be malformed in the raw text and how to handle it
- Always validate output: print sample rows, shapes, and spot-check named entities before saving
- Write preprocessing as standalone scripts that can be run independently, not imported modules
- Output files go to `/backend/data/` as JSON or CSV — confirm the schema before writing
- Prefer readable loops over one-liners — this code runs once, clarity matters more than brevity
- Flag ambiguous parsing decisions (e.g. chapter heading detection edge cases) as comments

---

## Mode: Backend Engineer

**Use when:** Writing or debugging anything in `/backend/routers/` or `main.py`

**Behaviour:**
- Routes are read-only — they load pre-computed data from `/backend/data/`, they do not recompute
- The only exception is `/api/chat` which queries ChromaDB and calls Gemini
- Always add response models (Pydantic) to routes — no bare dicts
- CORS must be open to `localhost:3000`
- Gemini API key comes from `.env` via `python-dotenv` — never hardcode it
- Stream Gemini responses using `StreamingResponse` where possible
- Keep routes thin — business logic goes in a `/backend/services/` module if it grows

---

## Mode: Frontend Engineer

**Use when:** Writing or debugging anything in `/frontend/src/`

**Behaviour:**
- Functional components only
- Fetch calls go in `/src/api/` — never inline in components
- Use Recharts for all charts except the relationship graph (use D3 or react-force-graph for that)
- Tailwind for all styling — no inline styles, no CSS modules
- The chat panel must always serialise current chart context before sending a message — this is the core feature, never skip it
- Think about loading and error states on every component before considering it done
- Keep component files under ~150 lines — split if they grow beyond that

---

## Mode: Debugger

**Use when:** Something is broken and the cause is unclear

**Behaviour:**
- Read the full error message and stack trace before suggesting anything
- Ask for the actual output, not just a description of it
- Form a hypothesis, explain it, then suggest the minimal change to test it
- Do not suggest rewriting working code to fix a bug in adjacent code
- If the bug is in preprocessing output, validate the JSON/CSV first before touching the code that reads it

---

## Mode: Reviewer

**Use when:** A feature is complete and needs a final check before moving on

**Behaviour:**
- Check against `docs/architecture.md` — does the implementation match the design?
- Check `docs/backlog.md` — is this task actually done or are sub-tasks missed?
- Look for: missing error handling, hardcoded values, copyright text accidentally included in any output, API keys in code
- Update `docs/memory.md` with any new decisions made during this feature
- Update `docs/restart.md` with current state
- Update `docs/backlog.md` — mark completed items, add any new technical debt found
