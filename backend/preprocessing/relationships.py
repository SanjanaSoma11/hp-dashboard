#!/usr/bin/env python3
"""
relationships.py — Phase 2, step 3.

Reads backend/data/characters.json (post alias-resolution) and produces
backend/data/relationships.json: a weighted co-occurrence edge list for the
top 30 characters across all books.

Edge construction:
  For each chapter, collect the set of unique top-30 character names that
  appear in it (presence only — mention count is ignored for edge building).
  For every pair of characters co-appearing in the same chapter, increment
  their shared edge weight by 1.

Output: list of { source, target, weight } objects.
  source < target alphabetically to guarantee pair uniqueness.

Run from any directory with the venv active:
    python backend/preprocessing/relationships.py
"""

import json
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INPUT_PATH = ROOT / "backend" / "data" / "characters.json"
OUTPUT_PATH = ROOT / "backend" / "data" / "relationships.json"

TOP_N = 30

# Known data quality notes:
#   - "Weasley" and "Malfoy" are ambiguous surnames left unresolved by design —
#     they cover multiple characters and Gemini correctly omitted them from the
#     alias map.  They appear as their own nodes.
#   - "Harry" is resolved to "Harry Potter" by the Gemini alias map; the two are
#     now merged and "Harry Potter" carries the combined mention count.
#   - "Hogwarts" may still appear — spaCy tags it as PERSON (OCR / model artifact).


def main() -> None:
    """Build character co-occurrence graph from characters.json."""
    records: list[dict] = json.loads(INPUT_PATH.read_text(encoding="utf-8"))

    # Compute total mention counts per character across all books
    total_mentions: Counter[str] = Counter()
    for r in records:
        total_mentions[r["character_name"]] += r["mention_count"]

    # Top-N characters by total mentions
    top_n: set[str] = {name for name, _ in total_mentions.most_common(TOP_N)}

    print(f"\nTop {TOP_N} characters selected:")
    for i, (name, count) in enumerate(total_mentions.most_common(TOP_N), 1):
        print(f"  {i:>2}. {count:>6,}  {name}")

    # For each chapter, collect the unique top-N characters present
    chapter_chars: defaultdict[tuple, set[str]] = defaultdict(set)
    for r in records:
        if r["character_name"] in top_n:
            key = (r["book_number"], r["chapter_number"])
            chapter_chars[key].add(r["character_name"])

    # Build co-occurrence edge weights
    edge_weights: Counter[tuple[str, str]] = Counter()
    for chars in chapter_chars.values():
        char_list = sorted(chars)
        for a, b in combinations(char_list, 2):
            edge_weights[(a, b)] += 1  # a < b guaranteed by sorted()

    relationships = [
        {"source": a, "target": b, "weight": w}
        for (a, b), w in edge_weights.items()
    ]

    OUTPUT_PATH.write_text(
        json.dumps(relationships, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\nWritten {len(relationships)} edges to {OUTPUT_PATH}")

    # Validation summary
    nodes = top_n
    print(f"\nTotal nodes: {len(nodes)}")
    print(f"Total edges: {len(relationships)}")

    print("\n=== TOP 15 EDGES BY WEIGHT ===")
    for (a, b), w in edge_weights.most_common(15):
        print(f"  {w:>4}  {a} — {b}")

    # Flag fragment names in the top-N node set (a sign of incomplete resolution)
    # "Fragment" heuristic: single-token name that is also a common surname
    # or a name known to be a shorthand for a full-name character.
    # NOTE: Harry and Ron appearing here is correct — they are the canonical
    # forms (17k and 6k mentions respectively), not fragments.
    fragment_candidates = [
        n for n in nodes
        if len(n.split()) == 1 and n[0].isupper()
        and n not in {"Harry", "Ron", "Hermione", "Dumbledore", "Hagrid",
                      "Voldemort", "Luna", "Ginny", "Percy", "Fred", "George",
                      "Dobby", "Neville", "Snape", "Draco", "Bill"}
    ]
    if fragment_candidates:
        print(
            "\n[NOTE] The following single-token names appear as top nodes — review "
            "whether they represent standalone characters or unresolved fragments:\n  "
            + "\n  ".join(sorted(fragment_candidates))
        )


if __name__ == "__main__":
    main()
