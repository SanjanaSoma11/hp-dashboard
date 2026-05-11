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

# TODO: deaths data not yet populated
with (_DATA_DIR / "deaths.json").open() as f:
    _deaths: list = json.load(f)

router = APIRouter()


class SentimentRecord(BaseModel):
    book: int
    chapter: int
    compound: float
    positive: float
    negative: float
    neutral: float


class WordCountRecord(BaseModel):
    book: int
    chapter: int
    word_count: int


@router.get("/sentiment", response_model=list[SentimentRecord])
def get_sentiment() -> list[dict]:
    """Return per-chapter VADER sentiment scores."""
    return _sentiment


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


@router.get("/deaths", response_model=list)
def get_deaths() -> list:
    """Return character deaths per chapter. Placeholder — data not yet populated."""
    # TODO: deaths data not yet populated
    return _deaths
