#!/usr/bin/env python3
"""
chunker.py — Phase 2, step 4.

Loads backend/data/chapters.json, splits each chapter into chunks with
LangChain RecursiveCharacterTextSplitter, embeds with sentence-transformers
all-MiniLM-L6-v2, and stores in a local ChromaDB collection (hp_books).

Run from any directory with the venv active:
    python backend/preprocessing/chunker.py
"""

import json
import logging
import random
from collections import defaultdict
from pathlib import Path

import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
INPUT_PATH = ROOT / "backend" / "data" / "chapters.json"
CHARACTERS_PATH = ROOT / "backend" / "data" / "characters.json"
CHROMA_PATH = ROOT / "backend" / "chroma_db"

COLLECTION_NAME = "hp_books"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
EMBED_BATCH = 64
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
TOP_N_CHARACTERS = 30


def load_top_characters(n: int) -> list[str]:
    """Return the top-N character names by total mention count."""
    with open(CHARACTERS_PATH, encoding="utf-8") as f:
        records = json.load(f)
    totals: dict[str, int] = defaultdict(int)
    for r in records:
        totals[r["character_name"]] += r["mention_count"]
    ranked = sorted(totals.items(), key=lambda x: -x[1])
    return [name for name, _ in ranked[:n]]


def main() -> None:
    with open(INPUT_PATH, encoding="utf-8") as f:
        chapters = json.load(f)

    # Build lookup: (book_number, chapter_number) → title fields
    chapter_meta: dict[tuple[int, int], dict] = {}
    for ch in chapters:
        key = (ch["book_number"], ch["chapter_number"])
        chapter_meta[key] = {
            "book_title": ch.get("book_title", f"Book {ch['book_number']}"),
            "chapter_title": ch.get("chapter_title", f"Chapter {ch['chapter_number']}"),
        }

    top_characters = load_top_characters(TOP_N_CHARACTERS)
    log.info(f"Top {TOP_N_CHARACTERS} characters loaded for mention matching")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
    )

    # Build flat list of (text, metadata) tuples
    chunks: list[tuple[str, dict]] = []
    for ch in chapters:
        key = (ch["book_number"], ch["chapter_number"])
        titles = chapter_meta[key]
        texts = splitter.split_text(ch["text"])
        for idx, text in enumerate(texts):
            found = [name for name in top_characters if name in text]
            chunks.append((text, {
                "book": ch["book_number"],
                "book_title": titles["book_title"],
                "chapter": ch["chapter_number"],
                "chapter_title": titles["chapter_title"],
                "chunk_index": idx,
                "word_count": len(text.split()),
                "characters_mentioned": ",".join(found),
            }))

    log.info(f"Total chunks to embed: {len(chunks)}")

    # Embed
    log.info(f"Loading embedding model: {EMBED_MODEL}")
    model = SentenceTransformer(EMBED_MODEL)

    all_texts = [c[0] for c in chunks]
    embeddings: list[list[float]] = []
    for start in range(0, len(all_texts), EMBED_BATCH):
        batch = all_texts[start : start + EMBED_BATCH]
        vecs = model.encode(batch, show_progress_bar=False).tolist()
        embeddings.extend(vecs)
        log.info(f"  Embedded {min(start + EMBED_BATCH, len(all_texts))}/{len(all_texts)}")

    # ChromaDB — delete and recreate for safe reruns
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    try:
        client.delete_collection(COLLECTION_NAME)
        log.info(f"Deleted existing collection '{COLLECTION_NAME}'")
    except Exception:
        pass
    collection = client.create_collection(COLLECTION_NAME)
    log.info(f"Created collection '{COLLECTION_NAME}'")

    # Store in batches
    ids = [f"b{m['book']}_c{m['chapter']}_{m['chunk_index']}" for _, m in chunks]
    metadatas = [m for _, m in chunks]
    documents = all_texts

    for start in range(0, len(chunks), EMBED_BATCH):
        collection.add(
            ids=ids[start : start + EMBED_BATCH],
            embeddings=embeddings[start : start + EMBED_BATCH],
            documents=documents[start : start + EMBED_BATCH],
            metadatas=metadatas[start : start + EMBED_BATCH],
        )

    # --- Validation ---
    total_stored = collection.count()
    log.info(f"\nTotal chunks stored: {total_stored}")
    log.info(f"Collection name: {collection.name}")

    # 3 random samples spread across different books — verify all new metadata fields
    log.info("\nRandom sample chunks (verify enriched metadata):")
    seen_books: set[int] = set()
    candidates = list(range(len(chunks)))
    random.shuffle(candidates)
    samples: list[int] = []
    for i in candidates:
        book = chunks[i][1]["book"]
        if book not in seen_books:
            seen_books.add(book)
            samples.append(i)
        if len(samples) == 3:
            break

    for i in samples:
        text, meta = chunks[i]
        log.info(
            f"  [{ids[i]}]\n"
            f"    book={meta['book']} book_title={meta['book_title']!r}\n"
            f"    chapter={meta['chapter']} chapter_title={meta['chapter_title']!r}\n"
            f"    chunk_index={meta['chunk_index']} word_count={meta['word_count']}\n"
            f"    characters_mentioned={meta['characters_mentioned']!r}\n"
            f"    text={text[:80]!r}"
        )


if __name__ == "__main__":
    main()
