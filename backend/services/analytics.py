import json
import logging
from functools import lru_cache
from pathlib import Path

logger = logging.getLogger(__name__)

_DATA = Path(__file__).parent.parent / "data"


@lru_cache(maxsize=1)
def _load_characters() -> list[dict]:
    with open(_DATA / "characters.json") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def _load_sentiment() -> list[dict]:
    with open(_DATA / "sentiment.json") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def _load_relationships() -> dict:
    with open(_DATA / "relationships.json") as f:
        return json.load(f)


def get_top_characters(book: int | None, n: int) -> list[dict]:
    """Return top N characters by total mention count, optionally filtered to a single book."""
    records = _load_characters()
    if book is not None:
        records = [r for r in records if r["book_number"] == book]

    totals: dict[str, int] = {}
    for r in records:
        totals[r["character_name"]] = totals.get(r["character_name"], 0) + r["mention_count"]

    ranked = sorted(totals.items(), key=lambda x: x[1], reverse=True)
    return [{"character": name, "total_mentions": count} for name, count in ranked[:n]]


def get_character_mentions(character: str, book: int | None) -> list[dict]:
    """Return per-chapter mention records for a character, optionally filtered to a book."""
    records = _load_characters()
    char_lower = character.lower()

    matches = [r for r in records if char_lower in r["character_name"].lower()]
    if book is not None:
        matches = [r for r in matches if r["book_number"] == book]

    return sorted(matches, key=lambda r: (r["book_number"], r["chapter_number"]))


def get_sentiment_extremes(n: int, direction: str) -> list[dict]:
    """Return top N chapters by compound sentiment score ('positive' or 'negative')."""
    records = _load_sentiment()
    reverse = direction == "positive"
    ranked = sorted(records, key=lambda r: r["compound"], reverse=reverse)
    return ranked[:n]


def get_relationships(character: str) -> list[dict]:
    """Return all co-occurrence edges involving the given character, sorted by weight."""
    data = _load_relationships()
    char_lower = character.lower()
    edges = [
        e for e in data["edges"]
        if char_lower in e["source"].lower() or char_lower in e["target"].lower()
    ]
    return sorted(edges, key=lambda e: e["weight"], reverse=True)


def known_characters() -> list[str]:
    """Return the canonical character names from the relationship graph nodes."""
    data = _load_relationships()
    return [n["id"] for n in data.get("nodes", [])]
