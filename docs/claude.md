# Claude Instructions

Instructions for AI assistants working on this project.

---

## Project Context

This is a local Harry Potter analytics dashboard built for personal/educational use. It is not deployed. Book text is copyrighted and must never be committed. The AI layer uses Gemini 2.0 Flash for chart-aware Q&A.

---

## Working Principles

- **Don't over-engineer.** This is a fun personal project, not production software. Prefer simple, readable solutions over clever abstractions.
- **Explain tradeoffs honestly.** If there is a better approach, say so even if it means changing a prior decision.
- **Push back on bad ideas.** Don't validate weak decisions to be agreeable.
- **Stay local-first.** All solutions should work entirely on localhost. Do not suggest cloud services, databases, or infrastructure unless explicitly asked.

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

## What Not to Do

- Do not suggest deploying anywhere
- Do not suggest adding auth, user accounts, or sessions
- Do not commit or reference book text in any code
- Do not add dependencies without a clear reason
- Do not use `print()` for logging in FastAPI — use Python `logging`
- Do not hardcode the Gemini API key — it lives in `.env`

---

## Environment

- Machine: MacBook Air M4, 16GB RAM, macOS
- Python environment: venv at `/backend/.venv`
- Node: via nvm
- Books location: `/books/` (gitignored)
- Gemini API key: stored in `/backend/.env` as `GEMINI_API_KEY`
