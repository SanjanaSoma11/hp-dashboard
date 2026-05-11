#!/usr/bin/env python3
"""
alias_resolver.py — Resolves NER entity aliases using Gemini.

Loads the entity list from characters.json, takes the top 200 by total mention
count, sends them to Gemini in a single prompt, and writes the validated alias
map to backend/data/aliases.json.

Cache: raw Gemini response text is written to backend/data/aliases_raw.json.
If that file already exists, the API call is skipped and the cached text is
parsed instead.

Run from any directory with the venv active:
    python backend/preprocessing/alias_resolver.py
"""

import json
import logging
import os
from collections import Counter
from pathlib import Path

from dotenv import load_dotenv
from google import genai

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
CHARACTERS_PATH = ROOT / "backend" / "data" / "characters.json"
ALIASES_RAW_PATH = ROOT / "backend" / "data" / "aliases_raw.json"
ALIASES_PATH = ROOT / "backend" / "data" / "aliases.json"

_MODEL = "gemini-3.1-flash-lite"
TOP_N = 200

load_dotenv(ROOT / "backend" / ".env")

client = genai.Client(
    vertexai=True,
    project=os.getenv("GCP_PROJECT", "hpdashboard"),
    location=os.getenv("GCP_LOCATION", "global"),
)

_PROMPT_TEMPLATE = """\
You are analysing named entities extracted from the Harry Potter book series by a spaCy NER model.

Below is a list of the top {n} entity names, ordered by total mention count across all 7 books.

Your task: return a JSON object mapping every alias, shorthand, or fragment to its canonical full name.

Rules:
- Only include a mapping when you are confident the alias refers to a specific canonical full name that also appears verbatim in the list below.
- The canonical name (the value) MUST appear verbatim in the input list. Do not invent or hallucinate names.
- Do NOT include self-mappings (e.g. "Harry Potter" → "Harry Potter").
- Do NOT include mappings for genuinely ambiguous surnames shared by multiple characters (e.g. "Weasley" could be any of several Weasley family members — omit it).
- Names that are already canonical should be omitted from the output entirely.
- Examples of correct mappings: {{"Harry": "Harry Potter", "Ron": "Ron Weasley", "He-Who-Must-Not-Be-Named": "Lord Voldemort"}}

Entity list (name : total mentions):
{names}

Return ONLY valid JSON. No explanation, no markdown fences, no code blocks. Just the JSON object.
"""


def load_top_names(path: Path, top_n: int) -> tuple[list[str], Counter]:
    """Load characters.json and return (top_n names, full mention counter)."""
    records = json.loads(path.read_text(encoding="utf-8"))
    totals: Counter = Counter()
    for r in records:
        totals[r["character_name"]] += r["mention_count"]
    top_names = [name for name, _ in totals.most_common(top_n)]
    return top_names, totals


def call_gemini(names: list[str], totals: Counter) -> str:
    """Call Gemini with the alias resolution prompt and return raw response text."""
    names_str = "\n".join(f"  {i + 1:>3}. {name} : {totals[name]:,}" for i, name in enumerate(names))
    prompt = _PROMPT_TEMPLATE.format(n=len(names), names=names_str)
    response = client.models.generate_content(model=_MODEL, contents=prompt)
    return response.text


def parse_alias_map(raw_text: str) -> dict[str, str]:
    """Parse a JSON object from raw Gemini response text, stripping any markdown fences."""
    text = raw_text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        end = len(lines) - 1 if lines[-1].strip() == "```" else len(lines)
        text = "\n".join(lines[1:end])
    return json.loads(text.strip())


def validate_alias_map(
    raw_map: dict[str, str],
    valid_names: set[str],
) -> dict[str, str]:
    """Validate that every canonical value appears in the input name list."""
    validated: dict[str, str] = {}
    for alias, canonical in raw_map.items():
        if alias == canonical:
            continue  # skip self-mappings silently
        if canonical not in valid_names:
            log.warning(f"  DISCARDED (hallucinated canonical): {alias!r} → {canonical!r}")
        else:
            validated[alias] = canonical
    return validated


def main() -> None:
    """Resolve aliases and write aliases.json."""
    log.info(f"Loading entity list from {CHARACTERS_PATH}")
    top_names, totals = load_top_names(CHARACTERS_PATH, TOP_N)
    valid_name_set = set(top_names)
    log.info(f"Top {TOP_N} names loaded (total unique entities: {len(totals)})")

    if ALIASES_RAW_PATH.exists():
        log.info(f"Cache found at {ALIASES_RAW_PATH} — skipping Gemini API call")
        cache = json.loads(ALIASES_RAW_PATH.read_text(encoding="utf-8"))
        raw_text = cache["response"]
    else:
        log.info(f"Calling Gemini ({_MODEL}) for alias resolution…")
        raw_text = call_gemini(top_names, totals)
        ALIASES_RAW_PATH.write_text(
            json.dumps({"response": raw_text, "names": top_names}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        log.info(f"Raw response cached to {ALIASES_RAW_PATH}")

    log.info("Parsing Gemini response…")
    raw_map = parse_alias_map(raw_text)
    log.info(f"Parsed {len(raw_map)} entries from Gemini response")

    log.info("Validating entries (canonical names must appear in input list)…")
    alias_map = validate_alias_map(raw_map, valid_name_set)
    discarded = len(raw_map) - len(alias_map) - sum(1 for k, v in raw_map.items() if k == v)
    log.info(f"Validated {len(alias_map)} aliases ({discarded} discarded)")

    ALIASES_PATH.write_text(
        json.dumps(alias_map, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    log.info(f"Written to {ALIASES_PATH}")

    print(f"\n=== ALIAS MAP ({len(alias_map)} entries) ===")
    for alias, canonical in sorted(alias_map.items(), key=lambda x: -totals[x[0]]):
        print(f"  {alias:<35} ({totals[alias]:>6,})  →  {canonical}")

    harry_target = alias_map.get("Harry")
    if harry_target:
        combined = totals.get(harry_target, 0) + totals.get("Harry", 0)
        print(f"\n[OK] Harry ({totals['Harry']:,}) → {harry_target} — combined ≈ {combined:,} mentions")
    else:
        print(f"\n[WARN] 'Harry' not resolved — check the alias map or delete the cache and re-run")


if __name__ == "__main__":
    main()
