#!/usr/bin/env python3
"""
relationships.py — Phase 2, step 3.

Reads backend/data/characters.json (post alias-resolution) and produces
backend/data/relationships.json: weighted co-occurrence graph for the
top 30 characters across all books.

Edge construction:
  For each chapter, collect the set of unique top-30 character names that
  appear in it (presence only — mention count is ignored for edge building).
  For every pair of characters co-appearing in the same chapter, increment
  their shared edge weight by 1.

Output schema:
  {
    "nodes": [
      {
        "id": "Harry Potter",
        "mention_count": 17862,
        "degree": 29,
        "weighted_degree": 4523.0,
        "betweenness": 0.0342,
        "pagerank": 0.0891,
        "books": [1, 2, 3, 4, 5, 6, 7]
      }
    ],
    "edges": [
      {"source": "Harry Potter", "target": "Ron Weasley", "weight": 142}
    ]
  }

Run from any directory with the venv active:
    python backend/preprocessing/relationships.py
"""

import json
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parents[2]
INPUT_PATH = ROOT / "backend" / "data" / "characters.json"
OUTPUT_PATH = ROOT / "backend" / "data" / "relationships.json"

TOP_N = 30

# Known data quality notes:
#   - "Weasley" and "Malfoy" are ambiguous surnames left unresolved by design.
#   - "Harry" is resolved to "Harry Potter" by the alias map.
#   - "Hogwarts" may appear — spaCy tags it as PERSON (OCR / model artifact).


def main() -> None:
    """Build character co-occurrence graph with centrality metrics from characters.json."""
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

    # Per-character book membership (which books each top-N character appears in)
    char_books: defaultdict[str, set[int]] = defaultdict(set)
    for r in records:
        if r["character_name"] in top_n:
            char_books[r["character_name"]].add(r["book_number"])

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

    # Build networkx graph for centrality computation
    G: nx.Graph = nx.Graph()
    for name in top_n:
        G.add_node(name)
    for (a, b), w in edge_weights.items():
        G.add_edge(a, b, weight=w)

    # Compute centrality metrics
    degree_map: dict[str, int] = dict(G.degree())
    weighted_degree_map: dict[str, float] = dict(G.degree(weight="weight"))
    betweenness_map: dict[str, float] = nx.betweenness_centrality(G)
    pagerank_map: dict[str, float] = nx.pagerank(G, weight="weight")

    # Build nodes list ordered by total mention count descending
    nodes: list[dict] = []
    for name, count in total_mentions.most_common(TOP_N):
        nodes.append(
            {
                "id": name,
                "mention_count": count,
                "degree": degree_map[name],
                "weighted_degree": round(weighted_degree_map[name], 4),
                "betweenness": round(betweenness_map[name], 4),
                "pagerank": round(pagerank_map[name], 4),
                "books": sorted(char_books[name]),
            }
        )

    edges: list[dict] = [
        {"source": a, "target": b, "weight": w}
        for (a, b), w in edge_weights.items()
    ]

    output = {"nodes": nodes, "edges": edges}
    OUTPUT_PATH.write_text(
        json.dumps(output, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\nWritten {len(nodes)} nodes and {len(edges)} edges to {OUTPUT_PATH}")

    # Validation: top 5 by each centrality metric
    print("\n=== TOP 5 BY DEGREE ===")
    for n in sorted(nodes, key=lambda x: x["degree"], reverse=True)[:5]:
        print(f"  {n['degree']:>4}  {n['id']}")

    print("\n=== TOP 5 BY WEIGHTED DEGREE ===")
    for n in sorted(nodes, key=lambda x: x["weighted_degree"], reverse=True)[:5]:
        print(f"  {n['weighted_degree']:>10.4f}  {n['id']}")

    print("\n=== TOP 5 BY BETWEENNESS ===")
    for n in sorted(nodes, key=lambda x: x["betweenness"], reverse=True)[:5]:
        print(f"  {n['betweenness']:.4f}  {n['id']}")

    print("\n=== TOP 5 BY PAGERANK ===")
    for n in sorted(nodes, key=lambda x: x["pagerank"], reverse=True)[:5]:
        print(f"  {n['pagerank']:.4f}  {n['id']}")

    print(f"\nTotal nodes: {len(nodes)}")
    print(f"Total edges: {len(edges)}")

    print("\n=== TOP 15 EDGES BY WEIGHT ===")
    for (a, b), w in edge_weights.most_common(15):
        print(f"  {w:>4}  {a} — {b}")

    # Flag single-token names in the top-N set that may be unresolved fragments
    fragment_candidates = [
        n["id"]
        for n in nodes
        if len(n["id"].split()) == 1
        and n["id"][0].isupper()
        and n["id"]
        not in {
            "Harry", "Ron", "Hermione", "Dumbledore", "Hagrid",
            "Voldemort", "Luna", "Ginny", "Percy", "Fred", "George",
            "Dobby", "Neville", "Snape", "Draco", "Bill",
        }
    ]
    if fragment_candidates:
        print(
            "\n[NOTE] Single-token names that may be unresolved fragments:\n  "
            + "\n  ".join(sorted(fragment_candidates))
        )


if __name__ == "__main__":
    main()
