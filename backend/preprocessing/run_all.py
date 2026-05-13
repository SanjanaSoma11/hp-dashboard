"""
Preprocessing orchestrator. Runs all scripts in the required order:

  1. chapter_splitter.py    — splits book text into chapters → chapters.json
  2. ner_mentions.py        — Pass 1: extracts raw character entities → characters.json
  3. alias_resolver.py      — sends top-200 entities to Gemini, writes aliases.json
  4. ner_mentions.py        — Pass 2: re-runs with aliases.json applied → characters.json (canonical)
  5. relationships.py       — builds co-occurrence edges from characters.json → relationships.json
  6. sentiment.py           — VADER sentence-level scoring → sentiment.json
  7. chunker.py             — LangChain chunking + embedding → ChromaDB

ner_mentions.py runs twice because alias_resolver.py depends on the raw entity list produced
in Pass 1, and Pass 2 needs aliases.json to exist before it can apply canonical names.

Run from the project root:
    python backend/preprocessing/run_all.py
"""

import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent

STEPS = [
    ("chapter_splitter.py", "Splitting chapters"),
    ("ner_mentions.py", "NER pass 1 — raw entity extraction"),
    ("alias_resolver.py", "Resolving aliases via Gemini"),
    ("ner_mentions.py", "NER pass 2 — applying aliases"),
    ("relationships.py", "Building relationship graph"),
    ("sentiment.py", "Scoring sentiment"),
    ("chunker.py", "Chunking and embedding into ChromaDB"),
]


def main() -> None:
    python = sys.executable
    total = len(STEPS)

    for i, (script, label) in enumerate(STEPS, start=1):
        script_path = SCRIPTS_DIR / script
        print(f"[{i}/{total}] {label} ({script}) ...", flush=True)

        result = subprocess.run(
            [python, str(script_path)],
            capture_output=False,
        )

        if result.returncode != 0:
            print(f"\n[FAILED] {script} exited with code {result.returncode}. Stopping.")
            sys.exit(result.returncode)

        print(f"[{i}/{total}] Done: {script}", flush=True)

    print(f"\nAll {total} steps completed successfully.")


if __name__ == "__main__":
    main()
