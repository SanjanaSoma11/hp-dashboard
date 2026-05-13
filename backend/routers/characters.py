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
        "mentions_per_1k_words": r.get("mentions_per_1k_words", 0.0),
    }
    for r in _raw
]

with (_DATA_DIR / "relationships.json").open() as f:
    _rel_data: dict = json.load(f)

router = APIRouter()


class MentionRecord(BaseModel):
    character: str
    book: int
    chapter: int
    mention_count: int
    mentions_per_1k_words: float = 0.0


class NodeRecord(BaseModel):
    id: str
    mention_count: int
    degree: int
    weighted_degree: float
    betweenness: float
    pagerank: float
    books: list[int]


class RelationshipRecord(BaseModel):
    source: str
    target: str
    weight: int


class RelationshipsResponse(BaseModel):
    nodes: list[NodeRecord]
    edges: list[RelationshipRecord]


@router.get("/mentions", response_model=list[MentionRecord])
def get_mentions() -> list[dict]:
    """Return per-chapter character mention counts."""
    return _mentions


@router.get("/relationships", response_model=RelationshipsResponse)
def get_relationships() -> dict:
    """Return character co-occurrence graph with centrality metrics for the top 30 characters."""
    return _rel_data
