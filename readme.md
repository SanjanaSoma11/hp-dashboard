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
- AI chat panel with context from the currently visible chart (powered by Gemini 3.1 Flash Lite via Vertex AI)
- RAG-grounded answers pulled from book text via ChromaDB

---

## Prerequisites

- Python 3.11+
- Node.js 18+
- A Google Cloud project with the Vertex AI API enabled, and `gcloud auth application-default login` completed on your machine (used for Gemini access — no API key needed)
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

Create a `.env` file in `/backend/` with your GCP project details if they differ from the defaults:

```
GCP_PROJECT=hpdashboard
GCP_LOCATION=global
```

Authentication uses Google Application Default Credentials (ADC). Run `gcloud auth application-default login` before starting the backend.

### 4. Run preprocessing (once only)

```bash
python backend/preprocessing/run_all.py
```

This runs all preprocessing scripts in the correct order and generates the JSON files and ChromaDB collection. You only need to run this once.

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

Frontend runs at `http://localhost:5173`.

---

## Project Structure

See [`docs/context.md`](docs/context.md) for the full breakdown.

---

## Gitignored

The following are never committed:

- `/books/` — book text files
- `/backend/data/` — preprocessed JSON/CSV
- `/backend/chroma_db/` — vector store
- `/backend/.env` — environment config

---

## License

Code is MIT licensed. Book content is copyright J.K. Rowling. This project does not distribute or reproduce any copyrighted text.
