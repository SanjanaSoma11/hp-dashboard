# Memory

Tracks key facts, decisions made, and project history for long-term context.

---

## Project Identity

- **Name:** HP Dashboard
- **Type:** Personal fun project, non-commercial, not deployed
- **Developer:** Solo, local machine only
- **Purpose:** Harry Potter analytics + AI Q&A for personal use

---

## Key Decisions

| Decision | Choice | Reason |
|---|---|---|
| Scope | Story Arc + Character Intelligence dashboards + Chat Q&A | Best combination of coherent data and interesting interactivity |
| Frontend | React + Recharts | Standard, well-documented, good charting library |
| Backend | FastAPI (Python) | Fits Python-heavy preprocessing stack |
| Vector store | ChromaDB | Fully local, no external service needed |
| NER | spaCy | Best Python NER library for named entity extraction |
| Sentiment | VADER | Lightweight, no model download, works well on narrative text |
| Chunking | LangChain | Standard RAG tooling |
| AI model | Gemini 2.0 Flash | Free tier, large context window, good quality |
| Deployment | None — localhost only | Book text is copyrighted, keeping everything local |
| Book text in git | No — gitignored | Copyright compliance |
| Preprocessing data in git | No — gitignored | Derived from copyrighted text |

---

## Dataset

- Source: Kaggle (`rupanshukapoor/harry-potter-books`)
- Format: 7 plain `.txt` files, one per book
- Chapter detection: ALL CAPS lines (e.g. `THE BOY WHO LIVED`)
- Page markers present: `Page | N Harry Potter and the... - J.K. Rowling` — strip during preprocessing
- Dialogue: not tagged by speaker — needs NLP attribution
- License on Kaggle dataset: CC0 (note: the Kaggle uploader did not have rights to relicense — handle as copyrighted)

---

## Hardware

- MacBook Air M4, 16GB unified memory, macOS
- Local model inference (Ollama) was considered and is capable on this hardware, but Gemini API was chosen for convenience

---

## What Has Been Done

- [x] Project ideation and scope defined
- [x] Dashboard combination chosen (Story Arc + Character Intel + Chat Q&A)
- [x] Tech stack finalised
- [x] Architecture designed
- [x] Project docs created (architecture.md, claude.md, readme.md, memory.md, backlog.md, restart.md, agents.md)

## What Has Not Been Done

- [ ] Any code written
- [ ] Project directory initialised
- [ ] Preprocessing run
- [ ] Backend built
- [ ] Frontend built

---

## Known Data Quality Issues

| Book | Issue | Detail | Decision |
|---|---|---|---|
| Book 4 (Goblet of Fire) | 36 chapters detected instead of 37 | Chapter 36 heading lost in OCR — text is present but heading is missing, so the splitter merged it into the previous chapter | Accepted as OCR ceiling, not a code bug. Do not attempt to fix in `chapter_splitter.py`. |

---

## Open Questions

- How to handle dialogue attribution (who says what) — spaCy alone won't solve this cleanly
- Whether to use `sentence-transformers` or Gemini's own embedding API for ChromaDB
- Exact Recharts components to use for relationship graph (likely need D3 or a graph library instead)
