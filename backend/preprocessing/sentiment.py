#!/usr/bin/env python3
"""
sentiment.py — Phase 2, step 3.

Loads backend/data/chapters.json, runs VADER sentiment analysis on each
chapter's full text, and writes backend/data/sentiment.json.

Each output record: { book, chapter, compound, positive, negative, neutral }

Run from any directory with the venv active:
    python backend/preprocessing/sentiment.py
"""

import json
import logging
from pathlib import Path

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
INPUT_PATH = ROOT / "backend" / "data" / "chapters.json"
OUTPUT_PATH = ROOT / "backend" / "data" / "sentiment.json"


def main() -> None:
    with open(INPUT_PATH, encoding="utf-8") as f:
        chapters = json.load(f)

    analyzer = SentimentIntensityAnalyzer()
    records = []

    for ch in chapters:
        scores = analyzer.polarity_scores(ch["text"])
        records.append({
            "book": ch["book_number"],
            "chapter": ch["chapter_number"],
            "compound": round(scores["compound"], 4),
            "positive": round(scores["pos"], 4),
            "negative": round(scores["neg"], 4),
            "neutral": round(scores["neu"], 4),
        })

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)

    # --- Validation ---
    log.info(f"\nTotal records written: {len(records)}")

    sorted_pos = sorted(records, key=lambda r: r["compound"], reverse=True)
    log.info("\nTop 5 most positive chapters (highest compound):")
    for r in sorted_pos[:5]:
        log.info(f"  Book {r['book']} Chapter {r['chapter']}: {r['compound']}")

    sorted_neg = sorted(records, key=lambda r: r["compound"])
    log.info("\nTop 5 most negative chapters (lowest compound):")
    for r in sorted_neg[:5]:
        log.info(f"  Book {r['book']} Chapter {r['chapter']}: {r['compound']}")

    # Per-book average compound
    from collections import defaultdict
    book_totals: dict[int, list[float]] = defaultdict(list)
    for r in records:
        book_totals[r["book"]].append(r["compound"])
    log.info("\nPer-book average compound score:")
    for book in sorted(book_totals):
        avg = round(sum(book_totals[book]) / len(book_totals[book]), 4)
        log.info(f"  Book {book}: {avg}")

    # Spot checks
    spot = {(r["book"], r["chapter"]): r for r in records}
    for key in [(3, 1), (7, 33)]:
        r = spot.get(key)
        if r:
            log.info(
                f"\nSpot check Book {key[0]} Chapter {key[1]}: "
                f"compound={r['compound']}, pos={r['positive']}, "
                f"neg={r['negative']}, neu={r['neutral']}"
            )
        else:
            log.info(f"\nSpot check Book {key[0]} Chapter {key[1]}: NOT FOUND")


if __name__ == "__main__":
    main()
