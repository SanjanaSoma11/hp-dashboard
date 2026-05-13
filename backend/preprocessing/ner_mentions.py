#!/usr/bin/env python3
"""
ner_mentions.py — Phase 2, step 2.

Loads backend/data/chapters.json, runs spaCy NER (en_core_web_sm) on each
chapter, extracts PERSON entities, applies the Gemini-produced alias map from
backend/data/aliases.json, and writes backend/data/characters.json.

Each output record: { character_name, book_number, chapter_number, mention_count }

Run alias_resolver.py first to produce aliases.json, then:
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
ALIASES_PATH = ROOT / "backend" / "data" / "aliases.json"
MANUAL_ALIASES_PATH = ROOT / "backend" / "data" / "character_aliases.manual.json"

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
    if t.endswith("'s") or t.endswith("’s"):
        t = t[:-2]
    elif t.endswith("'") or t.endswith("’"):
        t = t[:-1]
    return t.strip()


def load_chapters(path: Path) -> list[dict]:
    """Load and return the list of chapter dicts from chapters.json."""
    return json.loads(path.read_text(encoding="utf-8"))


def load_aliases(path: Path) -> dict[str, str]:
    """Load the Gemini-produced alias map from aliases.json.

    Returns an empty dict if the file does not exist, with a warning to run
    alias_resolver.py first.
    """
    if not path.exists():
        log.warning(
            f"aliases.json not found at {path}. "
            "Run alias_resolver.py first to generate it. Proceeding without aliases."
        )
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def load_manual_aliases(path: Path) -> dict[str, str | None]:
    """Load the hand-curated alias map from character_aliases.manual.json.

    Returns an empty dict if the file does not exist.
    Entries with null values are intentionally ambiguous and are excluded.
    """
    if not path.exists():
        log.warning(f"Manual aliases file not found at {path}. Proceeding without manual aliases.")
        return {}
    raw: dict[str, str | None] = json.loads(path.read_text(encoding="utf-8"))
    return {alias: canon for alias, canon in raw.items() if canon is not None}


def extract_mentions(
    chapters: list[dict],
    nlp: Language,
    aliases: dict[str, str],
    chapter_word_counts: dict[tuple[int, int], int],
) -> list[dict]:
    """Run NER on each chapter; return per-(character, book, chapter) mention counts.

    Two-pass approach:
      Pass 1 — collect raw entity lists per chapter (single NER run).
      Pass 2 — apply aliases to merge fragments into canonical forms before
               aggregating per (book, chapter) counts.
    """
    texts = [ch["text"] for ch in chapters]
    log.info(f"Running NER on {len(texts)} chapters (this may take a minute)...")

    # Pass 1: collect raw per-chapter entity lists
    raw_chapter_data: list[tuple[dict, list[str]]] = []
    for chapter, doc in zip(chapters, nlp.pipe(texts, batch_size=10)):
        names: list[str] = []
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                name = normalise(ent.text)
                if len(name) >= MIN_NAME_LEN and name.lower() not in BLOCKLIST:
                    names.append(name)
        raw_chapter_data.append((chapter, names))

    # Compute global mention counts across all chapters (raw, pre-resolution)
    global_counts: Counter[str] = Counter()
    for _, names in raw_chapter_data:
        for name in names:
            global_counts[name] += 1

    # Pass 2: apply alias map and aggregate per (book, chapter)
    records: list[dict] = []
    for chapter, names in raw_chapter_data:
        book_num = chapter["book_number"]
        chap_num = chapter["chapter_number"]
        word_count = chapter_word_counts.get((book_num, chap_num), 0)
        counts: Counter[str] = Counter()
        for name in names:
            resolved = aliases.get(name, name)
            counts[resolved] += 1
        for name, count in counts.items():
            per_1k = round((count / word_count) * 1000, 2) if word_count > 0 else 0.0
            records.append({
                "character_name": name,
                "book_number": book_num,
                "chapter_number": chap_num,
                "mention_count": count,
                "mentions_per_1k_words": per_1k,
            })

    # Compute post-resolution global totals for the validation summary
    resolved_totals: Counter[str] = Counter()
    for r in records:
        resolved_totals[r["character_name"]] += r["mention_count"]

    _print_alias_summary(aliases, global_counts, resolved_totals)

    return records


def _print_alias_summary(
    aliases: dict[str, str],
    global_counts: Counter[str],
    resolved_totals: Counter[str],
) -> None:
    """Print alias resolution report with before/after comparison."""
    print("\n" + "=" * 60)
    print("ALIAS RESOLUTION SUMMARY")
    print("=" * 60)

    # Only show aliases that actually had mentions in this corpus
    applied = {alias: canon for alias, canon in aliases.items() if alias in global_counts}

    print(f"\n--- Applied aliases ({len(applied)} of {len(aliases)} loaded) ---")
    if applied:
        for alias, canon in sorted(applied.items(), key=lambda x: -global_counts[x[0]]):
            before = global_counts[alias]
            after = resolved_totals[canon]
            print(f"  {alias:<30} ({before:>7,})  →  {canon:<30} ({after:>7,} post-resolution)")
    else:
        print("  (none applied — check aliases.json)")

    print("\n--- Before / After for top resolved names ---")
    print(f"  {'Alias':<30} {'Before':>8}   {'Canonical':<30} {'After':>8}")
    print(f"  {'-'*30} {'-'*8}   {'-'*30} {'-'*8}")
    for alias, canon in sorted(applied.items(), key=lambda x: -global_counts[x[0]])[:15]:
        print(f"  {alias:<30} {global_counts[alias]:>8,}   {canon:<30} {resolved_totals[canon]:>8,}")

    harry_canon = applied.get("Harry")
    if harry_canon:
        print(
            f"\n[OK] Harry ({global_counts['Harry']:,} raw) → {harry_canon} "
            f"({resolved_totals[harry_canon]:,} post-resolution)"
        )
    else:
        print(f"\n[WARN] 'Harry' not resolved — verify aliases.json")

    print(f"\n--- Top 20 characters post-resolution ---")
    for i, (name, count) in enumerate(resolved_totals.most_common(20), 1):
        marker = " ◄ Harry Potter (was separate node)" if name == "Harry Potter" and "Harry" in applied else ""
        print(f"  {i:>2}. {count:>7,}  {name}{marker}")
    print()


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
    """Run NER extraction with merged alias resolution and write characters.json."""
    chapters = load_chapters(INPUT_PATH)
    log.info(f"Loaded {len(chapters)} chapters from {INPUT_PATH}")

    gemini_aliases = load_aliases(ALIASES_PATH)
    log.info(f"Loaded {len(gemini_aliases)} Gemini aliases from {ALIASES_PATH}")

    manual_aliases = load_manual_aliases(MANUAL_ALIASES_PATH)
    log.info(f"Loaded {len(manual_aliases)} manual aliases from {MANUAL_ALIASES_PATH}")

    # Merge: manual takes priority over Gemini for any overlapping alias key
    aliases: dict[str, str] = {**gemini_aliases, **manual_aliases}
    log.info(f"Merged alias map: {len(aliases)} total entries ({len(manual_aliases)} manual, {len(gemini_aliases)} Gemini)")

    # Build word-count lookup from chapter text (used for mentions_per_1k_words)
    chapter_word_counts: dict[tuple[int, int], int] = {
        (ch["book_number"], ch["chapter_number"]): len(ch["text"].split())
        for ch in chapters
    }

    nlp = spacy.load("en_core_web_sm")

    records = extract_mentions(chapters, nlp, aliases, chapter_word_counts)
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
