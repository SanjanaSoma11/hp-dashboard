import json
import logging
from pathlib import Path

from fastapi import APIRouter
from pydantic import BaseModel

logger = logging.getLogger(__name__)

_DATA_DIR = Path(__file__).parent.parent / "data"

with (_DATA_DIR / "sentiment.json").open() as f:
    _sentiment: list[dict] = json.load(f)

with (_DATA_DIR / "chapters.json").open() as f:
    _chapters: list[dict] = json.load(f)

with (_DATA_DIR / "events.json").open() as f:
    _events: list[dict] = json.load(f)

# (book, chapter) → {book_title, chapter_title}
_chapter_meta: dict[tuple[int, int], dict] = {
    (ch["book_number"], ch["chapter_number"]): {
        "book_title": ch.get("book_title", f"Book {ch['book_number']}"),
        "chapter_title": ch.get("chapter_title", f"Chapter {ch['chapter_number']}"),
    }
    for ch in _chapters
}

# Build sequential chapter index: sort chapters by (book, chapter), assign 0-based index.
_sorted_chapters = sorted(_chapters, key=lambda c: (c["book_number"], c["chapter_number"]))
_chapter_seq: dict[tuple[int, int], int] = {
    (c["book_number"], c["chapter_number"]): i
    for i, c in enumerate(_sorted_chapters)
}

router = APIRouter()


class SentimentRecord(BaseModel):
    book: int
    chapter: int
    book_title: str
    chapter_title: str
    compound: float
    positive: float
    negative: float
    neutral: float


class WordCountRecord(BaseModel):
    book: int
    chapter: int
    word_count: int


class DeathEvent(BaseModel):
    character: str
    book: int
    chapter: int
    book_title: str
    chapter_title: str
    chapter_seq_index: int


@router.get("/sentiment", response_model=list[SentimentRecord])
def get_sentiment() -> list[dict]:
    """Return per-chapter VADER sentiment scores with book and chapter titles."""
    enriched = []
    for r in _sentiment:
        meta = _chapter_meta.get((r["book"], r["chapter"]), {})
        enriched.append({
            **r,
            "book_title": meta.get("book_title", f"Book {r['book']}"),
            "chapter_title": meta.get("chapter_title", f"Chapter {r['chapter']}"),
        })
    return enriched


@router.get("/wordcount", response_model=list[WordCountRecord])
def get_wordcount() -> list[WordCountRecord]:
    """Return per-chapter word counts computed from chapter text."""
    return [
        WordCountRecord(
            book=ch["book_number"],
            chapter=ch["chapter_number"],
            word_count=len(ch["text"].split()),
        )
        for ch in _chapters
    ]


@router.get("/deaths", response_model=list[DeathEvent])
def get_deaths() -> list[DeathEvent]:
    """Return major character deaths with sequential chapter index for timeline plotting."""
    deaths = [e for e in _events if e["event_type"] == "death"]
    return [
        DeathEvent(
            character=d["character"],
            book=d["book"],
            chapter=d["chapter"],
            book_title=_chapter_meta.get((d["book"], d["chapter"]), {}).get(
                "book_title", f"Book {d['book']}"
            ),
            chapter_title=_chapter_meta.get((d["book"], d["chapter"]), {}).get(
                "chapter_title", f"Chapter {d['chapter']}"
            ),
            chapter_seq_index=_chapter_seq.get((d["book"], d["chapter"]), 0),
        )
        for d in deaths
    ]
