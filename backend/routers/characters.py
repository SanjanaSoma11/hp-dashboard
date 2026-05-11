import json
import logging
from pathlib import Path

from fastapi import APIRouter
from pydantic import BaseModel

logger = logging.getLogger(__name__)

_DATA_DIR = Path(__file__).parent.parent / "data"

with (_DATA_DIR / "characters.json").open() as f:
    _raw = json.load(f)

_mentions: list[dict] = [
    {
        "character": r["character_name"],
        "book": r["book_number"],
        "chapter": r["chapter_number"],
        "mention_count": r["mention_count"],
    }
    for r in _raw
]

with (_DATA_DIR / "relationships.json").open() as f:
    _relationships: list = json.load(f)

router = APIRouter()


class MentionRecord(BaseModel):
    character: str
    book: int
    chapter: int
    mention_count: int


class RelationshipRecord(BaseModel):
    source: str
    target: str
    weight: int


@router.get("/mentions", response_model=list[MentionRecord])
def get_mentions() -> list[dict]:
    """Return per-chapter character mention counts."""
    return _mentions


@router.get("/relationships", response_model=list[RelationshipRecord])
def get_relationships() -> list:
    """Return character co-occurrence edge list for the top 30 characters."""
    return _relationships
