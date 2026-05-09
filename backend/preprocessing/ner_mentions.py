#!/usr/bin/env python3
"""
ner_mentions.py — Phase 2, step 2.

Loads backend/data/chapters.json, runs spaCy NER (en_core_web_sm) on each
chapter, extracts PERSON entities, and writes backend/data/characters.json.

Each output record: { character_name, book_number, chapter_number, mention_count }

Run from any directory with the venv active:
    python backend/preprocessing/ner_mentions.py
"""

import json
import logging
import re
from collections import Counter, defaultdict
from pathlib import Path

import spacy
from spacy.language import Language

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
INPUT_PATH = ROOT / "backend" / "data" / "chapters.json"
OUTPUT_PATH = ROOT / "backend" / "data" / "characters.json"

# Filter names shorter than this — eliminates single-letter OCR artifacts
# while keeping short valid names like "Al", "Jo", "Tom"
MIN_NAME_LEN = 2

BLOCKLIST: set[str] = {
    "the order of",
    "order of the phoenix",
    "order of",
    "order",
}


def normalise(text: str) -> str:
    """Strip possessive suffixes and collapse internal whitespace."""
    t = re.sub(r"\s+", " ", text).strip()
    if t.endswith("’s") or t.endswith("’s"):
        t = t[:-2]
    elif t.endswith("’") or t.endswith("’"):
        t = t[:-1]
    return t.strip()


def load_chapters(path: Path) -> list[dict]:
    """Load and return the list of chapter dicts from chapters.json."""
    return json.loads(path.read_text(encoding="utf-8"))


def extract_mentions(chapters: list[dict], nlp: Language) -> list[dict]:
    """Run NER on each chapter; return per-(character, book, chapter) mention counts."""
    records: list[dict] = []

    texts = [ch["text"] for ch in chapters]
    log.info(f"Running NER on {len(texts)} chapters (this may take a minute)...")

    for chapter, doc in zip(chapters, nlp.pipe(texts, batch_size=10)):
        counts: Counter[str] = Counter()
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                name = normalise(ent.text)
                if len(name) >= MIN_NAME_LEN and name.lower() not in BLOCKLIST:
                    counts[name] += 1

        for name, count in counts.items():
            records.append({
                "character_name": name,
                "book_number": chapter["book_number"],
                "chapter_number": chapter["chapter_number"],
                "mention_count": count,
            })

    return records


def print_validation_summary(records: list[dict]) -> None:
    """Print top 10 characters overall and top 5 per book."""
    overall: Counter[str] = Counter()
    by_book: defaultdict[int, Counter[str]] = defaultdict(Counter)

    for r in records:
        overall[r["character_name"]] += r["mention_count"]
        by_book[r["book_number"]][r["character_name"]] += r["mention_count"]

    unique_names = len(overall)
    total_mentions = sum(overall.values())
    print(f"\nUnique entity strings: {unique_names}  |  Total mentions: {total_mentions}")

    print("\n=== TOP 10 CHARACTERS (ALL BOOKS) ===")
    for name, count in overall.most_common(10):
        print(f"  {count:>6}  {name}")

    print()
    for book_num in sorted(by_book):
        print(f"=== TOP 5 — BOOK {book_num} ===")
        for name, count in by_book[book_num].most_common(5):
            print(f"  {count:>6}  {name}")
        print()


def main() -> None:
    """Run NER extraction and write characters.json."""
    chapters = load_chapters(INPUT_PATH)
    log.info(f"Loaded {len(chapters)} chapters from {INPUT_PATH}")

    nlp = spacy.load("en_core_web_sm")

    records = extract_mentions(chapters, nlp)
    log.info(f"Extracted {len(records)} (character, book, chapter) records")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(records, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    log.info(f"Written to {OUTPUT_PATH}")

    print_validation_summary(records)


if __name__ == "__main__":
    main()
