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
from pathlib import Path

import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
INPUT_PATH = ROOT / "backend" / "data" / "chapters.json"
CHROMA_PATH = ROOT / "backend" / "chroma_db"

COLLECTION_NAME = "hp_books"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
EMBED_BATCH = 64
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def main() -> None:
    with open(INPUT_PATH, encoding="utf-8") as f:
        chapters = json.load(f)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
    )

    # Build flat list of (text, metadata) tuples
    chunks: list[tuple[str, dict]] = []
    for ch in chapters:
        texts = splitter.split_text(ch["text"])
        for idx, text in enumerate(texts):
            chunks.append((text, {
                "book": ch["book_number"],
                "chapter": ch["chapter_number"],
                "chunk_index": idx,
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
    log.info(f"Collection count: {total_stored}")
    log.info(f"Collection name: {collection.name}")

    # 3 random samples spread across different books
    log.info("\nRandom sample chunks:")
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
            f"  [{ids[i]}] book={meta['book']} chapter={meta['chapter']} "
            f"chunk_index={meta['chunk_index']}"
        )
        log.info(f"  Text: {text[:100]!r}")


if __name__ == "__main__":
    main()
