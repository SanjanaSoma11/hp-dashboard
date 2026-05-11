import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any, AsyncGenerator

import chromadb
from dotenv import load_dotenv
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from google import genai
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

_ROOT = Path(__file__).parent.parent
_TOP_K = 5
_MODEL = "gemini-3.1-flash-lite"

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


class ChatRequest(BaseModel):
    question: str
    chart_context: dict[str, Any]


def _build_prompt(question: str, docs: list[str], chart_context: dict[str, Any]) -> str:
    """Assemble the prompt from retrieved chunks, chart context, and the question."""
    parts: list[str] = []

    if docs:
        numbered = "\n\n".join(f"[{i + 1}] {doc}" for i, doc in enumerate(docs))
        parts.append(f"Context passages from the Harry Potter books:\n\n{numbered}")

    parts.append(f"Current chart context:\n{json.dumps(chart_context, indent=2)}")
    parts.append(f"Question: {question}")

    return "\n\n---\n\n".join(parts)


async def _stream_answer(question: str, chart_context: dict[str, Any]) -> AsyncGenerator[str, None]:
    vector = _embed_model.encode(question).tolist()
    results = _collection.query(query_embeddings=[vector], n_results=_TOP_K)
    docs: list[str] = results.get("documents", [[]])[0]
    logger.info("ChromaDB returned %d chunks for question: %r", len(docs), question)

    prompt = _build_prompt(question, docs, chart_context)

    def _collect_chunks() -> list[str]:
        return [
            chunk.text
            for chunk in client.models.generate_content_stream(
                model=_MODEL,
                contents=prompt,
            )
            if chunk.text
        ]

    chunks = await asyncio.to_thread(_collect_chunks)
    for chunk in chunks:
        yield chunk


@router.post("/")
async def post_chat(body: ChatRequest) -> StreamingResponse:
    """Stream a Vertex AI answer grounded in ChromaDB context and chart data."""
    return StreamingResponse(
        _stream_answer(body.question, body.chart_context),
        media_type="text/plain",
    )
