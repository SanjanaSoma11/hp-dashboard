#!/usr/bin/env python3
"""
sentiment.py — Phase 2, step 3.

Loads backend/data/chapters.json, scores VADER sentiment at sentence level
(nltk.sent_tokenize), averages compound/pos/neg/neu per chapter, and writes
backend/data/sentiment.json.

Sentence-level averaging avoids VADER's sigmoid saturation that occurs when
the full chapter text is scored as a single string.

Each output record: { book, chapter, compound, positive, negative, neutral }

Run from any directory with the venv active:
    python backend/preprocessing/sentiment.py
"""

import json
import logging
from collections import defaultdict
from pathlib import Path
from statistics import mean

import nltk
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

nltk.download("punkt_tab", quiet=True)

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
INPUT_PATH = ROOT / "backend" / "data" / "chapters.json"
OUTPUT_PATH = ROOT / "backend" / "data" / "sentiment.json"


def score_chapter(text: str, analyzer: SentimentIntensityAnalyzer) -> dict[str, float]:
    """Average sentence-level VADER scores across all sentences in a chapter."""
    sentences = nltk.sent_tokenize(text)
    if not sentences:
        return {"compound": 0.0, "pos": 0.0, "neg": 0.0, "neu": 1.0}
    scored = [analyzer.polarity_scores(s) for s in sentences]
    return {
        "compound": mean(s["compound"] for s in scored),
        "pos": mean(s["pos"] for s in scored),
        "neg": mean(s["neg"] for s in scored),
        "neu": mean(s["neu"] for s in scored),
    }


def main() -> None:
    with open(INPUT_PATH, encoding="utf-8") as f:
        chapters = json.load(f)

    analyzer = SentimentIntensityAnalyzer()
    records = []

    for ch in chapters:
        scores = score_chapter(ch["text"], analyzer)
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

    compounds = [r["compound"] for r in records]
    log.info(f"Compound range: min={min(compounds):.4f}  max={max(compounds):.4f}")
    saturated = sum(1 for c in compounds if abs(c) >= 0.9)
    log.info(f"Saturated at |compound| ≥ 0.9: {saturated} / {len(compounds)} chapters")

    sorted_pos = sorted(records, key=lambda r: r["compound"], reverse=True)
    log.info("\nTop 5 most positive chapters:")
    for r in sorted_pos[:5]:
        log.info(f"  Book {r['book']} Ch {r['chapter']}: {r['compound']}")

    sorted_neg = sorted(records, key=lambda r: r["compound"])
    log.info("\nTop 5 most negative chapters:")
    for r in sorted_neg[:5]:
        log.info(f"  Book {r['book']} Ch {r['chapter']}: {r['compound']}")

    book_totals: dict[int, list[float]] = defaultdict(list)
    for r in records:
        book_totals[r["book"]].append(r["compound"])
    log.info("\nPer-book average compound score:")
    for book in sorted(book_totals):
        avg = round(sum(book_totals[book]) / len(book_totals[book]), 4)
        log.info(f"  Book {book}: {avg}")

    spot = {(r["book"], r["chapter"]): r for r in records}
    for key in [(3, 1), (7, 33)]:
        r = spot.get(key)
        if r:
            log.info(
                f"\nSpot check Book {key[0]} Ch {key[1]}: "
                f"compound={r['compound']}  pos={r['positive']}  "
                f"neg={r['negative']}  neu={r['neutral']}"
            )
        else:
            log.info(f"\nSpot check Book {key[0]} Ch {key[1]}: NOT FOUND")


if __name__ == "__main__":
    main()
