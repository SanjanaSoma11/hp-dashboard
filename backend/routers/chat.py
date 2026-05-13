import asyncio
import json
import logging
import os
import re
from pathlib import Path
from typing import Any, AsyncGenerator

import chromadb
from dotenv import load_dotenv
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from google import genai
from google.genai import types
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

from services.analytics import (
    get_character_mentions,
    get_relationships,
    get_sentiment_extremes,
    get_top_characters,
    known_characters,
)

logger = logging.getLogger(__name__)

_ROOT = Path(__file__).parent.parent
_TOP_K = 5
_MODEL = "gemini-3.1-flash-lite"

_SYSTEM_PROMPT = """You are a Harry Potter expert. Answer questions using ONLY the evidence passages provided below.

Rules you must follow without exception:
1. Every factual claim must be followed by an inline citation in the format: (Book X, Chapter Y: [title]).
2. If the provided passages do not contain enough information to answer the question, respond with exactly: "I don't have enough information in the text to answer that."
3. Never invent quotes, character names, chapter names, or plot details that are not present in the passages.
4. Never fabricate citations or refer to chapters not mentioned in the passages.
5. When a "Structured analytics data" block is present, treat it as authoritative for any quantitative answer (counts, rankings, comparisons). Base your answer on that data and still cite book/chapter where applicable."""

# Ordinal and word-form book number mappings
_BOOK_WORD_MAP = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
    "first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5, "sixth": 6, "seventh": 7,
    "philosopher": 1, "sorcerer": 1, "chamber": 2, "prisoner": 3,
    "goblet": 4, "order": 5, "phoenix": 5, "half": 6, "hallows": 7,
}

_QUANT_KEYWORDS = frozenset({
    "most", "least", "how many", "compare", "which book", "top",
    "lowest", "highest", "ranked", "how often", "fewest", "count",
})

# Loaded once at startup from relationships.json
_KNOWN_CHARACTERS: list[str] = []


def _init_known_characters() -> None:
    global _KNOWN_CHARACTERS
    try:
        _KNOWN_CHARACTERS = known_characters()
    except Exception:
        logger.warning("Could not load known characters for analytics classifier")


def _extract_book(q: str) -> int | None:
    """Extract a book number from question text via digit or word form."""
    m = re.search(r'\bbook\s+(\d)\b', q)
    if m:
        return int(m.group(1))
    for word, num in _BOOK_WORD_MAP.items():
        if re.search(r'\b' + re.escape(word) + r'\b', q):
            return num
    return None


def _extract_character(q: str) -> str | None:
    """Return the first known character whose name (or a part of it) appears in the question."""
    for char in _KNOWN_CHARACTERS:
        if char.lower() in q:
            return char
    # Fall back to matching individual tokens (length > 3) with word boundaries
    for char in _KNOWN_CHARACTERS:
        for part in char.split():
            if len(part) > 3 and re.search(r'\b' + re.escape(part.lower()) + r'\b', q):
                return char
    return None


def _detect_analytics(question: str) -> dict | None:
    """Return a structured analytics payload if the question is quantitative, else None."""
    q = question.lower()

    if not any(kw in q for kw in _QUANT_KEYWORDS):
        return None

    book = _extract_book(q)
    char = _extract_character(q)

    is_sentiment = any(kw in q for kw in {
        "sentiment", "mood", "tone", "positive", "negative", "dark", "sad", "happy", "cheerful", "depressing",
    })
    is_mention = any(kw in q for kw in {
        "mention", "appear", "how many", "how often", "count", "frequency", "times",
    })
    is_relationship = any(kw in q for kw in {
        "connect", "relationship", "interact", "appear with", "alongside", "relation",
    })
    is_top = any(kw in q for kw in {"most", "top", "highest", "ranked", "least", "lowest", "fewest"})

    # Relationships for a specific character
    if is_relationship and char:
        return {"query_type": "relationships", "character": char, "data": get_relationships(char)}

    # Sentiment chapter ranking
    if is_sentiment and is_top:
        direction = (
            "negative"
            if any(kw in q for kw in {"negative", "dark", "sad", "depressing", "worst", "lowest"})
            else "positive"
        )
        return {"query_type": "sentiment_extremes", "direction": direction, "data": get_sentiment_extremes(5, direction)}

    # Mention count for a specific character
    if is_mention and char:
        return {"query_type": "character_mentions", "character": char, "book": book, "data": get_character_mentions(char, book)}

    # Top characters by mention count
    if is_top and any(kw in q for kw in {"character", "mention", "appear", "popular", "frequent", "who"}):
        return {"query_type": "top_characters", "book": book, "data": get_top_characters(book, 10)}

    return None

load_dotenv(_ROOT / ".env")

client = genai.Client(
    vertexai=True,
    project=os.getenv("GCP_PROJECT", "hpdashboard"),
    location=os.getenv("GCP_LOCATION", "global"),
)

_embed_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
_chroma = chromadb.PersistentClient(path=str(_ROOT / "chroma_db"))
_collection = _chroma.get_collection("hp_books")

router = APIRouter()

_init_known_characters()


class HistoryTurn(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    question: str
    chart_context: dict[str, Any]
    history: list[HistoryTurn] = []


def _build_prompt(
    question: str,
    docs: list[str],
    metadatas: list[dict],
    chart_context: dict[str, Any],
    history: list[HistoryTurn],
    analytics: dict | None = None,
) -> str:
    """Assemble the prompt from retrieved passages with citations, chart context, history, and the question."""
    parts: list[str] = []

    if analytics:
        parts.append(
            "Structured analytics data (pre-computed from the full dataset — use this as the primary source for any quantitative answer):\n\n"
            + json.dumps(analytics, indent=2)
        )

    if docs:
        passages: list[str] = []
        for i, (doc, meta) in enumerate(zip(docs, metadatas)):
            book = meta.get("book_title", "Unknown Book")
            chapter = meta.get("chapter_title", "Unknown Chapter")
            passages.append(f"[{i + 1}] Source: {book}, {chapter}\n{doc}")
        parts.append("Evidence passages from the Harry Potter books:\n\n" + "\n\n".join(passages))

    parts.append(f"Current chart context:\n{json.dumps(chart_context, indent=2)}")

    if history:
        history_lines = [
            f"{'User' if turn.role == 'user' else 'Assistant'}: {turn.content}"
            for turn in history
        ]
        parts.append("Conversation history:\n\n" + "\n\n".join(history_lines))

    parts.append(f"Question: {question}")

    return "\n\n---\n\n".join(parts)


async def _stream_answer(
    question: str,
    chart_context: dict[str, Any],
    history: list[HistoryTurn],
) -> AsyncGenerator[str, None]:
    """Query ChromaDB and stream a Gemini response token-by-token."""
    vector = _embed_model.encode(question).tolist()
    results = _collection.query(query_embeddings=[vector], n_results=_TOP_K)
    docs: list[str] = results.get("documents", [[]])[0]
    metadatas: list[dict] = results.get("metadatas", [[]])[0]
    logger.info("ChromaDB returned %d chunks for question: %r", len(docs), question)

    analytics = _detect_analytics(question)
    if analytics:
        logger.info("Analytics data injected: type=%s", analytics.get("query_type"))

    prompt = _build_prompt(question, docs, metadatas, chart_context, history, analytics)

    # Emit deduplicated source list before the text stream so the frontend can render source cards
    seen_sources: set[tuple[str, str]] = set()
    sources: list[dict] = []
    for m in metadatas:
        key = (m.get("book_title", ""), m.get("chapter_title", ""))
        if key not in seen_sources:
            seen_sources.add(key)
            sources.append({"book_title": key[0], "chapter_title": key[1]})
    yield f"__SOURCES__:{json.dumps(sources)}\n"

    loop = asyncio.get_running_loop()
    queue: asyncio.Queue[str | None] = asyncio.Queue()

    def _produce() -> None:
        try:
            for chunk in client.models.generate_content_stream(
                model=_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(system_instruction=_SYSTEM_PROMPT),
            ):
                if chunk.text:
                    loop.call_soon_threadsafe(queue.put_nowait, chunk.text)
        finally:
            loop.call_soon_threadsafe(queue.put_nowait, None)

    future = loop.run_in_executor(None, _produce)

    while True:
        token = await queue.get()
        if token is None:
            break
        yield token

    await future


@router.post("/")
async def post_chat(body: ChatRequest) -> StreamingResponse:
    """Stream a Vertex AI answer grounded in ChromaDB context and chart data."""
    return StreamingResponse(
        _stream_answer(body.question, body.chart_context, body.history),
        media_type="text/plain",
    )
