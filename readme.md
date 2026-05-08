# HP Dashboard

A local Harry Potter analytics dashboard with AI-powered Q&A.

Combines a **Story Arc dashboard** (sentiment timeline, character mentions, death timeline) with a **Character Intelligence dashboard** (relationship graph, allegiance shifts, dialogue breakdown) and a **chart-aware chat panel** that lets you ask questions about the story grounded in the actual book text.

> **Note:** This is a personal, non-commercial fan project for educational use. Book text is not included in this repository. You must supply your own copies.

---

## Features

- Sentiment analysis across all 7 books by chapter
- Character mention frequency over time
- Character relationship graph
- Allegiance shift tracking
- Death timeline
- AI chat panel with context from the currently visible chart (powered by Gemini)
- RAG-grounded answers pulled from book text via ChromaDB

---

## Prerequisites

- Python 3.11+
- Node.js 18+
- A [Gemini API key](https://aistudio.google.com/app/apikey) (free tier)
- Harry Potter book text files (not included — source your own copies)

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/your-username/hp-dashboard.git
cd hp-dashboard
```

### 2. Add book files

Place your book `.txt` files in the `/books/` directory:

```
books/
├── Book1.txt
├── Book2.txt
├── Book3.txt
├── Book4.txt
├── Book5.txt
├── Book6.txt
└── Book7.txt
```

These are gitignored and will never leave your machine.

### 3. Set up Python backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in `/backend/`:

```
GEMINI_API_KEY=your_key_here
```

### 4. Run preprocessing (once only)

```bash
cd backend
python preprocessing/chapter_splitter.py
python preprocessing/ner_mentions.py
python preprocessing/sentiment.py
python preprocessing/chunker.py
```

This generates all JSON/CSV files and populates ChromaDB. You only need to run this once.

### 5. Start the backend

```bash
cd backend
uvicorn main:app --reload
```

Backend runs at `http://localhost:8000`.

### 6. Set up and start the frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:3000`.

---

## Project Structure

See [`docs/architecture.md`](docs/architecture.md) for the full breakdown.

---

## Gitignored

The following are never committed:

- `/books/` — book text files
- `/backend/data/` — preprocessed JSON/CSV
- `/backend/chroma_db/` — vector store
- `/backend/.env` — API key

---

## License

Code is MIT licensed. Book content is copyright J.K. Rowling. This project does not distribute or reproduce any copyrighted text.
